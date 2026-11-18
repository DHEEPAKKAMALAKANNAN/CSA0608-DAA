"""SwiftLogix CO3 case study - test harness for all four modules.

Checks every algorithm variant against the test cases in test_cases/*.json (expected outputs produced by
independent references: sorted(), bisect, numpy), against the generated datasets, against randomised
inputs, and checks the operation counts against the closed forms derived in Part 4.

Run:  py -3 run_all_tests.py              all modules
      py -3 run_all_tests.py --module 3   one module only
Prints one PASS/FAIL line per test and a final 'RESULT: k/k tests passed'.
"""
import argparse
import bisect
import csv
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for sub in ("Module_1_Merge_Sort", "Module_2_Quick_Sort", "Module_3_Binary_Search",
            "Module_4_Strassen_Matrix_Multiplication"):
    sys.path.insert(0, str(ROOT / sub / "Source_Code"))

import binary_search as m3  # noqa: E402
import merge_sort as m1  # noqa: E402
import quick_sort as m2  # noqa: E402
import strassen as m4  # noqa: E402

RESULT = {"passed": 0, "total": 0}


def check(name, ok, detail=""):
    RESULT["total"] += 1
    RESULT["passed"] += bool(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


def load_cases(name):
    with open(HERE / "test_cases" / name, encoding="utf-8") as fh:
        return json.load(fh)["cases"]


def lg_ceil(n):
    return (n - 1).bit_length()


# ----------------------------------------------------------------------------- Module 1
def test_m1():
    print("--- Module 1: merge sort (top-down, hybrid n0=16, hybrid n0=4, natural, insertion baseline)")
    variants = {"top-down": m1.merge_sort, "hybrid16": m1.merge_sort_hybrid,
                "hybrid4": lambda a, key=None: m1.merge_sort_hybrid(a, key=key, cutoff=4),
                "natural": m1.natural_merge_sort, "insertion": m1.insertion_sort}
    for case in load_cases("m1_merge_sort_cases.json"):
        key = (lambda r: r[0]) if "key" in case else None
        bad = [v for v, f in variants.items() if f(case["input"], key=key) != case["expected"]]
        check(f"M1 case '{case['name']}' - 5 variants == expected", not bad, ", ".join(bad))
    events = m1.load_events()
    out = [r["event_id"] for r in m1.merge_sort(events, key=m1.event_key)]
    check("M1 given sample -> E02 E10 E06 E11 E05 E08 E04 E09 E01 E03 E12 E07 (stable)",
          out == "E02 E10 E06 E11 E05 E08 E04 E09 E01 E03 E12 E07".split())
    gen = m1.load_events(HERE / "datasets" / "generated" / "m1_shipment_events_5000.csv")
    ref = [r["event_id"] for r in sorted(gen, key=m1.event_key)]
    bad = [v for v, f in variants.items() if v != "insertion" and [r["event_id"] for r in f(gen, key=m1.event_key)] != ref]
    check("M1 generated 5,000 hub-feed events - stable order == sorted()", not bad, ", ".join(bad))
    rng = random.Random(1)
    bad = 0
    for _ in range(300):
        a = [rng.randint(0, 50) for _ in range(rng.randint(0, 300))]
        bad += any(f(a) != sorted(a) for f in variants.values())
    check("M1 300 random lists (n <= 300, many duplicates) - all variants == sorted()", bad == 0, f"{bad} failures")
    ok = True
    for n in range(1, 301):
        c = m1.OpCounter()
        m1.merge_sort([rng.random() for _ in range(n)], counter=c)
        ok &= c.comparisons <= n * lg_ceil(n) - 2 ** lg_ceil(n) + 1 and c.calls == 2 * n - 1
    check("M1 comparisons <= n*ceil(lg n) - 2^ceil(lg n) + 1 and calls = 2n - 1, n = 1..300", ok)
    ok = True
    for k in range(1, 13):
        n = 2 ** k
        c = m1.OpCounter()
        m1.merge_sort(list(range(n)), counter=c)
        c2 = m1.OpCounter()
        m1.merge_sort([rng.random() for _ in range(n)], counter=c2)
        ok &= c.comparisons == n * k // 2 and c2.moves == 2 * n * k and c.max_depth == k
    check("M1 n = 2^k: sorted input costs (n/2) lg n comparisons, moves = 2n lg n, depth = lg n", ok)
    ok = True
    for n in (640, 6400, 64000):
        size = n // 64
        a = [x for h in range(64) for x in sorted(rng.random() for _ in range(size))]
        c = m1.OpCounter()
        ok &= m1.natural_merge_sort(a, counter=c) == sorted(a) and c.comparisons <= (n - 1) + 6 * n
    check("M1 natural merge sort on 64 sorted hub feeds: comparisons <= (n - 1) + n lg 64", ok)


# ----------------------------------------------------------------------------- Module 2
def run_qs(variant, a, c=None):
    b = list(a)
    if variant == "3way":
        m2.quick_sort_3way(b, counter=c)
    elif variant == "hybrid":
        m2.quick_sort_hybrid(b, counter=c)
    elif variant == "hybrid4":
        m2.quick_sort_hybrid(b, counter=c, cutoff=4)
    elif variant == "hybrid-fixed":
        m2.quick_sort_hybrid(b, counter=c, pivot_sample="fixed", cutoff=4)
    elif variant == "heap-only":
        m2.quick_sort_hybrid(b, counter=c, cutoff=1, depth_limit=0)
    else:
        m2.quick_sort(b, pivot=variant, counter=c)
    return b


QS_VARIANTS = ["last", "median3", "random", "3way", "hybrid", "hybrid4", "hybrid-fixed", "heap-only"]


def test_m2():
    print("--- Module 2: quick sort (last, median3, random, 3way, hybrid, hybrid n0=4, hybrid fixed-m3, heap-only)")
    for case in load_cases("m2_quick_sort_cases.json"):
        bad = [v for v in QS_VARIANTS if run_qs(v, case["input"]) != case["expected"]]
        check(f"M2 case '{case['name']}' - 8 variants == expected", not bad, ", ".join(bad))
    with open(HERE / "datasets" / "generated" / "m2_priority_scores_5000.csv", encoding="utf-8") as fh:
        scores = [int(r["priority_score"]) for r in csv.DictReader(fh)]
    bad = [v for v in QS_VARIANTS if run_qs(v, scores) != sorted(scores)]
    check("M2 generated 5,000 priority scores (0..100) - 8 variants == sorted()", not bad, ", ".join(bad))
    rng = random.Random(2)
    bad = 0
    for _ in range(300):
        a = [rng.randint(-20, 20) for _ in range(rng.randint(0, 200))]
        bad += any(run_qs(v, a) != sorted(a) for v in QS_VARIANTS)
    check("M2 300 random lists (n <= 200) - all variants == sorted()", bad == 0, f"{bad} failures")
    ok = True
    for n in range(2, 201):
        c = m2.OpCounter()
        run_qs("last", list(range(n)), c)
        ok &= c.comparisons == n * (n - 1) // 2 and c.max_depth == n - 1
    check("M2 baseline on sorted input: comparisons = n(n-1)/2 and depth = n - 1, n = 2..200", ok)
    ok = True
    for n in range(2, 201):
        c = m2.OpCounter()
        run_qs("last", [5] * n, c)
        ok &= c.comparisons == n * (n - 1) // 2
    check("M2 baseline on all-equal input: comparisons = n(n-1)/2 (Lomuto worst case)", ok)
    c = m2.OpCounter()
    out = run_qs("heap-only", [rng.random() for _ in range(5000)], c)
    check("M2 depth budget 0 forces the heap-sort fallback and still sorts", out == sorted(out) and c.fallbacks == 1)
    ok = True
    for data in ([rng.random() for _ in range(20000)], list(range(20000)), [rng.randint(0, 100) for _ in range(20000)],
                 list(range(20000, 0, -1))):
        c = m2.OpCounter()
        ok &= run_qs("hybrid", data, c) == sorted(data) and c.max_depth <= 15 and c.fallbacks == 0
    check("M2 hybrid on random/sorted/scores/reversed n = 20,000: depth <= lg n = 14.3, no fallback", ok)
    ok = True
    for _ in range(200):
        a = [rng.randint(0, 9) for _ in range(rng.randint(1, 60))]
        lt, gt = m2.partition_3way(a, 0, len(a) - 1, m2.OpCounter())
        v = a[lt]
        ok &= all(x < v for x in a[:lt]) and all(x == v for x in a[lt:gt + 1]) and all(x > v for x in a[gt + 1:])
    check("M2 3-way partition invariant  A[<lt] < v = A[lt..gt] < A[>gt]  (200 random arrays)", ok)
    ok = True
    for _ in range(200):
        a = [rng.randint(0, 50) for _ in range(rng.randint(1, 60))]
        p = m2.partition_lomuto(a, 0, len(a) - 1, m2.OpCounter())
        ok &= all(x <= a[p] for x in a[:p]) and all(x > a[p] for x in a[p + 1:])
    check("M2 Lomuto partition invariant  A[<p] <= pivot < A[>p]  (200 random arrays)", ok)


# ----------------------------------------------------------------------------- Module 3
def test_m3():
    print("--- Module 3: binary search (iterative, recursive), interpolation, guarded interpolation, linear")
    variants = {"binary": m3.binary_search, "recursive": m3.binary_search_recursive,
                "interpolation": m3.interpolation_search, "guarded": m3.guarded_interpolation_search,
                "linear": m3.linear_search}
    for case in load_cases("m3_binary_search_cases.json"):
        bad = [v for v, f in variants.items()
               if [f(case["keys"], q) for q in case["queries"]] != case["expected"]]
        check(f"M3 case '{case['name']}', queries: {len(case['queries'])} - 5 variants == bisect", not bad,
              ", ".join(bad))
    with open(HERE / "datasets" / "generated" / "m3_tracking_index_20000.csv", encoding="utf-8") as fh:
        keys = [int(r["tracking_id"][3:]) for r in csv.DictReader(fh)]
    with open(HERE / "datasets" / "generated" / "m3_lookup_queries_2000.csv", encoding="utf-8") as fh:
        qs = [(int(r["tracking_id"][3:]), r["expected"]) for r in csv.DictReader(fh)]
    bad = 0
    for q, label in qs:
        p = bisect.bisect_left(keys, q)
        ref = p if p < len(keys) and keys[p] == q else -1
        bad += any(f(keys, q) != ref for v, f in variants.items() if v != "linear") or ((ref >= 0) != (label == "present"))
    check("M3 generated index 20,000 IDs x 2,000 queries - all variants == bisect == labels", bad == 0, f"{bad} bad")
    ok = True
    for n in range(1, 301):
        ks = list(range(0, 3 * n, 3))
        for t in list(ks) + [k + 1 for k in ks] + [-1]:
            c = m3.OpCounter()
            m3.binary_search(ks, t, counter=c)
            ok &= c.comparisons <= n.bit_length()
    check("M3 every hit and every gap, n = 1..300: comparisons <= floor(lg n) + 1", ok)
    s_tot, e_tot = {0: 0}, {0: 0}
    for n in range(1, 201):
        left = (n - 1) // 2
        s_tot[n] = n + s_tot[left] + s_tot[n - 1 - left]
        e_tot[n] = n + 1 + e_tot[left] + e_tot[n - 1 - left]
    ok = True
    for n in range(1, 201):
        ks = list(range(0, 2 * n, 2))
        hit = fail = 0
        for t in ks:
            c = m3.OpCounter()
            m3.binary_search(ks, t, counter=c)
            hit += c.comparisons
        for t in [-1] + [k + 1 for k in ks]:
            c = m3.OpCounter()
            m3.binary_search(ks, t, counter=c)
            fail += c.comparisons
        ok &= hit == s_tot[n] and fail == e_tot[n]
    check("M3 total counted comparisons == S(n) (hits) and E(n) (misses) recurrences, n = 1..200", ok)
    rng = random.Random(3)
    ok = True
    for _ in range(500):
        t = rng.choice(keys) if rng.random() < 0.5 else rng.randrange(10 ** 9, 10 ** 10)
        c1, c2 = m3.OpCounter(), m3.OpCounter()
        ok &= m3.binary_search(keys, t, counter=c1) == m3.binary_search_recursive(keys, t, counter=c2) \
            and c1.comparisons == c2.comparisons
    check("M3 recursive and iterative versions: same answers and same comparison counts (500 queries)", ok)
    clustered = []
    for base in sorted(rng.sample(range(10 ** 9, 9 * 10 ** 9), 8)):
        k = base
        for _ in range(2500):
            k += rng.randint(1, 3)
            clustered.append(k)
    ok, worst = True, 0
    bound = 2 * (len(clustered).bit_length())
    for t in rng.sample(clustered, 2000):
        c = m3.OpCounter()
        ok &= clustered[m3.guarded_interpolation_search(clustered, t, counter=c)] == t
        worst = max(worst, c.probes)
    check(f"M3 guarded interpolation on clustered IDs: probes <= 2(floor(lg n) + 1) = {bound}", ok and worst <= bound,
          f"worst {worst}")


# ----------------------------------------------------------------------------- Module 4
def test_m4():
    print("--- Module 4: Strassen (cutoff 1 / 2 with power-of-two padding, cutoff 4 / 8 with minimal padding), naive")
    variants = {"naive": m4.naive_multiply,
                "pure": lambda A, B: m4.strassen_multiply(A, B, cutoff=1),
                "cut2": lambda A, B: m4.strassen_multiply(A, B, cutoff=2),
                "cut4-min": lambda A, B: m4.strassen_multiply(A, B, cutoff=4, padding="minimal"),
                "cut8-min": lambda A, B: m4.strassen_multiply(A, B, cutoff=8, padding="minimal")}
    for case in load_cases("m4_strassen_cases.json"):
        bad = [v for v, f in variants.items() if f(case["A"], case["B"]) != case["expected"]]
        check(f"M4 case '{case['name']}' - 5 variants == numpy", not bad, ", ".join(bad))
    gen = HERE / "datasets" / "generated"
    mats = []
    for name in ("m4_demand_64x64.csv", "m4_cost_64x64.csv"):
        with open(gen / name, encoding="utf-8") as fh:
            mats.append([[int(x) for x in row] for row in list(csv.reader(fh))[1:]])
    ref = (np.array(mats[0]) @ np.array(mats[1])).tolist()
    bad = [v for v, f in variants.items() if f(*mats) != ref]
    check("M4 generated 64 x 64 demand x cost - 5 variants == numpy", not bad, ", ".join(bad))
    ok = True
    rng = random.Random(4)
    for k in range(0, 7):
        n = 2 ** k
        A = [[rng.randint(0, 9) for _ in range(n)] for _ in range(n)]
        for cut in (1, 4, 8):
            c = m4.OpCounter()
            m4.strassen_multiply(A, A, cutoff=cut, counter=c)
            ok &= (c.mults, c.adds) == m4.strassen_ops(n, cut)
    check("M4 counted (mults, adds) == closed form strassen_ops(n, n0), n = 1..64, n0 = 1, 4, 8", ok)
    ok = all(m4.strassen_ops(2 ** k, 1) == (7 ** k, 6 * (7 ** k - 4 ** k)) for k in range(0, 12))
    check("M4 pure Strassen: M(n) = 7^k = n^lg7 and A(n) = 6(7^k - 4^k) for n = 2^k, k = 0..11", ok)
    ok = (m4.padded_size(600, 64, "minimal") == 608 and m4.padded_size(600, 64, "pow2") == 1024 and
          m4.padded_size(100, 32, "minimal") == 100 and m4.padded_size(100, 16, "minimal") == 104 and
          m4.padded_size(129, 32, "minimal") == 136 and m4.padded_size(1024, 8, "minimal") == 1024 and
          m4.padded_size(5, 1, "minimal") == 8)
    check("M4 PadSize: 600->608 (n0 64), 100->100 (n0 32), 100->104 (n0 16), 129->136 (n0 32), 5->8 (n0 1)", ok)
    bad = 0
    for _ in range(30):
        n = rng.randint(1, 40)
        A = [[rng.randint(-9, 9) for _ in range(n)] for _ in range(n)]
        B = [[rng.randint(-9, 9) for _ in range(n)] for _ in range(n)]
        cut = rng.choice([1, 2, 3, 5, 8, 16])
        mode = rng.choice(["pow2", "minimal"])
        bad += m4.strassen_multiply(A, B, cutoff=cut, padding=mode) != (np.array(A) @ np.array(B)).tolist()
    check("M4 30 random sizes 1..40 x random cutoff x padding policy == numpy", bad == 0, f"{bad} failures")
    try:
        m4.strassen([[1] * 3] * 3, [[1] * 3] * 3, cutoff=1)
        raised = False
    except ValueError:
        raised = True
    check("M4 odd size above the cutoff without padding is rejected (ValueError)", raised)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", type=int, choices=[1, 2, 3, 4])
    args = ap.parse_args()
    for k, fn in ((1, test_m1), (2, test_m2), (3, test_m3), (4, test_m4)):
        if args.module in (None, k):
            fn()
    print(f"RESULT: {RESULT['passed']}/{RESULT['total']} tests passed")
    sys.exit(0 if RESULT["passed"] == RESULT["total"] else 1)


if __name__ == "__main__":
    main()
