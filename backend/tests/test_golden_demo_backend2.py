import pytest
import time
from app.models.emergency import AmbulanceStatus, EmergencyPriority, RequestStatus, RouteStatus
from app.models.emergency_conflict import ConflictStatus
from app.models.green_corridor import CorridorStatus
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork
from app.simulation.signal_engine import SignalController
from app.services.traffic_service import TrafficService
from app.services.incident_service import IncidentService
from app.services.emergency_routing_service import EmergencyRoutingService
from app.services.ambulance_assignment_service import AmbulanceAssignmentService
from app.optimization.qubo_formulation import QUBOFormulationService
from app.optimization.qaoa_execution import QAOAExecutionService
from app.services.green_corridor_service import GreenCorridorService
from app.services.emergency_conflict_resolution_service import EmergencyConflictResolutionService
from app.services.emergency_service import EmergencyService
from app.services.metrics_service import MetricsService
from app.websocket.events import broadcast_event


def test_backend2_golden_demo_complete_workflow():
    """
    End-to-End Golden Demo Test for Backend Developer 2.
    Validates the complete 17-step workflow:
    Network Initialization -> Initial Traffic -> Traffic Surge -> Incident ->
    Emergency Request -> Ambulance Assignment -> Emergency Route -> QUBO -> QAOA ->
    Green Corridor -> Conflict Resolution -> Signal Priority -> Metrics ->
    Corridor Release -> Ambulance Release -> Final State Validation.
    """

    # ----------------------------------------------------
    # Step 1 — Network Initialization
    # ----------------------------------------------------
    traffic_service = TrafficService(seed=42)
    traffic_service.incident_service.incidents.clear()
    for r in traffic_service.network.roads.values():
        r.status = RoadStatus.OPEN

    net = traffic_service.network
    assert len(net.junctions) >= 6
    assert len(net.roads) >= 10
    j1 = net.get_junction("J1")
    assert j1 is not None

    sig_controller = SignalController(network=net)
    incident_service = traffic_service.incident_service
    metrics_service = traffic_service.metrics_service

    # ----------------------------------------------------
    # Step 2 — Initial Traffic State
    # ----------------------------------------------------
    r_j1_j2 = net.get_road("R_J1_J2")
    assert r_j1_j2 is not None
    assert r_j1_j2.status == RoadStatus.OPEN
    assert r_j1_j2.traffic_density >= 0.0
    assert r_j1_j2.queue_length >= 0

    # ----------------------------------------------------
    # Step 3 — Traffic Surge
    # ----------------------------------------------------
    surge_state = traffic_service.trigger_traffic_surge(["R_J1_J2"], surge_factor=3.0)
    surge_road = net.get_road("R_J1_J2")
    assert surge_road.traffic_density >= 0.0
    assert surge_road.travel_time > 0.0

    # ----------------------------------------------------
    # Step 4 — Incident (Road Blockage)
    # ----------------------------------------------------
    accident = traffic_service.create_incident("INC_GOLDEN_DEMO_2", "ACCIDENT", "R_J1_J4", description="Tanker rollover blocking R_J1_J4")
    assert accident.active is True
    assert net.get_road("R_J1_J4").status == RoadStatus.BLOCKED

    # ----------------------------------------------------
    # Step 5 — Emergency Request
    # ----------------------------------------------------
    emg_svc = EmergencyService(network=net)
    net = emg_svc.network
    # Clear any previous test residue on emergency service
    emg_svc.routing_service.requests.clear()
    emg_svc.routing_service.vehicles.clear()
    emg_svc.routing_service.assignments.clear()
    emg_svc.green_corridor_service.active_plans.clear()

    routing_svc = emg_svc.routing_service
    assign_svc = emg_svc.assignment_service
    qubo_svc = emg_svc.qubo_service
    qaoa_svc = emg_svc.qaoa_service
    corridor_svc = emg_svc.green_corridor_service
    conflict_svc = emg_svc.conflict_service

    req1 = emg_svc.create_request("REQ_GD2_1", origin="J1", destination="J3", priority=EmergencyPriority.CRITICAL)
    assert req1.request_id == "REQ_GD2_1"
    assert req1.status == RequestStatus.PENDING

    # ----------------------------------------------------
    # Step 6 — Ambulance Registration & Assignment
    # ----------------------------------------------------
    amb1 = emg_svc.register_ambulance("AMB_GD2_1", current_location="J1")
    amb2 = emg_svc.register_ambulance("AMB_GD2_2", current_location="J5")

    asg1 = emg_svc.assign_ambulance("REQ_GD2_1", vehicle_id="AMB_GD2_1")
    assert asg1 is not None
    assert asg1.vehicle_id == "AMB_GD2_1"
    assert amb1.status == AmbulanceStatus.DISPATCHED
    assert req1.status == RequestStatus.ASSIGNED

    # Verify duplicate assignment prevention
    with pytest.raises(ValueError):
        emg_svc.assign_ambulance("REQ_GD2_1", vehicle_id="AMB_GD2_2")

    # ----------------------------------------------------
    # Step 7 — Emergency Route Calculation
    # ----------------------------------------------------
    route1 = asg1.route
    assert route1 is not None
    assert route1.status == RouteStatus.CALCULATED
    # R_J1_J4 is BLOCKED, so shortest path from J1 to J3 must go through J2 -> ['J1', 'J2', 'J3']
    assert "R_J1_J4" not in route1.road_ids
    assert route1.path == ["J1", "J2", "J3"]
    assert route1.total_distance > 0.0

    # ----------------------------------------------------
    # Step 8 — QUBO Formulation
    # ----------------------------------------------------
    qubo_prob = qubo_svc.build_qubo_from_routes([route1])
    assert len(qubo_prob.variables) >= 1
    assert qubo_prob.variables[0].var_id == "x_0"
    assert len(qubo_prob.q_matrix) > 0

    # ----------------------------------------------------
    # Step 9 — QAOA Execution
    # ----------------------------------------------------
    qaoa_res = qaoa_svc.execute_qaoa(qubo_prob)
    assert qaoa_res.optimal_binary_vector is not None
    assert qaoa_res.selected_route is not None
    assert "R_J1_J4" not in qaoa_res.selected_route.road_ids

    # ----------------------------------------------------
    # Step 10 — Green Corridor Planning
    # ----------------------------------------------------
    corridor_plan = corridor_svc.plan_corridor(asg1)
    assert corridor_plan.request_id == "REQ_GD2_1"
    assert corridor_plan.status == CorridorStatus.PLANNED
    assert corridor_plan.ordered_junctions == ["J1", "J2", "J3"]

    # ----------------------------------------------------
    # Step 11 — Emergency Conflict Resolution
    # ----------------------------------------------------
    # 11a: Single request case (No Conflict)
    res_no_conflict = conflict_svc.resolve_conflicts([asg1], {"REQ_GD2_1": req1})
    assert res_no_conflict.status == ConflictStatus.NO_CONFLICT

    # 11b: Two conflicting requests case
    # Block R_J5_J6 so REQ_GD2_2 (J5 to J3) must route through J2 (J5 -> J2 -> J3), creating overlap at J2 and J3
    net.update_road_status("R_J5_J6", RoadStatus.BLOCKED)
    req2 = emg_svc.create_request("REQ_GD2_2", origin="J5", destination="J3", priority=EmergencyPriority.MEDIUM)
    asg2 = emg_svc.assign_ambulance("REQ_GD2_2", vehicle_id="AMB_GD2_2")
    assert asg2 is not None

    reqs_map = {"REQ_GD2_1": req1, "REQ_GD2_2": req2}
    conflict_res = conflict_svc.resolve_conflicts([asg1, asg2], reqs_map)

    assert conflict_res.status == ConflictStatus.RESOLVED
    assert "J2" in conflict_res.overlapping_junctions
    assert "REQ_GD2_1" in conflict_res.granted_requests
    assert "REQ_GD2_2" in conflict_res.deferred_requests

    # ----------------------------------------------------
    # Step 12 — Activate Green Corridor
    # ----------------------------------------------------
    activated = corridor_svc.activate_corridor("REQ_GD2_1")
    assert activated.status == CorridorStatus.ACTIVE

    # Verify signal controller has priority reservations
    active_corridors = [p for p in corridor_svc.active_plans.values() if p.status == CorridorStatus.ACTIVE]
    assert len(active_corridors) >= 1
    assert active_corridors[0].request_id == "REQ_GD2_1"

    # ----------------------------------------------------
    # Step 13 — Traffic & Signal Updates API & Events
    # ----------------------------------------------------
    all_requests = emg_svc.get_all_requests()
    assert len(all_requests) >= 2
    all_ambulances = emg_svc.get_all_ambulances()
    assert len(all_ambulances) >= 2

    # Verify event system function
    broadcast_event("traffic.updated", "network:main", {"status": "active"})

    # ----------------------------------------------------
    # Step 14 — Metrics Retrieval
    # ----------------------------------------------------
    metrics = traffic_service.get_metrics()
    assert hasattr(metrics, "average_waiting_time")
    assert hasattr(metrics, "average_queue_length")
    assert hasattr(metrics, "maximum_queue_length")
    assert hasattr(metrics, "traffic_throughput")
    assert hasattr(metrics, "emergency_delay")
    assert hasattr(metrics, "emergency_travel_time")
    assert hasattr(metrics, "fuel_estimate")
    assert hasattr(metrics, "co2_estimate")
    assert hasattr(metrics, "pedestrian_delay")

    # ----------------------------------------------------
    # Step 15 — Corridor Release
    # ----------------------------------------------------
    released_plan = corridor_svc.release_corridor("REQ_GD2_1")
    assert released_plan.status == CorridorStatus.RELEASED

    # Handle corridor release in conflict service so deferred REQ_GD2_2 can gain corridor priority
    release_res = conflict_svc.handle_corridor_release("REQ_GD2_1", remaining_assignments=[asg2], requests=reqs_map)
    assert "REQ_GD2_2" in release_res.granted_requests

    # ----------------------------------------------------
    # Step 16 — Ambulance Release & Lifecycle Completion
    # ----------------------------------------------------
    rel_ok = emg_svc.release_ambulance("AMB_GD2_1", new_location="J3")
    assert rel_ok is True
    assert amb1.status == AmbulanceStatus.AVAILABLE
    assert amb1.current_location == "J3"

    # Reuse released ambulance for a new emergency request
    req3 = emg_svc.create_request("REQ_GD2_3", origin="J3", destination="J6", priority=EmergencyPriority.HIGH)
    asg3 = emg_svc.assign_ambulance("REQ_GD2_3", vehicle_id="AMB_GD2_1")
    assert asg3 is not None
    assert asg3.vehicle_id == "AMB_GD2_1"
    assert amb1.status == AmbulanceStatus.DISPATCHED

    # ----------------------------------------------------
    # Step 17 — Final State Validation
    # ----------------------------------------------------
    assert net.get_road("R_J1_J4").status == RoadStatus.BLOCKED
    assert net.get_road("R_J5_J6").status == RoadStatus.BLOCKED
    active_corridors = [p for p in corridor_svc.active_plans.values() if p.status == CorridorStatus.ACTIVE]
    assert len(active_corridors) <= 1
    assert amb1.status == AmbulanceStatus.DISPATCHED
    assert amb2.status == AmbulanceStatus.DISPATCHED  # (assigned to REQ_GD2_2)

    # Clean release of remaining active corridors & ambulances
    corridor_svc.release_corridor("REQ_GD2_2")
    emg_svc.release_ambulance("AMB_GD2_1")
    emg_svc.release_ambulance("AMB_GD2_2")

    assert amb1.status == AmbulanceStatus.AVAILABLE
    assert amb2.status == AmbulanceStatus.AVAILABLE
    active_corridors_end = [p for p in corridor_svc.active_plans.values() if p.status == CorridorStatus.ACTIVE]
    assert len(active_corridors_end) == 0
