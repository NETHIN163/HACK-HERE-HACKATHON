from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ConflictStatus(str, Enum):
    NO_CONFLICT = "NO_CONFLICT"
    RESOLVED = "RESOLVED"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"


class JunctionConflict(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    junction_id: str = Field(..., description="Junction where emergency priority overlap occurs")
    competing_request_ids: List[str] = Field(..., description="List of emergency request IDs competing for junction")
    winner_request_id: Optional[str] = Field(None, description="Request ID granted priority at this junction")
    deferred_request_ids: List[str] = Field(default_factory=list, description="Request IDs deferred at this junction")
    resolution_reason: str = Field(..., description="Explanation of resolution policy outcome or safety lock")


class EmergencyConflictResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    conflict_id: str = Field(..., description="Unique conflict resolution event identifier")
    status: ConflictStatus = Field(..., description="Overall status of conflict resolution")
    conflicting_request_ids: List[str] = Field(default_factory=list, description="All request IDs involved in conflict")
    overlapping_junctions: List[str] = Field(default_factory=list, description="List of junctions shared across routes")
    overlapping_roads: List[str] = Field(default_factory=list, description="List of roads shared across routes")
    junction_resolutions: List[JunctionConflict] = Field(default_factory=list, description="Per-junction resolution details")
    granted_requests: List[str] = Field(default_factory=list, description="Requests granted corridor priority")
    deferred_requests: List[str] = Field(default_factory=list, description="Requests deferred or partially granted")
    timestamp: float = Field(..., description="Unix timestamp of resolution execution")
