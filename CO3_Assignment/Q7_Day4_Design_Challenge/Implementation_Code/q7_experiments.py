"""Q7 experiments - the original quick sort, both independent proposals and the joint designs on IDENTICAL datasets.

Variants
  Baseline   Q2's textbook quick sort (Lomuto, last-element pivot)          - imported from Q2
  A          Student A: median-of-3 + Hoare partition + smaller-part recursion - Student_A_Initial_Design
  B          Student B: random pivot (seed 42) + Dijkstra 3-way + insertion <= 16 - Student_B_Initial_Design
  Joint-v1   first joint attempt: A's pivot + B's Dijkstra partition (+ cutoff, guard) - rejected
  Joint      final joint design: median-of-3 + fat partition + insertion <= 16 + depth budget/heapsort
Datasets (n = 1,000 / 2,000 / 4,000 / 8,000; deadlines in seconds after 06:00, seed 42)
  random, sorted, reverse, slots (64 distinct 15-minute slots), all-equal,
  killer-A / killer-B / killer-J: adversarial inputs built by McIlroy's adversary against A, B (seed 42)
  and the Joint design without its guard (q7_adversary.py).
Writes results/q7_results.csv, q7_guard.csv, q7_seed.csv, q7_large.csv.
Run:  py q7_experiments.py      (about 3-5 minutes)
"""
import csv
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
Q7 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(Q7, "Student_A_Initial_Design"))
sys.path.insert(0, os.path.join(Q7, "Student_B_Initial_Design"))
sys.path.insert(0, os.path.join(os.path.dirname(Q7), "Q2_MergeSort_QuickSort", "Implementation_Code"))

from proposal_a_median3_hoare import quick_sort_a  # noqa: E402
from proposal_b_threeway_cutoff import quick_sort_b  # noqa: E402
from q2_sorting import quick_sort  # noqa: E402
from q7_adversary import make_killer  # noqa: E402
from q7_introsort_hybrid import hybrid_sort, hybrid_sort_unguarded, hybrid_sort_v1  # noqa: E402

sys.setrecursionlimit(200_000)
RESULTS = os.path.join(HERE, "results")
SIZES = (1000, 2000, 4000, 8000)
DAY, SLOT = 16 * 3600, 900
VARIANTS = {"Baseline": lambda a: quick_sort(a, "last"), "A": quick_sort_a, "B": quick_sort_b,
            "Joint-v1": hybrid_sort_v1, "Joint": hybrid_sort}
NATURAL = ("random", "sorted", "reverse", "slots", "all-equal")
DATASETS = NATURAL + ("killer-A", "killer-B", "killer-J")


def make_datasets(n, rng):
    base = [rng.randrange(DAY) for _ in range(n)]
    data = {"random": base, "sorted": sorted(base), "reverse": sorted(base, reverse=True),
            "slots": [rng.randrange(DAY // SLOT) * SLOT for _ in range(n)], "all-equal": [9 * SLOT] * n}
    data["killer-A"] = make_killer(quick_sort_a, n)[0]
    data["killer-B"] = make_killer(quick_sort_b, n)[0]
    data["killer-J"] = make_killer(hybrid_sort_unguarded, n)[0]
    return data


def run(fn, data):
    """Sort a copy, verify against sorted(), return (stats, ms); fast runs repeated 3 times (minimum)."""
    best, stats = float("inf"), None
    for _ in range(3):
        a = list(data)
        t0 = time.perf_counter()
        st = fn(a)
        t = (time.perf_counter() - t0) * 1000
        assert a == sorted(data)
        stats, best = st, min(best, t)
        if t > 200:
            break
    return stats, best


def table(title, rows_by_ds, fmt, width=11):
    print(f"\n{title}")
    print(f"{'dataset':>10} | " + " ".join(f"{v:>{width}}" for v in VARIANTS))
    for ds in DATASETS:
        print(f"{ds:>10} | " + " ".join(format(x, fmt) for x in rows_by_ds[ds]))


def main():
    rng = random.Random(42)
    t_start = time.perf_counter()
    print("=" * 104)
    print("Q7 EXPERIMENTS - original quick sort vs proposal A vs proposal B vs joint designs (identical datasets)")
    print("=" * 104)
    rows, res = [], {}
    for n in SIZES:
        data = make_datasets(n, rng)
        for ds in DATASETS:
            for name, fn in VARIANTS.items():
                st, t = run(fn, data[ds])
                hs = getattr(st, "heapsort_fallbacks", 0)
                res[(name, ds, n)] = (st, t)
                rows.append([name, ds, n, st.comparisons, st.moves, st.max_depth, hs, round(t, 2),
                             round(n * math.log2(n)), round(st.comparisons / (n * math.log2(n)), 3)])
    n = SIZES[-1]
    nlg = n * math.log2(n)
    table(f"[1] Comparisons at n = {n:,} (n log2 n = {nlg:,.0f}; n(n-1)/2 = {n * (n - 1) // 2:,})",
          {ds: [res[(v, ds, n)][0].comparisons for v in VARIANTS] for ds in DATASETS}, ">11,")
    table(f"[2] Comparisons / (n log2 n) at n = {n:,}",
          {ds: [res[(v, ds, n)][0].comparisons / nlg for v in VARIANTS] for ds in DATASETS}, ">11.2f")
    table(f"[3] Moves (element writes; a swap = 2) at n = {n:,}",
          {ds: [res[(v, ds, n)][0].moves for v in VARIANTS] for ds in DATASETS}, ">11,")
    table(f"[4] Maximum recursion depth at n = {n:,} (log2 n = {math.log2(n):.1f})",
          {ds: [res[(v, ds, n)][0].max_depth for v in VARIANTS] for ds in DATASETS}, ">11,")
    table(f"[5] Time in ms at n = {n:,} (minimum of 3 runs; single run if > 200 ms)",
          {ds: [res[(v, ds, n)][1] for v in VARIANTS] for ds in DATASETS}, ">11.1f")

    print("\n[6] Joint design: comparisons / (n log2 n) and heapsort fallbacks at every size")
    print(f"{'dataset':>10} | " + " ".join(f"{f'n={s:,}':>13}" for s in SIZES))
    for ds in DATASETS:
        cells = [f"{res[('Joint', ds, s)][0].comparisons / (s * math.log2(s)):>7.2f} ({res[('Joint', ds, s)][0].heapsort_fallbacks})"
                 for s in SIZES]
        print(f"{ds:>10} | " + " ".join(f"{c:>13}" for c in cells))

    print("\n[7] Why the depth budget is needed: Joint without and with the guard on its own adversarial input")
    print(f"{'n':>6} | {'unguarded comps':>15} {'/ n lg n':>8} {'time ms':>8} | {'guarded comps':>13} {'/ n lg n':>8} "
          f"{'time ms':>8} {'fallbacks':>9}")
    guard_rows = []
    for s in SIZES:
        killer = make_killer(hybrid_sort_unguarded, s)[0]
        su, tu = run(hybrid_sort_unguarded, killer)
        sg, tg = run(hybrid_sort, killer)
        sl = s * math.log2(s)
        print(f"{s:>6,} | {su.comparisons:>15,} {su.comparisons / sl:>8.2f} {tu:>8.1f} | {sg.comparisons:>13,} "
              f"{sg.comparisons / sl:>8.2f} {tg:>8.1f} {sg.heapsort_fallbacks:>9}")
        guard_rows.append([s, su.comparisons, su.max_depth, round(tu, 2), sg.comparisons, sg.max_depth,
                           sg.heapsort_fallbacks, round(tg, 2)])

    print("\n[8] Proposal B on its adversarial input: the random pivot protects only while the seed is secret")
    print(f"{'n':>6} | {'B seed 42 (attacked)':>21} {'depth':>6} | {'B seed 7':>9} {'depth':>6}")
    seed_rows = []
    for s in SIZES:
        killer = make_killer(quick_sort_b, s)[0]
        s42, _ = run(quick_sort_b, killer)
        s7, _ = run(lambda a: quick_sort_b(a, seed=7), killer)
        print(f"{s:>6,} | {s42.comparisons:>21,} {s42.max_depth:>6,} | {s7.comparisons:>9,} {s7.max_depth:>6}")
        seed_rows.append([s, s42.comparisons, s42.max_depth, s7.comparisons, s7.max_depth])

    print("\n[9] Large batch, n = 100,000 (natural inputs only): comparisons / (n log2 n) | time ms")
    big_rng = random.Random(4242)
    base = [big_rng.randrange(DAY) for _ in range(100_000)]
    big = {"random": base, "sorted": sorted(base), "reverse": sorted(base, reverse=True),
           "slots": [big_rng.randrange(64) * SLOT for _ in range(100_000)], "all-equal": [9 * SLOT] * 100_000}
    large_rows = []
    lgb = 100_000 * math.log2(100_000)
    names = [v for v in VARIANTS if v != "Baseline"]
    print(f"{'dataset':>10} | " + " ".join(f"{v:>17}" for v in names))
    for ds, data in big.items():
        cells = []
        for v in names:
            st, t = run(VARIANTS[v], data)
            cells.append(f"{st.comparisons / lgb:>6.2f} | {t:>8.1f}")
            large_rows.append([v, ds, 100_000, st.comparisons, round(st.comparisons / lgb, 3), st.moves,
                               st.max_depth, getattr(st, "heapsort_fallbacks", 0), round(t, 1)])
        print(f"{ds:>10} | " + " ".join(f"{c:>17}" for c in cells))

    print("\n[10] Design objectives of the joint design (all sizes, all datasets above)")
    joint = [r for r in rows if r[0] == "Joint"]
    nat = max(r[9] for r in joint if r[1] in NATURAL)
    adv = max(r[9] for r in joint if r[1] not in NATURAL)
    depth_ok = all(r[5] <= math.log2(r[2]) for r in joint)
    eq = max(r[3] - 2 * r[2] for r in joint if r[1] == "all-equal")
    slots_ok = all(res[("Joint", "slots", s)][0].comparisons <= res[("Joint", "random", s)][0].comparisons for s in SIZES)
    print(f"   O1 natural inputs <= 1.5 n lg n          : max {nat:.2f} n lg n  -> {'met' if nat <= 1.5 else 'NOT met'}")
    print(f"   O2 adversarial inputs <= 6 n lg n        : max {adv:.2f} n lg n  -> {'met' if adv <= 6 else 'NOT met'}")
    print(f"   O3 recursion depth <= log2 n             : {'met' if depth_ok else 'NOT met'}")
    print(f"   O4 all-equal <= 2n + 3, slots <= random  : all-equal 2n{eq:+d}, slots <= random: "
          f"{'met' if eq <= 3 and slots_ok else 'NOT met'}")
    print(f"   O5 every output equal to sorted()        : met ({len(rows) + 2 * len(SIZES) * 2 + len(large_rows)} runs "
          f"checked)")
    print(f"\nTotal run time {time.perf_counter() - t_start:.0f} s. CSV files written to results/.")

    os.makedirs(RESULTS, exist_ok=True)
    for name, header, data in (
            ("q7_results.csv", ["variant", "dataset", "n", "comparisons", "moves", "max_depth", "heapsort_fallbacks",
                                "time_ms", "n_log2_n", "comparisons_per_nlog2n"], rows),
            ("q7_guard.csv", ["n", "unguarded_comparisons", "unguarded_depth", "unguarded_ms", "guarded_comparisons",
                              "guarded_depth", "heapsort_fallbacks", "guarded_ms"], guard_rows),
            ("q7_seed.csv", ["n", "B_seed42_comparisons", "B_seed42_depth", "B_seed7_comparisons", "B_seed7_depth"],
             seed_rows),
            ("q7_large.csv", ["variant", "dataset", "n", "comparisons", "comparisons_per_nlog2n", "moves", "max_depth",
                              "heapsort_fallbacks", "time_ms"], large_rows)):
        with open(os.path.join(RESULTS, name), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(data)


if __name__ == "__main__":
    main()
