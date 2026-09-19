"""Green Corridor: route nodes -> per-junction signal reservations."""
from . import events
from . import network_store as net

_reservations: dict[str, dict] = {}


def generate(emergency_id: str, nodes: list[str]) -> list[dict]:
    out = []
    for i, j in enumerate(nodes):
        state = "GREEN" if i == 0 else ("PREPARING" if i == 2 else "RESERVED")
        if net.pedestrian_active(j):
            state = "PENDING_PEDESTRIAN_CLEARANCE"
        _reservations[j] = {"junction": j, "state": state, "emergency_id": emergency_id}
        out.append(_reservations[j])
    events.emit("green_corridor.updated", {"emergency_id": emergency_id, "reservations": out})
    return out


def release(emergency_id: str) -> None:
    for j in [k for k, v in _reservations.items() if v["emergency_id"] == emergency_id]:
        del _reservations[j]
    events.emit("green_corridor.updated", {"emergency_id": emergency_id, "reservations": []})


def current(emergency_id: str) -> list[dict]:
    return [v for v in _reservations.values() if v["emergency_id"] == emergency_id]
