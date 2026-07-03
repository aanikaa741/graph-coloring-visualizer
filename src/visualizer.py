"""
visualizer.py
Generates all project figures:
  1. Runtime comparison chart (greedy vs backtracking)
  2. Color count comparison chart (greedy vs backtracking, where both ran)
  3. Side-by-side colored graph drawings for a sample graph

Saves figures to data/figures/
"""

import json
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

sys.path.insert(0, os.path.dirname(__file__))
from graph_gen import generate_random_graph
from greedy_coloring import greedy_coloring
from backtracking_coloring import chromatic_number

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

PALETTE = [
    "#E63946", "#457B9D", "#2A9D8F", "#E9C46A",
    "#F4A261", "#6A4C93", "#A8DADC", "#264653",
    "#90BE6D", "#F9C74F", "#F8961E", "#43AA8B",
    "#577590", "#F94144", "#277DA1", "#4D908E",
]


# ── Figure 1: Runtime comparison ────────────────────────────────────────────

def plot_runtime(results):
    fig, ax = plt.subplots(figsize=(9, 5))

    g_ns    = [r["n"]       for r in results["greedy"]]
    g_times = [r["time_ms"] for r in results["greedy"]]
    b_ns    = [r["n"]       for r in results["backtracking"]]
    b_times = [r["time_ms"] for r in results["backtracking"]]

    ax.plot(g_ns, g_times, "o-", color="#457B9D", linewidth=2.5,
            markersize=6, label="Greedy (degree-descending order)")
    ax.plot(b_ns, b_times, "s-", color="#E63946", linewidth=2.5,
            markersize=6, label="Backtracking (exact, capped at n=35)")

    ax.set_xlabel("Number of vertices (n)", fontsize=12)
    ax.set_ylabel("Average runtime (ms, log scale)", fontsize=12)
    ax.set_title("Runtime Comparison: Greedy vs Backtracking Graph Coloring\n"
                 f"(Erdős–Rényi G(n, p={results['edge_prob']}), averaged over 3 runs)",
                 fontsize=12, fontweight="bold")
    ax.set_yscale("log")
    ax.legend(fontsize=10)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.annotate("Exponential\ngrowth →", xy=(30, b_times[-2]),
                xytext=(22, b_times[-2] * 5),
                arrowprops=dict(arrowstyle="->", color="#E63946"),
                color="#E63946", fontsize=9)

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "runtime_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


# ── Figure 2: Color count comparison ────────────────────────────────────────

def plot_color_count(results):
    # only sizes where both algorithms ran
    bt_ns     = {r["n"]: r["colors"] for r in results["backtracking"]}
    g_by_n    = {r["n"]: r["colors"] for r in results["greedy"]}
    shared_ns = sorted(bt_ns.keys())

    g_colors  = [g_by_n[n]  for n in shared_ns]
    bt_colors = [bt_ns[n]   for n in shared_ns]
    gap       = [g - b for g, b in zip(g_colors, bt_colors)]

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(shared_ns, bt_colors, "s-", color="#2A9D8F", linewidth=2.5,
            markersize=7, label="Backtracking — exact χ(G)")
    ax.plot(shared_ns, g_colors,  "o-", color="#F4A261", linewidth=2.5,
            markersize=7, label="Greedy — colors used")
    ax.fill_between(shared_ns, bt_colors, g_colors,
                    alpha=0.15, color="#F4A261",
                    label="Suboptimality gap (greedy − χ(G))")

    ax.set_xlabel("Number of vertices (n)", fontsize=12)
    ax.set_ylabel("Colors used", fontsize=12)
    ax.set_title("Color Count: Greedy vs Exact Chromatic Number\n"
                 f"(Erdős–Rényi G(n, p={results['edge_prob']}), same seed)",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.yaxis.get_major_locator().set_params(integer=True)

    # annotate the gap at n=25
    idx = shared_ns.index(25)
    if gap[idx] > 0:
        ax.annotate(f"+{gap[idx]} extra\ncolors at n=25",
                    xy=(25, g_colors[idx]),
                    xytext=(27, g_colors[idx] + 0.4),
                    arrowprops=dict(arrowstyle="->", color="#F4A261"),
                    fontsize=9, color="#F4A261")

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "color_count_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


# ── Figure 3: Side-by-side colored graph drawings ───────────────────────────

def _draw_colored_graph(ax, adj, coloring, title):
    G = nx.Graph()
    G.add_nodes_from(adj.keys())
    for v, neighbors in adj.items():
        for u in neighbors:
            if u > v:
                G.add_edge(v, u)

    pos = nx.spring_layout(G, seed=7)
    node_colors = [PALETTE[coloring[v] % len(PALETTE)] for v in G.nodes()]

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4, width=1.5, edge_color="#888")
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=500, edgecolors="#333", linewidths=1.2)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=9,
                            font_color="white", font_weight="bold")

    num_colors = len(set(coloring.values()))
    ax.set_title(f"{title}\n({num_colors} colors used)", fontsize=11, fontweight="bold")
    ax.axis("off")

    # legend patches
    patches = [
        mpatches.Patch(color=PALETTE[c % len(PALETTE)], label=f"Color {c}")
        for c in sorted(set(coloring.values()))
    ]
    ax.legend(handles=patches, loc="lower left", fontsize=8,
              framealpha=0.7, ncol=2)


def plot_colored_graphs():
    adj = generate_random_graph(n=12, p=0.4, seed=42)

    greedy_coloring_result, greedy_n = greedy_coloring(adj, order="natural")
    greedy_deg_result,      greedy_d = greedy_coloring(adj, order="degree_desc")
    chi, bt_coloring                 = chromatic_number(adj)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Graph Coloring on the Same Graph (n=12, p=0.4)\n"
                 "Greedy (natural order) vs Greedy (degree-desc) vs Exact Backtracking",
                 fontsize=12, fontweight="bold")

    _draw_colored_graph(axes[0], adj, greedy_coloring_result, "Greedy — natural order")
    _draw_colored_graph(axes[1], adj, greedy_deg_result,      "Greedy — degree-desc order")
    _draw_colored_graph(axes[2], adj, bt_coloring,            "Backtracking (exact χ(G))")

    fig.tight_layout()
    path = os.path.join(FIGURES_DIR, "colored_graph_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    results_path = os.path.join(os.path.dirname(__file__), "..", "data", "results.json")
    with open(results_path) as f:
        results = json.load(f)

    plot_runtime(results)
    plot_color_count(results)
    plot_colored_graphs()
    print("\nAll figures saved to data/figures/")
