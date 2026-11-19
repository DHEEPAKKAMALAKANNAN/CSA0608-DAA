"""Q7 Stage 1 - Student B's INDEPENDENT initial proposal (kept unchanged as evidence; it is NOT the final design).

Problem: most profitable contiguous run of delivery hours (maximum subarray sum of hourly profits p[0..n-1]).

Student B's proposal (written before discussing with Student A):
  decomposition : split the hours into a left and a right half at the middle
  base case     : one hour x -> (total, best prefix, best suffix, best) = (x, max(x, 0), max(x, 0), max(x, 0))
                  (an empty prefix / suffix / run of value 0 was allowed)
  information   : each half returns the 4 numbers (total, best prefix, best suffix, best run) - sums only
  combine       : total = L.total + R.total
                  prefix = max(L.prefix, L.total + R.prefix);  suffix = max(R.suffix, R.total + L.suffix)
                  best   = max(L.best, R.best, L.suffix + R.prefix)      <- the crossing run, in O(1)
Known defects (found in Stage 2): (1) because empty runs are allowed, a day on which EVERY hour is a loss returns
0 instead of the least-bad hour; (2) only sums are returned, so the operations manager does not learn WHICH hours.
Run:  py -3 proposal_b_four_tuple.py
"""
import random


def proposal_b(p, lo=0, hi=None):
    """Student B's initial D&C: returns (total, prefix, suffix, best) with empty runs allowed."""
    if hi is None:
        hi = len(p) - 1
    if lo == hi:                                    # base case: one hour (empty choice allowed -> max(x, 0))
        x = p[lo]
        return x, max(x, 0), max(x, 0), max(x, 0)
    mid = (lo + hi) // 2                            # divide at the middle
    lt, lp, ls, lb = proposal_b(p, lo, mid)         # conquer
    rt, rp, rs, rb = proposal_b(p, mid + 1, hi)
    return (lt + rt, max(lp, lt + rp), max(rs, rt + ls), max(lb, rb, ls + rp))   # combine in O(1)


def brute_force(p):
    """Reference: best sum over all n(n+1)/2 non-empty runs."""
    return max(sum(p[i:j + 1]) for i in range(len(p)) for j in range(i, len(p)))


def main():
    print("=" * 96)
    print("Q7 STAGE 1 - Student B's initial proposal: 4-number summary per half, O(1) combine")
    print("=" * 96)
    p = [-120, 340, -60, 410, -380, 150, 220, -90]
    print(f"Hours 0-7 (Rs): {p}")
    print(f"   proposal B (total, prefix, suffix, best): {proposal_b(p)}   brute force best: {brute_force(p)}")
    print("   -> correct best sum, crossing run found as L.suffix + R.prefix; but no start/end hour is reported")
    storm = [-40, -15, -90, -25]
    print(f"\nStorm day, every hour a loss (Rs): {storm}")
    print(f"   proposal B best = {proposal_b(storm)[3]}   brute force best = {brute_force(storm)} (hour 1 alone)")
    print("   -> proposal B returns 0 = 'an empty run', which is not a run of operating hours")
    rng = random.Random(42)
    print("\nRandom data, 500 instances per size: mixed hours (-400..400) and all-loss hours (-400..-1)")
    print(f"{'n':>6} | {'mixed: wrong':>13} | {'all-loss: wrong':>15}")
    for n in (2, 4, 8, 16, 32, 64):
        wm = sum(proposal_b(q)[3] != brute_force(q)
                 for q in ([rng.randint(-400, 400) for _ in range(n)] for _ in range(500)))
        wl = sum(proposal_b(q)[3] != brute_force(q)
                 for q in ([rng.randint(-400, -1) for _ in range(n)] for _ in range(500)))
        print(f"{n:>6} | {wm:>5} = {100 * wm / 500:>5.1f}% | {wl:>7} = {100 * wl / 500:>5.1f}%")
    print("Conclusion: the O(1) combine is right, but runs must be non-empty and the hours must be returned.")


if __name__ == "__main__":
    main()
