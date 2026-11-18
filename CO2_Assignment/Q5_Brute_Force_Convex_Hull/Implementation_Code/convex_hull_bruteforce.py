"""Q5 - Brute-force convex hull for wildlife-reserve boundary monitoring.

Problem
    Monitoring stations P_i = (x_i, y_i) (integer metres) are spread over a reserve; determine the outer
    boundary they form.

Decision rule derived from the given principle ("a line joining two candidate points may form part of the
outer boundary if all remaining points lie on an appropriate single side of that line"):
    * orientation(Pi, Pj, Pk) = (xj-xi)(yk-yi) - (yj-yi)(xk-xi): > 0 left of Pi->Pj, < 0 right, = 0 collinear;
    * segment PiPj is a hull edge iff no station is strictly left while another is strictly right AND every
      collinear station lies BETWEEN Pi and Pj (otherwise a longer collinear edge exists);
    * accepted edges are stored directed (all other stations on the left), so following next[] from the
      lowest corner yields the boundary counter-clockwise.
Duplicates are removed first; 0-2 distinct stations or an all-collinear set return the extreme stations.

Run this file for the tests, the two designed configurations (A: boundary + interior, B: collinear +
duplicates) and the plot ../Output_Screenshots/q5_hull_configs.png.
"""

import csv
import math
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")


def orientation(p, q, r):
    """Cross product of (q - p) and (r - p): > 0 r left of p->q, < 0 right, 0 collinear."""
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def between(p, q, r):
    """For r collinear with p and q: True if r lies on the closed segment pq."""
    return min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and min(p[1], q[1]) <= r[1] <= max(p[1], q[1])


def brute_force_hull(points, early_exit=False):
    """Return (hull vertices counter-clockwise from the lowest point, statistics dict).

    early_exit=False : every pair tests all n-2 other stations (the pure principle, exactly C(n,2)(n-2) tests);
    early_exit=True  : a pair is REJECTED as soon as stations on both sides (or a collinear station outside
                       the segment) have been seen; acceptance still needs all n-2 tests."""
    pts = list(dict.fromkeys((int(x), int(y)) for x, y in points))     # remove duplicate stations
    n = len(pts)
    stats = {"input_points": len(points), "duplicates_removed": len(points) - n, "distinct": n,
             "pairs_examined": 0, "orientation_tests": 0, "edges_accepted": 0}
    if n <= 2:
        return sorted(pts, key=lambda p: (p[1], p[0])), stats
    nxt = {}
    collinear_pair = None
    tests = pairs = 0
    for i in range(n - 1):
        xi, yi = pts[i]
        for j in range(i + 1, n):
            pairs += 1
            xj, yj = pts[j]
            dx, dy = xj - xi, yj - yi                    # direction of the candidate line, computed once per pair
            left = right = 0
            outside = False
            for k in range(n):
                if k == i or k == j:
                    continue
                tests += 1
                xk, yk = pts[k]
                o = dx * (yk - yi) - dy * (xk - xi)       # = orientation(Pi, Pj, Pk)
                if o > 0:
                    left += 1
                elif o < 0:
                    right += 1
                elif not between(pts[i], pts[j], pts[k]):
                    outside = True
                if early_exit and (outside or (left and right)):
                    break
            if outside or (left and right):
                continue                                  # not a boundary edge
            stats["edges_accepted"] += 1
            if right == 0 and left > 0:
                nxt[i] = j                                # others on the left of i->j: CCW direction
            elif left == 0 and right > 0:
                nxt[j] = i                                # others on the left of j->i
            else:
                collinear_pair = (i, j)                   # all stations on one line
    stats["pairs_examined"], stats["orientation_tests"] = pairs, tests
    if not nxt:                                           # degenerate: all collinear -> the two extreme stations
        return sorted((pts[collinear_pair[0]], pts[collinear_pair[1]]), key=lambda p: (p[1], p[0])), stats
    start = min(nxt, key=lambda v: (pts[v][1], pts[v][0]))
    hull, v = [start], nxt[start]
    while v != start:
        hull.append(v)
        v = nxt[v]
        if len(hull) > n:
            raise RuntimeError("accepted edges do not form a closed boundary")
    return [pts[v] for v in hull], stats


def naive_edge_count(points):
    """Pairs a NAIVE rule would accept ("no station strictly on both sides", collinear stations ignored) -
    shows why the 'collinear stations must lie between' condition is needed."""
    pts = list(dict.fromkeys(points))
    count = 0
    for i in range(len(pts) - 1):
        for j in range(i + 1, len(pts)):
            sides = [orientation(pts[i], pts[j], pts[k]) for k in range(len(pts)) if k != i and k != j]
            count += not (any(o > 0 for o in sides) and any(o < 0 for o in sides))
    return count


def boundary_non_corners(points, hull):
    """Distinct stations lying on a hull edge but not being corners (collinear boundary stations)."""
    corners = set(hull)
    out = []
    for p in dict.fromkeys(points):
        if p in corners:
            continue
        for a, b in zip(hull, hull[1:] + hull[:1]):
            if orientation(a, b, p) == 0 and between(a, b, p):
                out.append(p)
                break
    return out


def monotone_chain(points):
    """Independent reference (test oracle only): Andrew's monotone chain, collinear points excluded."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and orientation(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and orientation(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def same_cycle(a, b):
    """True if b is a rotation of a (same vertices in the same counter-clockwise order)."""
    if len(a) != len(b):
        return False
    if not a:
        return True
    k = b.index(a[0]) if a[0] in b else -1
    return k >= 0 and b[k:] + b[:k] == a


# ------------------------------------------------------------------------------------- configurations
def config_a():
    """10 perimeter stations (convex position on an ellipse) + 30 interior stations; integer metres."""
    rng = random.Random(42)
    cx, cy, rx, ry = 10_000, 6_000, 9_000, 5_000
    angles = sorted(rng.uniform(0, 2 * math.pi) for _ in range(10))
    boundary = [(round(cx + rx * math.cos(a)), round(cy + ry * math.sin(a))) for a in angles]
    interior = []
    while len(interior) < 30:
        x, y = rng.uniform(-1, 1), rng.uniform(-1, 1)
        if x * x + y * y < 0.55:                                     # well inside the perimeter ellipse
            interior.append((round(cx + rx * x), round(cy + ry * y)))
    return boundary + interior, boundary


def config_b():
    """Challenge: rectangle with collinear stations on every side (two vertical sides), duplicates and
    interior stations collinear with a diagonal."""
    corners = [(0, 0), (8000, 0), (8000, 5000), (0, 5000)]
    sides = ([(x, 0) for x in (2000, 4000, 6000)] + [(x, 5000) for x in (2000, 4000, 6000)]
             + [(0, y) for y in (1250, 2500, 3750)] + [(8000, y) for y in (1250, 2500, 3750)])
    diagonal = [(1600, 1000), (3200, 2000), (4800, 3000), (6400, 4000)]
    interior = [(2500, 3500), (5500, 1500), (7000, 2600)]
    duplicates = [(8000, 5000), (3200, 2000)]                          # a corner and an interior station again
    return corners + sides + diagonal + interior + duplicates, corners


# ------------------------------------------------------------------------------------------------- tests
def run_tests():
    cases = [
        ("single station", [(5, 5)], [(5, 5)]),
        ("two stations", [(0, 0), (3, 1)], [(0, 0), (3, 1)]),
        ("duplicates of two stations", [(0, 0), (3, 1), (0, 0), (3, 1)], [(0, 0), (3, 1)]),
        ("three collinear", [(0, 0), (2, 2), (1, 1)], [(0, 0), (2, 2)]),
        ("ten stations on one line", [(k, 2 * k) for k in range(10)], [(0, 0), (9, 18)]),
        ("triangle + interior point", [(0, 0), (10, 0), (5, 8), (5, 3)], [(0, 0), (10, 0), (5, 8)]),
        ("square: collinear sides+centre", [(0, 0), (4, 0), (4, 4), (0, 4), (2, 0), (4, 2), (2, 4), (0, 2), (2, 2)],
         [(0, 0), (4, 0), (4, 4), (0, 4)]),
        ("config A (10 boundary + 30 in)", config_a()[0], None),
        ("config B (collinear + dups)", config_b()[0], [(0, 0), (8000, 0), (8000, 5000), (0, 5000)]),
    ]
    print("CORRECTNESS TESTS  (expected hull = hand result and/or independent monotone-chain oracle, CCW order)")
    passed = 0
    for name, pts, expected in cases:
        expected = expected if expected is not None else monotone_chain(pts)
        hull, st = brute_force_hull(pts)
        hull_e, _ = brute_force_hull(pts, early_exit=True)
        n = st["distinct"]
        exact_tests = st["orientation_tests"] == (n * (n - 1) // 2) * (n - 2) if n > 2 else True
        ok = same_cycle(hull, expected) and same_cycle(hull_e, expected) and exact_tests \
            and same_cycle(hull, monotone_chain(pts) if len(set(pts)) > 2 and len(hull) > 2 else hull)
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  Q5 {name:<30} corners {len(hull):>2}, expected {len(expected):>2}"
              f" | early exit: {'same' if same_cycle(hull_e, expected) else 'DIFF'}"
              f" | test count: {'exact' if exact_tests else 'WRONG'}")
    rng = random.Random(11)
    rand_ok = True
    for _ in range(150):                                  # small grid -> many collinear points and duplicates
        pts = [(rng.randint(0, 12), rng.randint(0, 12)) for _ in range(rng.randint(3, 35))]
        hull, _ = brute_force_hull(pts)
        ref = monotone_chain(pts)
        rand_ok &= same_cycle(hull, ref) if len(ref) > 2 else sorted(hull) == sorted(ref)
    passed += rand_ok
    print(f"{'PASS' if rand_ok else 'FAIL'}  Q5 150 random grid sets (collinear/duplicate-heavy) equal the oracle")
    print(f"RESULT: {passed}/{len(cases) + 1} tests passed")
    return passed == len(cases) + 1


def describe(label, pts, expected_corners):
    hull, st = brute_force_hull(pts)
    _, st_e = brute_force_hull(pts, early_exit=True)
    n = st["distinct"]
    on_edge = boundary_non_corners(pts, hull)
    print(f"\n{label}: {st['input_points']} stations, {st['duplicates_removed']} duplicate(s) removed -> n = {n}")
    print(f"  candidate pairs C(n,2) = {st['pairs_examined']:,};  orientation tests = {st['orientation_tests']:,}"
          f" (formula n(n-1)(n-2)/2 = {n * (n - 1) * (n - 2) // 2:,});  with early rejection: {st_e['orientation_tests']:,}")
    print(f"  accepted edges = {st['edges_accepted']};  a naive one-side rule (collinear condition dropped) would accept"
          f" {naive_edge_count(pts)}")
    print(f"  hull corners (counter-clockwise) = {len(hull)}:")
    for k in range(0, len(hull), 5):
        print("     " + "  ".join(f"({x:>5},{y:>5})" for x, y in hull[k:k + 5]))
    if on_edge:
        print(f"  stations ON the boundary but not corners (collinear): {len(on_edge)} -> "
              + " ".join(f"({x},{y})" for x, y in on_edge[:5]) + (" ..." if len(on_edge) > 5 else ""))
    print(f"  expected corners found: {'YES' if same_cycle(hull, expected_corners) or set(hull) == set(expected_corners) else 'NO'}"
          f";  matches monotone-chain oracle: {'YES' if same_cycle(hull, monotone_chain(pts)) else 'NO'}")
    return hull, on_edge, st, st_e


def plot(configs):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, (title, pts, hull, on_edge) in zip(axes, configs):
        uniq = list(dict.fromkeys(pts))
        dup = [p for p in uniq if pts.count(p) > 1]
        inner = [p for p in uniq if p not in hull and p not in on_edge]
        poly = hull + hull[:1]
        ax.fill([p[0] for p in poly], [p[1] for p in poly], color="#55A868", alpha=0.12)
        if "diagonal" in title:                          # stations collinear with a corner-to-corner diagonal
            ax.plot([0, 8000], [0, 5000], ":", color="grey", lw=1, label="diagonal (collinear interior stations)")
        ax.plot([p[0] for p in poly], [p[1] for p in poly], "-", color="#2E7D32", lw=2, label="computed boundary")
        ax.scatter([p[0] for p in inner], [p[1] for p in inner], s=25, color="#4C72B0", label="interior station")
        if on_edge:
            ax.scatter([p[0] for p in on_edge], [p[1] for p in on_edge], s=45, marker="s", facecolors="none",
                       edgecolors="#DD8452", lw=1.5, label="on boundary, not a corner")
        ax.scatter([p[0] for p in hull], [p[1] for p in hull], s=70, color="#C44E52", zorder=3, label="hull corner")
        if dup:
            ax.scatter([p[0] for p in dup], [p[1] for p in dup], s=220, facecolors="none", edgecolors="black",
                       lw=1, label="duplicate station (removed)")
        for k, (x, y) in enumerate(hull, start=1):
            ax.annotate(f"C{k}", (x, y), textcoords="offset points", xytext=(6, 6), fontsize=8, color="#C44E52")
        ax.set_title(title)
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(0, -0.12), ncol=3)
    fig.suptitle("Q5 - Brute-force convex hull of the reserve monitoring stations")
    fig.tight_layout()
    path = os.path.join(SHOTS, "q5_hull_configs.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main():
    ok = run_tests()
    a_pts, a_expected = config_a()
    b_pts, b_expected = config_b()
    os.makedirs(os.path.join(RESULTS, "datasets"), exist_ok=True)
    rows = []
    for name, pts in (("A", a_pts), ("B", b_pts)):
        with open(os.path.join(RESULTS, "datasets", f"q5_config_{name}.csv"), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["station", "x_m", "y_m"])
            w.writerows((f"S{k + 1}", x, y) for k, (x, y) in enumerate(pts))
    ha, ea, sa, sea = describe("CONFIG A - perimeter + interior stations", a_pts, a_expected)
    hb, eb, sb, seb = describe("CONFIG B - collinear sides, vertical edges, duplicates, diagonal", b_pts, b_expected)
    for name, hull, st, ste in (("A", ha, sa, sea), ("B", hb, sb, seb)):
        rows.append({"config": name, "input_points": st["input_points"], "duplicates_removed": st["duplicates_removed"],
                     "n_distinct": st["distinct"], "pairs_examined": st["pairs_examined"],
                     "orientation_tests_full": st["orientation_tests"],
                     "orientation_tests_early_exit": ste["orientation_tests"], "edges_accepted": st["edges_accepted"],
                     "hull_corners": len(hull), "hull_ccw": " ".join(f"({x};{y})" for x, y in hull)})
    with open(os.path.join(RESULTS, "q5_configs.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    path = plot([("Config A: 10 perimeter + 30 interior stations", a_pts, ha, ea),
                 ("Config B: collinear sides, duplicates, diagonal", b_pts, hb, eb)])
    print(f"\nCSV  : results/q5_configs.csv  datasets: results/datasets/q5_config_A.csv, q5_config_B.csv")
    print(f"Graph: ../Output_Screenshots/{os.path.basename(path)}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
