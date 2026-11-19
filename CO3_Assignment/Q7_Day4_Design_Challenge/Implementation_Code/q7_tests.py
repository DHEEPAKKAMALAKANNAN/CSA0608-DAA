"""Q7 Stage 4 (Student B) - correctness tests of the joint D&C design (and of the baseline and the variants).

References: brute force over all runs and an independent Kadane scan. The two Stage-1 proposals are imported
to confirm (as tests) the defects that the Stage-2 comparison identified.
Run:  py -3 q7_tests.py
"""
import math
import os
import random
import sys

from q7_max_subarray import Counter, brute_force_max_subarray, dc_crossing, dc_joint, hourly_profits, kadane

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Student_A_Initial_Design"))
sys.path.insert(0, os.path.join(HERE, "..", "Student_B_Initial_Design"))
from proposal_a_midpoint_split import proposal_a  # noqa: E402
from proposal_b_four_tuple import proposal_b  # noqa: E402

RESULTS = []


def check(name, condition):
    RESULTS.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


def valid(p, r):
    """The reported hours i..j really have the reported sum."""
    best, i, j = r
    return 0 <= i <= j < len(p) and sum(p[i:j + 1]) == best


def main():
    print("Q7 TESTS - Maximum Subarray Sum: joint D&C design, crossing-scan variant, brute-force baseline")
    print("-" * 100)
    demo = [-120, 340, -60, 410, -380, 150, 220, -90]
    check("demo hours: all three methods find Rs 690 on hours 1..3",
          brute_force_max_subarray(demo) == dc_crossing(demo) == dc_joint(demo) == (690, 1, 3))
    check("single hour: n = 1 returns that hour (positive and negative)",
          dc_joint([250]) == (250, 0, 0) and dc_joint([-80]) == (-80, 0, 0))
    storm = [-40, -15, -90, -25]
    check("all-loss day: best run is the least-bad single hour (-15 at hour 1), never an empty run",
          dc_joint(storm) == (-15, 1, 1) and dc_crossing(storm)[0] == -15)
    check("all-profit day: best run is the whole day", dc_joint([5, 1, 7, 3]) == (16, 0, 3))
    check("zeros: best sum 0 with a valid run", dc_joint([0, 0, 0])[0] == 0 and valid([0, 0, 0], dc_joint([0, 0, 0])))
    check("best run crossing the top-level split (hours 3..4 of 8)",
          dc_joint([-5, -5, -5, 9, 9, -5, -5, -5]) == (18, 3, 4))
    check("best run at the very start and at the very end",
          dc_joint([9, 9, -50, 1, 2])[1:] == (0, 1) and dc_joint([1, -50, 2, 8, 9])[1:] == (2, 4))
    check("empty input is rejected with ValueError", raises_value_error())
    rng = random.Random(42)
    ok_b = ok_x = ok_valid = ok_k = True
    for _ in range(2000):
        n = rng.randint(1, 60)
        p = [rng.randint(-50, 50) for _ in range(n)]
        bf = brute_force_max_subarray(p)
        j, x = dc_joint(p), dc_crossing(p)
        ok_b &= j[0] == bf[0]
        ok_x &= x[0] == bf[0]
        ok_valid &= valid(p, j) and valid(p, x)
        ok_k &= kadane(p) == bf[0]
    check("2,000 random instances (n = 1..60, many ties): joint D&C sum = brute force", ok_b)
    check("2,000 random instances: crossing-scan D&C sum = brute force", ok_x)
    check("2,000 random instances: reported hours i..j really add up to the reported best", ok_valid)
    check("2,000 random instances: independent Kadane reference agrees with brute force", ok_k)
    big = hourly_profits(20000)
    check("n = 20,000 hourly data: joint = crossing = Kadane and the run is valid",
          dc_joint(big)[0] == dc_crossing(big)[0] == kadane(big) and valid(big, dc_joint(big)))
    ok = True
    for n in list(range(1, 130)) + [1000, 4097]:
        c = Counter()
        dc_joint(hourly_profits(n), c)
        ok &= c.additions == 4 * (n - 1) and c.comparisons == 4 * (n - 1) and c.calls == 2 * n - 1
        ok &= c.max_depth == (math.ceil(math.log2(n)) if n > 1 else 0)
    check("joint design: exactly 4(n-1) additions, 4(n-1) comparisons, 2n-1 calls, depth ceil(log2 n) (131 sizes)", ok)
    ok = True
    for k in range(0, 13):
        n = 2 ** k
        c = Counter()
        dc_crossing(hourly_profits(n), c)
        ok &= c.comparisons == n * k and c.additions == n * k + n - 1
    check("crossing variant: exactly n log2 n comparisons and n log2 n + n - 1 additions (n = 2^k, k = 0..12)", ok)
    ok = True
    for n in (1, 2, 7, 50, 300):
        c = Counter()
        brute_force_max_subarray(hourly_profits(n), c)
        ok &= c.additions == c.comparisons == n * (n + 1) // 2
    check("brute force: exactly n(n+1)/2 additions and n(n+1)/2 comparisons (n = 1, 2, 7, 50, 300)", ok)
    check("counts are data-independent: same joint/crossing counts for random, sorted and all-loss data (n = 777)",
          len({count_pair(p) for p in (hourly_profits(777), sorted(hourly_profits(777)), [-1] * 777)}) == 1)
    print("-" * 100)
    check("Stage 2 evidence: Student A's proposal misses the crossing run on the demo (410 instead of 690)",
          proposal_a(demo)[0] == 410)
    check("Stage 2 evidence: Student B's proposal returns 0 (empty run) on the all-loss day instead of -15",
          proposal_b(storm)[3] == 0)
    check("Stage 2 evidence: Student B's O(1) combine gives the right sum whenever some hour is profitable",
          all(proposal_b(p)[3] == brute_force_max_subarray(p)[0]
              for p in ([rng.randint(-50, 50) for _ in range(rng.randint(1, 40))] for _ in range(500))
              if max(p) > 0))
    print("-" * 100)
    print(f"RESULT: {sum(RESULTS)}/{len(RESULTS)} tests passed")


def raises_value_error():
    try:
        dc_joint([])
    except ValueError:
        return True
    return False


def count_pair(p):
    cj, cx = Counter(), Counter()
    dc_joint(p, cj)
    dc_crossing(p, cx)
    return cj.additions, cj.comparisons, cx.additions, cx.comparisons


if __name__ == "__main__":
    main()
