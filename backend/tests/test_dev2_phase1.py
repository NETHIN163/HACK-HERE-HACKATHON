import pytest
from app.models.emergency import (
    AmbulanceStatus,
    EmergencyAssignment,
    EmergencyPriority,
    EmergencyRequest,
    EmergencyRoute,
    EmergencyVehicle,
    RequestStatus,
    RouteStatus,
)
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork
from app.services.incident_service import IncidentService
from app.services.emergency_routing_service import EmergencyRoutingService


def test_emergency_request_creation():
    net = TrafficNetwork()
    service = EmergencyRoutingService(network=net)

    req = service.create_emergency_request(
        request_id="REQ_AMB_10",
        origin="J1",
        destination="J3",
        priority=EmergencyPriority.CRITICAL,
    )

    assert req.request_id == "REQ_AMB_10"
    assert req.origin == "J1"
    assert req.destination == "J3"
    assert req.priority == EmergencyPriority.CRITICAL
    assert req.status == RequestStatus.PENDING


def test_ambulance_vehicle_creation():
    net = TrafficNetwork()
    service = EmergencyRoutingService(network=net)

    veh = service.register_ambulance(vehicle_id="AMB_01", current_location="J1")

    assert veh.vehicle_id == "AMB_01"
    assert veh.current_location == "J1"
    assert veh.status == AmbulanceStatus.AVAILABLE
    assert veh.assigned_request_id is None


def test_emergency_assignment_model():
    net = TrafficNetwork()
    service = EmergencyRoutingService(network=net)

    service.register_ambulance(vehicle_id="AMB_02", current_location="J1")
    service.create_emergency_request(request_id="REQ_100", origin="J1", destination="J3")

    assignment = service.assign_emergency(request_id="REQ_100", vehicle_id="AMB_02")
    assert assignment is not None
    assert assignment.request_id == "REQ_100"
    assert assignment.vehicle_id == "AMB_02"
    assert assignment.route.origin == "J1"
    assert assignment.route.destination == "J3"
    assert service.vehicles["AMB_02"].status == AmbulanceStatus.DISPATCHED
    assert service.requests["REQ_100"].status == RequestStatus.ASSIGNED


def test_valid_emergency_route_calculation():
    net = TrafficNetwork()
    service = EmergencyRoutingService(network=net)

    route = service.calculate_emergency_route(origin="J1", destination="J3")
    assert route is not None
    assert route.origin == "J1"
    assert route.destination == "J3"
    assert route.path == ["J1", "J2", "J3"]
    assert route.road_ids == ["R_J1_J2", "R_J2_J3"]
    assert route.total_distance > 0.0
    assert route.estimated_travel_time > 0.0


def test_route_avoiding_blocked_road():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    service = EmergencyRoutingService(network=net)

    # Block R_J1_J2 with an accident
    inc_service.create_incident("INC_ACC_1", "ACCIDENT", "R_J1_J2")
    assert net.get_road("R_J1_J2").status == RoadStatus.BLOCKED

    route = service.calculate_emergency_route(origin="J1", destination="J3")
    assert route is not None
    # Must avoid R_J1_J2
    assert "R_J1_J2" not in route.road_ids
    assert route.path[0] == "J1"
    assert route.path[-1] == "J3"


def test_route_avoiding_closed_road():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    service = EmergencyRoutingService(network=net)

    # Close R_J1_J2 with road closure
    inc_service.create_incident("INC_CLS_1", "ROAD_CLOSURE", "R_J1_J2")
    assert net.get_road("R_J1_J2").status == RoadStatus.CLOSED

    route = service.calculate_emergency_route(origin="J1", destination="J3")
    assert route is not None
    assert "R_J1_J2" not in route.road_ids


def test_route_using_alternative_path():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    service = EmergencyRoutingService(network=net)

    # Block direct route R_J1_J2
    inc_service.create_incident("INC_1", "ACCIDENT", "R_J1_J2")

    route = service.calculate_emergency_route(origin="J1", destination="J3")
    assert route is not None
    # Check alternate path utilized e.g. J1 -> J4 -> J5 -> J6 -> J3
    assert route.path == ["J1", "J4", "J5", "J6", "J3"]


def test_no_available_route_when_all_paths_blocked():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    service = EmergencyRoutingService(network=net)

    # Block all outbound roads from J1: R_J1_J2 and R_J1_J4
    inc_service.create_incident("INC_1", "ACCIDENT", "R_J1_J2")
    inc_service.create_incident("INC_2", "ROAD_CLOSURE", "R_J1_J4")

    route = service.calculate_emergency_route(origin="J1", destination="J3")
    assert route is None


def test_travel_time_calculation():
    net = TrafficNetwork()
    net.update_road_status("R_J1_J4", RoadStatus.BLOCKED)
    service = EmergencyRoutingService(network=net)

    # Increase travel time on R_J1_J2
    net.get_road("R_J1_J2").travel_time = 120.0
    net.get_road("R_J2_J3").travel_time = 60.0

    route = service.calculate_emergency_route(origin="J1", destination="J3")
    assert route is not None
    # 120 + 60 = 180s
    assert route.estimated_travel_time == 180.0

