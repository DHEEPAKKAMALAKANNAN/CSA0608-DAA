"""
Task 1 - experiments for activity selection (EOC briefing-room bookings).

E1  Rule comparison: 2,000 random days of 12 requests; every greedy rule is compared with the exact optimum
    (DP, certified against brute force on the first 200 days) -> how often each rule is optimal.
E2  Scaling + optimisation: the naive re-scanning EFT (Theta(n*k)) against the sort-once EFT
    (Theta(n log n)); counted comparisons are the primary evidence, time is secondary.
Writes results/task1_rule_comparison.csv, results/task1_scaling.csv and two PNG graphs.
Run:  py -3 task1_experiments.py
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

from activity_selection import (RULES, Request, optimum_bruteforce, optimum_dp, select_eft,  # noqa: E402
                                select_naive_rescan)

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
SEED = 42


def random_day(rng, n, horizon=600, slot=15):
    """n requests inside a 10-hour day (08:00-18:00), starts on 15-min slots, durations 30-240 min."""
    reqs = []
    for i in range(n):
        s = 480 + rng.randrange(0, horizon - 30, slot)
        d = rng.randrange(30, 241, slot)
        reqs.append(Request(f"Q{i}", "", s, min(s + d, 480 + horizon)))
    return reqs


def random_term(rng, n):
    """n requests spread over a horizon proportional to n (a whole booking term): k grows with n."""
    return [Request(i, "", s, s + rng.randrange(30, 241, 15))
            for i, s in enumerate(rng.randrange(0, 30 * n, 15) for _ in range(n))]


def write_csv(name, rows):
    with open(os.path.join(RES, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def e1_rule_comparison(trials=2000, n=12):
    rng = random.Random(SEED)
    stats = {rule: {"optimal": 0, "ratios": []} for rule in RULES}
    certified = 0
    for t in range(trials):
        day = random_day(rng, n)
        opt = optimum_dp(day)
        if t < 200:                                   # certify the DP reference with brute force
            assert optimum_bruteforce(day) == opt
            certified += 1
        for rule, fn in RULES.items():
            got = len(fn(day))
            stats[rule]["optimal"] += got == opt
            stats[rule]["ratios"].append(got / opt)
    rows = []
    print(f"E1  {trials:,} random days x {n} requests (DP optimum, certified by brute force on {certified} days)")
    print(f"    {'greedy rule':<22} {'optimal days':>12} {'% optimal':>10} {'mean ratio':>11} {'worst ratio':>12}")
    for rule, s in stats.items():
        pct = 100 * s["optimal"] / trials
        mean, worst = statistics.mean(s["ratios"]), min(s["ratios"])
        rows.append(dict(rule=rule, trials=trials, n=n, optimal_days=s["optimal"], pct_optimal=round(pct, 2),
                         mean_ratio=round(mean, 4), worst_ratio=round(worst, 4)))
        print(f"    {rule:<22} {s['optimal']:>12,} {pct:>9.1f}% {mean:>11.4f} {worst:>12.3f}")
    write_csv("task1_rule_comparison.csv", rows)
    return rows


def e2_scaling(sizes=(1000, 2000, 4000, 8000, 16000, 32000, 64000), naive_max=8000):
    rng = random.Random(SEED)
    rows = []
    print("\nE2  Scaling: sort-once EFT vs naive re-scanning EFT (random booking terms, k grows with n)")
    print(f"    {'n':>6} {'k':>6} {'EFT comparisons':>16} {'n log2 n':>10} {'ratio':>6} {'EFT ms':>8} "
          f"{'naive comparisons':>18} {'naive ms':>9} {'optimum(DP)':>11}")
    for n in sizes:
        reqs = random_term(rng, n)
        ops, best_t = Counter(), float("inf")
        for rep in range(3):
            o = Counter()
            t0 = time.perf_counter()
            chosen = select_eft(reqs, o)
            best_t = min(best_t, time.perf_counter() - t0)
            ops = o
        eft_cmp = ops["sort_comparisons"] + ops["compatibility_checks"]
        opt = optimum_dp(reqs)
        assert len(chosen) == opt
        naive_cmp, naive_ms = "", ""
        if n <= naive_max:
            o = Counter()
            t0 = time.perf_counter()
            nv = select_naive_rescan(reqs, o)
            naive_ms = round((time.perf_counter() - t0) * 1e3, 1)
            naive_cmp = o["scan_comparisons"]
            assert len(nv) == opt
        nlogn = n * math.log2(n)
        rows.append(dict(n=n, accepted_k=len(chosen), eft_sort_comparisons=ops["sort_comparisons"],
                         eft_checks=ops["compatibility_checks"], eft_total=eft_cmp, n_log2_n=round(nlogn),
                         eft_ms=round(best_t * 1e3, 2), naive_comparisons=naive_cmp, naive_ms=naive_ms,
                         optimum_dp=opt))
        print(f"    {n:>6,} {len(chosen):>6,} {eft_cmp:>16,} {round(nlogn):>10,} {eft_cmp / nlogn:>6.3f} "
              f"{best_t * 1e3:>8.1f} {naive_cmp if naive_cmp == '' else f'{naive_cmp:,}':>18} "
              f"{str(naive_ms):>9} {opt:>11,}")
    write_csv("task1_scaling.csv", rows)
    return rows


def plot(rule_rows, scale_rows):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    names = [r["rule"] for r in rule_rows]
    colors = ["#2E7D32" if r["pct_optimal"] == 100 else "#C62828" for r in rule_rows]
    ax[0].barh(names, [r["pct_optimal"] for r in rule_rows], color=colors)
    for i, r in enumerate(rule_rows):
        ax[0].text(r["pct_optimal"] + 1, i, f"{r['optimal_days']:,}/{r['trials']:,}", va="center", fontsize=8)
    ax[0].set_xlim(0, 125); ax[0].invert_yaxis()
    ax[0].set_xlabel("days on which the rule found the optimum (%)")
    ax[0].set_title("E1: how often each greedy rule is optimal\n(2,000 random days, n = 12)")
    ax[0].grid(axis="x", alpha=0.3)
    ax[1].bar(names, [r["worst_ratio"] for r in rule_rows], color=colors)
    ax[1].set_ylim(0, 1.1); ax[1].set_ylabel("worst ratio  accepted / optimum")
    ax[1].set_title("E1: worst case of each rule")
    ax[1].tick_params(axis="x", rotation=25, labelsize=8); ax[1].grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "task1_rule_comparison.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    n = [r["n"] for r in scale_rows]
    eft = [r["eft_total"] for r in scale_rows]
    nv = [(r["n"], r["naive_comparisons"]) for r in scale_rows if r["naive_comparisons"] != ""]
    ax[0].loglog(n, eft, "o-", label="sort-once EFT (measured)")
    ax[0].loglog([a for a, _ in nv], [b for _, b in nv], "s-", label="naive re-scan EFT (measured)")
    ax[0].loglog(n, [x * math.log2(x) for x in n], "k--", lw=1, label="n log₂ n")
    c = nv[-1][1] / nv[-1][0] ** 2
    ax[0].loglog(n, [c * x * x for x in n], "k:", lw=1, label="c·n² (scaled)")
    ax[0].set_xlabel("number of requests n"); ax[0].set_ylabel("comparisons (count)")
    ax[0].set_title("E2: comparisons"); ax[0].legend(fontsize=8); ax[0].grid(True, which="both", alpha=0.3)
    ax[1].loglog(n, [r["eft_ms"] for r in scale_rows], "o-", label="sort-once EFT")
    ax[1].loglog([r["n"] for r in scale_rows if r["naive_ms"] != ""],
                 [r["naive_ms"] for r in scale_rows if r["naive_ms"] != ""], "s-", label="naive re-scan EFT")
    ax[1].set_xlabel("number of requests n"); ax[1].set_ylabel("time (ms)")
    ax[1].set_title("E2: running time (best of 3 / single run)"); ax[1].legend(fontsize=8)
    ax[1].grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "task1_scaling.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(RES, exist_ok=True)
    print("TASK 1 - EXPERIMENTS (seed 42)")
    print("=" * 110)
    rules = e1_rule_comparison()
    scale = e2_scaling()
    plot(rules, scale)
    print("\nWrote results/task1_rule_comparison.csv, results/task1_scaling.csv and 2 PNG graphs")


if __name__ == "__main__":
    main()
