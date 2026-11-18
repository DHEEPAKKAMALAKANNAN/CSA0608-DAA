"""
Task 2 - experiments: when is greedy optimal for knapsack and coin change, and what does optimisation buy?

E1  0/1 knapsack quality: 2,000 random instances (n = 15) of two classes, every greedy rule against the exact
    DP optimum (DP certified by brute force on the first 100 instances of each class).
E2  Fractional knapsack optimisation: full merge sort vs bottom-up heap + lazy pops, n = 1,000 .. 128,000,
    for a small truck (capacity = 5% of the total weight) and a truck that takes everything (100%).
E3  Coin change: greedy vs DP for every amount 1..1,000 in six coin systems.
Run:  py -3 task2_experiments.py
"""
import csv
import math
import os
import random
import statistics
import time
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from knapsack_coin_change import (INR, Item, dp_change, fractional_heap, fractional_sort, greedy_01,  # noqa: E402
                                  greedy_01_half_approx, greedy_change, knapsack_01_bruteforce,
                                  knapsack_01_dp)

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
SEED = 42


def write_csv(name, rows):
    with open(os.path.join(RES, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def instance(rng, n, kind):
    """'uncorrelated': independent w, v in 1..100; 'correlated': v = w + 10 (hard for greedy)."""
    items = []
    for i in range(n):
        w = rng.randint(1, 100)
        v = rng.randint(1, 100) if kind == "uncorrelated" else w + 10
        items.append(Item(f"i{i}", w, v))
    return items, max(1, int(0.4 * sum(it.weight for it in items)))


def e1_quality(trials=2000, n=15):
    rng = random.Random(SEED)
    rules = {"greedy by density": lambda it, W: greedy_01(it, W, "density")[0],
             "greedy by value": lambda it, W: greedy_01(it, W, "value")[0],
             "greedy by lightest": lambda it, W: greedy_01(it, W, "lightest")[0],
             "max(density, best single)": lambda it, W: greedy_01_half_approx(it, W)[0]}
    rows = []
    print(f"E1  0/1 knapsack: {trials:,} random instances per class, n = {n}, W = 40% of total weight")
    print(f"    {'class':<13} {'strategy':<27} {'% optimal':>9} {'mean ratio':>10} {'worst ratio':>11} "
          f"{'greedy cmp':>10} {'DP cells':>9}")
    for kind in ("uncorrelated", "correlated"):
        res = {r: [] for r in rules}
        cells = []
        cmp_count = []
        for t in range(trials):
            items, W = instance(rng, n, kind)
            ops = Counter()
            opt = knapsack_01_dp(items, W, ops)[0]
            cells.append(ops["dp_cells"])
            if t < 100:
                assert knapsack_01_bruteforce(items, W) == opt
            gops = Counter()
            greedy_01(items, W, "density", gops)
            cmp_count.append(gops["comparisons"])
            for r, fn in rules.items():
                res[r].append(fn(items, W) / opt)
        for r, ratios in res.items():
            pct = 100 * sum(x == 1 for x in ratios) / trials
            row = dict(instance_class=kind, strategy=r, trials=trials, n=n, pct_optimal=round(pct, 1),
                       mean_ratio=round(statistics.mean(ratios), 4), worst_ratio=round(min(ratios), 4),
                       mean_greedy_comparisons=round(statistics.mean(cmp_count), 1),
                       mean_dp_cells=round(statistics.mean(cells)))
            rows.append(row)
            print(f"    {kind:<13} {r:<27} {pct:>8.1f}% {row['mean_ratio']:>10.4f} {row['worst_ratio']:>11.3f} "
                  f"{row['mean_greedy_comparisons']:>10} {row['mean_dp_cells']:>9,}")
    write_csv("task2_01_greedy_quality.csv", rows)
    return rows


def e2_fractional(sizes=(1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000)):
    rng = random.Random(SEED)
    rows = []
    print("\nE2  Fractional knapsack: full sort vs heap + lazy pops (k = items loaded)")
    print(f"    {'n':>7} {'capacity':>8} {'k':>7} {'sort cmp':>10} {'n log2 n':>10} {'heap cmp':>10} "
          f"{'2n + 2k log2 n':>14} {'sort ms':>8} {'heap ms':>8} {'same value':>10}")
    for n in sizes:
        items = [Item(i, rng.randint(1, 100), rng.randint(1, 1000)) for i in range(n)]
        total_w = sum(it.weight for it in items)
        for share in (0.05, 1.0):
            W = int(share * total_w)
            so, ho = Counter(), Counter()
            t0 = time.perf_counter(); sv, splan = fractional_sort(items, W, so); ts = time.perf_counter() - t0
            t0 = time.perf_counter(); hv, _ = fractional_heap(items, W, ho); th = time.perf_counter() - t0
            k = len(splan)
            bound = 2 * n + 2 * k * math.log2(n)
            rows.append(dict(n=n, capacity_share=share, k_loaded=k, sort_comparisons=so["comparisons"],
                             n_log2_n=round(n * math.log2(n)), heap_comparisons=ho["comparisons"],
                             heap_bound=round(bound), sort_ms=round(ts * 1e3, 1), heap_ms=round(th * 1e3, 1),
                             same_value=sv == hv))
            print(f"    {n:>7,} {f'{share:.0%}':>8} {k:>7,} {so['comparisons']:>10,} {round(n * math.log2(n)):>10,} "
                  f"{ho['comparisons']:>10,} {round(bound):>14,} {ts * 1e3:>8.1f} {th * 1e3:>8.1f} "
                  f"{str(sv == hv):>10}")
    write_csv("task2_02_fractional_sort_vs_heap.csv", rows)
    return rows


def e3_coins(max_amount=1000):
    systems = {"Indian rupee": INR, "US cents": (1, 5, 10, 25), "{1, 3, 4}": (1, 3, 4),
               "{1, 10, 25}": (1, 10, 25), "{1, 7, 10}": (1, 7, 10), "UK pre-1971": (1, 3, 6, 12, 24, 30)}
    rows = []
    print(f"\nE3  Coin change: greedy vs DP for every amount 1..{max_amount:,}")
    print(f"    {'system':<14} {'non-optimal amounts':>19} {'share':>7} {'max extra coins':>15} "
          f"{'greedy coins':>12} {'optimal coins':>13} {'DP steps':>9}")
    for name, cs in systems.items():
        ops = Counter()
        bad = extra = g_tot = o_tot = 0
        for a in range(1, max_amount + 1):
            g = len(greedy_change(cs, a))
            o = len(dp_change(cs, a, ops if a == max_amount else None))
            g_tot += g; o_tot += o
            if g > o:
                bad += 1
                extra = max(extra, g - o)
        rows.append(dict(system=name, coins=" ".join(map(str, cs)), amounts=max_amount, non_optimal=bad,
                         share_pct=round(100 * bad / max_amount, 1), max_extra_coins=extra,
                         greedy_coins_total=g_tot, optimal_coins_total=o_tot,
                         dp_steps_for_max_amount=ops["dp_steps"]))
        print(f"    {name:<14} {bad:>19,} {100 * bad / max_amount:>6.1f}% {extra:>15} {g_tot:>12,} {o_tot:>13,} "
              f"{ops['dp_steps']:>9,}")
    write_csv("task2_03_coin_systems.csv", rows)
    return rows


def plot(q_rows, f_rows, c_rows):
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
    strategies = list(dict.fromkeys(r["strategy"] for r in q_rows))
    x = range(len(strategies))
    for off, kind, col in ((-0.2, "uncorrelated", "#1565C0"), (0.2, "correlated", "#EF6C00")):
        vals = [next(r["pct_optimal"] for r in q_rows if r["strategy"] == s and r["instance_class"] == kind)
                for s in strategies]
        ax[0].bar([i + off for i in x], vals, width=0.4, label=kind, color=col)
    ax[0].set_xticks(list(x)); ax[0].set_xticklabels([s.replace(" ", "\n", 2) for s in strategies], fontsize=7)
    ax[0].set_ylabel("instances solved optimally (%)"); ax[0].set_ylim(0, 100)
    ax[0].set_title("E1: greedy on 0/1 knapsack (n = 15)"); ax[0].legend(fontsize=8); ax[0].grid(axis="y", alpha=0.3)
    for share, mk in ((0.05, "o"), (1.0, "s")):
        rr = [r for r in f_rows if r["capacity_share"] == share]
        ns = [r["n"] for r in rr]
        if share == 1.0:            # the sort does identical work for every capacity
            ax[1].loglog(ns, [r["sort_comparisons"] for r in rr], "^-", color="#2E7D32", label="sort (any W)")
        ax[1].loglog(ns, [r["heap_comparisons"] for r in rr], mk + "--", label=f"heap, W = {share:.0%}")
    ns = sorted({r["n"] for r in f_rows})
    ax[1].loglog(ns, [n * math.log2(n) for n in ns], "k:", lw=1, label="n log₂ n")
    ax[1].set_xlabel("number of items n"); ax[1].set_ylabel("key comparisons (count)")
    ax[1].set_title("E2: fractional knapsack, sort vs heap"); ax[1].legend(fontsize=7)
    ax[1].grid(True, which="both", alpha=0.3)
    ax[2].bar([r["system"] for r in c_rows], [r["share_pct"] for r in c_rows],
              color=["#2E7D32" if r["non_optimal"] == 0 else "#C62828" for r in c_rows])
    for i, r in enumerate(c_rows):
        ax[2].text(i, r["share_pct"] + 0.8, f"{r['share_pct']:.1f}%", ha="center", fontsize=8)
    ax[2].set_ylabel("amounts 1..1000 where greedy is not optimal (%)")
    ax[2].set_title("E3: greedy change-making by coin system"); ax[2].tick_params(axis="x", rotation=25, labelsize=8)
    ax[2].grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "task2_experiments.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(RES, exist_ok=True)
    print("TASK 2 - EXPERIMENTS (seed 42)")
    print("=" * 118)
    q = e1_quality()
    f = e2_fractional()
    c = e3_coins()
    plot(q, f, c)
    print("\nWrote results/task2_01..03_*.csv and results/task2_experiments.png")


if __name__ == "__main__":
    main()
