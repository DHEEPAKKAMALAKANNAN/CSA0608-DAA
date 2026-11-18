"""Q4 - Brute-force closest pair for drone collision-risk monitoring.

Problem
    Drones report positions D_i = (x_i, y_i) in metres inside a 10 km x 10 km monitoring area.  The system must
    identify the two drones that are closest to one another.

Design
    Every unordered pair {D_i, D_j} is a candidate.  Duplicates are avoided by examining only i < j (the inner
    loop starts at j = i + 1), so exactly n(n-1)/2 pairs are examined.  Squared distances are compared (same
    order as true distances), so only one square root is taken, at the end.
    Counters: pairs examined, distance calculations, best-so-far improvements.

This module also provides make_drones(n, layout) - the seeded position generator reused by Q7.
Run it for the correctness tests and a 6-drone demonstration that lists all 15 candidate pairs.
"""

import itertools
import math
import random

AREA_M = 10_000.0            # side of the square monitoring area (m)


def closest_pair_brute_force(points):
    """Return ((i, j), distance, counters) for the closest two points of `points` (list of (x, y)), n >= 2."""
    n = len(points)
    if n < 2:
        raise ValueError("at least two drones are needed")
    best_d2 = math.inf
    best_pair = None
    pairs_examined = distance_calcs = improvements = 0
    for i in range(n - 1):
        xi, yi = points[i]
        for j in range(i + 1, n):                       # j > i: every unordered pair exactly once
            pairs_examined += 1
            xj, yj = points[j]
            dx = xi - xj
            dy = yi - yj
            d2 = dx * dx + dy * dy                       # squared Euclidean distance
            distance_calcs += 1
            if d2 < best_d2:
                best_d2 = d2
                best_pair = (i, j)
                improvements += 1
    counters = {"pairs_examined": pairs_examined, "distance_calcs": distance_calcs, "improvements": improvements}
    return best_pair, math.sqrt(best_d2), counters


def make_drones(n, layout="uniform", seed=None):
    """Seeded drone positions (metres, 0.01 m resolution).

    uniform   : spread evenly over the 10 km x 10 km area;
    clustered : five delivery hubs, drones normally distributed around them (sd 150 m);
    corridor  : a north-south air corridor 20 m wide (x almost constant, y spread over 10 km);
    cross     : two perpendicular straight routes, half the drones on each (exact x / y) - used in Q7."""
    rng = random.Random(1000 + n if seed is None else seed)
    pts = []
    if layout == "uniform":
        pts = [(rng.uniform(0, AREA_M), rng.uniform(0, AREA_M)) for _ in range(n)]
    elif layout == "clustered":
        hubs = [(rng.uniform(1000, 9000), rng.uniform(1000, 9000)) for _ in range(5)]
        for _ in range(n):
            hx, hy = rng.choice(hubs)
            pts.append((min(max(rng.gauss(hx, 150), 0), AREA_M), min(max(rng.gauss(hy, 150), 0), AREA_M)))
    elif layout == "corridor":
        pts = [(5000 + rng.uniform(-10, 10), rng.uniform(0, AREA_M)) for _ in range(n)]
    elif layout == "cross":                    # drones locked to two straight routes (exactly x = 5000 / y = 5000)
        cm = [k for k in rng.sample(range(1_000_001), n + 1) if k != 500_000][:n]   # distinct cm positions
        for k, pos in enumerate(cm):
            pts.append((5000.0, pos / 100) if k % 2 == 0 else (pos / 100, 5000.0))
    else:
        raise ValueError(layout)
    return [(round(x, 2), round(y, 2)) for x, y in pts]


def reference_closest_distance(points):
    """Independent reference: math.dist over itertools.combinations (no shared code with the algorithm)."""
    return min(math.dist(p, q) for p, q in itertools.combinations(points, 2))


# ------------------------------------------------------------------------------------------------- tests
def run_tests():
    cases = [
        ("two drones (3-4-5 triangle)", [(0, 0), (3, 4)], (0, 1), 5.0),
        ("three drones, hand-checked", [(0, 0), (10, 0), (0, 2)], (0, 2), 2.0),
        ("duplicate positions -> 0 m", [(5, 5), (100, 100), (5, 5)], (0, 2), 0.0),
        ("vertical line (same x)", [(5, 0), (5, 7), (5, 3), (5, 12)], (0, 2), 3.0),
        ("negative coordinates", [(-4, -4), (6, 6), (-1, 0), (12, 15)], (0, 2), 5.0),
    ]
    print("CORRECTNESS TESTS  (hand-checked answers; random cases vs an independent math.dist reference)")
    passed = 0
    for name, pts, exp_pair, exp_d in cases:
        pair, d, c = closest_pair_brute_force(pts)
        ok = pair == exp_pair and abs(d - exp_d) < 1e-12 and c["pairs_examined"] == len(pts) * (len(pts) - 1) // 2
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  Q4 {name:<29} pair {pair} d = {d:.1f} m (expected {exp_pair},"
              f" {exp_d:.1f} m), {c['pairs_examined']} pairs")
    rng = random.Random(9)
    ok_rand = ok_count = True
    for _ in range(150):
        n = rng.randint(2, 40)
        pts = [(rng.uniform(-50, 50), rng.uniform(-50, 50)) for _ in range(n)]
        _, d, c = closest_pair_brute_force(pts)
        ok_rand &= abs(d - reference_closest_distance(pts)) < 1e-9
        ok_count &= c["pairs_examined"] == c["distance_calcs"] == n * (n - 1) // 2
    passed += ok_rand + ok_count
    print(f"{'PASS' if ok_rand else 'FAIL'}  Q4 150 random fleets (n = 2..40): distance equals the reference")
    print(f"{'PASS' if ok_count else 'FAIL'}  Q4 150 random fleets: pairs examined = distance calcs = n(n-1)/2")
    try:
        closest_pair_brute_force([(1, 1)])
        ok_err = False
    except ValueError:
        ok_err = True
    passed += ok_err
    print(f"{'PASS' if ok_err else 'FAIL'}  Q4 a single drone is rejected with ValueError")
    total = len(cases) + 3
    print(f"RESULT: {passed}/{total} tests passed")
    return passed == total


def demo():
    """Six drones: list every candidate pair (i < j) to show that each pair is examined exactly once."""
    drones = [(1200.0, 3400.0), (8050.5, 920.0), (1215.0, 3390.0), (4500.0, 7000.0), (8000.0, 1000.0),
              (4420.0, 7090.0)]
    print("\nDEMO - 6 drones, every unordered pair examined once (i < j):  6*5/2 = 15 pairs")
    for k, (x, y) in enumerate(drones, start=1):
        print(f"   D{k}: ({x:7.1f}, {y:7.1f}) m", end="" if k % 3 else "\n")
    pairs = [(i, j, math.dist(drones[i], drones[j])) for i in range(6) for j in range(i + 1, 6)]
    for row in range(5):
        print("   " + "   ".join(f"D{i + 1}-D{j + 1}: {d:9.1f} m" for i, j, d in pairs[row * 3:row * 3 + 3]))
    (i, j), d, c = closest_pair_brute_force(drones)
    print(f"Closest pair: D{i + 1} and D{j + 1} at {d:.1f} m  -> collision-risk alert"
          f"   [pairs examined {c['pairs_examined']}, distance calcs {c['distance_calcs']},"
          f" best-so-far updates {c['improvements']}]")


def main():
    ok = run_tests()
    demo()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
