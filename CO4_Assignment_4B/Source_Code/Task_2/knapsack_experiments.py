"""
Task 2.3 + 2.4 - instrumented engineering comparison of Solution A (greedy) and Solution B (0/1 DP).

E0  The two test cases: comparisons / items examined / DP cells / memory cells / value / quality / guarantee.
E1  Work and memory vs capacity W (n = 100 fixed): greedy is independent of W, DP grows linearly with W.
E2  Work vs number of items n (W = 1,000 fixed): greedy ~ n log2 n comparisons, DP = (n + 1)(W + 1) cells.
E3  Solution quality of the fast 0/1 heuristics over 1,000 random instances (n = 15, brute-force-free: the DP
    is the reference) for uncorrelated and strongly correlated (value = weight + 10) data.
E4  Changed requirement (2.4): measured time of the greedy, best-of-two heuristic and DP for realistic sizes.
Operation counts are the primary evidence; times are medians of 5 runs (secondary). Seed 42.
Writes results/t2_*.csv and the graph results/t2_engineering_comparison.png (+ copy in Report/Screenshots).
Run:  py -3 knapsack_experiments.py
"""
import csv
import json
import math
import os
import random
import shutil
import statistics
import time
import tracemalloc
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import knapsack_engines as ks  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.normpath(os.path.join(HERE, "..", "..", "Report", "Screenshots"))


def write_csv(name, rows):
    with open(os.path.join(HERE, "results", name), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def random_items(rng, n, max_w=100, correlated=False):
    items = []
    for k in range(n):
        w = rng.randint(1, max_w)
        v = w + 10 if correlated else rng.randint(1, 100)
        items.append(ks.Item(f"I{k}", w, v))
    return items


def median_time(fn, repeats=5):
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def peak_bytes(fn):
    tracemalloc.start()
    fn()
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return peak


def e0_test_cases():
    print("E0  Instrumented comparison on the two test cases")
    print(f"    {'case':<5} {'solution':<26} {'comparisons':>11} {'items exam.':>11} {'DP cells':>8} "
          f"{'memory cells':>12} {'value':>7} {'% of opt':>8}  guarantee")
    rows = []
    for name in ("normal_case.json", "counterexample.json"):
        with open(os.path.join(HERE, "test_data", name), encoding="utf-8") as f:
            spec = json.load(f)
        items, cap = [ks.Item(*r) for r in spec["items"]], spec["capacity"]
        opt = ks.knapsack_01_dp(items, cap)[0]
        label = spec["name"].split()[0]
        results = []
        ops = Counter()
        v, _, _ = ks.fractional_greedy(items, cap, ops)
        results.append(("A fractional greedy", ops, float(v), "optimal (fractional)"))
        ops = Counter()
        v, _, _ = ks.greedy_01_ratio(items, cap, ops)
        results.append(("ratio greedy on 0/1", ops, v, "none (arbitrarily bad)"))
        ops = Counter()
        v, _, _ = ks.knapsack_01_dp(items, cap, ops)
        results.append(("B 0/1 DP", ops, v, "optimal (0/1)"))
        for sol, ops, v, guarantee in results:
            pct = 100 * v / opt
            print(f"    {label:<5} {sol:<26} {ops['comparisons']:>11} {ops['items_examined']:>11} {ops['dp_cells']:>8} "
                  f"{ops['memory_cells']:>12} {v:>7.1f} {pct:>7.1f}%  {guarantee}")
            rows.append(dict(case=label, solution=sol, comparisons=ops["comparisons"],
                             items_examined=ops["items_examined"], dp_cells=ops["dp_cells"],
                             memory_cells=ops["memory_cells"], value=round(v, 2), pct_of_01_opt=round(pct, 1),
                             guarantee=guarantee))
    write_csv("t2_test_case_comparison.csv", rows)
    print("    (the fractional value may exceed the 0/1 optimum: it is an upper bound for the 0/1 problem)")


def e1_capacity(rng):
    print("\nE1  Work and memory vs capacity W (n = 100 items, weights 1..W/2)")
    print(f"    {'W':>7} {'greedy cmp':>10} {'greedy mem':>10} {'DP cells':>11} {'DP mem cells':>12} "
          f"{'DP peak KiB':>11} {'greedy ms':>9} {'DP ms':>9}")
    rows = []
    for cap in (100, 300, 1000, 3000, 10000, 30000):
        items = random_items(rng, 100, max_w=max(2, cap // 2))
        gops, dops = Counter(), Counter()
        ks.fractional_greedy(items, cap, gops)
        ks.knapsack_01_dp(items, cap, dops)
        g_ms = median_time(lambda: ks.fractional_greedy(items, cap)) * 1000
        d_ms = median_time(lambda: ks.knapsack_01_dp(items, cap), repeats=3) * 1000
        peak = peak_bytes(lambda: ks.knapsack_01_dp(items, cap)) / 1024
        rows.append(dict(capacity=cap, greedy_comparisons=gops["comparisons"], greedy_memory_cells=gops["memory_cells"],
                         dp_cells=dops["dp_cells"], dp_memory_cells=dops["memory_cells"], dp_peak_kib=round(peak),
                         greedy_ms=round(g_ms, 3), dp_ms=round(d_ms, 2)))
        print(f"    {cap:>7,} {gops['comparisons']:>10,} {gops['memory_cells']:>10,} {dops['dp_cells']:>11,} "
              f"{dops['memory_cells']:>12,} {peak:>11,.0f} {g_ms:>9.3f} {d_ms:>9.2f}")
    write_csv("t2_work_vs_capacity.csv", rows)
    return rows


def e2_items(rng):
    print("\nE2  Work vs number of items n (W = 1,000)")
    print(f"    {'n':>5} {'greedy cmp':>10} {'n log2 n':>9} {'DP cells':>10} {'(n+1)(W+1)':>10} {'greedy ms':>9} "
          f"{'DP ms':>8}")
    rows = []
    for n in (25, 50, 100, 200, 400, 800):
        items = random_items(rng, n)
        gops, dops = Counter(), Counter()
        ks.fractional_greedy(items, 1000, gops)
        ks.knapsack_01_dp(items, 1000, dops)
        g_ms = median_time(lambda: ks.fractional_greedy(items, 1000)) * 1000
        d_ms = median_time(lambda: ks.knapsack_01_dp(items, 1000), repeats=3) * 1000
        rows.append(dict(n=n, greedy_comparisons=gops["comparisons"], n_log2_n=round(n * math.log2(n)),
                         dp_cells=dops["dp_cells"], greedy_ms=round(g_ms, 3), dp_ms=round(d_ms, 2)))
        print(f"    {n:>5} {gops['comparisons']:>10,} {rows[-1]['n_log2_n']:>9,} {dops['dp_cells']:>10,} "
              f"{(n + 1) * 1001:>10,} {g_ms:>9.3f} {d_ms:>8.2f}")
    write_csv("t2_work_vs_items.csv", rows)
    return rows


def e3_quality(rng):
    print("\nE3  Quality of the fast 0/1 heuristics vs the DP optimum (1,000 random instances each, n = 15)")
    print(f"    {'data':<22} {'heuristic':<24} {'mean %':>7} {'worst %':>8} {'optimal in':>10}")
    rows, ratios_all = [], {}
    for correlated in (False, True):
        label = "strongly correlated" if correlated else "uncorrelated"
        ratios = {"ratio greedy": [], "best-of-two": []}
        for _ in range(1000):
            items = random_items(rng, 15, correlated=correlated)
            cap = sum(it.weight for it in items) // 2
            opt = ks.knapsack_01_dp(items, cap)[0]
            ratios["ratio greedy"].append(ks.greedy_01_ratio(items, cap)[0] / opt)
            ratios["best-of-two"].append(ks.greedy_01_best_of_two(items, cap)[0] / opt)
        for name, r in ratios.items():
            optimal = sum(1 for x in r if x == 1.0)
            rows.append(dict(data=label, heuristic=name, mean_pct=round(100 * statistics.mean(r), 2),
                             worst_pct=round(100 * min(r), 2), optimal_count=optimal, instances=len(r)))
            print(f"    {label:<22} {name:<24} {100 * statistics.mean(r):>6.2f}% {100 * min(r):>7.2f}% "
                  f"{optimal:>5}/1000")
        ratios_all[label] = ratios["ratio greedy"]
    adversarial = [ks.Item("tiny", 1, 2), ks.Item("big", 1000, 1000)]
    g = ks.greedy_01_ratio(adversarial, 1000)[0]
    b = ks.greedy_01_best_of_two(adversarial, 1000)[0]
    print("    adversarial instance W = 1000: tiny(1 kg, value 2, ratio 2.0) + big(1000 kg, value 1000, ratio 1.0)")
    print(f"      ratio greedy {g} = {100 * g / 1000:.1f} % of the optimum 1000;  best-of-two {b} "
          f"(= {100 * b / 1000:.0f} %)")
    write_csv("t2_quality.csv", rows)
    return ratios_all


def e4_requirement():
    print("\nE4  Changed requirement - measured decision time (median of 3) for growing problem sizes")
    print(f"    {'n':>6} {'W':>8} {'DP cells':>13} {'greedy ms':>9} {'best-of-2 ms':>12} {'DP ms':>10} "
          f"{'greedy % of opt':>15}")
    rng, rows = random.Random(7), []
    for n, cap in ((50, 1000), (200, 5000), (500, 20000), (1000, 50000)):
        items = [ks.Item(f"I{k}", rng.randint(1, cap // 10), rng.randint(1, 1000)) for k in range(n)]
        g_ms = median_time(lambda: ks.greedy_01_ratio(items, cap), 3) * 1000
        b_ms = median_time(lambda: ks.greedy_01_best_of_two(items, cap), 3) * 1000
        start = time.perf_counter()
        opt = ks.knapsack_01_value_1d(items, cap)
        d_ms = (time.perf_counter() - start) * 1000
        pct = 100 * ks.greedy_01_ratio(items, cap)[0] / opt
        rows.append(dict(n=n, capacity=cap, dp_cells=n * (cap + 1), greedy_ms=round(g_ms, 2),
                         best_of_two_ms=round(b_ms, 2), dp_ms=round(d_ms, 1), greedy_pct_of_opt=round(pct, 3)))
        print(f"    {n:>6,} {cap:>8,} {n * (cap + 1):>13,} {g_ms:>9.2f} {b_ms:>12.2f} {d_ms:>10.1f} {pct:>14.3f}%")
    write_csv("t2_requirement_change.csv", rows)
    print("    (DP here = the memory-optimised one-row version, value only)")


def plot(cap_rows, n_rows, ratios):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    w = [r["capacity"] for r in cap_rows]
    axes[0].loglog(w, [r["dp_cells"] for r in cap_rows], "o-", label="DP: table cells (work)", color="#d62728")
    axes[0].loglog(w, [r["dp_memory_cells"] for r in cap_rows], "s--", label="DP: memory cells", color="#ff9896")
    axes[0].loglog(w, [r["greedy_comparisons"] for r in cap_rows], "o-", label="greedy: comparisons",
                   color="#1f77b4")
    axes[0].loglog(w, [r["greedy_memory_cells"] for r in cap_rows], "s--", label="greedy: memory cells",
                   color="#aec7e8")
    axes[0].set_xlabel("vehicle capacity W (kg)")
    axes[0].set_ylabel("count (log scale)")
    axes[0].set_title("Work & memory vs W (n = 100)")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3, which="both")
    n = [r["n"] for r in n_rows]
    axes[1].loglog(n, [r["dp_cells"] for r in n_rows], "o-", color="#d62728", label="DP cells (measured)")
    axes[1].loglog(n, [r["greedy_comparisons"] for r in n_rows], "o-", color="#1f77b4",
                   label="greedy comparisons (measured)")
    axes[1].loglog(n, [r["n_log2_n"] for r in n_rows], "k:", label="n log₂ n (theory)")
    axes[1].set_xlabel("number of items n")
    axes[1].set_ylabel("count (log scale)")
    axes[1].set_title("Work vs n (W = 1,000)")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.3, which="both")
    bins = [0.80 + 0.01 * k for k in range(21)]
    for label, color in (("uncorrelated", "#1f77b4"), ("strongly correlated", "#d62728")):
        axes[2].hist([min(1.0, max(0.8, x)) for x in ratios[label]], bins=bins, alpha=0.6, color=color, label=label)
    axes[2].set_xlabel("ratio-greedy value / DP optimum")
    axes[2].set_ylabel("number of instances (of 1,000)")
    axes[2].set_title("0/1 solution quality of the greedy (n = 15)")
    axes[2].legend(fontsize=8)
    axes[2].grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(HERE, "results", "t2_engineering_comparison.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    shutil.copy(path, os.path.join(SHOTS, "t2_engineering_comparison.png"))


def main():
    rng = random.Random(42)
    print("TASK 2.3 + 2.4 - ENGINEERING COMPARISON OF GREEDY AND DP (operation counts first, time second)")
    print("=" * 112)
    e0_test_cases()
    cap_rows = e1_capacity(rng)
    n_rows = e2_items(rng)
    ratios = e3_quality(rng)
    e4_requirement()
    plot(cap_rows, n_rows, ratios)
    print("\nGraph: results/t2_engineering_comparison.png")


if __name__ == "__main__":
    main()
