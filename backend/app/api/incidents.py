import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.incident import Incident
from app.services.traffic_service import traffic_service

router = APIRouter(tags=["incidents"])


class CreateIncidentRequest(BaseModel):
    incident_id: Optional[str] = Field(None, description="Optional incident ID. Auto-generated if omitted.")
    type: str = Field(..., description="Incident type: ACCIDENT or ROAD_CLOSURE")
    road_id: str = Field(..., description="Target road ID affected by incident")
    severity: float = Field(1.0, description="Severity rating factor", ge=0.1)
    description: Optional[str] = Field(None, description="Detailed description")


class UpdateIncidentRequest(BaseModel):
    active: Optional[bool] = Field(None, description="Whether incident is active")
    severity: Optional[float] = Field(None, description="Updated severity rating", ge=0.1)
    description: Optional[str] = Field(None, description="Updated description")


@router.get("/api/incidents", response_model=List[Incident])
def get_incidents(active_only: bool = False):
    """Returns active or historical incidents."""
    return traffic_service.get_all_incidents(active_only=active_only)


@router.post("/api/incidents", response_model=Incident, status_code=status.HTTP_201_CREATED)
def create_incident(payload: CreateIncidentRequest):
    """Creates a new incident (ACCIDENT or ROAD_CLOSURE) and updates road network status."""
    inc_id = payload.incident_id or f"INC_{int(time.time() * 1000) % 100000}"
    try:
        return traffic_service.create_incident(
            incident_id=inc_id,
            type=payload.type,
            road_id=payload.road_id,
            severity=payload.severity,
            description=payload.description,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )


@router.patch("/api/incidents/{incident_id}", response_model=Incident)
def update_incident(incident_id: str, payload: UpdateIncidentRequest):
    """Updates an existing incident. Setting active=False resolves the incident and restores road status."""
    try:
        return traffic_service.update_incident(
            incident_id=incident_id,
            active=payload.active,
            severity=payload.severity,
            description=payload.description,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(err).lower() else status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )
