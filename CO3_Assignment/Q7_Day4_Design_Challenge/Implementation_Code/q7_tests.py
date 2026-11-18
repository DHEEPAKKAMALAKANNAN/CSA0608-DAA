"""Q7 tests - correctness of the original, both proposals and the joint designs; adversary consistency; guarantees.

Run:  py q7_tests.py      (prints PASS/FAIL per test and a final RESULT line)
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
Q7 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(Q7, "Student_A_Initial_Design"))
sys.path.insert(0, os.path.join(Q7, "Student_B_Initial_Design"))
sys.path.insert(0, os.path.join(os.path.dirname(Q7), "Q2_MergeSort_QuickSort", "Implementation_Code"))

from proposal_a_median3_hoare import quick_sort_a  # noqa: E402
from proposal_b_threeway_cutoff import quick_sort_b  # noqa: E402
from q2_sorting import quick_sort  # noqa: E402
from q7_adversary import make_killer  # noqa: E402
from q7_introsort_hybrid import hybrid_sort, hybrid_sort_unguarded, hybrid_sort_v1  # noqa: E402

sys.setrecursionlimit(200_000)
results = []
VARIANTS = {"Baseline": lambda a: quick_sort(a, "last"), "A": quick_sort_a, "B": quick_sort_b,
            "Joint-v1": hybrid_sort_v1, "Joint": hybrid_sort, "Joint-unguarded": hybrid_sort_unguarded}


def check(name, condition):
    """Record and print one test outcome."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


def natural_inputs(n, rng):
    base = [rng.randrange(57_600) for _ in range(n)]
    return [base, sorted(base), sorted(base, reverse=True), [rng.randrange(64) * 900 for _ in range(n)], [8100] * n]


def main():
    rng = random.Random(42)
    print("Q7 TESTS - original quick sort, proposals A and B, joint designs, adversary")
    print("-" * 100)
    cases = []
    for n in range(0, 151):
        cases += natural_inputs(n, rng) + [[rng.randrange(3) for _ in range(n)]]
    cases.append([-3.5, 2, 2, -7, 0.25, 99, -7])
    for name, fn in VARIANTS.items():
        ok = True
        for data in cases:
            a = list(data)
            fn(a)
            ok &= a == sorted(data)
        check(f"{name:<15} sorts {len(cases)} lists (n = 0..150: random/sorted/reverse/slots/all-equal/3 values)", ok)

    ok = all(quick_sort_a(list(d)).max_depth <= math.log2(n) for n in (100, 1000, 3000)
             for d in natural_inputs(n, rng))
    check("A: recursion depth <= log2 n on all five natural inputs (n = 100, 1,000, 3,000)", ok)
    ok = all(quick_sort_b([5] * n).comparisons == 2 * n for n in range(17, 3000, 97))
    check("B: an all-equal list costs exactly 2n comparisons (one 3-way partition)", ok)
    ok = all(hybrid_sort([5] * n).comparisons == 2 * n + 3 for n in range(17, 3000, 97))
    check("Joint: an all-equal list costs exactly 2n + 3 comparisons (median-of-3 + one fat partition)", ok)
    ok = True
    for n in (100, 1000, 5000):
        for d in natural_inputs(n, rng):
            st = hybrid_sort(list(d))
            ok &= st.max_depth <= math.log2(n) and st.heapsort_fallbacks == 0
    check("Joint: depth <= log2 n and no heapsort fallback on the natural inputs (n = 100, 1,000, 5,000)", ok)
    ok = all(hybrid_sort(list(range(n))).moves <= n // 2 for n in (1000, 4000))
    check("Joint: an already sorted list is left almost untouched (moves <= n/2)", ok)
    v1 = hybrid_sort_v1(list(range(4000)))
    check(f"Joint-v1 (rejected): sorted input triggers heapsort fallbacks ({v1.heapsort_fallbacks}) - the reason for "
          f"rejecting it", v1.heapsort_fallbacks > 0)

    print("-" * 100)
    ok_perm, ok_replay = True, True
    for fn in (quick_sort_a, quick_sort_b, hybrid_sort_unguarded):
        for n in (50, 300, 1000):
            killer, attacked = make_killer(fn, n)
            ok_perm &= sorted(killer) == list(range(n))
            ok_replay &= fn(list(killer)).comparisons == attacked
    check("Adversary: every killer input is a permutation of 0..n-1 (A, B seed 42, Joint unguarded)", ok_perm)
    check("Adversary: replaying the sort on its killer repeats exactly the comparisons made under attack", ok_replay)
    ok_quad, ok_guard, ok_fb = True, True, True
    for n in (500, 1000, 2000):
        killer = make_killer(hybrid_sort_unguarded, n)[0]
        ok_quad &= hybrid_sort_unguarded(list(killer)).comparisons >= n * n / 8
        st = hybrid_sort(list(killer))
        ok_guard &= st.comparisons <= 6 * n * math.log2(n)
        ok_fb &= st.heapsort_fallbacks >= 1
    check("Killer-J forces the unguarded joint design to >= n^2/8 comparisons (quadratic)", ok_quad)
    check("With the depth budget the same killers cost <= 6 n log2 n comparisons (O(n log n) guarantee)", ok_guard)
    check("The guard is what saves it: at least one heapsort fallback on every killer-J input", ok_fb)
    ok = True
    for n in (500, 1000):
        killer = make_killer(quick_sort_a, n)[0]
        ok &= quick_sort_a(list(killer)).comparisons >= n * n / 8
    check("Killer-A forces proposal A to >= n^2/8 comparisons (median-of-3 is deterministic)", ok)
    killer = make_killer(quick_sort_b, 1000)[0]
    check("Killer-B hurts B only with the attacked seed: seed 42 quadratic, seed 7 below 2 n log2 n",
          quick_sort_b(list(killer)).comparisons >= 1000 ** 2 / 8 and
          quick_sort_b(list(killer), seed=7).comparisons < 2 * 1000 * math.log2(1000))
    data = natural_inputs(2000, rng)[0]
    s1, s2 = hybrid_sort(list(data)), hybrid_sort(list(data))
    check("Joint is deterministic: the same batch always costs the same work",
          (s1.comparisons, s1.moves, s1.max_depth) == (s2.comparisons, s2.moves, s2.max_depth))

    print("-" * 100)
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
