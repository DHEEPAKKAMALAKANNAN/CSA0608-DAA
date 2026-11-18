"""ShopSphere audit - part (f): the nightly report generator costs f(n) = 3n^2 + 10 n log2 n + 50.

Claim 1  f(n) = Theta(n^2).  Formal definition: there are c1, c2 > 0 and n0 with
         c1 n^2 <= f(n) <= c2 n^2 for all n >= n0.
         Pair A (simple): for n >= 1, log2 n >= 0 gives f(n) >= 3n^2; log2 n <= n and 1 <= n^2 give
                          f(n) <= 3n^2 + 10n^2 + 50n^2 = 63n^2.            -> c1 = 3, c2 = 63, n0 = 1
         Pair B (tight):  f(n) <= 4n^2  <=>  g(n) = n^2 - 10 n log2 n - 50 >= 0, which first holds at
                          n = 60 and g keeps increasing afterwards.        -> c1 = 3, c2 = 4, n0 = 60
Claim 2  f(n) is not O(n): f(n) <= c n for all n >= n0 would force 3n^2 <= c n, i.e. n <= c/3, which is
         false for every n > max(n0, c/3). The program exhibits such an n for several c.

This program checks both constant pairs for every integer n up to 10^6, finds the smallest n0 for c2 = 4,
prints f(n)/n^2 (-> 3) and f(n)/n (unbounded) and the witnesses that defeat every proposed O(n) constant.
"""
import math

from audit_common import (NIGHTLY_WINDOW_S, OPS_PER_SECOND, banner, check, fmt_int, fmt_time,
                          print_table, section, verdict, write_csv)

LIMIT = 1_000_000


def f(n):
    """Operation count of the nightly report generator."""
    return 3 * n * n + 10 * n * math.log2(n) + 50


def violations(c1, c2, n0, n_max=LIMIT):
    """Number of integers n in [n0, n_max] for which c1 n^2 <= f(n) <= c2 n^2 is FALSE."""
    return sum(not (c1 * n * n <= f(n) <= c2 * n * n) for n in range(n0, n_max + 1))


def smallest_n0(c2, n_max=LIMIT):
    """Smallest n0 such that f(n) <= c2 n^2 for every n in [n0, n_max]."""
    n0 = 1
    for n in range(1, n_max + 1):
        if f(n) > c2 * n * n:
            n0 = n + 1
    return n0


def main():
    banner("ShopSphere audit - part (f): f(n) = 3n^2 + 10 n log2 n + 50 is Theta(n^2), not O(n)")

    section("1. Checking the constant pairs for every integer n up to 10^6")
    ok = check("pair A (c1=3, c2=63, n0=1): violations", 0, violations(3, 63, 1))
    ok &= check("pair B (c1=3, c2=4, n0=60): violations", 0, violations(3, 4, 60))
    ok &= check("smallest n0 that works with c2 = 4", 60, smallest_n0(4))
    ok &= check("n = 59 breaks c2 = 4: f(59) > 4*59^2", True, f(59) > 4 * 59 * 59)
    print(f"  f(1) = {f(1):g} -> the largest f(n)/n^2 for n >= 1 is 53 (at n = 1), so c2 = 63 is safe.")
    print(f"  g(n) = n^2 - 10 n log2 n - 50: g(59) = {59**2 - 10*59*math.log2(59) - 50:.2f}, "
          f"g(60) = {60**2 - 10*60*math.log2(60) - 50:.2f}, and g'(n) = 2n - 10 log2 n - 10/ln 2 > 0 "
          "for n >= 60.")

    section("2. Ratios: f(n)/n^2 tends to 3 (Theta(n^2)); f(n)/n grows without bound (not O(n))")
    rows, csv_rows = [], []
    for n in (1, 2, 10, 60, 100, 1000, 10**4, 10**5, 10**6):
        value = f(n)
        rows.append([fmt_int(n), f"{value:,.0f}", f"{3 * n * n:,}", f"{value / n**2:.6f}",
                     f"{value / n:,.1f}",
                     f"{3 * n * n / value:.4%}"])
        csv_rows.append([n, round(value, 3), value / n**2, value / n])
    print_table(["n", "f(n)", "3n^2", "f(n)/n^2", "f(n)/n", "share of 3n^2"], rows)
    write_csv("f_bound_check.csv", ["n", "f_n", "f_over_n2", "f_over_n"], csv_rows)

    section("3. f(n) is not O(n): for any proposed constant c, n = floor(c/3) + 1 gives f(n) > c n")
    rows = []
    for c in (10, 1000, 10**6, 10**9):
        n = c // 3 + 1
        beaten = f(n) > c * n
        ok &= beaten
        rows.append([fmt_int(c), fmt_int(n), f"{f(n):.4e}", f"{c * n:.4e}", f"{f(n) - c * n:.4e}",
                     verdict(beaten)])
    print_table(["proposed c", "witness n", "f(n)", "c * n", "f(n) - c n", "f(n) > c n ?"], rows)
    print("  Whatever c and n0 are chosen, every n > max(n0, c/3) is a counter-example: f(n) is not O(n).")

    section(f"4. Cost of the report generator at the audit sizes ({OPS_PER_SECOND:.0e} ops/s)")
    rows = []
    for n in (100_000, 1_000_000):
        secs = f(n) / OPS_PER_SECOND
        rows.append([fmt_int(n), f"{f(n):.4e}", f"{secs:,.0f} s", fmt_time(secs),
                     verdict(secs <= NIGHTLY_WINDOW_S)])
    print_table(["n", "f(n)", "seconds", "readable", "fits 10 min?"], rows)
    print(f"\nSelf-check: {verdict(ok)}")


if __name__ == "__main__":
    main()
