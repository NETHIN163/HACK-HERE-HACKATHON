from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services import conflict_service as cf
from ..services import corridor_service as corridor
from ..services import emergency_service as ems
from ..services import rerouting_service as rr

router = APIRouter(prefix="/api", tags=["routes"])


class IncidentBody(BaseModel):
    u: str
    v: str


@router.post("/incidents")
def incident(b: IncidentBody):
    return {"rerouted": rr.handle_incident(b.u, b.v)}


@router.get("/emergencies/{eid}/corridor")
def get_corridor(eid: str):
    return corridor.current(eid)


@router.post("/conflicts/resolve")
def resolve(body: dict):
    try:
        return cf.resolve(body["junction"], body["ambulance_a"], body["ambulance_b"])
    except (KeyError, ValueError) as e:
        raise HTTPException(409, str(e))
