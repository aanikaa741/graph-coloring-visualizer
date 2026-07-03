"""
graph_gen.py
Generates random undirected graphs for testing graph coloring algorithms.

We use the Erdos-Renyi G(n, p) model: n nodes, each possible edge included
independently with probability p. This gives us control over graph density,
which directly affects how hard coloring becomes (denser graphs need more
colors and are harder to color optimally).

Graphs are represented as an adjacency list: dict[int, set[int]]
"""

import random


def generate_random_graph(n, p, seed=None):
    """
    Generate a random undirected graph using the Erdos-Renyi G(n, p) model.

    Args:
        n: number of vertices (labeled 0 to n-1)
        p: probability that any given edge (u, v) exists, 0 <= p <= 1
        seed: optional random seed for reproducibility

    Returns:
        adjacency list as dict[int, set[int]], e.g. {0: {1, 2}, 1: {0}, 2: {0}}
    """
    if seed is not None:
        random.seed(seed)

    adj = {v: set() for v in range(n)}

    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < p:
                adj[u].add(v)
                adj[v].add(u)

    return adj


def graph_density(adj):
    """Return actual edge density: edges / max_possible_edges."""
    n = len(adj)
    if n < 2:
        return 0.0
    edge_count = sum(len(neighbors) for neighbors in adj.values()) // 2
    max_edges = n * (n - 1) // 2
    return edge_count / max_edges


def edge_count(adj):
    """Return number of edges in the graph."""
    return sum(len(neighbors) for neighbors in adj.values()) // 2


if __name__ == "__main__":
    # quick sanity check
    g = generate_random_graph(n=8, p=0.4, seed=42)
    print("Adjacency list:")
    for v, neighbors in g.items():
        print(f"  {v}: {sorted(neighbors)}")
    print(f"Vertices: {len(g)}")
    print(f"Edges: {edge_count(g)}")
    print(f"Density: {graph_density(g):.3f}")
