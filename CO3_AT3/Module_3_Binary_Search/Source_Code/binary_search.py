"""SwiftLogix - Module 3: Binary Search for tracking-ID lookups in the sorted shipment index.

Problem
    Customers, couriers and partner APIs look up shipments by tracking ID (production workload:
    20,000,000 lookups/day on an index of 10,000,000 IDs).  Module 1 rebuilds the index every night
    as an array of tracking IDs in strictly increasing order with the offset of each shipment record.
    A lookup must return the record offset, or report "not found" quickly.

Divide-and-conquer design (decrease-by-half)
    DIVIDE : probe the middle element K[mid] of the current interval [lo, hi]
    CONQUER: continue in ONE half only (left if t < K[mid], right if t > K[mid])
    COMBINE: trivial - the answer of the sub-problem is the answer of the problem
    Basic operation: one three-way comparison of the target with K[mid].
    C_worst(n) = C(floor(n/2)) + 1  ->  floor(lg n) + 1 comparisons, Theta(log n).

Also here: linear search (baseline), interpolation search and guarded interpolation search (Part 5).
Tracking IDs are 'SLX' + 10 digits; the numeric part is used as the key.

Run:  py -3 binary_search.py      traces on the given sample index and queries + verification with bisect
"""
import bisect
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "Supporting_Files" / "datasets"


class OpCounter:
    """Counts key comparisons (a three-way comparison counts as one) and loop iterations / calls."""

    def __init__(self):
        self.comparisons = self.probes = 0


def tid(key):
    return f"SLX{key:010d}"


# ----------------------------------------------------------------------------- binary search (iterative)
def binary_search(keys, target, counter=None, trace=None):
    """Return the index of target in the sorted list keys, or -1. trace(step, lo, mid, hi, outcome)."""
    c = counter if counter is not None else OpCounter()
    lo, hi = 0, len(keys) - 1
    step = 0
    while lo <= hi:
        mid = (lo + hi) // 2                          # DIVIDE: middle of [lo, hi]
        step += 1
        c.probes += 1
        c.comparisons += 1                            # BASIC OPERATION: three-way comparison
        if target == keys[mid]:
            if trace:
                trace(step, lo, mid, hi, "found")
            return mid
        if target < keys[mid]:
            if trace:
                trace(step, lo, mid, hi, "go left")
            hi = mid - 1                              # CONQUER the left half only
        else:
            if trace:
                trace(step, lo, mid, hi, "go right")
            lo = mid + 1                              # CONQUER the right half only
    if trace:
        trace(step + 1, lo, None, hi, "empty")
    return -1


# ----------------------------------------------------------------------------- binary search (recursive)
def binary_search_recursive(keys, target, lo=0, hi=None, counter=None, trace=None, depth=0):
    """Recursive version: same comparisons, O(log n) stack frames instead of O(1) extra space."""
    c = counter if counter is not None else OpCounter()
    if hi is None:
        hi = len(keys) - 1
    if lo > hi:                                       # base case: empty interval
        if trace:
            trace(depth, lo, None, hi, "empty -> return -1")
        return -1
    mid = (lo + hi) // 2
    c.probes += 1
    c.comparisons += 1
    if target == keys[mid]:
        if trace:
            trace(depth, lo, mid, hi, f"found -> return {mid}")
        return mid
    if target < keys[mid]:
        if trace:
            trace(depth, lo, mid, hi, "recurse on left half")
        return binary_search_recursive(keys, target, lo, mid - 1, c, trace, depth + 1)
    if trace:
        trace(depth, lo, mid, hi, "recurse on right half")
    return binary_search_recursive(keys, target, mid + 1, hi, c, trace, depth + 1)


# ----------------------------------------------------------------------------- baseline + improvements
def linear_search(keys, target, counter=None):
    """Brute-force baseline: scan left to right (stops early once keys exceed the target)."""
    c = counter if counter is not None else OpCounter()
    for i, k in enumerate(keys):
        c.probes += 1
        c.comparisons += 1
        if k == target:
            return i
        if k > target:                                # sorted index: target cannot appear later
            return -1
    return -1


def interpolation_search(keys, target, counter=None):
    """Probe where the target 'should' be if keys were uniform: O(log log n) expected, O(n) worst."""
    c = counter if counter is not None else OpCounter()
    lo, hi = 0, len(keys) - 1
    while lo <= hi:
        c.comparisons += 2                            # range check K[lo] <= t <= K[hi]
        if not (keys[lo] <= target <= keys[hi]):
            return -1
        if keys[hi] == keys[lo]:
            pos = lo
        else:
            pos = lo + (target - keys[lo]) * (hi - lo) // (keys[hi] - keys[lo])
        c.probes += 1
        c.comparisons += 1                            # three-way comparison with K[pos]
        if keys[pos] == target:
            return pos
        if target < keys[pos]:
            hi = pos - 1
        else:
            lo = pos + 1
    return -1


def guarded_interpolation_search(keys, target, counter=None):
    """Interpolation probes, but a binary (halving) probe follows any step that did not halve the interval.

    Keeps the O(log log n) behaviour on uniform IDs while bounding the worst case by O(log n).
    """
    c = counter if counter is not None else OpCounter()
    lo, hi = 0, len(keys) - 1
    use_binary = False
    while lo <= hi:
        c.comparisons += 2
        if not (keys[lo] <= target <= keys[hi]):
            return -1
        width = hi - lo + 1
        if use_binary or keys[hi] == keys[lo]:
            pos = (lo + hi) // 2
        else:
            pos = lo + (target - keys[lo]) * (hi - lo) // (keys[hi] - keys[lo])
        c.probes += 1
        c.comparisons += 1
        if keys[pos] == target:
            return pos
        if target < keys[pos]:
            hi = pos - 1
        else:
            lo = pos + 1
        use_binary = (hi - lo + 1) > width // 2
    return -1


# ----------------------------------------------------------------------------- demo on the sample
def load_sample():
    with open(DATA / "m3_tracking_index_sample.csv", newline="", encoding="utf-8") as fh:
        index = [(int(r["tracking_id"][3:]), int(r["record_offset"])) for r in csv.DictReader(fh)]
    with open(DATA / "m3_lookup_queries_sample.csv", newline="", encoding="utf-8") as fh:
        queries = [(r["query_id"], int(r["tracking_id"][3:]), r["expected"]) for r in csv.DictReader(fh)]
    return index, queries


def run_demo():
    index, queries = load_sample()
    keys = [k for k, _ in index]
    offsets = [o for _, o in index]
    n = len(keys)
    print("=" * 104)
    print(f"SwiftLogix M3 - binary search in the sorted tracking index (given sample: n = {n} IDs, "
          f"{len(queries)} queries)")
    print("=" * 104)
    for row in range(0, n, 4):
        print("  " + "   ".join(f"[{p:>2}] {tid(keys[p])} -> rec {offsets[p]:>2}" for p in range(row, row + 4)))

    print("\nIterative binary search - interval [lo, hi], probe mid, decision (one 3-way comparison per step)")
    summary = []
    for qid, target, expected in queries:
        lines = []

        def tr(step, lo, mid, hi, outcome):
            if mid is None:
                lines.append(f"      end    : lo={lo:>2} hi={hi:>2}  lo > hi -> interval empty, stop")
            else:
                lines.append(f"      step {step}: lo={lo:>2} hi={hi:>2} mid={mid:>2}  K[mid]={tid(keys[mid])}  -> {outcome}")

        c = OpCounter()
        pos = binary_search(keys, target, counter=c, trace=tr)
        ref = bisect.bisect_left(keys, target)
        ref_pos = ref if ref < n and keys[ref] == target else -1
        result = f"FOUND at [{pos}] -> record offset {offsets[pos]}" if pos >= 0 else \
            f"NOT FOUND (insertion point {ref})"
        print(f"  {qid} {tid(target)} ({expected}): {result}; comparisons = {c.comparisons}")
        for line in lines:
            print(line)
        summary.append((qid, pos, ref_pos, c.comparisons, expected))

    print("\nRecursive version on Q5 - each call keeps ONE half (divide + conquer), the result is passed back"
          " unchanged (combine)")
    q5 = queries[4][1]

    def rtr(depth, lo, mid, hi, outcome):
        mid_txt = f"mid={mid:>2} K[mid]={tid(keys[mid])}" if mid is not None else "lo > hi"
        print(f"    {'  ' * depth}BinarySearchRec(lo={lo:>2}, hi={hi:>2}): {mid_txt} -> {outcome}")

    binary_search_recursive(keys, q5, trace=rtr)

    print("\nVerification against bisect.bisect_left (Python's C implementation) and the expected labels")
    ok = all(p == r and ((p >= 0) == (e == "present")) for _, p, r, _, e in summary)
    print(f"  all {len(summary)} queries agree: {ok}")
    worst = n.bit_length()                                  # floor(lg n) + 1
    print(f"  comparisons per query: {[s[3] for s in summary]}  (max {max(s[3] for s in summary)}"
          f" <= floor(lg n) + 1 = {worst})")
    print(f"  linear search would need up to n = {n} comparisons per query")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    run_demo()


if __name__ == "__main__":
    main()
