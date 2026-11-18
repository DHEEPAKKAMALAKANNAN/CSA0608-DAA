"""Q2 experiments - Merge Sort vs Quick Sort (3 pivot rules) on 5 input conditions and 4 sizes.

Datasets (deadlines in seconds after 06:00 within a 16-hour dispatch day, seed 42):
  random     uniform deadlines (0 .. 57,599 s)            sorted    the same values ascending
  reverse    the same values descending                    slots     64 distinct values (15-minute slots)
  all-equal  every order in one slot (edge case)
Writes results/q2_results.csv (every run) and results/q2_large.csv (n = 100,000 random).
Run:  py q2_experiments.py      (about 1-2 minutes)
"""
import csv
import math
import os
import random
import time

from q2_sorting import ALGORITHMS

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
SIZES = (1000, 2000, 4000, 8000)
DAY = 16 * 3600
SLOT = 15 * 60


def make_inputs(n, rng):
    """The five input conditions of one size (all lists contain deadlines in seconds)."""
    base = [rng.randrange(DAY) for _ in range(n)]
    return {"random": base, "sorted": sorted(base), "reverse": sorted(base, reverse=True),
            "slots": [rng.randrange(DAY // SLOT) * SLOT for _ in range(n)], "all-equal": [9 * SLOT] * n}


def run(fn, data):
    """Sort a copy of data, verify it, return (stats, time in ms). Fast runs are repeated (minimum of 3)."""
    best, stats = float("inf"), None
    for attempt in range(3):
        a = list(data)
        t0 = time.perf_counter()
        st = fn(a)
        t = (time.perf_counter() - t0) * 1000
        assert a == sorted(data), "sort failed"
        stats, best = st, min(best, t)
        if t > 200:                                      # slow (quadratic) runs: one measurement is enough
            break
    return stats, best


def theory(n):
    """Reference counts: n log2 n, merge-sort worst case, quick-sort average 2(n+1)H_n - 4n, n(n-1)/2."""
    k = math.ceil(math.log2(n))
    h = sum(1 / i for i in range(1, n + 1))
    return n * math.log2(n), n * k - 2 ** k + 1, 2 * (n + 1) * h - 4 * n, n * (n - 1) // 2


def main():
    rng = random.Random(42)
    rows = []
    print("=" * 112)
    print("Q2 EXPERIMENTS - Merge Sort vs Quick Sort (last / random / median-of-three pivot), seed 42")
    print("=" * 112)
    print("\n[1] Comparisons (counted) with reference formulas")
    print(f"{'input':>9} {'n':>6} | {'Merge':>9} {'Q-last':>10} {'Q-random':>10} {'Q-median3':>10} | "
          f"{'MS worst':>9} {'QS avg':>9} {'n(n-1)/2':>10}")
    by_key = {}
    datasets = {n: make_inputs(n, rng) for n in SIZES}
    for inp in ("random", "sorted", "reverse", "slots", "all-equal"):
        for n in SIZES:
            data = datasets[n][inp]
            cells = []
            for alg, fn in ALGORITHMS.items():
                st, t = run(fn, data)
                by_key[(alg, inp, n)] = (st, t)
                nlg, ms_worst, qs_avg, quad = theory(n)
                rows.append([alg, inp, n, st.comparisons, st.moves, st.max_depth, st.calls, round(t, 2),
                             round(nlg), ms_worst, round(qs_avg), quad])
                cells.append(st.comparisons)
            nlg, ms_worst, qs_avg, quad = theory(n)
            print(f"{inp:>9} {n:>6,} | {cells[0]:>9,} {cells[1]:>10,} {cells[2]:>10,} {cells[3]:>10,} | "
                  f"{ms_worst:>9,} {round(qs_avg):>9,} {quad:>10,}")
    n = SIZES[-1]
    for title, idx, fmt in (("[2] Moves (element writes; a swap = 2) at n = 8,000", 0, ">10,"),
                            ("[3] Maximum recursion depth at n = 8,000 (ceil(log2 n) = 13)", 1, ">10,"),
                            ("[4] Time (ms; minimum of 3 runs, single run if > 200 ms) at n = 8,000", 2, ">10.1f")):
        print(f"\n{title}")
        print(f"{'input':>9} | {'Merge':>10} {'Q-last':>10} {'Q-random':>10} {'Q-median3':>10}")
        for inp in ("random", "sorted", "reverse", "slots", "all-equal"):
            vals = []
            for alg in ALGORITHMS:
                st, t = by_key[(alg, inp, n)]
                vals.append((st.moves, st.max_depth, t)[idx])
            print(f"{inp:>9} | " + " ".join(format(v, fmt) for v in vals))

    print("\n[5] Large random input, n = 100,000 (comparisons / (n log2 n) shows the constant factor)")
    print(f"{'algorithm':>14} | {'comparisons':>12} {'/ n lg n':>8} | {'moves':>10} | {'depth':>5} | {'time ms':>8}")
    big_rng = random.Random(4242)
    big = [big_rng.randrange(DAY) for _ in range(100_000)]
    large_rows = []
    nlg = 100_000 * math.log2(100_000)
    for alg, fn in ALGORITHMS.items():
        st, t = run(fn, big)
        print(f"{alg:>14} | {st.comparisons:>12,} {st.comparisons / nlg:>8.3f} | {st.moves:>10,} | "
              f"{st.max_depth:>5} | {t:>8.1f}")
        large_rows.append([alg, 100_000, st.comparisons, round(st.comparisons / nlg, 4), st.moves, st.max_depth,
                           round(t, 1)])
    _, _, qs_avg, _ = theory(100_000)
    print(f"   references at n = 100,000: merge ~ n lg n - 1.25n -> {1 - 1.25 / math.log2(100_000):.3f}; "
          f"random pivot 2(n+1)H_n - 4n = {qs_avg:,.0f} -> {qs_avg / nlg:.3f}")
    print("   (asymptotic constants 2 ln 2 = 1.386 for a random pivot and 12/7 ln 2 = 1.188 for median-of-3 "
          "are reached only for very large n)")

    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "q2_results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["algorithm", "input", "n", "comparisons", "moves", "max_depth", "calls", "time_ms",
                    "n_log2_n", "merge_worst_formula", "quick_avg_formula", "n_n_minus_1_over_2"])
        w.writerows(rows)
    with open(os.path.join(RESULTS, "q2_large.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["algorithm", "n", "comparisons", "comparisons_per_nlog2n", "moves", "max_depth", "time_ms"])
        w.writerows(large_rows)
    print("\nCSV files written to results/: q2_results.csv, q2_large.csv")


if __name__ == "__main__":
    main()
