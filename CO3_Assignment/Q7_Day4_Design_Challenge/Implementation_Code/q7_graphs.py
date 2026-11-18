"""Q7 graphs - design diagram of the joint design and the comparison graphs of all variants.

Writes to results/: q7_design_diagram.png, q7_ratio_n8000.png, q7_growth.png, q7_guard_seed.png, q7_depth_moves.png
Run after q7_experiments.py:  py q7_graphs.py
"""
import csv
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
VARIANTS = ("Baseline", "A", "B", "Joint-v1", "Joint")
COLORS = {"Baseline": "#d62728", "A": "#1f77b4", "B": "#2ca02c", "Joint-v1": "#9467bd", "Joint": "#ff7f0e"}
MARKS = {"Baseline": "s", "A": "o", "B": "^", "Joint-v1": "v", "Joint": "D"}
DATASETS = ("random", "sorted", "reverse", "slots", "all-equal", "killer-A", "killer-B", "killer-J")


def read(name):
    with open(os.path.join(RESULTS, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get(rows, variant, dataset, n, key):
    r = next(r for r in rows if r["variant"] == variant and r["dataset"] == dataset and int(r["n"]) == n)
    return float(r[key])


def fig_design():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [1.1, 1]})
    # left: the fat partition of one sub-array
    stages = [("during the scan", [("= v", 1.2, "#ffe699"), ("< v", 2.6, "#c6e0b4"), ("unscanned", 2.4, "#ededed"),
                                   ("> v", 2.6, "#f8cbad"), ("= v", 1.2, "#ffe699")]),
              ("after the scan", [("= v", 1.4, "#ffe699"), ("< v", 3.6, "#c6e0b4"), ("> v", 3.6, "#f8cbad"),
                                  ("= v", 1.4, "#ffe699")]),
              ("equal blocks swapped to the middle", [("< v  -> recurse", 3.6, "#c6e0b4"),
                                                     ("= v  DONE", 2.8, "#ffe699"),
                                                     ("> v  -> recurse/loop", 3.6, "#f8cbad")])]
    for row, (label, parts) in enumerate(stages):
        x, y = 0, -row * 1.6
        for text, w, color in parts:
            ax1.add_patch(Rectangle((x, y), w, 0.9, fc=color, ec="#1f3864"))
            ax1.text(x + w / 2, y + 0.45, text, ha="center", va="center", fontsize=8.5)
            x += w
        ax1.text(-0.2, y + 0.45, label, ha="right", va="center", fontsize=9)
    ax1.annotate("", xy=(3.8, 0.95), xytext=(3.8, 1.5), arrowprops=dict(arrowstyle="->"))
    ax1.text(3.8, 1.55, "left pointer pb (A's Hoare scan)", ha="center", fontsize=8)
    ax1.annotate("", xy=(6.2, 0.95), xytext=(6.2, 1.5), arrowprops=dict(arrowstyle="->"))
    ax1.text(7.0, 1.55, "right pointer pc", ha="center", fontsize=8)
    ax1.set_xlim(-4.6, 10.4)
    ax1.set_ylim(-3.6, 2.1)
    ax1.axis("off")
    ax1.set_title("Divide: fat partition around v = median of three\n(keys equal to v are finished: B's 3-way idea)",
                  fontsize=10)
    # right: control flow of one call
    boxes = [(0.5, 4.6, "sort(lo, hi, budget)", "#eef3fb"),
             (0.5, 3.6, "size <= 16 ?  -> insertion sort (B)", "#e2efda"),
             (0.5, 2.6, "budget = 0 ?  -> heapsort (joint guard)", "#fde9d9"),
             (0.5, 1.6, "v = median of three (A);  fat partition", "#eef3fb"),
             (0.5, 0.6, "recurse on smaller part (A), loop on larger", "#eef3fb")]
    for x, y, text, color in boxes:
        ax2.add_patch(FancyBboxPatch((x, y), 9, 0.7, boxstyle="round,pad=0.08", fc=color, ec="#1f3864"))
        ax2.text(x + 4.5, y + 0.35, text, ha="center", va="center", fontsize=9)
    for y in (4.6, 3.6, 2.6, 1.6):
        ax2.annotate("", xy=(5, y - 0.28), xytext=(5, y - 0.02), arrowprops=dict(arrowstyle="->"))
    ax2.annotate("", xy=(9.7, 4.95), xytext=(9.7, 0.95),
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.5", color="#555555"))
    ax2.text(10.9, 2.9, "loop:\nbudget - 1\nper level", fontsize=8, ha="left")
    ax2.set_xlim(0, 12.2)
    ax2.set_ylim(0.2, 5.6)
    ax2.axis("off")
    ax2.set_title("Conquer / combine: one call of the joint design\n(budget = 2 floor(log2 n) partition levels)",
                  fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q7_design_diagram.png"), dpi=150)
    plt.close(fig)


def fig_ratio(rows):
    n = 8000
    fig, ax = plt.subplots(figsize=(13, 5))
    width = 0.16
    for k, v in enumerate(VARIANTS):
        vals = [get(rows, v, d, n, "comparisons_per_nlog2n") for d in DATASETS]
        ax.bar([i + (k - 2) * width for i in range(len(DATASETS))], vals, width, color=COLORS[v], label=v)
    ax.axhline(1.5, color="black", ls="--", lw=1, label="objective O1: 1.5 (natural inputs)")
    ax.axhline(6, color="black", ls=":", lw=1.2, label="objective O2: 6 (adversarial inputs)")
    ax.set_yscale("log")
    ax.set_xticks(range(len(DATASETS)))
    ax.set_xticklabels(DATASETS)
    ax.set_xlabel("dataset (identical for every variant)")
    ax.set_ylabel("comparisons / (n log2 n)  (log scale)")
    ax.set_title("Comparisons per n log2 n at n = 8,000: only the joint design stays within both objectives on every dataset")
    ax.grid(True, axis="y", which="both", alpha=0.3)
    ax.legend(fontsize=8, ncol=4, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q7_ratio_n8000.png"), dpi=150)
    plt.close(fig)


def fig_growth(rows):
    sizes = sorted({int(r["n"]) for r in rows})
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    for ax, d in zip(axes.flat, DATASETS):
        for v in VARIANTS:
            ax.loglog(sizes, [get(rows, v, d, s, "comparisons") for s in sizes], MARKS[v] + "-", color=COLORS[v],
                      label=v, ms=5)
        ax.loglog(sizes, [s * math.log2(s) for s in sizes], "k--", lw=1, label="n log2 n")
        ax.loglog(sizes, [s * (s - 1) / 2 for s in sizes], "k:", lw=1.2, label="n(n-1)/2")
        ax.set_title(d)
        ax.set_xlabel("orders n")
        ax.set_ylabel("comparisons")
        ax.grid(True, which="both", alpha=0.3)
    axes.flat[0].legend(fontsize=7)
    fig.suptitle("Growth of the comparisons on each dataset (log-log): slope 2 = quadratic, slope ~1 = n log n",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q7_growth.png"), dpi=150)
    plt.close(fig)


def fig_guard_seed():
    guard, seed = read("q7_guard.csv"), read("q7_seed.csv")
    n = [int(r["n"]) for r in guard]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))
    ax1.loglog(n, [int(r["unguarded_comparisons"]) for r in guard], "s-", color="#d62728", label="joint WITHOUT guard")
    ax1.loglog(n, [int(r["guarded_comparisons"]) for r in guard], "D-", color="#ff7f0e", label="joint WITH guard")
    ax1.loglog(n, [x * x / 4 for x in n], "k:", lw=1.2, label="n^2/4")
    ax1.loglog(n, [6 * x * math.log2(x) for x in n], "k--", lw=1, label="6 n log2 n (objective O2)")
    ax1.set_title("killer-J: the depth budget turns n^2/4 into O(n log n)")
    ax1.set_xlabel("orders n")
    ax1.set_ylabel("comparisons")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)
    ns = [int(r["n"]) for r in seed]
    ax2.loglog(ns, [int(r["B_seed42_comparisons"]) for r in seed], "^-", color="#2ca02c",
               label="B, seed 42 (known to the attacker)")
    ax2.loglog(ns, [int(r["B_seed7_comparisons"]) for r in seed], "^--", color="#2ca02c", mfc="none",
               label="B, seed 7 (unknown)")
    ax2.loglog(ns, [x * x / 2 for x in ns], "k:", lw=1.2, label="n^2/2")
    ax2.loglog(ns, [x * math.log2(x) for x in ns], "k--", lw=1, label="n log2 n")
    ax2.set_title("killer-B: a random pivot protects only with a secret seed")
    ax2.set_xlabel("orders n")
    ax2.set_ylabel("comparisons")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q7_guard_seed.png"), dpi=150)
    plt.close(fig)


def fig_depth_moves(rows):
    n = 8000
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 4.8))
    width = 0.16
    for k, v in enumerate(VARIANTS):
        xs = [i + (k - 2) * width for i in range(len(DATASETS))]
        ax1.bar(xs, [max(get(rows, v, d, n, "max_depth"), 1) for d in DATASETS], width, color=COLORS[v], label=v)
        ax2.bar(xs, [max(get(rows, v, d, n, "moves"), 1) for d in DATASETS], width, color=COLORS[v], label=v)
    ax1.axhline(math.log2(n), color="black", ls="--", lw=1, label="log2 n = 13 (objective O3)")
    for ax, title, ylabel in ((ax1, "Maximum recursion depth, n = 8,000", "depth (log scale)"),
                              (ax2, "Moves (element writes), n = 8,000", "moves (log scale; 0 drawn as 1)")):
        ax.set_yscale("log")
        ax.set_xticks(range(len(DATASETS)))
        ax.set_xticklabels(DATASETS, rotation=20)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.grid(True, axis="y", which="both", alpha=0.3)
    ax1.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q7_depth_moves.png"), dpi=150)
    plt.close(fig)


def main():
    rows = read("q7_results.csv")
    fig_design()
    fig_ratio(rows)
    fig_growth(rows)
    fig_guard_seed()
    fig_depth_moves(rows)
    print("Q7 graphs written to", RESULTS)


if __name__ == "__main__":
    main()
