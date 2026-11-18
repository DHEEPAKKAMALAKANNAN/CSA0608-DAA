"""Q1 - Max-Min and Binary Search by Divide-and-Conquer (CSA06 Assignment 3, CO3).

Scenario (Smart Logistics - city drone-delivery operations centre):
  * After every flight a drone's controller must report the highest and the lowest battery-cell
    temperature among the n readings it logged (the Max-Min problem). Comparisons cost energy.
  * At the hub, scanners look up parcel IDs in a manifest that is kept sorted (searching problem).

Algorithms (pure Python; every element comparison is counted):
  maxmin_naive       straightforward scan, compares each reading with the max AND the min: 2(n - 1)
  maxmin_dc          divide-and-conquer Max-Min, T(n) = T(n1) + T(n2) + 2, T(2) = 1, T(1) = 0
                     rule 'half': split in the middle   rule 'even': the first part has an even size
  maxmin_pairwise    the same D&C with the division "2 readings | rest", unrolled into a loop
  binary_search_rec  recursive binary search, one three-way comparison ("probe") per call,
                     C(n) = C(floor(n/2)) + 1, C(1) = 1  ->  worst case floor(log2 n) + 1 probes

Run:  py q1_maxmin_binsearch.py      (small demo with recursion traces; experiments: q1_experiments.py)
"""


class MaxMinStats:
    """Operation counters of one Max-Min run."""

    def __init__(self):
        self.comparisons = 0   # element comparisons (the basic operation)
        self.calls = 0         # nodes of the recursion tree
        self.leaves1 = 0       # base cases holding 1 reading (0 comparisons)
        self.leaves2 = 0       # base cases holding 2 readings (1 comparison)
        self.max_depth = 0     # deepest recursion level (root = 0)


def maxmin_naive(a, stats=None):
    """Straightforward scan: every reading after the first is compared with the max and with the min.

    Returns (maximum, minimum, stats); exactly 2(n - 1) comparisons for every input.
    """
    stats = stats or MaxMinStats()
    hi = lo = a[0]
    comparisons = 0
    for i in range(1, len(a)):
        x = a[i]
        comparisons += 2
        if x > hi:
            hi = x
        if x < lo:
            lo = x
    stats.comparisons += comparisons
    return hi, lo, stats


def left_part_size(n, rule):
    """Size of the first sub-array when n >= 3 readings are divided.

    'half': ceil(n/2) (the textbook middle split).
    'even': the size closest to n/2 that is EVEN, so that the first part never produces a lone reading.
    """
    if rule == "half":
        return (n + 1) // 2
    h = n // 2
    return h if h % 2 == 0 else h + 1


def maxmin_dc(a, rule="half", stats=None, trace=None):
    """Divide-and-conquer Max-Min of a[0..n-1].

    Divide : split the readings into two parts (sizes from left_part_size).
    Conquer: solve both parts recursively (1 reading: 0 comparisons, 2 readings: 1 comparison).
    Combine: 1 comparison for the larger maximum + 1 comparison for the smaller minimum.
    Returns (maximum, minimum, stats). If trace is a list, one text line per node is appended.
    """
    stats = stats or MaxMinStats()

    def solve(lo, hi, depth):
        stats.calls += 1
        if depth > stats.max_depth:
            stats.max_depth = depth
        pad = "    " * depth
        if lo == hi:                                    # one reading: it is the max and the min
            stats.leaves1 += 1
            if trace is not None:
                trace.append(f"{pad}[{lo}..{hi}] leaf -> max={a[lo]}, min={a[lo]}  (0 comparisons)")
            return a[lo], a[lo]
        if hi == lo + 1:                                # two readings: one comparison
            stats.leaves2 += 1
            stats.comparisons += 1
            big, small = (a[hi], a[lo]) if a[lo] < a[hi] else (a[lo], a[hi])
            if trace is not None:
                trace.append(f"{pad}[{lo}..{hi}] leaf -> max={big}, min={small}  (1 comparison)")
            return big, small
        k = left_part_size(hi - lo + 1, rule)           # DIVIDE
        if trace is not None:
            trace.append(f"{pad}[{lo}..{hi}] divide into [{lo}..{lo + k - 1}] and [{lo + k}..{hi}]")
        max1, min1 = solve(lo, lo + k - 1, depth + 1)   # CONQUER
        max2, min2 = solve(lo + k, hi, depth + 1)
        stats.comparisons += 2                          # COMBINE
        big = max1 if max1 > max2 else max2
        small = min1 if min1 < min2 else min2
        if trace is not None:
            trace.append(f"{pad}[{lo}..{hi}] combine -> max={big}, min={small}  (2 comparisons)")
        return big, small

    hi, lo = solve(0, len(a) - 1, 0)
    return hi, lo, stats


def maxmin_pairwise(a, stats=None):
    """Iterative form of D&C Max-Min with the division '2 readings | the rest' (tail recursion unrolled).

    Each pair costs 1 comparison (which is larger) + 1 (larger vs max) + 1 (smaller vs min):
    3 comparisons per 2 readings, i.e. ceil(3n/2) - 2 in total, with no recursion stack.
    Returns (maximum, minimum, stats).
    """
    stats = stats or MaxMinStats()
    n = len(a)
    if n % 2:                                   # odd n: the first reading starts both max and min
        hi = lo = a[0]
        start, comparisons = 1, 0
    else:                                       # even n: the first pair starts them (1 comparison)
        hi, lo = (a[1], a[0]) if a[0] < a[1] else (a[0], a[1])
        start, comparisons = 2, 1
    for i in range(start, n - 1, 2):
        x, y = a[i], a[i + 1]
        comparisons += 3
        if x < y:
            x, y = y, x                         # x = larger of the pair, y = smaller
        if x > hi:
            hi = x
        if y < lo:
            lo = y
    stats.comparisons += comparisons
    return hi, lo, stats


def maxmin_formula_optimal(n):
    """Lower bound (and count of the 'even' rule): ceil(3n/2) - 2."""
    return (3 * n + 1) // 2 - 2


def maxmin_formula_from_leaves(n, leaves1):
    """Exact count of ANY division rule: (3n + L1)/2 - 2, where L1 = number of 1-reading leaves."""
    return (3 * n + leaves1) // 2 - 2


def binary_search_rec(a, key, lo, hi, trace=None):
    """Recursive binary search for key in the sorted list a[lo..hi].

    Divide : probe the middle element a[mid] (one three-way comparison).
    Conquer: search only the half that can still contain the key (the other half is discarded).
    Combine: nothing - the answer of the sub-problem is the answer.
    Returns (index or -1, number of probes).
    """
    if lo > hi:                                         # empty range: key is absent
        if trace is not None:
            trace.append(f"   range [{lo}..{hi}] is empty -> not found")
        return -1, 0
    mid = (lo + hi) // 2
    if trace is not None:
        trace.append(f"   probe a[{mid}] = {a[mid]} in range [{lo}..{hi}]")
    if key == a[mid]:
        return mid, 1
    if key < a[mid]:
        index, probes = binary_search_rec(a, key, lo, mid - 1, trace)
    else:
        index, probes = binary_search_rec(a, key, mid + 1, hi, trace)
    return index, probes + 1


def binary_search(a, key, trace=None):
    """Search the whole sorted list; returns (index or -1, probes)."""
    return binary_search_rec(a, key, 0, len(a) - 1, trace)


def floor_log2(n):
    """floor(log2 n) for n >= 1, using integers only."""
    return n.bit_length() - 1


def main():
    print("=" * 100)
    print("Q1 DEMO - Max-Min of one flight's battery temperatures and Binary Search in a parcel manifest")
    print("=" * 100)
    temps = [31.5, 28.0, 44.2, 39.9, 25.1, 47.3, 30.6, 41.8]      # deg C, one 8-reading flight
    print(f"\nFlight log (n = {len(temps)}): {temps}")
    _, _, s = maxmin_naive(temps)
    print(f"Straightforward scan     : {s.comparisons} comparisons (2n - 2 = {2 * len(temps) - 2})")
    trace = []
    hi, lo, s = maxmin_dc(temps, "half", trace=trace)
    print("Divide-and-conquer trace (rule 'half'):")
    for line in trace:
        print("   " + line)
    print(f"Result: max = {hi} C, min = {lo} C; {s.comparisons} comparisons "
          f"(3n/2 - 2 = {3 * len(temps) // 2 - 2}), {s.calls} calls, depth {s.max_depth}")

    six = temps[:6]
    print(f"\nWhen n is not a power of 2 the division rule matters (n = 6: {six})")
    for rule in ("half", "even"):
        trace = []
        _, _, s = maxmin_dc(six, rule, trace=trace)
        divides = [t.strip() for t in trace if "divide" in t]
        print(f"   rule '{rule}': {s.comparisons} comparisons, lone-reading leaves L1 = {s.leaves1}; "
              f"{divides[0]}")
    print(f"   optimum ceil(3n/2) - 2 = {maxmin_formula_optimal(6)}; any rule costs (3n + L1)/2 - 2")
    _, _, s = maxmin_pairwise(six)
    print(f"   pairwise loop ('2 | rest' division, no recursion): {s.comparisons} comparisons")

    manifest = [10210, 10342, 10477, 10519, 10604, 10788, 10835, 10912,
                11050, 11163, 11297, 11348, 11402, 11586, 11621, 11799]   # sorted parcel IDs
    print(f"\nSorted parcel manifest (n = {len(manifest)}):")
    print(f"   indices 0-7 : {manifest[:8]}")
    print(f"   indices 8-15: {manifest[8:]}")
    for key in (11348, 10600):
        trace = []
        idx, probes = binary_search(manifest, key, trace)
        print(f"Look up parcel {key}:")
        for line in trace:
            print(line)
        outcome = f"found at index {idx}" if idx >= 0 else "not in the manifest"
        print(f"   -> {outcome} after {probes} probes "
              f"(worst case floor(log2 n) + 1 = {floor_log2(len(manifest)) + 1})")


if __name__ == "__main__":
    main()
