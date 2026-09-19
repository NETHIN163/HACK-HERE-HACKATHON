from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.signal import SignalPhase


class CorridorStatus(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    REROUTED = "REROUTED"
    FAILED = "FAILED"


class JunctionPriorityPlan(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    junction_id: str = Field(..., description="Target junction ID in emergency corridor")
    sequence_order: int = Field(..., description="1-indexed sequence order along emergency route", ge=1)
    requires_priority: bool = Field(True, description="Whether emergency signal priority is requested")
    requested_phase: SignalPhase = Field(SignalPhase.EMERGENCY_PRIORITY, description="Target emergency signal phase")
    green_duration: float = Field(60.0, description="Target green priority duration in seconds", ge=5.0)
    is_safe: bool = Field(True, description="Whether priority activation passes safety conflict & pedestrian checks")
    safety_reason: Optional[str] = Field(None, description="Detailed explanation if priority is rejected/unsafe")
    activated: bool = Field(False, description="Whether priority has been activated at this junction")


class GreenCorridorPlan(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    corridor_id: str = Field(..., description="Unique Green Corridor plan identifier")
    request_id: str = Field(..., description="Associated emergency request ID")
    vehicle_id: str = Field(..., description="Dispatched ambulance vehicle ID")
    route_id: str = Field(..., description="Assigned emergency route ID")
    ordered_junctions: List[str] = Field(..., description="Ordered list of junction IDs forming corridor")
    junction_plans: List[JunctionPriorityPlan] = Field(..., description="Per-junction signal priority plans")
    status: CorridorStatus = Field(CorridorStatus.PLANNED, description="Lifecycle status of Green Corridor plan")
    created_at: float = Field(..., description="Plan creation timestamp")
