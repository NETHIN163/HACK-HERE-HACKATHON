from pydantic import BaseModel


class Hospital(BaseModel):
    hospital_id: str
    name: str
    latitude: float = 0.0
    longitude: float = 0.0
    emergency_capacity: int = 10
    status: str = "OPEN"
