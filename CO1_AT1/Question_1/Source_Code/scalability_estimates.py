"""ShopSphere audit - part (g): operation and running-time estimates for the CTO (10^8 operations / second).

Every module is evaluated with the cost function derived in parts (b)-(f):
    M1 duplicate detector        C(n) = n(n-1)/2
    M2 rate limiter              A(n) = 2^ceil(log2 n) - 1
    S1 sequential search         p(n+1)/2 + n(1-p) per search, p = 0.5
    S2 binary search             floor(log2 n) + 1 per search (worst case)
    M4 current / redesign        2n^2 - n  /  n log2 n + n
    M5 sales analytics           n log2 n (log2 n + 1)/2 + n
    report generator             f(n) = 3n^2 + 10 n log2 n + 50
    M1 redesigns                 hash set: n lookups;  sort + scan: n log2 n + (n - 1) comparisons
The program prints operations and time for n = 10^5 (today) and n = 10^6 (in a year), the PASS/FAIL
verdict against the 10-minute nightly window, the growth factor, and the largest catalogue size each
batch module can handle inside the window.
"""
import math

from audit_common import (NIGHTLY_WINDOW_S, N_CURRENT, N_FUTURE, OPS_PER_SECOND, banner, fmt_time,
                          print_table, section, verdict, write_csv)

# name -> (growth class, cost function, is it a nightly batch job?)
MODULES = {
    "M1 duplicate detector":     ("Theta(n^2)",       lambda n: n * (n - 1) / 2, True),
    "M2 rate limiter":           ("Theta(n)",         lambda n: 2 ** (n - 1).bit_length() - 1, True),
    "S1 sequential (1 search)":  ("Theta(n)",         lambda n: 0.5 * (n + 1) / 2 + n * 0.5, False),
    "S2 binary (1 search)":      ("Theta(log n)",     lambda n: math.floor(math.log2(n)) + 1, False),
    "M4 current (4 parts)":      ("Theta(n^2)",       lambda n: 2 * n * n - n, True),
    "M4 redesign (2 parts)":     ("Theta(n log n)",   lambda n: n * math.log2(n) + n, True),
    "M5 sales analytics":        ("Theta(n log^2 n)", lambda n: n * math.log2(n) * (math.log2(n) + 1) / 2 + n,
                                  True),
    "Report generator f(n)":     ("Theta(n^2)",       lambda n: 3 * n * n + 10 * n * math.log2(n) + 50, True),
    "M1 redesign: hash set":     ("Theta(n) exp.",    lambda n: n, True),
    "M1 redesign: sort + scan":  ("Theta(n log n)",   lambda n: n * math.log2(n) + n - 1, True),
}


def seconds(ops):
    """Running time at the stated server speed."""
    return ops / OPS_PER_SECOND


def largest_n_within_window(cost, hi=10**12):
    """Largest n whose cost fits in the nightly window (binary search; cost is increasing in n)."""
    budget = NIGHTLY_WINDOW_S * OPS_PER_SECOND
    if cost(hi) <= budget:
        return None                                  # fits for every n we consider
    lo = 2
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if cost(mid) <= budget:
            lo = mid
        else:
            hi = mid - 1
    return lo


def estimates(n):
    """Dictionary module -> (operations, seconds, fits-in-window) for catalogue size n."""
    return {name: (cost(n), seconds(cost(n)), seconds(cost(n)) <= NIGHTLY_WINDOW_S)
            for name, (_, cost, _) in MODULES.items()}


def main():
    banner("ShopSphere audit - part (g): scalability estimates at 10^8 basic operations per second")
    now, later = estimates(N_CURRENT), estimates(N_FUTURE)

    section(f"1. Operations and time: n = {N_CURRENT:,} today vs n = {N_FUTURE:,} in a year (window = 600 s)")
    rows, csv_rows = [], []
    for name, (growth, cost, batch) in MODULES.items():
        ops5, t5, ok5 = now[name]
        ops6, t6, ok6 = later[name]
        rows.append([name, growth, f"{ops5:.3e}", fmt_time(t5), f"{ops6:.3e}", fmt_time(t6),
                     f"x{ops6 / ops5:,.1f}", verdict(ok6) if batch else "per query"])
        csv_rows.append([name, growth, ops5, t5, ops6, t6, ops6 / ops5,
                         verdict(ok6) if batch else "per query"])
    print_table(["module", "growth", "ops n=10^5", "time", "ops n=10^6", "time", "growth", "10 min @10^6"],
                rows, right={2, 3, 4, 5, 6})
    write_csv("scalability_estimates.csv", ["module", "growth", "ops_1e5", "seconds_1e5", "ops_1e6",
                                            "seconds_1e6", "growth_factor", "verdict_1e6"], csv_rows)

    section("2. Largest catalogue each batch module can process inside the 10-minute window")
    rows, csv_rows = [], []
    for name, (growth, cost, batch) in MODULES.items():
        if not batch:
            continue
        limit = largest_n_within_window(cost)
        rows.append([name, growth, "beyond 10^12" if limit is None else f"{limit:,}",
                     "yes" if limit is None or limit >= N_FUTURE else "NO - redesign"])
        csv_rows.append([name, growth, limit])
    print_table(["module", "growth", "max n in 600 s", "OK at 10^6?"], rows, right={2})
    write_csv("scalability_window_limits.csv", ["module", "growth", "max_n_in_600s"], csv_rows)

    section("3. Search throughput at n = 10^6 (searches per second on one server)")
    s1, s2 = later["S1 sequential (1 search)"][0], later["S2 binary (1 search)"][0]
    print(f"  S1: {s1:,.2f} comparisons per search -> {OPS_PER_SECOND / s1:,.0f} searches/s")
    print(f"  S2: {s2:,.0f} comparisons per search (worst) -> {OPS_PER_SECOND / s2:,.0f} searches/s"
          f"  ({s1 / s2:,.0f} times more)")

    failing = [name for name, (_, _, ok) in later.items() if MODULES[name][2] and not ok]
    print("\nModules that miss the 10-minute window at n = 10^6: " + ", ".join(failing))


if __name__ == "__main__":
    main()
