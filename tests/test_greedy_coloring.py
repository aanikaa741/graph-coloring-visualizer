"""
test_greedy_coloring.py
Unit tests for greedy_coloring.py

Run with: python3 -m pytest tests/test_greedy_coloring.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from greedy_coloring import greedy_coloring, is_valid_coloring
from graph_gen import generate_random_graph


def test_empty_graph():
    """A graph with no vertices should produce an empty coloring."""
    adj = {}
    coloring, num_colors = greedy_coloring(adj)
    assert coloring == {}
    assert num_colors == 0


def test_single_vertex():
    """A single isolated vertex needs exactly 1 color."""
    adj = {0: set()}
    coloring, num_colors = greedy_coloring(adj)
    assert num_colors == 1
    assert coloring[0] == 0


def test_two_isolated_vertices():
    """Two vertices with no edge between them can share color 0."""
    adj = {0: set(), 1: set()}
    coloring, num_colors = greedy_coloring(adj)
    assert num_colors == 1
    assert coloring[0] == coloring[1] == 0


def test_single_edge():
    """Two connected vertices must get different colors."""
    adj = {0: {1}, 1: {0}}
    coloring, num_colors = greedy_coloring(adj)
    assert num_colors == 2
    assert coloring[0] != coloring[1]


def test_triangle_needs_three_colors():
    """A triangle (K3, complete graph on 3 vertices) requires exactly 3 colors."""
    adj = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}}
    coloring, num_colors = greedy_coloring(adj)
    assert num_colors == 3
    assert is_valid_coloring(adj, coloring)


def test_bipartite_graph_uses_two_colors_with_good_order():
    """
    A bipartite graph (e.g. a 4-cycle: 0-1-2-3-0) has chromatic number 2.
    With degree_desc or natural order this should still find 2 colors
    since all vertices have equal degree here.
    """
    adj = {0: {1, 3}, 1: {0, 2}, 2: {1, 3}, 3: {0, 2}}
    coloring, num_colors = greedy_coloring(adj, order="natural")
    assert num_colors == 2
    assert is_valid_coloring(adj, coloring)


def test_complete_graph_needs_n_colors():
    """A complete graph K_n always needs exactly n colors, regardless of order."""
    n = 5
    adj = {v: set(range(n)) - {v} for v in range(n)}
    for order in ["natural", "degree_desc", "random"]:
        coloring, num_colors = greedy_coloring(adj, order=order, seed=0)
        assert num_colors == n
        assert is_valid_coloring(adj, coloring)


def test_validity_on_random_graphs():
    """
    Property-based check: for many random graphs and orderings,
    the greedy coloring must always be a VALID coloring (no two
    adjacent vertices share a color), even though the number of
    colors used may vary by ordering.
    """
    for seed in range(20):
        adj = generate_random_graph(n=15, p=0.3, seed=seed)
        for order in ["natural", "degree_desc", "random"]:
            coloring, num_colors = greedy_coloring(adj, order=order, seed=seed)
            assert is_valid_coloring(adj, coloring), (
                f"Invalid coloring on seed={seed}, order={order}"
            )
            # sanity bound: greedy never needs more than max_degree + 1 colors
            max_degree = max((len(neighbors) for neighbors in adj.values()), default=0)
            assert num_colors <= max_degree + 1, (
                f"Greedy used more than max_degree+1 colors on seed={seed}"
            )


def test_ordering_can_change_color_count():
    """
    Demonstrates the key theoretical point: different vertex orderings
    can produce different numbers of colors on the same graph.
    This is not asserting a specific outcome, just that the function
    behaves consistently and colorings remain valid across orderings.
    """
    adj = generate_random_graph(n=20, p=0.3, seed=42)
    results = {}
    for order in ["natural", "degree_desc", "random"]:
        coloring, num_colors = greedy_coloring(adj, order=order, seed=1)
        assert is_valid_coloring(adj, coloring)
        results[order] = num_colors
    # just confirm we recorded a result for every strategy
    assert set(results.keys()) == {"natural", "degree_desc", "random"}


if __name__ == "__main__":
    # allow running without pytest installed, as a plain script
    test_fns = [
        test_empty_graph,
        test_single_vertex,
        test_two_isolated_vertices,
        test_single_edge,
        test_triangle_needs_three_colors,
        test_bipartite_graph_uses_two_colors_with_good_order,
        test_complete_graph_needs_n_colors,
        test_validity_on_random_graphs,
        test_ordering_can_change_color_count,
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
