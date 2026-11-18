"""ShopSphere audit - Modules M4 and M5: Master Theorem and recursion trees (parts (d) and (g)).

M4 current  : T(n) = 4T(n/2) + n          a=4, b=2, n^(log_b a) = n^2, f(n) = n = O(n^(2-e))  -> Case 1
              exact (T(1) = 1, n = 2^k):  T(n) = 2n^2 - n                                   -> Theta(n^2)
M4 redesign : T(n) = 2T(n/2) + n          a=2, b=2, n^(log_b a) = n,   f(n) = Theta(n)      -> Case 2
              exact:                      T(n) = n log2 n + n                               -> Theta(n log n)
M5          : T(n) = 2T(n/2) + n log2 n   a=2, b=2, n^(log_b a) = n,   f(n)/n = log2 n is neither
              Theta(1) nor >= n^e, so none of the three basic cases applies; the extended Case 2
              (f = Theta(n log^1 n)) or the recursion tree gives
              exact:                      T(n) = n log2 n (log2 n + 1)/2 + n            -> Theta(n log^2 n)

The program evaluates each recurrence exactly for n = 2^k, compares it with the closed forms, prints the
recursion-tree level sums for n = 1,024, the doubling ratios T(2n)/T(n), the "polynomially larger" test
for M5, and the recurrences with integer halves at n = 10^5 and 10^6 (used for part (g)).
"""
import math
from functools import lru_cache

from audit_common import (NIGHTLY_WINDOW_S, OPS_PER_SECOND, banner, check, fmt_int, fmt_time,
                          print_table, section, verdict, write_csv)

# name -> (a, b, f(n) as text, f evaluated at n = 2^k given (n, k))
MODELS = {
    "M4 current":  (4, 2, "n",         lambda n, k: n),
    "M4 redesign": (2, 2, "n",         lambda n, k: n),
    "M5":          (2, 2, "n log2 n",  lambda n, k: n * k),
}


def T_power_of_two(model, k):
    """Exact T(2^k) by unfolding T(n) = a T(n/2) + f(n) from T(1) = 1 (integer arithmetic)."""
    a, _, _, f = MODELS[model]
    value = 1
    for j in range(1, k + 1):
        value = a * value + f(2 ** j, j)
    return value


def closed_form(model, n):
    """Closed forms derived in the report (valid exactly for n = 2^k, used as estimates otherwise)."""
    lg = math.log2(n)
    if model == "M4 current":
        return 2 * n * n - n
    if model == "M4 redesign":
        return n * lg + n
    return n * lg * (lg + 1) / 2 + n


@lru_cache(maxsize=None)
def T_integer(model, n):
    """Recurrence with integer halves floor(n/2), ceil(n/2) for any n >= 1 (T(1) = 1)."""
    if n <= 1:
        return 1
    lo, hi = n // 2, n - n // 2
    if model == "M4 current":        # four parts: two copies of each half
        return 2 * T_integer(model, lo) + 2 * T_integer(model, hi) + n
    if model == "M4 redesign":
        return T_integer(model, lo) + T_integer(model, hi) + n
    return T_integer(model, lo) + T_integer(model, hi) + n * math.log2(n)


def main():
    banner("ShopSphere audit - M4 Recommendation Engine and M5 Sales Analytics (recurrences)")

    section("1. Master Theorem parameters  T(n) = a T(n/b) + f(n)")
    rows = []
    cases = {"M4 current": ("n = O(n^(2-e)), e = 1", "Case 1", "Theta(n^2)"),
             "M4 redesign": ("n = Theta(n^1)", "Case 2", "Theta(n log n)"),
             "M5": ("n log n vs n: ratio log n", "none (gap)", "Theta(n log^2 n)")}
    for name, (a, b, f_text, _) in MODELS.items():
        crit = math.log(a) / math.log(b)
        rows.append([name, a, b, f_text, f"n^{crit:g}", *cases[name]])
    print_table(["module", "a", "b", "f(n)", "n^(log_b a)", "f(n) vs n^(log_b a)", "case", "result"],
                rows, right={1, 2})

    section("2. Exact T(2^k) from the recurrence vs the closed forms")
    rows, csv_rows, ok = [], [], True
    for k in range(0, 21):
        n = 2 ** k
        vals = [T_power_of_two(m, k) for m in MODELS]
        forms = [2 * n * n - n, n * k + n, n * k * (k + 1) // 2 + n]
        ok &= vals == forms
        csv_rows.append([k, n] + vals)
        if k in (0, 1, 2, 3, 4, 10, 15, 20):
            rows.append([k, fmt_int(n), fmt_int(vals[0]), fmt_int(vals[1]), fmt_int(vals[2]),
                         verdict(vals == forms)])
    print_table(["k", "n", "M4 cur: 2n^2-n", "M4 new: n lg n + n", "M5: n lg n(lg n+1)/2 + n",
                 "match"], rows)
    write_csv("m4_m5_recurrences.csv", ["k", "n", "T_m4_current", "T_m4_redesign", "T_m5"], csv_rows)
    ok &= check("all k = 0..20 equal the closed forms", True, ok)

    section("3. Recursion-tree level sums for n = 1,024 (level i has a^i nodes of size n/2^i)")
    n, k, rows = 1024, 10, []
    totals = [0, 0, 0]
    for i in range(k):
        size = n // 2 ** i
        level = [4 ** i * size, 2 ** i * size, 2 ** i * size * (k - i)]
        totals = [t + v for t, v in zip(totals, level)]
        rows.append([i, fmt_int(4 ** i), fmt_int(2 ** i), size, fmt_int(level[0]), fmt_int(level[1]),
                     fmt_int(level[2])])
    leaves = [4 ** k, 2 ** k, 2 ** k]
    totals = [t + v for t, v in zip(totals, leaves)]
    rows.append(["leaves", fmt_int(4 ** k), fmt_int(2 ** k), 1, *map(fmt_int, leaves)])
    rows.append(["total", "", "", "", *map(fmt_int, totals)])
    print_table(["level i", "nodes a=4", "nodes a=2", "size", "M4 cur: 2^i n", "M4 new: n",
                 "M5: n(lg n - i)"], rows)
    for name, total in zip(MODELS, totals):
        ok &= check(f"tree total == T(1024) for {name}", T_power_of_two(name, k), total)

    section("4. What happens when the data doubles: T(2n) / T(n)")
    rows = []
    for k in (5, 10, 15, 19):
        rows.append([f"2^{k} -> 2^{k + 1}"] +
                    [f"{T_power_of_two(m, k + 1) / T_power_of_two(m, k):.4f}" for m in MODELS])
    print_table(["n -> 2n", "M4 current", "M4 redesign", "M5"], rows)
    print("M4 current -> 4x (quadratic); redesign -> 2(lg n + 2)/(lg n + 1), just over 2x; "
          "M5 -> a bit more than 2x.")

    section("5. M5: is f(n) = n log2 n polynomially larger than n^(log_b a) = n?")
    rows = []
    for k in (10, 100, 1000, 2000, 5000):
        rows.append([f"2^{k}", k, f"{k / 2 ** (0.1 * k):.3e}", f"{k / 2 ** (0.01 * k):.3e}"])
    print_table(["n", "f(n)/n = log2 n", "log2 n / n^0.1", "log2 n / n^0.01"], rows)
    print("f(n)/n = log2 n grows (so not Case 2) but log2 n / n^e -> 0 for every e > 0 (so not Case 3):")
    print("the gap between Case 2 and Case 3. Extended Case 2 with k = 1 gives Theta(n log^2 n).")
    rows = []
    for k in (4, 8, 12, 16, 20):
        t = T_power_of_two("M5", k)
        n = 2 ** k
        rows.append([f"2^{k}", fmt_int(t), f"{t / (n * k):.3f}", f"{t / (n * k * k):.4f}"])
    print_table(["n", "T(n)", "T / (n log2 n)", "T / (n log2^2 n)"], rows)
    print("T/(n log n) keeps growing, T/(n log^2 n) settles towards 1/2: Theta(n log^2 n) confirmed.")

    section("6. Integer-halves recurrences at the audit sizes (part (g); 10^8 ops/s, window 600 s)")
    rows = []
    for name in MODELS:
        for n in (10**5, 10**6):
            exact, est = T_integer(name, n), closed_form(name, n)
            secs = exact / OPS_PER_SECOND
            rows.append([name, fmt_int(n), f"{est:.4e}", f"{exact:.4e}", f"{exact / est:.3f}",
                         fmt_time(secs), verdict(secs <= NIGHTLY_WINDOW_S)])
    print_table(["module", "n", "closed form", "integer recurrence", "ratio", "time", "fits 10 min?"],
                rows)
    print(f"\nSelf-check: {verdict(ok)}")


if __name__ == "__main__":
    main()
