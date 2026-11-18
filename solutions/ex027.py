# Exercise 27 - Convex hull of 2D points (brute force)
from itertools import permutations


def cross(o, a, b):
    """> 0 if b is left of the directed line o->a, < 0 if right, 0 if collinear."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def between(p, q, r):
    """True if r (already collinear with p, q) lies on the segment pq."""
    return (min(p[0], q[0]) <= r[0] <= max(p[0], q[0])
            and min(p[1], q[1]) <= r[1] <= max(p[1], q[1]))


def convex_hull_brute_force(points):
    """Directed segment p->q is a hull edge iff every other point lies on its left
    (or on the segment itself).  Chain the edges to get counter-clockwise order."""
    pts = sorted(set(points))
    next_vertex = {}
    for p, q in permutations(pts, 2):                     # O(n^2) candidate edges
        edge_ok = True
        for r in pts:                                     # O(n) check per edge
            if r in (p, q):
                continue
            c = cross(p, q, r)
            if c < 0 or (c == 0 and not between(p, q, r)):
                edge_ok = False
                break
        if edge_ok:
            next_vertex[p] = q
    start = pts[0]                    # leftmost-lowest point is always a hull vertex
    hull, cur = [start], next_vertex[start]
    while cur != start:
        hull.append(cur)
        cur = next_vertex[cur]
    return hull


if __name__ == "__main__":
    tests = [
        [(1, 1), (4, 6), (8, 1), (0, 0), (3, 3)],
        [(0, 0), (2, 0), (4, 0), (4, 4), (0, 4), (2, 2)],   # extra: collinear + interior
    ]
    doc_expected = [(0, 0), (1, 1), (8, 1), (4, 6)]
    for n, pts in enumerate(tests, 1):
        hull = convex_hull_brute_force(pts)
        print(f"Test Case {n}" + ("" if n == 1 else "  (extra test)"))
        print(f"Input   : Points = {pts}")
        print(f"Output  : Convex Hull (counter-clockwise) = {hull}")
        if n == 1:
            if hull == doc_expected:
                print(f"Expected: {doc_expected}")
            else:
                # (1,1) lies strictly inside triangle (0,0),(8,1),(4,6), so it is not a hull vertex.
                print(f"Note    : document lists {doc_expected}; correct value is {hull}")
                print("          ((1,1) lies strictly inside the triangle, so it is not a hull vertex)")
        print()
    print("Time complexity : O(n^3) - n(n-1) candidate edges, each checked against n-2 points")
    print("Space complexity: O(n)")
