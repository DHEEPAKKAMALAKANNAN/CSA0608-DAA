"""Q1 experiments - comparison counts of Max-Min and Binary Search against their closed forms.

Writes four CSV files to results/:
  q1_maxmin_growth.csv   naive / D&C 'half' / D&C 'even' at 7 sizes (random temperatures) + times
  q1_maxmin_inputs.csv   the same three methods on 4 input orders at n = 10,000 (data independence)
  q1_maxmin_sweep.csv    every n from 2 to 2,048: comparisons per reading of both division rules
  q1_binary_search.csv   all n successful and all n + 1 unsuccessful look-ups at 6 manifest sizes
  q1_designed_cases.csv  designed look-ups (first/middle/last/deepest, absent below/inside/above) at 4 sizes
Run:  py q1_experiments.py      (about 1 minute; seed 42)
"""
import csv
import os
import random
import sys
import time

from q1_maxmin_binsearch import (binary_search, floor_log2, maxmin_dc, maxmin_formula_from_leaves,
                                 maxmin_formula_optimal, maxmin_naive, maxmin_pairwise)

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
SEED = 42


def write_csv(name, header, rows):
    """Save one table of raw numbers next to the graphs."""
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def best_time(fn, repeats=3):
    """Minimum wall-clock time (ms) of `repeats` calls of fn()."""
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t0)
    return best * 1000


def temperatures(n, rng):
    """n battery-cell temperatures in deg C (one decimal, 15.0 - 65.0)."""
    return [rng.randint(150, 650) / 10 for _ in range(n)]


def experiment_maxmin_growth(rng):
    print("\n[1a] Max-Min on random flight logs: counted comparisons vs closed forms")
    print(f"{'n':>9} | {'naive':>9} {'2n-2':>9} | {'D&C half':>9} {'L1':>6} {'(3n+L1)/2-2':>11} | "
          f"{'D&C even':>9} {'pairwise':>9} {'ceil(3n/2)-2':>12} | {'saving':>6}")
    rows, timing_lines = [], []
    for n in (1000, 1024, 1500, 10_000, 65_536, 100_000, 1_000_000):
        a = temperatures(n, rng)
        mx, mn = max(a), min(a)
        r_naive = maxmin_naive(a)
        r_half = maxmin_dc(a, "half")
        r_even = maxmin_dc(a, "even")
        r_pair = maxmin_pairwise(a)
        assert r_naive[:2] == r_half[:2] == r_even[:2] == r_pair[:2] == (mx, mn)
        c_naive, s_half, s_even = r_naive[2].comparisons, r_half[2], r_even[2]
        c_pair = r_pair[2].comparisons
        f_half = maxmin_formula_from_leaves(n, s_half.leaves1)
        f_opt = maxmin_formula_optimal(n)
        reps = 1 if n >= 1_000_000 else 3
        t_naive = best_time(lambda: maxmin_naive(a), reps)
        t_half = best_time(lambda: maxmin_dc(a, "half"), reps)
        t_even = best_time(lambda: maxmin_dc(a, "even"), reps)
        t_pair = best_time(lambda: maxmin_pairwise(a), reps)
        saving = 100 * (1 - s_even.comparisons / c_naive)
        print(f"{n:>9,} | {c_naive:>9,} {2 * n - 2:>9,} | {s_half.comparisons:>9,} {s_half.leaves1:>6,} "
              f"{f_half:>11,} | {s_even.comparisons:>9,} {c_pair:>9,} {f_opt:>12,} | {saving:>5.1f}%")
        timing_lines.append(f"{n:>9,} | {s_half.calls:>9,} {s_half.max_depth:>6} | {s_even.calls:>9,} "
                            f"{s_even.max_depth:>6} | {t_naive:>9.1f} {t_half:>9.1f} {t_even:>9.1f} {t_pair:>9.1f}")
        rows.append([n, c_naive, 2 * n - 2, s_half.comparisons, s_half.leaves1, f_half, s_half.calls,
                     s_half.max_depth, s_even.comparisons, f_opt, s_even.calls, s_even.max_depth, c_pair,
                     round(saving, 2), round(t_naive, 2), round(t_half, 2), round(t_even, 2), round(t_pair, 2)])
    print("\n[1b] Recursion size and time (ms, minimum of 3 runs; 1 run at n = 1,000,000)")
    print(f"{'n':>9} | {'half calls':>9} {'depth':>6} | {'even calls':>9} {'depth':>6} | "
          f"{'t naive':>9} {'t half':>9} {'t even':>9} {'t pairwise':>9}")
    for line in timing_lines:
        print(line)
    write_csv("q1_maxmin_growth.csv",
              ["n", "naive_comparisons", "formula_2n_minus_2", "half_comparisons", "half_leaves1",
               "half_formula_3n_plus_L1_over_2_minus_2", "half_calls", "half_depth", "even_comparisons",
               "formula_ceil_3n_over_2_minus_2", "even_calls", "even_depth", "pairwise_comparisons",
               "saving_even_vs_naive_pct", "time_naive_ms", "time_half_ms", "time_even_ms", "time_pairwise_ms"],
              rows)


def experiment_maxmin_inputs(rng):
    n = 10_000
    print(f"\n[2] Data independence at n = {n:,}: comparisons for four orders of the same readings")
    base = temperatures(n, rng)
    inputs = {"random": base, "ascending": sorted(base), "descending": sorted(base, reverse=True),
              "all equal": [36.6] * n}
    print(f"{'input':>11} | {'naive':>8} | {'D&C half':>8} | {'D&C even':>8} | {'pairwise':>8}")
    rows = []
    for name, a in inputs.items():
        c = [maxmin_naive(a)[2].comparisons, maxmin_dc(a, "half")[2].comparisons,
             maxmin_dc(a, "even")[2].comparisons, maxmin_pairwise(a)[2].comparisons]
        print(f"{name:>11} | {c[0]:>8,} | {c[1]:>8,} | {c[2]:>8,} | {c[3]:>8,}")
        rows.append([name, n] + c)
    write_csv("q1_maxmin_inputs.csv", ["input", "n", "naive", "dc_half", "dc_even", "pairwise"], rows)


def experiment_maxmin_sweep(rng):
    print("\n[3] Every n from 2 to 2,048: how far is each division rule from the optimum ceil(3n/2) - 2?")
    rows, worse, worst_gap, worst_n = [], 0, 0, 0
    for n in range(2, 2049):
        a = temperatures(n, rng)
        s_half, s_even = maxmin_dc(a, "half")[2], maxmin_dc(a, "even")[2]
        opt = maxmin_formula_optimal(n)
        assert s_even.comparisons == opt == maxmin_pairwise(a)[2].comparisons
        gap = s_half.comparisons - opt
        worse += gap > 0
        if gap > worst_gap:
            worst_gap, worst_n = gap, n
        rows.append([n, 2 * n - 2, s_half.comparisons, s_even.comparisons, opt, s_half.leaves1])
    pct = 100 * worst_gap / maxmin_formula_optimal(worst_n)
    print(f"   rule 'even' and the pairwise loop = ceil(3n/2) - 2 for all 2,047 sizes;")
    print(f"   rule 'half' is above the optimum for {worse:,} of the 2,047 sizes, by up to {worst_gap} comparisons "
          f"(n = {worst_n:,}, +{pct:.1f}%)")
    write_csv("q1_maxmin_sweep.csv", ["n", "naive", "dc_half", "dc_even", "optimum", "half_leaves1"], rows)


def exact_bs_averages(n):
    """Exact average probes of binary search over all n keys / all n + 1 gaps (balanced decision tree)."""
    internal_path = sum(floor_log2(i) for i in range(1, n + 1))
    return (internal_path + n) / n, (internal_path + 2 * n) / (n + 1)


def experiment_binary_search(rng):
    print("\n[4] Binary search in sorted manifests: every present ID and one absent ID per gap (n + 1)")
    print(f"{'n':>9} | {'max succ':>8} {'max unsucc':>10} {'floor(lg n)+1':>13} | {'avg succ':>8} {'theory':>7} | "
          f"{'avg unsucc':>10} {'theory':>7} | {'seq. avg':>9} | {'us/look-up':>10}")
    rows = []
    for n in (1000, 1023, 1024, 10_000, 100_000, 1_000_000):
        ids = sorted(rng.sample(range(5_000_000, 50_000_000), n))
        ids = [2 * x for x in ids]                      # even parcel IDs; odd numbers are absent
        absent = [ids[0] - 1] + [x + 1 for x in ids]    # one absent ID inside each of the n + 1 gaps
        t0 = time.perf_counter()
        succ = []
        for i, key in enumerate(ids):
            idx, probes = binary_search(ids, key)
            assert idx == i
            succ.append(probes)
        t_succ = (time.perf_counter() - t0) / n * 1e6
        unsucc = []
        for key in absent:
            idx, probes = binary_search(ids, key)
            assert idx == -1
            unsucc.append(probes)
        th_s, th_u = exact_bs_averages(n)
        avg_s, avg_u = sum(succ) / n, sum(unsucc) / (n + 1)
        worst = floor_log2(n) + 1
        print(f"{n:>9,} | {max(succ):>8} {max(unsucc):>10} {worst:>13} | {avg_s:>8.3f} {th_s:>7.3f} | "
              f"{avg_u:>10.3f} {th_u:>7.3f} | {(n + 1) / 2:>9,.1f} | {t_succ:>10.2f}")
        rows.append([n, max(succ), min(unsucc), max(unsucc), worst, round(avg_s, 4), round(th_s, 4),
                     round(avg_u, 4), round(th_u, 4), (n + 1) / 2, n, round(t_succ, 3)])
    print("   theory = exact averages of the balanced decision tree: (I + n)/n and (I + 2n)/(n + 1), "
          "I = sum floor(log2 i)")
    write_csv("q1_binary_search.csv",
              ["n", "max_probes_successful", "min_probes_unsuccessful", "max_probes_unsuccessful",
               "formula_floor_log2n_plus_1", "avg_probes_successful", "theory_avg_successful",
               "avg_probes_unsuccessful", "theory_avg_unsuccessful", "sequential_avg_successful",
               "sequential_unsuccessful", "time_us_per_successful_lookup"], rows)


def experiment_designed_cases(rng):
    """Student A, Part B: deliberately designed successful and unsuccessful look-ups at four manifest sizes."""
    print("\n[5] Designed look-up cases (probes = three-way comparisons; bound = floor(log2 n) + 1)")
    cases = ["first", "middle", "last", "deepest", "below min", "in a gap", "above max"]
    print(f"{'n':>9} | " + " ".join(f"{c:>9}" for c in cases) + f" | {'bound':>5}")
    rows = []
    for n in (16, 1000, 1024, 1_000_000):
        ids = [2 * x for x in sorted(rng.sample(range(5_000_000, 50_000_000), n))]
        probes_all = [binary_search(ids, k)[1] for k in ids]    # deepest present key: most probes
        deep = ids[probes_all.index(max(probes_all))]
        keys = [ids[0], ids[(n - 1) // 2], ids[-1], deep,
                ids[0] - 1, ids[n // 2] + 1, ids[-1] + 1]
        counts = []
        for case, key in zip(cases, keys):
            idx, probes = binary_search(ids, key)
            assert (idx >= 0) == (case in ("first", "middle", "last", "deepest"))
            counts.append(probes)
            rows.append([n, case, key, idx, probes, floor_log2(n) + 1])
        print(f"{n:>9,} | " + " ".join(f"{c:>9}" for c in counts) + f" | {floor_log2(n) + 1:>5}")
    write_csv("q1_designed_cases.csv", ["n", "case", "key", "index", "probes", "bound_floor_log2n_plus_1"], rows)


def main():
    sys.setrecursionlimit(10_000)
    rng = random.Random(SEED)
    print("=" * 118)
    print("Q1 EXPERIMENTS - Max-Min (flight temperature logs) and Binary Search (parcel manifests); seed 42")
    print("=" * 118)
    experiment_maxmin_growth(rng)
    experiment_maxmin_inputs(rng)
    experiment_maxmin_sweep(rng)
    experiment_binary_search(rng)
    experiment_designed_cases(rng)
    print("\nCSV files written to results/: q1_maxmin_growth, q1_maxmin_inputs, q1_maxmin_sweep, q1_binary_search,"
          " q1_designed_cases")


if __name__ == "__main__":
    main()
