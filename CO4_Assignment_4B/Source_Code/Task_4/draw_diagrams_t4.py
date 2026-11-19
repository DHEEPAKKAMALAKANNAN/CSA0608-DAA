"""
draw_diagrams_t4.py - flowchart and station diagrams for Task 4 (assembly-line scheduling), to Report/Screenshots/.

  t4_flowchart_assembly_line.png   flowchart of the DP + route reconstruction
  t4_line_diagram.png              the two lines with station times, transfer arcs, f values and the optimal
                                   route highlighted: baseline, after the 4.3 transfer change, after the 4.4
                                   slowdown (three panels)
  t4_three_line_state.png          4.5: the transitions that feed one DP state when a third line exists
All values are computed by assembly_line_dp.py at drawing time.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

import assembly_line_dp as al  # noqa: E402
from assembly_line_demo import load_instance  # noqa: E402

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
def flowchart():
    fig, ax = new_canvas(15.2, 0.8, 17.2, "Assembly Line Scheduling - DP over stations (two lines)")
    start = Node(ax, 5.2, 16.6, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.2, 15.5, "Input: a1[1..n], a2[1..n], t1, t2 [1..n-1], e1, e2, x1, x2", "io", w=8.2)
    val = Node(ax, 5.2, 14.1, "lengths consistent and\nall times >= 0 ?", "decision", w=4.4, h=1.4)
    err = Node(ax, 12.4, 14.1, "Output: reject\n(ValueError)", "io", w=3.0, h=1.0)
    init = Node(ax, 5.2, 12.6, "f1[1] <- e1 + a1[1];  f2[1] <- e2 + a2[1];  j <- 2", "process", w=7.0)
    d_j = Node(ax, 5.2, 11.2, "j <= n ?", "decision", w=2.6, h=1.2)
    calc = Node(ax, 5.2, 9.6, "stay1 = f1[j-1] + a1[j];  trans1 = f2[j-1] + t2[j-1] + a1[j]\n"
                "stay2 = f2[j-1] + a2[j];  trans2 = f1[j-1] + t1[j-1] + a2[j]", "process", w=8.4, h=1.1, size=8.5)
    d_1 = Node(ax, 5.2, 7.9, "stay1 <= trans1 ?", "decision", w=3.6, h=1.2)
    s1 = Node(ax, 2.0, 6.4, "f1[j] <- stay1\npred1[j] <- 1", "process", w=2.8, h=1.0, size=8.5)
    t1 = Node(ax, 8.4, 6.4, "f1[j] <- trans1\npred1[j] <- 2", "process", w=2.8, h=1.0, size=8.5)
    same2 = Node(ax, 5.2, 4.9, "same decision for line 2 -> f2[j], pred2[j];\nrecord row of the decision table;  "
                 "j <- j + 1", "process", w=7.4, h=1.0, size=8.5)
    exitn = Node(ax, 12.4, 11.2, "f* = min(f1[n] + x1,\nf2[n] + x2); last line", "process", w=3.6, h=1.1, size=8.5)
    rec = Node(ax, 12.4, 9.0, "Reconstruct backwards:\nline <- pred_line[j]\nfor j = n .. 2", "call", w=3.6, h=1.4,
               size=8.5)
    out = Node(ax, 12.4, 6.9, "Output: f*, line per\nstation, transfers,\narrow route", "io", w=3.6, h=1.3, size=8.5)
    end = Node(ax, 12.4, 5.2, "End", "terminal", w=2.2)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), val.top()])
    arrow(ax, [val.right(), err.left()], "No", 0, dx=0.1)
    arrow(ax, [val.bottom(), init.top()], "Yes", 0)
    arrow(ax, [init.bottom(), d_j.top()])
    arrow(ax, [d_j.bottom(), calc.top()], "Yes", 0)
    arrow(ax, [calc.bottom(), d_1.top()])
    arrow(ax, [d_1.left(), (s1.x, d_1.y), s1.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d_1.right(), (t1.x, d_1.y), t1.top()], "No", 0, dx=0.1)
    arrow(ax, [s1.bottom(), (s1.x, 5.6), (4.0, 5.6), (4.0, same2.y + 0.5)])
    arrow(ax, [t1.bottom(), (t1.x, 5.6), (6.4, 5.6), (6.4, same2.y + 0.5)])
    arrow(ax, [same2.bottom(), (5.2, 3.9), (0.3, 3.9), (0.3, d_j.y), d_j.left()])
    arrow(ax, [d_j.right(), exitn.left()], "No", 0, dx=0.15)
    arrow(ax, [exitn.bottom(), rec.top()])
    arrow(ax, [rec.bottom(), out.top()])
    arrow(ax, [out.bottom(), end.top()])
    ax.text(6.8, 2.3, "Optimal substructure: the fastest way through station j on a line uses the fastest way through\n"
            "station j-1 on one of the two lines.  2 comparisons per station -> Theta(n) time, Theta(n) memory.",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "t4_flowchart_assembly_line.png")


def draw_lines(ax, inst, sched, title, highlight=None):
    n = inst.n
    ys = {1: 1.6, 2: 0.0}
    on_route = set(sched.route)
    ax.text(-0.9, 0.8, f"entry\ne1={inst.e[0]}\ne2={inst.e[1]}", ha="center", va="center", fontsize=7.5)
    ax.text(n + 0.9, 0.8, f"exit\nx1={inst.x[0]}\nx2={inst.x[1]}", ha="center", va="center", fontsize=7.5)
    for line in (1, 2):
        for j in range(1, n + 1):
            active = (j, line) in on_route
            bad = highlight == (j, line)
            ax.add_patch(FancyBboxPatch((j - 0.32, ys[line] - 0.28), 0.64, 0.56, boxstyle="round,pad=0.02",
                                        facecolor="#c6e2c3" if active else "#f2f2f2",
                                        edgecolor="red" if bad else ("#2e7d32" if active else "#999999"),
                                        lw=2.4 if bad or active else 0.8))
            ax.text(j, ys[line] + 0.06, f"{inst.a[line - 1][j - 1]}", ha="center", va="center", fontsize=10,
                    fontweight="bold")
            f = sched.f[line - 1][j - 1]
            ax.text(j, ys[line] - 0.17, f"f={f}", ha="center", va="center", fontsize=6.5, color="#555555")
            if j < n:
                ax.plot([j + 0.32, j + 0.68], [ys[line]] * 2, color="#999999", lw=0.8)
        ax.text(0.2, ys[line], f"Line {line}", ha="right", va="center", fontsize=9, fontweight="bold")
    for j in range(1, n):                           # transfer arcs with their times
        ax.annotate("", xy=(j + 0.75, ys[2] + 0.3), xytext=(j + 0.25, ys[1] - 0.3),
                    arrowprops=dict(arrowstyle="->", color="#bbbbbb", lw=0.7))
        ax.annotate("", xy=(j + 0.75, ys[1] - 0.3), xytext=(j + 0.25, ys[2] + 0.3),
                    arrowprops=dict(arrowstyle="->", color="#bbbbbb", lw=0.7))
        ax.text(j + 0.5, ys[1] - 0.48, f"{inst.t[0][j - 1]}", ha="center", fontsize=6.5, color="#1f77b4")
        ax.text(j + 0.5, ys[2] + 0.42, f"{inst.t[1][j - 1]}", ha="center", fontsize=6.5, color="#d62728")
    pts = [(-0.5, 0.8)] + [(s, ys[l]) for s, l in sched.route] + [(n + 0.5, 0.8)]
    xs, yv = zip(*pts)
    ax.plot(xs, yv, color="#2e7d32", lw=2.6, alpha=0.75, zorder=0)
    for s, a_line, b_line, tt in sched.transfers:
        ax.text(s + 0.5, 0.8, f"T+{tt}", ha="center", va="center", fontsize=8, fontweight="bold", color="#2e7d32",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="#2e7d32"))
    for j in range(1, n + 1):
        ax.text(j, 2.15, f"S{j}", ha="center", fontsize=8.5)
    ax.set_xlim(-1.5, n + 1.5)
    ax.set_ylim(-0.6, 2.45)
    ax.axis("off")
    ax.set_title(f"{title}: minimum time {sched.min_time}", fontsize=10.5, fontweight="bold")


def line_diagram(inst):
    with open(os.path.join(HERE, "test_data", "change_predictions.json"), encoding="utf-8") as f:
        pred = json.load(f)
    variants = [("Baseline (4.1)", inst, None)]
    for key, title in (("task_4_3", "4.3: transfer L1->L2 after S2 raised 2 -> 12"),
                       ("task_4_4", "4.4: line 2 station 4 slowed 3 -> 12")):
        change = {k: {int(s): v for s, v in e.items()} for k, e in pred[key]["change"].items()}
        mark = None
        if "a2" in change:
            mark = (next(iter(change["a2"])), 2)
        variants.append((title, inst.copy_with(**change), mark))
    fig, axes = plt.subplots(3, 1, figsize=(11, 9.6))
    for ax, (title, case, mark) in zip(axes, variants):
        draw_lines(ax, case, al.schedule(case), title, mark)
    fig.suptitle("Two-line station diagram: box = processing time (f = DP value), small numbers = transfer times\n"
                 "(blue L1->L2, red L2->L1); green = optimal route, T = transfer point", fontsize=10.5)
    save(fig, "t4_line_diagram.png")


def three_line_state():
    fig, ax = plt.subplots(figsize=(9, 3.9))
    ys = {1: 2.0, 2: 1.0, 3: 0.0}
    for line, y in ys.items():
        for j, x in ((1, 1.0), (2, 4.5)):
            target = j == 2 and line == 2
            ax.add_patch(FancyBboxPatch((x - 0.7, y - 0.3), 1.4, 0.6, boxstyle="round,pad=0.02",
                                        facecolor="#fde3cf" if target else "#eef3f8",
                                        edgecolor="#c55a11" if target else "#888888", lw=1.6 if target else 0.8))
            ax.text(x, y, f"f[{line}][j{'-1' if j == 1 else ''}]", ha="center", va="center", fontsize=9)
        ax.text(-0.3, y, f"Line {line}", ha="right", va="center", fontsize=9, fontweight="bold")
    for line, y in ys.items():
        label = "+ a[2][j]  (stay)" if line == 2 else f"+ t[{line}->2][j-1] + a[2][j]"
        ax.annotate("", xy=(3.8, 1.0), xytext=(1.7, y), arrowprops=dict(arrowstyle="-|>", color="#c55a11", lw=1.4))
        ax.text(2.3, (y + 1.0) / 2 + (0.18 if line != 3 else -0.18), label, fontsize=8, color="#7f3f00")
    ax.text(7.6, 1.0, "f[2][j] = min over k in {1,2,3} of\n  f[k][j-1] + t[k->2][j-1] + a[2][j]\n"
            "(t[2->2] = 0)\npred[2][j] = the minimising k", va="center", fontsize=8.5,
            bbox=dict(boxstyle="round", fc="#fff2cc", ec="#999999"))
    ax.set_xlim(-1.3, 10.6)
    ax.set_ylim(-0.6, 2.6)
    ax.axis("off")
    ax.set_title("4.5 - with three lines every state has three incoming transitions (k lines: k)", fontsize=10.5,
                 fontweight="bold")
    save(fig, "t4_three_line_state.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    inst = load_instance()
    flowchart()
    line_diagram(inst)
    three_line_state()


if __name__ == "__main__":
    main()
