import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.emergency import (
    EmergencyAssignment,
    EmergencyPriority,
    EmergencyRequest,
    EmergencyRoute,
    EmergencyVehicle,
)
from app.models.emergency_conflict import EmergencyConflictResult
from app.models.green_corridor import GreenCorridorPlan
from app.models.qubo import QAOAResult
from app.services.emergency_service import emergency_service

router = APIRouter(tags=["emergency"])


# Request Body Models
class CreateEmergencyRequestPayload(BaseModel):
    request_id: Optional[str] = Field(None, description="Optional request ID. Auto-generated if omitted.")
    origin: str = Field(..., description="Emergency scene junction ID")
    destination: str = Field(..., description="Hospital destination junction ID")
    priority: EmergencyPriority = Field(EmergencyPriority.HIGH, description="Urgency priority rating")


class RegisterAmbulancePayload(BaseModel):
    vehicle_id: str = Field(..., description="Unique vehicle/ambulance ID")
    current_location: str = Field(..., description="Current junction ID of ambulance")


class AssignAmbulancePayload(BaseModel):
    request_id: str = Field(..., description="Target emergency request ID")
    vehicle_id: Optional[str] = Field(None, description="Optional target vehicle ID")


class ReleaseAmbulancePayload(BaseModel):
    vehicle_id: str = Field(..., description="Ambulance vehicle ID to release")
    new_location: Optional[str] = Field(None, description="Updated junction location")


class CalculateRoutePayload(BaseModel):
    origin: str = Field(..., description="Origin junction ID")
    destination: str = Field(..., description="Destination junction ID")


class QAOARouteOptimizationPayload(BaseModel):
    origin: str = Field(..., description="Origin junction ID")
    destination: str = Field(..., description="Destination junction ID")


class PlanCorridorPayload(BaseModel):
    assignment_id: str = Field(..., description="Target assignment ID to plan Green Corridor for")


# 1. Emergency Requests
@router.post("/api/emergency/requests", response_model=EmergencyRequest, status_code=status.HTTP_201_CREATED)
def create_emergency_request(payload: CreateEmergencyRequestPayload):
    """Creates a new emergency dispatch request."""
    req_id = payload.request_id or f"REQ_{int(time.time() * 1000) % 100000}"
    try:
        return emergency_service.create_request(
            request_id=req_id,
            origin=payload.origin,
            destination=payload.destination,
            priority=payload.priority,
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("/api/emergency/requests", response_model=List[EmergencyRequest])
def list_emergency_requests():
    """Lists all emergency dispatch requests."""
    return emergency_service.get_all_requests()


@router.get("/api/emergency/requests/{request_id}", response_model=EmergencyRequest)
def get_emergency_request(request_id: str):
    """Retrieves single emergency request or returns 404 Not Found."""
    req = emergency_service.get_request(request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Emergency request '{request_id}' not found.")
    return req


# 2. Ambulances
@router.get("/api/emergency/ambulances", response_model=List[EmergencyVehicle])
def list_ambulances():
    """Lists all registered ambulances and their operational state."""
    return emergency_service.get_all_ambulances()


@router.post("/api/emergency/ambulances", response_model=EmergencyVehicle, status_code=status.HTTP_201_CREATED)
def register_ambulance(payload: RegisterAmbulancePayload):
    """Registers a new ambulance or updates location of existing vehicle."""
    try:
        return emergency_service.register_ambulance(
            vehicle_id=payload.vehicle_id,
            current_location=payload.current_location,
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("/api/emergency/ambulances/{vehicle_id}", response_model=EmergencyVehicle)
def get_ambulance(vehicle_id: str):
    """Retrieves single ambulance details or returns 404 Not Found."""
    veh = emergency_service.get_ambulance(vehicle_id)
    if not veh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ambulance '{vehicle_id}' not found.")
    return veh


# 3. Emergency Assignment
@router.post("/api/emergency/assignments", response_model=EmergencyAssignment, status_code=status.HTTP_201_CREATED)
def assign_ambulance(payload: AssignAmbulancePayload):
    """Assigns an available ambulance to an emergency request."""
    try:
        return emergency_service.assign_ambulance(
            request_id=payload.request_id,
            vehicle_id=payload.vehicle_id,
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("/api/emergency/assignments/{assignment_id}", response_model=EmergencyAssignment)
def get_assignment(assignment_id: str):
    """Retrieves single assignment details or returns 404 Not Found."""
    asg = emergency_service.get_assignment(assignment_id)
    if not asg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Assignment '{assignment_id}' not found.")
    return asg


@router.post("/api/emergency/assignments/{assignment_id}/release")
def release_assignment(assignment_id: str, payload: Optional[ReleaseAmbulancePayload] = None):
    """Releases assigned ambulance after emergency dispatch completion."""
    asg = emergency_service.get_assignment(assignment_id)
    if not asg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Assignment '{assignment_id}' not found.")

    v_id = payload.vehicle_id if payload else asg.vehicle_id
    new_loc = payload.new_location if payload else None
    success = emergency_service.release_ambulance(v_id, new_loc)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to release vehicle '{v_id}'.")
    return {"status": "released", "assignment_id": assignment_id, "vehicle_id": v_id}


# 4. Emergency Routing
@router.post("/api/emergency/routes", response_model=EmergencyRoute)
def calculate_emergency_route(payload: CalculateRoutePayload):
    """Calculates an optimal emergency route excluding BLOCKED/CLOSED roads."""
    try:
        return emergency_service.calculate_route(origin=payload.origin, destination=payload.destination)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


# 5. QUBO & QAOA Optimization
@router.post("/api/emergency/optimization/qaoa", response_model=QAOAResult)
def run_qaoa_route_optimization(payload: QAOARouteOptimizationPayload):
    """Formulates QUBO route selection and executes QAOA optimization solver."""
    try:
        return emergency_service.run_qaoa_route_optimization(origin=payload.origin, destination=payload.destination)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


# 6. Green Corridor
@router.post("/api/emergency/corridors/plan", response_model=GreenCorridorPlan, status_code=status.HTTP_201_CREATED)
def plan_green_corridor(payload: PlanCorridorPayload):
    """Plans a Green Corridor for an emergency assignment."""
    try:
        return emergency_service.plan_corridor(payload.assignment_id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/api/emergency/corridors/{request_id}/activate", response_model=GreenCorridorPlan)
def activate_green_corridor(request_id: str):
    """Activates Green Corridor signal priority for an emergency request."""
    try:
        return emergency_service.activate_corridor(request_id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/api/emergency/corridors/{request_id}/release", response_model=GreenCorridorPlan)
def release_green_corridor(request_id: str):
    """Releases Green Corridor signal priority and restores baseline timing."""
    try:
        return emergency_service.release_corridor(request_id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("/api/emergency/corridors", response_model=List[GreenCorridorPlan])
def list_active_corridors():
    """Lists all active Green Corridor plans."""
    return emergency_service.get_active_corridors()


# 7. Emergency Conflict Resolution
@router.post("/api/emergency/conflicts/resolve", response_model=EmergencyConflictResult)
def resolve_emergency_conflicts():
    """Detects and resolves overlapping emergency route conflicts across active requests."""
    try:
        return emergency_service.resolve_conflicts()
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
