"""Q2 tests - correctness of Merge Sort and the three Quick Sort variants against sorted(), plus exact counts.

Run:  py q2_tests.py      (prints PASS/FAIL per test and a final RESULT line)
"""
import math
import random

from q2_sorting import ALGORITHMS, merge_sort, quick_sort

results = []


def check(name, condition):
    """Record and print one test outcome."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


class Order:
    """A delivery order compared by deadline only (to test stability)."""

    def __init__(self, deadline, order_id):
        self.deadline, self.order_id = deadline, order_id

    def __lt__(self, other):
        return self.deadline < other.deadline

    def __le__(self, other):
        return self.deadline <= other.deadline


def main():
    rng = random.Random(42)
    print("Q2 TESTS - Merge Sort and Quick Sort (last / random / median-of-three pivot)")
    print("-" * 92)
    cases = []
    for n in range(0, 151):
        base = [rng.randrange(57_600) for _ in range(n)]
        cases += [base, sorted(base), sorted(base, reverse=True), [rng.randrange(4) for _ in range(n)], [7] * n]
    cases.append([-5, 3.5, 0, -2.25, 99, 3.5])
    for alg, fn in ALGORITHMS.items():
        ok = True
        for data in cases:
            a = list(data)
            fn(a)
            ok &= a == sorted(data)
        check(f"{alg:<13} sorts {len(cases)} lists (n = 0..150; random/sorted/reverse/4 values/all equal)", ok)

    orders = [Order(rng.randrange(6) * 900, i) for i in range(300)]
    a = list(orders)
    merge_sort(a)
    stable = all(a[i].deadline < a[i + 1].deadline or
                 (a[i].deadline == a[i + 1].deadline and a[i].order_id < a[i + 1].order_id) for i in range(299))
    check("Merge Sort is stable: equal deadlines keep their arrival order (300 orders, 6 slots)", stable)

    ok_cmp, ok_mov, ok_dep = True, True, True
    for k in range(1, 12):
        n = 2 ** k
        for data in (list(range(n)), list(range(n, 0, -1))):
            st = merge_sort(list(data))
            ok_cmp &= st.comparisons == n * k // 2
            ok_mov &= st.moves == 2 * n * k
            ok_dep &= st.max_depth == k
    check("Merge Sort on sorted and reversed n = 2^k: exactly (n/2) log2 n comparisons (k = 1..11)", ok_cmp)
    check("Merge Sort on n = 2^k: exactly 2 n log2 n moves and recursion depth log2 n (k = 1..11)", ok_mov and ok_dep)
    ok = True
    for n in range(2, 600, 7):
        k = math.ceil(math.log2(n))
        st = merge_sort([rng.random() for _ in range(n)])
        ok &= st.comparisons <= n * k - 2 ** k + 1 and st.max_depth == k
    check("Merge Sort on random data never exceeds n*ceil(lg n) - 2^ceil(lg n) + 1 comparisons (85 sizes)", ok)

    ok = all(quick_sort(list(range(n)), "last").comparisons == n * (n - 1) // 2 and
             quick_sort(list(range(n)), "last").max_depth == n - 1 for n in range(2, 400, 13))
    check("Quick-last on sorted data: exactly n(n-1)/2 comparisons and depth n - 1 (worst case)", ok)
    ok = all(quick_sort(list(range(n, 0, -1)), "last").comparisons == n * (n - 1) // 2 for n in range(2, 400, 13))
    check("Quick-last on reversed data: exactly n(n-1)/2 comparisons", ok)
    ok = all(quick_sort([5] * n, rule).comparisons >= n * (n - 1) // 2
             for n in range(2, 300, 11) for rule in ("last", "random", "median3"))
    check("All three pivot rules on all-equal data: at least n(n-1)/2 comparisons (Lomuto puts all on one side)", ok)
    ok = all(quick_sort(list(range(n)), "median3").max_depth <= math.ceil(math.log2(n + 1)) for n in range(2, 2000, 37))
    check("Quick-median3 on sorted data: recursion depth <= ceil(log2(n + 1)) (median = middle element)", ok)
    s1, s2 = quick_sort(list(range(500, 0, -1)), "random"), quick_sort(list(range(500, 0, -1)), "random")
    check("Quick-random is reproducible with a fixed seed (same counts twice)",
          (s1.comparisons, s1.moves) == (s2.comparisons, s2.moves))
    ok = True
    for n in (1000, 3000):
        bound = 2 * n * math.log2(n)
        for rule in ("random", "median3"):
            ok &= quick_sort([rng.random() for _ in range(n)], rule).comparisons < bound
    check("Quick-random/median3 on random data stay below 2 n log2 n comparisons (n = 1,000 and 3,000)", ok)

    print("-" * 92)
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
