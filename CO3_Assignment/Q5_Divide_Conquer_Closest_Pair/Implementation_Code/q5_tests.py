"""Q5 - Correctness tests for the closest-pair algorithms (CSA06 DAA, Assignment 3 - CO3).

Each test prints PASS/FAIL; the last line is "RESULT: k/k tests passed".
Reference: the brute-force algorithm (all pairs) and hand-computed answers; math.hypot for the reported pair.
Run:  py -3 q5_tests.py
"""
import math
import random

from q5_closest_pair import closest_pair_brute_force, closest_pair_dc, merge_sort_by, Counters, DEMO_FLEET
from q5_experiments import uniform_fleet, clustered_fleet, line_fleet, duplicate_fleet

results = []


def check(name, condition):
    """Record and print one test result."""
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


def pair_distance(pair):
    """Euclidean distance of a reported pair (independent check of the returned distance)."""
    (x1, y1), (x2, y2) = pair
    return math.hypot(x1 - x2, y1 - y2)


def main():
    print("Q5 closest pair - correctness tests")
    print("-" * 90)
    # 1. hand-made fleet
    pts = [p for _, p in DEMO_FLEET]
    d_bf, pair_bf, _ = closest_pair_brute_force(pts)
    d_dc, pair_dc, _ = closest_pair_dc(pts)
    check("demo fleet: brute force finds D04-D07 at 50.0 m", abs(d_bf - 50.0) < 1e-9 and
          set(pair_bf) == {(4100.0, 4100.0), (4130.0, 4140.0)})
    check("demo fleet: D&C finds the same pair at 50.0 m", abs(d_dc - 50.0) < 1e-9 and set(pair_dc) == set(pair_bf))
    # 2. smallest inputs
    d, pair, _ = closest_pair_dc([(0.0, 0.0), (3.0, 4.0)])
    check("n = 2: distance 5 (3-4-5 triangle)", abs(d - 5.0) < 1e-12)
    d, pair, _ = closest_pair_dc([(0.0, 0.0), (10.0, 0.0), (10.0, 1.0)])
    check("n = 3: distance 1", abs(d - 1.0) < 1e-12)
    # 3. degenerate positions
    d, pair, _ = closest_pair_dc([(5.0, 5.0)] * 6)
    check("six drones at the same position: distance 0", d == 0.0)
    d_dup, _, _ = closest_pair_dc(duplicate_fleet(3000))
    check("duplicate fleet (n = 3,000): distance 0", d_dup == 0.0)
    pts = [(float(i * 7), 100.0) for i in range(500)]
    check("500 drones on a horizontal line spaced 7 m: distance 7", abs(closest_pair_dc(pts)[0] - 7.0) < 1e-12)
    pts = line_fleet(2000)
    check("line fleet (identical x, n = 2,000): D&C = brute force",
          closest_pair_dc(pts)[0] == closest_pair_brute_force(pts)[0])
    # 4. the cross-pair case: closest pair straddles the dividing line
    pts = [(float(x), float(y)) for x in range(0, 100, 10) for y in range(0, 100, 10)]
    pts.append((44.9, 50.0))
    pts.append((45.1, 50.0))
    d, pair, _ = closest_pair_dc(pts)
    check("closest pair straddles the dividing line (0.2 m apart)", abs(d - 0.2) < 1e-9)
    # 5. random tests against brute force
    rng = random.Random(42)
    ok, worst_nb = True, 0
    for trial in range(300):
        n = rng.randint(2, 60)
        pts = [(rng.randint(0, 50) * 1.0, rng.randint(0, 50) * 1.0) for _ in range(n)]   # many ties/duplicates
        db = closest_pair_brute_force(pts)[0]
        dd, pr, c = closest_pair_dc(pts)
        ok &= (db == dd) and abs(pair_distance(pr) - dd) < 1e-9
        worst_nb = max(worst_nb, c.max_neighbours)
    check("300 random small fleets on an integer grid (ties, duplicates): D&C = brute force", ok)
    ok = True
    for trial in range(20):
        pts = uniform_fleet(rng.randint(500, 1500), seed=trial)
        dd, pr, c = closest_pair_dc(pts)
        ok &= dd == closest_pair_brute_force(pts)[0] and abs(pair_distance(pr) - dd) < 1e-9
        worst_nb = max(worst_nb, c.max_neighbours)
    check("20 random uniform fleets (500-1,500 drones): D&C = brute force", ok)
    pts = clustered_fleet(4000)
    dd, pr, c = closest_pair_dc(pts)
    check("clustered fleet (n = 4,000): D&C = brute force", dd == closest_pair_brute_force(pts)[0])
    worst_nb = max(worst_nb, c.max_neighbours)
    check(f"every strip point examined at most 7 neighbours in all tests (max seen = {worst_nb})", worst_nb <= 7)
    # 6. operation counts
    for n in (10, 100, 1000):
        _, _, cb = closest_pair_brute_force(uniform_fleet(n))
        check(f"brute force makes exactly n(n-1)/2 = {n * (n - 1) // 2:,} distance computations (n = {n:,})",
              cb.distances == n * (n - 1) // 2)
    _, _, c = closest_pair_dc(uniform_fleet(1024))
    check(f"D&C recursion depth for n = 1,024 is log2(n) - 1 = 9 (got {c.max_depth})", c.max_depth == 9)
    c2 = Counters()
    srt = merge_sort_by(uniform_fleet(1000), 0, c2)
    check("presort by x returns the points in x order (= sorted())", srt == sorted(uniform_fleet(1000)))
    _, _, c = closest_pair_dc(uniform_fleet(20000))
    check(f"D&C at n = 20,000 makes far fewer distance computations than n log2 n ({c.distances:,} < "
          f"{round(20000 * math.log2(20000)):,})", c.distances < 20000 * math.log2(20000))
    print("-" * 90)
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
