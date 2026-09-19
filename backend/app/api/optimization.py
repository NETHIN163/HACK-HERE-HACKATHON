import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..optimization import qubo as Q, evaluator as ev
from ..services import events

router = APIRouter(prefix="/api/optimization", tags=["optimization"])
_runs: dict[str, dict] = {}


class RunBody(BaseModel):
    junctions: list[str] = ["J1", "J2", "J3"]
    mode: str = "HYBRID"


@router.post("/run")
def run(b: RunBody):
    q = Q.build(b.junctions)
    rid = f"O-{uuid.uuid4().hex[:6].upper()}"
    if b.mode.upper() == "CLASSICAL":
        res = ev.classical(q)
    else:
        res = ev.hybrid(q)
    res.update({"status": "COMPLETED", "variables": q["variables"], "candidates": res.get("candidates", 1)})
    res["metrics"] = ev.metrics_for(res["configuration"])
    _runs[rid] = {"id": rid, "qubo": {"variables": q["variables"]}, **res}
    events.emit("optimization.completed", {"id": rid, **res})
    return {"id": rid, **res}


@router.post("/classical")
def classical(b: RunBody):
    b.mode = "CLASSICAL"
    return run(b)


@router.post("/hybrid")
def hybrid(b: RunBody):
    b.mode = "HYBRID"
    return run(b)


@router.get("/{rid}")
def get(rid: str):
    if rid not in _runs:
        raise HTTPException(404, "Optimization failure: unknown id")
    return _runs[rid]


@router.get("/{rid}/candidates")
def candidates(rid: str):
    if rid not in _runs:
        raise HTTPException(404, "Optimization failure: unknown id")
    return _runs[rid]
