# Exercise 26 - Closest pair (brute force) and brute-force Convex Hull
from itertools import combinations
from math import dist, sqrt

P = [(10, 0), (11, 5), (5, 3), (9, 3.5), (15, 3), (12.5, 7), (6, 6.5), (7.5, 4.5)]
NAME = {p: f"P{i + 1}" for i, p in enumerate(P)}


def euclidean(p, q):
    return sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def closest_pair(points):
    """Brute force: try all n(n-1)/2 pairs and keep the nearest."""
    return min(((p, q, euclidean(p, q)) for p, q in combinations(points, 2)), key=lambda t: t[2])


def cross(a, b, c):                      # > 0 if c is to the left of the directed line a -> b
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def inside_segment(a, b, p):             # p is on line ab: does it lie between a and b?
    return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])


def hull_edges(pts, handle_collinear=True):
    """Directed edge a -> b is on the hull if every other point is on its left.
    Collinear points (cross = 0) are tolerated only if they lie inside segment ab."""
    edges = {}
    for a in pts:
        for b in pts:
            if a != b and all(
                cross(a, b, c) > 0 or (handle_collinear and cross(a, b, c) == 0 and inside_segment(a, b, c))
                for c in pts if c not in (a, b)
            ):
                edges[a] = b
    return edges


def convex_hull(pts):
    """Hull vertices in counter-clockwise order, starting from the lowest point."""
    edges = hull_edges(pts)
    hull = [min(edges, key=lambda p: (p[1], p[0]))]
    while edges[hull[-1]] != hull[0]:
        hull.append(edges[hull[-1]])
    return hull


if __name__ == "__main__":
    print("Part A - closest pair, brute force (points P1..P8)")
    p, q, d = closest_pair(P)
    reference = min(dist(a, b) for a, b in combinations(P, 2))
    print(f"Output  : {NAME[p]} {p} - {NAME[q]} {q}, distance = {d}")
    print(f"Verified: equals min(math.dist over all pairs) -> {abs(d - reference) < 1e-12}")
    print("Time complexity: O(n^2) - n(n-1)/2 distance computations, O(1) extra space")
    print()
    print("Part B - brute-force convex hull (O(n^3): n^2 candidate edges x n side tests)")
    hull = convex_hull(P)
    print(f"Points  : {', '.join(f'{NAME[x]}{x}' for x in P)}")
    print(f"Output  : {', '.join(NAME[x] for x in hull)}   (counter-clockwise from the lowest point)")
    print(f"Interior: {', '.join(NAME[x] for x in P if x not in hull)}")
    # P4 (9, 3.5) lies strictly inside the polygon P1-P5-P6-P7-P3, so it cannot be a hull vertex.
    print("Note    : document lists P3, P4, P6, P5, P7, P1; correct hull is P1, P5, P6, P7, P3 (P4 is interior)")
    print()
    print("Part C - several points on the same line")
    S = [(0, 0), (2, 0), (4, 0), (4, 4), (0, 4), (2, 2)]
    plain, fixed = hull_edges(S, False), hull_edges(S, True)
    print(f"Points  : {S}   ((2, 0) lies on the bottom edge)")
    print(f"Without the fix: {len(plain)} of 4 hull edges found - the bottom edge is lost (cross = 0)")
    print(f"With the fix   : {len(fixed)} of 4 hull edges, hull = {convex_hull(S)}")
    print("Modification: a cross product of 0 is not a failure. Accept the pair (a, b) if all the")
    print("collinear points lie inside segment ab (a, b are then the extreme points); the middle")
    print("collinear points are boundary points but not vertices. Pairs that leave a collinear point")
    print("outside the segment are rejected, so the same edge is never reported twice.")
