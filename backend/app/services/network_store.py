"""Demo road network stub. Backend Dev 1 owns the real traffic/network services;
this module provides a compatible in-memory graph so Dev 2 can build standalone."""
import networkx as nx

_graph: nx.DiGraph | None = None
_pedestrian: dict[str, bool] = {}
_weights: dict[str, float] = {
    "travel_time": 1.0,
    "congestion": 2.0,
    "queue": 1.5,
    "signal_delay": 1.0,
    "diversion": 1.0,
    "safety": 3.0,
}


def get_weights() -> dict[str, float]:
    return dict(_weights)


def set_weights(w: dict[str, float]) -> dict[str, float]:
    _weights.update(w)
    return get_weights()


def _build_demo() -> nx.DiGraph:
    g = nx.DiGraph()
    for j in ["J1", "J2", "J3", "J4", "J5"]:
        g.add_node(j)
    edges = [
        ("J1", "J2", {"distance": 4.0, "travel_time": 240.0, "congestion": 0.3, "queue": 2.0, "signal_delay": 20.0, "diversion": 0.1, "safety": 0.0, "blocked": False}),
        ("J2", "J3", {"distance": 3.0, "travel_time": 200.0, "congestion": 0.5, "queue": 4.0, "signal_delay": 25.0, "diversion": 0.2, "safety": 0.0, "blocked": False}),
        ("J3", "J5", {"distance": 5.0, "travel_time": 300.0, "congestion": 0.2, "queue": 1.0, "signal_delay": 15.0, "diversion": 0.1, "safety": 0.0, "blocked": False}),
        ("J1", "J4", {"distance": 6.0, "travel_time": 360.0, "congestion": 0.1, "queue": 0.0, "signal_delay": 10.0, "diversion": 0.0, "safety": 0.0, "blocked": False}),
        ("J4", "J5", {"distance": 4.0, "travel_time": 260.0, "congestion": 0.2, "queue": 1.0, "signal_delay": 12.0, "diversion": 0.0, "safety": 0.0, "blocked": False}),
        ("J2", "J4", {"distance": 2.0, "travel_time": 150.0, "congestion": 0.6, "queue": 5.0, "signal_delay": 30.0, "diversion": 0.3, "safety": 0.1, "blocked": False}),
    ]
    for u, v, d in edges:
        g.add_edge(u, v, **d)
    return g


def get_graph() -> nx.DiGraph:
    global _graph
    if _graph is None:
        _graph = _build_demo()
    return _graph


def reset_graph() -> nx.DiGraph:
    global _graph
    _graph = _build_demo()
    return _graph


def set_blocked(u: str, v: str, blocked: bool = True) -> None:
    g = get_graph()
    if g.has_edge(u, v):
        g[u][v]["blocked"] = blocked


def pedestrian_active(junction: str) -> bool:
    return _pedestrian.get(junction, False)


def set_pedestrian(junction: str, active: bool) -> None:
    _pedestrian[junction] = active
