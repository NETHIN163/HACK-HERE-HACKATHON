import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_get_traffic_state():
    response = client.get("/api/traffic")
    assert response.status_code == 200
    data = response.json()
    assert "roads" in data
    assert "junctions" in data
    assert "timestamp" in data


def test_get_traffic_junctions():
    response = client.get("/api/traffic/junctions")
    assert response.status_code == 200
    junctions = response.json()
    assert isinstance(junctions, list)
    assert len(junctions) == 6


def test_get_traffic_roads():
    response = client.get("/api/traffic/roads")
    assert response.status_code == 200
    roads = response.json()
    assert isinstance(roads, list)
    assert len(roads) == 14


def test_get_junction_by_id_success():
    response = client.get("/api/junctions/J1")
    assert response.status_code == 200
    data = response.json()
    assert data["junction_id"] == "J1"


def test_get_junction_by_id_invalid_404():
    response = client.get("/api/junctions/J9999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_get_road_by_id_success():
    response = client.get("/api/roads/R_J1_J2")
    assert response.status_code == 200
    data = response.json()
    assert data["road_id"] == "R_J1_J2"


def test_get_road_by_id_invalid_404():
    response = client.get("/api/roads/R_INVALID_99")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_incidents_crud_flow():
    from app.services.traffic_service import traffic_service
    from app.models.road import RoadStatus
    traffic_service.incident_service.incidents.clear()
    traffic_service.network.update_road_status("R_J1_J2", RoadStatus.OPEN)

    # 1. GET incidents initially
    resp_get = client.get("/api/incidents")
    assert resp_get.status_code == 200

    # 2. POST create accident
    create_payload = {
        "incident_id": "INC_API_1",
        "type": "ACCIDENT",
        "road_id": "R_J1_J2",
        "severity": 1.5,
        "description": "Multi-car collision on J1-J2",
    }
    resp_post = client.post("/api/incidents", json=create_payload)
    assert resp_post.status_code == 201
    inc_data = resp_post.json()
    assert inc_data["incident_id"] == "INC_API_1"
    assert inc_data["type"] == "ACCIDENT"

    # Verify road state changed to BLOCKED
    resp_road = client.get("/api/roads/R_J1_J2")
    assert resp_road.json()["status"] == "BLOCKED"

    # 3. PATCH update incident (resolve)
    update_payload = {"active": False, "description": "Resolved"}
    resp_patch = client.patch("/api/incidents/INC_API_1", json=update_payload)
    assert resp_patch.status_code == 200
    assert resp_patch.json()["active"] is False

    # Verify road state restored to OPEN
    resp_road_after = client.get("/api/roads/R_J1_J2")
    assert resp_road_after.json()["status"] == "OPEN"


def test_post_incident_invalid_road_400():
    payload = {
        "type": "ACCIDENT",
        "road_id": "R_NON_EXISTENT",
    }
    response = client.post("/api/incidents", json=payload)
    assert response.status_code == 400
    assert "invalid road" in response.json()["detail"].lower()


def test_post_incident_invalid_type_422():
    # Invalid enum type caught by Pydantic validation
    payload = {
        "type": "METEOR_STRIKE",
        "road_id": "R_J1_J2",
    }
    response = client.post("/api/incidents", json=payload)
    # FastAPI returns 422 for unprocessable Pydantic body validation failure
    assert response.status_code in [400, 422]


def test_scenario_traffic_surge():
    payload = {
        "surge_roads": ["R_J1_J2", "R_J2_J3"],
        "surge_factor": 3.5,
    }
    response = client.post("/api/scenarios/traffic-surge", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "roads" in data
    assert data["roads"]["R_J1_J2"]["traffic_density"] >= 0.0


def test_scenario_traffic_surge_invalid_road_400():
    payload = {
        "surge_roads": ["R_BAD_ROAD_99"],
        "surge_factor": 2.0,
    }
    response = client.post("/api/scenarios/traffic-surge", json=payload)
    assert response.status_code == 400


def test_scenario_accident():
    payload = {
        "road_id": "R_J2_J3",
        "description": "Sudden oil spill",
    }
    response = client.post("/api/scenarios/accident", json=payload)
    assert response.status_code == 201
    assert response.json()["type"] == "ACCIDENT"

    resp_road = client.get("/api/roads/R_J2_J3")
    assert resp_road.json()["status"] == "BLOCKED"


def test_scenario_road_closure():
    payload = {
        "road_id": "R_J4_J5",
        "description": "Bridge repair",
    }
    response = client.post("/api/scenarios/road-closure", json=payload)
    assert response.status_code == 201
    assert response.json()["type"] == "ROAD_CLOSURE"

    resp_road = client.get("/api/roads/R_J4_J5")
    assert resp_road.json()["status"] == "CLOSED"


def test_get_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert "average_waiting_time" in metrics
    assert "average_queue_length" in metrics
    assert "maximum_queue_length" in metrics
    assert "traffic_throughput" in metrics
    assert "fuel_estimate" in metrics
    assert "co2_estimate" in metrics


def test_get_classical_optimization():
    response = client.get("/api/optimization/classical")
    assert response.status_code == 200
    configs = response.json()
    assert isinstance(configs, dict)
    assert "J1" in configs
    assert "signal_phase" in configs["J1"]
    assert "green_duration" in configs["J1"]
