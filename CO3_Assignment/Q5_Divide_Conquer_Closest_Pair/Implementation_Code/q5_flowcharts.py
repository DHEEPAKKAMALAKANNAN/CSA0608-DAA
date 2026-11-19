"""q5_flowcharts.py - flowcharts of the two closest-pair algorithms of Q5 (CSA06 DAA, Assignment 3 - CO3).

Draws, with standard flowchart symbols (see flowchart_helpers.py):
  ../Pseudocode/q5_flowchart_brute_force.png      CO2 baseline: every pair, n(n-1)/2 distance computations
  ../Pseudocode/q5_flowchart_dc_closest_pair.png  Divide-and-Conquer: presort, recursive Closest(Px) with the strip
Run:  py -3 q5_flowcharts.py
"""
import os

from matplotlib.patches import Rectangle

from flowchart_helpers import Node, arrow, new_canvas, save

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Pseudocode")


def flowchart_brute_force():
    fig, ax = new_canvas(10, 1.4, 15.4, "Brute-Force Closest Pair (CO2 baseline)")
    start = Node(ax, 5, 14.6, "Start", "terminal", w=2.2)
    inp = Node(ax, 5, 13.5, "Input: drones D[0..n-1] = (x, y)", "io", w=5.4)
    init = Node(ax, 5, 12.3, "best2 <- infinity;  i <- 0", "process", w=4.2)
    d1 = Node(ax, 5, 10.9, "i <= n - 2 ?", "decision", w=3.0, h=1.3)
    j0 = Node(ax, 5, 9.5, "j <- i + 1", "process", w=2.4)
    d2 = Node(ax, 5, 8.1, "j <= n - 1 ?", "decision", w=3.0, h=1.3)
    dist = Node(ax, 5, 6.6, "d2 <- (xi - xj)^2 + (yi - yj)^2\n(one distance computation)", "process",
                w=4.2, h=1.0, size=8.5)
    d3 = Node(ax, 5, 5.0, "d2 < best2 ?", "decision", w=3.0, h=1.3)
    upd = Node(ax, 8.4, 5.0, "best2 <- d2\npair <- (D[i], D[j])", "process", w=2.8, h=1.0, size=8.5)
    incj = Node(ax, 5, 3.6, "j <- j + 1", "process", w=2.4)
    inci = Node(ax, 1.3, 8.1, "i <- i + 1", "process", w=1.8)
    out = Node(ax, 8.2, 10.9, "Output: sqrt(best2),\npair", "io", w=2.9, h=0.9, size=8.5)
    end = Node(ax, 8.2, 12.3, "End", "terminal", w=2.0)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), d1.top()])
    arrow(ax, [d1.bottom(), j0.top()], "Yes", 0)
    arrow(ax, [d1.right(), out.left()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [out.top(), end.bottom()])
    arrow(ax, [j0.bottom(), d2.top()])
    arrow(ax, [d2.bottom(), dist.top()], "Yes", 0)
    arrow(ax, [d2.left(), inci.right()], "No", 0, dx=-0.6, dy=0.15)
    arrow(ax, [inci.top(), (inci.x, d1.y), d1.left()])
    arrow(ax, [dist.bottom(), d3.top()])
    arrow(ax, [d3.right(), upd.left()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [d3.bottom(), incj.top()], "No", 0)
    arrow(ax, [upd.bottom(), (upd.x, incj.y), incj.right()])
    arrow(ax, [incj.left(), (2.65, incj.y), (2.65, 8.9), (d2.x, 8.9), d2.top()])
    ax.text(5, 2.3, "Every one of the n(n-1)/2 pairs is examined: Theta(n^2) distance computations",
            ha="center", fontsize=8.5, style="italic")
    save(fig, os.path.join(OUT, "q5_flowchart_brute_force.png"))


def flowchart_dc():
    fig, ax = new_canvas(13, 0.3, 21.2, "Divide-and-Conquer Closest Pair")
    start = Node(ax, 6.5, 20.5, "Start", "terminal", w=2.2)
    inp = Node(ax, 6.5, 19.45, "Input: drones D[0..n-1], n >= 2", "io", w=5.0)
    pre = Node(ax, 6.5, 18.3, "Px <- MergeSortBy(D, x)   (presort once, Theta(n log n))", "call", w=7.6)
    call = Node(ax, 6.5, 17.15, "(best2, pair, Py) <- Closest(Px)", "call", w=5.4)
    out = Node(ax, 6.5, 16.05, "Output: sqrt(best2), pair", "io", w=4.4)
    end = Node(ax, 6.5, 15.0, "End", "terminal", w=2.2)
    for a, b in ((start, inp), (inp, pre), (pre, call), (call, out), (out, end)):
        arrow(ax, [a.bottom(), b.top()])
    ax.add_patch(Rectangle((0.2, 0.6), 12.6, 13.85, fill=False, ls="--", lw=1.0, ec="#555555"))
    ax.text(0.4, 14.05, "function Closest(Px)  - returns (best squared distance, pair, Px sorted by y)",
            fontsize=9, style="italic")
    entry = Node(ax, 6.5, 13.3, "Closest(Px), m = |Px|", "terminal", w=4.0)
    arrow(ax, [call.right(), (11.9, call.y), (11.9, 14.3), (7.6, 14.3), (7.6, entry.y + entry.h / 2)],
          "first call", 1, dx=0.1, dy=-0.4, dashed=True)
    d1 = Node(ax, 6.5, 11.95, "m <= 3 ?", "decision", w=2.6, h=1.2)
    base = Node(ax, 2.75, 11.95, "BASE: brute force on\n<= 3 points; sort them by y;\nreturn (best2, pair, Py)",
                "terminal", w=3.4, h=1.3, size=8)
    div = Node(ax, 6.5, 10.55, "DIVIDE: mid <- floor(m/2); mid_x <- Px[mid].x", "process", w=6.0)
    rec = Node(ax, 6.5, 9.35, "CONQUER: (bL, pL, Ly) <- Closest(Px[0..mid-1])\n"
               "(bR, pR, Ry) <- Closest(Px[mid..m-1])", "call", w=6.8, h=1.0, size=8.5)
    best = Node(ax, 6.5, 8.1, "best2 <- min(bL, bR) with its pair;  Py <- MergeByY(Ly, Ry)", "process", w=7.6)
    strip = Node(ax, 6.5, 7.0, "delta <- sqrt(best2);  S <- [p in Py : |p.x - mid_x| < delta]  (y order)",
                 "process", w=8.4)
    i0 = Node(ax, 6.5, 5.95, "i <- 0", "process", w=1.8)
    d2 = Node(ax, 6.5, 4.75, "i < |S| ?", "decision", w=2.6, h=1.2)
    ret = Node(ax, 10.6, 4.75, "return\n(best2, pair, Py)", "terminal", w=2.6, h=1.0, size=8.5)
    d3 = Node(ax, 6.5, 3.2, "next S[j] with\nS[j].y - S[i].y < delta ?", "decision", w=4.0, h=1.6, size=8.5)
    cmp_ = Node(ax, 6.5, 1.45, "distance(S[i], S[j]); if smaller: update best2, pair, delta\n"
                "(at most 7 such j per strip point)", "process", w=7.4, h=1.0, size=8.5)
    inci = Node(ax, 2.2, 3.2, "i <- i + 1", "process", w=1.9)
    arrow(ax, [entry.bottom(), d1.top()])
    arrow(ax, [d1.left(), base.right()], "Yes", 0, dx=-0.6, dy=0.15)
    arrow(ax, [d1.bottom(), div.top()], "No", 0)
    arrow(ax, [div.bottom(), rec.top()])
    arrow(ax, [rec.bottom(), best.top()])
    arrow(ax, [best.bottom(), strip.top()])
    arrow(ax, [strip.bottom(), i0.top()])
    arrow(ax, [i0.bottom(), d2.top()])
    arrow(ax, [d2.right(), ret.left()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [d2.bottom(), d3.top()], "Yes", 0)
    arrow(ax, [d3.bottom(), cmp_.top()], "Yes", 0)
    arrow(ax, [cmp_.right(), (11.6, cmp_.y), (11.6, d3.y), d3.right()])
    arrow(ax, [d3.left(), inci.right()], "No", 0, dx=-0.55, dy=0.15)
    arrow(ax, [inci.top(), (inci.x, d2.y), d2.left()])
    arrow(ax, [rec.left(), (0.55, rec.y), (0.55, entry.y), entry.left()], dashed=True)
    ax.text(0.38, 10.4, "recursive calls", rotation=90, fontsize=9, fontweight="bold", color="#7f3f00",
            ha="center", va="center")
    save(fig, os.path.join(OUT, "q5_flowchart_dc_closest_pair.png"))


def main():
    flowchart_brute_force()
    flowchart_dc()


if __name__ == "__main__":
    main()
