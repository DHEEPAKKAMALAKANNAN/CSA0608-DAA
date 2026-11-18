"""SwiftLogix - Module 2: Quick Sort for ranking order-priority scores in the dispatch queue.

Problem
    Every dispatch cycle the platform ranks the open orders (production workload: 2,000,000 orders)
    by their priority score (integer 0-100, so the data are DUPLICATE-HEAVY) entirely in memory.
    The ranking must be fast and in place; stability is not required (ties are broken by a
    secondary key in production).

Divide-and-conquer design (baseline, as specified in Part 2)
    Pivot rule      : the LAST element of the sub-array          Partition scheme: Lomuto
    DIVIDE : partition A[lo..hi] around the pivot -> pivot lands at its final index p
    CONQUER: quick-sort A[lo..p-1] and A[p+1..hi] recursively
    COMBINE: nothing - the array is sorted in place
    Basic operation: comparison of an element with the pivot.
    Average 2n ln n ~ 1.39 n lg n comparisons; worst case n(n-1)/2 (sorted or all-equal input).

Improved variants measured in Part 5: median-of-three pivot, random pivot, 3-way (Dijkstra)
partitioning and the final introsort-style hybrid (median-of-three + 3-way + insertion cutoff 16 +
heap-sort fallback + recursion on the smaller side).

Run:  py -3 quick_sort.py         partition trace on the given sample dataset + verification
"""
import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "Supporting_Files" / "datasets" / "m2_priority_scores_sample.csv"
sys.setrecursionlimit(20000)                     # the baseline recurses n deep on sorted input


class OpCounter:
    """Counts pivot comparisons, swaps, partition calls, the deepest recursion level and heap-sort fallbacks."""

    def __init__(self):
        self.comparisons = self.swaps = self.partitions = self.max_depth = self.fallbacks = 0


# ----------------------------------------------------------------------------- partition schemes
def partition_lomuto(a, lo, hi, c):
    """Lomuto partition around pivot a[hi]; returns the pivot's final index."""
    pivot = a[hi]
    i = lo - 1
    for j in range(lo, hi):
        c.comparisons += 1                       # BASIC OPERATION
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
            c.swaps += 1
    a[i + 1], a[hi] = a[hi], a[i + 1]
    c.swaps += 1
    return i + 1


def partition_3way(a, lo, hi, c):
    """Dijkstra 3-way partition around v = a[lo]: returns (lt, gt) with a[lt..gt] == v."""
    v = a[lo]
    lt, i, gt = lo, lo + 1, hi
    while i <= gt:
        c.comparisons += 1
        if a[i] < v:
            a[lt], a[i] = a[i], a[lt]; c.swaps += 1
            lt += 1; i += 1
        else:
            c.comparisons += 1
            if a[i] > v:
                a[i], a[gt] = a[gt], a[i]; c.swaps += 1
                gt -= 1
            else:
                i += 1
    return lt, gt


def median_of_three(a, lo, hi, c):
    """Order a[lo], a[mid], a[hi]; return mid (the index of the median of the three)."""
    mid = (lo + hi) // 2
    for x, y in ((lo, mid), (mid, hi), (lo, mid)):
        c.comparisons += 1
        if a[y] < a[x]:
            a[x], a[y] = a[y], a[x]; c.swaps += 1
    return mid


def median_of_random_three(a, lo, hi, c, rng):
    """Index of the median of three elements sampled at random positions (no swaps, 2-3 comparisons)."""
    i, j, k = rng.randint(lo, hi), rng.randint(lo, hi), rng.randint(lo, hi)
    c.comparisons += 1
    if a[i] > a[j]:
        i, j = j, i                              # now a[i] <= a[j]
    c.comparisons += 1
    if a[k] >= a[j]:
        return j                                 # a[i] <= a[j] <= a[k]
    c.comparisons += 1
    return k if a[k] > a[i] else i


# ----------------------------------------------------------------------------- baseline + simple variants
def quick_sort(a, pivot="last", counter=None, trace=None, seed=42):
    """In-place quick sort with Lomuto partitioning. pivot = 'last' (baseline), 'median3' or 'random'."""
    c = counter if counter is not None else OpCounter()
    rng = random.Random(seed)

    def sort(lo, hi, depth):
        c.max_depth = max(c.max_depth, depth)
        if lo >= hi:                                             # 0 or 1 element: sorted
            return
        if pivot == "median3" and hi - lo >= 2:
            m = median_of_three(a, lo, hi, c)
            a[m], a[hi] = a[hi], a[m]; c.swaps += 1             # median becomes the pivot a[hi]
        elif pivot == "random":
            r = rng.randint(lo, hi)
            a[r], a[hi] = a[hi], a[r]; c.swaps += 1
        before = (c.comparisons, c.swaps)
        p = partition_lomuto(a, lo, hi, c)                       # DIVIDE
        c.partitions += 1
        if trace:
            trace(depth, lo, hi, p, a, c.comparisons - before[0], c.swaps - before[1])
        sort(lo, p - 1, depth + 1)                               # CONQUER left (<= pivot)
        sort(p + 1, hi, depth + 1)                               # CONQUER right (> pivot)
        # COMBINE: nothing to do

    sort(0, len(a) - 1, 0)
    return a


def quick_sort_3way(a, counter=None, seed=42):
    """Random pivot + Dijkstra 3-way partitioning (equal keys are finished in one pass)."""
    c = counter if counter is not None else OpCounter()
    rng = random.Random(seed)

    def sort(lo, hi, depth):
        c.max_depth = max(c.max_depth, depth)
        if lo >= hi:
            return
        r = rng.randint(lo, hi)
        a[lo], a[r] = a[r], a[lo]; c.swaps += 1
        lt, gt = partition_3way(a, lo, hi, c)
        c.partitions += 1
        sort(lo, lt - 1, depth + 1)
        sort(gt + 1, hi, depth + 1)

    sort(0, len(a) - 1, 0)
    return a


# ----------------------------------------------------------------------------- final design: hybrid
def _insertion(a, lo, hi, c):
    for i in range(lo + 1, hi + 1):
        x, j = a[i], i - 1
        while j >= lo:
            c.comparisons += 1
            if a[j] > x:
                a[j + 1] = a[j]; c.swaps += 1; j -= 1
            else:
                break
        a[j + 1] = x


def _heap_sort(a, lo, hi, c):
    """Heap sort of a[lo..hi] (fallback when the recursion budget is exhausted)."""
    n = hi - lo + 1

    def sift(root, end):
        while 2 * root + 1 < end:
            child = 2 * root + 1
            if child + 1 < end:
                c.comparisons += 1
                if a[lo + child] < a[lo + child + 1]:
                    child += 1
            c.comparisons += 1
            if a[lo + root] < a[lo + child]:
                a[lo + root], a[lo + child] = a[lo + child], a[lo + root]; c.swaps += 1
                root = child
            else:
                return

    for start in range(n // 2 - 1, -1, -1):
        sift(start, n)
    for end in range(n - 1, 0, -1):
        a[lo], a[lo + end] = a[lo + end], a[lo]; c.swaps += 1
        sift(0, end)


def quick_sort_hybrid(a, counter=None, cutoff=16, depth_limit=None, pivot_sample="random", seed=42):
    """Introsort-style quick sort: median-of-3 + 3-way partition + insertion cutoff + heap-sort fallback.

    pivot_sample='random': median of three randomly placed elements (final design);
    pivot_sample='fixed' : median of a[lo], a[mid], a[hi] (kept to show why it was rejected).
    Recursing only on the smaller part bounds the stack depth by lg n; the depth budget 2*floor(lg n)
    bounds the running time by O(n log n) even for adversarial inputs.
    """
    c = counter if counter is not None else OpCounter()
    rng = random.Random(seed)
    n = len(a)
    if depth_limit is None:
        depth_limit = 2 * max(n, 1).bit_length()

    def sort(lo, hi, budget, depth):
        c.max_depth = max(c.max_depth, depth)
        while hi - lo + 1 > cutoff:
            if budget == 0:
                c.fallbacks += 1
                _heap_sort(a, lo, hi, c)
                return
            budget -= 1
            if pivot_sample == "random":
                m = median_of_random_three(a, lo, hi, c, rng)
            else:
                m = median_of_three(a, lo, hi, c)
            a[lo], a[m] = a[m], a[lo]; c.swaps += 1
            lt, gt = partition_3way(a, lo, hi, c)
            c.partitions += 1
            if lt - lo < hi - gt:                                # recurse on the smaller side,
                sort(lo, lt - 1, budget, depth + 1)              # loop on the larger side
                lo = gt + 1
            else:
                sort(gt + 1, hi, budget, depth + 1)
                hi = lt - 1
        _insertion(a, lo, hi, c)

    sort(0, n - 1, depth_limit, 0)
    return a


# ----------------------------------------------------------------------------- demo on the sample
def load_orders(path=SAMPLE):
    with open(path, newline="", encoding="utf-8") as fh:
        return [(r["order_id"], int(r["priority_score"])) for r in csv.DictReader(fh)]


def fmt(a, lo, hi, p):
    """Array state: active range between | |, pivot in [ ]."""
    cells = []
    for k, x in enumerate(a):
        s = f"[{x:>2}]" if k == p else f" {x:>2} "
        if k == lo:
            s = "|" + s
        if k == hi:
            s = s + "|"
        cells.append(s)
    return "".join(cells)


def trace_printer(depth, lo, hi, p, a, comps, swaps):
    print(f"  {depth:>5}  [{lo:>2}..{hi:>2}]  {a[p]:>5}  {comps:>3}  {swaps:>5}  {p:>3}   {fmt(a, lo, hi, p)}")


def run_demo():
    orders = load_orders()
    scores = [s for _, s in orders]
    n = len(scores)
    print("=" * 104)
    print(f"SwiftLogix M2 - quick sort of order-priority scores (given sample: {n} orders)")
    print("=" * 104)
    print("Orders  : " + "  ".join(f"{o}:{s}" for o, s in orders))
    print("Pivot rule = last element of the sub-array, partition scheme = Lomuto")
    print("\nDivide (partition) trace - array after each partition, active range in | |, pivot in [ ]")
    print(f"  {'depth':>5}  {'range':<8}  {'pivot':>5}  {'cmp':>3}  {'swaps':>5}  {'pos':>3}   array")
    print(f"  {'':>5}  {'':<8}  {'':>5}  {'':>3}  {'':>5}  {'':>3}   {fmt(scores, -1, -1, -1)}  (input)")
    a = list(scores)
    c = OpCounter()
    quick_sort(a, pivot="last", counter=c, trace=trace_printer)
    print(f"  sub-arrays of size 0/1 are already sorted (CONQUER base case); COMBINE does nothing (in place)")
    print(f"\nSorted scores (ascending): {a}")
    ranked = sorted(orders, key=lambda o: (-o[1], o[0]))         # dispatch order: highest score first
    print("Dispatch queue (highest priority first, ties by order id):")
    print("  " + " ".join(f"{o}({s})" for o, s in ranked))

    print("\nVerification")
    print(f"  equals sorted(): {a == sorted(scores)}   comparisons = {c.comparisons}, swaps = {c.swaps}, "
          f"partitions = {c.partitions}, max depth = {c.max_depth}")
    harmonic = sum(1 / k for k in range(1, n + 1))
    print(f"  expected for a random order 2(n+1)H_n - 4n = {2 * (n + 1) * harmonic - 4 * n:.1f};  "
          f"observed {c.comparisons};  worst case n(n-1)/2 = {n * (n - 1) // 2}")

    print("\nSame 12 scores in other arrangements - comparisons / max recursion depth")
    print(f"  {'input':<20} {'last (baseline)':>16} {'median-of-3':>12} {'random':>10} {'3-way':>10} {'hybrid':>10}")
    cases = [("given sample", scores), ("already sorted", sorted(scores)),
             ("reverse sorted", sorted(scores, reverse=True)), ("all equal (50)", [50] * n)]
    for name, data in cases:
        cells = []
        for algo in ("last", "median3", "random", "3way", "hybrid"):
            c = OpCounter()
            b = list(data)
            if algo == "3way":
                quick_sort_3way(b, counter=c)
            elif algo == "hybrid":
                quick_sort_hybrid(b, counter=c, cutoff=4)
            else:
                quick_sort(b, pivot=algo, counter=c)
            assert b == sorted(data)
            cells.append(f"{c.comparisons}/{c.max_depth}")
        print(f"  {name:<20} {cells[0]:>16} {cells[1]:>12} {cells[2]:>10} {cells[3]:>10} {cells[4]:>10}")
    print("  (hybrid run with cutoff 4 here so that it partitions at n = 12; production cutoff is 16)")

    print("\nStability check - sorting (score, order) records by score with the baseline quick sort")
    recs = [(s, o) for o, s in orders]
    keys = [s for s, _ in recs]
    idx = list(range(n))
    idx_sorted = sorted(idx, key=lambda k: keys[k])               # stable reference order
    tagged = [(keys[k], k) for k in idx]
    quick_sort_records(tagged)
    ties_qs = [recs[k][1] for s, k in tagged if s == 50]
    ties_ref = [recs[k][1] for k in idx_sorted if keys[k] == 50]
    print(f"  score-50 orders in input order : {' '.join(ties_ref)}")
    print(f"  score-50 orders after quick sort: {' '.join(ties_qs)}  -> stable: {ties_qs == ties_ref}")


def quick_sort_records(recs):
    """Baseline quick sort on (score, tag) pairs comparing the SCORE only (used for the stability check)."""
    def part(lo, hi):
        pivot = recs[hi][0]
        i = lo - 1
        for j in range(lo, hi):
            if recs[j][0] <= pivot:
                i += 1
                recs[i], recs[j] = recs[j], recs[i]
        recs[i + 1], recs[hi] = recs[hi], recs[i + 1]
        return i + 1

    def sort(lo, hi):
        if lo < hi:
            p = part(lo, hi)
            sort(lo, p - 1)
            sort(p + 1, hi)

    sort(0, len(recs) - 1)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    run_demo()


if __name__ == "__main__":
    main()
