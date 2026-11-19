"""Q7 Stage 1 - Student A's INDEPENDENT initial proposal (kept unchanged as evidence; it is NOT the final design).

Problem: most profitable contiguous run of delivery hours (maximum subarray sum of hourly profits p[0..n-1]).

Student A's proposal (written before discussing with Student B):
  decomposition : split the hours at the middle, mid = (lo + hi) // 2
  base case     : one hour -> the run is that hour (sum p[lo], hours lo..lo)
  information   : each half returns its best run (sum, start hour, end hour)
  combine       : keep the better of the two halves' runs
Known defect (found in Stage 2): a run that CROSSES the middle (starts in the left half, ends in the right half) is
never considered, so the answer can be too small. This program demonstrates the defect against brute force.
Run:  py -3 proposal_a_midpoint_split.py
"""
import random


def proposal_a(p, lo=0, hi=None):
    """Student A's initial D&C: returns (best_sum, i, j) of the better half - misses crossing runs."""
    if hi is None:
        hi = len(p) - 1
    if lo == hi:                                    # base case: a single hour
        return p[lo], lo, hi
    mid = (lo + hi) // 2                            # divide at the middle
    left = proposal_a(p, lo, mid)                   # conquer
    right = proposal_a(p, mid + 1, hi)
    return left if left[0] >= right[0] else right   # combine: better half only (crossing case missing)


def brute_force(p):
    """Reference: best sum over all n(n+1)/2 runs."""
    return max(sum(p[i:j + 1]) for i in range(len(p)) for j in range(i, len(p)))


def main():
    print("=" * 96)
    print("Q7 STAGE 1 - Student A's initial proposal: split at the middle, return the better half's best run")
    print("=" * 96)
    p = [-120, 340, -60, 410, -380, 150, 220, -90]
    a = proposal_a(p)
    print(f"Hours 0-7 (Rs): {p}")
    print(f"   proposal A : profit Rs {a[0]} (hours {a[1]}..{a[2]})")
    print(f"   brute force: profit Rs {brute_force(p)} (hours 1..3 = 340 - 60 + 410) -> the best run CROSSES the")
    print("                split between hours 1 and 2 of the left half, which proposal A never examines")
    rng = random.Random(42)
    print("\nRandom hourly profit/loss data (values -400..400), 500 instances per size:")
    print(f"{'n':>6} | {'wrong answers':>14} | {'mean shortfall (Rs)':>19} | {'worst shortfall (Rs)':>20}")
    for n in (2, 4, 8, 16, 32, 64):
        wrong, short, worst = 0, 0, 0
        for _ in range(500):
            q = [rng.randint(-400, 400) for _ in range(n)]
            gap = brute_force(q) - proposal_a(q)[0]
            wrong += gap > 0
            short += gap
            worst = max(worst, gap)
        print(f"{n:>6} | {wrong:>6} = {100 * wrong / 500:>5.1f}% | {short / 500:>19.1f} | {worst:>20}")
    print("Conclusion: correct only when the best run lies entirely inside one half -> a crossing case is required.")


if __name__ == "__main__":
    main()
