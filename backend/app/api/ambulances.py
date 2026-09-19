from fastapi import APIRouter, HTTPException
from ..services import ambulance_service as amb
from ..services import emergency_service as ems
from ..models.ambulance import AmbulanceStatus

router = APIRouter(prefix="/api/ambulances", tags=["ambulances"])


@router.get("")
def list_all():
    return amb.list_all()


@router.get("/{aid}")
def get(aid: str):
    a = amb.get(aid)
    if not a:
        raise HTTPException(404, "Ambulance not found")
    return a


@router.post("/{aid}/assign")
def assign(aid: str, body: dict):
    eid = body.get("emergency_id")
    if not eid or not ems.get(eid):
        raise HTTPException(404, "Invalid emergency")
    a = amb.assign(aid, eid)
    if not a:
        raise HTTPException(404, "Ambulance not found")
    em = ems.get(eid)
    em.ambulance_id = aid
    return a
