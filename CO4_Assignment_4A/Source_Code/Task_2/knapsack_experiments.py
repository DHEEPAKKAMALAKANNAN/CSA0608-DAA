"""
Task 2 - experiments: cost of the 0/1 knapsack algorithms as n*W grows.

E1  n in {25, 50, 100, 200} x W in {500, 1000, 2000, 4000} (random parcels, seed 42): cells evaluated (= n*W),
    times of the bottom-up table, the single-row version and the memory function (median of 3), fraction of
    cells the memory function actually computes, and Python memory of the full table (tracemalloc peak).
E2  brute force (2^n subsets) vs bottom-up DP for n = 8..20, W = half the total weight.
Outputs: results/knapsack_E1.csv, results/knapsack_E2.csv, ../../Report/Screenshots/task2_knapsack_growth.png
Run:  py -3 knapsack_experiments.py
"""
import csv
import os
import random
import statistics
import time
import tracemalloc

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from knapsack_dp import (knapsack_bottom_up, knapsack_brute_force, knapsack_memory_function,  # noqa: E402
                         knapsack_one_row)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.normpath(os.path.join(HERE, "..", "..", "Report", "Screenshots"))


def random_instance(n, W, rng):
    """Weights spread so that about 40 % of the parcels fit; values weakly correlated with weights."""
    hi = max(2, 4 * W // n)
    weights = [rng.randint(max(1, W // n), hi) for _ in range(n)]
    values = [max(1, w + rng.randint(-w // 3, w // 3)) for w in weights]
    return weights, values


def median_time(fn, *args, repeats=3):
    times, res = [], None
    for _ in range(repeats):
        t0 = time.perf_counter()
        res = fn(*args)
        times.append(time.perf_counter() - t0)
    return statistics.median(times), res


def table_memory_mb(weights, values, W):
    tracemalloc.start()
    knapsack_bottom_up(weights, values, W)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return peak / 2**20


def experiment_1(rng):
    rows = []
    print("E1  time vs n*W (median of 3 runs); MF = memory function; mem = tracemalloc peak of the full table")
    hdr = (f"  {'n':>4}{'W':>6}{'n*W':>9}{'cells':>9}{'table s':>9}{'1-row s':>9}{'MF s':>8}{'MF cells':>10}"
           f"{'MF %':>6}{'ns/cell':>9}{'table MB':>10}{'equal?':>8}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for n in (25, 50, 100, 200):
        for W in (500, 1000, 2000, 4000):
            wts, vals = random_instance(n, W, rng)
            t2d, (F, o2d) = median_time(knapsack_bottom_up, wts, vals, W)
            t1d, (v1d, o1d) = median_time(knapsack_one_row, wts, vals, W)
            tmf, (vmf, _, omf) = median_time(knapsack_memory_function, wts, vals, W)
            mem = table_memory_mb(wts, vals, W)
            same = F[n][W] == v1d == vmf
            rows.append({"n": n, "W": W, "nW": n * W, "cells": o2d["cells"], "table_s": t2d, "one_row_s": t1d,
                         "mf_s": tmf, "mf_cells": omf["cells_computed"],
                         "mf_fraction": omf["cells_computed"] / (n * W), "table_MB": mem, "value": F[n][W]})
            print(f"  {n:>4}{W:>6}{n * W:>9}{o2d['cells']:>9}{t2d:>9.4f}{t1d:>9.4f}{tmf:>8.4f}"
                  f"{omf['cells_computed']:>10}{100 * omf['cells_computed'] / (n * W):>6.1f}"
                  f"{1e9 * t2d / (n * W):>9.1f}{mem:>10.2f}{'yes' if same else 'NO':>8}")
    return rows


def experiment_2(rng):
    rows = []
    print("\nE2  brute force (all 2^n subsets) vs bottom-up DP, W = half of the total weight")
    hdr = f"  {'n':>4}{'W':>6}{'2^n subsets':>13}{'brute s':>10}{'DP cells':>10}{'DP s':>10}{'same value?':>13}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for n in range(8, 21, 2):
        wts = [rng.randint(1, 30) for _ in range(n)]
        vals = [rng.randint(1, 40) for _ in range(n)]
        W = sum(wts) // 2
        tbf, (vbf, _, obf) = median_time(knapsack_brute_force, wts, vals, W, repeats=1)
        tdp, (F, odp) = median_time(knapsack_bottom_up, wts, vals, W)
        rows.append({"n": n, "W": W, "subsets": obf["subsets"], "brute_s": tbf, "dp_cells": odp["cells"],
                     "dp_s": tdp, "value": vbf})
        print(f"  {n:>4}{W:>6}{obf['subsets']:>13}{tbf:>10.4f}{odp['cells']:>10}{tdp:>10.5f}"
              f"{'yes' if vbf == F[n][W] else 'NO':>13}")
    return rows


def save_csv(rows, name):
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


def plot(e1, e2):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    e1s = sorted(e1, key=lambda r: r["nW"])
    x = [r["nW"] for r in e1s]
    ax1.loglog(x, [r["table_s"] for r in e1s], "o", label="bottom-up 2-D table")
    ax1.loglog(x, [r["one_row_s"] for r in e1s], "s", label="single row (Theta(W) space)")
    ax1.loglog(x, [r["mf_s"] for r in e1s], "^", label="memory function (top-down)")
    c = statistics.median(r["table_s"] / r["nW"] for r in e1s)
    ax1.loglog([x[0], x[-1]], [c * x[0], c * x[-1]], "k:", label="theory c * n*W (scaled)")
    ax1.set_title("DP knapsack: time vs table size n*W")
    ax1.set_xlabel("n * W cells (log scale)")
    ax1.set_ylabel("time in seconds (log scale)")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)

    n2 = [r["n"] for r in e2]
    ax2.semilogy(n2, [r["brute_s"] for r in e2], "o-", label="brute force (2^n subsets)")
    ax2.semilogy(n2, [r["dp_s"] for r in e2], "s-", label="bottom-up DP (n*W cells)")
    c2 = e2[-1]["brute_s"] / 2 ** n2[-1]
    ax2.semilogy(n2, [c2 * 2 ** n for n in n2], "k:", label="theory c * 2^n (scaled)")
    ax2.set_title("Exhaustive search vs DP")
    ax2.set_xlabel("number of parcels n")
    ax2.set_ylabel("time in seconds (log scale)")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    path = os.path.join(SHOTS, "task2_knapsack_growth.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main():
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    rng = random.Random(42)
    print("=" * 100)
    print(" TASK 2 - EXPERIMENTS: 0/1 KNAPSACK COST AS n*W GROWS  (random parcels, seed 42)")
    print("=" * 100)
    e1 = experiment_1(rng)
    e2 = experiment_2(rng)
    ns = [r["table_s"] * 1e9 / r["nW"] for r in e1]
    print(f"\n  bottom-up cost per cell: median {statistics.median(ns):.0f} ns (range {min(ns):.0f}-{max(ns):.0f})"
          " -> time grows linearly in n*W, as Theta(nW) predicts")
    print(f"  memory function computed {min(r['mf_fraction'] for r in e1) * 100:.0f}-"
          f"{max(r['mf_fraction'] for r in e1) * 100:.0f}% of the cells, but recursion overhead makes it slower")
    print("Saved:", os.path.relpath(save_csv(e1, "knapsack_E1.csv"), HERE), ",",
          os.path.relpath(save_csv(e2, "knapsack_E2.csv"), HERE))
    print("Graph:", os.path.relpath(plot(e1, e2), HERE))


if __name__ == "__main__":
    main()
