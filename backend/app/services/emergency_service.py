"""Emergency CRUD + assignment orchestration."""
import uuid
from ..models.emergency import Emergency, EmergencyStatus
from ..models.route import Route, RouteStatus
from . import ambulance_service as amb, events
from . import hospital_service as hosp
from . import routing_service as routing
from . import corridor_service as corridor

_emergencies: dict[str, Emergency] = {}
_routes: dict[str, Route] = {}


def create(type: str, priority: int, pickup: str, destination: str | None = None) -> Emergency:
    eid = f"E-{uuid.uuid4().hex[:6].upper()}"
    em = Emergency(emergency_id=eid, type=type, priority=priority, pickup=pickup, destination=destination or "H1")
    _emergencies[eid] = em
    events.emit("emergency.created", em.model_dump())
    # auto-assign ambulance + hospital + initial route
    assign(eid)
    return em


def get(emergency_id: str) -> Emergency | None:
    return _emergencies.get(emergency_id)


def list_all() -> list[Emergency]:
    return list(_emergencies.values())


def patch(emergency_id: str, fields: dict) -> Emergency | None:
    em = get(emergency_id)
    if not em:
        return None
    for k, v in fields.items():
        if hasattr(em, k):
            setattr(em, k, v)
    events.emit("emergency.updated", em.model_dump())
    return em


def assign(emergency_id: str) -> Emergency | None:
    em = get(emergency_id)
    if not em:
        return None
    a = amb.nearest_available(em.pickup)
    if not a:
        raise ValueError("No ambulance available")
    h = hosp.nearest_open(em.pickup)
    if not h:
        raise ValueError("Hospital unavailable")
    em.hospital_id = h.hospital_id
    em.destination = h.hospital_id
    amb.assign(a.ambulance_id, emergency_id)
    em.ambulance_id = a.ambulance_id
    em.status = EmergencyStatus.ASSIGNED
    optimize_route(emergency_id)
    events.emit("emergency.updated", em.model_dump())
    return em


def optimize_route(emergency_id: str) -> Route | None:
    from . import hospital_service as hs
    em = get(emergency_id)
    if not em or not em.ambulance_id:
        return None
    dest_node = hs.hospital_node(em.destination)
    cands = routing.candidate_routes(em.pickup, [dest_node], k=2)
    if not cands:
        raise ValueError("No route available")
    best = cands[0]
    rid = f"R-{uuid.uuid4().hex[:6].upper()}"
    route = Route(route_id=rid, emergency_id=emergency_id, roads=best["roads"], nodes=best["nodes"],
                  distance=best["distance"], estimated_time=best["estimated_time"], score=best["score"])
    _routes[rid] = route
    em.route_id = rid
    em.eta_seconds = best["estimated_time"]
    em.status = EmergencyStatus.EN_ROUTE
    corridor.generate(emergency_id, best["nodes"])
    events.emit("route.updated", route.model_dump())
    return route


def active_route(emergency_id: str) -> Route | None:
    em = get(emergency_id)
    if not em or not em.route_id:
        return None
    return _routes.get(em.route_id)


def invalidate_route(route_id: str) -> None:
    r = _routes.get(route_id)
    if r:
        r.status = RouteStatus.INVALIDATED
        events.emit("route.blocked", r.model_dump())
