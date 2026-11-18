"""Q5 - Divide-and-Conquer Closest Pair (CSA06 DAA, Assignment 3 - CO3).

Problem (airspace deconfliction): the operations centre receives the position (x, y) in metres of every airborne
drone once per second and must find the two drones that are closest to one another.

Two algorithms are implemented, both with explicit operation counters:

* closest_pair_brute_force(points) - examines every one of the n(n-1)/2 pairs (baseline and reference).
* closest_pair_dc(points)          - Divide-and-Conquer:
      presort  : the drones are sorted ONCE by x (hand-written merge sort, comparisons counted);
      divide   : split the x-sorted list at its middle -> vertical dividing line x = mid_x;
      conquer  : solve the left and the right half recursively (each call also returns its points sorted by y);
      combine  : merge the two y-sorted halves (Theta(n)) and examine only the strip |x - mid_x| < delta,
                 comparing each strip point with the following strip points while dy < delta (at most 7 of them).
  Recurrence: T(n) = 2T(n/2) + Theta(n)  ->  Theta(n log n).

Run:  py -3 q5_closest_pair.py      (small hand-checkable demo; experiments are in q5_experiments.py)
"""
import math


class Counters:
    """Operation counters of one closest-pair run."""

    def __init__(self):
        self.distances = 0            # distance computations (primary measure)
        self.sort_comparisons = 0     # x-comparisons of the one-off presort
        self.merge_comparisons = 0    # y-comparisons while merging halves (and sorting base cases by y)
        self.strip_points = 0         # total number of points placed in strips over all calls
        self.max_neighbours = 0       # most neighbours examined by any single strip point (theory: <= 7)
        self.neighbour_hist = [0] * 9  # how many strip points examined 0,1,...,7 neighbours; index 8 = more than 7
        self.calls = 0                # recursive calls
        self.max_depth = 0            # deepest recursion level reached


# ----------------------------------------------------------------------------------------------- brute force
def closest_pair_brute_force(points, counters=None):
    """Return (distance, (p, q), counters) by examining all n(n-1)/2 pairs of points.

    Squared distances are compared (same order as the true distance); the square root is taken once at the end.
    """
    if counters is None:
        counters = Counters()
    n = len(points)
    best2, pair = math.inf, None
    for i in range(n - 1):
        xi, yi = points[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            dx, dy = xi - xj, yi - yj
            d2 = dx * dx + dy * dy
            if d2 < best2:
                best2, pair = d2, (points[i], points[j])
        counters.distances += n - 1 - i      # the inner loop made exactly n-1-i distance computations
    return math.sqrt(best2), pair, counters


# ----------------------------------------------------------------------------------------------- helpers
def merge_sort_by(points, axis, counters):
    """Stable top-down merge sort of a list of (x, y) points by coordinate `axis` (0 = x, 1 = y).

    Every key comparison is counted in counters.sort_comparisons (used for the one-off presort by x).
    """
    if len(points) <= 1:
        return list(points)
    mid = len(points) // 2
    left = merge_sort_by(points[:mid], axis, counters)
    right = merge_sort_by(points[mid:], axis, counters)
    out, i, j, comps = [], 0, 0, 0
    while i < len(left) and j < len(right):
        comps += 1
        if left[i][axis] <= right[j][axis]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    counters.sort_comparisons += comps
    return out


def merge_by_y(left_y, right_y, counters):
    """Merge two lists that are sorted by y into one y-sorted list (the Theta(n) part of the combine step)."""
    out, i, j, comps = [], 0, 0, 0
    nl, nr = len(left_y), len(right_y)
    while i < nl and j < nr:
        comps += 1
        if left_y[i][1] <= right_y[j][1]:
            out.append(left_y[i])
            i += 1
        else:
            out.append(right_y[j])
            j += 1
    out.extend(left_y[i:])
    out.extend(right_y[j:])
    counters.merge_comparisons += comps
    return out


# ----------------------------------------------------------------------------------------------- divide and conquer
def closest_pair_dc(points, counters=None):
    """Return (distance, (p, q), counters) using the Divide-and-Conquer algorithm (n >= 2 points)."""
    if counters is None:
        counters = Counters()
    if len(points) < 2:
        raise ValueError("at least two drones are needed")
    px = merge_sort_by(points, 0, counters)          # presort by x once: Theta(n log n)
    best2, pair, _ = _closest_rec(px, counters, 0)
    return math.sqrt(best2), pair, counters


def _closest_rec(px, c, depth):
    """Closest pair of the x-sorted list px. Returns (best squared distance, pair, px's points sorted by y)."""
    c.calls += 1
    if depth > c.max_depth:
        c.max_depth = depth
    n = len(px)
    if n <= 3:                                       # base case: brute force on 2 or 3 drones
        best2, pair = math.inf, None
        for i in range(n - 1):
            for j in range(i + 1, n):
                c.distances += 1
                dx, dy = px[i][0] - px[j][0], px[i][1] - px[j][1]
                d2 = dx * dx + dy * dy
                if d2 < best2:
                    best2, pair = d2, (px[i], px[j])
        py = list(px)                                # insertion sort by y (at most 3 comparisons)
        for i in range(1, n):
            key, k = py[i], i - 1
            while k >= 0:
                c.merge_comparisons += 1
                if py[k][1] > key[1]:
                    py[k + 1] = py[k]
                    k -= 1
                else:
                    break
            py[k + 1] = key
        return best2, pair, py

    # DIVIDE: vertical line through the middle drone
    mid = n // 2
    mid_x = px[mid][0]
    # CONQUER: the two halves
    best_l, pair_l, left_y = _closest_rec(px[:mid], c, depth + 1)
    best_r, pair_r, right_y = _closest_rec(px[mid:], c, depth + 1)
    best2, pair = (best_l, pair_l) if best_l <= best_r else (best_r, pair_r)

    # COMBINE (1): merge the y-sorted halves -> this call returns its points sorted by y
    py = merge_by_y(left_y, right_y, c)
    # COMBINE (2): only drones closer than delta to the dividing line can form a closer cross pair
    delta = math.sqrt(best2)
    strip = [p for p in py if abs(p[0] - mid_x) < delta]
    c.strip_points += len(strip)
    m = len(strip)
    for i in range(m):
        xi, yi = strip[i]
        examined = 0
        j = i + 1
        while j < m and strip[j][1] - yi < delta:    # at most 7 strip points can satisfy this (packing bound)
            examined += 1
            c.distances += 1
            dx, dy = xi - strip[j][0], yi - strip[j][1]
            d2 = dx * dx + dy * dy
            if d2 < best2:
                best2, pair = d2, (strip[i], strip[j])
                delta = math.sqrt(best2)
            j += 1
        c.neighbour_hist[min(examined, 8)] += 1
        if examined > c.max_neighbours:
            c.max_neighbours = examined
    return best2, pair, py


# ----------------------------------------------------------------------------------------------- demo
DEMO_FLEET = [  # 10 drones, positions in metres (hand-checkable): closest pair is D04-D07 at 50.0 m
    ("D01", (1200.0, 3400.0)), ("D02", (5200.0, 800.0)), ("D03", (2500.0, 2600.0)), ("D04", (4100.0, 4100.0)),
    ("D05", (300.0, 900.0)), ("D06", (6100.0, 3900.0)), ("D07", (4130.0, 4140.0)), ("D08", (3500.0, 300.0)),
    ("D09", (2450.0, 2700.0)), ("D10", (5800.0, 5600.0)),
]


def main():
    print("=" * 96)
    print("Q5  Divide-and-Conquer closest pair  -  demo on a hand-checkable fleet of 10 drones")
    print("=" * 96)
    names = {pos: name for name, pos in DEMO_FLEET}
    pts = [pos for _, pos in DEMO_FLEET]
    for name, (x, y) in DEMO_FLEET:
        print(f"  {name}: x = {x:7.1f} m   y = {y:7.1f} m")
    d_bf, pair_bf, c_bf = closest_pair_brute_force(pts)
    d_dc, pair_dc, c_dc = closest_pair_dc(pts)
    n = len(pts)
    print("-" * 96)
    print(f"{'Method':<22}{'closest pair':<16}{'distance (m)':>14}{'distance comps':>16}{'theory':>18}")
    print(f"{'Brute force':<22}{names[pair_bf[0]] + '-' + names[pair_bf[1]]:<16}{d_bf:>14.2f}"
          f"{c_bf.distances:>16}{'n(n-1)/2 = ' + str(n * (n - 1) // 2):>18}")
    print(f"{'Divide-and-Conquer':<22}{names[pair_dc[0]] + '-' + names[pair_dc[1]]:<16}{d_dc:>14.2f}"
          f"{c_dc.distances:>16}{'<= 7 per strip pt':>18}")
    print("-" * 96)
    print(f"D&C details: recursive calls = {c_dc.calls}, max depth = {c_dc.max_depth}, presort comparisons = "
          f"{c_dc.sort_comparisons}, merge comparisons = {c_dc.merge_comparisons}")
    print(f"             strip points = {c_dc.strip_points}, max neighbours examined by one strip point = "
          f"{c_dc.max_neighbours} (bound 7)")
    print(f"Same answer: {'YES' if abs(d_bf - d_dc) < 1e-9 else 'NO'}   "
          f"(hand check: sqrt(30^2 + 40^2) = {math.hypot(30, 40):.1f} m between D04 and D07)")


if __name__ == "__main__":
    main()
