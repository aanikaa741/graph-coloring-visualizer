"""
greedy_coloring.py
Greedy graph coloring algorithm.

THEORY:
Greedy coloring processes vertices in a fixed order. For each vertex v,
it assigns the smallest color (non-negative integer) that is not already
used by any of v's already-colored neighbors.

This is a polynomial-time heuristic: O(V + E) for a fixed vertex order,
since each vertex examines its neighbors' colors once.

Greedy coloring does NOT guarantee the chromatic number chi(G) -- the
minimum number of colors needed. The number of colors used depends
heavily on vertex ordering. A bad ordering can force greedy to use far
more colors than necessary. For example, "crown graphs" / specifically
constructed bipartite graphs can force greedy to use n/2 colors when
chi(G) = 2.

We support multiple vertex orderings to make this comparison concrete:
  - natural order (0, 1, 2, ..., n-1)
  - degree descending (largest-degree vertices colored first; this is
    a well-known heuristic that tends to use fewer colors in practice,
    since high-degree vertices are the most constrained)
  - random order
"""

import random


def greedy_coloring(adj, order="degree_desc", seed=None):
    """
    Color the graph using the greedy algorithm.

    Args:
        adj: adjacency list, dict[int, set[int]]
        order: vertex ordering strategy, one of:
            "natural"     -> 0, 1, 2, ..., n-1
            "degree_desc" -> highest degree vertices first
            "random"      -> random permutation
        seed: random seed, used only when order="random"

    Returns:
        coloring: dict[int, int] mapping vertex -> color (0-indexed)
        num_colors: int, total distinct colors used
    """
    vertices = list(adj.keys())

    if order == "natural":
        vertex_order = sorted(vertices)
    elif order == "degree_desc":
        vertex_order = sorted(vertices, key=lambda v: len(adj[v]), reverse=True)
    elif order == "random":
        if seed is not None:
            random.seed(seed)
        vertex_order = vertices.copy()
        random.shuffle(vertex_order)
    else:
        raise ValueError(f"Unknown order strategy: {order}")

    coloring = {}

    for v in vertex_order:
        # find colors already used by v's colored neighbors
        used_colors = {coloring[u] for u in adj[v] if u in coloring}

        # assign smallest non-negative integer not in used_colors
        color = 0
        while color in used_colors:
            color += 1

        coloring[v] = color

    num_colors = len(set(coloring.values()))
    return coloring, num_colors


def is_valid_coloring(adj, coloring):
    """
    Verify that no two adjacent vertices share the same color.
    Used as a correctness check / unit test helper.
    """
    for v, neighbors in adj.items():
        for u in neighbors:
            if coloring[v] == coloring[u]:
                return False
    return True


if __name__ == "__main__":
    from graph_gen import generate_random_graph

    g = generate_random_graph(n=8, p=0.4, seed=42)

    for order in ["natural", "degree_desc", "random"]:
        coloring, num_colors = greedy_coloring(g, order=order, seed=1)
        valid = is_valid_coloring(g, coloring)
        print(f"Order: {order:12s} | Colors used: {num_colors} | Valid: {valid}")
        print(f"  Coloring: {coloring}")
