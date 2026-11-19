"""Q4 tests - correctness and operation-count checks for conventional and Strassen matrix multiplication.

References: the conventional triple loop and numpy's matrix product (numpy is used only for verification).
Prints one PASS/FAIL line per test and a final "RESULT: k/k tests passed".   Run:  py -3 q4_tests.py
"""
import random

import numpy as np

from q4_strassen import (OpCounter, closed_form_strassen, conventional_multiply, predicted_strassen_counts,
                         random_matrix, strassen_multiply, strassen_static_padding)

RESULTS = []


def check(name, condition):
    """Record and print one test result."""
    RESULTS.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


def numpy_product(A, B):
    """Reference product computed by numpy (int64)."""
    return (np.array(A, dtype=np.int64) @ np.array(B, dtype=np.int64)).tolist()


def main():
    rng = random.Random(42)
    print("Q4 TESTS - conventional and Strassen matrix multiplication")
    print("=" * 90)

    A, B = [[1, 3], [7, 5]], [[6, 8], [4, 2]]
    check("2 x 2 worked example: Strassen = conventional = [[18, 14], [62, 66]]",
          strassen_multiply(A, B, OpCounter()) == conventional_multiply(A, B, OpCounter()) == [[18, 14], [62, 66]])
    check("conventional equals numpy for n = 1..12 (random integer matrices)",
          all(conventional_multiply(X, Y, OpCounter()) == numpy_product(X, Y)
              for X, Y in ((random_matrix(n, rng), random_matrix(n, rng)) for n in range(1, 13))))
    check("Strassen (cutoff 1, dynamic padding) equals numpy for EVERY n = 1..40",
          all(strassen_multiply(X, Y, OpCounter()) == numpy_product(X, Y)
              for X, Y in ((random_matrix(n, rng), random_matrix(n, rng)) for n in range(1, 41))))
    check("Strassen with cutoffs 2, 4, 8, 16, 32 equals numpy at n = 64 and n = 100",
          all(strassen_multiply(X, Y, OpCounter(), c) == numpy_product(X, Y)
              for X, Y in ((random_matrix(n, rng), random_matrix(n, rng)) for n in (64, 100))
              for c in (2, 4, 8, 16, 32)))
    check("static padding (to the next power of 2) equals numpy for n = 5, 33, 100",
          all(strassen_static_padding(X, Y, OpCounter(), 4) == numpy_product(X, Y)
              for X, Y in ((random_matrix(n, rng), random_matrix(n, rng)) for n in (5, 33, 100))))
    check("negative entries: Strassen equals numpy for 16 x 16 matrices with entries in [-9, 9]",
          all(strassen_multiply(X, Y, OpCounter()) == numpy_product(X, Y)
              for X, Y in [(random_matrix(16, rng, -9, 9), random_matrix(16, rng, -9, 9))]))
    identity = [[int(i == j) for j in range(12)] for i in range(12)]
    M = random_matrix(12, rng)
    check("identity: I x M = M x I = M (n = 12, not a power of 2)",
          strassen_multiply(identity, M, OpCounter()) == M == strassen_multiply(M, identity, OpCounter()))
    zero = [[0] * 9 for _ in range(9)]
    check("zero matrix: 0 x M = 0 (n = 9)", strassen_multiply(zero, random_matrix(9, rng), OpCounter()) == zero)

    counts_ok = True
    for k in range(0, 7):
        n = 2 ** k
        ops = OpCounter()
        strassen_multiply(random_matrix(n, rng), random_matrix(n, rng), ops)
        counts_ok &= (ops.mults, ops.adds) == closed_form_strassen(n) and ops.max_depth == k
    check("pure Strassen counts: mults = 7^k, adds = 6(7^k - 4^k), depth = k for n = 2^k, k = 0..6", counts_ok)
    conv_ok = True
    for n in (1, 7, 16, 30):
        ops = OpCounter()
        conventional_multiply(random_matrix(n, rng), random_matrix(n, rng), ops)
        conv_ok &= ops.mults == n ** 3 and ops.adds == n * n * (n - 1)
    check("conventional counts: n^3 mults and n^2 (n - 1) adds (n = 1, 7, 16, 30)", conv_ok)
    pred_ok = True
    for n, c in ((100, 8), (129, 32), (200, 16), (37, 1), (64, 8)):
        ops = OpCounter()
        strassen_multiply(random_matrix(n, rng), random_matrix(n, rng), ops, c)
        pred_ok &= (ops.mults, ops.adds) == predicted_strassen_counts(n, c)
    check("hybrid/dynamic-padding counts match the recurrences M(n) = 7M(ceil(n/2)), "
          "A(n) = 7A(h) + 18h^2 (5 cases)", pred_ok)
    ops = OpCounter()
    strassen_multiply(random_matrix(100, rng), random_matrix(100, rng), ops, 1)
    check("dynamic padding of n = 100 pads exactly the odd sizes 25, 13, 7 at every node (3 levels padded)",
          ops.pads == 7 ** 2 + 7 ** 3 + 7 ** 4)
    ops = OpCounter()
    strassen_multiply(random_matrix(50, rng), random_matrix(50, rng), ops, 64)
    check("cutoff >= n gives exactly the conventional counts (n = 50, cutoff 64)",
          ops.mults == 50 ** 3 and ops.adds == 50 * 50 * 49)

    # Student B: the algebraic identities must hold for NON-commuting blocks (blocks are matrices, not numbers)
    identities_ok = True
    for _ in range(50):
        blocks = [random_matrix(3, rng, -9, 9) for _ in range(8)]
        a11, a12, a21, a22, b11, b12, b21, b22 = blocks
        mul = lambda X, Y: conventional_multiply(X, Y, OpCounter())          # noqa: E731
        add = lambda X, Y: [[x + y for x, y in zip(r, s)] for r, s in zip(X, Y)]    # noqa: E731
        sub = lambda X, Y: [[x - y for x, y in zip(r, s)] for r, s in zip(X, Y)]    # noqa: E731
        m1 = mul(add(a11, a22), add(b11, b22))
        m2, m3 = mul(add(a21, a22), b11), mul(a11, sub(b12, b22))
        m4, m5 = mul(a22, sub(b21, b11)), mul(add(a11, a12), b22)
        m6, m7 = mul(sub(a21, a11), add(b11, b12)), mul(sub(a12, a22), add(b21, b22))
        identities_ok &= add(sub(add(m1, m4), m5), m7) == add(mul(a11, b11), mul(a12, b21))
        identities_ok &= add(m3, m5) == add(mul(a11, b12), mul(a12, b22))
        identities_ok &= add(m2, m4) == add(mul(a21, b11), mul(a22, b21))
        identities_ok &= add(add(sub(m1, m2), m3), m6) == add(mul(a21, b12), mul(a22, b22))
    check("Strassen identities C11..C22 equal the 8 block products for non-commuting 3 x 3 blocks (50 trials)",
          identities_ok)

    # Student A: the overhead profiler (q4_overhead.py) must not change results and must restore the module
    import q4_overhead
    import q4_strassen
    original_add = q4_strassen.mat_add
    X, Y = random_matrix(64, rng), random_matrix(64, rng)
    ops = OpCounter()
    with q4_overhead.Profiler() as prof:
        C = q4_strassen.strassen_multiply(X, Y, ops, 8)
    check("profiler: wrapped Strassen (n = 64, c = 8) equals numpy and the module functions are restored",
          C == numpy_product(X, Y) and q4_strassen.mat_add is original_add)
    check("profiler counts: 18 block additions per splitting call (18 x 57 = 1,026) and 7^3 = 343 base-case calls",
          prof.calls["mat_add"] + prof.calls["mat_sub"] == 18 * 57 and prof.calls["conventional_multiply"] == 343
          and ops.calls == 400)
    check("temporary-matrix count formula: n = 64, c = 8 -> 27 x 57 + 343 = 1,882",
          q4_overhead.temporaries(64, 8) == 27 * 57 + 343)

    passed = sum(RESULTS)
    print("-" * 90)
    print(f"RESULT: {passed}/{len(RESULTS)} tests passed")


if __name__ == "__main__":
    main()
