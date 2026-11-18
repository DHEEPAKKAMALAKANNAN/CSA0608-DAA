"""ShopSphere audit - automated test suite for every module program (Appendix D of the report).

Each test compares a derived closed form or a reference answer with what the hand-written code actually
does (operation counters, search results, recursion counters) and prints one PASS/FAIL line.
The last line is "RESULT: k/k tests passed". Exit code 0 only if every test passes.
"""
import bisect
import math
import random
import sys
from fractions import Fraction

import f_bound_proof_check as fpc
import m1_duplicate_detector as m1
import m2_rate_limiter as m2
import m3_product_search as m3
import m4_m5_recurrences as rec
import m4_m5_simulation as sim
import scalability_estimates as se

RESULTS = []


def test(description, expected, actual):
    """Record and print one test in the form 'PASS  description  (expected ..., got ...)'."""
    ok = expected == actual
    RESULTS.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {description:<60} (expected {expected}, got {actual})")


def m1_tests():
    demo = [("Bottle", "s7"), ("Lamp", "s2"), ("Bottle", "s3"), ("Bottle", "s7"), ("Mat", "s2"),
            ("Lamp", "s2")]
    marked, comps, sellers = m1.detect_duplicates_nested(demo)
    test("M1 hand-made catalogue: duplicates marked", [3, 5], sorted(marked))
    test("M1 hand-made catalogue: title comparisons = 6*5/2", 15, comps)
    test("M1 seller compared only when titles match", 4, sellers)
    test("M1 n = 0, 1, 2 -> 0, 0, 1 comparisons", [0, 0, 1],
         [m1.detect_duplicates_nested(demo[:k])[1] for k in (0, 1, 2)])
    test("M1 counted == n(n-1)/2 for n = 1..120", True,
         all(m1.detect_duplicates_nested(m1.make_catalogue(n, 0, seed=n))[1] == n * (n - 1) // 2
             for n in range(1, 121)))
    cat = m1.make_catalogue(980, 20, seed=5)
    ref = m1.reference_duplicates(cat)
    test("M1 nested loops find exactly the 20 planted duplicates", (True, 20),
         (m1.detect_duplicates_nested(cat)[0] == ref, len(ref)))
    test("M1 redesign A (hash set) == reference", True, m1.detect_duplicates_hash(cat)[0] == ref)
    test("M1 redesign B (sort + scan) == reference", True, m1.detect_duplicates_sort_scan(cat)[0] == ref)
    test("M1 C(10^6) = 499,999,500,000", 499_999_500_000, m1.closed_form(10**6))


def m2_tests():
    test("M2 n = 1,024: Audit calls = 1 + 2 + ... + 512", 1023, m2.run_rate_limiter([0] * 1024))
    test("M2 counted == 2^ceil(log2 n) - 1 for n = 1..1500", True,
         all(m2.run_rate_limiter([0] * n) == m2.closed_form(n) for n in range(1, 1501)))
    test("M2 n = 10^6 counted audits", 1_048_575, m2.run_rate_limiter([0] * 10**6))
    test("M2 n - 1 <= A(n) <= 2n - 3 for n = 2..10^6", True,
         all(n - 1 <= m2.closed_form(n) <= 2 * n - 3 for n in range(2, 10**6 + 1)))
    test("M2 A(n) = n - 1 for every power of two 2..2^30", True,
         all(m2.closed_form(2**k) == 2**k - 1 for k in range(1, 31)))


def m3_tests():
    rng = random.Random(3)
    index = m3.make_index(1000, seed=3)
    shuffled = index[:]
    rng.shuffle(shuffled)
    test("S1 finds every key at its true position (n = 1,000)", True,
         all(shuffled[m3.sequential_search(shuffled, k)[0]] == k for k in index))
    test("S2 iterative == bisect for all 1,000 keys", True,
         all(m3.binary_search_iterative(index, k)[0] == bisect.bisect_left(index, k) for k in index))
    test("S2 absent keys (all 1,001 gaps) -> -1", True,
         all(m3.binary_search_iterative(index, k)[0] == -1 for k in m3.gap_keys(index)))
    test("S2 recursive == iterative (positions and comparisons)", True,
         all(m3.binary_search_recursive(index, k)[:2] == m3.binary_search_iterative(index, k)
             for k in index + m3.gap_keys(index)))
    test("S2 worst case == floor(log2 n) + 1 for every n = 1..300", True,
         all(m3.s2_profile(m3.make_index(n, seed=n))[2] == n.bit_length() for n in range(1, 301)))
    test("S2 recursion depth <= floor(log2 n) + 2 for n = 1..300", True,
         all(m3.s2_profile(m3.make_index(n, seed=n), recursive=True)[4] <= n.bit_length() + 1
             for n in range(1, 301)))
    test("T(n) = T(n/2) + 1 unfolds to floor(log2 n) + 1, n = 1..10^5", True,
         all(m3.recurrence_T(n) == math.floor(math.log2(n)) + 1 for n in range(1, 10**5 + 1)))
    test("S2 best case = 1 comparison (middle key)", 1,
         m3.binary_search_iterative(index, index[(len(index) - 1) // 2])[1])
    test("S1 best / worst = 1 / n (n = 1,000)", (1, 1000),
         (m3.sequential_search(index, index[0])[1], m3.sequential_search(index, -1)[1]))
    succ = Fraction(sum(m3.sequential_search(index, k)[1] for k in index), 1000)
    test("S1 average successful = (n+1)/2 (all 1,000 searches)", Fraction(1001, 2), succ)
    test("S1 average with p = 1/2 = p(n+1)/2 + n(1-p) (n = 1,000)",
         m3.s1_average_formula(1000, Fraction(1, 2)),
         Fraction(1, 2) * succ + Fraction(1, 2) * 1000)
    test("S1 average for n = 10^6, p = 0.5", 750000.25, float(m3.s1_average_formula(10**6, Fraction(1, 2))))


def m4_m5_tests():
    test("M4 current T(2^k) == 2n^2 - n, k = 0..30", True,
         all(rec.T_power_of_two("M4 current", k) == 2 * 4**k - 2**k for k in range(31)))
    test("M4 redesign T(2^k) == n log2 n + n, k = 0..30", True,
         all(rec.T_power_of_two("M4 redesign", k) == 2**k * k + 2**k for k in range(31)))
    test("M5 T(2^k) == n k(k+1)/2 + n, k = 0..30", True,
         all(rec.T_power_of_two("M5", k) == 2**k * k * (k + 1) // 2 + 2**k for k in range(31)))
    test("M4 current engine counter == 2n^2 - n, n = 2^0..2^8", True,
         all(sim.count_ops(sim.recommend, [0.5] * 2**k, True) == 2 * 4**k - 2**k for k in range(9)))
    test("M4 redesign engine counter == n log2 n + n, n = 2^0..2^12", True,
         all(sim.count_ops(sim.recommend, [0.5] * 2**k, False) == 2**k * (k + 1) for k in range(13)))
    rng = random.Random(9)
    records = [rng.uniform(1, 999) for _ in range(256)]
    flag = [True]
    sim.sales_analytics(records, [0], flag)
    test("M5 engine sorts every level correctly (n = 256)", True, flag[0])
    test("M5 doubling ratio at n = 2^19 is between 2 and 4", True,
         2 < rec.T_power_of_two("M5", 20) / rec.T_power_of_two("M5", 19) < 4)
    test("M4 current doubling ratio at n = 2^19 rounds to 4.000", "4.000",
         f"{rec.T_power_of_two('M4 current', 20) / rec.T_power_of_two('M4 current', 19):.3f}")


def f_tests():
    test("(f) 3n^2 <= f(n) <= 63n^2 for n = 1..10^5", 0, fpc.violations(3, 63, 1, 10**5))
    test("(f) 3n^2 <= f(n) <= 4n^2 for n = 60..10^5", 0, fpc.violations(3, 4, 60, 10**5))
    test("(f) n = 59 violates f(n) <= 4n^2 (n0 = 60 is minimal)", True, fpc.f(59) > 4 * 59**2)
    test("(f) not O(n): witness n = c//3 + 1 beats c*n for c = 10..10^9", True,
         all(fpc.f(c // 3 + 1) > c * (c // 3 + 1) for c in (10, 100, 10**4, 10**6, 10**9)))


def g_tests():
    later = se.estimates(10**6)
    verdicts = {name: ok for name, (_, _, ok) in later.items() if se.MODULES[name][2]}
    failing = {name for name, ok in verdicts.items() if not ok}
    test("(g) n = 10^6 misses window: M1, M4 current, report generator", True,
         failing == {"M1 duplicate detector", "M4 current (4 parts)", "Report generator f(n)"})
    test("(g) every batch module fits the window at n = 10^5", True,
         all(ok for name, (_, _, ok) in se.estimates(10**5).items() if se.MODULES[name][2]))
    test("(g) M1 at 10^6: 5,000 s (83.3 min)", "83.3", f"{later['M1 duplicate detector'][1] / 60:.1f}")
    m1_cost = se.MODULES["M1 duplicate detector"][1]
    test("(g) largest n for M1 inside 600 s", 346_410, se.largest_n_within_window(m1_cost))


def main():
    for group in (m1_tests, m2_tests, m3_tests, m4_m5_tests, f_tests, g_tests):
        group()
    passed = sum(RESULTS)
    print(f"RESULT: {passed}/{len(RESULTS)} tests passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
