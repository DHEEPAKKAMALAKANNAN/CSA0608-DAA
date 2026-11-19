"""
draw_diagrams_t6.py - flowcharts and diagrams for Task 6 (TSP by Held-Karp dynamic programming).

Standard flowchart symbols drawn with matplotlib (terminal = rounded, process = rectangle, decision = diamond,
input/output = parallelogram, predefined process = rectangle with side bars).  All route data are computed by
tsp_held_karp.py at run time (nothing is typed in by hand).  Writes into ../../Report/Screenshots/:
  t6_flowchart_held_karp.png    Held-Karp DP
  t6_flowchart_exhaustive.png   exhaustive enumeration used as the independent reference (Task 6.4)
  t6_state_insufficient.png     Task 6.1: why the current location alone cannot be the state
  t6_subset_lattice.png         Task 6.2: DP[S][j] built from smaller subsets (hub + 4 locations)
  t6_delivery_map.png           Task 6.3: delivery map with the optimal tour
Run:  py -3 draw_diagrams_t6.py
"""
import csv
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

import tsp_held_karp as hk  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "..", "Report", "Screenshots")
DATA = os.path.join(HERE, "test_data")
FILL = {"terminal": "#d9ead3", "process": "#dbe8f6", "decision": "#fff2cc", "io": "#e8dff5",
        "call": "#fde3cf"}


# ----------------------------------------------------------------------------- flowchart helpers
class Node:
    """A flowchart symbol centred at (x, y) with width w and height h."""

    def __init__(self, ax, x, y, text, kind="process", w=3.6, h=0.8, size=9):
        self.x, self.y, self.w, self.h = x, y, w, h
        style = dict(facecolor=FILL[kind], edgecolor="#333333", linewidth=1.2)
        if kind == "terminal":
            ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                        boxstyle=f"round,pad=0,rounding_size={h / 2}", **style))
        elif kind == "decision":
            ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)], **style))
        elif kind == "io":
            s = 0.25
            ax.add_patch(Polygon([(x - w / 2 + s, y + h / 2), (x + w / 2 + s, y + h / 2),
                                  (x + w / 2 - s, y - h / 2), (x - w / 2 - s, y - h / 2)], **style))
        else:
            ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, **style))
            if kind == "call":
                for dx in (0.18, w - 0.18):
                    ax.plot([x - w / 2 + dx] * 2, [y - h / 2, y + h / 2], color="#333333", lw=1.0)
        ax.text(x, y, text, ha="center", va="center", fontsize=size)

    def top(self):
        return (self.x, self.y + self.h / 2)

    def bottom(self):
        return (self.x, self.y - self.h / 2)

    def left(self):
        return (self.x - self.w / 2, self.y)

    def right(self):
        return (self.x + self.w / 2, self.y)


def arrow(ax, points, label=None, label_at=0, dx=0.12, dy=0.12, dashed=False):
    """Draw a polyline through `points` with an arrow head at the end; optional label near a vertex."""
    xs, ys = zip(*points)
    ax.plot(xs, ys, color="#333333", lw=1.2, ls="--" if dashed else "-")
    ax.annotate("", xy=points[-1], xytext=points[-2],
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2, shrinkA=0, shrinkB=0))
    if label:
        x, y = points[label_at]
        ax.text(x + dx, y + dy, label, fontsize=9, fontweight="bold", color="#7f3f00")


def new_canvas(width, y_low, y_high, title):
    fig, ax = plt.subplots(figsize=(width * 0.62, (y_high - y_low) * 0.62))
    ax.set_xlim(0, width)
    ax.set_ylim(y_low, y_high)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold")
    return fig, ax


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(os.path.normpath(path))


# ----------------------------------------------------------------------------- flowcharts
def flowchart_held_karp():
    fig, ax = new_canvas(13.2, 0.6, 21.4, "Held-Karp Dynamic Programming for the delivery TSP")
    cx = 5.6
    start = Node(ax, cx, 20.7, "Start", "terminal", w=2.2)
    inp = Node(ax, cx, 19.6, "Input: cost matrix c[0..n][0..n]\n(0 = hub, 1..n = delivery locations)", "io",
               w=6.0, h=1.0)
    valid = Node(ax, cx, 18.0, "matrix square, n >= 1,\ncosts >= 0, diagonal 0 ?", "decision", w=4.8, h=1.7)
    err = Node(ax, 11.0, 18.0, "Output: reject\n(InvalidCostMatrix)", "io", w=3.0, h=1.0)
    base = Node(ax, cx, 16.2, "for every location j:\nDP[{j}][j] <- c(hub, j);  PARENT[{j}][j] <- hub", "process",
                w=6.6, h=1.0)
    dS = Node(ax, cx, 14.5, "next subset S (increasing\nbitmask, |S| >= 2) ?", "decision", w=4.8, h=1.7)
    dj = Node(ax, cx, 12.3, "next location j in S ?", "decision", w=4.2, h=1.4)
    rec = Node(ax, cx, 10.3, "DP[S][j] <- min over k in S-{j} of DP[S-{j}][k] + c(k, j)\n"
                             "PARENT[S][j] <- the minimising k   (count: 1 state, |S|-1 transitions)",
               "process", w=8.6, h=1.1, size=8.5)
    close = Node(ax, 1.9, 8.4, "OPT <- min over j of\nDP[ALL][j] + c(j, hub)\n(return to hub)", "process",
                 w=3.4, h=1.4, size=8.5)
    dinf = Node(ax, 1.9, 6.3, "OPT = inf ?", "decision", w=2.8, h=1.3)
    nofeas = Node(ax, 1.9, 4.4, "Output: no feasible\ntour", "io", w=3.0, h=1.0)
    recon = Node(ax, 6.6, 6.3, "Reconstruct route: start at best last j,\n"
                               "follow PARENT[S][j] back to hub, reverse", "call", w=6.2, h=1.1, size=8.5)
    out = Node(ax, 6.6, 4.4, "Output: OPT, route Hub -> ... -> Hub,\nstates and transitions", "io", w=6.0, h=1.0)
    end = Node(ax, 4.2, 2.6, "End", "terminal", w=2.2)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), valid.top()])
    arrow(ax, [valid.right(), err.left()], "No", 0, dx=0.1, dy=0.15)
    arrow(ax, [err.right(), (12.85, err.y), (12.85, end.y), end.right()])
    arrow(ax, [valid.bottom(), base.top()], "Yes", 0)
    arrow(ax, [base.bottom(), dS.top()])
    arrow(ax, [dS.bottom(), dj.top()], "Yes", 0)
    arrow(ax, [dj.bottom(), rec.top()], "Yes", 0)
    arrow(ax, [rec.right(), (10.4, rec.y), (10.4, dj.y), dj.right()])
    arrow(ax, [dj.left(), (2.2, dj.y), (2.2, dS.y), dS.left()], "No", 0, dx=-0.6, dy=0.15)
    arrow(ax, [dS.right(), (11.4, dS.y), (11.4, 9.1), (close.x, 9.1)], "No", 0, dx=0.1, dy=0.15)
    arrow(ax, [close.bottom(), dinf.top()])
    arrow(ax, [dinf.bottom(), nofeas.top()], "Yes", 0)
    arrow(ax, [dinf.right(), recon.left()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [recon.bottom(), out.top()])
    arrow(ax, [nofeas.bottom(), (nofeas.x, end.y), end.left()])
    arrow(ax, [out.bottom(), (out.x, 3.4), (end.x + 0.6, 3.4), (end.x + 0.6, end.y + end.h / 2)])
    ax.text(6.5, 1.2, "Increasing bitmask order guarantees that S-{j} is always finished before S.\n"
            "States n*2^(n-1), transitions n(n-1)*2^(n-2) + n  ->  time Theta(n^2 2^n), memory Theta(n 2^n)",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "t6_flowchart_held_karp.png")


def flowchart_exhaustive():
    fig, ax = new_canvas(12, 1.0, 15.0, "Exhaustive enumeration (independent reference, Task 6.4)")
    cx = 6.0
    start = Node(ax, cx, 14.3, "Start", "terminal", w=2.2)
    inp = Node(ax, cx, 13.2, "Input: cost matrix c (hub + n locations)", "io", w=5.6)
    init = Node(ax, cx, 12.0, "best <- inf;  bestRoutes <- []", "process", w=4.4)
    dp = Node(ax, cx, 10.5, "next permutation p of\nlocations 1..n ?", "decision", w=4.4, h=1.6)
    cost = Node(ax, cx, 8.6, "cost <- c(hub,p1) + c(p1,p2) + ... + c(pn,hub)\n(legs re-added, no DP)", "process",
                w=6.2, h=1.0, size=8.5)
    less = Node(ax, cx, 6.9, "cost < best ?", "decision", w=3.0, h=1.3)
    upd = Node(ax, cx, 5.3, "best <- cost;  bestRoutes <- [p]", "process", w=4.6)
    eq = Node(ax, 10.2, 6.9, "cost = best:\nappend p", "process", w=2.2, h=1.0, size=8.5)
    out = Node(ax, 1.5, 4.1, "Output: best,\nbestRoutes,\nn! routes tried", "io", w=2.5, h=1.4, size=8.5)
    end = Node(ax, 1.5, 2.5, "End", "terminal", w=2.0)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), dp.top()])
    arrow(ax, [dp.bottom(), cost.top()], "Yes", 0)
    arrow(ax, [cost.bottom(), less.top()])
    arrow(ax, [less.bottom(), upd.top()], "Yes", 0)
    arrow(ax, [less.right(), eq.left()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [eq.top(), (eq.x, dp.y), dp.right()])
    arrow(ax, [upd.right(), (11.7, upd.y), (11.7, 11.3), (cx + 0.9, 11.3), (cx + 0.9, dp.y + 0.6)])
    arrow(ax, [dp.left(), (out.x, dp.y), out.top()], "No", 0, dx=-0.7)
    arrow(ax, [out.bottom(), end.top()])
    ax.text(6.6, 1.4, "n! routes, n+1 additions each  ->  Theta(n * n!)   (n = 4: 24 routes; n = 6: 720; n = 9: 362,880)",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "t6_flowchart_exhaustive.png")


# ----------------------------------------------------------------------------- map helpers
def load_coordinates():
    with open(os.path.join(DATA, "delivery_locations.csv"), newline="", encoding="utf-8") as f:
        return {r["name"]: (float(r["x_km"]), float(r["y_km"])) for r in csv.DictReader(f)}


def draw_nodes(ax, coords, highlight=(), faded=()):
    for name, (x, y) in coords.items():
        colour = "#c00000" if name == "Hub" else ("#1f4e79" if name in highlight else "#7f7f7f")
        alpha = 0.35 if name in faded else 1.0
        marker = "s" if name == "Hub" else "o"
        ax.scatter([x], [y], s=520 if name == "Hub" else 380, marker=marker, color=colour, alpha=alpha, zorder=3,
                   edgecolors="black")
        ax.text(x, y, name if name != "Hub" else "H", ha="center", va="center", color="white", fontsize=9,
                fontweight="bold", zorder=4)


def draw_leg(ax, p, q, colour, label=None, width=2.0, style="-|>"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=16, color=colour, lw=width,
                                 shrinkA=13, shrinkB=13, zorder=2))
    if label is not None:
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        ax.text(mx, my, label, fontsize=8.5, ha="center", va="center", zorder=5,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=colour, lw=0.8))


def frame(ax, title):
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_xlim(-10, 11)
    ax.set_ylim(-10.5, 12.5)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.25)
    ax.set_xlabel("x (km)")
    ax.set_ylabel("y (km)")


def state_insufficient(names, cost, coords):
    idx = {nm: i for i, nm in enumerate(names)}
    partial = [("Partial route P1: Hub -> A -> F -> B", ["Hub", "A", "F", "B"]),
               ("Partial route P2: Hub -> D -> B", ["Hub", "D", "B"]),
               ("Partial route P3: Hub -> F -> A -> B", ["Hub", "F", "A", "B"])]
    fig, axes = plt.subplots(1, 3, figsize=(16, 6.2))
    for ax, (title, route) in zip(axes, partial):
        visited = set(route[1:])
        remaining = sorted(set(names[1:]) - visited)
        draw_nodes(ax, coords, highlight=visited, faded=remaining)
        total = 0
        for a, b in zip(route, route[1:]):
            total += cost[idx[a]][idx[b]]
            draw_leg(ax, coords[a], coords[b], "#1f4e79", str(cost[idx[a]][idx[b]]))
        frame(ax, title)
        ax.text(0.5, -0.2, f"current location j = B,  visited S = {{{','.join(sorted(visited))}}}\n"
                f"cost so far = {total} min,  still to visit: {{{','.join(remaining)}}}",
                transform=ax.transAxes, ha="center", va="top", fontsize=9.5,
                bbox=dict(boxstyle="round", fc="#fff2cc", ec="#b8860b"))
    fig.suptitle("Task 6.1 - the current location alone is not a valid state: P1 and P2 both stand at B but "
                 "must still visit different locations;\nP1 and P3 have the same (S, j) = ({A,B,F}, B), so only "
                 "the cheaper one (P1) can belong to an optimal tour - DP keeps one value per (S, j)",
                 fontsize=10.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0.03, 1, 0.92))
    save(fig, "t6_state_insufficient.png")


def subset_lattice():
    names, cost = hk.load_cost_matrix(os.path.join(DATA, "validation_hub4.csv"))
    n = len(names) - 1
    trace = []
    result = hk.held_karp(cost, Counter(), trace)
    dp = {(m, j): (v, k) for m, j, v, k in trace}
    chain, mask = set(), 0
    for j in result.route[1:-1]:
        mask |= 1 << (j - 1)
        chain.add((mask, j))
    by_size = {}
    for m in range(1, 1 << n):
        by_size.setdefault(bin(m).count("1"), []).append(m)
    fig, ax = plt.subplots(figsize=(17, 10.4))
    ax.set_xlim(0, 17)
    ax.set_ylim(0.2, 11.0)
    ax.axis("off")
    pos, bw, bh = {}, 1.95, 1.25
    for size, masks in by_size.items():
        y = 1.2 + (size - 1) * 2.45
        for i, m in enumerate(masks):
            pos[m] = (0.8 + 16.2 * (i + 1) / (len(masks) + 1), y)
        ax.text(0.05, y, f"|S| = {size}", fontsize=10, fontweight="bold", va="center")
    for m, (x, y) in pos.items():                                    # inclusion edges S-{j} -> S
        for j in hk.members(m, n):
            prev = m ^ (1 << (j - 1))
            if prev:
                on_chain = (m, j) in chain and (prev, dp[(m, j)][1]) in chain
                px, py = pos[prev]
                ax.plot([px, x], [py + bh / 2, y - bh / 2], color="#c00000" if on_chain else "#c8c8c8",
                        lw=2.6 if on_chain else 0.8, zorder=1)
    for m, (x, y) in pos.items():
        is_chain = any((m, j) in chain for j in range(1, n + 1))
        ax.add_patch(FancyBboxPatch((x - bw / 2, y - bh / 2), bw, bh, boxstyle="round,pad=0.04",
                                    fc="#fde3cf" if is_chain else "#dbe8f6",
                                    ec="#c00000" if is_chain else "#333333", lw=1.8 if is_chain else 1.0, zorder=2))
        label = "{" + ",".join(names[j] for j in hk.members(m, n)) + "}"
        ax.text(x, y + bh / 2 - 0.2, label, ha="center", va="center", fontsize=9, fontweight="bold", zorder=3)
        cells = [f"{names[j]}:{dp[(m, j)][0]:g}" + ("*" if (m, j) in chain else "") for j in hk.members(m, n)]
        lines = ["  ".join(cells[:2])] + (["  ".join(cells[2:])] if len(cells) > 2 else [])
        ax.text(x, y - 0.18, "\n".join(lines), ha="center", va="center", fontsize=8.2, zorder=3)
    full = (1 << n) - 1
    fx, fy = pos[full]
    last = result.route[-2]
    hub_y = fy + 1.5
    ax.add_patch(FancyBboxPatch((fx - 2.6, hub_y - 0.4), 5.2, 0.8, boxstyle="round,pad=0.04", fc="#d9ead3",
                                ec="#c00000", lw=1.8))
    ax.text(fx, hub_y, f"return to Hub: min_j DP[ALL][j] + c(j,Hub) = {dp[(full, last)][0]:g} + "
            f"{cost[last][0]} = {result.cost:g}", ha="center", va="center", fontsize=9, fontweight="bold")
    ax.plot([fx, fx], [fy + bh / 2, hub_y - 0.4], color="#c00000", lw=2.6)
    ax.set_title("Task 6.2 - DP[S][j] for the hub + 4 instance: each box is a subset S with DP[S][j] for every "
                 "end location j;\nlines join S-{j} to S (the recurrence uses only smaller subsets). "
                 f"Red = optimal chain (* entries): {' -> '.join(names[v] for v in result.route)}",
                 fontsize=10.5, fontweight="bold")
    fig.tight_layout()
    save(fig, "t6_subset_lattice.png")


def delivery_map(names, cost, coords):
    result = hk.held_karp(cost)
    fig, ax = plt.subplots(figsize=(9.5, 9.5))
    for i in range(len(names)):                                       # all roads, light grey with costs
        for j in range(i + 1, len(names)):
            p, q = coords[names[i]], coords[names[j]]
            ax.plot([p[0], q[0]], [p[1], q[1]], color="#d0d0d0", lw=0.8, zorder=1)
    draw_nodes(ax, coords, highlight=set(names[1:]))
    total = 0
    for step, (a, b) in enumerate(zip(result.route, result.route[1:]), 1):
        total += cost[a][b]
        draw_leg(ax, coords[names[a]], coords[names[b]], "#c00000", f"{step}: {cost[a][b]}", width=2.4)
    for order, v in enumerate(result.route[1:-1], 1):
        x, y = coords[names[v]]
        ax.text(x + 0.9, y + 0.9, f"#{order}", fontsize=10, color="#1f4e79", fontweight="bold")
    frame(ax, "")
    ax.set_title("Task 6.3 - Delivery map and the optimal tour found by Held-Karp\n"
                 + " -> ".join(names[v] for v in result.route) + f"   (Minimum Travel Cost = {result.cost:g} min)",
                 fontsize=11, fontweight="bold")
    ax.text(0.01, 0.01, "red arrows: legs in driving order with 'leg number: minutes'; #k: visit order; "
            "grey: all other roads", transform=ax.transAxes, fontsize=8.5, style="italic")
    save(fig, "t6_delivery_map.png")


def main():
    names, cost = hk.load_cost_matrix(os.path.join(DATA, "delivery_costs.csv"))
    coords = load_coordinates()
    flowchart_held_karp()
    flowchart_exhaustive()
    state_insufficient(names, cost, coords)
    subset_lattice()
    delivery_map(names, cost, coords)


if __name__ == "__main__":
    main()
