from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EmergencyPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    UNROUTABLE = "UNROUTABLE"


class AmbulanceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DISPATCHED = "DISPATCHED"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"


class RouteStatus(str, Enum):
    CALCULATED = "CALCULATED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    REROUTED = "REROUTED"


class EmergencyVehicle(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    vehicle_id: str = Field(..., description="Unique vehicle/ambulance identifier")
    current_location: str = Field(..., description="Current junction ID of the vehicle")
    status: AmbulanceStatus = Field(AmbulanceStatus.AVAILABLE, description="Operational status of vehicle")
    assigned_request_id: Optional[str] = Field(None, description="Assigned emergency request ID")


class EmergencyRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    request_id: str = Field(..., description="Unique emergency request identifier")
    origin: str = Field(..., description="Emergency scene junction ID")
    destination: str = Field(..., description="Destination hospital junction ID")
    priority: EmergencyPriority = Field(EmergencyPriority.HIGH, description="Urgency priority rating")
    vehicle_id: Optional[str] = Field(None, description="Assigned ambulance vehicle ID")
    status: RequestStatus = Field(RequestStatus.PENDING, description="Request lifecycle status")
    timestamp: float = Field(..., description="Unix creation timestamp")


class EmergencyRoute(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    route_id: str = Field(..., description="Unique emergency route identifier")
    origin: str = Field(..., description="Route origin junction ID")
    destination: str = Field(..., description="Route destination junction ID")
    path: List[str] = Field(..., description="Ordered list of junction IDs forming the route")
    road_ids: List[str] = Field(..., description="Ordered list of road IDs traversed")
    total_distance: float = Field(..., description="Total route distance in meters", ge=0.0)
    estimated_travel_time: float = Field(..., description="Estimated emergency travel time in seconds", ge=0.0)
    status: RouteStatus = Field(RouteStatus.CALCULATED, description="Operational status of route")


class EmergencyAssignment(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    assignment_id: str = Field(..., description="Unique assignment identifier")
    request_id: str = Field(..., description="Target emergency request ID")
    vehicle_id: str = Field(..., description="Dispatched ambulance vehicle ID")
    route: EmergencyRoute = Field(..., description="Assigned emergency route")
    timestamp: float = Field(..., description="Assignment creation timestamp")
