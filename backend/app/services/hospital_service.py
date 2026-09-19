"""Demo hospitals + nearest-by-graph assignment."""
import networkx as nx
from . import network_store as net
from ..models.hospital import Hospital

_hospitals: dict[str, Hospital] = {
    "H1": Hospital(hospital_id="H1", name="City General", emergency_capacity=8),
    "H2": Hospital(hospital_id="H2", name="North Care", emergency_capacity=4),
}
_hospital_node = {"H1": "J5", "H2": "J4"}


def list_all() -> list[Hospital]:
    return list(_hospitals.values())


def get(hospital_id: str) -> Hospital | None:
    return _hospitals.get(hospital_id)


def nearest_open(pickup: str) -> Hospital | None:
    g = net.get_graph()
    open_h = [h for h in _hospitals.values() if h.status == "OPEN" and h.emergency_capacity > 0]
    if not open_h:
        return None
    best, best_d = None, float("inf")
    for h in open_h:
        try:
            d = nx.shortest_path_length(g, pickup, _hospital_node[h.hospital_id], weight="travel_time")
        except Exception:
            d = 1e9
        if d < best_d:
            best, best_d = h, d
    return best


def hospital_node(hospital_id: str) -> str:
    if hospital_id in _hospital_node:
        return _hospital_node[hospital_id]
    if hospital_id.startswith("J"):
        return hospital_id
    return _hospital_node.get(hospital_id, "J5")
