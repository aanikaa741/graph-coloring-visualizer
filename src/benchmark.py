"""
benchmark.py
Benchmarks greedy vs backtracking graph coloring across graph sizes.

Greedy runs up to n=100 (polynomial, fast).
Backtracking is capped at n=35 (exponential -- blows up past this).

Results are saved to data/results.json for the visualizer to use.
"""

import time
import json
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from graph_gen import generate_random_graph
from greedy_coloring import greedy_coloring
from backtracking_coloring import chromatic_number

# graph sizes to test
GREEDY_SIZES   = [5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 75, 100]
BACKTRACK_SIZES = [5, 10, 15, 20, 25, 30, 35]

EDGE_PROB = 0.4   # graph density: ~40% of possible edges exist
SEED      = 42
RUNS      = 3     # average over this many runs to reduce timing noise


def time_fn(fn, runs=RUNS):
    """Run fn() `runs` times and return (avg_seconds, result_of_last_run)."""
    result = None
    total = 0.0
    for _ in range(runs):
        start = time.perf_counter()
        result = fn()
        total += time.perf_counter() - start
    return total / runs, result


def run_benchmark():
    results = {
        "edge_prob": EDGE_PROB,
        "seed": SEED,
        "greedy": [],
        "backtracking": [],
    }

    print("── Greedy coloring benchmark ──")
    for n in GREEDY_SIZES:
        g = generate_random_graph(n=n, p=EDGE_PROB, seed=SEED)
        avg_time, (_, num_colors) = time_fn(lambda g=g: greedy_coloring(g, order="degree_desc"))
        results["greedy"].append({
            "n": n,
            "colors": num_colors,
            "time_ms": round(avg_time * 1000, 4),
        })
        print(f"  n={n:4d}  colors={num_colors}  time={avg_time*1000:.4f}ms")

    print("\n── Backtracking coloring benchmark (exact, capped at n=35) ──")
    for n in BACKTRACK_SIZES:
        g = generate_random_graph(n=n, p=EDGE_PROB, seed=SEED)
        avg_time, (chi, _) = time_fn(lambda g=g: chromatic_number(g))
        results["backtracking"].append({
            "n": n,
            "colors": chi,
            "time_ms": round(avg_time * 1000, 4),
        })
        print(f"  n={n:4d}  chi={chi}  time={avg_time*1000:.4f}ms")

    # save results
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    return results


if __name__ == "__main__":
    run_benchmark()
