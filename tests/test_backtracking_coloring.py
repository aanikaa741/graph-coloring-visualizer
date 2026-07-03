"""
test_backtracking_coloring.py
Unit tests for backtracking_coloring.py

Run with: python3 -m pytest tests/test_backtracking_coloring.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from backtracking_coloring import chromatic_number, can_color_with_k, is_valid_coloring
from graph_gen import generate_random_graph


def test_empty_graph():
    """An empty graph has chromatic number 0."""
    chi, coloring = chromatic_number({})
    assert chi == 0
    assert coloring == {}


def test_single_vertex():
    """A single isolated vertex has chromatic number 1."""
    adj = {0: set()}
    chi, coloring = chromatic_number(adj)
    assert chi == 1


def test_two_isolated_vertices():
    """Two vertices with no edge can share 1 color."""
    adj = {0: set(), 1: set()}
    chi, coloring = chromatic_number(adj)
    assert chi == 1


def test_single_edge_needs_two_colors():
    """Two connected vertices need exactly 2 colors."""
    adj = {0: {1}, 1: {0}}
    chi, coloring = chromatic_number(adj)
    assert chi == 2
    assert is_valid_coloring(adj, coloring)


def test_triangle_needs_three_colors():
    """K3 (triangle) has chromatic number exactly 3 -- this is a known exact result."""
    adj = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}}
    chi, coloring = chromatic_number(adj)
    assert chi == 3
    assert is_valid_coloring(adj, coloring)


def test_complete_graph_kn_needs_n_colors():
    """K_n (complete graph) always has chromatic number exactly n."""
    for n in range(1, 6):
        adj = {v: set(range(n)) - {v} for v in range(n)}
        chi, coloring = chromatic_number(adj)
        assert chi == n, f"K_{n} should need exactly {n} colors, got {chi}"
        assert is_valid_coloring(adj, coloring)


def test_even_cycle_needs_two_colors():
    """
    An even cycle (e.g. a 4-cycle or 6-cycle) is bipartite, so it has
    chromatic number exactly 2. This is a known graph theory result we
    can check exactly.
    """
    for n in [4, 6, 8]:
        adj = {v: set() for v in range(n)}
        for v in range(n):
            adj[v].add((v + 1) % n)
            adj[(v + 1) % n].add(v)
        chi, coloring = chromatic_number(adj)
        assert chi == 2, f"Even cycle C_{n} should need 2 colors, got {chi}"
        assert is_valid_coloring(adj, coloring)


def test_odd_cycle_needs_three_colors():
    """
    An odd cycle (e.g. a 5-cycle) is NOT bipartite, so it needs exactly 3
    colors -- this is a classic graph theory fact and a good exact check.
    """
    for n in [3, 5, 7]:
        adj = {v: set() for v in range(n)}
        for v in range(n):
            adj[v].add((v + 1) % n)
            adj[(v + 1) % n].add(v)
        chi, coloring = chromatic_number(adj)
        assert chi == 3, f"Odd cycle C_{n} should need 3 colors, got {chi}"
        assert is_valid_coloring(adj, coloring)


def test_can_color_with_k_rejects_insufficient_k():
    """A triangle cannot be colored with only 2 colors."""
    adj = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}}
    success, coloring = can_color_with_k(adj, k=2)
    assert success is False
    assert coloring is None


def test_can_color_with_k_accepts_sufficient_k():
    """A triangle CAN be colored with 3 colors."""
    adj = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}}
    success, coloring = can_color_with_k(adj, k=3)
    assert success is True
    assert is_valid_coloring(adj, coloring)


def test_validity_on_small_random_graphs():
    """
    Property-based check: for many small random graphs, the backtracking
    result must always be a VALID coloring. Kept small (n<=12) since
    backtracking is exponential and this needs to run quickly in CI/tests.
    """
    for seed in range(15):
        adj = generate_random_graph(n=10, p=0.3, seed=seed)
        chi, coloring = chromatic_number(adj)
        assert is_valid_coloring(adj, coloring), f"Invalid coloring on seed={seed}"
        assert len(set(coloring.values())) == chi


def test_backtracking_finds_optimal_leq_greedy():
    """
    Sanity cross-check against greedy: backtracking's exact chromatic
    number must never exceed what greedy achieves, since backtracking
    finds the true minimum. This is the core theoretical guarantee the
    whole project demonstrates.
    """
    from greedy_coloring import greedy_coloring

    for seed in range(10):
        adj = generate_random_graph(n=10, p=0.3, seed=seed)
        chi, _ = chromatic_number(adj)
        _, greedy_colors = greedy_coloring(adj, order="degree_desc")
        assert chi <= greedy_colors, (
            f"Backtracking chi={chi} should never exceed greedy's {greedy_colors} "
            f"colors on seed={seed}"
        )


if __name__ == "__main__":
    test_fns = [
        test_empty_graph,
        test_single_vertex,
        test_two_isolated_vertices,
        test_single_edge_needs_two_colors,
        test_triangle_needs_three_colors,
        test_complete_graph_kn_needs_n_colors,
        test_even_cycle_needs_two_colors,
        test_odd_cycle_needs_three_colors,
        test_can_color_with_k_rejects_insufficient_k,
        test_can_color_with_k_accepts_sufficient_k,
        test_validity_on_small_random_graphs,
        test_backtracking_finds_optimal_leq_greedy,
    ]
    passed = 0
    for fn in test_fns:
        try:
            fn()
            print(f"PASS: {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {fn.__name__} -- {e}")
    print(f"\n{passed}/{len(test_fns)} tests passed")
