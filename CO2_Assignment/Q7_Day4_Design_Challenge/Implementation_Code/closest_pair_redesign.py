"""Q7 - Redesigned closest pair for drone collision-risk monitoring ("sort once, sweep, stop early").

Diagnosis (from Q4): the brute force computes all n(n-1)/2 distances although almost every pair is already ruled
out by its coordinate gap alone, and it never uses the best distance found so far to skip work.

Redesign
    1. choose the sweep axis with the larger spread (max - min) - exploits the geometry of the data;
    2. sort the drones once along that axis (hand-written merge sort, key comparisons counted);
    3. sweep: compare each drone only with the drones after it in sorted order, and STOP (break) as soon as the
       gap along the sweep axis satisfies gap^2 >= best^2 - every later drone is even farther away;
    4. skip the full distance when the gap on the other axis alone already satisfies gap^2 >= best^2.
    Counters: sort comparisons, candidate pairs examined (gap checks), distance calculations, improvements.

Run this file for the tests (redesign vs the ORIGINAL Q4 brute force on many fleets) and a small demo.
"""

import math
import os
import random
import sys

Q4_CODE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Q4_Brute_Force_Closest_Pair",
                       "Implementation_Code")
sys.path.insert(0, os.path.abspath(Q4_CODE))
from closest_pair_bruteforce import closest_pair_brute_force, make_drones  # noqa: E402  (the original, unchanged)


def merge_sort_indices(keys):
    """Return (indices sorted by keys[index], number of key comparisons).  Stable, Theta(n log n)."""
    comparisons = 0

    def sort(idx):
        nonlocal comparisons
        if len(idx) <= 1:
            return idx
        mid = len(idx) // 2
        left, right = sort(idx[:mid]), sort(idx[mid:])
        merged, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            comparisons += 1
            if keys[left[i]] <= keys[right[j]]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged

    return sort(list(range(len(keys)))), comparisons


def closest_pair_sweep(points, axis="auto"):
    """Return ((i, j), distance, counters) - same answer as the brute force, far fewer distance calculations.

    axis = "auto" (sweep along the coordinate with the larger spread), "x" or "y" (forced; used in ablation)."""
    n = len(points)
    if n < 2:
        raise ValueError("at least two drones are needed")
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    if axis == "auto":
        axis = "x" if max(xs) - min(xs) >= max(ys) - min(ys) else "y"
    a, b = (xs, ys) if axis == "x" else (ys, xs)
    order, sort_comparisons = merge_sort_indices(a)          # preprocessing: Theta(n log n)
    best_d2 = math.inf
    best_pair = None
    candidates = distance_calcs = improvements = 0
    for p in range(n - 1):
        i = order[p]
        ai, bi = a[i], b[i]
        for q in range(p + 1, n):
            j = order[q]
            candidates += 1                                   # one gap check
            ga = a[j] - ai                                    # >= 0 because of the sort
            ga2 = ga * ga
            if ga2 >= best_d2:
                break                                         # all later drones are even farther: stop
            gb = b[j] - bi
            gb2 = gb * gb
            if gb2 >= best_d2:
                continue                                      # other-axis gap alone too large
            d2 = ga2 + gb2
            distance_calcs += 1
            if d2 < best_d2:
                best_d2 = d2
                best_pair = (min(i, j), max(i, j))
                improvements += 1
    counters = {"axis": axis, "sort_comparisons": sort_comparisons, "candidates": candidates,
                "distance_calcs": distance_calcs, "improvements": improvements,
                "pairs_never_examined": n * (n - 1) // 2 - candidates}
    return best_pair, math.sqrt(best_d2), counters


# ------------------------------------------------------------------------------------------------- tests
def run_tests():
    print("CORRECTNESS TESTS  (expected = original Q4 brute force on the same fleet; identical distance required)")
    passed = total = 0

    def check(name, ok, detail):
        nonlocal passed, total
        total += 1
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  Q7 {name:<41} {detail}")

    hand = [("two drones", [(0, 0), (3, 4)]), ("duplicate positions", [(5, 5), (100, 100), (5, 5)]),
            ("vertical line (same x)", [(5, 0), (5, 7), (5, 3), (5, 12)]),
            ("negative coordinates", [(-4, -4), (6, 6), (-1, 0), (12, 15)]),
            ("all drones identical", [(7, 7)] * 6)]
    for name, pts in hand:
        _, d0, _ = closest_pair_brute_force(pts)
        _, d1, c = closest_pair_sweep(pts)
        check(name, d0 == d1, f"expected {d0:.3f} m, actual {d1:.3f} m (axis {c['axis']})")
    rng = random.Random(77)
    for layout in ("uniform", "clustered", "corridor", "cross"):
        ok = True
        for trial in range(60):
            pts = make_drones(rng.randint(2, 300), layout, seed=trial * 31 + len(layout))
            ok &= closest_pair_brute_force(pts)[1] == closest_pair_sweep(pts)[1]
        check(f"60 random {layout} fleets (n = 2..300)", ok, "distance identical to brute force")
    grid_ok = True
    for trial in range(60):                      # integer grid: many ties, duplicates, shared x and y values
        pts = [(rng.randint(0, 6), rng.randint(0, 6)) for _ in range(rng.randint(2, 40))]
        for ax in ("auto", "x", "y"):
            grid_ok &= closest_pair_brute_force(pts)[1] == closest_pair_sweep(pts, ax)[1]
    check("60 tie-heavy grid fleets, all 3 axes", grid_ok, "distance identical to brute force")
    keys = [rng.random() for _ in range(1000)]
    order, comps = merge_sort_indices(keys)
    check("merge sort of 1,000 keys", [keys[i] for i in order] == sorted(keys) and comps <= 1000 * 10,
          f"sorted; {comps:,} comparisons <= n log2 n = {int(1000 * math.log2(1000)):,}")
    print(f"RESULT: {passed}/{total} tests passed")
    return passed == total


def demo():
    """Show how the sweep stops early on 12 drones (compare with 66 pairs for brute force)."""
    pts = make_drones(12, "uniform", seed=2026)
    (i, j), d, c = closest_pair_sweep(pts)
    (bi, bj), bd, bc = closest_pair_brute_force(pts)
    print(f"\nDEMO - 12 drones: brute force examined {bc['pairs_examined']} pairs ({bc['distance_calcs']} distance calcs);"
          f" sweep (axis {c['axis']}) sorted with {c['sort_comparisons']} comparisons,")
    print(f"       examined {c['candidates']} candidate pairs, computed {c['distance_calcs']} distances,"
          f" never examined {c['pairs_never_examined']} pairs.")
    print(f"       closest pair: brute force D{bi + 1}-D{bj + 1} {bd:.2f} m | sweep D{i + 1}-D{j + 1} {d:.2f} m"
          f" -> {'identical' if (bi, bj, bd) == (i, j, d) else 'DIFFERENT'}")


def main():
    ok = run_tests()
    demo()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
