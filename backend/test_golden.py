"""Deterministic Golden Demo: emergency -> route -> incident -> reroute -> corridor -> conflict -> optimization."""
from app.services import network_store as net
from app.services import emergency_service as ems
from app.services import rerouting_service as rr
from app.services import corridor_service as corridor
from app.services import conflict_service as cf
from app.optimization import qubo as Q, evaluator as ev


def main() -> None:
    net.reset_graph()
    em = ems.create("TRAUMA", 1, "J1")
    assert em.ambulance_id and em.route_id, "assignment failed"
    r1 = ems.active_route(em.emergency_id)
    assert r1 and "J2-J3" in r1.roads, f"expected J1-J2-J3 path, got {r1.roads if r1 else None}"
    corr = corridor.current(em.emergency_id)
    assert corr and corr[0]["state"] == "GREEN", "green corridor head must be GREEN"
    # accident on active route -> must reroute away from blocked road
    rr.handle_incident("J2", "J3")
    r2 = ems.active_route(em.emergency_id)
    assert r2 and "J2-J3" not in r2.roads, "ambulance must never continue toward blocked road"
    assert r2.status.value == "ACTIVE"
    # conflict: priority 1 beats priority 2 deterministically
    d = cf.resolve("J4",
                   {"ambulance_id": "A1", "priority": 2, "eta_seconds": 100, "dispatch_seq": 1},
                   {"ambulance_id": "A2", "priority": 1, "eta_seconds": 500, "dispatch_seq": 2})
    assert d["first"] == "A2" and d["cleared"] == ["A2", "A1"], "deterministic priority failed"
    # optimization: both modes on same QUBO, raw metrics only
    q = Q.build(["J1", "J2", "J3"])
    c, h = ev.classical(q), ev.hybrid(q)
    assert c["configuration"] and h["configuration"]
    print("GOLDEN DEMO OK:", em.emergency_id, r2.roads, d, h["configuration"])


if __name__ == "__main__":
    main()
