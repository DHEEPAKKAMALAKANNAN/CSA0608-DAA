"""SwiftLogix - Module 1: Merge Sort for the nightly STABLE sort of shipment-event records.

Problem
    Every night the SwiftLogix analytics platform orders all shipment-event records of the day
    (production workload: 5,000,000 events) by the composite key (delivery_date, event_time).
    Events with identical keys (bulk scans at a hub) must keep their arrival order, so the sort
    must be STABLE.  Merge sort is stable, has a guaranteed Theta(n log n) running time and suits
    large, external (on-disk) batches.

Divide-and-conquer design (top-down merge sort)
    DIVIDE : split the range [lo, hi) at mid = (lo + hi) // 2
    CONQUER: sort both halves recursively (a range of 0 or 1 record is already sorted)
    COMBINE: merge the two sorted halves; on equal keys the LEFT record is taken first (stability)
    Basic operation: one key comparison inside merge().  C(n) = 2C(n/2) + (n - 1)  ->  Theta(n log n)

Also here: the improved variants measured in Part 5 (hybrid merge sort with an insertion-sort
cutoff + "skip merge if already ordered", and bottom-up natural merge sort) and the insertion-sort
baseline.  Every function counts its basic operations in an OpCounter.

Run:  py -3 merge_sort.py           trace on the given sample dataset + output verification
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]                      # .../CO3_AT3
SAMPLE = ROOT / "Supporting_Files" / "datasets" / "m1_shipment_events_sample.csv"


class OpCounter:
    """Counts key comparisons, element moves, recursive calls and the deepest recursion level."""

    def __init__(self):
        self.comparisons = self.moves = self.calls = self.max_depth = 0


# ----------------------------------------------------------------------------- merge (COMBINE step)
def _merge(a, aux, lo, mid, hi, c):
    """Merge sorted runs a[lo:mid] and a[mid:hi] (items are (key, record) pairs). Stable."""
    aux[lo:hi] = a[lo:hi]                    # copy both runs into the work array
    c.moves += hi - lo
    i, j = lo, mid
    for k in range(lo, hi):
        if i >= mid:                         # left run exhausted -> take from the right
            a[k] = aux[j]; j += 1
        elif j >= hi:                        # right run exhausted -> take from the left
            a[k] = aux[i]; i += 1
        else:
            c.comparisons += 1               # BASIC OPERATION: one key comparison
            if aux[j][0] < aux[i][0]:        # strictly smaller -> right record first
                a[k] = aux[j]; j += 1
            else:                            # equal keys -> LEFT record first => stable
                a[k] = aux[i]; i += 1
    c.moves += hi - lo


def _decorate(items, key):
    keyf = key if key is not None else (lambda x: x)
    return [(keyf(x), x) for x in items]


# ----------------------------------------------------------------------------- baseline: top-down
def merge_sort(items, key=None, counter=None, trace=None):
    """Top-down merge sort. Returns a NEW stably sorted list (input list is not modified).

    trace(event, depth, lo, mid, hi, a, comparisons) is called for 'divide', 'base' and 'combine'.
    """
    c = counter if counter is not None else OpCounter()
    a = _decorate(items, key)
    aux = [None] * len(a)

    def sort(lo, hi, depth):
        c.calls += 1
        c.max_depth = max(c.max_depth, depth)
        if hi - lo <= 1:                                        # CONQUER: base case
            if trace and hi - lo == 1:
                trace("base", depth, lo, lo, hi, a, 0)
            return
        mid = (lo + hi) // 2                                    # DIVIDE
        if trace:
            trace("divide", depth, lo, mid, hi, a, 0)
        sort(lo, mid, depth + 1)                                # CONQUER left half
        sort(mid, hi, depth + 1)                                # CONQUER right half
        before = c.comparisons
        _merge(a, aux, lo, mid, hi, c)                          # COMBINE
        if trace:
            trace("combine", depth, lo, mid, hi, a, c.comparisons - before)

    sort(0, len(a), 0)
    return [x for _, x in a]


# ----------------------------------------------------------------------------- baseline: insertion sort
def _insertion_range(a, lo, hi, c):
    """Stable insertion sort of a[lo:hi] (decorated pairs)."""
    for i in range(lo + 1, hi):
        item = a[i]
        j = i - 1
        while j >= lo:
            c.comparisons += 1
            if a[j][0] > item[0]:            # strictly greater -> shift (keeps stability)
                a[j + 1] = a[j]; c.moves += 1; j -= 1
            else:
                break
        a[j + 1] = item
        c.moves += 1


def insertion_sort(items, key=None, counter=None):
    """Brute-force baseline: stable insertion sort, Theta(n^2) comparisons on average."""
    c = counter if counter is not None else OpCounter()
    a = _decorate(items, key)
    _insertion_range(a, 0, len(a), c)
    return [x for _, x in a]


# ----------------------------------------------------------------------------- improvement 1: hybrid
def merge_sort_hybrid(items, key=None, cutoff=16, counter=None):
    """Top-down merge sort + insertion sort for ranges <= cutoff + skip merge if halves are in order."""
    c = counter if counter is not None else OpCounter()
    a = _decorate(items, key)
    aux = [None] * len(a)

    def sort(lo, hi, depth):
        c.calls += 1
        c.max_depth = max(c.max_depth, depth)
        if hi - lo <= cutoff:
            _insertion_range(a, lo, hi, c)
            return
        mid = (lo + hi) // 2
        sort(lo, mid, depth + 1)
        sort(mid, hi, depth + 1)
        c.comparisons += 1
        if a[mid][0] < a[mid - 1][0]:        # halves overlap -> merge is needed
            _merge(a, aux, lo, mid, hi, c)

    sort(0, len(a), 0)
    return [x for _, x in a]


# ----------------------------------------------------------------------------- improvement 2: natural
def natural_merge_sort(items, key=None, counter=None):
    """Bottom-up natural merge sort: detect ascending runs (e.g. pre-sorted hub feeds), merge pairwise."""
    c = counter if counter is not None else OpCounter()
    a = _decorate(items, key)
    n = len(a)
    if n <= 1:
        return [x for _, x in a]
    bounds = [0]
    for i in range(1, n):                    # one pass: find the starts of non-decreasing runs
        c.comparisons += 1
        if a[i][0] < a[i - 1][0]:
            bounds.append(i)
    bounds.append(n)
    aux = [None] * n
    while len(bounds) > 2:                   # more than one run left
        runs = len(bounds) - 1
        new_bounds, r = [0], 0
        while r + 1 < runs:                  # merge runs r and r+1
            _merge(a, aux, bounds[r], bounds[r + 1], bounds[r + 2], c)
            new_bounds.append(bounds[r + 2])
            r += 2
        if r < runs:                         # odd run count: last run carried to the next pass
            new_bounds.append(bounds[r + 1])
        bounds = new_bounds
        c.max_depth += 1                     # here: number of merge passes
    return [x for _, x in a]


# ----------------------------------------------------------------------------- demo on the sample
def load_events(path=SAMPLE):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def event_key(r):
    """Composite sort key: (delivery_date, event_time); ISO strings compare chronologically."""
    return (r["delivery_date"], r["event_time"])


def print_events(title, records):
    print(title)
    print(f"  {'pos':>3}  {'event':<5}  {'tracking ID':<13}  {'delivery date':<13}  {'time':<8}  hub  status")
    for p, r in enumerate(records):
        print(f"  {p:>3}  {r['event_id']:<5}  {r['tracking_id']:<13}  {r['delivery_date']:<13}  "
              f"{r['event_time']:<8}  {r['hub']:<3}  {r['status']}")


def trace_printer(event, depth, lo, mid, hi, a, comps):
    ids = lambda s, e: " ".join(rec["event_id"] for _, rec in a[s:e])
    pad = "  " * depth
    if event == "divide":
        print(f"  {pad}DIVIDE  [{lo}:{hi}] -> [{lo}:{mid}] + [{mid}:{hi}]")
    elif event == "base":
        print(f"  {pad}BASE    [{lo}:{hi}] {ids(lo, hi)}  (one record = sorted)")
    else:
        print(f"  {pad}COMBINE [{lo}:{hi}] {comps} cmp -> {ids(lo, hi)}")


def run_demo():
    events = load_events()
    n = len(events)
    print("=" * 100)
    print(f"SwiftLogix M1 - stable merge sort of shipment events (given sample: {n} records)")
    print("=" * 100)
    print_events("Input in arrival order (key = delivery_date, event_time):", events)
    print("\nDivide / conquer / combine trace (record IDs after each step):")
    c = OpCounter()
    out = merge_sort(events, key=event_key, counter=c, trace=trace_printer)
    print()
    print_events("Output (sorted by delivery_date, event_time):", out)

    ref = sorted(events, key=event_key)                         # Python's sorted() is stable
    same = [r["event_id"] for r in out] == [r["event_id"] for r in ref]
    pos = {r["event_id"]: p for p, r in enumerate(out)}
    print("\nVerification")
    print(f"  identical to Python sorted() (stable reference) : {same}")
    for x, y in (("E06", "E11"), ("E04", "E09")):
        print(f"  equal keys {x}/{y}: {x} at pos {pos[x]}, {y} at pos {pos[y]} -> arrival order kept: "
              f"{pos[x] < pos[y]}")
    log_n = (n - 1).bit_length()
    worst = n * log_n - 2 ** log_n + 1
    print(f"  comparisons = {c.comparisons}  (worst-case bound n*ceil(lg n) - 2^ceil(lg n) + 1 = {worst})")
    print(f"  moves = {c.moves}, recursive calls = {c.calls} (= 2n - 1 = {2 * n - 1}), "
          f"max depth = {c.max_depth} (= ceil(lg n) = {log_n})")


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    run_demo()


if __name__ == "__main__":
    main()
