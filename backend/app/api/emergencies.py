from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services import emergency_service as ems
from ..services import rerouting_service as rr

router = APIRouter(prefix="/api/emergencies", tags=["emergencies"])


class CreateBody(BaseModel):
    type: str = "TRAUMA"
    priority: int = 1
    pickup: str = "J1"
    destination: str | None = None


@router.post("")
def create(b: CreateBody):
    try:
        return ems.create(b.type, b.priority, b.pickup, b.destination)
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.get("")
def list_all():
    return ems.list_all()


@router.get("/{eid}")
def get(eid: str):
    em = ems.get(eid)
    if not em:
        raise HTTPException(404, "Emergency not found")
    return em


@router.patch("/{eid}")
def patch(eid: str, fields: dict):
    em = ems.patch(eid, fields)
    if not em:
        raise HTTPException(404, "Emergency not found")
    return em


@router.post("/{eid}/optimize-route")
def optimize(eid: str):
    try:
        r = ems.optimize_route(eid)
    except ValueError as e:
        raise HTTPException(409, str(e))
    if not r:
        raise HTTPException(404, "Invalid emergency")
    return r


@router.post("/{eid}/reroute")
def reroute(eid: str):
    try:
        return rr.reroute_emergency(eid)
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.get("/{eid}/route")
def route(eid: str):
    r = ems.active_route(eid)
    if not r:
        raise HTTPException(404, "No route available")
    return r


@router.post("/{eid}/assign")
def assign(eid: str):
    try:
        em = ems.assign(eid)
    except ValueError as e:
        raise HTTPException(409, str(e))
    if not em:
        raise HTTPException(404, "Emergency not found")
    return em
