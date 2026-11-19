"""Q3 - Karatsuba multiplication of large integers (CSA06 DAA, Assignment 3 - CO3: Divide-and-Conquer).

Scenario (drone-delivery operations centre): every flight command is digitally signed, and signing multiplies
very large integers - 617 decimal digits for a 2,048-bit RSA modulus, 1,234 digits for a 4,096-bit modulus.
The firmware uses the schoolbook method. This module implements, on base-10 digit arrays:

  * schoolbook_multiply   - the grade-school method: exactly n*m single-digit multiplications;
  * karatsuba_multiply    - Divide-and-Conquer (subtractive variant): three half-size products per level,
                            with an optional threshold below which it falls back to the schoolbook method;
  * karatsuba_additive    - the textbook additive variant, kept only to show why its count is not exact.

Basic operations counted (OpCounter):
  * mults - single-digit multiplications (the operation Karatsuba saves);
  * adds  - digit additions/subtractions: every + or - applied to digits, carries and borrows included.
Carry normalisation (t % 10, t // 10) is identical in both methods and is not counted.
Numbers are little-endian digit lists: 1234 -> [4, 3, 2, 1].

Run:  py -3 q3_karatsuba.py      (demo)   - experiments: q3_experiments.py, tests: q3_tests.py
"""
import math
import random
import sys

if hasattr(sys, "set_int_max_str_digits"):        # products of 2,048-digit numbers have 4,096 digits
    sys.set_int_max_str_digits(100_000)


class OpCounter:
    """Counts the basic digit operations of one (recursive) multiplication."""

    def __init__(self, per_level=False):
        self.mults = 0        # single-digit multiplications
        self.adds = 0         # digit additions / subtractions (carries and borrows included)
        self.calls = 0        # multiplication calls = nodes of the recursion tree
        self.max_depth = 0    # deepest recursion level reached
        # optional overhead breakdown: depth -> [calls, own mults, own adds, digits in temporary lists]
        self.levels = {} if per_level else None

    @property
    def total(self):
        """All counted digit operations (multiplications + additions/subtractions)."""
        return self.mults + self.adds


# ----------------------------------------------------------------------------- digit-array helpers
def to_digits(x, n=None):
    """Little-endian base-10 digits of the integer x >= 0, zero-padded to length n."""
    digits = [int(c) for c in reversed(str(x))]
    if n is not None:
        digits += [0] * (n - len(digits))
    return digits


def from_digits(digits):
    """Integer value of a little-endian digit list (used only for checking and tracing)."""
    return int("".join(map(str, reversed(digits)))) if digits else 0


def random_digits(n, rng):
    """A random n-digit number (most significant digit non-zero) as a little-endian digit list."""
    return [rng.randint(0, 9) for _ in range(n - 1)] + [rng.randint(1, 9)]


def compare_magnitude(x, y):
    """Compare two equal-length digit lists from the most significant digit: -1, 0 or +1."""
    for i in range(len(x) - 1, -1, -1):
        if x[i] != y[i]:
            return 1 if x[i] > y[i] else -1
    return 0


def add_digits(x, y, ops):
    """x + y for digit lists; the result has max(len) + 1 digits. Counts 2 additions per digit."""
    if len(x) < len(y):
        x, y = y, x
    ly = len(y)
    result = [0] * (len(x) + 1)
    carry = 0
    adds = 0
    for i in range(len(x)):
        t = x[i] + (y[i] if i < ly else 0) + carry          # 2 additions (digit + digit + carry)
        adds += 2
        result[i] = t % 10
        carry = t // 10
    result[len(x)] = carry
    ops.adds += adds
    return result


def subtract_digits(x, y, ops):
    """x - y for digit lists with value(x) >= value(y) and len(x) >= len(y). Counts 2 subtractions per digit."""
    ly = len(y)
    result = [0] * len(x)
    borrow = 0
    adds = 0
    for i in range(len(x)):
        t = x[i] - (y[i] if i < ly else 0) - borrow         # 2 subtractions (digit - digit - borrow)
        adds += 2
        if t < 0:
            t += 10
            borrow = 1
        else:
            borrow = 0
        result[i] = t
    ops.adds += adds
    return result


def abs_difference(x, y, ops):
    """|x - y| (same length as x) and the sign of x - y (+1, 0 or -1) for equal-length digit lists."""
    sign = compare_magnitude(x, y)
    if sign >= 0:
        return subtract_digits(x, y, ops), sign
    return subtract_digits(y, x, ops), -1


def add_into(result, x, offset, ops):
    """result += x * 10**offset in place, propagating the carry. Counts 2 additions per digit of x
    and 1 per extra carry step."""
    carry = 0
    adds = 0
    for i, d in enumerate(x):
        t = result[offset + i] + d + carry
        adds += 2
        result[offset + i] = t % 10
        carry = t // 10
    k = offset + len(x)
    while carry:
        t = result[k] + carry
        adds += 1
        result[k] = t % 10
        carry = t // 10
        k += 1
    ops.adds += adds


# ----------------------------------------------------------------------------- the two methods
def schoolbook_multiply(a, b, ops):
    """Grade-school multiplication of digit lists a (n digits) and b (m digits) -> n + m digits.

    Every digit of a is multiplied by every digit of b: exactly n*m single-digit multiplications and
    2*n*m digit additions (each partial product is added to the accumulator together with the carry)."""
    n, m = len(a), len(b)
    result = [0] * (n + m)
    mults = adds = 0
    for i in range(n):
        ai = a[i]
        carry = 0
        for j in range(m):
            t = ai * b[j] + result[i + j] + carry           # 1 multiplication, 2 additions
            mults += 1
            adds += 2
            result[i + j] = t % 10
            carry = t // 10
        result[i + m] = carry                               # this position is still empty (0) here
    ops.mults += mults
    ops.adds += adds
    return result


def _record_level(ops, depth, mults, adds, temp_digits):
    """Add one node's own work to the per-level overhead breakdown (only when ops.levels is enabled)."""
    row = ops.levels.setdefault(depth, [0, 0, 0, 0])
    row[0] += 1
    row[1] += mults
    row[2] += adds
    row[3] += temp_digits


def karatsuba_multiply(a, b, ops, threshold=1, depth=0, trace=None, label="root"):
    """Karatsuba multiplication (subtractive variant) of two equal-length digit lists -> 2n digits.

    DIVIDE : split each number at m = ceil(n/2):  a = a1*10^m + a0,  b = b1*10^m + b0
             (the high halves are zero-padded to m digits, so every sub-problem has exactly m digits).
    CONQUER: three recursive m-digit products   z0 = a0*b0,  z2 = a1*b1,  z1' = |a0 - a1| * |b1 - b0|.
             |a0 - a1| < 10^m, so the middle operands also have m digits (the additive form a0 + a1 could
             have m + 1 digits).
    COMBINE: z1 = a0*b1 + a1*b0 = z0 + z2 + sign * z1'   and   a*b = z2*10^(2m) + z1*10^m + z0.
    Below the threshold (n <= threshold) the schoolbook method is used.
    With threshold 1 the number of single-digit multiplications is exactly 3^ceil(log2 n).
    """
    n = len(a)
    ops.calls += 1
    if depth > ops.max_depth:
        ops.max_depth = depth
    if n <= threshold:
        m0, a_before = ops.mults, ops.adds
        product = schoolbook_multiply(a, b, ops)
        if ops.levels is not None:                                  # overhead breakdown (optional)
            _record_level(ops, depth, ops.mults - m0, ops.adds - a_before, 2 * n)
    else:
        m = (n + 1) // 2                                            # DIVIDE
        pad = [0] * (2 * m - n)
        a0, a1 = a[:m], a[m:] + pad
        b0, b1 = b[:m], b[m:] + pad
        z0 = karatsuba_multiply(a0, b0, ops, threshold, depth + 1, trace, "z0")      # CONQUER
        z2 = karatsuba_multiply(a1, b1, ops, threshold, depth + 1, trace, "z2")
        own_adds = ops.adds
        diff_a, sign_a = abs_difference(a0, a1, ops)
        diff_b, sign_b = abs_difference(b1, b0, ops)
        own_adds = ops.adds - own_adds
        z1_mid = karatsuba_multiply(diff_a, diff_b, ops, threshold, depth + 1, trace,
                                    "z1'" + ("(-)" if sign_a * sign_b < 0 else ""))
        combine_start = ops.adds
        middle = add_digits(z0, z2, ops)                                              # COMBINE
        if sign_a * sign_b > 0:
            middle = add_digits(middle, z1_mid, ops)
        elif sign_a * sign_b < 0:
            middle = subtract_digits(middle, z1_mid, ops)
        product = z0 + z2 + [0, 0]          # z0 at 10^0 and z2 at 10^(2m): placed side by side, no additions
        add_into(product, middle, m, ops)
        product = product[:2 * n]           # an n-digit x n-digit product has at most 2n digits
        if ops.levels is not None:          # temporaries: 4 halves, 2 differences, middle sum(s), product
            own_adds += ops.adds - combine_start
            _record_level(ops, depth, 0, own_adds, 6 * m + 2 * (2 * m + 2) + 4 * m + 2 + 2 * n)
    if trace is not None:
        trace.append((depth, label, from_digits(a), from_digits(b), from_digits(product)))
    return product


def karatsuba_additive(a, b, ops, threshold=3, depth=0):
    """Textbook ADDITIVE Karatsuba, z1 = (a0 + a1)(b0 + b1) - z0 - z2, kept only for comparison.

    The sums a0 + a1 and b0 + b1 can have m + 1 digits, so the middle sub-problem is sometimes larger than
    n/2: the multiplication count depends on the data, and for n <= 3 the middle problem would not shrink at
    all (m + 1 >= n), so the recursion needs a larger base case (schoolbook for n <= threshold, threshold >= 3)."""
    n = len(a)
    ops.calls += 1
    ops.max_depth = max(ops.max_depth, depth)
    if n <= max(threshold, 3):
        return schoolbook_multiply(a, b, ops)
    m = (n + 1) // 2
    pad = [0] * (2 * m - n)
    a0, a1 = a[:m], a[m:] + pad
    b0, b1 = b[:m], b[m:] + pad
    z0 = karatsuba_additive(a0, b0, ops, threshold, depth + 1)
    z2 = karatsuba_additive(a1, b1, ops, threshold, depth + 1)
    sum_a, sum_b = add_digits(a0, a1, ops), add_digits(b0, b1, ops)       # m + 1 digits each
    if sum_a[-1] == 0 and sum_b[-1] == 0:                                  # no carry: m-digit sub-problem
        sum_a, sum_b = sum_a[:-1], sum_b[:-1]
    z1 = karatsuba_additive(sum_a, sum_b, ops, threshold, depth + 1)
    z1 = subtract_digits(subtract_digits(z1, z0, ops), z2, ops)
    product = z0 + z2 + [0, 0]
    add_into(product, z1, m, ops)
    return product[:2 * n]


def predicted_karatsuba_mults(n, threshold=1):
    """Single-digit multiplications predicted by M(n) = 3 M(ceil(n/2)), M(n) = n^2 for n <= threshold."""
    if n <= threshold:
        return n * n
    return 3 * predicted_karatsuba_mults((n + 1) // 2, threshold)


def multiply_ints(x, y, method="karatsuba", threshold=1):
    """Multiply two non-negative ints with the chosen method; returns (product, OpCounter)."""
    n = max(len(str(x)), len(str(y)))
    a, b = to_digits(x, n), to_digits(y, n)
    ops = OpCounter()
    if method == "schoolbook":
        digits = schoolbook_multiply(a, b, ops)
    elif method == "additive":
        digits = karatsuba_additive(a, b, ops, max(threshold, 3))
    else:
        digits = karatsuba_multiply(a, b, ops, threshold)
    return from_digits(digits), ops


# ----------------------------------------------------------------------------- demo
def main():
    print("Q3 - KARATSUBA vs SCHOOLBOOK MULTIPLICATION ON DIGIT ARRAYS (demo)")
    print("=" * 100)

    print("\n1) Recursion trace of 1234 x 5678 (Karatsuba, threshold 1, subtractive variant)")
    trace = []
    ops = OpCounter()
    product = karatsuba_multiply(to_digits(1234), to_digits(5678), ops, 1, trace=trace)
    for depth, label, x, y, p in sorted(trace, key=lambda r: r[0]):
        if depth <= 1:
            print(f"   level {depth}  {label:<8} {x:>5} x {y:<5} = {p}")
    print(f"   result {from_digits(product)}  (Python int: {1234 * 5678})   single-digit mults = {ops.mults} "
          f"= 3^2   schoolbook would need 4^2 = 16")

    print("\n2) Counted single-digit multiplications against the closed forms (random n-digit operands, seed 42)")
    rng = random.Random(42)
    print(f"   {'n':>5} | {'schoolbook':>10} {'n^2':>10} | {'Karatsuba':>10} {'3^ceil(lg n)':>12} | "
          f"{'depth':>5} | correct")
    print("   " + "-" * 78)
    for n in (4, 8, 16, 100, 617, 1234):
        a, b = random_digits(n, rng), random_digits(n, rng)
        x, y = from_digits(a), from_digits(b)
        ops_s, ops_k = OpCounter(), OpCounter()
        ps = from_digits(schoolbook_multiply(a, b, ops_s))
        pk = from_digits(karatsuba_multiply(a, b, ops_k))
        ok = ps == pk == x * y
        print(f"   {n:>5} | {ops_s.mults:>10,} {n * n:>10,} | {ops_k.mults:>10,} "
              f"{3 ** math.ceil(math.log2(n)):>12,} | {ops_k.max_depth:>5} | {'yes' if ok else 'NO'}")

    print("\n3) Why the subtractive variant: additive vs subtractive Karatsuba on random 64-digit pairs")
    print("   Both use the schoolbook base case n <= 3 (the additive variant needs it: for n <= 3 its middle")
    print("   operands a0 + a1 have m + 1 >= n digits, so the problem would not shrink).")
    print(f"   Predicted subtractive count: M(64) = 3^5 * M(2) = 243 * 4 = {predicted_karatsuba_mults(64, 3)}")
    for trial in range(4):
        a, b = random_digits(64, rng), random_digits(64, rng)
        ops_a, ops_k = OpCounter(), OpCounter()
        pa = from_digits(karatsuba_additive(a, b, ops_a, 3))
        pk = from_digits(karatsuba_multiply(a, b, ops_k, 3))
        print(f"   pair {trial + 1}: additive mults = {ops_a.mults:>5,}   subtractive mults = {ops_k.mults:>5,}"
              f"   both correct: {pa == pk == from_digits(a) * from_digits(b)}")
    nines = [9] * 64
    ops_a = OpCounter()
    karatsuba_additive(nines, nines, ops_a, 3)
    print(f"   all-nines operands (a carry at every level): additive mults = {ops_a.mults:,}"
          f"  -> the additive count depends on the data")


if __name__ == "__main__":
    main()
