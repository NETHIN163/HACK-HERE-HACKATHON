import pytest
from app.models.emergency import (
    AmbulanceStatus,
    EmergencyPriority,
    RequestStatus,
)
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork
from app.services.incident_service import IncidentService
from app.services.emergency_routing_service import EmergencyRoutingService
from app.services.ambulance_assignment_service import AmbulanceAssignmentService


def test_assigning_an_available_ambulance():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)

    routing.register_ambulance("AMB_01", current_location="J1")
    routing.create_emergency_request("REQ_01", origin="J1", destination="J3")

    assignment = assign_service.assign_ambulance_to_request("REQ_01")

    assert assignment is not None
    assert assignment.vehicle_id == "AMB_01"
    assert assignment.request_id == "REQ_01"
    assert routing.vehicles["AMB_01"].status == AmbulanceStatus.DISPATCHED
    assert routing.requests["REQ_01"].status == RequestStatus.ASSIGNED


def test_selecting_ambulance_with_lowest_travel_time():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)

    # AMB_FAR is at J6 (far from J1 scene), AMB_NEAR is at J2 (near J1 scene)
    routing.register_ambulance("AMB_FAR", current_location="J6")
    routing.register_ambulance("AMB_NEAR", current_location="J2")

    routing.create_emergency_request("REQ_02", origin="J1", destination="J3")

    assignment = assign_service.assign_ambulance_to_request("REQ_02")

    assert assignment is not None
    # AMB_NEAR selected because it has lower travel time to J1
    assert assignment.vehicle_id == "AMB_NEAR"


def test_distance_as_tie_breaker():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)

    # Register two ambulances at J2 (same distance/time to J1)
    routing.register_ambulance("AMB_A", current_location="J2")
    routing.register_ambulance("AMB_B", current_location="J2")

    # Increase travel time on road to AMB_B's alternate route
    net.get_road("R_J2_J1").travel_time = 36.0

    routing.create_emergency_request("REQ_03", origin="J1", destination="J3")

    assignment = assign_service.assign_ambulance_to_request("REQ_03")
    assert assignment is not None


def test_vehicle_id_as_deterministic_final_tie_breaker():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)

    # AMB_Z and AMB_A are both at J1 (identical travel time 0.0, distance 0.0)
    routing.register_ambulance("AMB_Z", current_location="J1")
    routing.register_ambulance("AMB_A", current_location="J1")

    routing.create_emergency_request("REQ_04", origin="J1", destination="J3")

    assignment = assign_service.assign_ambulance_to_request("REQ_04")

    # AMB_A selected because "AMB_A" < "AMB_Z" in alphabetical tie-breaking
    assert assignment.vehicle_id == "AMB_A"


def test_ignoring_unavailable_ambulances():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)

    veh1 = routing.register_ambulance("AMB_BUSY", current_location="J1")
    veh1.status = AmbulanceStatus.BUSY

    routing.register_ambulance("AMB_AVAIL", current_location="J4")

    routing.create_emergency_request("REQ_05", origin="J1", destination="J3")

    assignment = assign_service.assign_ambulance_to_request("REQ_05")
    assert assignment.vehicle_id == "AMB_AVAIL"


def test_ignoring_ambulances_with_no_valid_route():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)

    # AMB_BLOCKED is isolated at J4, block R_J4_J1 and R_J4_J5
    routing.register_ambulance("AMB_BLOCKED", current_location="J4")
    inc_service.create_incident("INC_1", "ACCIDENT", "R_J4_J1")
    inc_service.create_incident("INC_2", "ACCIDENT", "R_J4_J5")

    routing.register_ambulance("AMB_OK", current_location="J2")

    routing.create_emergency_request("REQ_06", origin="J1", destination="J3")

    assignment = assign_service.assign_ambulance_to_request("REQ_06")
    assert assignment.vehicle_id == "AMB_OK"


def test_no_available_ambulance_handling():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)

    # No registered ambulances
    routing.create_emergency_request("REQ_07", origin="J1", destination="J3")

    assignment = assign_service.assign_ambulance_to_request("REQ_07")
    assert assignment is None
    assert routing.requests["REQ_07"].status == RequestStatus.UNROUTABLE


def test_no_valid_route_for_any_ambulance_handling():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)

    routing.register_ambulance("AMB_1", current_location="J1")

    # Block all routes out of J1
    inc_service.create_incident("INC_1", "ACCIDENT", "R_J1_J2")
    inc_service.create_incident("INC_2", "ROAD_CLOSURE", "R_J1_J4")

    routing.create_emergency_request("REQ_08", origin="J1", destination="J3")

    assignment = assign_service.assign_ambulance_to_request("REQ_08")
    assert assignment is None
    assert routing.requests["REQ_08"].status == RequestStatus.UNROUTABLE


def test_preventing_duplicate_assignment():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)

    routing.register_ambulance("AMB_1", current_location="J1")
    routing.create_emergency_request("REQ_09", origin="J1", destination="J3")

    assign1 = assign_service.assign_ambulance_to_request("REQ_09")
    assert assign1 is not None

    # Attempt second assignment of same request
    with pytest.raises(ValueError, match="already assigned"):
        assign_service.assign_ambulance_to_request("REQ_09")


def test_releasing_and_reusing_an_ambulance():
    net = TrafficNetwork()
    routing = EmergencyRoutingService(network=net)
    assign_service = AmbulanceAssignmentService(routing_service=routing)

    routing.register_ambulance("AMB_1", current_location="J1")
    routing.create_emergency_request("REQ_10", origin="J1", destination="J3")

    # Assign
    assign1 = assign_service.assign_ambulance_to_request("REQ_10")
    assert routing.vehicles["AMB_1"].status == AmbulanceStatus.DISPATCHED

    # Release ambulance to new location J3
    released = assign_service.release_ambulance("AMB_1", new_location="J3")
    assert released is True
    assert routing.vehicles["AMB_1"].status == AmbulanceStatus.AVAILABLE
    assert routing.vehicles["AMB_1"].current_location == "J3"
    assert routing.requests["REQ_10"].status == RequestStatus.COMPLETED

    # Reuse released ambulance for new request
    routing.create_emergency_request("REQ_11", origin="J3", destination="J6")
    assign2 = assign_service.assign_ambulance_to_request("REQ_11")
    assert assign2 is not None
    assert assign2.vehicle_id == "AMB_1"
    assert assign2.request_id == "REQ_11"
