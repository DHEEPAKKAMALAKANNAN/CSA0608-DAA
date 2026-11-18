"""Q6 - Correctness tests for Median of Medians and Meet-in-the-Middle (CSA06 DAA, Assignment 3 - CO3).

References: sorted(a)[k] for selection; exhaustive enumeration and dynamic programming (bitset over capacities)
for payload packing. Each test prints PASS/FAIL; the last line is "RESULT: k/k tests passed".
Run:  py -3 q6_tests.py
"""
import itertools
import random

from q6_median_of_medians import (Counter, mom_select, quickselect_random, quickselect_first, sort_then_pick,
                                  merge_sort_count, insertion_sort_count, partition3, make_input)
from q6_meet_in_the_middle import (PackCounter, best_fill_brute_force, best_fill_mitm, best_fill_dp,
                                   sorted_subset_sums, mask_total)

results = []


def check(name, condition):
    """Record and print one test result."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


def all_ranks_ok(select, a):
    """True if select(a, k) == sorted(a)[k] for every rank k."""
    ref = sorted(a)
    return all(select(list(a), k) == ref[k] for k in range(len(a)))


def main():
    print("Q6 Median of Medians and Meet-in-the-Middle - correctness tests")
    print("-" * 96)
    rng = random.Random(42)
    # ---------------------------------------------------------------- (a) selection
    check("partition3 splits [5,1,5,9,3] around 5 into [1,3] | [5,5] | [9]",
          partition3([5, 1, 5, 9, 3], 5)[:3] == ([1, 3], [5, 5], [9]))
    g = [4, 2, 5, 1, 3]
    comps = insertion_sort_count(g)
    check(f"insertion sort of a group of 5 sorts it ({g}) with <= 10 comparisons ({comps})",
          g == [1, 2, 3, 4, 5] and comps <= 10)
    a = [rng.randint(0, 10**6) for _ in range(2000)]
    check("merge sort equals sorted() on 2,000 random integers", merge_sort_count(a, Counter()) == sorted(a))
    for grp in (3, 5, 7):
        ok = all(all_ranks_ok(lambda x, k: mom_select(x, k, Counter(), grp), [rng.randint(0, 50) for _ in range(n)])
                 for n in (1, 2, 3, 4, 5, 6, 7, 11, 25, 60))
        check(f"MoM g={grp}: every rank k of 10 small arrays (n = 1..60, duplicates) equals sorted(a)[k]", ok)
    for kind in ("random", "sorted", "duplicates"):
        a = make_input(kind, 5000)
        ref = sorted(a)
        ks = [0, 1, 2499, 4499, 4999]
        ok = all(mom_select(a, k, Counter()) == ref[k] for k in ks)
        check(f"MoM g=5 on the {kind!r} delivery-time input (n = 5,000): min, median, P90, max correct", ok)
    a = [7] * 1001
    check("MoM g=5 on 1,001 equal values returns 7", mom_select(a, 500, Counter()) == 7)
    a = list(range(3000, 0, -1))
    check("MoM g=5 on a reversed list: median = 1500", mom_select(a, 1499, Counter()) == 1500)
    ok = all(all_ranks_ok(lambda x, k: quickselect_random(x, k, Counter(), random.Random(s)),
                          [rng.randint(0, 30) for _ in range(40)]) for s in range(5))
    check("randomised Quickselect: all ranks of 5 random arrays (n = 40) correct", ok)
    ok = all_ranks_ok(lambda x, k: quickselect_first(x, k, Counter()), [rng.randint(0, 30) for _ in range(40)])
    check("first-pivot Quickselect: all ranks of a random array (n = 40) correct", ok)
    a = [rng.random() for _ in range(999)]
    check("sort-then-pick median equals sorted(a)[499]", sort_then_pick(a, 499, Counter()) == sorted(a)[499])
    a = list(range(1000))
    c = Counter()
    quickselect_first(a, 499, c)
    check(f"first-pivot Quickselect on sorted distinct input makes 2(k+1)n - k(k+1) = 750,500 comparisons "
          f"({c.comparisons:,})", c.comparisons == 750_500)
    c = Counter()
    mom_select([rng.random() for _ in range(50_000)], 25_000, c)
    check(f"MoM g=5 keeps at most 7n/10 + 6 elements per round, n >= 100 (max fraction {c.max_keep:.3f} <= 0.76)",
          c.max_keep <= 0.7 + 6 / 100)
    check(f"MoM g=5 uses fewer than 20n comparisons at n = 50,000 ({c.comparisons / 50_000:.2f} n)",
          c.comparisons < 20 * 50_000)
    # ---------------------------------------------------------------- (b) payload packing
    w = [2300, 1700, 4100, 900, 3600, 2800, 1250, 600, 3350, 1900]
    best, mask = best_fill_mitm(w, 9000, PackCounter())
    check("demo: MITM finds an exact 9,000 g load and the mask really weighs 9,000 g",
          best == 9000 and mask_total(w, mask) == 9000)
    check("brute force on [3, 5, 7], W = 11 gives 10 (3 + 7)", best_fill_brute_force([3, 5, 7], 11, PackCounter())[0] == 10)
    check("W = 0: best load is empty (0 g)", best_fill_mitm([300, 400, 500], 0, PackCounter())[0] == 0)
    check("every parcel heavier than W: best load 0 g", best_fill_mitm([900, 800, 700, 1000], 500, PackCounter())[0] == 0)
    check("W larger than all parcels together: take everything",
          best_fill_mitm([100, 200, 300, 400, 500], 10_000, PackCounter())[0] == 1500)
    check("single parcel (n = 1) that fits", best_fill_mitm([700], 800, PackCounter())[0] == 700)
    ok = True
    for trial in range(200):
        n = rng.randint(1, 14)
        ws = [rng.randint(1, 60) for _ in range(n)]
        W = rng.randint(0, sum(ws))
        exh = max(s for r in range(n + 1) for comb in itertools.combinations(ws, r) if (s := sum(comb)) <= W)
        bf = best_fill_brute_force(ws, W, PackCounter())
        mb = best_fill_mitm(ws, W, PackCounter(), "binary")
        mt = best_fill_mitm(ws, W, PackCounter(), "two_pointer")
        ok &= exh == bf[0] == mb[0] == mt[0] == best_fill_dp(ws, W)
        ok &= mask_total(ws, bf[1]) == bf[0] and mask_total(ws, mb[1]) == mb[0] and mask_total(ws, mt[1]) == mt[0]
    check("200 random instances (n = 1..14): brute force = MITM binary = MITM two-pointer = DP = itertools", ok)
    sums, _ = sorted_subset_sums([5, 1, 4], PackCounter())
    check("sorted subset sums of [5, 1, 4] = [0, 1, 4, 5, 5, 6, 9, 10]", sums == [0, 1, 4, 5, 5, 6, 9, 10])
    c = PackCounter()
    best_fill_brute_force(list(range(1, 17)), 50, c)
    check("brute force examines exactly 2^16 = 65,536 subsets with 65,535 additions",
          c.subsets == 65_536 and c.additions == 65_535)
    c = PackCounter()
    best_fill_mitm([rng.randint(200, 5000) for _ in range(20)], 20_000, c)
    check(f"MITM n = 20 stores 2 x 2^10 = 2,048 sums and makes <= 10 x 2^10 + 2^10 probes ({c.probes:,})",
          c.stored_sums == 2048 and c.probes <= 11 * 1024)
    print("-" * 96)
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
