from enum import Enum
from pydantic import BaseModel, Field


class AmbulanceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    EN_ROUTE = "EN_ROUTE"
    AT_PICKUP = "AT_PICKUP"
    TRANSPORTING = "TRANSPORTING"
    AT_HOSPITAL = "AT_HOSPITAL"
    REROUTING = "REROUTING"
    DELAYED = "DELAYED"


class Ambulance(BaseModel):
    ambulance_id: str
    vehicle_number: str
    status: AmbulanceStatus = AmbulanceStatus.AVAILABLE
    latitude: float = 0.0
    longitude: float = 0.0
    current_emergency_id: str | None = None
    current_hospital_id: str | None = None
    current_route_id: str | None = None
    eta_seconds: float = 0.0
    dispatch_seq: int = 0
