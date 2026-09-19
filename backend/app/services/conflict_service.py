"""Deterministic two-ambulance intersection arbitration. Never dual-green.

Priority key (ascending = more urgent):
  (emergency_priority, eta_seconds, dispatch_seq, ambulance_id)

Lifecycle:
  acquire(junction, ambulance_id)  -> reserves intersection
  release(junction)                -> clears reservation
  resolve(junction, amb_a, amb_b)  -> full arbitration with sequential clearance
"""
_locks: dict[str, str] = {}  # junction -> ambulance_id currently holding reservation


def _priority_key(a: dict) -> tuple:
    return (a["priority"], a["eta_seconds"], a["dispatch_seq"], a["ambulance_id"])


def acquire(junction: str, ambulance_id: str) -> bool:
    """Try to acquire junction for ambulance_id. Returns True if successful."""
    holder = _locks.get(junction)
    if holder is None or holder == ambulance_id:
        _locks[junction] = ambulance_id
        return True
    return False  # junction already held by a different ambulance


def release(junction: str) -> None:
    """Release a junction reservation."""
    _locks.pop(junction, None)


def holder(junction: str) -> str | None:
    """Return the ambulance_id currently holding the junction, or None."""
    return _locks.get(junction)


def resolve(junction: str, amb_a: dict, amb_b: dict) -> dict:
    """Arbitrate two ambulances at the same intersection.

    Never issues simultaneous conflicting greens.
    Returns a decision dict describing the safe clearance sequence.
    """
    first, second = (
        (amb_a, amb_b) if _priority_key(amb_a) <= _priority_key(amb_b) else (amb_b, amb_a)
    )
    current_holder = _locks.get(junction)
    if current_holder is not None and current_holder != first["ambulance_id"]:
        raise ValueError(
            f"Intersection {junction} already reserved by {current_holder}"
        )
    # Phase 1: first ambulance acquires and passes
    _locks[junction] = first["ambulance_id"]
    release(junction)
    # Phase 2: second ambulance acquires and passes
    _locks[junction] = second["ambulance_id"]
    release(junction)
    return {
        "junction": junction,
        "first": first["ambulance_id"],
        "second": second["ambulance_id"],
        "cleared": [first["ambulance_id"], second["ambulance_id"]],
        "reason": "priority+eta deterministic sequencing",
    }
