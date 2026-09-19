import pytest
from app.models.road import RoadStatus
from app.models.incident import IncidentType
from app.models.traffic import VehicleDemand
from app.simulation.network import TrafficNetwork
from app.simulation.traffic_engine import TrafficEngine
from app.services.incident_service import IncidentService


def test_create_accident_makes_road_blocked():
    net = TrafficNetwork()
    service = IncidentService(network=net)

    incident = service.create_incident(
        incident_id="INC_ACC_100",
        type="ACCIDENT",
        road_id="R_J1_J2",
        description="Multi-car collision",
    )

    assert incident.incident_id == "INC_ACC_100"
    assert incident.type == IncidentType.ACCIDENT
    assert incident.active is True
    # Verify road status updated to BLOCKED
    road = net.get_road("R_J1_J2")
    assert road.status == RoadStatus.BLOCKED


def test_create_road_closure_makes_road_closed():
    net = TrafficNetwork()
    service = IncidentService(network=net)

    incident = service.create_incident(
        incident_id="INC_CLS_200",
        type="ROAD_CLOSURE",
        road_id="R_J2_J3",
        description="Construction maintenance",
    )

    assert incident.incident_id == "INC_CLS_200"
    assert incident.type == IncidentType.ROAD_CLOSURE
    # Verify road status updated to CLOSED
    road = net.get_road("R_J2_J3")
    assert road.status == RoadStatus.CLOSED


def test_routing_avoids_affected_road():
    net = TrafficNetwork()
    service = IncidentService(network=net)

    # Initial shortest path J1 to J3 is J1 -> J2 -> J3
    assert net.get_shortest_path("J1", "J3", ignore_blocked=True) == ["J1", "J2", "J3"]

    # Create accident on R_J1_J2
    service.create_incident(
        incident_id="INC_ACC_300",
        type="ACCIDENT",
        road_id="R_J1_J2",
    )

    # Routing must immediately avoid R_J1_J2 and reroute
    new_path = net.get_shortest_path("J1", "J3", ignore_blocked=True)
    assert new_path is not None
    assert new_path != ["J1", "J2", "J3"]
    assert "R_J1_J2" not in [f"R_{new_path[i]}_{new_path[i+1]}" for i in range(len(new_path)-1)]


def test_invalid_road_id_raises_error():
    net = TrafficNetwork()
    service = IncidentService(network=net)

    with pytest.raises(ValueError, match="Invalid road ID"):
        service.create_incident(
            incident_id="INC_ERR_1",
            type="ACCIDENT",
            road_id="R_NON_EXISTENT",
        )


def test_invalid_incident_type_raises_error():
    net = TrafficNetwork()
    service = IncidentService(network=net)

    with pytest.raises(ValueError, match="Invalid incident type"):
        service.create_incident(
            incident_id="INC_ERR_2",
            type="WILDFIRE",
            road_id="R_J1_J2",
        )


def test_incident_update_and_resolution():
    net = TrafficNetwork()
    service = IncidentService(network=net)

    # Create incident
    service.create_incident(
        incident_id="INC_ACC_400",
        type="ACCIDENT",
        road_id="R_J1_J2",
    )
    assert net.get_road("R_J1_J2").status == RoadStatus.BLOCKED

    # Update severity
    updated = service.update_incident("INC_ACC_400", severity=2.0)
    assert updated.severity == 2.0
    assert net.get_road("R_J1_J2").status == RoadStatus.BLOCKED

    # Resolve incident (active=False)
    resolved = service.update_incident("INC_ACC_400", active=False)
    assert resolved.active is False
    # Road status restored to OPEN
    assert net.get_road("R_J1_J2").status == RoadStatus.OPEN


def test_events_prepared_for_websocket():
    net = TrafficNetwork()
    service = IncidentService(network=net)

    service.create_incident(
        incident_id="INC_ACC_500",
        type="ACCIDENT",
        road_id="R_J1_J2",
    )

    events = service.get_pending_events()
    assert len(events) == 2
    event_names = [e["event"] for e in events]
    assert "incident.created" in event_names
    assert "route.impact_required" in event_names

    # Queue cleared after retrieve
    assert len(service.get_pending_events()) == 0

    # Update incident
    service.update_incident("INC_ACC_500", active=False)
    update_events = service.get_pending_events()
    assert len(update_events) == 2
    assert update_events[0]["event"] == "incident.updated"
    assert update_events[1]["event"] == "route.impact_required"


def test_traffic_simulator_handles_incident_from_service():
    net = TrafficNetwork()
    service = IncidentService(network=net)
    engine = TrafficEngine(network=net, seed=42)

    incident = service.create_incident(
        incident_id="INC_ACC_600",
        type="ACCIDENT",
        road_id="R_J1_J2",
    )

    demands = [VehicleDemand(source="J1", destination="J2", rate=50.0)]
    state = engine.step(demands=demands, incidents=[incident], dt=1.0)

    road = state.roads["R_J1_J2"]
    assert road.status == RoadStatus.BLOCKED
    assert engine.road_flows["R_J1_J2"] == 0.0
    assert road.travel_time >= 999999.0
