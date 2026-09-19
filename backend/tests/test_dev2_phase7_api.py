import json
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_emergency_request_creation_and_retrieval():
    # 1. Create Emergency Request
    payload = {
        "request_id": "REQ_API_01",
        "origin": "J1",
        "destination": "J3",
        "priority": "CRITICAL",
    }
    resp_create = client.post("/api/emergency/requests", json=payload)
    assert resp_create.status_code == 201
    req_data = resp_create.json()
    assert req_data["request_id"] == "REQ_API_01"
    assert req_data["priority"] == "CRITICAL"

    # 2. Retrieve Request by ID
    resp_get = client.get("/api/emergency/requests/REQ_API_01")
    assert resp_get.status_code == 200
    assert resp_get.json()["request_id"] == "REQ_API_01"

    # 3. List All Requests
    resp_list = client.get("/api/emergency/requests")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 1


def test_ambulance_registration_and_listing():
    # Register Ambulance
    payload = {
        "vehicle_id": "AMB_API_01",
        "current_location": "J1",
    }
    resp_reg = client.post("/api/emergency/ambulances", json=payload)
    assert resp_reg.status_code == 201
    veh_data = resp_reg.json()
    assert veh_data["vehicle_id"] == "AMB_API_01"
    assert veh_data["current_location"] == "J1"

    # Retrieve Ambulance by ID
    resp_get = client.get("/api/emergency/ambulances/AMB_API_01")
    assert resp_get.status_code == 200
    assert resp_get.json()["status"] == "AVAILABLE"

    # List Ambulances
    resp_list = client.get("/api/emergency/ambulances")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 1


def test_ambulance_assignment_and_release_flow():
    # Create request and ambulance
    client.post("/api/emergency/ambulances", json={"vehicle_id": "AMB_API_02", "current_location": "J1"})
    client.post("/api/emergency/requests", json={"request_id": "REQ_API_02", "origin": "J1", "destination": "J3"})

    # Assign ambulance
    asg_payload = {"request_id": "REQ_API_02", "vehicle_id": "AMB_API_02"}
    resp_asg = client.post("/api/emergency/assignments", json=asg_payload)
    assert resp_asg.status_code == 201
    asg_data = resp_asg.json()
    assignment_id = asg_data["assignment_id"]
    assert asg_data["request_id"] == "REQ_API_02"
    assert asg_data["vehicle_id"] == "AMB_API_02"

    # Get assignment
    resp_get_asg = client.get(f"/api/emergency/assignments/{assignment_id}")
    assert resp_get_asg.status_code == 200

    # Release ambulance
    resp_rel = client.post(f"/api/emergency/assignments/{assignment_id}/release", json={"vehicle_id": "AMB_API_02", "new_location": "J3"})
    assert resp_rel.status_code == 200
    assert resp_rel.json()["status"] == "released"


def test_calculate_emergency_route_api():
    payload = {"origin": "J1", "destination": "J3"}
    response = client.post("/api/emergency/routes", json=payload)
    assert response.status_code == 200
    route = response.json()
    assert route["origin"] == "J1"
    assert route["destination"] == "J3"
    assert route["path"] == ["J1", "J2", "J3"]


def test_qaoa_route_optimization_api():
    payload = {"origin": "J1", "destination": "J3"}
    response = client.post("/api/emergency/optimization/qaoa", json=payload)
    assert response.status_code == 200
    qaoa_res = response.json()
    assert qaoa_res["is_valid"] is True
    assert qaoa_res["selected_route"]["path"] == ["J1", "J2", "J3"]
    assert qaoa_res["execution_method"] == "SIMULATED_QAOA"


def test_green_corridor_lifecycle_api():
    # Setup request, ambulance, assignment
    client.post("/api/emergency/ambulances", json={"vehicle_id": "AMB_API_03", "current_location": "J1"})
    client.post("/api/emergency/requests", json={"request_id": "REQ_API_03", "origin": "J1", "destination": "J3"})
    resp_asg = client.post("/api/emergency/assignments", json={"request_id": "REQ_API_03"})
    asg_id = resp_asg.json()["assignment_id"]

    # 1. PLAN Corridor
    resp_plan = client.post("/api/emergency/corridors/plan", json={"assignment_id": asg_id})
    assert resp_plan.status_code == 201
    plan = resp_plan.json()
    assert plan["status"] == "PLANNED"
    assert plan["ordered_junctions"] == ["J1", "J2", "J3"]

    # 2. ACTIVATE Corridor
    resp_act = client.post("/api/emergency/corridors/REQ_API_03/activate")
    assert resp_act.status_code == 200
    assert resp_act.json()["status"] == "ACTIVE"

    # 3. GET Active Corridors
    resp_list = client.get("/api/emergency/corridors")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 1

    # 4. RELEASE Corridor
    resp_rel = client.post("/api/emergency/corridors/REQ_API_03/release")
    assert resp_rel.status_code == 200
    assert resp_rel.json()["status"] == "RELEASED"


def test_emergency_conflict_resolution_api():
    response = client.post("/api/emergency/conflicts/resolve")
    assert response.status_code == 200
    res = response.json()
    assert "status" in res


def test_unknown_resource_handling_404():
    assert client.get("/api/emergency/requests/REQ_NON_EXISTENT").status_code == 404
    assert client.get("/api/emergency/ambulances/AMB_NON_EXISTENT").status_code == 404
    assert client.get("/api/emergency/assignments/ASG_NON_EXISTENT").status_code == 404


def test_full_emergency_workflow_integration_api():
    # 1. Create request
    r_resp = client.post("/api/emergency/requests", json={"request_id": "REQ_FULL", "origin": "J1", "destination": "J3", "priority": "CRITICAL"})
    assert r_resp.status_code == 201

    # 2. Register ambulance
    a_resp = client.post("/api/emergency/ambulances", json={"vehicle_id": "AMB_FULL", "current_location": "J1"})
    assert a_resp.status_code == 201

    # 3. Assign
    asg_resp = client.post("/api/emergency/assignments", json={"request_id": "REQ_FULL"})
    assert asg_resp.status_code == 201
    asg_id = asg_resp.json()["assignment_id"]

    # 4. Run QAOA Route Optimization
    qaoa_resp = client.post("/api/emergency/optimization/qaoa", json={"origin": "J1", "destination": "J3"})
    assert qaoa_resp.status_code == 200

    # 5. Plan & Activate Green Corridor
    client.post("/api/emergency/corridors/plan", json={"assignment_id": asg_id})
    act_resp = client.post("/api/emergency/corridors/REQ_FULL/activate")
    assert act_resp.status_code == 200

    # 6. Resolve conflicts
    conf_resp = client.post("/api/emergency/conflicts/resolve")
    assert conf_resp.status_code == 200

    # 7. Release Corridor & Assignment
    client.post("/api/emergency/corridors/REQ_FULL/release")
    rel_resp = client.post(f"/api/emergency/assignments/{asg_id}/release", json={"vehicle_id": "AMB_FULL", "new_location": "J3"})
    assert rel_resp.status_code == 200
