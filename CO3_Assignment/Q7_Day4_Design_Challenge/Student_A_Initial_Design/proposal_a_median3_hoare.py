"""Q7 - Student A's independent design proposal (initial prototype).

Diagnosed limitation (Q2): the textbook quick sort (Lomuto partition, last-element pivot) needs n(n - 1)/2
comparisons and recursion depth n - 1 on sorted, reversed and all-equal order lists, and degrades badly on
deadlines booked in a few 15-minute slots.

Proposal A - "pick a representative pivot and split equal keys evenly":
  1. median-of-three pivot (first, middle, last element)  -> sorted / reversed lists split in the middle
  2. Hoare's two-pointer partition whose pointers STOP on keys equal to the pivot
                                                          -> runs of equal deadlines are split in two halves
  3. recurse into the smaller part and loop on the larger -> recursion depth <= log2 n on every input
Prediction (made before testing): about 1.2 n log2 n comparisons on random, sorted and reversed lists,
about n log2 n on all-equal lists, recursion depth <= log2 n everywhere.
Run:  py proposal_a_median3_hoare.py      (prototype check on the five Q2 input conditions, n = 2,000)
"""
import math
import random


class SortStats:
    """Operation counters (same meaning as in Q2: moves = element writes, a swap = 2)."""

    def __init__(self):
        self.comparisons = 0
        self.moves = 0
        self.max_depth = 0
        self.heapsort_fallbacks = 0     # not used by proposal A (kept for a common interface)


def quick_sort_a(a, stats=None):
    """Proposal A: median-of-three pivot + Hoare partition + smaller-part-first recursion. Returns stats."""
    stats = stats or SortStats()

    def swap(i, j):
        a[i], a[j] = a[j], a[i]
        stats.moves += 2

    def median_of_three(lo, hi):
        """Order a[lo] <= a[mid] <= a[hi] in place (3 comparisons); the median a[mid] is the pivot."""
        mid = (lo + hi) // 2
        stats.comparisons += 3
        if a[mid] < a[lo]:
            swap(lo, mid)
        if a[hi] < a[lo]:
            swap(lo, hi)
        if a[hi] < a[mid]:
            swap(mid, hi)
        return a[mid]

    def partition(lo, hi):
        """Hoare partition: returns j with a[lo..j] <= pivot <= a[j+1..hi] and lo <= j < hi."""
        pivot = median_of_three(lo, hi)
        i, j = lo - 1, hi + 1
        comps = 0
        while True:
            i += 1
            comps += 1
            while a[i] < pivot:                 # stops on keys >= pivot (equal keys stop the pointer)
                i += 1
                comps += 1
            j -= 1
            comps += 1
            while a[j] > pivot:                 # stops on keys <= pivot
                j -= 1
                comps += 1
            if i >= j:
                stats.comparisons += comps
                return j
            swap(i, j)

    def sort(lo, hi, depth):
        if depth > stats.max_depth:
            stats.max_depth = depth
        while lo < hi:
            p = partition(lo, hi)
            if p - lo < hi - p:                 # recurse into the smaller part ...
                sort(lo, p, depth + 1)
                lo = p + 1                      # ... and continue the loop with the larger part
            else:
                sort(p + 1, hi, depth + 1)
                hi = p

    sort(0, len(a) - 1, 0)
    return stats


def main():
    n = 2000
    rng = random.Random(42)
    base = [rng.randrange(57_600) for _ in range(n)]
    inputs = {"random": base, "sorted": sorted(base), "reverse": sorted(base, reverse=True),
              "slots": [rng.randrange(64) * 900 for _ in range(n)], "all-equal": [8100] * n}
    lg = math.log2(n)
    print("Q7 - Student A prototype: median-of-three + Hoare partition + smaller-part recursion (n = 2,000)")
    print(f"{'input':>10} | {'comparisons':>11} {'/ n lg n':>8} | {'moves':>7} | {'depth':>5} | correct")
    for name, data in inputs.items():
        a = list(data)
        st = quick_sort_a(a)
        print(f"{name:>10} | {st.comparisons:>11,} {st.comparisons / (n * lg):>8.2f} | {st.moves:>7,} | "
              f"{st.max_depth:>5} | {a == sorted(data)}")
    print(f"Prediction: ~1.2 n lg n on random/sorted/reverse, ~1.0 n lg n on all-equal, depth <= lg n = {lg:.1f}")


if __name__ == "__main__":
    main()
