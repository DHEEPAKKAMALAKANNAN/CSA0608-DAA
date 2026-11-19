"""Q6 - Graphs and decomposition diagrams for Median of Medians and Meet-in-the-Middle (CSA06 DAA, Assignment 3 - CO3).

Reads the CSVs written by q6_median_of_medians.py and q6_meet_in_the_middle.py and writes:
  ../Median_of_Medians/results/q6_mom_comparisons.png    comparisons per element and time against n (random input)
  ../Median_of_Medians/results/q6_mom_inputs.png         input sensitivity at n = 10^6 and the first-pivot worst case
  ../Median_of_Medians/results/q6_mom_decomposition.png  groups-of-5 diagram + recursion tree of sizes
  ../Meet_in_the_Middle/results/q6_mitm_growth.png       operations and time against n with the 2-second limit
  ../Meet_in_the_Middle/results/q6_mitm_decomposition.png  split into halves, sorted sum lists, matching
  ../Median_of_Medians/results/q6_pivot_quality.png      distribution over 300 runs + kept fraction per round
  ../Meet_in_the_Middle/results/q6_mitm_memory.png       peak memory against n + time-memory trade-off (n = 26)
Run:  py -3 q6_graphs.py
"""
import csv
import math
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

from q6_meet_in_the_middle import sorted_subset_sums, PackCounter, predicted_mitm_ops  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MOM = os.path.join(os.path.dirname(HERE), "Median_of_Medians", "results")
MITM = os.path.join(os.path.dirname(HERE), "Meet_in_the_Middle", "results")
MCOL = {"sort_then_pick": "#d62728", "qs_random_mean": "#1f77b4", "qs_random_max": "#7fb3e0", "mom_g3": "#2ca02c",
        "mom_g5": "#ff7f0e", "mom_g7": "#9467bd"}
MLAB = {"sort_then_pick": "sort-then-pick (merge sort)", "qs_random_mean": "randomised Quickselect (mean of 5)",
        "qs_random_max": "randomised Quickselect (max of 5)", "mom_g3": "Median of Medians, g = 3",
        "mom_g5": "Median of Medians, g = 5", "mom_g7": "Median of Medians, g = 7"}


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# ----------------------------------------------------------------------------------------------- (a) graphs
def mom_comparisons_figure(rows):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
    rnd = [r for r in rows if r["input"] == "random"]
    ns = sorted({int(r["n"]) for r in rnd})
    for m in MCOL:
        rr = [r for r in rnd if r["method"] == m]
        ax1.plot([int(r["n"]) for r in rr], [float(r["comparisons_per_n"]) for r in rr], marker="o", color=MCOL[m],
                 label=MLAB[m], ls=":" if m == "qs_random_max" else "-")
    ax1.plot(ns, [math.log2(n) - 1.25 for n in ns], "k--", lw=1.2, label="theory for merge sort: log₂ n − 1.25")
    ax1.set_xscale("log")
    ax1.set_xlabel("batch size n (deliveries)")
    ax1.set_ylabel("element comparisons / n")
    ax1.set_title("Comparisons per element (random input): flat = linear time")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=7.5)
    for m in ("sort_then_pick", "qs_random_mean", "mom_g5"):
        rr = [r for r in rnd if r["method"] == m]
        ax2.plot([int(r["n"]) for r in rr], [float(r["time_s"]) for r in rr], marker="o", color=MCOL[m], label=MLAB[m])
    g5 = [r for r in rnd if r["method"] == "mom_g5"][-1]
    k = float(g5["time_s"]) / int(g5["n"])
    ax2.plot(ns, [k * n for n in ns], "k--", lw=1, label="c·n (scaled to MoM at 10⁶)")
    st = [r for r in rnd if r["method"] == "sort_then_pick"][-1]
    k2 = float(st["time_s"]) / (int(st["n"]) * math.log2(int(st["n"])))
    ax2.plot(ns, [k2 * n * math.log2(n) for n in ns], "r:", lw=1, label="c·n·log₂ n (scaled to sort at 10⁶)")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("batch size n (deliveries)")
    ax2.set_ylabel("time (s)")
    ax2.set_title("Running time (random input)")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=7.5)
    fig.tight_layout()
    fig.savefig(os.path.join(MOM, "q6_mom_comparisons.png"), dpi=150)
    plt.close(fig)


def mom_inputs_figure(rows, worst):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    inputs = ["random", "sorted", "duplicates"]
    big = max(int(r["n"]) for r in rows)
    width = 0.13
    for i, m in enumerate(MCOL):
        vals = [float(next(r["comparisons_per_n"] for r in rows if r["input"] == inp and int(r["n"]) == big
                           and r["method"] == m)) for inp in inputs]
        ax1.bar([x + (i - 2.5) * width for x in range(3)], vals, width, color=MCOL[m], label=MLAB[m])
    ax1.set_xticks(range(3))
    ax1.set_xticklabels(inputs)
    ax1.set_ylabel("element comparisons / n")
    ax1.set_title(f"Input sensitivity at n = {big:,}")
    ax1.grid(True, axis="y", alpha=0.3)
    ax1.legend(fontsize=7)
    ns = [int(r["n"]) for r in worst]
    ax2.plot(ns, [int(r["qs_first_comparisons"]) for r in worst], "o-", color="#8c564b",
             label="first-element pivot Quickselect (measured)")
    ax2.plot(ns, [int(r["formula"]) for r in worst], "k--", label="theory 2(k+1)n − k(k+1) ≈ 3n²/4")
    ax2.plot(ns, [int(r["mom_g5_comparisons"]) for r in worst], "s-", color=MCOL["mom_g5"],
             label="Median of Medians g = 5 (measured)")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("batch size n (sorted, distinct delivery times)")
    ax2.set_ylabel("element comparisons")
    ax2.set_title("A deterministic pivot rule without a guarantee: Θ(n²)")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(MOM, "q6_mom_inputs.png"), dpi=150)
    plt.close(fig)


def mom_decomposition_figure():
    rng = random.Random(5)
    vals = rng.sample(range(10, 100), 35)
    groups = [sorted(vals[i:i + 5]) for i in range(0, 35, 5)]
    groups.sort(key=lambda g: g[2])                       # drawn in order of their medians
    pivot = groups[3][2]
    fig, (ax, at) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1, 1.2]})
    ax.add_patch(Rectangle((-0.45, -0.45), 3.9, 2.9, color="#cfe2f3", zorder=0))
    ax.add_patch(Rectangle((2.55, 1.55), 3.9, 2.9, color="#fde2c8", zorder=0))
    for c, g in enumerate(groups):
        for r, v in enumerate(g):
            is_med, is_piv = r == 2, (c == 3 and r == 2)
            ax.scatter(c, r, s=900, color="crimson" if is_piv else ("#ffd966" if is_med else "white"),
                       edgecolors="black", zorder=2)
            ax.text(c, r, str(v), ha="center", va="center", fontsize=10, zorder=3,
                    color="white" if is_piv else "black", weight="bold" if is_med else None)
    ax.text(1.5, -0.85, "≤ pivot: 3 elements in each of at least ⌈⌈n/5⌉/2⌉ − 2 groups ⇒ ≥ 3n/10 − 6", ha="center",
            fontsize=9, color="#1f4e79")
    ax.text(4.5, 4.75, "≥ pivot: likewise ≥ 3n/10 − 6 elements", ha="center", fontsize=9, color="#a0522d")
    ax.set_xlim(-0.8, 6.8)
    ax.set_ylim(-1.2, 5.1)
    ax.set_xticks(range(7))
    ax.set_xticklabels([f"G{c + 1}" for c in range(7)])
    ax.set_yticks(range(5))
    ax.set_yticklabels(["smallest", "", "median", "", "largest"])
    ax.set_title(f"n = 35 delivery times in 7 sorted groups of 5 (yellow = group medians, red = pivot {pivot})",
                 fontsize=10)
    ax.set_xlabel("groups drawn in order of their medians (the algorithm does NOT sort them)")

    at.axis("off")
    at.set_xlim(0, 1)
    at.set_ylim(-0.3, 3.6)
    nodes = {0: [(0.5, "n", 1.0)], 1: [(0.25, "n/5", 0.2), (0.75, "7n/10", 0.7)],
             2: [(0.1, "n/25", 0.04), (0.32, "7n/50", 0.14), (0.62, "7n/50", 0.14), (0.88, "49n/100", 0.49)]}
    parent = {1: [0, 0], 2: [0, 0, 1, 1]}
    for lv, lst in nodes.items():
        y = 3.2 - 1.2 * lv
        for i, (x, lab, _) in enumerate(lst):
            at.text(x, y, lab, ha="center", va="center", fontsize=11,
                    bbox=dict(boxstyle="round,pad=0.3", fc="#dce6f2", ec="#1f3864"))
            if lv > 0:
                px = nodes[lv - 1][parent[lv][i]][0]
                at.plot([px, x], [y + 1.2 - 0.18, y + 0.18], color="#1f3864", lw=0.8)
        total = sum(f for _, _, f in lst)
        at.text(1.02, y, f"level sum {total:.2f}·cn", ha="left", va="center", fontsize=10, color="#7f0000")
    at.text(0.5, 0.35, "…  level i: (9/10)ⁱ·cn  (since 1/5 + 7/10 = 9/10 < 1)", ha="center", fontsize=10)
    at.text(0.5, -0.15, "T(n) ≤ cn·Σ (9/10)ⁱ = 10cn = Θ(n);   with g = 3: 1/3 + 2/3 = 1 ⇒ every level costs cn ⇒ Θ(n log n)",
            ha="center", fontsize=9.5, weight="bold")
    at.set_title("Recursion tree: T(n) ≤ T(n/5) + T(7n/10 + 6) + cn")
    fig.tight_layout()
    fig.savefig(os.path.join(MOM, "q6_mom_decomposition.png"), dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------------------------- (b) graphs
def mitm_growth_figure(rows, limits):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
    styles = {"brute_force": ("#d62728", "o", "brute force"),
              "mitm_binary": ("#1f77b4", "s", "MITM + binary search"),
              "mitm_two_pointer": ("#2ca02c", "^", "MITM + two-pointer")}
    for m, (col, mk, lab) in styles.items():
        rr = [r for r in rows if r["method"] == m]
        ax1.plot([int(r["n"]) for r in rr], [int(r["total_ops"]) for r in rr], marker=mk, color=col,
                 label=f"{lab} (counted operations)")
    ns = list(range(12, 41))
    theory = {"brute_force": (lambda n: 2 ** n, "2ⁿ"), "mitm_binary": (lambda n: (n / 2) * 2 ** (n / 2), "(n/2)·2^(n/2)"),
              "mitm_two_pointer": (lambda n: 2 ** (n / 2), "2^(n/2)")}
    for m, (f, lab) in theory.items():                  # theory curves scaled to the largest measured run
        last = [r for r in rows if r["method"] == m][-1]
        c = int(last["total_ops"]) / f(int(last["n"]))
        ax1.plot(ns, [c * f(n) for n in ns], "--", color=styles[m][0], lw=1, label=f"theory {c:.2f}·{lab}")
    ax1.set_yscale("log", base=2)
    ax1.set_xlabel("number of parcels n")
    ax1.set_ylabel("operations (log₂ scale)")
    ax1.set_title("Search effort: 2ⁿ against n·2^(n/2) and 2^(n/2)")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=7.5)
    lim = {r["method"]: float(r["cost_per_op_ns"]) * 1e-9 for r in limits}
    for m, (col, mk, lab) in styles.items():
        rr = [r for r in rows if r["method"] == m]
        ax2.plot([int(r["n"]) for r in rr], [float(r["time_s"]) for r in rr], marker=mk, color=col,
                 label=f"{lab} (measured)")
        if m == "brute_force":
            ext = list(range(24, 41))
            ax2.plot(ext, [lim[m] * 2 ** n for n in ext], ":", color=col, label="brute force (extrapolated)")
        else:
            ext = list(range(40, 47))
            ax2.plot(ext, [lim[m] * predicted_mitm_ops(n, "binary" if m == "mitm_binary" else "two") for n in ext],
                     ":", color=col, label=f"{lab} (extrapolated)")
    ax2.axhline(2.0, color="black", lw=1.5, label="2-second decision limit")
    ax2.set_yscale("log")
    ax2.set_xlabel("number of parcels n")
    ax2.set_ylabel("time (s)")
    ax2.set_title("Running time and the 2-second limit")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=7.5)
    fig.tight_layout()
    fig.savefig(os.path.join(MITM, "q6_mitm_growth.png"), dpi=150)
    plt.close(fig)


def mitm_decomposition_figure():
    w = [1200, 2500, 800, 3100, 1700, 2200]
    W = 6000
    A, _ = sorted_subset_sums(w[:3], PackCounter())
    B, _ = sorted_subset_sums(w[3:], PackCounter())
    fig, (ax0, ax) = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={"width_ratios": [1, 1.25]})
    # left: generating half 1's sorted sums by merging
    ax0.axis("off")
    ax0.set_xlim(0, 1)
    ax0.set_ylim(-0.5, 4.2)
    ax0.set_title("CONQUER: sorted subset sums of half 1 by merging L and L + w")
    L = [0]
    ax0.text(0.02, 3.6, "start", fontsize=9, va="center")
    ax0.text(0.25, 3.6, str(L), fontsize=9.5, va="center", family="monospace",
             bbox=dict(boxstyle="round", fc="#e8f5e9"))
    for step, wt in enumerate(w[:3], start=1):
        plus = [s + wt for s in L]
        L = sorted(L + plus)
        y = 3.6 - 1.15 * step
        ax0.text(0.02, y + 0.3, f"+ w{step} = {wt}", fontsize=9, color="#7f0000")
        ax0.text(0.25, y + 0.3, f"L + w = {plus}", fontsize=8.5, family="monospace", color="#555555")
        ax0.text(0.25, y - 0.12, f"merge → {L}", fontsize=9, family="monospace",
                 bbox=dict(boxstyle="round", fc="#e8f5e9"))
    ax0.text(0.5, -0.4, "2^(n/2) sums, already sorted: no separate sort is needed", ha="center", fontsize=9.5,
             weight="bold")
    # right: matching
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(-1.2, len(A) + 1.6)
    ax.set_title(f"DIVIDE into halves; COMBINE: for each a ≤ W find the largest b ≤ W − a  (W = {W:,} g)")
    ax.text(0.2, len(A) + 0.9, f"half 1: {w[:3]}", ha="center", fontsize=9.5, weight="bold")
    ax.text(0.8, len(A) + 0.9, f"half 2: {w[3:]}", ha="center", fontsize=9.5, weight="bold")
    best = (-1, None, None)
    for i, a in enumerate(A):
        ya = len(A) - 1 - i
        ax.add_patch(FancyBboxPatch((0.12, ya - 0.3), 0.16, 0.6, boxstyle="round,pad=0.02", fc="#dce6f2", ec="#1f3864"))
        ax.text(0.2, ya, f"a = {a:,}", ha="center", va="center", fontsize=9)
        if a <= W:
            j = max(k for k, b in enumerate(B) if b <= W - a)
            if a + B[j] > best[0]:
                best = (a + B[j], i, j)
    for j, b in enumerate(B):
        yb = len(B) - 1 - j
        ax.add_patch(FancyBboxPatch((0.72, yb - 0.3), 0.16, 0.6, boxstyle="round,pad=0.02", fc="#fde2c8", ec="#a0522d"))
        ax.text(0.8, yb, f"b = {b:,}", ha="center", va="center", fontsize=9)
    for i, a in enumerate(A):
        if a <= W:
            j = max(k for k, b in enumerate(B) if b <= W - a)
            is_best = (i == best[1] and j == best[2])
            ax.annotate("", xy=(0.71, len(B) - 1 - j), xytext=(0.29, len(A) - 1 - i),
                        arrowprops=dict(arrowstyle="->", color="crimson" if is_best else "grey",
                                        lw=2.2 if is_best else 0.8))
    ax.text(0.5, -0.8, f"best load a + b = {A[best[1]]:,} + {B[best[2]]:,} = {best[0]:,} g "
                       f"(binary search: ≈ log₂ 2^(n/2) = n/2 probes per a)", ha="center", fontsize=9.5,
            weight="bold", color="crimson")
    fig.tight_layout()
    fig.savefig(os.path.join(MITM, "q6_mitm_decomposition.png"), dpi=150)
    plt.close(fig)


def pivot_quality_figure():
    """Histogram of comparisons/n over 300 runs and of the kept fraction per round (q6_pivot_quality.py data)."""
    runs = load(os.path.join(MOM, "q6_pivot_quality_runs.csv"))
    keeps = load(os.path.join(MOM, "q6_pivot_quality_keeps.csv"))
    srt = {r["method"]: r for r in load(os.path.join(MOM, "q6_pivot_quality_sorted.csv"))}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.0))
    bins = [x / 4 for x in range(8, 46)]
    for key, lab, col in (("qs_random_cpn", "randomised QuickSelect (300 seeds, one batch)", "#1f77b4"),
                          ("qs_first_shuffled_cpn", "first-element pivot (300 shuffled batches)", "#d62728"),
                          ("mom_g5_shuffled_cpn", "Median of Medians g = 5 (300 shuffled batches)", "#ff7f0e")):
        ax1.hist([float(r[key]) for r in runs], bins=bins, alpha=0.55, color=col, label=lab, edgecolor="white")
    ax1.set_xlabel("element comparisons / n  (n = 10,001, median)")
    ax1.set_ylabel("number of runs")
    first = float(srt["QuickSelect first pivot"]["comparisons_per_n"])
    ax1.set_title("Cost of one selection over 300 runs\n"
                  f"(first pivot on the SORTED batch: {first:,.0f} n - off the scale)")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=8.5)
    kb = [x / 20 for x in range(0, 21)]
    ax2.hist([float(r["kept_fraction"]) for r in keeps if r["method"] == "qs_random"], bins=kb, density=True,
             alpha=0.6, color="#1f77b4", label="randomised QuickSelect", edgecolor="white")
    ax2.hist([float(r["kept_fraction"]) for r in keeps if r["method"] == "mom_g5"], bins=kb, density=True,
             alpha=0.6, color="#ff7f0e", label="Median of Medians g = 5", edgecolor="white")
    ax2.axvline(0.7, color="black", ls="--", lw=1.2)
    ax2.text(0.71, ax2.get_ylim()[1] * 0.9, "MoM bound 7n/10 + 6", fontsize=9)
    ax2.axvspan(0.9, 1.0, color="red", alpha=0.08)
    ax2.text(0.905, ax2.get_ylim()[1] * 0.6, "poor\n(> 90 %)", fontsize=9, color="darkred")
    ax2.set_xlabel("fraction of the round kept for the next round (rounds with n >= 100)")
    ax2.set_ylabel("density")
    ax2.set_title("Partition quality per round")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(MOM, "q6_pivot_quality.png"), dpi=150)
    plt.close(fig)


def mitm_memory_figure():
    """Peak memory of MitM vs brute force against n, and the k / n - k trade-off at n = 26."""
    mem = load(os.path.join(MITM, "q6_mitm_memory.csv"))
    trade = load(os.path.join(MITM, "q6_mitm_tradeoff.csv"))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.0))
    mi = [r for r in mem if r["method"].startswith("MitM")]
    bf = [r for r in mem if r["method"].startswith("brute")]
    ax1.semilogy([int(r["n"]) for r in mi], [int(r["peak_bytes"]) / 1024 for r in mi], "o-", color="#2ca02c",
                 label="Meet-in-the-Middle (measured peak)")
    ax1.semilogy([int(r["n"]) for r in bf], [max(int(r["peak_bytes"]), 1) / 1024 for r in bf], "s-",
                 color="#d62728", label="brute force (measured peak)")
    per = float(mi[-1]["bytes_per_stored_sum"])
    xs = list(range(16, 41, 2))
    ax1.semilogy(xs, [2 * 2 ** (n // 2) * per / 1024 for n in xs], "--", color="gray",
                 label=f"model 2·2^(n/2) sums × {per:.0f} B")
    ax1.set_xlabel("number of parcels n")
    ax1.set_ylabel("peak memory (KiB, log scale)")
    ax1.set_title("Extra memory of Meet-in-the-Middle")
    ax1.grid(alpha=0.3, which="both")
    ax1.legend(fontsize=8.5)
    one = [r for r in trade if r["variant"].startswith("store")]
    ks = [int(r["k"]) for r in one]
    ax2.semilogy(ks, [int(r["operations"]) for r in one], "o-", color="#1f77b4", label="operations (time)")
    ax2.semilogy(ks, [int(r["stored_sums"]) for r in one], "s-", color="#9467bd", label="stored sums (memory)")
    ax2.axvline(13, color="black", ls=":", lw=1)
    ax2.text(13.2, 3e2, "balanced k = n/2", fontsize=9)
    ax2.set_xlabel("k = parcels whose subset sums are stored (n = 26)")
    ax2.set_ylabel("count (log scale)")
    ax2.set_title("Time–memory trade-off at n = 26 (store 2^k, enumerate 2^(n−k))")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(MITM, "q6_mitm_memory.png"), dpi=150)
    plt.close(fig)


def main():
    pivot_quality_figure()
    mitm_memory_figure()
    rows = load(os.path.join(MOM, "q6_mom_comparisons.csv"))
    worst = load(os.path.join(MOM, "q6_mom_worstcase.csv"))
    mom_comparisons_figure(rows)
    mom_inputs_figure(rows, worst)
    mom_decomposition_figure()
    mrows = load(os.path.join(MITM, "q6_mitm_growth.csv"))
    limits = load(os.path.join(MITM, "q6_mitm_limits.csv"))
    mitm_growth_figure(mrows, limits)
    mitm_decomposition_figure()
    for f in ("Median_of_Medians/results/q6_mom_comparisons.png", "Median_of_Medians/results/q6_mom_inputs.png",
              "Median_of_Medians/results/q6_mom_decomposition.png", "Meet_in_the_Middle/results/q6_mitm_growth.png",
              "Meet_in_the_Middle/results/q6_mitm_decomposition.png", "Median_of_Medians/results/q6_pivot_quality.png",
              "Meet_in_the_Middle/results/q6_mitm_memory.png"):
        print("wrote ../" + f)


if __name__ == "__main__":
    main()
