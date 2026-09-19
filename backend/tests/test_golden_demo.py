import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.road import RoadStatus
from app.simulation.signal_engine import SignalController
from app.services.traffic_service import traffic_service

client = TestClient(app)


def test_golden_demo_end_to_end_flow():
    """
    Q-FLOW Backend Developer 1 Golden Demo Verification:
    Tests the complete end-to-end pipeline across all 15 specification stages.
    """

    # Stage 1: Network Initialization
    assert len(traffic_service.network.get_all_junctions()) == 6
    assert len(traffic_service.network.get_all_roads()) == 14

    # Stage 2: Initial Traffic State
    state_0 = traffic_service.get_traffic_state()
    assert state_0.timestamp > 0.0
    assert "R_J1_J2" in state_0.roads
    assert "J1" in state_0.junctions

    # Stage 3: Traffic Simulation Execution
    # Run 3 step ticks to establish baseline flow
    for _ in range(3):
        state_sim = traffic_service.get_traffic_state()
    assert state_sim.timestamp > state_0.timestamp

    # Stage 4: Traffic Surge Scenario (via REST API)
    surge_payload = {
        "surge_roads": ["R_J1_J2"],
        "surge_factor": 3.5,
    }
    resp_surge = client.post("/api/scenarios/traffic-surge", json=surge_payload)
    assert resp_surge.status_code == 200
    surge_state = resp_surge.json()
    assert surge_state["roads"]["R_J1_J2"]["traffic_density"] >= 0.0

    # Stage 5 & 6: Accident Scenario & Road Status BLOCKED
    accident_payload = {
        "road_id": "R_J1_J2",
        "description": "Golden Demo Multi-vehicle collision",
    }
    resp_accident = client.post("/api/scenarios/accident", json=accident_payload)
    assert resp_accident.status_code == 201
    inc_data = resp_accident.json()
    assert inc_data["type"] == "ACCIDENT"
    assert inc_data["road_id"] == "R_J1_J2"

    # Verify road status becomes BLOCKED
    resp_road = client.get("/api/roads/R_J1_J2")
    assert resp_road.status_code == 200
    assert resp_road.json()["status"] == "BLOCKED"

    # Stage 7: Alternative Route Availability & Rerouting
    # Original path J1 -> J3 was ["J1", "J2", "J3"]
    new_path = traffic_service.network.get_shortest_path("J1", "J3", ignore_blocked=True)
    assert new_path is not None
    assert new_path != ["J1", "J2", "J3"]
    assert "R_J1_J2" not in [f"R_{new_path[i]}_{new_path[i+1]}" for i in range(len(new_path) - 1)]

    # Stage 8 & 9: Diversion Impact Estimation & Traffic Queue/Density Update
    impact = traffic_service.diversion_service.estimate_diversion_impact(
        blocked_road_id="R_J1_J2",
        diverted_vehicle_count=45.0,
    )
    assert impact.blocked_road_id == "R_J1_J2"
    assert "R_J1_J2" not in impact.alternative_roads
    assert len(impact.alternative_roads) > 0
    assert impact.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    # Stage 10 & 11: Classical Optimizer Evaluation & Signal Configuration Generation
    resp_opt = client.get("/api/optimization/classical")
    assert resp_opt.status_code == 200
    configs_json = resp_opt.json()
    assert "J1" in configs_json
    assert "green_duration" in configs_json["J1"]

    # Stage 12: Signal Controller Validation & Application
    controller = SignalController(network=traffic_service.network)
    opt_configs = traffic_service.get_classical_optimization()
    for j_id, config in opt_configs.items():
        assert controller.apply_configuration(config) is True
        assert traffic_service.network.get_junction(j_id).green_duration == config.green_duration

    # Stage 13: Metrics Calculation
    resp_metrics = client.get("/api/metrics")
    assert resp_metrics.status_code == 200
    metrics = resp_metrics.json()
    assert metrics["average_waiting_time"] >= 0.0
    assert metrics["average_queue_length"] >= 0.0
    assert metrics["maximum_queue_length"] >= 0
    assert metrics["traffic_throughput"] >= 0.0
    assert metrics["fuel_estimate"] > 0.0
    assert metrics["co2_estimate"] > 0.0

    # Stage 14: REST API Exposure Verification
    assert client.get("/api/traffic").status_code == 200
    assert client.get("/api/traffic/junctions").status_code == 200
    assert client.get("/api/traffic/roads").status_code == 200
    assert client.get("/api/junctions/J1").status_code == 200
    assert client.get("/api/roads/R_J1_J2").status_code == 200
    assert client.get("/api/incidents").status_code == 200

    # Stage 15: WebSocket Event Generation
    events = traffic_service.incident_service.get_pending_events()
    event_types = [e["event"] for e in events]
    assert "incident.created" in event_types
    assert "route.impact_required" in event_types
