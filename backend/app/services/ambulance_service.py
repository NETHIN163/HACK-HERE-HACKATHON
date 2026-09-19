"""Ambulance registry + deterministic assignment (nearest AVAILABLE)."""
from . import network_store as net
from ..models.ambulance import Ambulance, AmbulanceStatus

_ambulances: dict[str, Ambulance] = {}
_seq = 0


def seed_demo() -> None:
    if _ambulances:
        return
    for i, (amb_id, node) in enumerate([("A1", "J1"), ("A2", "J4"), ("A3", "J2")], start=1):
        _ambulances[amb_id] = Ambulance(ambulance_id=amb_id, vehicle_number=f"AMB-00{i}", latitude=float(i), longitude=float(i))


def list_all() -> list[Ambulance]:
    seed_demo()
    return list(_ambulances.values())


def get(ambulance_id: str) -> Ambulance | None:
    seed_demo()
    return _ambulances.get(ambulance_id)


def register(ambulance_id: str, current_location: str = "J1") -> Ambulance:
    """Register a demo ambulance while retaining its current junction metadata."""
    existing = get(ambulance_id)
    if existing:
        existing.status = AmbulanceStatus.AVAILABLE
        return existing
    vehicle = Ambulance(ambulance_id=ambulance_id, vehicle_number=ambulance_id)
    _ambulances[ambulance_id] = vehicle
    return vehicle


def nearest_available(pickup: str) -> Ambulance | None:
    seed_demo()
    avail = [a for a in _ambulances.values() if a.status == AmbulanceStatus.AVAILABLE]
    if not avail:
        return None
    g = net.get_graph()
    import networkx as nx
    best, best_d = None, float("inf")
    for a in avail:
        # demo: map ambulance to a home junction by index
        home = {"A1": "J1", "A2": "J4", "A3": "J2"}.get(a.ambulance_id, "J1")
        try:
            d = nx.shortest_path_length(g, home, pickup, weight="travel_time")
        except Exception:
            d = 1e9
        if d < best_d:
            best, best_d = a, d
    return best


def assign(ambulance_id: str, emergency_id: str) -> Ambulance | None:
    global _seq
    a = get(ambulance_id)
    if not a:
        return None
    _seq += 1
    a.status = AmbulanceStatus.EN_ROUTE
    a.current_emergency_id = emergency_id
    a.dispatch_seq = _seq
    return a


def update_status(ambulance_id: str, status: AmbulanceStatus, **kw) -> Ambulance | None:
    a = get(ambulance_id)
    if not a:
        return None
    a.status = status
    for k, v in kw.items():
        setattr(a, k, v)
    return a
