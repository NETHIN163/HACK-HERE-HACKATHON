from enum import Enum
from pydantic import BaseModel


class RouteStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INVALIDATED = "INVALIDATED"
    COMPLETED = "COMPLETED"


class Route(BaseModel):
    route_id: str
    emergency_id: str
    roads: list[str] = []
    nodes: list[str] = []
    distance: float = 0.0
    estimated_time: float = 0.0
    score: float = 0.0
    status: RouteStatus = RouteStatus.ACTIVE
