"""Small signal-timing QUBO over x(junction, phase). Prototype only."""
import numpy as np


def build(junctions: list[str], phases: tuple[str, ...] = ("PHASE_1", "PHASE_2"), seed: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    n = len(junctions) * len(phases)
    Q = np.zeros((n, n))
    idx = { (j, p): i for i, (j, p) in enumerate([(j, p) for j in junctions for p in phases])}
    for j in junctions:
        w = rng.uniform(5, 15)
        for p in phases:
            Q[idx[(j, p)], idx[(j, p)]] += w  # waiting/queue cost proxy
        # penalty: exactly one phase per junction
        lam = 30.0
        for a in phases:
            for b in phases:
                Q[idx[(j, a)], idx[(j, b)]] += lam
            Q[idx[(j, a)], idx[(j, a)]] -= lam
    # penalty: conflicting greens across neighbours (simplified all-pairs)
    for i in range(len(junctions) - 1):
        lam = 8.0
        Q[idx[(junctions[i], "PHASE_2")], idx[(junctions[i + 1], "PHASE_2")]] += lam
    return {"junctions": junctions, "phases": list(phases), "Q": Q.tolist(), "variables": n}


def energy(Q: list[list[float]], bits: list[int]) -> float:
    import numpy as np
    Qm = np.array(Q); b = np.array(bits)
    return float(b @ Qm @ b)
