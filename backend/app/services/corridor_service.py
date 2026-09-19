"""Green Corridor: converts a route node list into per-junction signal reservations.

Phase logic:
  index 0  -> GREEN          (ambulance is here now)
  index 1  -> PREPARING      (next junction, pre-warming signal)
  index 2+ -> RESERVED       (upcoming junctions)

If a junction has an active pedestrian crossing it gets
PENDING_PEDESTRIAN_CLEARANCE instead and must be explicitly cleared.

Multi-emergency support: reservations are keyed by (junction, emergency_id)
so two emergencies sharing a junction do not overwrite each other.
"""
import time
from . import events
from . import network_store as net
from app.models.green_corridor import GreenCorridorPlan, JunctionPriorityPlan, CorridorStatus, SignalPhase

# Key: (junction, emergency_id) -> reservation dict
_reservations: dict[tuple, dict] = {}
# Compatibility registry used by the class-based emergency workflow.
active_plans: dict[str, list[dict]] = {}


def plan_corridor(assignment) -> GreenCorridorPlan:
    """Compatibility adapter for the class-based corridor workflow."""
    route = assignment.route
    if route is None:
        raise ValueError(f"Assignment '{assignment.assignment_id}' has no route")
    generate(assignment.request_id, route.path)
    plan = GreenCorridorPlan(
        corridor_id=f"CORRIDOR_{assignment.vehicle_id}_{assignment.request_id}",
        request_id=assignment.request_id,
        vehicle_id=assignment.vehicle_id,
        route_id=route.route_id,
        ordered_junctions=route.path,
        junction_plans=[
            JunctionPriorityPlan(
                junction_id=junction,
                sequence_order=index,
                requires_priority=True,
                requested_phase=SignalPhase.EMERGENCY_PRIORITY,
                green_duration=60.0,
                is_safe=True,
                activated=False,
            )
            for index, junction in enumerate(route.path, start=1)
        ],
        status=CorridorStatus.PLANNED,
        created_at=time.time(),
    )
    active_plans[assignment.request_id] = plan
    return plan


def activate_corridor(request_id: str) -> GreenCorridorPlan:
    plan = active_plans[request_id]
    plan.status = CorridorStatus.ACTIVE
    return plan


def release_corridor(request_id: str) -> GreenCorridorPlan:
    plan = active_plans[request_id]
    plan.status = CorridorStatus.RELEASED
    active_plans.pop(request_id, None)
    release(request_id)
    return plan


def generate(emergency_id: str, nodes: list[str]) -> list[dict]:
    """Create/replace all corridor reservations for an emergency."""
    _clear_emergency(emergency_id)
    out = []
    for i, j in enumerate(nodes):
        if i == 0:
            state = "GREEN"
        elif i == 1:
            state = "PREPARING"
        else:
            state = "RESERVED"
        # Pedestrian override: ambulance must wait for safe clearance
        if net.pedestrian_active(j) and state in ("GREEN", "PREPARING"):
            state = "PENDING_PEDESTRIAN_CLEARANCE"
        reservation = {"junction": j, "state": state, "emergency_id": emergency_id, "created_at": time.time()}
        _reservations[(j, emergency_id)] = reservation
        out.append(reservation)
    events.emit("green_corridor.updated", {"emergency_id": emergency_id, "reservations": out})
    active_plans[emergency_id] = out
    return out


def release(emergency_id: str) -> None:
    """Release all corridor reservations for an emergency."""
    _clear_emergency(emergency_id)
    events.emit("green_corridor.updated", {"emergency_id": emergency_id, "reservations": []})
    active_plans.pop(emergency_id, None)


def current(emergency_id: str) -> list[dict]:
    """Return active reservations for one emergency, ordered by creation time."""
    return sorted(
        [v for k, v in _reservations.items() if k[1] == emergency_id],
        key=lambda r: r["created_at"],
    )


def advance(emergency_id: str) -> list[dict]:
    """Shift corridor forward by one junction (ambulance passed the GREEN head)."""
    reservations = current(emergency_id)
    if not reservations:
        return []
    head = reservations[0]
    _reservations.pop((head["junction"], emergency_id), None)
    remaining = current(emergency_id)
    if remaining:
        remaining[0]["state"] = "GREEN"
        if len(remaining) > 1 and remaining[1]["state"] == "RESERVED":
            remaining[1]["state"] = "PREPARING"
    events.emit("green_corridor.updated", {"emergency_id": emergency_id, "reservations": remaining})
    return remaining


def clear_pedestrian(junction: str, emergency_id: str) -> dict | None:
    """Called when pedestrian crossing clears; promote junction to its proper phase."""
    key = (junction, emergency_id)
    if key not in _reservations:
        return None
    res = current(emergency_id)
    idx = next((i for i, r in enumerate(res) if r["junction"] == junction), None)
    if idx is None:
        return None
    new_state = "GREEN" if idx == 0 else ("PREPARING" if idx == 1 else "RESERVED")
    _reservations[key]["state"] = new_state
    events.emit("green_corridor.updated", {"emergency_id": emergency_id, "reservations": current(emergency_id)})
    return _reservations[key]


def all_reservations() -> list[dict]:
    """Return every active reservation across all emergencies (admin/debug)."""
    return list(_reservations.values())


def _clear_emergency(emergency_id: str) -> None:
    for key in [k for k in list(_reservations.keys()) if k[1] == emergency_id]:
        del _reservations[key]
