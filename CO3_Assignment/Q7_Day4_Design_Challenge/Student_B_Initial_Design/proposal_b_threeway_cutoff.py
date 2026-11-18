"""Q7 - Student B's independent design proposal (initial prototype).

Diagnosed limitation (Q2): the textbook quick sort compares every key with the pivot again and again when
many orders share the same deadline (15-minute booking slots, all-equal batches), and a fixed pivot position
makes sorted and reversed exports quadratic.

Proposal B - "finish equal keys in one pass and stop recursing on tiny parts":
  1. random pivot (seeded generator)                     -> no fixed input order is bad on average
  2. Dijkstra's 3-way partition  < pivot | = pivot | > pivot  -> all keys equal to the pivot are DONE and
                                                            never compared again (k distinct keys: n log k)
  3. insertion sort for sub-arrays of <= 16 orders       -> removes the many tiny recursive calls
Prediction (made before testing): about 1.4-1.6 n log2 n comparisons on random, sorted and reversed lists,
about 2n comparisons (one partition) on an all-equal list and about n log2 64 on 64 slot values;
expected recursion depth about 2 log2 n.
Run:  py proposal_b_threeway_cutoff.py      (prototype check on the five Q2 input conditions, n = 2,000)
"""
import math
import random


class SortStats:
    """Operation counters (same meaning as in Q2: moves = element writes, a swap = 2)."""

    def __init__(self):
        self.comparisons = 0
        self.moves = 0
        self.max_depth = 0
        self.heapsort_fallbacks = 0     # not used by proposal B (kept for a common interface)


def quick_sort_b(a, stats=None, seed=42, cutoff=16):
    """Proposal B: random pivot + 3-way partition + insertion sort for n <= cutoff. Returns stats."""
    stats = stats or SortStats()
    rng = random.Random(seed)

    def insertion_sort(lo, hi):
        comps = moves = 0
        for k in range(lo + 1, hi + 1):
            key = a[k]
            j = k - 1
            while j >= lo:
                comps += 1
                if a[j] > key:
                    a[j + 1] = a[j]                 # shift one place right (1 write)
                    moves += 1
                    j -= 1
                else:
                    break
            if j + 1 != k:
                a[j + 1] = key
                moves += 1
        stats.comparisons += comps
        stats.moves += moves

    def sort(lo, hi, depth):
        if depth > stats.max_depth:
            stats.max_depth = depth
        if hi - lo + 1 <= cutoff:
            insertion_sort(lo, hi)
            return
        pivot = a[rng.randint(lo, hi)]
        lt, i, gt = lo, lo, hi                      # a[lo..lt-1] < p, a[lt..i-1] = p, a[gt+1..hi] > p
        comps = moves = 0
        while i <= gt:
            comps += 1
            if a[i] < pivot:
                if lt != i:
                    a[lt], a[i] = a[i], a[lt]
                    moves += 2
                lt += 1
                i += 1
            else:
                comps += 1
                if a[i] > pivot:
                    a[i], a[gt] = a[gt], a[i]
                    moves += 2
                    gt -= 1
                else:
                    i += 1                          # equal to the pivot: already in its final region
        stats.comparisons += comps
        stats.moves += moves
        sort(lo, lt - 1, depth + 1)
        sort(gt + 1, hi, depth + 1)

    sort(0, len(a) - 1, 0)
    return stats


def main():
    n = 2000
    rng = random.Random(42)
    base = [rng.randrange(57_600) for _ in range(n)]
    inputs = {"random": base, "sorted": sorted(base), "reverse": sorted(base, reverse=True),
              "slots": [rng.randrange(64) * 900 for _ in range(n)], "all-equal": [8100] * n}
    lg = math.log2(n)
    print("Q7 - Student B prototype: random pivot + 3-way partition + insertion sort below 16 (n = 2,000)")
    print(f"{'input':>10} | {'comparisons':>11} {'/ n lg n':>8} | {'moves':>7} | {'depth':>5} | correct")
    for name, data in inputs.items():
        a = list(data)
        st = quick_sort_b(a)
        print(f"{name:>10} | {st.comparisons:>11,} {st.comparisons / (n * lg):>8.2f} | {st.moves:>7,} | "
              f"{st.max_depth:>5} | {a == sorted(data)}")
    print(f"Prediction: ~1.4-1.6 n lg n on random/sorted/reverse, 2n = {2 * n:,} on all-equal, "
          f"~n lg 64 = {6 * n:,} on slots")


if __name__ == "__main__":
    main()
