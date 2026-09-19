"""Weighted route scoring + k candidate routes over the shared graph."""
import itertools
import networkx as nx
from . import network_store as net


def edge_cost(d: dict, w: dict) -> float:
    return (
        w["travel_time"] * d.get("travel_time", 0.0)
        + w["congestion"] * d.get("congestion", 0.0) * 100.0
        + w["queue"] * d.get("queue", 0.0) * 10.0
        + w["signal_delay"] * d.get("signal_delay", 0.0)
        + w["diversion"] * d.get("diversion", 0.0) * 100.0
        + w["safety"] * d.get("safety", 0.0) * 200.0
    )


def _open_graph() -> nx.DiGraph:
    g = net.get_graph()
    h = nx.DiGraph()
    h.add_nodes_from(g.nodes)
    for u, v, d in g.edges(data=True):
        if not d.get("blocked"):
            h.add_edge(u, v, **d)
    return h


def candidate_routes(origin: str, dest_nodes: list[str], k: int = 2) -> list[dict]:
    w = net.get_weights()
    g = _open_graph()
    cands: list[dict] = []
    for dest in dest_nodes:
        if origin not in g or dest not in g:
            continue
        try:
            paths = list(itertools.islice(nx.shortest_simple_paths(g, origin, dest, weight=lambda u, v, d: edge_cost(d, w)), k))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue
        for p in paths:
            roads, dist, t = [], 0.0, 0.0
            score = 0.0
            for u, v in zip(p, p[1:]):
                d = g[u][v]
                roads.append(f"{u}-{v}")
                dist += d.get("distance", 0.0)
                t += d.get("travel_time", 0.0) + d.get("signal_delay", 0.0)
                score += edge_cost(d, w)
            cands.append({"nodes": p, "roads": roads, "distance": dist, "estimated_time": t, "score": score})
    cands.sort(key=lambda c: c["score"])
    return cands[: max(k, 1)]
