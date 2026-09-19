"""QAOA via Qiskit Aer with classical fallback. Never claims optimality."""
from . import qubo as Q


def solve(qubo: dict, reps: int = 1, shots: int = 256) -> dict:
    n = qubo["variables"]
    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator
        from qiskit.circuit.library import QAOAAnsatz
        from qiskit.quantum_info import SparsePauliOp
        import numpy as np
        Qm = np.array(qubo["Q"])
        # Ising from QUBO diagonal/off-diagonal (Z-basis, prototype mapping)
        paulis, coeffs = [], []
        for i in range(n):
            paulis.append("I" * i + "Z" + "I" * (n - i - 1)); coeffs.append(float(Qm[i, i]) / 2)
            for j in range(i + 1, n):
                if Qm[i, j]:
                    s = ["I"] * n; s[i] = "Z"; s[j] = "Z"
                    paulis.append("".join(s)); coeffs.append(float(Qm[i, j]) / 4)
        op = SparsePauliOp(paulis, coeffs)
        ansatz = QAOAAnsatz(op, reps=reps)
        qc = QuantumCircuit(n + ansatz.num_parameters)
        # fixed prototype angles (no variational loop in demo)
        import math
        bound = ansatz.assign_parameters([0.5] * ansatz.num_parameters)
        full = QuantumCircuit(n, n)
        full.compose(bound, inplace=True)
        full.measure(range(n), range(n))
        sim = AerSimulator()
        res = sim.run(full, shots=shots).result()
        counts = res.get_counts()
        cands = sorted(counts.items(), key=lambda kv: -kv[1])[:16]
        out = []
        for bits, c in cands:
            b = [int(x) for x in bits.replace(" ", "")[:n]]
            out.append({"bits": b, "count": c, "objective": Q.energy(qubo["Q"], b)})
        out.sort(key=lambda d: d["objective"])
        return {"mode": "HYBRID", "candidates": out, "shots": shots}
    except Exception as e:
        import random
        rng = random.Random(7)
        out = []
        for _ in range(16):
            b = [rng.randint(0, 1) for _ in range(n)]
            out.append({"bits": b, "count": 1, "objective": Q.energy(qubo["Q"], b)})
        out.sort(key=lambda d: d["objective"])
        return {"mode": "HYBRID_FALLBACK", "candidates": out, "shots": 16, "note": f"simulator fallback: {type(e).__name__}"}


def to_signal_config(qubo: dict, bits: list[int]) -> dict:
    cfg = {}
    k = 0
    for j in qubo["junctions"]:
        cfg[j] = qubo["phases"][1] if bits[k + 1] else qubo["phases"][0]
        k += len(qubo["phases"])
    return cfg
