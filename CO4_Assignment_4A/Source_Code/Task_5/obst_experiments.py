"""
Task 5 - experiments: cost of building the optimal BST, Levitin's Theta(n^3) algorithm vs Knuth's Theta(n^2).

Random access counts (seed 42) for n = 25, 50, 100, 200, 400 keys: root candidates examined (Levitin's count is
exactly n(n-1)(n+4)/6), Knuth's candidates, times (median of 3), and the average lookup cost of the optimal tree
vs the balanced (median-root) BST and the greedy (most-probable-root) BST on skewed (Zipf-like) frequencies.
Outputs: results/obst_growth.csv, ../../Report/Screenshots/task5_obst_growth.png
Run:  py -3 obst_experiments.py
"""
import csv
import os
import random
import statistics
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from optimal_bst import balanced_depths, greedy_depths, optimal_bst, optimal_bst_knuth, tree_cost  # noqa: E402

sys.setrecursionlimit(10_000)
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.normpath(os.path.join(HERE, "..", "..", "Report", "Screenshots"))


def zipf_counts(n, rng):
    """Skewed access counts: the r-th most popular key gets ~1000/r lookups; popularity order is random."""
    counts = [max(1, round(1000 / r)) for r in range(1, n + 1)]
    rng.shuffle(counts)
    return counts


def median_time(fn, p, repeats=3):
    times, res = [], None
    for _ in range(repeats):
        t0 = time.perf_counter()
        res = fn(p)
        times.append(time.perf_counter() - t0)
    return statistics.median(times), res


def main():
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    rng = random.Random(42)
    rows = []
    print("=" * 112)
    print(" TASK 5 - EXPERIMENTS: OPTIMAL BST CONSTRUCTION, n = 25 ... 400 keys (Zipf-like access counts, seed 42)")
    print("=" * 112)
    hdr = (f"  {'n':>4}{'Levitin cand.':>15}{'n(n-1)(n+4)/6':>15}{'Knuth cand.':>13}{'Knuth/n^2':>11}"
           f"{'Levitin s':>11}{'Knuth s':>9}{'same C?':>9}{'opt cost':>10}{'balanced':>10}{'greedy':>8}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for n in (25, 50, 100, 200, 400):
        p = zipf_counts(n, rng)
        tl, (C, R, ol) = median_time(optimal_bst, p)
        tk, (Ck, Rk, ok) = median_time(optimal_bst_knuth, p)
        total = sum(p)
        opt = C[1][n] / total
        bal = tree_cost(balanced_depths(1, n), p) / total
        gre = tree_cost(greedy_depths(p, 1, n), p) / total
        formula = n * (n - 1) * (n + 4) // 6
        rows.append({"n": n, "levitin_candidates": ol["candidates"], "formula": formula,
                     "knuth_candidates": ok["candidates"], "levitin_s": tl, "knuth_s": tk,
                     "opt_cost": opt, "balanced_cost": bal, "greedy_cost": gre})
        print(f"  {n:>4}{ol['candidates']:>15}{formula:>15}{ok['candidates']:>13}{ok['candidates'] / n ** 2:>11.2f}"
              f"{tl:>11.4f}{tk:>9.4f}{'yes' if C[1][n] == Ck[1][n] else 'NO':>9}{opt:>10.3f}{bal:>10.3f}{gre:>8.3f}")
    gl = rows[-1]["levitin_s"] / rows[-2]["levitin_s"]
    gk = rows[-1]["knuth_s"] / rows[-2]["knuth_s"]
    print(f"\n  last doubling of n: Levitin time x{gl:.1f} (Theta(n^3) -> x8), Knuth time x{gk:.1f} (Theta(n^2) -> x4)")
    print(f"  optimal tree saves {100 * (1 - rows[-1]['opt_cost'] / rows[-1]['balanced_cost']):.1f}% of the comparisons"
          f" of the balanced BST at n = {rows[-1]['n']}")
    path = os.path.join(RESULTS, "obst_growth.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    ns = [r["n"] for r in rows]
    ax1.loglog(ns, [r["levitin_candidates"] for r in rows], "o-", label="Levitin: candidates examined")
    ax1.loglog(ns, [n ** 3 / 6 for n in ns], "k:", label="n^3 / 6")
    ax1.loglog(ns, [r["knuth_candidates"] for r in rows], "s-", label="Knuth: candidates examined")
    ax1.loglog(ns, [n ** 2 for n in ns], "k--", label="n^2")
    ax1.set_title("Optimal BST: root candidates examined")
    ax1.set_xlabel("number of keys n (log scale)")
    ax1.set_ylabel("candidates (log scale)")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.plot(ns, [r["opt_cost"] for r in rows], "o-", label="optimal BST (DP)")
    ax2.plot(ns, [r["greedy_cost"] for r in rows], "^-", label="greedy: most probable key as root")
    ax2.plot(ns, [r["balanced_cost"] for r in rows], "s-", label="balanced BST (median root)")
    ax2.set_xscale("log")
    ax2.set_title("Average comparisons per lookup (Zipf-like access)")
    ax2.set_xlabel("number of keys n (log scale)")
    ax2.set_ylabel("average comparisons per lookup")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    gpath = os.path.join(SHOTS, "task5_obst_growth.png")
    fig.savefig(gpath, dpi=150)
    plt.close(fig)
    print("Saved:", os.path.relpath(path, HERE), "  Graph:", os.path.relpath(gpath, HERE))


if __name__ == "__main__":
    main()
