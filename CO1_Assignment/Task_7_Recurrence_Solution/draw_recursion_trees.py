"""
draw_recursion_trees.py - recursion trees used to solve the recurrences in Task 7.

Problem: show the level-by-level cost of
  (a) recursive binary search   C(n) = C(floor(n/2)) + 1, C(0) = 0   -> one node per level, cost 1 each
  (b) merge sort preprocessing   C(n) = 2 C(n/2) + (n - 1), C(1) = 0
                                 -> 2^i nodes on level i, level cost n - 2^i
and print the level sums for n = 16 (so the drawing can be checked by hand).
Writes recursion_trees.png next to this file.
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
N = 16


def box(ax, x, y, text, color, w=1.5, h=0.6, size=11):
    ax.add_patch(plt.Rectangle((x - w / 2, y - h / 2), w, h, fc=color, ec="#333333", lw=1.1, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=size, zorder=3)


def binary_tree_panel(ax):
    sizes = []
    m = N
    while m >= 1:
        sizes.append(m)
        m //= 2
    for level, size in enumerate(sizes):
        y = -level * 1.15
        box(ax, 1.5, y, f"C({size})", "#cfe2f3")
        if level:
            ax.annotate("", xy=(1.5, y + 0.3), xytext=(1.5, y + 0.85),
                        arrowprops=dict(arrowstyle="-|>", color="#333333"))
        ax.text(2.6, y, f"level {level}: 1 subproblem of size {size} -> 1 comparison", va="center",
                fontsize=11)
    y = -len(sizes) * 1.15
    box(ax, 1.5, y, "C(0) = 0", "#f4cccc")
    ax.annotate("", xy=(1.5, y + 0.3), xytext=(1.5, y + 0.85),
                arrowprops=dict(arrowstyle="-|>", color="#333333"))
    ax.text(2.6, y, "empty range: base case, 0 comparisons", va="center", fontsize=11, color="#990000")
    ax.text(0.3, y - 1.2, f"Total = 1 per level x (floor(log2 {N}) + 1) levels = {len(sizes)} comparisons\n"
            f"In general C(n) = floor(log2 n) + 1  ->  Theta(log n)", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 10)
    ax.set_ylim(y - 1.8, 0.8)
    ax.axis("off")
    ax.set_title("(a) Recursive binary search (worst case):  C(n) = C(floor(n/2)) + 1", fontsize=13)
    print(f"(a) binary search, n = {N}: levels {sizes} -> total {len(sizes)} = floor(log2 n) + 1 = "
          f"{math.floor(math.log2(N)) + 1}")


def merge_tree_panel(ax):
    levels = int(math.log2(N))
    total = 0
    width = 12.0
    for level in range(levels + 1):
        count, size = 2 ** level, N // 2 ** level
        y = -level * 1.3
        for i in range(count):
            x = width * (i + 0.5) / count
            w = min(1.5, width / count * 0.85)
            box(ax, x, y, f"{size}" if count > 4 else f"C({size})", "#d9ead3" if size > 1 else "#f4cccc", w=w,
                size=10 if count > 4 else 11)
            if level:
                parent_x = width * (i // 2 + 0.5) / (count // 2)
                ax.plot([parent_x, x], [y + 1.3 - 0.28, y + 0.28], color="#777777", lw=0.8, zorder=1)
        cost = count * (size - 1) if size > 1 else 0
        total += cost
        label = (f"level {level}: {count} x merge of size {size} -> {count} x ({size} - 1) = {cost}"
                 if size > 1 else f"level {level}: {count} single records, base case -> 0")
        ax.text(width + 0.4, y, label, va="center", fontsize=11)
    bound = N * levels - N + 1
    ax.text(0, -(levels + 1) * 1.3 - 0.3, f"Total (worst case) = sum over levels of (n - 2^i) = {total} = "
            f"n log2 n - n + 1 = {bound}\nIn general C(n) = n log2 n - n + 1  ->  Theta(n log n)",
            fontsize=12, fontweight="bold")
    ax.set_xlim(-0.2, 23)
    ax.set_ylim(-(levels + 1) * 1.3 - 1.0, 0.8)
    ax.axis("off")
    ax.set_title("(b) Merge-sort preprocessing (worst case):  C(n) = 2 C(n/2) + (n - 1)", fontsize=13)
    print(f"(b) merge sort, n = {N}: total worst-case comparisons {total} = n log2 n - n + 1 = {bound}")


def main():
    fig, axes = plt.subplots(2, 1, figsize=(11, 12.5), gridspec_kw={"height_ratios": [1, 1.05]})
    binary_tree_panel(axes[0])
    merge_tree_panel(axes[1])
    fig.suptitle(f"Recursion trees for n = {N}", fontsize=14, fontweight="bold")
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "recursion_trees.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(path)


if __name__ == "__main__":
    main()
