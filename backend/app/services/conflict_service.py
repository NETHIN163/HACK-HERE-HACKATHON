"""Deterministic two-ambulance intersection arbitration. Never dual-green."""
_locks: dict[str, str] = {}


def resolve(junction: str, amb_a: dict, amb_b: dict) -> dict:
    """amb = {ambulance_id, priority, eta_seconds, dispatch_seq}. Lower priority number wins, then lower ETA, then lower seq, then id."""
    key = lambda a: (a["priority"], a["eta_seconds"], a["dispatch_seq"], a["ambulance_id"])
    first, second = (amb_a, amb_b) if key(amb_a) <= key(amb_b) else (amb_b, amb_a)
    if _locks.get(junction) not in (None, first["ambulance_id"]):
        raise ValueError(f"Intersection {junction} already reserved")
    _locks[junction] = first["ambulance_id"]
    decision = {"junction": junction, "first": first["ambulance_id"], "second": second["ambulance_id"], "cleared": [first["ambulance_id"]]}
    # simulate sequential clearance
    _locks.pop(junction, None)
    decision["cleared"] = [first["ambulance_id"], second["ambulance_id"]]
    return decision
