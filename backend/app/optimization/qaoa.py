"""QAOA via Qiskit Aer with classical fallback. Never claims optimality.

PROTOTYPE: fixed angles, no variational optimisation loop.
Valid hackathon claim: explores hybrid quantum-classical approach vs classical baseline.
"""
from . import qubo as Q


def solve(qubo: dict, reps: int = 1, shots: int = 256) -> dict:
    n = qubo["variables"]
    try:
        import numpy as np
        from qiskit.quantum_info import SparsePauliOp
        from qiskit.circuit.library import QAOAAnsatz
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator
        import math

        Qm = np.array(qubo["Q"])

        # Build Ising Hamiltonian from QUBO (Qiskit uses big-endian Pauli strings)
        paulis, coeffs = [], []
        for i in range(n):
            label = "I" * (n - i - 1) + "Z" + "I" * i
            paulis.append(label)
            coeffs.append(float(Qm[i, i]) / 2.0)
            for j in range(i + 1, n):
                if Qm[i, j] != 0.0:
                    label_list = ["I"] * n
                    label_list[n - i - 1] = "Z"
                    label_list[n - j - 1] = "Z"
                    paulis.append("".join(label_list))
                    coeffs.append(float(Qm[i, j]) / 4.0)

        op = SparsePauliOp(paulis, coeffs=coeffs)
        ansatz = QAOAAnsatz(cost_operator=op, reps=reps)

        # Fixed prototype angles (no variational loop in hackathon demo)
        param_values = [math.pi / 4] * ansatz.num_parameters
        bound = ansatz.assign_parameters(param_values)

        n_qubits = bound.num_qubits
        full = QuantumCircuit(n_qubits, n_qubits)
        full.compose(bound, inplace=True)
        full.measure(range(n_qubits), range(n_qubits))
        sim = AerSimulator()
        res = sim.run(full, shots=shots).result()
        counts = res.get_counts()
        top = sorted(counts.items(), key=lambda kv: -kv[1])[:16]
        out = []
        for bits_str, count in top:
            bits_str = bits_str.replace(" ", "")
            # Qiskit measurement output is in reverse qubit order; reverse to get variable order
            bits = [int(x) for x in reversed(bits_str)][:n]
            bits += [0] * (n - len(bits))  # pad if ansatz has more qubits than QUBO vars
            out.append({"bits": bits, "count": count, "objective": Q.energy(qubo["Q"], bits)})
        out.sort(key=lambda d: d["objective"])
        return {"mode": "HYBRID", "candidates": out, "shots": shots, "qubits": n_qubits}
    except Exception as e:
        import random
        rng = random.Random(7)
        out = []
        for _ in range(16):
            b = [rng.randint(0, 1) for _ in range(n)]
            out.append({"bits": b, "count": 1, "objective": Q.energy(qubo["Q"], b)})
        out.sort(key=lambda d: d["objective"])
        return {
            "mode": "HYBRID_FALLBACK",
            "candidates": out,
            "shots": 16,
            "note": f"Qiskit simulator unavailable ({type(e).__name__}); using random sampling fallback",
        }


def to_signal_config(qubo: dict, bits: list[int]) -> dict:
    """Convert a QUBO bit vector into a {junction: phase} signal configuration."""
    cfg = {}
    phases = qubo["phases"]
    k = 0
    for j in qubo["junctions"]:
        # Pick the phase whose bit is set; default to phases[0] if all zero
        selected = phases[0]
        for p_idx, p in enumerate(phases):
            if k + p_idx < len(bits) and bits[k + p_idx] == 1:
                selected = p
                break
        cfg[j] = selected
        k += len(phases)
    return cfg

