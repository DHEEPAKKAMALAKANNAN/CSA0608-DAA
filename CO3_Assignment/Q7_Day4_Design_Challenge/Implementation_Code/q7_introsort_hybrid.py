"""Q7 - Joint final design: an introsort-style hybrid quick sort for the dispatch scheduler.

It combines the parts of both independent proposals that the comparison on identical datasets supported,
and adds the joint elements that neither proposal had:
  from A : median-of-three pivot; two-pointer (Hoare) scanning; recursion into the smaller part and a loop
           on the larger part (recursion depth <= log2 n)
  from B : keys equal to the pivot are finished in the partition step (3-way idea); insertion sort for
           sub-arrays of <= 16 orders
  joint  : (1) "fat" partition of Bentley & McIlroy (1993): Hoare's two-pointer scan that parks keys equal
               to the pivot at both ends and swaps them to the middle at the end. It keeps A's behaviour on
               sorted data (no element moves) and B's behaviour on equal keys (2n comparisons for all-equal).
           (2) depth budget of 2*floor(log2 n) partition levels; a path that exhausts it is finished by
               heapsort -> worst case O(n log n) GUARANTEED, even for adversarial inputs.
The first joint attempt (v1) paired A's pivot with B's Dijkstra partition; it is kept as hybrid_sort_v1 because
the experiments showed why it was rejected (Dijkstra's partition reverses the upper part of a sorted list).
Counters: comparisons, moves (element writes; a swap = 2), max_depth, heapsort_fallbacks.
Run:  py q7_introsort_hybrid.py      (small demo; the full comparison is q7_experiments.py)
"""
import math
import random


class SortStats:
    """Operation counters (same meaning as in Q2)."""

    def __init__(self):
        self.comparisons = 0
        self.moves = 0
        self.max_depth = 0
        self.heapsort_fallbacks = 0


def hybrid_sort(a, stats=None, cutoff=16, guard=True, partition="fat"):
    """Sort list a in place with the joint hybrid design; returns stats.

    partition='fat'      final design (Bentley-McIlroy fat partition)
    partition='dijkstra' rejected first attempt v1 (Dijkstra 3-way partition)
    guard=False          switches the depth budget off (only to show why it is needed)
    """
    stats = stats or SortStats()
    n = len(a)

    def swap(i, j):
        a[i], a[j] = a[j], a[i]
        stats.moves += 2

    def insertion_sort(lo, hi):                  # from proposal B
        comps = moves = 0
        for k in range(lo + 1, hi + 1):
            key = a[k]
            j = k - 1
            while j >= lo:
                comps += 1
                if a[j] > key:
                    a[j + 1] = a[j]
                    moves += 1
                    j -= 1
                else:
                    break
            if j + 1 != k:
                a[j + 1] = key
                moves += 1
        stats.comparisons += comps
        stats.moves += moves

    def heapsort(lo, hi):                        # joint safety net
        """Classic heapsort of a[lo..hi] (max-heap, sift-down); worst case O(m log m) for m elements."""
        stats.heapsort_fallbacks += 1
        m = hi - lo + 1

        def sift_down(root, end):               # heap indices are relative to lo
            while 2 * root + 1 <= end:
                child = 2 * root + 1
                if child + 1 <= end:
                    stats.comparisons += 1
                    if a[lo + child] < a[lo + child + 1]:
                        child += 1
                stats.comparisons += 1
                if a[lo + root] < a[lo + child]:
                    swap(lo + root, lo + child)
                    root = child
                else:
                    return
        for start in range(m // 2 - 1, -1, -1):  # build the heap bottom-up
            sift_down(start, m - 1)
        for end in range(m - 1, 0, -1):          # move the maximum to the end, restore the heap
            swap(lo, lo + end)
            sift_down(0, end - 1)

    def median_of_three(lo, hi):                 # from proposal A
        mid = (lo + hi) // 2
        stats.comparisons += 3
        if a[mid] < a[lo]:
            swap(lo, mid)
        if a[hi] < a[lo]:
            swap(lo, hi)
        if a[hi] < a[mid]:
            swap(mid, hi)
        return a[mid]

    def partition_fat(lo, hi, v):
        """Bentley-McIlroy fat partition; returns (lt, gt) with a[lo..lt-1] < v, a[lt..gt] = v, a[gt+1..hi] > v."""
        pa = pb = lo
        pc = pd = hi
        comps = 0
        while True:
            while pb <= pc:                      # left pointer (A's scan): passes keys < v
                x = a[pb]
                comps += 1
                if x < v:
                    pb += 1
                    continue
                comps += 1
                if x > v:
                    break
                if pa != pb:                     # key equal to v: park it at the left end (B's idea)
                    swap(pa, pb)
                pa += 1
                pb += 1
            while pc >= pb:                      # right pointer: passes keys > v
                x = a[pc]
                comps += 1
                if x > v:
                    pc -= 1
                    continue
                comps += 1
                if x < v:
                    break
                if pc != pd:                     # equal key: park it at the right end
                    swap(pc, pd)
                pd -= 1
                pc -= 1
            if pb > pc:
                break
            swap(pb, pc)                         # a[pb] > v and a[pc] < v: exchange them
            pb += 1
            pc -= 1
        stats.comparisons += comps
        s = min(pa - lo, pb - pa)                # move the left block of equal keys to the middle
        for k in range(s):
            swap(lo + k, pb - s + k)
        s = min(pd - pc, hi - pd)                # move the right block of equal keys to the middle
        for k in range(s):
            swap(pb + k, hi - s + 1 + k)
        return lo + (pb - pa), hi - (pd - pc)

    def partition_dijkstra(lo, hi, v):
        """Dijkstra 3-way partition (proposal B); used only by the rejected v1."""
        lt, i, gt = lo, lo, hi
        comps = 0
        while i <= gt:
            comps += 1
            if a[i] < v:
                if lt != i:
                    swap(lt, i)
                lt += 1
                i += 1
            else:
                comps += 1
                if a[i] > v:
                    swap(i, gt)
                    gt -= 1
                else:
                    i += 1
        stats.comparisons += comps
        return lt, gt

    split = partition_fat if partition == "fat" else partition_dijkstra

    def sort(lo, hi, budget, depth):
        if depth > stats.max_depth:
            stats.max_depth = depth
        while hi - lo + 1 > cutoff:
            if guard and budget == 0:            # too many partition levels on this path
                heapsort(lo, hi)
                return
            budget -= 1
            lt, gt = split(lo, hi, median_of_three(lo, hi))
            if lt - lo < hi - gt:                # smaller part first (recursion), larger part by the loop
                sort(lo, lt - 1, budget, depth + 1)
                lo = gt + 1
            else:
                sort(gt + 1, hi, budget, depth + 1)
                hi = lt - 1
        insertion_sort(lo, hi)

    budget = 2 * int(math.log2(n)) if n > 1 else 0
    sort(0, n - 1, budget, 0)
    return stats


def hybrid_sort_unguarded(a, stats=None):
    """Final design WITHOUT the depth budget (ablation; also the target of the adversary)."""
    return hybrid_sort(a, stats, guard=False)


def hybrid_sort_v1(a, stats=None):
    """Rejected first joint attempt: median-of-three + Dijkstra 3-way partition (+ cutoff, guard)."""
    return hybrid_sort(a, stats, partition="dijkstra")


def main():
    n = 2000
    rng = random.Random(42)
    base = [rng.randrange(57_600) for _ in range(n)]
    inputs = {"random": base, "sorted": sorted(base), "reverse": sorted(base, reverse=True),
              "slots": [rng.randrange(64) * 900 for _ in range(n)], "all-equal": [8100] * n}
    lg = math.log2(n)
    print("Q7 - Joint final design vs the rejected first attempt v1 (n = 2,000 orders)")
    print(f"{'design':>13} {'input':>10} | {'comparisons':>11} {'/ n lg n':>8} | {'moves':>7} | {'depth':>5} | "
          f"{'heapsort':>8} | correct")
    for label, fn in (("final (fat)", hybrid_sort), ("v1 Dijkstra", hybrid_sort_v1)):
        for name, data in inputs.items():
            a = list(data)
            st = fn(a)
            print(f"{label:>13} {name:>10} | {st.comparisons:>11,} {st.comparisons / (n * lg):>8.2f} | "
                  f"{st.moves:>7,} | {st.max_depth:>5} | {st.heapsort_fallbacks:>8} | {a == sorted(data)}")


if __name__ == "__main__":
    main()
