"""
Task 1 - test suite for binomial_dp.py.

* Table-driven cases from test_data/binomial_test_cases.csv (given + own + boundary cases): every algorithm must
  return the expected value, which is also cross-checked against the reference math.comb.
* Property tests: symmetry, Pascal's rule, 300 random (n, k) pairs vs math.comb, counted operations equal the
  closed forms, error handling, Fibonacci warm-up.
Prints PASS/FAIL lines and a final "RESULT: k/k tests passed".   Run:  py -3 test_binomial.py
"""
import csv
import math
import os
import random

from binomial_dp import (binom_bottom_up, binom_memo, binom_naive, binom_one_row, fib_bottom_up,
                         fib_memo, fib_naive, formula_bottom_up_additions)

HERE = os.path.dirname(os.path.abspath(__file__))
results = []


def check(name, condition, detail=""):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


def table_cases():
    with open(os.path.join(HERE, "test_data", "binomial_test_cases.csv"), encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            n, k, exp = int(row["n"]), int(row["k"]), int(row["expected"])
            got = [binom_memo(n, k)[0], binom_bottom_up(n, k)[0], binom_one_row(n, k)[0]]
            if row["run_naive"] == "yes":
                got.append(binom_naive(n, k)[0])
            ok = all(g == exp for g in got) and exp == math.comb(n, max(k, 0)) * (k >= 0)
            shown = str(exp) if len(str(exp)) <= 15 else str(exp)[:12] + "..."
            label = f"C({n},{k}) = {shown}"
            check(f"{row['case_id']:<4}({row['category']:<8}) {label:<30} {row['description']}", ok,
                  f"{len(got)} algorithms agree")


def property_tests():
    random.seed(42)
    pairs = [(n, random.randint(0, n)) for n in (random.randint(0, 60) for _ in range(300))]
    ok = all(binom_bottom_up(n, k)[0] == binom_one_row(n, k)[0] == binom_memo(n, k)[0] == math.comb(n, k)
             for n, k in pairs)
    check("300 random (n, k), n <= 60: table = single row = memo = math.comb", ok)
    ok = all(binom_bottom_up(n, k)[0] == binom_bottom_up(n, n - k)[0] for n, k in pairs)
    check("symmetry C(n, k) = C(n, n-k) on the 300 random pairs", ok)
    ok = all(binom_one_row(n, k)[0] == binom_one_row(n - 1, k - 1)[0] + binom_one_row(n - 1, k)[0]
             for n, k in pairs if 0 < k < n)
    check("Pascal's rule C(n,k) = C(n-1,k-1) + C(n-1,k) holds for the computed values", ok)
    ok = all(binom_naive(n, k)[1]["calls"] == 2 * math.comb(n, k) - 1 for n in range(0, 19) for k in range(n + 1))
    check("naive recursion makes exactly 2C(n,k) - 1 calls for all 0 <= k <= n <= 18", ok)
    ok = all(binom_memo(n, k)[1]["additions"] == k * (n - k) for n in range(0, 40) for k in range(n + 1))
    check("memoised version performs exactly k(n-k) additions for all 0 <= k <= n < 40", ok)
    ok = all(binom_bottom_up(n, k)[1]["additions"] == binom_one_row(n, k)[1]["additions"]
             == formula_bottom_up_additions(n, k) for n in range(0, 40) for k in range(n + 1))
    check("table and single row both perform (k-1)k/2 + k(n-k) additions (0 <= k <= n < 40)", ok)
    ok = binom_one_row(1000, 500, modulus=1_000_000_007)[0] == math.comb(1000, 500) % 1_000_000_007
    check("single row mod p: C(1000, 500) mod 1e9+7 matches math.comb", ok)
    ok = binom_one_row(500, 250)[1]["cells_stored"] == 251
    check("single row stores only k + 1 = 251 cells for C(500, 250)", ok)
    try:
        binom_bottom_up(-1, 0)
        ok = False
    except ValueError:
        ok = True
    check("negative n raises ValueError (invalid input rejected)", ok)
    try:
        binom_one_row(5.0, 2)
        ok = False
    except TypeError:
        ok = True
    check("non-integer n raises TypeError", ok)
    ok = all(fib_naive(m)[0] == fib_memo(m)[0] == fib_bottom_up(m)[0] for m in range(0, 22))
    check("Fibonacci: naive = memo = bottom-up for n = 0..21", ok)
    ok = all(fib_naive(m)[1]["calls"] == 2 * fib_bottom_up(m + 1)[0] - 1 for m in range(0, 22))
    check("Fibonacci naive calls = 2F(n+1) - 1 for n = 0..21", ok)


def main():
    print("Task 1 - binomial coefficient: test run")
    table_cases()
    property_tests()
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
