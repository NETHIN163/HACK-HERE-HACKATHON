from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .route import RouteStatus


class EmergencyPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EmergencyStatus(str, Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    REROUTING = "REROUTING"
    AT_HOSPITAL = "AT_HOSPITAL"
    CLOSED = "CLOSED"


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    ROUTED = "ROUTED"
    EN_ROUTE = "EN_ROUTE"
    AT_HOSPITAL = "AT_HOSPITAL"
    CLOSED = "CLOSED"
    UNROUTABLE = "UNROUTABLE"
    COMPLETED = "COMPLETED"


class AmbulanceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    EN_ROUTE = "EN_ROUTE"
    AT_PICKUP = "AT_PICKUP"
    TRANSPORTING = "TRANSPORTING"
    AT_HOSPITAL = "AT_HOSPITAL"
    REROUTING = "REROUTING"
    DELAYED = "DELAYED"
    DISPATCHED = "DISPATCHED"


class EmergencyRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    request_id: str
    origin: str
    destination: str
    priority: EmergencyPriority = EmergencyPriority.HIGH
    status: RequestStatus = RequestStatus.PENDING
    created_at: float
    timestamp: Optional[float] = None
    assigned_vehicle_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    assigned_route_id: Optional[str] = None
    corridor_id: Optional[str] = None


class EmergencyVehicle(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    vehicle_id: str
    current_location: str
    status: AmbulanceStatus = AmbulanceStatus.AVAILABLE
    assigned_request_id: Optional[str] = None


class EmergencyAssignment(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    assignment_id: str
    request_id: str
    vehicle_id: str
    route_id: Optional[str] = None
    route: Optional["EmergencyRoute"] = None
    assigned_at: float = 0.0
    timestamp: Optional[float] = None


class EmergencyRoute(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    route_id: str
    origin: str
    destination: str
    path: List[str] = Field(default_factory=list)
    road_ids: List[str] = Field(default_factory=list)
    total_distance: float = 0.0
    estimated_travel_time: float = 0.0
    status: str = "CALCULATED"
    is_eligible: bool = True


# Legacy Emergency model for backward compatibility
class Emergency(BaseModel):
    emergency_id: str
    type: str = "TRAUMA"
    priority: int = Field(default=1, ge=1, le=5)
    pickup: str = "J1"
    destination: str = "H1"
    ambulance_id: str | None = None
    hospital_id: str | None = None
    status: EmergencyStatus = EmergencyStatus.CREATED
    route_id: str | None = None
    eta_seconds: float = 0.0
