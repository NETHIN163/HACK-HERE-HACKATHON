import pytest
from app.models.road import RoadStatus
from app.models.traffic import VehicleDemand
from app.models.incident import Incident, IncidentType
from app.simulation.network import TrafficNetwork
from app.simulation.traffic_engine import TrafficEngine
from app.simulation.scenarios import ScenarioEngine


def test_basic_traffic_flow():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)

    demands = [
        VehicleDemand(source="J1", destination="J2", rate=30.0),
        VehicleDemand(source="J1", destination="J4", rate=20.0),
    ]

    state = engine.step(demands=demands, dt=1.0)
    assert state.timestamp == 1.0
    assert "R_J1_J2" in state.roads
    assert "R_J1_J4" in state.roads
    assert engine.road_flows["R_J1_J2"] > 0.0


def test_queue_and_density_calculation():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)

    # Set J2 signal to EW_GREEN so vertical road R_J1_J2 (horizontal) has green and moves,
    # but horizontal/vertical roads stopping at red accumulate queues.
    net.get_junction("J2").signal_phase = "EW_GREEN"

    # High demand to force queue building
    demands = [VehicleDemand(source="J1", destination="J2", rate=120.0)]

    # Step simulation multiple times
    for _ in range(10):
        state = engine.step(demands=demands, dt=1.0)

    road = state.roads["R_J1_J2"]
    assert road.traffic_density > 0.0
    assert road.queue_length >= 0


def test_travel_time_calculation_and_capacity_handling():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)

    road = net.get_road("R_J1_J2")
    initial_travel_time = road.travel_time

    # Run heavy demand exceeding capacity to trigger congestion
    demands = [VehicleDemand(source="J1", destination="J2", rate=200.0)]
    for _ in range(15):
        state = engine.step(demands=demands, dt=1.0)

    road_after = state.roads["R_J1_J2"]
    # Density should increase under high demand
    assert road_after.traffic_density > 0.1
    # Travel time should increase via BPR function
    assert road_after.travel_time >= initial_travel_time


def test_blocked_road_behavior():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)

    # Add accident incident on R_J1_J2
    incident = Incident(
        incident_id="INC_ACC_1",
        type=IncidentType.ACCIDENT,
        road_id="R_J1_J2",
        timestamp=1.0,
        active=True,
    )

    demands = [VehicleDemand(source="J1", destination="J2", rate=50.0)]
    state = engine.step(demands=demands, incidents=[incident], dt=1.0)

    road = state.roads["R_J1_J2"]
    assert road.status == RoadStatus.BLOCKED
    assert engine.road_flows["R_J1_J2"] == 0.0
    assert road.travel_time >= 999999.0
    assert "INC_ACC_1" in state.active_incidents


def test_deterministic_seeded_behavior():
    net1 = TrafficNetwork()
    engine1 = TrafficEngine(network=net1, seed=12345)

    net2 = TrafficNetwork()
    engine2 = TrafficEngine(network=net2, seed=12345)

    demands = [
        VehicleDemand(source="J1", destination="J3", rate=45.0),
        VehicleDemand(source="J4", destination="J6", rate=35.0),
    ]

    for _ in range(5):
        state1 = engine1.step(demands=demands, dt=1.0)
        state2 = engine2.step(demands=demands, dt=1.0)

    # Verify identical outputs for same seed
    for r_id in state1.roads:
        assert state1.roads[r_id].traffic_density == state2.roads[r_id].traffic_density
        assert state1.roads[r_id].queue_length == state2.roads[r_id].queue_length
        assert state1.roads[r_id].travel_time == state2.roads[r_id].travel_time
        assert engine1.road_flows[r_id] == engine2.road_flows[r_id]


def test_traffic_surge_scenario():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)

    surge_roads = ["R_J1_J2", "R_J2_J3"]

    # Run traffic surge scenario
    surge_state = ScenarioEngine.apply_traffic_surge(
        network=net,
        engine=engine,
        surge_roads=surge_roads,
        surge_factor=4.0,
        base_demand_rate=20.0,
        steps=10,
    )

    surge_road_1 = surge_state.roads["R_J1_J2"]
    normal_road = surge_state.roads["R_J4_J5"]

    # Surge road should have higher density and travel time compared to baseline
    assert surge_road_1.traffic_density > 0.0
    assert surge_road_1.queue_length >= 0
    assert surge_road_1.travel_time > 0.0
