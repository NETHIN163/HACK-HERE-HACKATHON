from pydantic import BaseModel


class CorridorReservation(BaseModel):
    junction: str
    state: str = "RESERVED"
    emergency_id: str
