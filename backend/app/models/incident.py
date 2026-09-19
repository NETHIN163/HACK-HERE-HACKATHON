from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class IncidentType(str, Enum):
    ACCIDENT = "ACCIDENT"
    ROAD_CLOSURE = "ROAD_CLOSURE"


class Incident(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    incident_id: str = Field(..., description="Unique incident identifier")
    type: IncidentType = Field(..., description="Incident classification type")
    road_id: str = Field(..., description="Affected road ID")
    severity: float = Field(1.0, description="Severity factor (1.0 = standard, 2.0 = severe)", ge=0.1)
    description: Optional[str] = Field(None, description="Human readable description")
    timestamp: float = Field(..., description="Incident creation timestamp")
    active: bool = Field(True, description="Whether incident is currently active")

