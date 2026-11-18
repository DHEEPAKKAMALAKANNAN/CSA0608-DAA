"""
draw_decision_tree.py - binary-search decision tree for n = 15 (Task 4, best/average/worst case).

Problem: the cases of binary search are easiest to see on its decision tree: every internal node is
one three-way comparison key : A[mid]; a successful search for the key stored at a node at depth d
(root depth 1) costs d comparisons; an unsuccessful search ends in an external node (a gap) after
passing through every internal node on its path.  The script computes the tree with exactly the same
mid = (low + high) // 2 rule as search_algorithms.binary_search_recursive, draws it, prints the
level counts, and writes binary_search_decision_tree.png next to this file.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
N = 15


def build(low, high, depth, x_left, x_right, nodes, gaps):
    """Record (index, depth, x) of every mid chosen for the range [low..high] and every gap."""
    if low > high:
        gaps.append((depth, (x_left + x_right) / 2, low))
        return
    mid = (low + high) // 2
    x = (x_left + x_right) / 2
    nodes.append((mid, depth, x))
    build(low, mid - 1, depth + 1, x_left, x, nodes, gaps)
    build(mid + 1, high, depth + 1, x, x_right, nodes, gaps)


def main():
    nodes, gaps = [], []
    build(0, N - 1, 1, 0.0, 16.0, nodes, gaps)
    position = {mid: (x, depth) for mid, depth, x in nodes}
    fig, ax = plt.subplots(figsize=(12, 6.2))
    for mid, depth, x in nodes:                       # edges to the children
        for child in nodes:
            if child[1] == depth + 1 and abs(child[2] - x) < 16 / 2 ** depth:
                ax.plot([x, child[2]], [-depth, -child[1]], color="#555555", lw=1, zorder=1)
    for depth, x, low in gaps:
        parent = min((p for p in nodes if p[1] == depth - 1), key=lambda p: abs(p[2] - x))
        ax.plot([parent[2], x], [-parent[1], -depth + 0.25], color="#bbbbbb", lw=0.8, ls="--", zorder=1)
        ax.add_patch(plt.Rectangle((x - 0.18, -depth + 0.07), 0.36, 0.3, fc="#f4cccc", ec="#990000", zorder=2))
    colors = {1: "#b6d7a8", 2: "#cfe2f3", 3: "#fff2cc", 4: "#f9cb9c"}
    for mid, depth, x in nodes:
        ax.scatter([x], [-depth], s=1250, color=colors[depth], edgecolors="#333333", zorder=3)
        ax.text(x, -depth, f"A[{mid}]", ha="center", va="center", fontsize=8.5, zorder=4)
    levels = {}
    for _, depth, _ in nodes:
        levels[depth] = levels.get(depth, 0) + 1
    total = 0
    for depth in sorted(levels):
        total += depth * levels[depth]
        ax.text(16.6, -depth, f"level {depth}: {levels[depth]} key(s) x {depth} comparison(s) = "
                f"{depth * levels[depth]}", va="center", fontsize=9)
    gap_depth = "/".join(str(d) for d in sorted({d - 1 for d, _, _ in gaps}))
    ax.text(16.6, -4.75, f"{len(gaps)} gaps (unsuccessful searches): {gap_depth} comparisons each",
            va="center", fontsize=9, color="#990000")
    ax.text(16.6, -5.35, f"successful: best 1, worst {max(levels)}, average {total}/{N} = {total / N:.2f}",
            va="center", fontsize=9, fontweight="bold")
    ax.set_xlim(-0.5, 25.5)
    ax.set_ylim(-5.8, -0.4)
    ax.axis("off")
    ax.set_title(f"Decision tree of recursive binary search for n = {N} (mid = (low + high) // 2): "
                 "depth = number of three-way comparisons", fontsize=11)
    path = os.path.join(OUT_DIR, "binary_search_decision_tree.png")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"levels {levels}, total successful comparisons {total}, average {total / N:.4f}")
    print(path)


if __name__ == "__main__":
    main()
