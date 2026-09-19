import pytest
from app.models.road import Road, RoadStatus
from app.models.junction import Junction
from app.models.traffic import TrafficState, VehicleDemand
from app.models.signal import SignalPhase, SignalConfiguration
from app.models.incident import Incident, IncidentType
from app.simulation.network import TrafficNetwork


def test_road_model():
    road = Road(
        road_id="R_J1_J2",
        source="J1",
        destination="J2",
        distance=500.0,
        capacity=60.0,
        travel_time=36.0,
        traffic_density=0.2,
        queue_length=5,
        status=RoadStatus.OPEN,
    )
    assert road.road_id == "R_J1_J2"
    assert road.source == "J1"
    assert road.destination == "J2"
    assert road.distance == 500.0
    assert road.status == RoadStatus.OPEN

    # Verify status enum values
    assert RoadStatus.OPEN == "OPEN"
    assert RoadStatus.CONGESTED == "CONGESTED"
    assert RoadStatus.BLOCKED == "BLOCKED"
    assert RoadStatus.CLOSED == "CLOSED"


def test_junction_model():
    junction = Junction(
        junction_id="J1",
        signal_phase="NS_GREEN",
        green_duration=30.0,
        red_duration=30.0,
        queue_length=3,
        vehicle_density=0.15,
        pedestrian_count=4,
        emergency_reserved=False,
    )
    assert junction.junction_id == "J1"
    assert junction.signal_phase == "NS_GREEN"
    assert junction.pedestrian_count == 4
    assert junction.emergency_reserved is False


def test_traffic_signal_incident_models():
    demand = VehicleDemand(source="J1", destination="J3", rate=12.5)
    assert demand.rate == 12.5

    sig_config = SignalConfiguration(
        junction_id="J1",
        signal_phase=SignalPhase.NS_GREEN,
        green_duration=45.0,
        red_duration=15.0,
    )
    assert sig_config.signal_phase == SignalPhase.NS_GREEN

    incident = Incident(
        incident_id="INC_001",
        type=IncidentType.ACCIDENT,
        road_id="R_J1_J2",
        severity=1.5,
        timestamp=1000.0,
    )
    assert incident.type == IncidentType.ACCIDENT
    assert incident.active is True


def test_network_initialization():
    net = TrafficNetwork()

    # Check 6 junctions created
    junctions = net.get_all_junctions()
    assert len(junctions) == 6
    j_ids = {j.junction_id for j in junctions}
    assert j_ids == {"J1", "J2", "J3", "J4", "J5", "J6"}

    # Check roads created (7 bi-directional pairs = 14 roads)
    roads = net.get_all_roads()
    assert len(roads) == 14

    # Verify outbound and inbound lookup
    outbound_j1 = net.get_outbound_roads("J1")
    outbound_ids = {r.road_id for r in outbound_j1}
    assert outbound_ids == {"R_J1_J2", "R_J1_J4"}


def test_network_multi_path_and_blocking():
    net = TrafficNetwork()

    # Find paths from J1 to J3
    paths_all = net.find_all_paths("J1", "J3", ignore_blocked=True)
    assert len(paths_all) > 1
    # Check that direct path J1 -> J2 -> J3 is present
    assert ["J1", "J2", "J3"] in paths_all
    # Check that alternative path J1 -> J4 -> J5 -> J6 -> J3 is present
    assert ["J1", "J4", "J5", "J6", "J3"] in paths_all

    # Verify shortest path initially goes through J1 -> J2 -> J3
    shortest = net.get_shortest_path("J1", "J3", ignore_blocked=True)
    assert shortest == ["J1", "J2", "J3"]

    # Block road R_J1_J2
    net.update_road_status("R_J1_J2", RoadStatus.BLOCKED)

    # Search for available paths ignoring blocked roads
    paths_after_block = net.find_all_paths("J1", "J3", ignore_blocked=True)

    # Path containing J1 -> J2 must no longer be present
    assert ["J1", "J2", "J3"] not in paths_after_block

    # Alternate paths avoiding R_J1_J2 must still exist
    assert ["J1", "J4", "J5", "J6", "J3"] in paths_after_block

    # Shortest path must now reroute around the blocked road
    new_shortest = net.get_shortest_path("J1", "J3", ignore_blocked=True)
    assert new_shortest != ["J1", "J2", "J3"]
    assert new_shortest[0] == "J1"
    assert new_shortest[-1] == "J3"
    assert "J2" not in new_shortest or new_shortest.index("J2") != 1
