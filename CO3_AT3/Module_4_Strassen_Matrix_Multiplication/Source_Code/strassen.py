"""SwiftLogix - Module 4: Strassen's matrix multiplication for the network-forecasting job.

Problem
    The forecasting engine multiplies the route-demand matrix D (origin zone x hub corridor) by the
    cost matrix C (hub corridor x destination zone) to obtain the network cost forecast F = D x C
    (production workload: 1,024 x 1,024 matrices, one product every 15 minutes).

Divide-and-conquer design (Strassen, 1969)
    DIVIDE : split A and B into four (n/2) x (n/2) blocks each
    CONQUER: 7 recursive block products M1..M7 (instead of the 8 of the block-definition method)
             M1 = (A11 + A22)(B11 + B22)   M2 = (A21 + A22) B11   M3 = A11 (B12 - B22)
             M4 = A22 (B21 - B11)          M5 = (A11 + A12) B22   M6 = (A21 - A11)(B11 + B12)
             M7 = (A12 - A22)(B21 + B22)
    COMBINE: C11 = M1 + M4 - M5 + M7   C12 = M3 + M5   C21 = M2 + M4   C22 = M1 - M2 + M3 + M6
    Basic operations: scalar multiplications (M(n) = 7M(n/2) -> n^lg7 = n^2.807) and scalar additions
    (A(n) = 7A(n/2) + 18(n/2)^2).  Sizes that are not powers of two are zero-padded.

The hybrid (Part 5) switches to the naive method for blocks of size <= cutoff and pads only to s * 2^d.

Run:  py -3 strassen.py        trace on the given 4 x 4 sample + padding demo + verification
"""
import json
import sys
from pathlib import Path

import numpy as np                                       # used ONLY to verify results

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "Supporting_Files" / "datasets" / "m4_route_matrices_sample.json"


class OpCounter:
    """Counts scalar multiplications, scalar additions/subtractions, recursive calls and depth."""

    def __init__(self):
        self.mults = self.adds = self.calls = self.max_depth = 0

    @property
    def total(self):
        return self.mults + self.adds


# ----------------------------------------------------------------------------- matrix helpers
def naive_multiply(A, B, c=None):
    """Definition-based product (baseline): n^3 multiplications and n^2 (n - 1) additions for n x n."""
    c = c if c is not None else OpCounter()
    n, m, p = len(A), len(B), len(B[0])
    cols = list(zip(*B))
    C = [[sum(a * b for a, b in zip(row, col)) for col in cols] for row in A]
    c.mults += n * m * p
    c.adds += n * p * (m - 1)
    return C


def mat_add(X, Y, c):
    c.adds += len(X) * len(X[0])
    return [[x + y for x, y in zip(rx, ry)] for rx, ry in zip(X, Y)]


def mat_sub(X, Y, c):
    c.adds += len(X) * len(X[0])
    return [[x - y for x, y in zip(rx, ry)] for rx, ry in zip(X, Y)]


def split(M):
    h = len(M) // 2
    return ([r[:h] for r in M[:h]], [r[h:] for r in M[:h]], [r[:h] for r in M[h:]], [r[h:] for r in M[h:]])


def join(C11, C12, C21, C22):
    return [a + b for a, b in zip(C11, C12)] + [a + b for a, b in zip(C21, C22)]


# ----------------------------------------------------------------------------- Strassen
def strassen(A, B, cutoff=1, c=None, trace=None, depth=0):
    """Strassen product of two n x n matrices; n must be even whenever n > cutoff (pad first)."""
    c = c if c is not None else OpCounter()
    n = len(A)
    c.calls += 1
    c.max_depth = max(c.max_depth, depth)
    if n <= cutoff:                                          # base case (cutoff 1 = scalar product)
        return naive_multiply(A, B, c)
    if n % 2:
        raise ValueError("odd size above the cutoff - pad the matrices first")
    A11, A12, A21, A22 = split(A)                            # DIVIDE
    B11, B12, B21, B22 = split(B)
    if trace:
        trace("divide", depth, {"A11": A11, "A12": A12, "A21": A21, "A22": A22,
                                "B11": B11, "B12": B12, "B21": B21, "B22": B22})
    plan = (("M1", "(A11 + A22)(B11 + B22)", lambda: mat_add(A11, A22, c), lambda: mat_add(B11, B22, c)),
            ("M2", "(A21 + A22) B11", lambda: mat_add(A21, A22, c), lambda: B11),
            ("M3", "A11 (B12 - B22)", lambda: A11, lambda: mat_sub(B12, B22, c)),
            ("M4", "A22 (B21 - B11)", lambda: A22, lambda: mat_sub(B21, B11, c)),
            ("M5", "(A11 + A12) B22", lambda: mat_add(A11, A12, c), lambda: B22),
            ("M6", "(A21 - A11)(B11 + B12)", lambda: mat_sub(A21, A11, c), lambda: mat_add(B11, B12, c)),
            ("M7", "(A12 - A22)(B21 + B22)", lambda: mat_sub(A12, A22, c), lambda: mat_add(B21, B22, c)))
    M = {}
    for name, formula, left, right in plan:                 # CONQUER: 7 recursive products
        X, Y = left(), right()
        M[name] = strassen(X, Y, cutoff, c, trace, depth + 1)
        if trace:
            trace("product", depth, (name, formula, X, Y, M[name]))
    C11 = mat_add(mat_sub(mat_add(M["M1"], M["M4"], c), M["M5"], c), M["M7"], c)      # COMBINE
    C12 = mat_add(M["M3"], M["M5"], c)
    C21 = mat_add(M["M2"], M["M4"], c)
    C22 = mat_add(mat_add(mat_sub(M["M1"], M["M2"], c), M["M3"], c), M["M6"], c)
    if trace:
        trace("combine", depth, {"C11": C11, "C12": C12, "C21": C21, "C22": C22})
    return join(C11, C12, C21, C22)


def padded_size(n, cutoff=1, mode="pow2"):
    """pow2: next power of two >= n.  minimal: smallest s * 2^d >= n with s <= cutoff (PadSize pseudocode)."""
    if mode == "pow2":
        m = 1
        while m < n:
            m *= 2
        return m
    d = 0
    while -(-n // 2 ** d) > cutoff:
        d += 1
    return -(-n // 2 ** d) * 2 ** d


def pad(M, m):
    return [list(row) + [0] * (m - len(row)) for row in M] + [[0] * m for _ in range(m - len(M))]


def strassen_multiply(A, B, cutoff=1, padding="pow2", counter=None, trace=None):
    """Multiply any two n x n matrices with Strassen: pad, multiply, strip the padding."""
    n = len(A)
    if n == 0:
        return []
    m = padded_size(n, cutoff, padding)
    C = strassen(pad(A, m), pad(B, m), cutoff, counter, trace)
    return [row[:n] for row in C[:n]]


def strassen_ops(n, cutoff=1):
    """Closed-form (multiplications, additions) of strassen() on an n x n input with the given cutoff."""
    if n <= cutoff:
        return n ** 3, n * n * (n - 1)
    h = n // 2
    m, a = strassen_ops(h, cutoff)
    return 7 * m, 7 * a + 18 * h * h


# ----------------------------------------------------------------------------- demo on the sample
def show(M):
    return "[" + ", ".join("[" + ", ".join(f"{x}" for x in row) + "]" for row in M) + "]"


def print_side_by_side(titles, mats):
    width = [max(len(t), 4 * len(m[0]) + 1) for t, m in zip(titles, mats)]
    print("  " + "   ".join(f"{t:<{w}}" for t, w in zip(titles, width)))
    for r in range(len(mats[0])):
        print("  " + "   ".join(f"{''.join(f'{x:>4}' for x in m[r]):<{w}}" for m, w in zip(mats, width)))


class TracePrinter:
    """Prints the depth-0 steps in full; the scalar products of each depth-1 call are shown compactly."""

    def __init__(self):
        self.scalars = []

    def __call__(self, event, depth, payload):
        if depth == 1 and event == "product":
            self.scalars.append(payload[4][0][0])            # 1 x 1 result of a level-2 product
            return
        if depth != 0:
            return
        if event == "divide":
            print("DIVIDE - 2 x 2 blocks of A (demand) and B (cost):")
            p = payload
            print(f"  A11 = {show(p['A11']):<18} A12 = {show(p['A12']):<18} "
                  f"A21 = {show(p['A21']):<18} A22 = {show(p['A22'])}")
            print(f"  B11 = {show(p['B11']):<18} B12 = {show(p['B12']):<18} "
                  f"B21 = {show(p['B21']):<18} B22 = {show(p['B22'])}")
            print("CONQUER - 7 recursive 2 x 2 products (each one again uses 7 scalar products m1..m7):")
        elif event == "product":
            name, formula, X, Y, R = payload
            print(f"  {name} = {formula:<23} = {show(X)} x {show(Y)}")
            print(f"       = {show(R):<22}   level-2 scalar products m1..m7 = {self.scalars}")
            self.scalars = []
        elif event == "combine":
            p = payload
            print("COMBINE - 8 block additions/subtractions:")
            print(f"  C11 = M1 + M4 - M5 + M7 = {show(p['C11']):<20} C12 = M3 + M5 = {show(p['C12'])}")
            print(f"  C21 = M2 + M4           = {show(p['C21']):<20} C22 = M1 - M2 + M3 + M6 = {show(p['C22'])}")


def run_demo():
    with open(SAMPLE, encoding="utf-8") as fh:
        data = json.load(fh)
    D, C = data["demand_D"]["matrix"], data["cost_C"]["matrix"]
    n = len(D)
    print("=" * 104)
    print(f"SwiftLogix M4 - Strassen multiplication F = D x C (given sample: {n} x {n} route matrices)")
    print("=" * 104)
    print_side_by_side(["D (demand, 100 parcels)", "C (cost, Rs 1000 / 100 parcels)"], [D, C])
    print()
    c = OpCounter()
    F = strassen_multiply(D, C, cutoff=1, counter=c, trace=TracePrinter())
    cn = OpCounter()
    F_naive = naive_multiply(D, C, cn)
    print()
    print_side_by_side(["F = Strassen(D, C)", "naive D x C", "numpy D @ C"], [F, F_naive, np.array(D) @ np.array(C)])
    print()
    print("Verification and operation counts")
    print(f"  Strassen == naive == numpy : {F == F_naive == (np.array(D) @ np.array(C)).tolist()}")
    fm, fa = strassen_ops(4)
    print(f"  Strassen : {c.mults} multiplications + {c.adds} additions = {c.total}  "
          f"(formula 7^2 = {fm} mults, 6(7^2 - 4^2) = {fa} adds)")
    print(f"  naive    : {cn.mults} multiplications + {cn.adds} additions = {cn.total}  (n^3 = 64, n^2(n-1) = 48)")
    print(f"  recursive calls = {c.calls} (1 + 7 + 49), max depth = {c.max_depth} (= lg 4)")
    h = OpCounter()
    strassen_multiply(D, C, cutoff=2, counter=h)
    print(f"  hybrid, cutoff 2 (naive 2 x 2 blocks): {h.mults} mults + {h.adds} adds = {h.total}")

    print("\nNon-power-of-two sizes: zero padding to the next power of two (synthetic 3-zone and 5-zone matrices)")
    for size in (3, 5):
        A = [[(i * 7 + j * 3) % 10 for j in range(size)] for i in range(size)]
        B = [[(i * 5 + j * 2 + 1) % 9 for j in range(size)] for i in range(size)]
        cp = OpCounter()
        R = strassen_multiply(A, B, cutoff=1, counter=cp)
        ok = R == (np.array(A) @ np.array(B)).tolist()
        print(f"  {size} x {size} -> padded to {padded_size(size)} x {padded_size(size)}: result == numpy: {ok}; "
              f"{cp.mults} mults (naive {size ** 3}); first row {R[0]}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    run_demo()


if __name__ == "__main__":
    main()
