"""Q1 tests - correctness of Max-Min and Binary Search against Python references, and exact comparison counts.

References: built-in max()/min(), bisect.bisect_left and the `in` operator.
Run:  py q1_tests.py      (prints PASS/FAIL per test and a final RESULT line)
"""
import bisect
import random

from q1_maxmin_binsearch import (binary_search, floor_log2, maxmin_dc, maxmin_formula_from_leaves,
                                 maxmin_formula_optimal, maxmin_naive, maxmin_pairwise)

results = []


def check(name, condition):
    """Record and print one test outcome."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


def ceil_log2(n):
    return (n - 1).bit_length()


def main():
    rng = random.Random(42)
    sizes = range(1, 301)
    arrays = {n: [rng.uniform(-40, 80) for _ in range(n)] for n in sizes}
    dup_arrays = {n: [rng.randint(20, 25) for _ in range(n)] for n in sizes}

    print("Q1 TESTS - Max-Min (naive, D&C 'half', D&C 'even', pairwise) and recursive Binary Search")
    print("-" * 96)
    for label, data in (("random reals", arrays), ("many duplicates", dup_arrays)):
        ok = True
        for n, a in data.items():
            ref = (max(a), min(a))
            ok &= maxmin_naive(a)[:2] == ref and maxmin_pairwise(a)[:2] == ref
            ok &= maxmin_dc(a, "half")[:2] == ref and maxmin_dc(a, "even")[:2] == ref
        check(f"Max-Min: all four methods equal (max(), min()) for n = 1..300, {label}", ok)
    check("Max-Min: one reading and all-equal readings handled",
          maxmin_dc([36.6], "half")[:2] == (36.6, 36.6) and maxmin_dc([5] * 77, "even")[:2] == (5, 5)
          and maxmin_pairwise([7])[:2] == (7, 7))
    check("Max-Min: naive scan makes exactly 2n - 2 comparisons (n = 1..300)",
          all(maxmin_naive(a)[2].comparisons == 2 * n - 2 for n, a in arrays.items()))
    check("Max-Min: rule 'even' makes exactly ceil(3n/2) - 2 comparisons (n = 1..300)",
          all(maxmin_dc(a, "even")[2].comparisons == maxmin_formula_optimal(n) for n, a in arrays.items()))
    check("Max-Min: pairwise loop makes exactly ceil(3n/2) - 2 comparisons (n = 1..300)",
          all(maxmin_pairwise(a)[2].comparisons == maxmin_formula_optimal(n) for n, a in arrays.items()))
    ok = True
    for n, a in arrays.items():
        s = maxmin_dc(a, "half")[2]
        ok &= s.comparisons == maxmin_formula_from_leaves(n, s.leaves1) and s.comparisons >= maxmin_formula_optimal(n)
    check("Max-Min: rule 'half' makes exactly (3n + L1)/2 - 2 >= ceil(3n/2) - 2 comparisons (n = 1..300)", ok)
    ok = all(maxmin_dc(arrays[2 ** k] if 2 ** k <= 300 else [rng.random() for _ in range(2 ** k)], rule)[2]
             .comparisons == 3 * 2 ** k // 2 - 2 for k in range(1, 11) for rule in ("half", "even"))
    check("Max-Min: both rules make exactly 3n/2 - 2 comparisons for n = 2, 4, ..., 1024", ok)
    check("Max-Min: recursion depth of rule 'half' = ceil(log2 n) - 1 (n = 2..300)",
          all(maxmin_dc(a, "half")[2].max_depth == ceil_log2(n) - 1 for n, a in arrays.items() if n >= 2))
    check("Max-Min: counts do not depend on the order of the readings (n = 257)",
          len({maxmin_dc(v, "half")[2].comparisons for v in (arrays[257], sorted(arrays[257]),
                                                              sorted(arrays[257], reverse=True))}) == 1)

    print("-" * 96)
    check("Binary search: empty manifest returns (-1, 0)", binary_search([], 5) == (-1, 0))
    ok_found, ok_absent, ok_worst, ok_max = True, True, True, True
    for n in range(1, 301):
        ids = sorted(rng.sample(range(0, 10 * n), n))
        ids = [2 * x for x in ids]
        probes_all = []
        for key in ids:
            idx, p = binary_search(ids, key)
            ok_found &= idx == bisect.bisect_left(ids, key)
            probes_all.append(p)
        for key in [ids[0] - 1] + [x + 1 for x in ids]:
            idx, p = binary_search(ids, key)
            ok_absent &= idx == -1 and floor_log2(n) <= p <= floor_log2(n) + 1
            probes_all.append(p)
        ok_worst &= max(probes_all) <= floor_log2(n) + 1
        ok_max &= max(probes_all) == floor_log2(n) + 1
    check("Binary search: every present ID found at its bisect_left index (n = 1..300)", ok_found)
    check("Binary search: every absent ID (one per gap) returns -1 after floor(lg n) or floor(lg n)+1 probes",
          ok_absent)
    check("Binary search: no look-up needs more than floor(log2 n) + 1 probes (n = 1..300)", ok_worst)
    check("Binary search: the worst case floor(log2 n) + 1 is reached for every n = 1..300", ok_max)
    ok = True
    for n in range(1, 201):
        ids = list(range(0, 3 * n, 3))
        total = sum(binary_search(ids, k)[1] for k in ids)
        ok &= total == sum(floor_log2(i) + 1 for i in range(1, n + 1))
    check("Binary search: total probes over all keys = sum(floor(log2 i) + 1) exactly (n = 1..200)", ok)
    ok = True
    for _ in range(300):
        a = sorted(rng.randint(0, 30) for _ in range(rng.randint(1, 60)))
        key = rng.randint(-2, 32)
        idx, _ = binary_search(a, key)
        ok &= (idx >= 0) == (key in a) and (idx < 0 or a[idx] == key)
    ok = True
    for n in range(1, 301):
        ids = list(range(10, 10 + 2 * n, 2))
        bound = floor_log2(n) + 1
        ok &= binary_search(ids, ids[(n - 1) // 2]) == ((n - 1) // 2, 1)          # middle: first probe
        ok &= binary_search(ids, ids[0])[0] == 0 and binary_search(ids, ids[0])[1] <= bound
        ok &= binary_search(ids, ids[-1])[0] == n - 1 and binary_search(ids, ids[-1])[1] <= bound
        for key in (ids[0] - 1, ids[n // 2] - 1, ids[-1] + 1):                      # below / gap / above
            idx, p = binary_search(ids, key)
            ok &= idx == -1 and floor_log2(n) <= p <= bound
    check("Binary search: designed cases - middle in 1 probe; first/last <= bound; absent below/gap/above -1",
          ok)
    check("Binary search: manifests with duplicate IDs agree with the `in` operator (300 cases)", ok)

    print("-" * 96)
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
