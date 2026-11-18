"""ShopSphere audit - Module M3: Product Search, versions S1 and S2 (parts (a), (c), (e) and (g)).

S1  sequential search: scan the unsorted catalogue from the front until the product is found.
    Basic operation: key comparison  catalogue[i] == key.
S2  binary search on the sorted product index: compare the key with the middle entry and discard
    half of the index. Basic operation: one three-way comparison of the key with index[mid].
    Recurrence T(n) = T(n/2) + 1, T(1) = 1  ->  T(n) = log2 n + 1 (n = 2^k); floor(log2 n) + 1 in general.

The program checks both searches against Python's own lookup, measures best / average / worst
comparison counts by running every possible search, verifies the backward-substitution closed form,
measures the recursion depth (space) of a recursive S2, and checks the S1 average-case formula
C_avg(p) = p(n+1)/2 + n(1-p) exactly (n = 1,000) and by simulation (n = 10,000).
"""
import math
import random
from fractions import Fraction

from audit_common import (OPS_PER_SECOND, banner, check, fmt_time, print_table, section, verdict,
                          write_csv)


# --------------------------------------------------------------------------- the two search versions
def sequential_search(catalogue, key):
    """S1. Return (position or -1, number of key comparisons)."""
    comparisons = 0
    for i in range(len(catalogue)):
        comparisons += 1                      # basic operation: catalogue[i] == key
        if catalogue[i] == key:
            return i, comparisons
    return -1, comparisons


def binary_search_iterative(index, key):
    """S2, iterative version. Return (position or -1, comparisons). Extra space: lo, hi, mid -> Theta(1)."""
    lo, hi, comparisons = 0, len(index) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        comparisons += 1                      # one three-way comparison of key with index[mid]
        if key == index[mid]:
            return mid, comparisons
        if key < index[mid]:
            hi = mid - 1                      # discard the right half
        else:
            lo = mid + 1                      # discard the left half
    return -1, comparisons


def binary_search_recursive(index, key, lo=0, hi=None, depth=1):
    """S2, recursive version. Return (position or -1, comparisons, deepest call-stack depth)."""
    if hi is None:
        hi = len(index) - 1
    if lo > hi:                               # empty range: unsuccessful search
        return -1, 0, depth
    mid = (lo + hi) // 2
    if key == index[mid]:
        return mid, 1, depth
    if key < index[mid]:
        pos, comps, deepest = binary_search_recursive(index, key, lo, mid - 1, depth + 1)
    else:
        pos, comps, deepest = binary_search_recursive(index, key, mid + 1, hi, depth + 1)
    return pos, comps + 1, deepest


def recurrence_T(n):
    """T(n) = T(floor(n/2)) + 1 with T(1) = 1, evaluated by unfolding (backward substitution)."""
    steps = 1
    while n > 1:
        n //= 2
        steps += 1
    return steps


def make_index(n, seed=42):
    """Sorted, distinct, even product IDs; every odd number is guaranteed absent."""
    return sorted(random.Random(seed).sample(range(0, 40 * n, 2), n))


def gap_keys(index):
    """One absent key in each of the n+1 gaps (before, between and after the IDs)."""
    return [index[0] - 1] + [x + 1 for x in index]


def s2_profile(index, recursive=False):
    """Run S2 for every present key and every gap; return best/avg/worst comparisons and max depth."""
    succ, fail, depth = [], [], 0
    for key in index:
        if recursive:
            _, c, d = binary_search_recursive(index, key)
            depth = max(depth, d)
        else:
            c = binary_search_iterative(index, key)[1]
        succ.append(c)
    for key in gap_keys(index):
        if recursive:
            _, c, d = binary_search_recursive(index, key)
            depth = max(depth, d)
        else:
            c = binary_search_iterative(index, key)[1]
        fail.append(c)
    return min(succ), sum(succ) / len(succ), max(succ + fail), sum(fail) / len(fail), depth


def s1_average_formula(n, p):
    """Derived S1 average: p(n+1)/2 + n(1-p), computed exactly with fractions."""
    p = Fraction(p)
    return p * Fraction(n + 1, 2) + n * (1 - p)


def main():
    banner("ShopSphere audit - M3 Product Search: S1 sequential vs S2 binary")
    rng = random.Random(42)

    section("1. Correctness against Python's own lookup (n = 2,000; all present and absent keys)")
    index = make_index(2000)
    catalogue = index[:]
    rng.shuffle(catalogue)
    where = {key: pos for pos, key in enumerate(catalogue)}
    ok = check("S1 positions == dict lookup (2,000 keys)", True,
               all(sequential_search(catalogue, k)[0] == where[k] for k in index))
    ok &= check("S2 iterative positions == list.index", True,
                all(binary_search_iterative(index, k)[0] == index.index(k) for k in index[::7]))
    ok &= check("S2 recursive == S2 iterative (all keys)", True,
                all(binary_search_recursive(index, k)[:2] == binary_search_iterative(index, k)
                    for k in index + gap_keys(index)))
    ok &= check("absent keys -> -1 in S1 and S2", True,
                all(sequential_search(catalogue, k)[0] == binary_search_iterative(index, k)[0] == -1
                    for k in gap_keys(index)[::25]))

    section("2. Part (c): T(n) = T(n/2) + 1 -> log2 n + 1, vs worst case counted by running S2")
    rows = []
    for k in (0, 1, 2, 3, 4, 8, 12, 16):
        n = 2 ** k
        _, _, worst, _, depth = s2_profile(make_index(n, seed=k), recursive=True)
        good = recurrence_T(n) == k + 1 == worst
        ok &= good
        rows.append([k, f"{n:,}", recurrence_T(n), k + 1, worst, depth, verdict(good)])
    print_table(["k", "n = 2^k", "T(n) unfolded", "log2 n + 1", "worst counted", "max stack depth",
                 "match"], rows)
    bad = sum(recurrence_T(n) != math.floor(math.log2(n)) + 1 for n in range(1, 1_000_001))
    ok &= check("n = 1..10^6 with T(n) != floor(log2 n) + 1", 0, bad)

    section("3. Part (e): best / average / worst comparisons, measured by running every search")
    rows, csv_rows = [], []
    for n in (1000, 1024, 1_000_000):
        index = make_index(n, seed=n)
        best, avg_s, worst, avg_u, _ = s2_profile(index)
        if n <= 1024:                          # S1: run every successful search (n^2/2 comparisons)
            s1_avg = sum(sequential_search(index, k)[1] for k in index) / n
            s1_src = "measured"
        else:                                  # 5*10^11 comparisons is too many: use (n+1)/2
            s1_avg, s1_src = (n + 1) / 2, "formula"
        s1_best = sequential_search(index, index[0])[1]
        s1_worst = max(sequential_search(index, index[-1])[1], sequential_search(index, -1)[1])
        ok &= s1_best == 1 and s1_worst == n and s1_avg == (n + 1) / 2
        ok &= best == 1 and worst == math.floor(math.log2(n)) + 1
        rows.append([f"{n:,}", s1_best, f"{s1_avg:,.1f} ({s1_src})", f"{s1_worst:,}", best,
                     f"{avg_s:.3f} / {avg_u:.3f}", worst])
        csv_rows.append([n, s1_best, s1_avg, s1_worst, best, round(avg_s, 4), round(avg_u, 4), worst])
    print_table(["n", "S1 best", "S1 avg (found)", "S1 worst", "S2 best", "S2 avg found / absent",
                 "S2 worst"], rows)
    write_csv("m3_search_cases.csv", ["n", "s1_best", "s1_avg_success", "s1_worst", "s2_best",
                                      "s2_avg_success", "s2_avg_fail", "s2_worst"], csv_rows)
    print("S2 worst = floor(log2 n) + 1 (20 for n = 10^6); S2 average found ~ log2 n - 1.")

    section("4. S1 average with success probability p: C_avg(p) = p(n+1)/2 + n(1-p)")
    n = 1000
    index = make_index(n, seed=7)
    succ_avg = Fraction(sum(sequential_search(index, k)[1] for k in index), n)
    fail_avg = Fraction(sum(sequential_search(index, k)[1] for k in gap_keys(index)), n + 1)
    for p in (0, Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), 1):
        ok &= check(f"n = 1,000, p = {p}: exact mixture of all runs", s1_average_formula(n, p),
                    p * succ_avg + (1 - p) * fail_avg)
    n, p, trials = 10_000, 0.5, 4000
    index = make_index(n, seed=11)
    total = 0
    for _ in range(trials):
        key = rng.choice(index) if rng.random() < p else rng.randrange(0, 40 * n, 2) + 1
        total += sequential_search(index, key)[1]
    expected = float(s1_average_formula(n, p))
    print(f"  Simulation n = 10,000, p = 0.5, {trials:,} searches: mean = {total / trials:,.1f}, "
          f"formula = {expected:,.2f}, error = {abs(total / trials - expected) / expected:.2%}")
    big = s1_average_formula(10**6, Fraction(1, 2))
    ok &= check("n = 10^6, p = 0.5: p(n+1)/2 + n(1-p)", Fraction(3000001, 4), big)
    print(f"  = {float(big):,.2f} comparisons -> {fmt_time(float(big) / OPS_PER_SECOND)} per search "
          f"at 10^8 ops/s, versus <= 20 comparisons ({fmt_time(20 / OPS_PER_SECOND)}) for S2.")
    print(f"\nSelf-check: {verdict(ok)}")


if __name__ == "__main__":
    main()
