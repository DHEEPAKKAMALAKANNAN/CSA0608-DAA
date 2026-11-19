"""Q2 - Merge Sort versus Quick Sort under different data conditions (CSA06 Assignment 3, CO3).

Scenario (Smart Logistics - city drone-delivery operations centre): before each dispatch wave the scheduling
service sorts the pending delivery orders by their promised deadline. Orders may arrive in random order,
already sorted, in reverse order, or with very many equal deadlines (15-minute booking slots).

Algorithms (pure Python, counted):
  merge_sort   top-down merge sort, stable; T(n) = 2T(n/2) + (n - 1) comparisons in the worst case
  quick_sort   Lomuto partition (CLRS). The group's stated pivot strategy is 'last'; the two other rules are
               kept only for the joint comparison:
               'last'    - the last element (textbook) - THE STRATEGY STUDIED IN Q2
               'random'  - a uniformly random element (seeded)
               'median3' - median of the first, middle and last element
               best/average T(n) = 2T(n/2) + (n - 1); worst T(n) = T(n - 1) + (n - 1) = n(n - 1)/2
Counters: comparisons = element comparisons; moves = element writes (a swap = 2 writes, a copy = 1 write);
          max_depth = deepest recursion level (root = 0); record = list of (depth, left, right) sizes.
designed_input(n, f) builds Student A's balanced (f = 0.5) / 90:10 (f = 0.9) inputs for the last-element pivot.
Run:  py q2_sorting.py      (small demo with traces; experiments: q2_experiments.py)
"""
import random
import sys

sys.setrecursionlimit(100_000)       # the textbook quick sort recurses n - 1 levels deep on sorted data


class SortStats:
    """Operation counters of one sorting run."""

    def __init__(self):
        self.comparisons = 0
        self.moves = 0
        self.max_depth = 0
        self.calls = 0


def merge_sort(a, stats=None, trace=None, record=None):
    """Sort list a in place by top-down merge sort; returns stats.

    record (optional list): one tuple (depth, left_size, right_size) is appended per division.

    Divide : split a[lo..hi] at mid = (lo + hi) // 2.
    Conquer: sort both halves recursively (a list of 0 or 1 element is sorted).
    Combine: merge the two sorted halves through an auxiliary array (stable: ties take the left element).
    """
    stats = stats or SortStats()
    aux = list(a)                                         # workspace of n elements (extra memory)

    def merge(lo, mid, hi):
        for k in range(lo, hi + 1):                       # copy the run to the workspace
            aux[k] = a[k]
        moves, comps = hi - lo + 1, 0
        i, j = lo, mid + 1
        for k in range(lo, hi + 1):                       # merge back into a
            if i > mid:
                a[k] = aux[j]
                j += 1
            elif j > hi:
                a[k] = aux[i]
                i += 1
            else:
                comps += 1
                if aux[j] < aux[i]:
                    a[k] = aux[j]
                    j += 1
                else:
                    a[k] = aux[i]
                    i += 1
            moves += 1
        stats.comparisons += comps
        stats.moves += moves

    def sort(lo, hi, depth):
        stats.calls += 1
        if depth > stats.max_depth:
            stats.max_depth = depth
        if lo >= hi:
            return
        mid = (lo + hi) // 2                              # DIVIDE
        if record is not None:
            record.append((depth, mid - lo + 1, hi - mid))
        sort(lo, mid, depth + 1)                          # CONQUER
        sort(mid + 1, hi, depth + 1)
        merge(lo, mid, hi)                                # COMBINE
        if trace is not None:
            trace.append(f"{'  ' * depth}merge [{lo}..{mid}] + [{mid + 1}..{hi}] -> {a[lo:hi + 1]}")

    sort(0, len(a) - 1, 0)
    return stats


def quick_sort(a, pivot="last", stats=None, seed=42, trace=None, record=None):
    """Sort list a in place by quick sort with Lomuto partitioning; returns stats.

    Pivot strategy of the group's study: pivot="last" (the last element, textbook Lomuto).
    record (optional list): one tuple (depth, left_size, right_size) is appended per partition.

    Divide : choose a pivot (rule `pivot`), move it to a[hi] and partition a[lo..hi] into
             a[lo..p-1] <= pivot, a[p] = pivot, a[p+1..hi] > pivot.
    Conquer: sort both parts recursively.
    Combine: nothing - the parts are already in their final positions.
    """
    stats = stats or SortStats()
    rng = random.Random(seed)

    def swap(i, j):
        a[i], a[j] = a[j], a[i]
        stats.moves += 2

    def median_of_three(lo, hi):
        """Index of the median of a[lo], a[mid], a[hi] (2 or 3 comparisons)."""
        mid = (lo + hi) // 2
        stats.comparisons += 2
        if a[lo] < a[mid]:
            if a[mid] < a[hi]:
                return mid
            stats.comparisons += 1
            return hi if a[lo] < a[hi] else lo
        if a[lo] < a[hi]:
            return lo
        stats.comparisons += 1
        return hi if a[mid] < a[hi] else mid

    def partition(lo, hi):
        if pivot == "random":
            p = rng.randint(lo, hi)
        elif pivot == "median3" and hi - lo >= 2:
            p = median_of_three(lo, hi)
        else:
            p = hi
        if p != hi:
            swap(p, hi)                                   # the pivot waits at a[hi]
        x = a[hi]
        i = lo - 1
        comps = 0
        for j in range(lo, hi):                           # Lomuto scan: hi - lo comparisons
            comps += 1
            if a[j] <= x:
                i += 1
                if i != j:
                    swap(i, j)
        stats.comparisons += comps
        if i + 1 != hi:
            swap(i + 1, hi)                               # pivot to its final place
        return i + 1

    def sort(lo, hi, depth):
        stats.calls += 1
        if depth > stats.max_depth:
            stats.max_depth = depth
        if lo >= hi:
            return
        p = partition(lo, hi)                             # DIVIDE
        if record is not None:
            record.append((depth, p - lo, hi - p))
        if trace is not None:
            trace.append(f"{'  ' * depth}[{lo}..{hi}] pivot {a[p]} -> left {p - lo}, right {hi - p}")
        sort(lo, p - 1, depth + 1)                        # CONQUER
        sort(p + 1, hi, depth + 1)

    sort(0, len(a) - 1, 0)
    return stats


def designed_input(n, left_fraction=0.5):
    """Student A's designed input: the values 0..n-1 arranged so that last-pivot Lomuto quick sort puts
    left_fraction of every sub-array on the left (0.5 -> every pivot is the median: perfectly balanced).

    Lomuto leaves a prefix of small keys in place and its final swap moves the FIRST key of the right
    part to the end, so the designed right part DR is stored as [DR[-1]] + DR[:-1].
    """
    def design(values):
        m = len(values)
        if m <= 1:
            return list(values)
        r = int(left_fraction * (m - 1)) if left_fraction != 0.5 else (m - 1) // 2   # pivot rank in sub-array
        left, pivot, right = values[:r], values[r], values[r + 1:]
        dl, dr = design(left), design(right)
        moved_right = [dr[-1]] + dr[:-1] if dr else []      # undo the final Lomuto swap in advance
        return dl + moved_right + [pivot]
    return design(list(range(n)))


ALGORITHMS = {
    "Merge": lambda a: merge_sort(a),
    "Quick-last": lambda a: quick_sort(a, "last"),
    "Quick-random": lambda a: quick_sort(a, "random"),
    "Quick-median3": lambda a: quick_sort(a, "median3"),
}


def hhmm(seconds_after_six):
    """Deadline (seconds after 06:00) as HH:MM."""
    m = seconds_after_six // 60
    return f"{6 + m // 60:02d}:{m % 60:02d}"


def main():
    print("=" * 96)
    print("Q2 DEMO - sorting delivery orders by deadline (seconds after 06:00) with Merge Sort and Quick Sort")
    print("=" * 96)
    rng = random.Random(7)
    deadlines = [rng.randrange(0, 16 * 3600) for _ in range(8)]
    print("Orders (deadline):", ", ".join(hhmm(d) for d in deadlines))
    trace = []
    a = list(deadlines)
    s = merge_sort(a, trace=trace)
    print("\nMerge Sort - combine steps (deepest first):")
    for line in trace:
        print("   " + line)
    print(f"   sorted: {', '.join(hhmm(d) for d in a)}")
    print(f"   {s.comparisons} comparisons, {s.moves} moves, depth {s.max_depth}")

    exported = sorted(deadlines)
    balanced = [exported[i] for i in designed_input(len(exported))]
    cases = (("the ALREADY SORTED export", exported), ("Student A's designed BALANCED input", balanced))
    for label, data in cases:
        trace = []
        a = list(data)
        s = quick_sort(a, "last", trace=trace)
        print(f"\nQuick Sort, pivot = LAST element, on {label} - partition steps:")
        print("   input:", ", ".join(hhmm(d) for d in data))
        for line in trace:
            print("   " + line)
        print(f"   {s.comparisons} comparisons, {s.moves} moves, depth {s.max_depth}")

    print("\nAll four sorts on the same 8 orders (random / sorted / reverse / one 15-minute slot):")
    print(f"{'algorithm':>14} | {'random':>15} | {'sorted':>15} | {'reverse':>15} | {'all equal':>15}")
    print(f"{'':>14} | " + " | ".join(f"{'comp mov dep':>15}" for _ in range(4)))
    inputs = [deadlines, sorted(deadlines), sorted(deadlines, reverse=True), [900] * 8]
    for name, fn in ALGORITHMS.items():
        cells = []
        for data in inputs:
            a = list(data)
            st = fn(a)
            assert a == sorted(data)
            cells.append(f"{st.comparisons:>4} {st.moves:>4} {st.max_depth:>4}")
        print(f"{name:>14} | " + " | ".join(f"{c:>15}" for c in cells))


if __name__ == "__main__":
    main()
