from enum import Enum
from pydantic import BaseModel, Field


class EmergencyStatus(str, Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    REROUTING = "REROUTING"
    AT_HOSPITAL = "AT_HOSPITAL"
    CLOSED = "CLOSED"


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
