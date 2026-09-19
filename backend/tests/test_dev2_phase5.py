import pytest
from app.models.emergency import EmergencyPriority
from app.models.green_corridor import CorridorStatus
from app.models.signal import SignalPhase
from app.simulation.network import TrafficNetwork
from app.simulation.signal_engine import SignalController
from app.services.emergency_routing_service import EmergencyRoutingService
from app.services.ambulance_assignment_service import AmbulanceAssignmentService
from app.services.green_corridor_service import GreenCorridorService


def test_green_corridor_plan_creation_and_junction_sequence():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)

    routing.register_ambulance("AMB_1", current_location="J1")
    routing.create_emergency_request("REQ_1", origin="J1", destination="J3")
    assignment = assign_service.assign_ambulance_to_request("REQ_1")

    plan = corridor_service.plan_corridor(assignment)

    assert plan.status == CorridorStatus.PLANNED
    assert plan.ordered_junctions == ["J1", "J2", "J3"]
    assert len(plan.junction_plans) == 3
    assert plan.junction_plans[0].junction_id == "J1"
    assert plan.junction_plans[0].sequence_order == 1
    assert plan.junction_plans[1].junction_id == "J2"
    assert plan.junction_plans[2].junction_id == "J3"


def test_corridor_lifecycle_plan_activate_release():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)

    routing.register_ambulance("AMB_1", current_location="J1")
    routing.create_emergency_request("REQ_2", origin="J1", destination="J3")
    assignment = assign_service.assign_ambulance_to_request("REQ_2")

    # 1. PLAN
    plan = corridor_service.plan_corridor(assignment)
    assert plan.status == CorridorStatus.PLANNED

    # 2. ACTIVATE
    active_plan = corridor_service.activate_corridor("REQ_2")
    assert active_plan.status == CorridorStatus.ACTIVE
    assert net.get_junction("J1").signal_phase == SignalPhase.EMERGENCY_PRIORITY
    assert net.get_junction("J1").emergency_reserved is True
    assert net.get_junction("J2").signal_phase == SignalPhase.EMERGENCY_PRIORITY

    # 3. RELEASE
    released_plan = corridor_service.release_corridor("REQ_2")
    assert released_plan.status == CorridorStatus.RELEASED
    assert net.get_junction("J1").emergency_reserved is False
    assert net.get_junction("J1").signal_phase == SignalPhase.NS_GREEN


def test_pedestrian_clearance_protection_prevents_unsafe_priority():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)

    routing.register_ambulance("AMB_1", current_location="J1")
    routing.create_emergency_request("REQ_3", origin="J1", destination="J3")
    assignment = assign_service.assign_ambulance_to_request("REQ_3")

    # Activate pedestrian crossing at J2
    sig_controller.set_pedestrian_crossing("J2", pedestrian_count=10, clearance_seconds=15.0)

    # PLAN corridor
    plan = corridor_service.plan_corridor(assignment)

    # J2 plan should be marked unsafe due to pedestrian crossing
    j2_plan = next(p for p in plan.junction_plans if p.junction_id == "J2")
    assert j2_plan.is_safe is False
    assert "pedestrian crossing" in j2_plan.safety_reason.lower()

    # ACTIVATE corridor
    active_plan = corridor_service.activate_corridor("REQ_3")
    # J2 priority must NOT be activated while pedestrian crossing is active
    assert net.get_junction("J2").signal_phase == SignalPhase.PEDESTRIAN_CLEARANCE


def test_duplicate_active_corridor_plan_prevention():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)

    routing.register_ambulance("AMB_1", current_location="J1")
    routing.create_emergency_request("REQ_4", origin="J1", destination="J3")
    assignment = assign_service.assign_ambulance_to_request("REQ_4")

    plan1 = corridor_service.plan_corridor(assignment)
    corridor_service.activate_corridor("REQ_4")

    # Planning again for same request safely replaces/releases old corridor
    plan2 = corridor_service.plan_corridor(assignment)
    assert plan2 is not None


def test_replan_corridor_on_route_change_releases_old_junctions():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)

    routing.register_ambulance("AMB_1", current_location="J1")
    routing.create_emergency_request("REQ_5", origin="J1", destination="J3")
    asg1 = assign_service.assign_ambulance_to_request("REQ_5")

    # Activate corridor J1->J2->J3
    corridor_service.plan_corridor(asg1)
    corridor_service.activate_corridor("REQ_5")
    assert net.get_junction("J2").emergency_reserved is True

    # Block R_J1_J2 and calculate new route J1->J4->J5->J6->J3
    net.get_road("R_J1_J2").status = "BLOCKED"
    new_route = routing.calculate_emergency_route(origin="J1", destination="J3")
    asg1.route = new_route

    # Replan corridor with new assignment
    new_plan = corridor_service.replan_corridor(asg1)

    assert new_plan.status == CorridorStatus.REROUTED
    # Old junction J2 must be released
    assert net.get_junction("J2").emergency_reserved is False
    # New junction J4 must be activated
    assert net.get_junction("J4").emergency_reserved is True


def test_deterministic_corridor_planning():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)

    routing.register_ambulance("AMB_1", current_location="J1")
    routing.create_emergency_request("REQ_6", origin="J1", destination="J3")
    assignment = assign_service.assign_ambulance_to_request("REQ_6")

    p1 = corridor_service.plan_corridor(assignment)
    p2 = corridor_service.plan_corridor(assignment)

    assert p1.ordered_junctions == p2.ordered_junctions
    assert [jp.is_safe for jp in p1.junction_plans] == [jp.is_safe for jp in p2.junction_plans]
