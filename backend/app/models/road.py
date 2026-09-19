from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class RoadStatus(str, Enum):
    OPEN = "OPEN"
    CONGESTED = "CONGESTED"
    BLOCKED = "BLOCKED"
    CLOSED = "CLOSED"


class Road(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    road_id: str = Field(..., description="Unique identifier for the road segment")
    source: str = Field(..., description="Origin junction ID")
    destination: str = Field(..., description="Destination junction ID")
    distance: float = Field(..., description="Road length in meters", ge=0.0)
    capacity: float = Field(..., description="Maximum vehicle capacity per minute", ge=0.0)
    travel_time: float = Field(..., description="Current estimated travel time in seconds", ge=0.0)
    traffic_density: float = Field(0.0, description="Traffic density ratio (0.0 to 1.0)", ge=0.0)
    queue_length: int = Field(0, description="Number of queued vehicles on this road", ge=0)
    status: RoadStatus = Field(RoadStatus.OPEN, description="Current road operational status")

