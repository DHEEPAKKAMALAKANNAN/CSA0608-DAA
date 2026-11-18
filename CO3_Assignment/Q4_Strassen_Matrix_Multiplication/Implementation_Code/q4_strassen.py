"""Q4 - Strassen versus conventional matrix multiplication (CSA06 DAA, Assignment 3 - CO3: Divide-and-Conquer).

Scenario (drone-delivery operations centre): the city is divided into n delivery zones; a zone-to-zone
transition matrix P (n x n) gives how deliveries move between zones, and multi-step demand forecasts need
matrix products such as P^2 and P^4. n grows from 16 to several hundred zones and is not always a power of 2.

This module implements, on square matrices stored as lists of lists (pure Python, exact integers):
  * conventional_multiply  - triple loop: n^3 scalar multiplications and n^2 (n - 1) scalar additions;
  * strassen_multiply      - Divide-and-Conquer with 7 half-size products and 18 block additions/subtractions,
                             a cutoff (conventional for n <= cutoff) and DYNAMIC padding (one zero row/column
                             is added when the current size is odd);
  * strassen_static_padding- pads the whole matrix once to the next power of 2 and then runs Strassen.
Counted basic operations (OpCounter): scalar multiplications and scalar additions/subtractions.
Copying, splitting and padding move data but do no arithmetic and are not counted.

Run:  py -3 q4_strassen.py      (demo)   - experiments: q4_experiments.py, tests: q4_tests.py
"""
import random


class OpCounter:
    """Counts the scalar arithmetic of one matrix multiplication."""

    def __init__(self):
        self.mults = 0        # scalar multiplications
        self.adds = 0         # scalar additions and subtractions
        self.calls = 0        # Strassen calls = nodes of the recursion tree
        self.max_depth = 0    # deepest recursion level reached
        self.pads = 0         # number of times an odd size was padded by one (dynamic padding)

    @property
    def total(self):
        """All counted scalar operations."""
        return self.mults + self.adds


# ----------------------------------------------------------------------------- matrix helpers
def random_matrix(n, rng, low=0, high=9):
    """An n x n matrix of random integers in [low, high]."""
    return [[rng.randint(low, high) for _ in range(n)] for _ in range(n)]


def mat_add(X, Y, ops):
    """X + Y for h x h matrices: exactly h^2 scalar additions."""
    ops.adds += len(X) * len(X)
    return [[x + y for x, y in zip(rx, ry)] for rx, ry in zip(X, Y)]


def mat_sub(X, Y, ops):
    """X - Y for h x h matrices: exactly h^2 scalar subtractions."""
    ops.adds += len(X) * len(X)
    return [[x - y for x, y in zip(rx, ry)] for rx, ry in zip(X, Y)]


def split(M, h):
    """The four h x h blocks M11, M12, M21, M22 of a 2h x 2h matrix (data movement only)."""
    top, bottom = M[:h], M[h:]
    return ([r[:h] for r in top], [r[h:] for r in top], [r[:h] for r in bottom], [r[h:] for r in bottom])


def join(C11, C12, C21, C22):
    """Assemble a 2h x 2h matrix from its four blocks."""
    return [r1 + r2 for r1, r2 in zip(C11, C12)] + [r1 + r2 for r1, r2 in zip(C21, C22)]


def pad(M, size):
    """M (n x n) extended with zero rows/columns to size x size."""
    n = len(M)
    return [row + [0] * (size - n) for row in M] + [[0] * size for _ in range(size - n)]


def unpad(M, n):
    """Top-left n x n part of M."""
    return [row[:n] for row in M[:n]]


def next_power_of_two(n):
    """Smallest power of 2 that is >= n."""
    p = 1
    while p < n:
        p *= 2
    return p


# ----------------------------------------------------------------------------- the two methods
def conventional_multiply(A, B, ops):
    """Triple-loop product C = A B of n x n matrices: C[i][j] = sum_k A[i][k] B[k][j].

    Each of the n^2 entries needs n multiplications and n - 1 additions: n^3 and n^2 (n - 1) in total."""
    n = len(A)
    Bt = [list(col) for col in zip(*B)]          # columns of B as rows (data movement only)
    C = [[0] * n for _ in range(n)]
    mults = adds = 0
    for i in range(n):
        Ai, Ci = A[i], C[i]
        for j in range(n):
            Bj = Bt[j]
            s = Ai[0] * Bj[0]
            mults += 1
            for k in range(1, n):
                s += Ai[k] * Bj[k]                 # 1 multiplication + 1 addition
                mults += 1
                adds += 1
            Ci[j] = s
    ops.mults += mults
    ops.adds += adds
    return C


def strassen_multiply(A, B, ops, cutoff=1, depth=0):
    """Strassen's product of n x n matrices A, B (any n >= 1).

    BASE   : n <= cutoff -> conventional multiplication.
    DIVIDE : h = ceil(n/2); if n is odd, pad A and B with one zero row and column (dynamic padding); split
             both into four h x h blocks.
    CONQUER: 7 recursive products (instead of 8)
             M1 = (A11 + A22)(B11 + B22)   M2 = (A21 + A22) B11   M3 = A11 (B12 - B22)   M4 = A22 (B21 - B11)
             M5 = (A11 + A12) B22          M6 = (A21 - A11)(B11 + B12)               M7 = (A12 - A22)(B21 + B22)
             (10 block additions/subtractions prepare the operands).
    COMBINE: C11 = M1 + M4 - M5 + M7, C12 = M3 + M5, C21 = M2 + M4, C22 = M1 - M2 + M3 + M6 (8 more),
             then remove the padding.  In total 18 additions/subtractions of h x h blocks per call.
    """
    n = len(A)
    ops.calls += 1
    if depth > ops.max_depth:
        ops.max_depth = depth
    if n <= cutoff:
        return conventional_multiply(A, B, ops)
    h = (n + 1) // 2
    if 2 * h != n:                                   # odd size: dynamic padding by one row/column
        ops.pads += 1
        A, B = pad(A, 2 * h), pad(B, 2 * h)
    A11, A12, A21, A22 = split(A, h)
    B11, B12, B21, B22 = split(B, h)
    d = depth + 1
    M1 = strassen_multiply(mat_add(A11, A22, ops), mat_add(B11, B22, ops), ops, cutoff, d)
    M2 = strassen_multiply(mat_add(A21, A22, ops), B11, ops, cutoff, d)
    M3 = strassen_multiply(A11, mat_sub(B12, B22, ops), ops, cutoff, d)
    M4 = strassen_multiply(A22, mat_sub(B21, B11, ops), ops, cutoff, d)
    M5 = strassen_multiply(mat_add(A11, A12, ops), B22, ops, cutoff, d)
    M6 = strassen_multiply(mat_sub(A21, A11, ops), mat_add(B11, B12, ops), ops, cutoff, d)
    M7 = strassen_multiply(mat_sub(A12, A22, ops), mat_add(B21, B22, ops), ops, cutoff, d)
    C11 = mat_add(mat_sub(mat_add(M1, M4, ops), M5, ops), M7, ops)
    C12 = mat_add(M3, M5, ops)
    C21 = mat_add(M2, M4, ops)
    C22 = mat_add(mat_add(mat_sub(M1, M2, ops), M3, ops), M6, ops)
    C = join(C11, C12, C21, C22)
    return C if 2 * h == n else unpad(C, n)


def strassen_static_padding(A, B, ops, cutoff=1):
    """STATIC padding: pad once to the next power of 2, run Strassen, cut the result back to n x n."""
    n = len(A)
    size = next_power_of_two(n)
    if size == n:
        return strassen_multiply(A, B, ops, cutoff)
    return unpad(strassen_multiply(pad(A, size), pad(B, size), ops, cutoff), n)


# ----------------------------------------------------------------------------- predicted counts
def predicted_strassen_counts(n, cutoff=1):
    """(multiplications, additions) predicted by the recurrences
         M(n) = 7 M(h),            A(n) = 7 A(h) + 18 h^2,      h = ceil(n/2)   for n > cutoff
         M(n) = n^3,               A(n) = n^2 (n - 1)                           for n <= cutoff."""
    if n <= cutoff:
        return n ** 3, n * n * (n - 1)
    h = (n + 1) // 2
    m, a = predicted_strassen_counts(h, cutoff)
    return 7 * m, 7 * a + 18 * h * h


def closed_form_strassen(n):
    """Closed forms for n = 2^k down to 1 x 1 blocks: M = 7^k = n^log2(7), A = 6 (7^k - 4^k)."""
    k = n.bit_length() - 1
    return 7 ** k, 6 * (7 ** k - 4 ** k)


# ----------------------------------------------------------------------------- demo
def print_matrix(name, M, width=5):
    """Print a small matrix with a name."""
    for i, row in enumerate(M):
        label = f"{name} =" if i == 0 else " " * (len(name) + 2)
        print(f"   {label} [" + " ".join(f"{v:>{width}}" for v in row) + " ]")


def main():
    print("Q4 - STRASSEN vs CONVENTIONAL MATRIX MULTIPLICATION (demo)")
    print("=" * 100)

    print("\n1) One level of Strassen on 2 x 2 matrices: 7 multiplications instead of 8")
    A, B = [[1, 3], [7, 5]], [[6, 8], [4, 2]]
    (a, b), (c, d) = A
    (e, f), (g, h) = B
    m = [(a + d) * (e + h), (c + d) * e, a * (f - h), d * (g - e), (a + b) * h, (c - a) * (e + f), (b - d) * (g + h)]
    print("   " + "  ".join(f"M{i + 1} = {v}" for i, v in enumerate(m)))
    ops = OpCounter()
    C = strassen_multiply(A, B, ops)
    print(f"   C11 = M1 + M4 - M5 + M7 = {m[0] + m[3] - m[4] + m[6]}   C12 = M3 + M5 = {m[2] + m[4]}   "
          f"C21 = M2 + M4 = {m[1] + m[3]}   C22 = M1 - M2 + M3 + M6 = {m[0] - m[1] + m[2] + m[5]}")
    print(f"   strassen_multiply -> {C}   conventional -> {conventional_multiply(A, B, OpCounter())}   "
          f"mults = {ops.mults}, adds = {ops.adds}")

    print("\n2) Counted operations against the closed forms (random integer matrices, seed 42, cutoff 1)")
    print(f"   {'n':>4} | {'conv mults':>10} {'n^3':>10} {'conv adds':>10} | {'Str mults':>10} {'7^k':>10} | "
          f"{'Str adds':>10} {'6(7^k-4^k)':>10} | equal")
    print("   " + "-" * 96)
    rng = random.Random(42)
    for n in (2, 4, 8, 16, 32):
        A, B = random_matrix(n, rng), random_matrix(n, rng)
        oc, os_ = OpCounter(), OpCounter()
        Cc, Cs = conventional_multiply(A, B, oc), strassen_multiply(A, B, os_)
        m7, a7 = closed_form_strassen(n)
        print(f"   {n:>4} | {oc.mults:>10,} {n ** 3:>10,} {oc.adds:>10,} | {os_.mults:>10,} {m7:>10,} | "
              f"{os_.adds:>10,} {a7:>10,} | {'yes' if Cc == Cs else 'NO'}")

    print("\n3) Zone-demand example: 6 zones (not a power of 2), T = trips between zones, T^2 = two-step trips")
    T = random_matrix(6, rng, 0, 5)
    ops, conv_ops = OpCounter(), OpCounter()
    T2 = strassen_multiply(T, T, ops)
    T2_conv = conventional_multiply(T, T, conv_ops)
    print_matrix("T  ", T, 3)
    print_matrix("T^2", T2, 3)
    print(f"   Strassen (dynamic padding 6 -> 3 -> 4 -> 2 -> 1, cutoff 1): {ops.mults} mults, {ops.adds} adds, "
          f"odd size padded {ops.pads} times")
    print(f"   conventional: {conv_ops.mults} mults, {conv_ops.adds} adds;  results equal: {T2 == T2_conv}"
          f"  -> for tiny matrices Strassen's overhead dominates")


if __name__ == "__main__":
    main()
