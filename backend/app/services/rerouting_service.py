"""Mandatory accident-on-route flow + dynamic rerouting."""
from ..models.emergency import EmergencyStatus
from . import emergency_service as ems
from . import corridor_service as corridor
from . import events
from . import network_store as net
from . import routing_service as routing
from . import hospital_service as hs


def handle_incident(u: str, v: str) -> list[dict]:
    """Block road u-v, then reroute every active emergency whose route uses it."""
    net.set_blocked(u, v, True)
    affected = []
    for em in ems.list_all():
        r = ems.active_route(em.emergency_id)
        if r and f"{u}-{v}" in r.roads and r.status.value == "ACTIVE":
            affected.append(reroute_emergency(em.emergency_id))
    return affected


def reroute_emergency(emergency_id: str) -> dict:
    em = ems.get(emergency_id)
    if not em:
        raise ValueError("Emergency not found")

    events.emit("reroute.started", {"emergency_id": emergency_id})

    # Step 1: Invalidate old route + release corridor reservations
    old = ems.active_route(emergency_id)
    if old:
        ems.invalidate_route(old.route_id)
    corridor.release(emergency_id)

    # Step 2: Probe for alternatives BEFORE committing (avoids silent failure)
    dest_node = hs.hospital_node(em.destination)
    probe = routing.candidate_routes(em.pickup, [dest_node], k=2)
    if not probe:
        em.status = EmergencyStatus.REROUTING
        events.emit("route.blocked", {"emergency_id": emergency_id, "reason": "All routes blocked after incident"})
        raise ValueError("All routes blocked")

    # Step 3: Full optimize (builds route object + generates green corridor)
    route = ems.optimize_route(emergency_id)
    assert route is not None, "optimize_route returned None despite probe confirming a valid path"

    events.emit("reroute.completed", {
        "emergency_id": emergency_id,
        "route_id": route.route_id,
        "eta_seconds": route.estimated_time,
        "alternatives_found": len(probe),
    })
    return {
        "emergency_id": emergency_id,
        "route": route.model_dump(),
        "alternatives_found": len(probe),
    }
