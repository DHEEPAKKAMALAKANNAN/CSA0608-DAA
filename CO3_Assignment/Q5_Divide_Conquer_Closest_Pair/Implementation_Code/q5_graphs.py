"""Q5 - Graphs and decomposition diagram for the closest-pair experiments (CSA06 DAA, Assignment 3 - CO3).

Reads results/q5_scaling.csv and results/q5_strip_histogram.csv (written by q5_experiments.py) and writes:
  results/q5_operations.png      distance computations and presort+merge comparisons against theory (log-log)
  results/q5_time.png            running time against n with the 1-second update cycle
  results/q5_strip_histogram.png neighbours examined per strip point at n = 20,000 (bound 7)
  results/q5_decomposition.png   geometric decomposition of 32 drones + recursion tree of sub-problem sizes
Run:  py -3 q5_graphs.py
"""
import csv
import math
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from q5_closest_pair import closest_pair_dc  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
COLORS = {"uniform": "#1f77b4", "clustered": "#ff7f0e", "line": "#2ca02c", "duplicate": "#9467bd"}
MARKERS = {"uniform": "o", "clustered": "s", "line": "^", "duplicate": "D"}


def load(name):
    with open(os.path.join(RES, name), newline="") as f:
        return list(csv.DictReader(f))


def operations_figure(rows):
    """Distance computations (left) and presort + merge comparisons (right) with theoretical overlays."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
    ns = sorted({int(r["n"]) for r in rows})
    ax1.plot(ns, [n * (n - 1) / 2 for n in ns], "k--", lw=1.5, label="brute force: n(n−1)/2 (exact count)")
    for d in COLORS:
        rr = [r for r in rows if r["distribution"] == d]
        ax1.plot([int(r["n"]) for r in rr], [int(r["dc_distances"]) for r in rr], marker=MARKERS[d],
                 color=COLORS[d], label=f"D&C – {d}")
    ax1.plot(ns, [7 * n * math.log2(n) for n in ns], ":", color="grey", lw=1.5, label="upper bound 7·n·log₂ n")
    ax1.plot(ns, [1.5 * n for n in ns], "-.", color="black", lw=1, label="linear reference 1.5·n")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlabel("number of drones n")
    ax1.set_ylabel("distance computations")
    ax1.set_title("Distance computations: brute force vs Divide-and-Conquer")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)

    uni = [r for r in rows if r["distribution"] == "uniform"]
    c = sum(int(r["dc_sort_comparisons"]) + int(r["dc_merge_comparisons"]) for r in uni) / \
        sum(int(r["n_log2_n"]) for r in uni)
    for d in COLORS:
        rr = [r for r in rows if r["distribution"] == d]
        ax2.plot([int(r["n"]) for r in rr],
                 [int(r["dc_sort_comparisons"]) + int(r["dc_merge_comparisons"]) for r in rr],
                 marker=MARKERS[d], color=COLORS[d], label=f"D&C – {d}")
    ax2.plot(ns, [c * n * math.log2(n) for n in ns], "k--", lw=1.5, label=f"theory {c:.2f}·n·log₂ n (fitted)")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("number of drones n")
    ax2.set_ylabel("key comparisons (presort by x + merges by y)")
    ax2.set_title("Sorting/merging work of D&C grows as n log n")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "q5_operations.png"), dpi=150)
    plt.close(fig)


def time_figure(rows):
    """Measured times (and extrapolated brute-force times) against n, with the 1-second update cycle."""
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for d in ("uniform", "clustered"):
        rr = [r for r in rows if r["distribution"] == d]
        meas = [r for r in rr if r["bf_time_status"] == "measured"]
        ext = [r for r in rr if r["bf_time_status"] != "measured"]
        ax.plot([int(r["n"]) for r in meas], [float(r["bf_time_s"]) for r in meas], marker=MARKERS[d],
                color=COLORS[d], ls="-", label=f"brute force – {d} (measured)")
        ax.plot([int(r["n"]) for r in ext], [float(r["bf_time_s"]) for r in ext], marker=MARKERS[d],
                color=COLORS[d], ls=":", mfc="none", label=f"brute force – {d} (extrapolated)")
    for d in COLORS:
        rr = [r for r in rows if r["distribution"] == d]
        ax.plot([int(r["n"]) for r in rr], [float(r["dc_time_s"]) for r in rr], marker=MARKERS[d], color=COLORS[d],
                ls="--", label=f"D&C – {d}")
    uni = [r for r in rows if r["distribution"] == "uniform"]
    k = float(uni[-1]["dc_time_s"]) / (int(uni[-1]["n"]) * math.log2(int(uni[-1]["n"])))
    ns = [int(r["n"]) for r in uni]
    ax.plot(ns, [k * n * math.log2(n) for n in ns], color="black", lw=1, ls="-.", label="c·n·log₂ n (scaled)")
    ax.axhline(1.0, color="red", lw=1.5, label="1-second update cycle")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("number of drones n")
    ax.set_ylabel("time per update (s)")
    ax.set_title("Running time: only Divide-and-Conquer meets the 1 s cycle at 20,000+ drones")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=7.5, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "q5_time.png"), dpi=150)
    plt.close(fig)


def histogram_figure(hist):
    """How many strip points examined 0, 1, ..., 7 (and > 7) neighbours, for each distribution at n = 20,000."""
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    labels = [h["neighbours_examined"] for h in hist if h["distribution"] == "uniform"]
    width = 0.2
    for i, d in enumerate(COLORS):
        vals = [int(h["strip_points"]) for h in hist if h["distribution"] == d]
        ax.bar([x + (i - 1.5) * width for x in range(len(labels))], vals, width, color=COLORS[d], label=d)
    ax.axvline(7.5, color="red", ls="--", lw=1.5, label="packing bound: at most 7 neighbours")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yscale("symlog", linthresh=1)
    ax.set_xlabel("neighbours examined by one strip point (dy < δ)")
    ax.set_ylabel("number of strip points (symlog)")
    seen = max(i for i, lab in enumerate(labels) if any(int(h["strip_points"]) > 0 for h in hist
                                                         if h["neighbours_examined"] == lab))
    ax.set_title(f"Strip work at n = 20,000: no strip point examined more than {seen} neighbours (bound 7)")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "q5_strip_histogram.png"), dpi=150)
    plt.close(fig)


def collect_splits(px, depth, out):
    """Record (mid_x, depth) of every dividing line the recursion draws (base case: <= 3 points)."""
    if len(px) <= 3:
        return
    mid = len(px) // 2
    out.append((px[mid][0], depth))
    collect_splits(px[:mid], depth + 1, out)
    collect_splits(px[mid:], depth + 1, out)


def decomposition_figure():
    """Left: 32 drones with the dividing lines of every level and the top-level strip. Right: recursion tree."""
    rng = random.Random(7)
    pts = [(rng.uniform(0, 20), rng.uniform(0, 20)) for _ in range(32)]
    px = sorted(pts)
    splits = []
    collect_splits(px, 0, splits)
    d, pair, _ = closest_pair_dc(pts)
    # top-level delta = min of the two halves' answers
    dl, _, _ = closest_pair_dc(px[:16])
    dr, _, _ = closest_pair_dc(px[16:])
    delta, mid_x = min(dl, dr), px[16][0]

    fig, (ax, at) = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={"width_ratios": [1, 1.25]})
    ax.axvspan(mid_x - delta, mid_x + delta, color="gold", alpha=0.35, label=f"top-level strip |x − mid| < δ = {delta:.2f} km")
    styles = {0: ("red", 2.4), 1: ("darkorange", 1.6), 2: ("green", 1.1), 3: ("grey", 0.8)}
    used = set()
    for x, dep in splits:
        col, lw = styles.get(dep, ("grey", 0.6))
        ax.axvline(x, color=col, lw=lw, ls="-" if dep == 0 else "--",
                   label=(f"dividing line, level {dep}" if dep not in used else None))
        used.add(dep)
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=28, color="#1f77b4", zorder=3, label="drone")
    ax.plot([pair[0][0], pair[1][0]], [pair[0][1], pair[1][1]], color="crimson", lw=2.5, zorder=4,
            label=f"closest pair, {d:.2f} km")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    ax.set_xlabel("x (km)")
    ax.set_ylabel("y (km)")
    ax.set_title("Divide: split by x at every level; Combine: only the strip")
    ax.legend(fontsize=7.5, loc="upper left", framealpha=0.9)
    ax.grid(alpha=0.2)

    # recursion tree of sub-problem sizes for n = 32 (base case n <= 3)
    at.set_xlim(0, 1)
    at.set_ylim(-0.6, 4.8)
    at.axis("off")
    levels = [[32]]
    while levels[-1][0] > 3:
        levels.append([s // 2 for s in levels[-1] for _ in (0, 1)])
    pos = {}
    tree_w = 0.66                                     # tree on the left, level costs on the right
    for lv, sizes in enumerate(levels):
        k = len(sizes)
        for i, s in enumerate(sizes):
            x, y = tree_w * (i + 0.5) / k, 4.3 - lv
            pos[(lv, i)] = (x, y)
            at.text(x, y, f"{s}", ha="center", va="center", fontsize=9 if k <= 8 else 6.5,
                    bbox=dict(boxstyle="round,pad=0.2", fc="#dce6f2" if s > 3 else "#e8f5e9", ec="#1f3864"))
            if lv > 0:
                px_, py_ = pos[(lv - 1, i // 2)]
                at.plot([px_, x], [py_ - 0.17, y + 0.17], color="#1f3864", lw=0.7)
        txt = (f"level {lv}: {k} × combine on {sizes[0]} pts\n(merge-by-y + strip) = Θ(n)" if lv < len(levels) - 1
               else f"level {lv}: {k} base cases\n× 1 distance = Θ(n)")
        at.text(tree_w + 0.03, 4.3 - lv, txt, ha="left", va="center", fontsize=8.5, color="#7f0000")
    at.text(0.5, -0.45, "log₂ n levels × Θ(n) per level  ⇒  T(n) = 2T(n/2) + Θ(n) = Θ(n log n)",
            ha="center", fontsize=10, weight="bold")
    at.set_title("Recursion tree of sub-problem sizes (n = 32)")
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "q5_decomposition.png"), dpi=150)
    plt.close(fig)


def main():
    rows = load("q5_scaling.csv")
    hist = load("q5_strip_histogram.csv")
    operations_figure(rows)
    time_figure(rows)
    histogram_figure(hist)
    decomposition_figure()
    for f in ("q5_operations.png", "q5_time.png", "q5_strip_histogram.png", "q5_decomposition.png"):
        print("wrote results/" + f)


if __name__ == "__main__":
    main()
