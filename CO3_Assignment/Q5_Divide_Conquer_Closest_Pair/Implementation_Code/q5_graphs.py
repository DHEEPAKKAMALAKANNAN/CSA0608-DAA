"""Q5 - Graphs and decomposition diagram for the closest-pair experiments (CSA06 DAA, Assignment 3 - CO3).

Reads results/q5_scaling.csv and results/q5_strip_histogram.csv (written by q5_experiments.py) and writes:
  results/q5_operations.png      distance computations and presort+merge comparisons against theory (log-log)
  results/q5_time.png            running time against n with the 1-second update cycle
  results/q5_strip_histogram.png neighbours examined per strip point at n = 20,000 (bound 7)
  results/q5_decomposition.png   geometric decomposition of 32 drones + recursion tree of sub-problem sizes
  results/q5_crossover.png       small-n crossover: distances, total operations and time (from q5_crossover.csv)
  results/q5_strip_boundary.png  why the dividing line needs special treatment + the delta x 2delta packing box
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


def crossover_figure(rows):
    """Small-n crossover: operation counts (left) and median time (right), brute force vs D&C."""
    ns = [int(r["n"]) for r in rows]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.0))
    ax1.plot(ns, [float(r["bf_distances"]) for r in rows], "k-o", ms=4, label="brute force: n(n−1)/2 distances")
    ax1.plot(ns, [float(r["dc_distances"]) for r in rows], "-s", color="#1f77b4", ms=4, label="D&C: distances")
    ax1.plot(ns, [float(r["dc_total_ops"]) for r in rows], "--^", color="#ff7f0e", ms=4,
             label="D&C: distances + sort/merge comparisons")
    ax1.set_xscale("log", base=2)
    ax1.set_yscale("log")
    ax1.set_xlabel("number of drones n")
    ax1.set_ylabel("basic operations (mean of 5 fleets)")
    def first_below(kb, kd):
        """Smallest n from which D&C stays below brute force."""
        ans = None
        for r in reversed(rows):
            if float(r[kd]) < float(r[kb]):
                ans = int(r["n"])
            else:
                break
        return ans
    ax1.set_title(f"Operation counts: D&C cheaper from n = {first_below('bf_distances', 'dc_distances')} "
                  f"(distances), n = {first_below('bf_total_ops', 'dc_total_ops')} (total)")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.plot(ns, [float(r["bf_time_us"]) for r in rows], "k-o", ms=4, label="brute force")
    ax2.plot(ns, [float(r["dc_time_us"]) for r in rows], "-s", color="#1f77b4", ms=4, label="Divide-and-Conquer")
    cross = None
    for r in reversed(rows):
        if float(r["dc_time_us"]) < float(r["bf_time_us"]):
            cross = int(r["n"])
        else:
            break
    if cross:
        ax2.axvline(cross, color="red", ls="--", lw=1.2, label=f"time crossover ≈ n = {cross}")
    ax2.set_xscale("log", base=2)
    ax2.set_yscale("log")
    ax2.set_xlabel("number of drones n")
    ax2.set_ylabel("time per call (µs, median of 7 loops)")
    ax2.set_title("Measured time: overhead dominates below ≈ 64–96 drones")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "q5_crossover.png"), dpi=150)
    plt.close(fig)


def strip_boundary_figure():
    """Left: a pair that straddles the dividing line is closer than the best pair of either half.
    Right: the delta x 2delta box above a strip point holds at most 8 points -> at most 7 neighbours."""
    from matplotlib.patches import Rectangle
    fig, (ax, ab) = plt.subplots(1, 2, figsize=(13, 5.6))
    left = [(1.0, 1.0), (1.0, 4.0), (2.4, 6.5), (3.6, 2.6), (2.0, 8.5)]
    right = [(6.4, 1.2), (6.4, 4.5), (8.5, 7.0), (5.6, 8.2), (7.8, 3.0)]
    cross = [(4.55, 5.3), (5.25, 5.55)]          # one point on each side of x = 5
    lp, rp = left + [cross[0]], right + [cross[1]]
    mid, delta = 5.0, 2.1
    ax.axvspan(mid - delta, mid + delta, color="gold", alpha=0.3, label="strip |x − mid| < δ")
    ax.axvline(mid, color="red", lw=2.2, label="dividing line x = mid (median x)")
    ax.scatter(*zip(*lp), s=40, color="#1f77b4", zorder=3, label="left half")
    ax.scatter(*zip(*rp), s=40, color="#2ca02c", marker="s", zorder=3, label="right half")
    ax.plot([1.0, 1.0], [1.0, 4.0], color="#1f77b4", lw=2, ls=":")
    ax.text(0.6, 2.5, "δ_L", fontsize=10, color="#1f77b4")
    ax.plot([7.8, 6.4], [3.0, 1.2], color="#2ca02c", lw=2, ls=":")
    ax.text(7.25, 1.85, "δ_R", fontsize=10, color="#2ca02c")
    ax.plot(*zip(*cross), color="crimson", lw=3, zorder=4, label="true closest pair (crosses the line)")
    ax.annotate("found only by the\ncombine (strip) step", xy=(4.9, 5.45), xytext=(5.6, 9.3), fontsize=9,
                arrowprops=dict(arrowstyle="->", color="crimson"))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel("x (km)")
    ax.set_ylabel("y (km)")
    ax.set_title("Why the boundary needs special treatment")
    ax.legend(fontsize=7.5, loc="lower center", ncol=2, framealpha=0.95)
    ax.grid(alpha=0.2)

    d = 1.0
    ab.add_patch(Rectangle((-d, 0), 2 * d, d, fill=False, lw=2, ec="black"))
    for i in range(4):
        for j in range(2):
            ab.add_patch(Rectangle((-d + i * d / 2, j * d / 2), d / 2, d / 2, fill=True,
                                   fc="#dbe8f6" if i < 2 else "#d9ead3", ec="grey", lw=0.8, ls="--"))
    ab.plot([0, 0], [-0.04, 1.04], color="red", lw=2)
    pts = [(-0.98, 0.02), (-0.02, 0.0), (-0.98, 0.98), (-0.02, 0.98),
           (0.02, 0.04), (0.98, 0.03), (0.02, 0.97), (0.98, 0.98)]
    ab.scatter(*zip(*pts), s=45, color="#1f3864", zorder=3)
    ab.scatter([-0.02], [0.0], s=120, facecolor="none", edgecolor="crimson", lw=2, zorder=4)
    ab.text(-0.3, -0.12, "strip point p", color="crimson", fontsize=9)
    ab.text(-0.5, 1.08, "left δ × δ square:\n≤ 4 points (pairwise ≥ δ)", ha="center", fontsize=9)
    ab.text(0.5, 1.08, "right δ × δ square:\n≤ 4 points (pairwise ≥ δ)", ha="center", fontsize=9)
    ab.text(0, -0.32, "8 cells of size δ/2 × δ/2, diagonal δ/√2 < δ ⇒ at most one point per cell\n"
            "⇒ box above p holds ≤ 8 points ⇒ p is compared with at most 7 following strip points",
            ha="center", fontsize=9.5, weight="bold")
    ab.set_xlim(-1.4, 1.4)
    ab.set_ylim(-0.5, 1.4)
    ab.set_aspect("equal")
    ab.axis("off")
    ab.set_title("Packing argument: the δ × 2δ box above a strip point")
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "q5_strip_boundary.png"), dpi=150)
    plt.close(fig)


def main():
    rows = load("q5_scaling.csv")
    hist = load("q5_strip_histogram.csv")
    operations_figure(rows)
    time_figure(rows)
    histogram_figure(hist)
    decomposition_figure()
    crossover_figure(load("q5_crossover.csv"))
    strip_boundary_figure()
    for f in ("q5_operations.png", "q5_time.png", "q5_strip_histogram.png", "q5_decomposition.png",
              "q5_crossover.png", "q5_strip_boundary.png"):
        print("wrote results/" + f)


if __name__ == "__main__":
    main()
