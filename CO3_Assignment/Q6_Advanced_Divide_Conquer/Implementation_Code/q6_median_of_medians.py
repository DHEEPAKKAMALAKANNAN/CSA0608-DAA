"""Q6(a) - Median of Medians: deterministic linear-time selection (CSA06 DAA, Assignment 3 - CO3).

Problem (SLA reporting): report the median and the 90th-percentile delivery time of a batch of n deliveries
(n up to 1,000,000) with a GUARANTEED worst-case time.  Selection = find the k-th smallest of n values.

Methods (all pure Python, every element comparison counted; all use the same three-way partition, which costs one
comparison for an element smaller than the pivot and two otherwise, so only the PIVOT RULE differs):
  sort_then_pick       hand-written merge sort, then a[k]                                     Theta(n log n)
  quickselect_random   random pivot                                expected Theta(n), worst case Theta(n^2)
  quickselect_first    first element as pivot (deterministic)      Theta(n^2) on sorted input
  mom_select           Median of Medians, groups of g (g = 3, 5, 7):
      DIVIDE   into ceil(n/g) groups of g, sort each group (insertion sort) and take its median;
      CONQUER  (1) select the median of these medians recursively -> pivot p;
      COMBINE  partition around p; at least ~3n/10 elements (g = 5) lie on each side of p, so
      CONQUER  (2) continues in ONE part of size <= 7n/10 + 6.
      T(n) <= T(ceil(n/5)) + T(7n/10 + 6) + Theta(n)  ->  Theta(n)   (g = 3 gives Theta(n log n)).

Run:  py -3 q6_median_of_medians.py     (demo + experiments; writes ../Median_of_Medians/results/*.csv)
"""
import csv
import math
import os
import random
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "Median_of_Medians", "results")


class Counter:
    """Comparison counter of one selection run (plus diagnostics of Median of Medians)."""

    def __init__(self):
        self.comparisons = 0
        self.rounds = 0             # partition rounds of the main (one-sided) recursion
        self.max_keep = 0.0         # largest fraction of a level kept for the next round (n >= 100), g = 5: <= 0.7 + 6/n


# ----------------------------------------------------------------------------------------------- building blocks
def partition3(a, pivot):
    """Split list a into (less, equal, greater) around pivot. Returns the three lists and the comparisons made."""
    less, equal, greater = [], [], []
    comps = 0
    for x in a:
        if x < pivot:
            less.append(x)
            comps += 1
        elif x > pivot:
            greater.append(x)
            comps += 2
        else:
            equal.append(x)
            comps += 2
    return less, equal, greater, comps


def insertion_sort_count(a):
    """Sort the small list a in place by insertion sort; return the number of comparisons made."""
    comps = 0
    for s in range(1, len(a)):
        key, t = a[s], s - 1
        while t >= 0:
            comps += 1
            if a[t] > key:
                a[t + 1] = a[t]
                t -= 1
            else:
                break
        a[t + 1] = key
    return comps


def merge_sort_count(a, counter):
    """Return a sorted copy of a (top-down merge sort); comparisons added to counter.comparisons."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    left, right = merge_sort_count(a[:mid], counter), merge_sort_count(a[mid:], counter)
    out, i, j, comps = [], 0, 0, 0
    nl, nr = len(left), len(right)
    while i < nl and j < nr:
        comps += 1
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    counter.comparisons += comps
    return out


# ----------------------------------------------------------------------------------------------- selection methods
def sort_then_pick(a, k, counter):
    """k-th smallest (0-based) by sorting everything first: Theta(n log n) comparisons."""
    return merge_sort_count(a, counter)[k]


def record_keep(keeps, n, kept):
    """Optional instrumentation: remember (size of this round, size kept for the next round)."""
    if keeps is not None:
        keeps.append((n, kept))


def quickselect_random(a, k, counter, rng, keeps=None):
    """k-th smallest with a uniformly random pivot (expected linear, no worst-case guarantee)."""
    while True:
        if len(a) == 1:
            return a[0]
        pivot = a[rng.randrange(len(a))]
        less, equal, greater, comps = partition3(a, pivot)
        counter.comparisons += comps
        counter.rounds += 1
        if k < len(less):
            record_keep(keeps, len(a), len(less))
            a = less
        elif k < len(less) + len(equal):
            record_keep(keeps, len(a), 0)
            return pivot
        else:
            record_keep(keeps, len(a), len(greater))
            k -= len(less) + len(equal)
            a = greater


def quickselect_first(a, k, counter, keeps=None):
    """k-th smallest with the FIRST element as pivot (deterministic; quadratic on sorted input)."""
    while True:
        if len(a) == 1:
            return a[0]
        less, equal, greater, comps = partition3(a, a[0])
        counter.comparisons += comps
        counter.rounds += 1
        if k < len(less):
            record_keep(keeps, len(a), len(less))
            a = less
        elif k < len(less) + len(equal):
            record_keep(keeps, len(a), 0)
            return equal[0]                              # equal always holds the pivot
        else:
            record_keep(keeps, len(a), len(greater))
            k -= len(less) + len(equal)
            a = greater


def mom_select(a, k, counter, group=5, keeps=None):
    """k-th smallest (0-based) of list a by the Median-of-Medians algorithm with groups of `group` elements."""
    while True:
        n = len(a)
        if n <= group:                                   # small problem: sort directly
            s = list(a)
            counter.comparisons += insertion_sort_count(s)
            return s[k]
        # DIVIDE: groups of `group`, sort each group, collect the group medians
        medians, comps = [], 0
        for i in range(0, n, group):
            grp = a[i:i + group]
            comps += insertion_sort_count(grp)
            medians.append(grp[(len(grp) - 1) // 2])
        counter.comparisons += comps
        # CONQUER (1): the pivot is the median of the medians, found by the same algorithm
        pivot = mom_select(medians, (len(medians) - 1) // 2, counter, group)   # (no keeps: inner recursion)
        # COMBINE: three-way partition around the pivot
        less, equal, greater, comps = partition3(a, pivot)
        counter.comparisons += comps
        counter.rounds += 1
        # CONQUER (2): continue in the one part that contains rank k (tail recursion written as a loop)
        if k < len(less):
            kept = less
        elif k < len(less) + len(equal):
            record_keep(keeps, n, 0)
            return pivot
        else:
            k -= len(less) + len(equal)
            kept = greater
        record_keep(keeps, n, len(kept))
        if n >= 100:
            counter.max_keep = max(counter.max_keep, len(kept) / n)
        a = kept


# ----------------------------------------------------------------------------------------------- datasets
def delivery_times(n, seed=42):
    """n delivery times in seconds (ms resolution): 8 min + Gamma(2, 600 s) -> long right tail, almost all distinct."""
    rng = random.Random(seed)
    return [round(480.0 + rng.gammavariate(2.0, 600.0), 3) for _ in range(n)]


def make_input(kind, n):
    """'random' delivery times, the same times 'sorted', or 'duplicates' (whole minutes: < 100 distinct values)."""
    base = delivery_times(n)
    if kind == "sorted":
        return sorted(base)
    if kind == "duplicates":
        return [int(t // 60) for t in base]
    return base


SIZES = [1_000, 10_000, 100_000, 1_000_000]
INPUTS = ["random", "sorted", "duplicates"]
QS_SEEDS = [1, 2, 3, 4, 5]
WORST_SIZES = [1_000, 2_000, 4_000]


def run_method(name, a, k):
    """Run one selection method on a copy of a; return (value, Counter, seconds)."""
    c = Counter()
    t0 = time.perf_counter()
    if name == "sort_then_pick":
        v = sort_then_pick(a, k, c)
    elif name.startswith("mom_g"):
        v = mom_select(a, k, c, int(name[-1]))
    elif name == "quickselect_first":
        v = quickselect_first(a, k, c)
    else:
        raise ValueError(name)
    return v, c, time.perf_counter() - t0


def main():
    os.makedirs(RESULTS, exist_ok=True)
    print("=" * 112)
    print("Q6(a)  Median of Medians - SLA report of one batch of 10,001 deliveries (demo)")
    print("=" * 112)
    batch = delivery_times(10_001, seed=7)
    k50, k90 = (len(batch) - 1) // 2, math.ceil(0.9 * len(batch)) - 1
    ref = sorted(batch)
    for label, k in (("median", k50), ("90th percentile", k90)):
        c = Counter()
        v = mom_select(batch, k, c)
        print(f"  {label:<16} rank k = {k:>5}: {v:9.3f} s = {v / 60:6.2f} min   comparisons = {c.comparisons:>7,} "
              f"({c.comparisons / len(batch):.2f} n)   correct = {v == ref[k]}")

    rows = []
    methods = ["sort_then_pick", "qs_random", "mom_g3", "mom_g5", "mom_g7"]
    table = {}
    for kind in INPUTS:
        for n in SIZES:
            a = make_input(kind, n)
            k = (n - 1) // 2
            truth = sorted(a)[k]
            for m in methods:
                if m == "qs_random":
                    comps, times, ok = [], [], True
                    for s in QS_SEEDS:
                        c = Counter()
                        t0 = time.perf_counter()
                        v = quickselect_random(a, k, c, random.Random(s))
                        times.append(time.perf_counter() - t0)
                        comps.append(c.comparisons)
                        ok &= v == truth
                    rows.append({"input": kind, "n": n, "method": "qs_random_mean", "comparisons": round(sum(comps) / 5),
                                 "comparisons_per_n": round(sum(comps) / 5 / n, 3), "time_s": round(sum(times) / 5, 5),
                                 "max_keep_fraction": "", "correct": ok})
                    rows.append({"input": kind, "n": n, "method": "qs_random_max", "comparisons": max(comps),
                                 "comparisons_per_n": round(max(comps) / n, 3), "time_s": round(max(times), 5),
                                 "max_keep_fraction": "", "correct": ok})
                    table[(kind, n, "qs_random_mean")] = (sum(comps) / 5, sum(times) / 5)
                    table[(kind, n, "qs_random_max")] = (max(comps), max(times))
                else:
                    v, c, t = run_method(m, a, k)
                    rows.append({"input": kind, "n": n, "method": m, "comparisons": c.comparisons,
                                 "comparisons_per_n": round(c.comparisons / n, 3), "time_s": round(t, 5),
                                 "max_keep_fraction": round(c.max_keep, 4) if m.startswith("mom") else "",
                                 "correct": v == truth})
                    table[(kind, n, m)] = (c.comparisons, t)
    with open(os.path.join(RESULTS, "q6_mom_comparisons.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    cols = ["sort_then_pick", "qs_random_mean", "qs_random_max", "mom_g3", "mom_g5", "mom_g7"]
    heads = ["sort+pick", "QS rand mean", "QS rand max", "MoM g=3", "MoM g=5", "MoM g=7"]
    print("\nElement comparisons to find the median (k = (n-1)/2); QS = randomised Quickselect over 5 seeds")
    print(f"{'input':<11}{'n':>10}" + "".join(f"{h:>15}" for h in heads))
    print("-" * 111)
    for kind in INPUTS:
        for n in SIZES:
            print(f"{kind:<11}{n:>10,}" + "".join(f"{round(table[(kind, n, c)][0]):>15,}" for c in cols))
    print("\nComparisons per element (comparisons / n)  -  constant = linear time; log2 n shown for reference")
    print(f"{'input':<11}{'n':>10}{'log2 n':>8}" + "".join(f"{h:>15}" for h in heads))
    print("-" * 111)
    for kind in INPUTS:
        for n in SIZES:
            print(f"{kind:<11}{n:>10,}{math.log2(n):>8.1f}" +
                  "".join(f"{table[(kind, n, c)][0] / n:>15.2f}" for c in cols))
    print("\nTime in seconds (single run; QS = mean of 5 seeds)")
    print(f"{'input':<11}{'n':>10}" + "".join(f"{h:>15}" for h in heads))
    print("-" * 111)
    for kind in INPUTS:
        for n in SIZES:
            print(f"{kind:<11}{n:>10,}" + "".join(f"{table[(kind, n, c)][1]:>15.4f}" for c in cols))
    keep = max(r["max_keep_fraction"] for r in rows if r["method"] == "mom_g5")
    print(f"\nLargest fraction of the elements kept for the next round by MoM g=5 (n >= 100): {keep} (bound 0.7 + 6/n)")
    print(f"All {len(rows)} results equal sorted(a)[k]: {all(r['correct'] for r in rows)}")

    # worst case of a deterministic pivot rule: first element as pivot on sorted input
    wrows = []
    print("\nDeterministic first-element pivot on SORTED, DISTINCT input (its worst case) vs Median of Medians g=5")
    print(f"{'n':>8}{'QS first: comparisons':>24}{'formula 2(k+1)n - k(k+1)':>27}{'MoM g=5':>12}{'QS first s':>12}"
          f"{'MoM g=5 s':>11}")
    for n in WORST_SIZES:
        a = [600.0 + 0.5 * i for i in range(n)]          # strictly increasing (sorted, all distinct) delivery times
        k = (n - 1) // 2
        v1, c1, t1 = run_method("quickselect_first", a, k)
        v2, c2, t2 = run_method("mom_g5", a, k)
        formula = 2 * (k + 1) * n - k * (k + 1)
        wrows.append({"n": n, "input": "sorted", "qs_first_comparisons": c1.comparisons, "formula": formula,
                      "mom_g5_comparisons": c2.comparisons, "qs_first_time_s": round(t1, 5),
                      "mom_g5_time_s": round(t2, 5), "correct": v1 == v2 == a[k]})
        print(f"{n:>8,}{c1.comparisons:>24,}{formula:>27,}{c2.comparisons:>12,}{t1:>12.4f}{t2:>11.4f}")
    with open(os.path.join(RESULTS, "q6_mom_worstcase.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(wrows[0].keys()))
        w.writeheader()
        w.writerows(wrows)
    print("CSV written: Median_of_Medians/results/q6_mom_comparisons.csv, q6_mom_worstcase.csv")


if __name__ == "__main__":
    main()
