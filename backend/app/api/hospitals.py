from fastapi import APIRouter, HTTPException
from ..services import hospital_service as hosp

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])


@router.get("")
def list_all():
    return hosp.list_all()


@router.get("/{hid}")
def get(hid: str):
    h = hosp.get(hid)
    if not h:
        raise HTTPException(404, "Hospital unavailable")
    return h
