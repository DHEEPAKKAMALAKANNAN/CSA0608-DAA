"""Q3 tests - correctness and operation-count checks for schoolbook and Karatsuba multiplication.

Reference: Python's built-in arbitrary-precision int multiplication (x * y).
Prints one PASS/FAIL line per test and a final "RESULT: k/k tests passed".   Run:  py -3 q3_tests.py
"""
import math
import random

from q3_karatsuba import (OpCounter, from_digits, karatsuba_additive, karatsuba_multiply, multiply_ints,
                          predicted_karatsuba_mults, random_digits, schoolbook_multiply, to_digits)

RESULTS = []


def check(name, condition):
    """Record and print one test result."""
    RESULTS.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


def all_n_correct(method, threshold, sizes, pairs, rng):
    """True if method gives the int product for `pairs` random operand pairs of every size in `sizes`."""
    for n in sizes:
        for _ in range(pairs):
            a, b = random_digits(n, rng), random_digits(n, rng)
            ops = OpCounter()
            if method == "schoolbook":
                digits = schoolbook_multiply(a, b, ops)
            else:
                digits = karatsuba_multiply(a, b, ops, threshold)
            if from_digits(digits) != from_digits(a) * from_digits(b):
                return False
    return True


def main():
    rng = random.Random(42)
    print("Q3 TESTS - schoolbook and Karatsuba multiplication on digit arrays")
    print("=" * 90)

    check("digit conversion round trip: 0, 7, 1234, 10^50 + 3 and zero padding",
          all(from_digits(to_digits(x)) == x for x in (0, 7, 1234, 10 ** 50 + 3))
          and to_digits(42, 5) == [2, 4, 0, 0, 0])
    check("schoolbook 1234 x 5678 = 7006652", multiply_ints(1234, 5678, "schoolbook")[0] == 7006652)
    check("Karatsuba 1234 x 5678 = 7006652 (worked example of the report)",
          multiply_ints(1234, 5678)[0] == 7006652)
    check("schoolbook equals int * for every n = 1..40 (3 random pairs each)",
          all_n_correct("schoolbook", 1, range(1, 41), 3, rng))
    check("Karatsuba (threshold 1) equals int * for every n = 1..70 (3 random pairs each)",
          all_n_correct("karatsuba", 1, range(1, 71), 3, rng))
    check("hybrid Karatsuba equals int * for thresholds 2, 4, 8, 16, 32, 64 at n = 617",
          all(all_n_correct("karatsuba", t, [617], 1, rng) for t in (2, 4, 8, 16, 32, 64)))

    counts_ok = True
    for n in range(1, 130):
        a, b = random_digits(n, rng), random_digits(n, rng)
        ops = OpCounter()
        karatsuba_multiply(a, b, ops, 1)
        if ops.mults != 3 ** math.ceil(math.log2(n)) or ops.max_depth != math.ceil(math.log2(n)):
            counts_ok = False
    check("Karatsuba single-digit mults = 3^ceil(log2 n) and depth = ceil(log2 n) for every n = 1..129", counts_ok)

    sb_ok = True
    for n in (1, 5, 64, 100):
        ops = OpCounter()
        schoolbook_multiply(random_digits(n, rng), random_digits(n, rng), ops)
        sb_ok &= ops.mults == n * n and ops.adds == 2 * n * n
    check("schoolbook counts: exactly n^2 mults and 2n^2 additions (n = 1, 5, 64, 100)", sb_ok)

    hyb_ok = True
    for n, t in ((617, 16), (1234, 32), (1000, 8), (100, 4)):
        ops = OpCounter()
        karatsuba_multiply(random_digits(n, rng), random_digits(n, rng), ops, t)
        hyb_ok &= ops.mults == predicted_karatsuba_mults(n, t)
    check("hybrid counts match M(n) = 3M(ceil(n/2)), M(n <= t) = n^2 (4 size/threshold pairs)", hyb_ok)

    nines = 10 ** 64 - 1
    check("all-nines operands (maximum carries): (10^64 - 1)^2 correct",
          multiply_ints(nines, nines)[0] == nines * nines)
    check("zero operand: 0 x (10^30 + 7) = 0 and 1-digit 9 x 9 = 81",
          multiply_ints(0, 10 ** 30 + 7)[0] == 0 and multiply_ints(9, 9)[0] == 81)
    check("operands of different lengths (zero-padded): 123456789 x 987 correct",
          multiply_ints(123456789, 987)[0] == 123456789 * 987)
    check("equal halves (a0 = a1, middle product 0): 4545 x 1212 correct",
          multiply_ints(4545, 1212)[0] == 4545 * 1212)
    rsa = [random_digits(617, rng), random_digits(617, rng), random_digits(1234, rng), random_digits(1234, rng)]
    check("RSA-size operands: 617-digit and 1,234-digit products correct (threshold 1 and 16)",
          all(from_digits(karatsuba_multiply(rsa[i], rsa[i + 1], OpCounter(), t))
              == from_digits(rsa[i]) * from_digits(rsa[i + 1]) for i in (0, 2) for t in (1, 16)))
    add_ok = True
    for n in (4, 17, 64, 100):
        a, b = random_digits(n, rng), random_digits(n, rng)
        add_ok &= from_digits(karatsuba_additive(a, b, OpCounter(), 3)) == from_digits(a) * from_digits(b)
    check("additive Karatsuba variant (comparison only) correct for n = 4, 17, 64, 100", add_ok)

    # per-level overhead breakdown used by q3_crossover.py (C3)
    a, b = random_digits(64, rng), random_digits(64, rng)
    lv = OpCounter(per_level=True)
    plain = OpCounter()
    same = karatsuba_multiply(a, b, lv, 1) == karatsuba_multiply(a, b, plain, 1)
    rows = lv.levels
    check("per-level breakdown (n = 64, t = 1): 3^d nodes at depth d, level sums = totals, same product/counts",
          same and all(rows[d][0] == 3 ** d for d in rows)
          and sum(r[0] for r in rows.values()) == lv.calls == plain.calls
          and sum(r[1] for r in rows.values()) == lv.mults == plain.mults == 729
          and sum(r[2] for r in rows.values()) == lv.adds == plain.adds)
    ops16 = OpCounter()
    karatsuba_multiply(random_digits(1024, rng), random_digits(1024, rng), ops16, 16)
    check("hybrid t = 16 at n = 1,024: 3^6 = 729 leaves of 16 digits -> 729 x 256 = 186,624 mults, 1,093 calls",
          ops16.mults == 186_624 and ops16.calls == 1_093)

    passed = sum(RESULTS)
    print("-" * 90)
    print(f"RESULT: {passed}/{len(RESULTS)} tests passed")


if __name__ == "__main__":
    main()
