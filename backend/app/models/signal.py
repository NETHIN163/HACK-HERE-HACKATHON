from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SignalPhase(str, Enum):
    NS_GREEN = "NS_GREEN"
    EW_GREEN = "EW_GREEN"
    ALL_RED = "ALL_RED"
    EMERGENCY_PRIORITY = "EMERGENCY_PRIORITY"
    PEDESTRIAN_CLEARANCE = "PEDESTRIAN_CLEARANCE"


class SignalConfiguration(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    junction_id: str = Field(..., description="Target junction ID")
    signal_phase: SignalPhase = Field(..., description="Selected signal phase")
    green_duration: float = Field(..., description="Target green phase duration in seconds", ge=5.0)
    red_duration: float = Field(..., description="Target red phase duration in seconds", ge=5.0)
    priority_override: bool = Field(False, description="Emergency priority override flag")
    reservation_id: Optional[str] = Field(None, description="Optional emergency corridor reservation ID")
