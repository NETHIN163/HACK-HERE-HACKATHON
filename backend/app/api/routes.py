import uuid
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel
from ..services import conflict_service as cf
from ..services import corridor_service as corridor
from ..services import emergency_service as ems
from ..services import rerouting_service as rr
from ..services.traffic_service import traffic_service

router = APIRouter(prefix="/api", tags=["routes"])


class IncidentBody(BaseModel):
    u: str | None = None
    v: str | None = None
    incident_id: str | None = None
    type: str | None = None
    road_id: str | None = None
    severity: float = 1.0
    description: str | None = None


@router.post("/incidents")
def incident(b: IncidentBody, response: Response):
    if b.u and b.v:
        return {"rerouted": rr.handle_incident(b.u, b.v)}
    if not b.type or not b.road_id:
        raise HTTPException(status_code=400, detail="type and road_id are required")
    try:
        incident_id = b.incident_id or f"INC_{uuid.uuid4().hex[:8].upper()}"
        created = traffic_service.create_incident(
            incident_id=incident_id,
            type=b.type,
            road_id=b.road_id,
            severity=b.severity,
            description=b.description,
        )
        response.status_code = status.HTTP_201_CREATED
        return created
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/emergencies/{eid}/corridor")
def get_corridor(eid: str):
    return corridor.current(eid)


@router.post("/conflicts/resolve")
def resolve(body: dict):
    try:
        return cf.resolve(body["junction"], body["ambulance_a"], body["ambulance_b"])
    except (KeyError, ValueError) as e:
        raise HTTPException(409, str(e))
