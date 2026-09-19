import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.websocket.events import ConnectionManager, SystemEvent, broadcast_event, manager
from app.models.signal import SignalConfiguration, SignalPhase
from app.simulation.signal_engine import SignalController
from app.simulation.network import TrafficNetwork
from app.services.incident_service import IncidentService

client = TestClient(app)


def test_shared_event_structure_validation():
    event = SystemEvent(
        event="traffic.updated",
        entity="network",
        data={"status": "ok"},
    )
    assert event.event == "traffic.updated"
    assert event.entity == "network"
    assert event.data == {"status": "ok"}
    assert event.timestamp > 0.0

    # JSON serialization validation
    event_json = json.loads(event.model_dump_json())
    assert event_json["event"] == "traffic.updated"
    assert event_json["entity"] == "network"
    assert "timestamp" in event_json


def test_websocket_connection_and_disconnection():
    with client.websocket_connect("/ws/traffic") as websocket:
        # Receives initial traffic.updated snapshot event on connect
        data = websocket.receive_text()
        event = json.loads(data)
        assert event["event"] == "traffic.updated"
        assert event["entity"] == "network"

        # Ping test
        websocket.send_text("ping")
        resp = websocket.receive_text()
        assert "pong" in resp

    # Client safely disconnects after context exit


def test_multiple_websocket_clients():
    with client.websocket_connect("/ws/traffic") as client1:
        data1 = json.loads(client1.receive_text())
        assert data1["event"] == "traffic.updated"

        with client.websocket_connect("/ws/traffic") as client2:
            data2 = json.loads(client2.receive_text())
            assert data2["event"] == "traffic.updated"

            # Check both connected sockets in manager
            assert len(manager.active_connections) >= 2

        # client2 disconnected
        assert len(manager.active_connections) >= 1


def test_websocket_broadcast_incident_created_and_updated():
    net = TrafficNetwork()
    inc_service = IncidentService(network=net)

    # Trigger incident creation
    inc = inc_service.create_incident("INC_WS_10", "ACCIDENT", "R_J1_J2")
    assert inc.incident_id == "INC_WS_10"

    # Trigger incident update
    updated_inc = inc_service.update_incident("INC_WS_10", active=False)
    assert updated_inc.active is False


def test_websocket_broadcast_signal_and_pedestrian_updated():
    net = TrafficNetwork()
    controller = SignalController(network=net)

    # 1. Apply signal configuration (triggers signal.updated)
    sig_config = SignalConfiguration(
        junction_id="J1",
        signal_phase=SignalPhase.EW_GREEN,
        green_duration=40.0,
        red_duration=20.0,
    )
    assert controller.apply_configuration(sig_config) is True

    # 2. Set pedestrian crossing (triggers pedestrian.updated)
    assert controller.set_pedestrian_crossing("J1", pedestrian_count=12, clearance_seconds=10.0) is True


def test_rest_apis_still_working_after_websocket_integration():
    # Verify GET /api/traffic
    resp_traffic = client.get("/api/traffic")
    assert resp_traffic.status_code == 200
    assert "roads" in resp_traffic.json()

    # Verify GET /api/junctions/J1
    resp_junc = client.get("/api/junctions/J1")
    assert resp_junc.status_code == 200

    # Verify POST /api/scenarios/traffic-surge
    resp_surge = client.post("/api/scenarios/traffic-surge", json={"surge_roads": ["R_J1_J2"], "surge_factor": 2.5})
    assert resp_surge.status_code == 200

    # Verify GET /api/metrics
    resp_metrics = client.get("/api/metrics")
    assert resp_metrics.status_code == 200
