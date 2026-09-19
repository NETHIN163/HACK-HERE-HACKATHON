import pytest
from app.models.road import RoadStatus
from app.simulation.network import TrafficNetwork
from app.simulation.traffic_engine import TrafficEngine
from app.services.incident_service import IncidentService
from app.services.metrics_service import MetricsService
from app.services.diversion_service import DiversionService


def test_metrics_average_waiting_time_queue_and_max_queue():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)

    state = engine.step(demands=[], dt=1.0)
    # Inject queues
    state.roads["R_J1_J2"].queue_length = 10
    state.roads["R_J2_J3"].queue_length = 20

    metrics = MetricsService.calculate_metrics(state, engine=engine)

    assert metrics.maximum_queue_length == 20
    assert metrics.average_queue_length > 0.0
    assert metrics.average_waiting_time >= 0.0


def test_metrics_traffic_throughput_and_emergency_delay():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)

    state = engine.step(demands=[], dt=1.0)
    metrics = MetricsService.calculate_metrics(state, engine=engine, emergency_route=["R_J1_J2", "R_J2_J3"])

    assert metrics.traffic_throughput >= 0.0
    assert metrics.emergency_travel_time > 0.0
    assert metrics.emergency_delay >= 0.0


def test_metrics_fuel_co2_and_pedestrian_delay():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)

    # Set pedestrian wait count
    net.get_junction("J1").pedestrian_count = 8
    state = engine.step(demands=[], dt=1.0)

    metrics = MetricsService.calculate_metrics(state, engine=engine)

    assert metrics.fuel_estimate > 0.0
    assert metrics.co2_estimate == round(metrics.fuel_estimate * 2.31, 2)
    assert metrics.pedestrian_delay >= 40.0  # 8 peds * 5.0s


def test_metrics_deterministic_reproducibility():
    net = TrafficNetwork()
    engine = TrafficEngine(network=net, seed=42)

    state = engine.step(demands=[], dt=1.0)

    m1 = MetricsService.calculate_metrics(state, engine=engine)
    m2 = MetricsService.calculate_metrics(state, engine=engine)

    assert m1.average_waiting_time == m2.average_waiting_time
    assert m1.average_queue_length == m2.average_queue_length
    assert m1.maximum_queue_length == m2.maximum_queue_length
    assert m1.traffic_throughput == m2.traffic_throughput
    assert m1.fuel_estimate == m2.fuel_estimate
    assert m1.co2_estimate == m2.co2_estimate
    assert m1.pedestrian_delay == m2.pedestrian_delay


def test_diversion_impact_from_blocked_road():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    div_service = DiversionService(network=net)

    # Block R_J1_J2
    inc_service.create_incident("INC_1", "ACCIDENT", "R_J1_J2")

    impact = div_service.estimate_diversion_impact(
        blocked_road_id="R_J1_J2",
        diverted_vehicle_count=30.0,
    )

    assert impact.blocked_road_id == "R_J1_J2"
    assert len(impact.alternative_roads) > 0
    # Blocked road R_J1_J2 must not be in alternative roads
    assert "R_J1_J2" not in impact.alternative_roads


def test_diversion_excludes_blocked_and_closed_roads_from_alternatives():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    div_service = DiversionService(network=net)

    # Block R_J1_J2 (target) and R_J1_J4 (potential alternate)
    inc_service.create_incident("INC_1", "ACCIDENT", "R_J1_J2")
    inc_service.create_incident("INC_2", "ROAD_CLOSURE", "R_J1_J4")

    # Pass R_J1_J4 explicitly as candidate
    impact = div_service.estimate_diversion_impact(
        blocked_road_id="R_J1_J2",
        candidate_roads=["R_J1_J4", "R_J2_J5"],
        diverted_vehicle_count=30.0,
    )

    # R_J1_J4 is CLOSED and must be filtered out
    assert "R_J1_J4" not in impact.alternative_roads
    assert "R_J2_J5" in impact.alternative_roads


def test_diversion_capacity_queue_congestion_and_affected_junctions():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)
    div_service = DiversionService(network=net)

    inc_service.create_incident("INC_1", "ACCIDENT", "R_J1_J2")

    impact = div_service.estimate_diversion_impact(
        blocked_road_id="R_J1_J2",
        diverted_vehicle_count=60.0,
    )

    for alt_r in impact.alternative_roads:
        assert alt_r in impact.predicted_traffic
        assert alt_r in impact.predicted_queue
        assert alt_r in impact.predicted_congestion
        assert impact.predicted_congestion[alt_r] >= 0.0

    assert len(impact.affected_junctions) > 0
    assert impact.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
