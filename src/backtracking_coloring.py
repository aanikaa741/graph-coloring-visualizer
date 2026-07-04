"""
backtracking_coloring.py
Exact graph coloring via backtracking search.

THEORY:
Unlike greedy coloring, backtracking coloring guarantees finding the true
chromatic number chi(G)

Approach: for a fixed number of colors k, try to assign colors to vertices
one at a time (in some order). At each vertex, try every color from 0 to
k-1; if a color conflicts with an already-colored neighbor, skip it. If a
vertex has no valid color, backtrack: undo the previous vertex's
assignment and try its next color option.

To find chi(G), we run this with k = 1, 2, 3, ... until a valid coloring
is found. The smallest such k is chi(G).

COMPLEXITY:
This is exponential in the worst case: O(k^V) without pruning. Graph
coloring (deciding if a graph is k-colorable) is NP-complete for k >= 3,
so no known polynomial-time algorithm exists for the general case. We use
two pruning strategies to make this practical for the small/medium graphs
in our benchmark:

  1. Vertex ordering by degree (descending): coloring highly-constrained
     (high-degree) vertices first prunes the search tree much faster than
     leaving them for last, since failures are detected sooner.
  2. Forward feasibility check is implicit: a vertex's candidate colors
     are restricted to those not used by ALREADY-colored neighbors, so we
     never explore branches that are immediately invalid.

This is still exact backtracking, not a polynomial approximation -- the
exponential blowup is real and is exactly the point of comparing it
against greedy in this project.
"""


def _is_safe(adj, coloring, vertex, color):
    """Check if assigning `color` to `vertex` conflicts with any already-colored neighbor."""
    for neighbor in adj[vertex]:
        if coloring.get(neighbor) == color:
            return False
    return True


def _backtrack(adj, vertex_order, coloring, index, k):
    """
    Try to color vertex_order[index:] using colors 0..k-1, given that
    vertex_order[:index] are already colored in `coloring`.
    Returns True if successful (coloring is filled in completely), False
    if no valid coloring with k colors exists from this state.
    """
    if index == len(vertex_order):
        return True  # all vertices colored successfully

    vertex = vertex_order[index]

    for color in range(k):
        if _is_safe(adj, coloring, vertex, color):
            coloring[vertex] = color
            if _backtrack(adj, vertex_order, coloring, index + 1, k):
                return True
            del coloring[vertex]  # undo and try next color (the "backtrack" step)

    return False  # no color worked for this vertex with current k


def can_color_with_k(adj, k, vertex_order=None):
    """
    Determine if `adj` can be colored with exactly k colors.

    Returns:
        (success: bool, coloring: dict[int, int] or None)
    """
    if vertex_order is None:
        vertex_order = sorted(adj.keys(), key=lambda v: len(adj[v]), reverse=True)

    coloring = {}
    success = _backtrack(adj, vertex_order, coloring, 0, k)
    return success, (coloring if success else None)


def chromatic_number(adj):
    """
    Find the exact chromatic number chi(G) by trying k = 1, 2, 3, ...
    until a valid k-coloring is found.

    Returns:
        (chi: int, coloring: dict[int, int])
    """
    n = len(adj)
    if n == 0:
        return 0, {}

    vertex_order = sorted(adj.keys(), key=lambda v: len(adj[v]), reverse=True)

    for k in range(1, n + 1):
        success, coloring = can_color_with_k(adj, k, vertex_order)
        if success:
            return k, coloring

    # unreachable for a simple graph: k = n always works (every vertex its own color)
    raise RuntimeError("Failed to find a valid coloring even with k = n; this should not happen")


def is_valid_coloring(adj, coloring):
    """Verify that no two adjacent vertices share the same color."""
    for v, neighbors in adj.items():
        for u in neighbors:
            if coloring[v] == coloring[u]:
                return False
    return True


if __name__ == "__main__":
    from graph_gen import generate_random_graph

    g = generate_random_graph(n=8, p=0.4, seed=42)

    chi, coloring = chromatic_number(g)
    print(f"Chromatic number (exact, via backtracking): {chi}")
    print(f"Coloring: {coloring}")
    print(f"Valid: {is_valid_coloring(g, coloring)}")
