from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.traffic import TrafficState
from app.models.incident import Incident
from app.services.traffic_service import traffic_service

router = APIRouter(tags=["scenarios"])


class TrafficSurgeRequest(BaseModel):
    surge_roads: List[str] = Field(..., description="List of road IDs to experience traffic surge")
    surge_factor: float = Field(3.0, description="Multiplier for demand increase", ge=1.0)


class ScenarioAccidentRequest(BaseModel):
    road_id: str = Field(..., description="Road ID where accident occurs")
    description: Optional[str] = Field(None, description="Accident description")


class ScenarioRoadClosureRequest(BaseModel):
    road_id: str = Field(..., description="Road ID to be closed")
    description: Optional[str] = Field(None, description="Road closure description")


@router.post("/api/scenarios/traffic-surge", response_model=TrafficState)
def trigger_traffic_surge(payload: TrafficSurgeRequest):
    """Triggers a traffic surge scenario on selected roads and returns updated TrafficState."""
    try:
        return traffic_service.trigger_traffic_surge(
            surge_roads=payload.surge_roads,
            surge_factor=payload.surge_factor,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )


@router.post("/api/scenarios/accident", response_model=Incident, status_code=status.HTTP_201_CREATED)
def trigger_accident_scenario(payload: ScenarioAccidentRequest):
    """Triggers an accident scenario, marking affected road BLOCKED."""
    try:
        return traffic_service.trigger_accident_scenario(
            road_id=payload.road_id,
            description=payload.description,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )


@router.post("/api/scenarios/road-closure", response_model=Incident, status_code=status.HTTP_201_CREATED)
def trigger_road_closure_scenario(payload: ScenarioRoadClosureRequest):
    """Triggers a road closure scenario, marking affected road CLOSED."""
    try:
        return traffic_service.trigger_road_closure_scenario(
            road_id=payload.road_id,
            description=payload.description,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        )
