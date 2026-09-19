import pytest
from app.models.emergency import EmergencyPriority
from app.models.emergency_conflict import ConflictStatus
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork
from app.simulation.signal_engine import SignalController
from app.services.emergency_routing_service import EmergencyRoutingService
from app.services.ambulance_assignment_service import AmbulanceAssignmentService
from app.services.green_corridor_service import GreenCorridorService
from app.services.emergency_conflict_resolution_service import EmergencyConflictResolutionService


def test_conflict_detection_no_overlap():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)
    conflict_service = EmergencyConflictResolutionService(
        green_corridor_service=corridor_service,
        signal_controller=sig_controller,
        network=net,
    )

    # REQ_1 route: J1 -> J2
    routing.register_ambulance("AMB_1", current_location="J1")
    r1 = routing.create_emergency_request("REQ_1", origin="J1", destination="J2")
    asg1 = assign_service.assign_ambulance_to_request("REQ_1")

    # REQ_2 route: J5 -> J6
    routing.register_ambulance("AMB_2", current_location="J5")
    r2 = routing.create_emergency_request("REQ_2", origin="J5", destination="J6")
    asg2 = assign_service.assign_ambulance_to_request("REQ_2")

    detection = conflict_service.detect_conflicts([asg1, asg2])
    assert detection.status == ConflictStatus.NO_CONFLICT
    assert len(detection.overlapping_junctions) == 0


def test_single_junction_overlap_detection_and_resolution():
    net = TrafficNetwork()
    net.update_road_status("R_J1_J4", RoadStatus.BLOCKED)
    net.update_road_status("R_J5_J6", RoadStatus.BLOCKED)
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)
    conflict_service = EmergencyConflictResolutionService(
        green_corridor_service=corridor_service,
        signal_controller=sig_controller,
        network=net,
    )

    # REQ_1 (CRITICAL priority): J1 -> J2 -> J3
    routing.register_ambulance("AMB_1", current_location="J1")
    r1 = routing.create_emergency_request("REQ_1", origin="J1", destination="J3", priority=EmergencyPriority.CRITICAL)
    asg1 = assign_service.assign_ambulance_to_request("REQ_1")

    # REQ_2 (MEDIUM priority): J5 -> J2 -> J3 (overlaps at J2 and J3)
    routing.register_ambulance("AMB_2", current_location="J5")
    r2 = routing.create_emergency_request("REQ_2", origin="J5", destination="J3", priority=EmergencyPriority.MEDIUM)
    asg2 = assign_service.assign_ambulance_to_request("REQ_2")

    requests_dict = {"REQ_1": r1, "REQ_2": r2}

    res = conflict_service.resolve_conflicts([asg1, asg2], requests_dict)

    assert res.status == ConflictStatus.RESOLVED
    assert "J2" in res.overlapping_junctions
    assert "REQ_1" in res.granted_requests
    assert "REQ_2" in res.deferred_requests

    # Verify resolution reason contains explanation
    j2_res = next(j for j in res.junction_resolutions if j.junction_id == "J2")
    assert j2_res.winner_request_id == "REQ_1"
    assert "REQ_2" in j2_res.deferred_request_ids
    assert "granted priority" in j2_res.resolution_reason.lower()


def test_deterministic_ranking_by_priority_travel_time_and_request_id():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)
    conflict_service = EmergencyConflictResolutionService(
        green_corridor_service=corridor_service,
        signal_controller=sig_controller,
        network=net,
    )

    # Two requests with same priority (HIGH) and identical routes J1->J2->J3
    routing.register_ambulance("AMB_A", current_location="J1")
    r_a = routing.create_emergency_request("REQ_A", origin="J1", destination="J3", priority=EmergencyPriority.HIGH)
    asg_a = assign_service.assign_ambulance_to_request("REQ_A")

    routing.register_ambulance("AMB_B", current_location="J1")
    r_b = routing.create_emergency_request("REQ_B", origin="J1", destination="J3", priority=EmergencyPriority.HIGH)
    asg_b = assign_service.assign_ambulance_to_request("REQ_B")

    reqs = {"REQ_A": r_a, "REQ_B": r_b}

    # REQ_B comes first alphabetically in tie-breaking if all else equal, or deterministic stable sort
    res1 = conflict_service.resolve_conflicts([asg_a, asg_b], reqs)
    res2 = conflict_service.resolve_conflicts([asg_a, asg_b], reqs)

    assert res1.granted_requests == res2.granted_requests
    assert res1.deferred_requests == res2.deferred_requests


def test_pedestrian_safety_defers_all_competing_priority_requests():
    net = TrafficNetwork()
    net.update_road_status("R_J1_J4", RoadStatus.BLOCKED)
    net.update_road_status("R_J5_J6", RoadStatus.BLOCKED)
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)
    conflict_service = EmergencyConflictResolutionService(
        green_corridor_service=corridor_service,
        signal_controller=sig_controller,
        network=net,
    )

    # Activate pedestrian crossing at shared junction J2
    sig_controller.set_pedestrian_crossing("J2", pedestrian_count=10, clearance_seconds=12.0)

    routing.register_ambulance("AMB_1", current_location="J1")
    r1 = routing.create_emergency_request("REQ_1", origin="J1", destination="J3", priority=EmergencyPriority.CRITICAL)
    asg1 = assign_service.assign_ambulance_to_request("REQ_1")

    routing.register_ambulance("AMB_2", current_location="J5")
    r2 = routing.create_emergency_request("REQ_2", origin="J5", destination="J3", priority=EmergencyPriority.HIGH)
    asg2 = assign_service.assign_ambulance_to_request("REQ_2")

    reqs = {"REQ_1": r1, "REQ_2": r2}

    res = conflict_service.resolve_conflicts([asg1, asg2], reqs)

    # J2 resolution must defer both priority requests due to active pedestrian clearance
    j2_res = next(j for j in res.junction_resolutions if j.junction_id == "J2")
    assert j2_res.winner_request_id is None
    assert "REQ_1" in j2_res.deferred_request_ids
    assert "REQ_2" in j2_res.deferred_request_ids
    assert "pedestrian crossing active" in j2_res.resolution_reason.lower()


def test_corridor_release_removes_conflict_and_grants_deferred_request():
    net = TrafficNetwork()
    net.update_road_status("R_J1_J4", RoadStatus.BLOCKED)
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)
    conflict_service = EmergencyConflictResolutionService(
        green_corridor_service=corridor_service,
        signal_controller=sig_controller,
        network=net,
    )

    routing.register_ambulance("AMB_1", current_location="J1")
    r1 = routing.create_emergency_request("REQ_1", origin="J1", destination="J3", priority=EmergencyPriority.CRITICAL)
    asg1 = assign_service.assign_ambulance_to_request("REQ_1")

    routing.register_ambulance("AMB_2", current_location="J5")
    r2 = routing.create_emergency_request("REQ_2", origin="J5", destination="J3", priority=EmergencyPriority.MEDIUM)
    asg2 = assign_service.assign_ambulance_to_request("REQ_2")

    reqs = {"REQ_1": r1, "REQ_2": r2}

    # Resolve initial conflict (REQ_1 wins J2/J3, REQ_2 deferred)
    res_initial = conflict_service.resolve_conflicts([asg1, asg2], reqs)
    assert "REQ_2" in res_initial.deferred_requests

    # Complete/release REQ_1 corridor
    res_release = conflict_service.handle_corridor_release("REQ_1", remaining_assignments=[asg2], requests=reqs)

    # REQ_2 should now be conflict-free and granted priority
    assert res_release.status in [ConflictStatus.NO_CONFLICT, ConflictStatus.RESOLVED]
    assert "REQ_2" in res_release.granted_requests


def test_route_change_updates_conflict_resolution():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)
    sig_controller = SignalController(network=net)
    corridor_service = GreenCorridorService(signal_controller=sig_controller, network=net)
    conflict_service = EmergencyConflictResolutionService(
        green_corridor_service=corridor_service,
        signal_controller=sig_controller,
        network=net,
    )

    routing.register_ambulance("AMB_1", current_location="J1")
    r1 = routing.create_emergency_request("REQ_1", origin="J1", destination="J2")
    asg1 = assign_service.assign_ambulance_to_request("REQ_1")

    routing.register_ambulance("AMB_2", current_location="J4")
    r2 = routing.create_emergency_request("REQ_2", origin="J4", destination="J6")
    asg2 = assign_service.assign_ambulance_to_request("REQ_2")

    reqs = {"REQ_1": r1, "REQ_2": r2}

    # Initially no overlap (J1->J2->J3 vs J4->J5->J6)
    res_initial = conflict_service.resolve_conflicts([asg1, asg2], reqs)
    assert res_initial.status == ConflictStatus.NO_CONFLICT

    # Block R_J4_J5, so REQ_2 is rerouted through J4->J1->J2->J3 (now overlapping at J1/J2/J3)
    net.get_road("R_J4_J5").status = "BLOCKED"
    new_route2 = routing.calculate_emergency_route(origin="J4", destination="J6")
    asg2.route = new_route2

    res_reroute = conflict_service.handle_route_change(asg2, active_assignments=[asg1, asg2], requests=reqs)
    assert res_reroute.status == ConflictStatus.RESOLVED
    assert len(res_reroute.overlapping_junctions) > 0
