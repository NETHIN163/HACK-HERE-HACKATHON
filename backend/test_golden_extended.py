"""Extended Golden Demo — covers all 6 P0 demo stages."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app.services import network_store as net
from app.services import emergency_service as ems
from app.services import rerouting_service as rr
from app.services import corridor_service as corridor
from app.services import conflict_service as cf
from app.optimization import qubo as Q, evaluator as ev

def _sep(t):
    print(f"\n{'='*56}\n  {t}\n{'='*56}")

def main():
    _sep("STAGE 0: Reset")
    net.reset_graph()
    ems._emergencies.clear(); ems._routes.clear()
    corridor._reservations.clear(); cf._locks.clear()
    print("  State reset OK")

    _sep("STAGE 1: Emergency creation + auto-assign")
    em = ems.create("TRAUMA", 1, "J1")
    assert em.ambulance_id, "Ambulance must be auto-assigned"
    assert em.route_id, "Route must be auto-generated"
    assert em.status.value == "EN_ROUTE"
    r1 = ems.active_route(em.emergency_id)
    assert r1 and r1.status.value == "ACTIVE"
    print(f"  Emergency: {em.emergency_id} | Ambulance: {em.ambulance_id} | Roads: {r1.roads}")

    _sep("STAGE 2: Green Corridor")
    corr = corridor.current(em.emergency_id)
    assert corr, "Corridor must be generated"
    assert corr[0]["state"] == "GREEN", f"Head must be GREEN, got {corr[0]['state']}"
    print(f"  Corridor: {[(c['junction'], c['state']) for c in corr]}")

    _sep("STAGE 3: Accident on active route -> reroute")
    u, v = r1.roads[0].split("-", 1)
    rr.handle_incident(u, v)
    r2 = ems.active_route(em.emergency_id)
    assert r2 and f"{u}-{v}" not in r2.roads, f"Route must avoid blocked road {u}-{v}"
    assert r2.status.value == "ACTIVE"
    assert r1.route_id != r2.route_id, "New route must have new ID"
    print(f"  Blocked: {u}-{v} | New route: {r2.route_id} | Roads: {r2.roads}")

    _sep("STAGE 4: Two-ambulance conflict")
    d = cf.resolve("J4",
        {"ambulance_id": "A1", "priority": 2, "eta_seconds": 100, "dispatch_seq": 1},
        {"ambulance_id": "A2", "priority": 1, "eta_seconds": 500, "dispatch_seq": 2})
    assert d["first"] == "A2", "Priority-1 ambulance goes first"
    assert d["cleared"] == ["A2", "A1"]
    print(f"  Decision: {d}")

    _sep("STAGE 5: Pedestrian safety")
    em2 = ems.create("CARDIAC", 2, "J1")
    r_ped = ems.active_route(em2.emergency_id)
    if r_ped and r_ped.nodes:
        fn = r_ped.nodes[0]
        net.set_pedestrian(fn, True)
        c2 = corridor.generate(em2.emergency_id, r_ped.nodes)
        assert c2[0]["state"] == "PENDING_PEDESTRIAN_CLEARANCE", f"Got {c2[0]['state']}"
        print(f"  Pedestrian at {fn}: {c2[0]['state']}")
        cleared = corridor.clear_pedestrian(fn, em2.emergency_id)
        assert cleared and cleared["state"] == "GREEN"
        print(f"  After clearance: {cleared['state']}")
        net.set_pedestrian(fn, False)

    _sep("STAGE 6: QUBO + Classical vs Hybrid")
    q = Q.build(["J1", "J2", "J3"])
    assert q["variables"] == 6
    c_res = ev.classical(q); h_res = ev.hybrid(q)
    assert c_res["configuration"] and h_res["configuration"]
    m_c = ev.metrics_for(c_res["configuration"])
    m_h = ev.metrics_for(h_res["configuration"])
    for k in ("average_waiting_time", "emergency_travel_time", "throughput", "co2_estimate"):
        assert k in m_c and k in m_h
    print(f"  Classical obj: {c_res['objective']:.1f} | config: {c_res['configuration']}")
    print(f"  Hybrid    obj: {h_res['objective']:.1f} | mode: {h_res['mode']} | config: {h_res['configuration']}")
    print(f"  Classical metrics: wait={m_c['average_waiting_time']:.1f} co2={m_c['co2_estimate']:.1f}")
    print(f"  Hybrid    metrics: wait={m_h['average_waiting_time']:.1f} co2={m_h['co2_estimate']:.1f}")

    _sep("ALL 6 STAGES PASSED [GOLDEN DEMO OK]")
    print(f"  Emergency: {em.emergency_id}")
    print(f"  Reroute:   {r2.route_id} avoids {u}-{v}")
    print(f"  Conflict:  {d['first']} goes first (priority 1)")
    print(f"  QAOA mode: {h_res['mode']}")

if __name__ == "__main__":
    main()
