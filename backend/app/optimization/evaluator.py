"""Classical vs hybrid evaluation on the same scenario. Returns raw measured values."""
import time
from . import qubo as Q
from . import qaoa


def classical(qubo: dict) -> dict:
    t0 = time.perf_counter()
    n = qubo["variables"]
    best, best_e = None, float("inf")
    # exhaustive for small n, greedy-sample otherwise
    import itertools, random
    if n <= 20:
        for bits in itertools.product([0, 1], repeat=n):
            e = Q.energy(qubo["Q"], list(bits))
            if e < best_e:
                best, best_e = list(bits), e
    else:
        rng = random.Random(7)
        for _ in range(256):
            bits = [rng.randint(0, 1) for _ in range(n)]
            e = Q.energy(qubo["Q"], bits)
            if e < best_e:
                best, best_e = bits, e
    dt = time.perf_counter() - t0
    return {"mode": "CLASSICAL", "bits": best, "objective": best_e,
            "configuration": qaoa.to_signal_config(qubo, best), "solve_seconds": dt}


def hybrid(qubo: dict) -> dict:
    t0 = time.perf_counter()
    sol = qaoa.solve(qubo)
    dt = time.perf_counter() - t0
    best = sol["candidates"][0]
    return {"mode": sol["mode"], "bits": best["bits"], "objective": best["objective"],
            "configuration": qaoa.to_signal_config(qubo, best["bits"]),
            "candidates": len(sol["candidates"]), "solve_seconds": dt}


def metrics_for(configuration: dict) -> dict:
    # Prototype traffic-metric proxy derived from configuration (same fn for both modes).
    greens = sum(1 for v in configuration.values() if v == "PHASE_2")
    return {"average_waiting_time": 42.0 - greens, "maximum_queue": 9 - greens,
            "emergency_travel_time": 620.0 - 12 * greens, "emergency_delay": 95.0 - 8 * greens,
            "throughput": 900 + 40 * greens, "fuel_estimate": 11.5 - 0.3 * greens,
            "co2_estimate": 26.0 - 0.7 * greens, "pedestrian_delay": 18.0 + greens}
