"""
draw_flowcharts.py - draws the flowchart of every algorithm designed in Assignment 4A (Tasks 1-6).

Standard symbols: terminal = rounded box, process = rectangle, decision = diamond (Yes/No labels),
input/output = parallelogram, predefined process = rectangle with side bars.  The flowcharts follow the
pseudocode in the report line by line.  PNGs are written next to this file.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FILL = {"terminal": "#d9ead3", "process": "#dbe8f6", "decision": "#fff2cc", "io": "#e8dff5",
        "call": "#fde3cf"}


class Node:
    """A flowchart symbol centred at (x, y) with width w and height h."""

    def __init__(self, ax, x, y, text, kind="process", w=3.6, h=0.8, size=8.5, edge="#333333", lw=1.2):
        self.x, self.y, self.w, self.h = x, y, w, h
        style = dict(facecolor=FILL[kind], edgecolor=edge, linewidth=lw)
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
                    ax.plot([x - w / 2 + dx] * 2, [y - h / 2, y + h / 2], color=edge, lw=1.0)
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
    """Polyline through `points` with an arrow head at the end; optional Yes/No label near a vertex."""
    xs, ys = zip(*points)
    ax.plot(xs, ys, color="#333333", lw=1.2, ls="--" if dashed else "-")
    ax.annotate("", xy=points[-1], xytext=points[-2],
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2, shrinkA=0, shrinkB=0))
    if label:
        x, y = points[label_at]
        ax.text(x + dx, y + dy, label, fontsize=8.5, fontweight="bold", color="#7f3f00")


def canvas(width, y_low, y_high, title):
    fig, ax = plt.subplots(figsize=(width * 0.62, (y_high - y_low) * 0.62))
    ax.set_xlim(0, width)
    ax.set_ylim(y_low, y_high)
    ax.axis("off")
    ax.set_title(title, fontsize=11.5, fontweight="bold")
    return fig, ax


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(path)


def chain(ax, nodes):
    for a, b in zip(nodes, nodes[1:]):
        arrow(ax, [a.bottom(), b.top()])


# ------------------------------------------------------------------------------------------- Task 1
def fc_task1():
    fig, ax = canvas(12, 2.6, 17.8, "Task 1 - Repaired LoadVehicle (greedy by value per unit weight)")
    s = Node(ax, 6, 17.2, "Start", "terminal", w=2.2)
    i = Node(ax, 6, 16.15, "Input: P[1..n] (id, weight w, value v), capacity C", "io", w=7.2)
    p1 = Node(ax, 6, 15.0, "ratio[k] ← v[k] / w[k] for k = 1..n\nSORT P in descending order of ratio",
              "process", w=6.6, h=1.0)
    p2 = Node(ax, 6, 13.75, "remaining ← C;  total ← 0;  Load ← empty;  i ← 1", "process", w=6.6)
    d1 = Node(ax, 6, 12.25, "remaining > 0\nAND i ≤ n ?", "decision", w=3.8, h=1.6)
    d2 = Node(ax, 6, 10.15, "w[i] ≤ remaining ?\n(feasibility)", "decision", w=3.8, h=1.6)
    fa = Node(ax, 3.0, 8.6, "fraction ← 1\n(take whole package)", "process", w=3.2, h=0.9)
    fb = Node(ax, 9.0, 8.6, "fraction ← remaining / w[i]\n(divide the package)", "process", w=3.4, h=0.9)
    up = Node(ax, 6, 6.85, "ADD (id[i], fraction) to Load\nremaining ← remaining − fraction × w[i]\n"
              "total ← total + fraction × v[i];   i ← i + 1", "process", w=6.4, h=1.4)
    out = Node(ax, 6, 4.6, "Output: Load (packages + fractions), total", "io", w=6.2)
    e = Node(ax, 6, 3.4, "End", "terminal", w=2.2)
    chain(ax, [s, i, p1, p2, d1])
    arrow(ax, [d1.bottom(), d2.top()], "Yes", 0)
    arrow(ax, [d2.left(), (fa.x, d2.y), fa.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d2.right(), (fb.x, d2.y), fb.top()], "No", 0, dx=0.2)
    arrow(ax, [fa.bottom(), (fa.x, 7.85), (5.2, 7.85), (5.2, up.y + up.h / 2)])
    arrow(ax, [fb.bottom(), (fb.x, 7.85), (6.8, 7.85), (6.8, up.y + up.h / 2)])
    arrow(ax, [up.left(), (0.6, up.y), (0.6, d1.y), d1.left()], "repeat", 1, dx=0.1, dy=3.9)
    arrow(ax, [d1.right(), (11.3, d1.y), (11.3, out.y), out.right()], "No", 0, dx=0.1)
    arrow(ax, [out.bottom(), e.top()])
    ax.text(6, 2.85, "Loop ends when the vehicle is full or no package is left; at most one package is divided.",
            ha="center", fontsize=8, style="italic")
    save(fig, "fc_task1_load_vehicle.png")


# ------------------------------------------------------------------------------------------- Task 2
def fc_task2():
    fig, ax = canvas(12, 1.6, 18.6, "Task 2 - JobSequencing (max profit first, latest free slot)")
    s = Node(ax, 6, 18.0, "Start", "terminal", w=2.2)
    i = Node(ax, 6, 17.0, "Input: J[1..n] (id, deadline d, profit p)", "io", w=6.0)
    p1 = Node(ax, 6, 15.95, "SORT J in descending order of profit", "process", w=5.6)
    p2 = Node(ax, 6, 14.85, "m ← min(n, max d);  slot[1..m] ← EMPTY\ntotal ← 0;  k ← 1", "process", w=6.0, h=1.0)
    d1 = Node(ax, 6, 13.35, "k ≤ n ?", "decision", w=2.6, h=1.2)
    p3 = Node(ax, 6, 11.95, "t ← min(d[k], m)", "process", w=3.4)
    d2 = Node(ax, 6, 10.35, "t ≥ 1 AND\nslot[t] ≠ EMPTY ?", "decision", w=3.8, h=1.6)
    dec = Node(ax, 9.9, 10.35, "t ← t − 1\n(try earlier slot)", "process", w=2.6, h=0.9)
    d3 = Node(ax, 6, 8.25, "t ≥ 1 ?\n(feasible)", "decision", w=2.8, h=1.4)
    acc = Node(ax, 3.0, 6.75, "slot[t] ← id[k]\ntotal ← total + p[k]", "process", w=3.4, h=0.9)
    rej = Node(ax, 9.0, 6.75, "REJECT job k\n(no free slot ≤ d[k])", "process", w=3.2, h=0.9)
    inc = Node(ax, 6, 5.3, "k ← k + 1", "process", w=2.4)
    out = Node(ax, 6, 3.35, "Output: schedule slot[1..m], total", "io", w=5.6)
    e = Node(ax, 6, 2.25, "End", "terminal", w=2.2)
    chain(ax, [s, i, p1, p2, d1])
    arrow(ax, [d1.bottom(), p3.top()], "Yes", 0)
    arrow(ax, [p3.bottom(), d2.top()])
    arrow(ax, [d2.right(), dec.left()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [dec.top(), (dec.x, 11.35), (6, 11.35)])
    arrow(ax, [d2.bottom(), d3.top()], "No", 0)
    arrow(ax, [d3.left(), (acc.x, d3.y), acc.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d3.right(), (rej.x, d3.y), rej.top()], "No", 0, dx=0.2)
    arrow(ax, [acc.bottom(), (acc.x, inc.y), inc.left()])
    arrow(ax, [rej.bottom(), (rej.x, inc.y), inc.right()])
    arrow(ax, [inc.bottom(), (6, 4.6), (0.5, 4.6), (0.5, d1.y), d1.left()], "next job", 2, dx=0.1, dy=4.0)
    arrow(ax, [d1.right(), (11.5, d1.y), (11.5, out.y), out.right()], "No", 0, dx=0.1)
    arrow(ax, [out.bottom(), e.top()])
    save(fig, "fc_task2_job_sequencing.png")


# ------------------------------------------------------------------------------------------- Task 3
def fc_task3():
    fig, ax = canvas(20, 2.4, 19.6, "Task 3 - Knapsack01: table filling (left) and solution reconstruction (right)")
    s = Node(ax, 5.5, 19.0, "Start", "terminal", w=2.2)
    i = Node(ax, 5.5, 18.0, "Input: n items (id, wt, val), capacity W", "io", w=6.2)
    p0 = Node(ax, 5.5, 16.9, "DP[0][w] ← 0 for w = 0..W\nDP[i][0] ← 0 for i = 0..n;   i ← 1", "process", w=6.0, h=1.0)
    d1 = Node(ax, 5.5, 15.4, "i ≤ n ?", "decision", w=2.6, h=1.2)
    pw = Node(ax, 5.5, 14.05, "w ← 1", "process", w=2.0)
    d2 = Node(ax, 5.5, 12.75, "w ≤ W ?", "decision", w=2.6, h=1.2)
    d3 = Node(ax, 5.5, 11.0, "wt[i] ≤ w ?\n(can include)", "decision", w=3.2, h=1.5)
    inc = Node(ax, 2.6, 9.05, "DP[i][w] ← max(DP[i−1][w],\nval[i] + DP[i−1][w − wt[i]])",
               "process", w=4.6, h=1.0)
    exc = Node(ax, 8.4, 9.05, "DP[i][w] ← DP[i−1][w]\n(must exclude)", "process", w=3.4, h=1.0)
    ww = Node(ax, 5.5, 7.55, "w ← w + 1", "process", w=2.2)
    ii = Node(ax, 9.6, 12.75, "i ← i + 1", "process", w=2.0)
    chain(ax, [s, i, p0, d1])
    arrow(ax, [d1.bottom(), pw.top()], "Yes", 0)
    arrow(ax, [pw.bottom(), d2.top()])
    arrow(ax, [d2.bottom(), d3.top()], "Yes", 0)
    arrow(ax, [d3.left(), (inc.x, d3.y), inc.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d3.right(), (exc.x, d3.y), exc.top()], "No", 0, dx=0.2)
    arrow(ax, [inc.bottom(), (inc.x, ww.y), ww.left()])
    arrow(ax, [exc.bottom(), (exc.x, ww.y), ww.right()])
    arrow(ax, [ww.bottom(), (5.5, 6.9), (0.3, 6.9), (0.3, d2.y), d2.left()], "next column", 2, dx=0.1, dy=4.7)
    arrow(ax, [d2.right(), ii.left()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [ii.top(), (ii.x, d1.y), d1.right()])
    # reconstruction column
    ax.plot([11.1, 11.1], [2.6, 19.4], color="#999999", lw=0.8, ls=":")
    r0 = Node(ax, 15.5, 15.4, "i ← n;  w ← W;  Selected ← empty", "process", w=5.2)
    arrow(ax, [d1.left(), (0.12, d1.y), (0.12, 2.9), (11.6, 2.9), (11.6, r0.y), r0.left()],
          "No (table complete)", 0, dx=-3.3, dy=0.15)
    rd1 = Node(ax, 15.5, 13.9, "i ≥ 1 ?", "decision", w=2.6, h=1.2)
    rd2 = Node(ax, 15.5, 11.9, "DP[i][w] ≠ DP[i−1][w] ?\n(item i was included)", "decision", w=4.6, h=1.8)
    take = Node(ax, 15.5, 9.6, "ADD item i to Selected\nw ← w − wt[i]", "process", w=4.0, h=1.0)
    dn = Node(ax, 15.5, 8.1, "i ← i − 1", "process", w=2.2)
    out = Node(ax, 15.5, 5.0, "Output: optimum DP[n][W],\nSelected items", "io", w=5.0, h=1.0)
    e = Node(ax, 15.5, 3.7, "End", "terminal", w=2.2)
    arrow(ax, [r0.bottom(), rd1.top()])
    arrow(ax, [rd1.bottom(), rd2.top()], "Yes", 0)
    arrow(ax, [rd2.bottom(), take.top()], "Yes", 0)
    arrow(ax, [rd2.right(), (18.6, rd2.y), (18.6, dn.y), dn.right()], "No", 0, dx=0.1)
    arrow(ax, [take.bottom(), dn.top()])
    arrow(ax, [dn.left(), (12.0, dn.y), (12.0, rd1.y), rd1.left()], "repeat", 1, dx=0.1, dy=2.6)
    arrow(ax, [rd1.right(), (19.4, rd1.y), (19.4, out.y), out.right()], "No", 0, dx=0.1)
    arrow(ax, [out.bottom(), e.top()])
    ax.text(5.5, 5.9, "Rows are filled in increasing i, so row i−1 is\ncomplete before any DP[i][w] is computed.",
            ha="center", fontsize=8, style="italic")
    save(fig, "fc_task3_knapsack_dp.png")


# ------------------------------------------------------------------------------------------- Task 4
def fc_task4():
    fig, ax = canvas(12, 1.6, 17.6, "Task 4 - Corrected WordBreak (repaired decision highlighted in red)")
    s = Node(ax, 6, 17.0, "Start", "terminal", w=2.2)
    i = Node(ax, 6, 16.0, "Input: Text (length n), Dictionary", "io", w=5.6)
    p0 = Node(ax, 6, 14.95, "DP[0] ← TRUE;   i ← 1", "process", w=4.0)
    d1 = Node(ax, 6, 13.6, "i ≤ n ?", "decision", w=2.6, h=1.2)
    p1 = Node(ax, 6, 12.2, "DP[i] ← FALSE;   j ← 0", "process", w=4.0)
    d2 = Node(ax, 6, 10.85, "j ≤ i − 1 ?", "decision", w=3.0, h=1.2)
    d3 = Node(ax, 6, 8.75, "DP[j] = TRUE  AND\nsubstring(Text, j, i)\n∈ Dictionary ?", "decision", w=4.6,
              h=2.1, edge="#c00000", lw=2.2)
    t = Node(ax, 6, 6.7, "DP[i] ← TRUE\nBREAK (stop trying j)", "process", w=3.8, h=0.9)
    jj = Node(ax, 10.0, 8.75, "j ← j + 1", "process", w=2.2)
    ii = Node(ax, 6, 5.4, "i ← i + 1", "process", w=2.2)
    out = Node(ax, 6, 3.4, "Output: RETURN DP[n]", "io", w=4.2)
    e = Node(ax, 6, 2.3, "End", "terminal", w=2.2)
    chain(ax, [s, i, p0, d1])
    arrow(ax, [d1.bottom(), p1.top()], "Yes", 0)
    arrow(ax, [p1.bottom(), d2.top()])
    arrow(ax, [d2.bottom(), d3.top()], "Yes", 0)
    arrow(ax, [d3.bottom(), t.top()], "Yes", 0)
    arrow(ax, [d3.right(), jj.left()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [jj.top(), (jj.x, d2.y), d2.right()])
    arrow(ax, [t.bottom(), ii.top()])
    arrow(ax, [d2.left(), (1.8, d2.y), (1.8, ii.y), ii.left()], "No", 0, dx=-0.9)
    arrow(ax, [ii.bottom(), (6, 4.75), (0.6, 4.75), (0.6, d1.y), d1.left()], "next i", 2, dx=0.1, dy=4.0)
    arrow(ax, [d1.right(), (11.4, d1.y), (11.4, out.y), out.right()], "No", 0, dx=0.1)
    arrow(ax, [out.bottom(), e.top()])
    ax.text(9.6, 7.35, "repair: the condition\n'DP[j] = TRUE AND' is added", ha="center", fontsize=8,
            color="#c00000", style="italic")
    save(fig, "fc_task4_word_break_corrected.png")


# ------------------------------------------------------------------------------------------- Task 5
def fc_task5_dijkstra():
    fig, ax = canvas(12, 1.6, 17.0, "Task 5.1 - GreedyShortestPaths (Dijkstra), non-negative weights")
    s = Node(ax, 6, 16.4, "Start", "terminal", w=2.2)
    i = Node(ax, 6, 15.4, "Input: G = (V, E), weights w ≥ 0, source s", "io", w=6.4)
    p0 = Node(ax, 6, 14.25, "dist[v] ← ∞, pred[v] ← NIL for every v ∈ V\ndist[s] ← 0;   Q ← V (keyed by dist)",
              "process", w=6.6, h=1.0)
    d1 = Node(ax, 6, 12.75, "Q ≠ empty ?", "decision", w=3.0, h=1.2)
    p1 = Node(ax, 6, 11.4, "u ← EXTRACT_MIN(Q)\n(dist[u] becomes final)", "call", w=4.4, h=0.9)
    d2 = Node(ax, 6, 9.85, "another edge (u, v)\nnot yet examined ?", "decision", w=4.0, h=1.6)
    d3 = Node(ax, 6, 7.7, "dist[u] + w(u, v)\n< dist[v] ?  (relax)", "decision", w=4.0, h=1.6)
    up = Node(ax, 6, 5.75, "dist[v] ← dist[u] + w(u, v)\npred[v] ← u;   DECREASE_KEY(Q, v)", "process",
              w=5.2, h=1.0)
    out = Node(ax, 9.6, 3.3, "Output: dist[ ], pred[ ]", "io", w=4.0)
    e = Node(ax, 9.6, 2.2, "End", "terminal", w=2.2)
    chain(ax, [s, i, p0, d1])
    arrow(ax, [d1.bottom(), p1.top()], "Yes", 0)
    arrow(ax, [p1.bottom(), d2.top()])
    arrow(ax, [d2.bottom(), d3.top()], "Yes", 0)
    arrow(ax, [d3.bottom(), up.top()], "Yes", 0)
    arrow(ax, [d3.left(), (2.2, d3.y)], "No", 0, dx=-0.9)
    arrow(ax, [up.left(), (2.2, up.y), (2.2, d2.y), d2.left()])
    arrow(ax, [d2.right(), (10.4, d2.y), (10.4, 13.55), (6.0, 13.55)], "No (next vertex)", 0, dx=0.05)
    arrow(ax, [d1.right(), (11.85, d1.y), (11.85, out.y), out.right()], "No (all final)", 0, dx=0.05)
    arrow(ax, [out.bottom(), e.top()])
    ax.text(3.5, 3.3, "Termination: every vertex is\nextracted exactly once (|V| rounds).", ha="center",
            fontsize=8, style="italic")
    save(fig, "fc_task5_dijkstra.png")


def fc_task5_bellman_ford():
    fig, ax = canvas(12, 1.4, 16.0, "Task 5.2 - BellmanFord (repeated relaxation, negative-cycle check)")
    s = Node(ax, 6, 15.4, "Start", "terminal", w=2.2)
    i = Node(ax, 6, 14.4, "Input: G = (V, E), weights w (may be < 0), source s", "io", w=7.0)
    p0 = Node(ax, 6, 13.3, "dist[v] ← ∞, pred[v] ← NIL;  dist[s] ← 0;  k ← 1", "process", w=6.8)
    d1 = Node(ax, 6, 11.9, "k ≤ |V| − 1 ?", "decision", w=3.2, h=1.2)
    p1 = Node(ax, 6, 10.35, "changed ← FALSE;  FOR each edge (u, v) ∈ E:\nIF dist[u] + w(u, v) < dist[v] THEN\n"
              "dist[v] ← dist[u] + w(u, v); pred[v] ← u; changed ← TRUE", "call", w=7.2, h=1.4)
    d2 = Node(ax, 6, 8.5, "changed ?", "decision", w=2.8, h=1.2)
    k = Node(ax, 9.9, 8.5, "k ← k + 1", "process", w=2.0)
    d3 = Node(ax, 6, 6.3, "some edge (u, v) still has\ndist[u] + w(u, v) < dist[v] ?", "decision", w=5.4, h=1.8)
    neg = Node(ax, 2.6, 4.1, "Output: 'reachable\nnegative cycle'", "io", w=3.4, h=1.0)
    ok = Node(ax, 9.4, 4.1, "Output: dist[ ], pred[ ]", "io", w=3.8)
    e = Node(ax, 6, 2.2, "End", "terminal", w=2.2)
    chain(ax, [s, i, p0, d1])
    arrow(ax, [d1.bottom(), p1.top()], "Yes", 0)
    arrow(ax, [p1.bottom(), d2.top()])
    arrow(ax, [d2.right(), k.left()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [k.top(), (k.x, d1.y), d1.right()])
    arrow(ax, [d2.bottom(), d3.top()], "No (converged early)", 0, dx=0.1, dy=-0.5)
    arrow(ax, [d1.left(), (1.2, d1.y), (1.2, 7.6), (6.0, 7.6)], "No", 0, dx=-0.6)
    arrow(ax, [d3.left(), (neg.x, d3.y), neg.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d3.right(), (ok.x, d3.y), ok.top()], "No", 0, dx=0.2)
    arrow(ax, [neg.bottom(), (neg.x, e.y), e.left()])
    arrow(ax, [ok.bottom(), (ok.x, e.y), e.right()])
    save(fig, "fc_task5_bellman_ford.png")


def fc_task5_floyd():
    fig, ax = canvas(12, 1.8, 16.2, "Task 5.3 - Floyd (all pairs): D(k) computed from D(k−1)")
    s = Node(ax, 6, 15.6, "Start", "terminal", w=2.2)
    i = Node(ax, 6, 14.6, "Input: weight matrix W[1..n][1..n]  (∞ = no edge, 0 on diagonal)", "io", w=8.4)
    p0 = Node(ax, 6, 13.5, "D ← W   (this is D(0));   k ← 1", "process", w=5.2)
    d1 = Node(ax, 6, 12.2, "k ≤ n ?", "decision", w=2.6, h=1.2)
    out = Node(ax, 10.0, 12.2, "Output: D = D(n)", "io", w=3.0)
    e = Node(ax, 10.0, 11.0, "End", "terminal", w=2.0, h=0.7)
    p1 = Node(ax, 6, 10.9, "i ← 1", "process", w=2.0)
    d2 = Node(ax, 6, 9.7, "i ≤ n ?", "decision", w=2.6, h=1.1)
    kk = Node(ax, 2.2, 9.7, "k ← k + 1", "process", w=2.2)
    p2 = Node(ax, 6, 8.5, "j ← 1", "process", w=2.0)
    d3 = Node(ax, 6, 7.3, "j ≤ n ?", "decision", w=2.6, h=1.1)
    ii = Node(ax, 9.9, 7.3, "i ← i + 1", "process", w=2.0)
    d4 = Node(ax, 6, 5.75, "D[i][k] + D[k][j]\n< D[i][j] ?", "decision", w=3.6, h=1.5)
    up = Node(ax, 6, 4.2, "D[i][j] ← D[i][k] + D[k][j]\nnext[i][j] ← next[i][k]", "process", w=4.6, h=1.0)
    jj = Node(ax, 6, 2.8, "j ← j + 1", "process", w=2.2)
    chain(ax, [s, i, p0, d1])
    arrow(ax, [d1.right(), out.left()], "No", 0, dx=0.1, dy=0.15)
    arrow(ax, [out.bottom(), e.top()])
    arrow(ax, [d1.bottom(), p1.top()], "Yes", 0)
    arrow(ax, [p1.bottom(), d2.top()])
    arrow(ax, [d2.left(), kk.right()], "No", 0, dx=-0.6, dy=0.15)
    arrow(ax, [kk.top(), (kk.x, d1.y), d1.left()])
    arrow(ax, [d2.bottom(), p2.top()], "Yes", 0)
    arrow(ax, [p2.bottom(), d3.top()])
    arrow(ax, [d3.right(), ii.left()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [ii.top(), (ii.x, d2.y), d2.right()])
    arrow(ax, [d3.bottom(), d4.top()], "Yes", 0)
    arrow(ax, [d4.bottom(), up.top()], "Yes", 0)
    arrow(ax, [d4.right(), (9.5, d4.y), (9.5, jj.y), jj.right()], "No", 0, dx=0.1)
    arrow(ax, [up.bottom(), jj.top()])
    arrow(ax, [jj.left(), (1.0, jj.y), (1.0, d3.y), d3.left()], "next j", 1, dx=0.1, dy=2.0)
    save(fig, "fc_task5_floyd.png")


# ------------------------------------------------------------------------------------------- Task 6
def fc_task6():
    fig, ax = canvas(20, 2.9, 19.4, "Task 6 - EnergyAwareSchedule: DP over jobs sorted by finish time (left), "
                     "reconstruction (right)")
    s = Node(ax, 5.5, 18.8, "Start", "terminal", w=2.2)
    i = Node(ax, 5.5, 17.8, "Input: n jobs (id, start s, finish f, value v)", "io", w=6.6)
    p1 = Node(ax, 5.5, 16.75, "SORT jobs in ascending order of finish time", "process", w=6.2)
    p2 = Node(ax, 5.5, 15.55, "FOR j ← 1 TO n:  p[j] ← BINARY_SEARCH for the largest\ni < j with f[i] ≤ s[j]"
              "  (0 if none)", "call", w=8.0, h=1.0)
    p3 = Node(ax, 5.5, 14.35, "OPT[0] ← 0;   j ← 1", "process", w=3.6)
    d1 = Node(ax, 5.5, 13.0, "j ≤ n ?", "decision", w=2.6, h=1.2)
    p4 = Node(ax, 5.5, 11.6, "inc ← v[j] + OPT[p[j]]   (job j + best compatible past)\n"
              "exc ← OPT[j − 1]   (schedule without job j)", "process", w=7.6, h=1.0)
    d2 = Node(ax, 5.5, 9.95, "inc > exc ?", "decision", w=3.0, h=1.3)
    ti = Node(ax, 2.5, 8.3, "OPT[j] ← inc\ntake[j] ← TRUE", "process", w=3.0, h=0.9)
    te = Node(ax, 8.5, 8.3, "OPT[j] ← exc\ntake[j] ← FALSE", "process", w=3.0, h=0.9)
    jj = Node(ax, 5.5, 6.9, "j ← j + 1", "process", w=2.2)
    chain(ax, [s, i, p1, p2, p3, d1])
    arrow(ax, [d1.bottom(), p4.top()], "Yes", 0)
    arrow(ax, [p4.bottom(), d2.top()])
    arrow(ax, [d2.left(), (ti.x, d2.y), ti.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d2.right(), (te.x, d2.y), te.top()], "No (tie → exclude)", 0, dx=0.1)
    arrow(ax, [ti.bottom(), (ti.x, jj.y), jj.left()])
    arrow(ax, [te.bottom(), (te.x, jj.y), jj.right()])
    arrow(ax, [jj.bottom(), (5.5, 6.2), (0.4, 6.2), (0.4, d1.y), d1.left()], "next job", 2, dx=0.1, dy=3.0)
    ax.plot([10.9, 10.9], [3.1, 19.2], color="#999999", lw=0.8, ls=":")
    r0 = Node(ax, 15.5, 13.0, "j ← n;   S ← empty list", "process", w=4.0)
    arrow(ax, [d1.right(), r0.left()], "No (all OPT[j] known)", 0, dx=0.2, dy=0.15)
    rd1 = Node(ax, 15.5, 11.6, "j > 0 ?", "decision", w=2.6, h=1.2)
    rd2 = Node(ax, 15.5, 9.95, "take[j] ?", "decision", w=2.8, h=1.3)
    a = Node(ax, 13.2, 8.3, "INSERT job j at front of S\nj ← p[j]", "process", w=3.8, h=0.9)
    b = Node(ax, 18.0, 8.3, "j ← j − 1", "process", w=2.2)
    out = Node(ax, 15.5, 4.9, "Output: selected jobs S,\nmaximum value OPT[n]", "io", w=5.0, h=1.0)
    e = Node(ax, 15.5, 3.6, "End", "terminal", w=2.2)
    arrow(ax, [r0.bottom(), rd1.top()])
    arrow(ax, [rd1.bottom(), rd2.top()], "Yes", 0)
    arrow(ax, [rd2.left(), (a.x, rd2.y), a.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [rd2.right(), (b.x, rd2.y), b.top()], "No", 0, dx=0.2)
    arrow(ax, [a.bottom(), (a.x, 7.1), (11.5, 7.1), (11.5, 12.38), (15.5, 12.38)])
    arrow(ax, [b.bottom(), (b.x, 7.1), (a.x, 7.1)])
    arrow(ax, [rd1.right(), (19.6, rd1.y), (19.6, out.y), out.right()], "No (j = 0)", 0, dx=0.1)
    arrow(ax, [out.bottom(), e.top()])
    save(fig, "fc_task6_energy_schedule.png")


def main():
    fc_task1()
    fc_task2()
    fc_task3()
    fc_task4()
    fc_task5_dijkstra()
    fc_task5_bellman_ford()
    fc_task5_floyd()
    fc_task6()


if __name__ == "__main__":
    main()
