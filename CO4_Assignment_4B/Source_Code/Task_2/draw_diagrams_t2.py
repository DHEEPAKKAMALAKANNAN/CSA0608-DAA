"""
draw_diagrams_t2.py - flowcharts and diagrams for Task 2 (greedy vs DP knapsack), written to Report/Screenshots/.

  t2_flowchart_fractional_greedy.png   Solution A - fractional knapsack greedy
  t2_flowchart_01_dp.png               Solution B - 0/1 knapsack DP with trace-back
  t2_counterexample_loads.png          the student counter-example: what the greedy loads vs what the DP loads,
                                       and the DP table best[i][c] as a heat map with the trace-back path
All numbers are computed by knapsack_engines.py at drawing time.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

import knapsack_engines as ks  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "Report", "Screenshots"))
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
    """Polyline through points with an arrow head at the end; optional label near a vertex."""
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
    print(path)


# ----------------------------------------------------------------------------- figures
def flowchart_fractional():
    fig, ax = new_canvas(13, 1.0, 16.6, "Solution A - Fractional Knapsack (greedy by value/weight)")
    start = Node(ax, 5.0, 16.0, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.0, 14.9, "Input: items (id, w, v), capacity W", "io", w=5.6)
    val = Node(ax, 5.0, 13.6, "W >= 0 and all w > 0,\nv >= 0 ?", "decision", w=4.2, h=1.4)
    err = Node(ax, 10.6, 13.6, "Output: reject input\n(ValueError)", "io", w=3.6, h=1.0)
    sort = Node(ax, 5.0, 12.1, "MergeSort items by v/w (decreasing)\n~ n log2 n comparisons", "call", w=5.6, h=1.0)
    init = Node(ax, 5.0, 10.8, "room <- W;  total <- 0;  k <- 1", "process", w=4.8)
    d_more = Node(ax, 5.0, 9.4, "k <= n and room > 0 ?", "decision", w=4.4, h=1.3)
    d_fit = Node(ax, 5.0, 7.6, "w_k <= room ?", "decision", w=3.2, h=1.3)
    whole = Node(ax, 1.9, 5.9, "take item k whole:\nroom -= w_k; total += v_k", "process", w=3.6, h=1.0, size=8.5)
    frac = Node(ax, 8.1, 5.9, "take fraction f = room / w_k:\ntotal += f * v_k; room <- 0", "process", w=4.2, h=1.0,
                size=8.5)
    inc = Node(ax, 5.0, 4.4, "record decision;  k <- k + 1", "process", w=4.2)
    out = Node(ax, 10.6, 9.4, "Output: total value,\nitems / fractions,\ndecision trace", "io", w=3.6, h=1.3)
    end = Node(ax, 10.6, 7.6, "End", "terminal", w=2.2)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), val.top()])
    arrow(ax, [val.right(), err.left()], "No", 0, dx=0.1)
    arrow(ax, [val.bottom(), sort.top()], "Yes", 0)
    arrow(ax, [sort.bottom(), init.top()])
    arrow(ax, [init.bottom(), d_more.top()])
    arrow(ax, [d_more.bottom(), d_fit.top()], "Yes", 0)
    arrow(ax, [d_more.right(), out.left()], "No", 0, dx=0.1)
    arrow(ax, [out.bottom(), end.top()])
    arrow(ax, [d_fit.left(), (whole.x, d_fit.y), whole.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d_fit.right(), (frac.x, d_fit.y), frac.top()], "No", 0, dx=0.1)
    arrow(ax, [whole.bottom(), (whole.x, inc.y), inc.left()])
    arrow(ax, [frac.bottom(), (frac.x, inc.y), inc.right()])
    arrow(ax, [inc.bottom(), (5.0, 3.6), (0.2, 3.6), (0.2, d_more.y), d_more.left()])
    ax.text(6.5, 2.4, "Greedy choice: the densest remaining item first.  Work Theta(n log n), memory Theta(n),\n"
            "independent of W.  Optimal for divisible items; applied to 0/1 items it can fail (Task 2.2).",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "t2_flowchart_fractional_greedy.png")


def flowchart_dp():
    fig, ax = new_canvas(14, 0.6, 17.6, "Solution B - 0/1 Knapsack by Dynamic Programming")
    start = Node(ax, 5.5, 17.0, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.5, 15.9, "Input: items (id, w, v), capacity W", "io", w=5.6)
    init = Node(ax, 5.5, 14.7, "best[0][c] <- 0 for c = 0..W;  i <- 1", "process", w=5.6)
    d_i = Node(ax, 5.5, 13.3, "i <= n ?", "decision", w=2.6, h=1.2)
    c0 = Node(ax, 5.5, 11.9, "c <- 0", "process", w=2.2)
    d_c = Node(ax, 5.5, 10.5, "c <= W ?", "decision", w=2.6, h=1.2)
    skip = Node(ax, 5.5, 9.1, "best[i][c] <- best[i-1][c]   (leave item i)", "process", w=6.0)
    d_w = Node(ax, 5.5, 7.6, "w_i <= c and best[i-1][c-w_i]\n+ v_i > best[i][c] ?", "decision", w=5.6, h=1.6)
    take = Node(ax, 5.5, 5.9, "best[i][c] <- best[i-1][c-w_i] + v_i  (take i)", "process", w=6.2)
    inc_c = Node(ax, 5.5, 4.7, "c <- c + 1", "process", w=2.4)
    inc_i = Node(ax, 11.3, 10.5, "i <- i + 1", "process", w=2.4)
    tb = Node(ax, 11.3, 13.3, "Trace back from best[n][W]:\nitem i taken iff\nbest[i][c] != best[i-1][c]",
              "call", w=4.4, h=1.5, size=8.5)
    out = Node(ax, 11.3, 7.0, "Output: optimum,\nselected items, table", "io", w=4.0, h=1.0)
    end = Node(ax, 11.3, 5.5, "End", "terminal", w=2.2)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), d_i.top()])
    arrow(ax, [d_i.bottom(), c0.top()], "Yes", 0)
    arrow(ax, [c0.bottom(), d_c.top()])
    arrow(ax, [d_c.bottom(), skip.top()], "Yes", 0)
    arrow(ax, [skip.bottom(), d_w.top()])
    arrow(ax, [d_w.bottom(), take.top()], "Yes", 0)
    arrow(ax, [take.bottom(), inc_c.top()])
    arrow(ax, [d_w.left(), (1.6, d_w.y), (1.6, inc_c.y), inc_c.left()], "No", 0, dx=-0.6)
    arrow(ax, [inc_c.bottom(), (5.5, 3.9), (0.6, 3.9), (0.6, d_c.y), d_c.left()])
    arrow(ax, [d_c.right(), inc_i.left()], "No", 0, dx=0.1)
    arrow(ax, [inc_i.top(), (inc_i.x, 11.6), (8.4, 11.6), (8.4, 14.05), (d_i.x, 14.05)])
    arrow(ax, [d_i.right(), tb.left()], "No", 0, dx=0.15, dy=-0.4)
    arrow(ax, [tb.right(), (13.8, tb.y), (13.8, out.y), out.right()])
    arrow(ax, [out.bottom(), end.top()])
    ax.text(7.0, 2.2, "Work: n (W + 1) cells, each O(1)  ->  Theta(n W) (pseudo-polynomial);  memory (n + 1)(W + 1)\n"
            "cells with item reconstruction, or W + 1 cells for the value only.  Always optimal for 0/1.",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "t2_flowchart_01_dp.png")


def counterexample_figure():
    with open(os.path.join(HERE, "test_data", "counterexample.json"), encoding="utf-8") as f:
        spec = json.load(f)
    items, cap = [ks.Item(*r) for r in spec["items"]], spec["capacity"]
    g_value, g_chosen, _ = ks.greedy_01_ratio(items, cap)
    best, chosen, table = ks.knapsack_01_dp(items, cap, keep_table=True)
    colors = {"C1": "#d62728", "C2": "#1f77b4", "C3": "#3182bd", "C4": "#2ca02c", "C5": "#9467bd"}
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    for row, (label, load, value) in enumerate((("Greedy (v/w)", g_chosen, g_value), ("DP optimum", chosen, best))):
        y, x = 1 - row * 1.3, 0
        for it in load:
            ax.add_patch(Rectangle((x, y), it.weight, 0.6, facecolor=colors[it.item_id], edgecolor="black"))
            ax.text(x + it.weight / 2, y + 0.3, f"{it.item_id}\n{it.weight} kg, {it.value}", ha="center",
                    va="center", fontsize=8 if it.weight >= 6 else 6.5, color="white", fontweight="bold")
            x += it.weight
        if x < cap:
            ax.add_patch(Rectangle((x, y), cap - x, 0.6, facecolor="white", edgecolor="grey", hatch="///"))
            ax.text(x + (cap - x) / 2, y + 0.75, f"{cap - x} kg unused", ha="center", fontsize=8)
        ax.text(-1, y + 0.3, f"{label}\nvalue {value}", ha="right", va="center", fontsize=9.5, fontweight="bold")
    ax.axvline(cap, color="red", lw=1.5)
    ax.text(cap, -0.45, f"W = {cap} kg", color="red", ha="center")
    ax.set_xlim(-12, cap + 2)
    ax.set_ylim(-0.6, 2.0)
    ax.axis("off")
    ax.set_title("Vehicle loads: committing to C1 (ratio 5.0) wastes 6 kg", fontsize=10.5, fontweight="bold")
    ax = axes[1]
    im = ax.imshow(table, aspect="auto", cmap="Blues", origin="upper")
    ax.set_yticks(range(len(items) + 1), ["0 (none)"] + [f"{i + 1} ({it.item_id})" for i, it in enumerate(items)])
    ax.set_xlabel("capacity c (kg)")
    ax.set_ylabel("items considered i")
    c, path = cap, []
    for i in range(len(items), 0, -1):
        taken = table[i][c] != table[i - 1][c]
        path.append((i, c, taken))
        if taken:
            c -= items[i - 1].weight
    path.append((0, c, False))
    for i, c, taken in path:
        ax.plot(c, i, "o", ms=10, mfc="orange" if taken else "none", mec="darkorange", mew=2)
        ax.text(c - 0.8, i - 0.2, f"{table[i][c]}", fontsize=8, color="black", fontweight="bold", ha="right")
    fig.colorbar(im, ax=ax, label="best[i][c] (value)")
    ax.set_title("DP table best[i][c]; circles = trace-back from best[5][40] = 192 (filled = item taken)",
                 fontsize=10.5, fontweight="bold")
    fig.tight_layout()
    save(fig, "t2_counterexample_loads.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    flowchart_fractional()
    flowchart_dp()
    counterexample_figure()


if __name__ == "__main__":
    main()
