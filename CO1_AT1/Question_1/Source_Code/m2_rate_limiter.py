"""ShopSphere audit - Module M2: API Rate Limiter (parts (a), (b) and (g)).

    i <- 1
    WHILE i < n DO
      FOR j <- 0 TO i-1 DO
        Audit(Request[j])          // basic operation
      END FOR
      i <- i * 2
    END WHILE

Input size      : n = number of requests in the audited log.
Basic operation : Audit(Request[j]) in the inner loop.
Derivation      : pass k (k = 0, 1, ..., m-1) has i = 2^k and performs exactly 2^k audits; the loop stops
                  at the first power of two >= n, so there are m = ceil(log2 n) passes and
                      A(n) = 2^0 + 2^1 + ... + 2^(m-1) = 2^m - 1 = 2^ceil(log2 n) - 1,
                  with n - 1 <= A(n) <= 2n - 3 for n >= 2. Hence A(n) is Theta(n), NOT Theta(n log n).

The program counts the audits for many n (powers and non-powers of 2), checks them against the closed
form and the bounds, traces n = 1,024 pass by pass, and contrasts the count with the claimed n log2 n.
"""
import math
import random

from audit_common import (NIGHTLY_WINDOW_S, N_CURRENT, N_FUTURE, OPS_PER_SECOND, banner, check,
                          fmt_int, fmt_time, min_time, print_table, section, verdict, write_csv)

RATE_LIMIT = 900          # a request whose "calls in the last minute" exceeds this is flagged


def make_requests(n, seed=42):
    """Simulated request log: request j = number of calls its client made in the last minute."""
    rng = random.Random(seed)
    return [rng.randint(1, 1000) for _ in range(n)]


def audit(request, stats):
    """Audit one request (the basic operation): count it and flag it if it breaks the rate limit."""
    stats["audits"] += 1
    if request > RATE_LIMIT:
        stats["flagged"] += 1


def run_rate_limiter(requests, trace=None):
    """The audited routine. Returns the number of Audit calls; optionally records (i, audits) per pass."""
    n = len(requests)
    stats = {"audits": 0, "flagged": 0}
    i = 1
    while i < n:                                  # WHILE i < n
        for j in range(0, i):                     # FOR j <- 0 TO i-1
            audit(requests[j], stats)             # Audit(Request[j])
        if trace is not None:
            trace.append((i, stats["audits"]))
        i = i * 2                                 # i <- i * 2
    return stats["audits"]


def ceil_log2(n):
    """Exact ceil(log2 n) for integers n >= 1 (no floating-point error)."""
    return (n - 1).bit_length()


def closed_form(n):
    """Derived number of audits A(n) = 2^ceil(log2 n) - 1 (0 when n <= 1)."""
    return 2 ** ceil_log2(n) - 1 if n > 1 else 0


def main():
    banner("ShopSphere audit - M2 API Rate Limiter (doubling windows)")

    section("1. Pass-by-pass trace for n = 1,024 (verification asked for in part (b))")
    trace = []
    total = run_rate_limiter(make_requests(1024), trace)
    rows, before = [], 0
    for k, (i, cumulative) in enumerate(trace):
        rows.append([k, fmt_int(i), f"j = 0..{i - 1}", fmt_int(cumulative - before), fmt_int(cumulative)])
        before = cumulative
    print_table(["pass k", "i = 2^k", "inner loop", "audits this pass", "cumulative audits"], rows)
    print(f"Loop exits when i = {2 ** len(trace):,} (not < 1,024) after {len(trace)} passes = log2 1024.")
    ok = check("A(1024) = 1 + 2 + ... + 512 = 2^10 - 1", 1023, total)
    ok &= check("A(1024) = n - 1 (n is a power of 2)", 1024 - 1, total)

    section("2. Counted audits vs closed form 2^ceil(log2 n) - 1 and the team's n log2 n claim")
    rows, csv_rows = [], []
    for n in (1, 2, 3, 5, 8, 100, 1000, 1023, 1024, 1025, 4096, 100_000, 1_000_000):
        counted = run_rate_limiter(make_requests(n, seed=n))
        claim = n * math.log2(n) if n > 1 else 0
        ok &= counted == closed_form(n)
        rows.append([fmt_int(n), ceil_log2(n), fmt_int(counted), fmt_int(closed_form(n)),
                     verdict(counted == closed_form(n)), f"{counted / n:.3f}", fmt_int(claim),
                     f"{claim / counted:.2f}" if counted else "-"])
        csv_rows.append([n, ceil_log2(n), counted, closed_form(n), round(claim, 2)])
    print_table(["n", "passes", "audits counted", "2^ceil(lg n)-1", "match", "audits/n",
                 "claimed n log2 n", "claim/actual"], rows)
    write_csv("m2_audit_counts.csv", ["n", "passes", "audits_counted", "closed_form", "n_log2_n"],
              csv_rows)

    section("3. Exhaustive check for every n = 2..3,000 (counted by running the loop)")
    mismatches = sum(run_rate_limiter([0] * n) != closed_form(n) for n in range(2, 3001))
    outside = sum(not (n - 1 <= closed_form(n) <= 2 * n - 3) for n in range(2, 1_000_001))
    ok &= check("n with counted != 2^ceil(log2 n) - 1", 0, mismatches)
    ok &= check("n <= 10^6 violating n-1 <= A(n) <= 2n-3", 0, outside)
    print("So (1/2)n <= A(n) <= 2n for all n >= 2: Theta(n) with c1 = 1/2, c2 = 2, n0 = 2.")

    section("4. Wall-clock doubling test (secondary evidence; counts above are primary)")
    rows, prev = [], None
    for n in (2**18, 2**19, 2**20, 2**21):
        best = min_time(run_rate_limiter, make_requests(n))
        rows.append([fmt_int(n), fmt_int(closed_form(n)), f"{best:.4f}",
                     f"{best / prev:.2f}" if prev else "-", f"{best / closed_form(n) * 1e9:.0f}"])
        prev = best
    print_table(["n", "audits", "time (s)", "time ratio", "ns per audit"], rows)
    print("Doubling n roughly doubles the time: linear behaviour, as the Theta(n) bound predicts.")

    section(f"5. Projection at {OPS_PER_SECOND:.0e} operations per second")
    rows = []
    for n in (N_CURRENT, N_FUTURE):
        secs = closed_form(n) / OPS_PER_SECOND
        rows.append([fmt_int(n), fmt_int(closed_form(n)), fmt_time(secs), verdict(secs <= NIGHTLY_WINDOW_S)])
    print_table(["n", "audits 2^ceil(lg n)-1", "time", "fits 10 min?"], rows)

    print(f"\nVerdict: the Theta(n log n) claim is an over-estimate; tight bound is Theta(n). "
          f"Self-check: {verdict(ok)}")


if __name__ == "__main__":
    main()
