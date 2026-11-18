"""
draw_flowcharts.py - draws the flowcharts of the three search approaches (Task 1).

Problem: Task 1 asks for pseudocode or a flowchart for every approach.  This script draws standard
flowchart symbols with matplotlib (terminal = rounded, process = rectangle, decision = diamond,
input/output = parallelogram, predefined process / recursive call = rectangle with side bars) and
writes flowchart_A_sequential_search.png, flowchart_B_recursive_binary_search.png and
flowchart_C_hash_table.png next to this file.
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
    print(path)


def flowchart_sequential():
    fig, ax = new_canvas(10, 2.6, 14.4, "Approach A - Iterative Sequential Search (no preprocessing)")
    start = Node(ax, 5, 13.6, "Start", "terminal", w=2.2)
    inp = Node(ax, 5, 12.4, "Input: records A[0..n-1] (unsorted), key", "io", w=6.2)
    init = Node(ax, 5, 11.1, "i <- 0", "process", w=2.4)
    d1 = Node(ax, 5, 9.6, "i < n ?", "decision", w=2.8, h=1.3)
    d2 = Node(ax, 5, 7.4, "A[i].reg_no = key ?\n(basic operation)", "decision", w=4.2, h=1.8)
    inc = Node(ax, 8.6, 7.4, "i <- i + 1", "process", w=2.0)
    found = Node(ax, 5.3, 5.3, "Output: return A[i]\n(record found)", "io", w=3.4, h=1.0)
    notf = Node(ax, 1.6, 5.3, "Output: return\nNOT FOUND", "io", w=2.6, h=1.0)
    end = Node(ax, 5.3, 3.9, "End", "terminal", w=2.2)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), d1.top()])
    arrow(ax, [d1.bottom(), d2.top()], "Yes", 0)
    arrow(ax, [d2.right(), inc.left()], "No", 0, dy=0.15)
    arrow(ax, [inc.top(), (inc.x, d1.y), d1.right()])
    arrow(ax, [d1.left(), (notf.x, d1.y), notf.top()], "No", 0, dx=-0.6)
    arrow(ax, [d2.bottom(), (d2.x, 6.2), (found.x, 6.2), found.top()], "Yes", 0)
    arrow(ax, [found.bottom(), end.top()])
    arrow(ax, [notf.bottom(), (notf.x, end.y), end.left()])
    ax.text(5, 2.9, "Successful search at position i: i + 1 comparisons;  unsuccessful: n comparisons",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "flowchart_A_sequential_search.png")


def flowchart_binary():
    fig, ax = new_canvas(11, -0.1, 17.9, "Approach B - Recursive Binary Search (preprocessing: merge sort)")
    start = Node(ax, 5.5, 17.2, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.5, 16.15, "Input: records (unsorted), key", "io", w=5.4)
    pre = Node(ax, 5.5, 15.0, "Preprocessing (once): A <- MergeSort(records by reg_no)\nTheta(n log n)",
               "call", w=7.4, h=1.0)
    call = Node(ax, 5.5, 13.8, "result <- BinSearch(A, key, 0, n-1)", "call", w=5.6)
    out = Node(ax, 5.5, 12.75, "Output: result (record or NOT FOUND)", "io", w=5.6)
    end = Node(ax, 5.5, 11.75, "End", "terminal", w=2.2)
    for a, b in ((start, inp), (inp, pre), (pre, call), (call, out), (out, end)):
        arrow(ax, [a.bottom(), b.top()])
    ax.add_patch(Rectangle((0.25, 0.2), 10.5, 10.85, fill=False, ls="--", lw=1.0, ec="#555555"))
    ax.text(0.45, 10.7, "function BinSearch(A, key, low, high)", fontsize=9, style="italic")
    entry = Node(ax, 5.5, 9.95, "BinSearch(A, key, low, high)", "terminal", w=4.6)
    arrow(ax, [call.right(), (9.6, call.y), (9.6, 10.6), (6.4, 10.6), (6.4, entry.y + entry.h / 2)],
          "first call", 1, dx=0.1, dy=-0.35, dashed=True)
    d1 = Node(ax, 5.5, 8.65, "low > high ?", "decision", w=3.0, h=1.3)
    base = Node(ax, 2.0, 8.65, "return NOT FOUND\n(base case)", "terminal", w=2.8, h=1.0, size=8.5)
    mid = Node(ax, 5.5, 7.25, "mid <- floor((low + high) / 2)", "process", w=3.9)
    d2 = Node(ax, 5.5, 5.65, "key = A[mid].reg_no ?\n(one 3-way comparison)", "decision", w=4.4, h=1.7)
    found = Node(ax, 9.25, 5.65, "return A[mid]\n(found)", "terminal", w=2.4, h=1.0, size=8.5)
    d3 = Node(ax, 5.5, 3.95, "key < A[mid].reg_no ?", "decision", w=4.2, h=1.3)
    left = Node(ax, 2.45, 2.3, "return BinSearch(A, key,\nlow, mid-1)", "call", w=3.6, h=1.0, size=8.5)
    right = Node(ax, 8.55, 2.3, "return BinSearch(A, key,\nmid+1, high)", "call", w=3.6, h=1.0, size=8.5)
    arrow(ax, [entry.bottom(), d1.top()])
    arrow(ax, [d1.left(), base.right()], "Yes", 0, dx=-0.55, dy=0.15)
    arrow(ax, [d1.bottom(), mid.top()], "No", 0)
    arrow(ax, [mid.bottom(), d2.top()])
    arrow(ax, [d2.right(), found.left()], "Yes", 0, dx=0.02, dy=0.15)
    arrow(ax, [d2.bottom(), d3.top()], "No", 0)
    arrow(ax, [d3.left(), (left.x, d3.y), left.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d3.right(), (right.x, d3.y), right.top()], "No", 0, dx=0.2)
    arrow(ax, [left.left(), (0.45, left.y), (0.45, entry.y), entry.left()], "recursive call", 1,
          dx=0.1, dy=1.2, dashed=True)
    arrow(ax, [right.right(), (10.55, right.y), (10.55, entry.y), entry.right()], dashed=True)
    ax.text(5.5, 0.75, "exactly ONE recursive call per activation, on a half of size <= floor(n/2)",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "flowchart_B_recursive_binary_search.png")


def flowchart_hash():
    fig, ax = new_canvas(16, 1.2, 14.5,
                         "Approach C - Hash Table with Separate Chaining (build once, then search)")
    ax.text(3.2, 13.9, "Preprocessing: Build(records)", ha="center", fontsize=10, fontweight="bold")
    ax.text(11.2, 13.9, "Search(T, key)", ha="center", fontsize=10, fontweight="bold")
    b0 = Node(ax, 3.2, 13.0, "Start", "terminal", w=2.2)
    b1 = Node(ax, 3.2, 11.7, "m <- smallest prime >= n / 0.75\nT[0..m-1] <- empty chains", "process",
              w=5.0, h=1.0)
    b2 = Node(ax, 3.2, 10.0, "another record r ?", "decision", w=3.8, h=1.4)
    b3 = Node(ax, 3.2, 8.3, "j <- r.reg_no mod m\n(one hash computation)", "process", w=4.4, h=1.0)
    b4 = Node(ax, 3.2, 6.8, "append r to chain T[j]\n(replace if the key is already there)", "process",
              w=5.0, h=1.0)
    b5 = Node(ax, 3.2, 4.9, "End: table T ready\n(alpha = n / m <= 0.75)", "terminal", w=4.4, h=1.0)
    arrow(ax, [b0.bottom(), b1.top()])
    arrow(ax, [b1.bottom(), b2.top()])
    arrow(ax, [b2.bottom(), b3.top()], "Yes", 0)
    arrow(ax, [b3.bottom(), b4.top()])
    arrow(ax, [b4.left(), (0.3, b4.y), (0.3, b2.y), b2.left()])
    arrow(ax, [b2.right(), (5.95, b2.y), (5.95, b5.y), b5.right()], "No", 0, dx=0.05)

    s0 = Node(ax, 11.2, 13.0, "Start", "terminal", w=2.2)
    s1 = Node(ax, 11.2, 11.7, "j <- key mod m\n(one hash computation)", "process", w=4.2, h=1.0)
    s2 = Node(ax, 11.2, 10.3, "p <- first record of chain T[j]", "process", w=4.6)
    s3 = Node(ax, 11.2, 8.9, "p = null ?", "decision", w=2.8, h=1.3)
    s4 = Node(ax, 11.2, 6.9, "p.reg_no = key ?\n(basic operation)", "decision", w=3.6, h=1.7)
    s5 = Node(ax, 7.4, 6.9, "p <- next record\nin the chain", "process", w=2.4, h=1.0, size=8.5)
    s6 = Node(ax, 11.2, 4.9, "Output: return p\n(found)", "io", w=3.0, h=1.0)
    s7 = Node(ax, 14.4, 4.9, "Output: return\nNOT FOUND", "io", w=2.5, h=1.0)
    s8 = Node(ax, 12.8, 3.2, "End", "terminal", w=2.2)
    arrow(ax, [s0.bottom(), s1.top()])
    arrow(ax, [s1.bottom(), s2.top()])
    arrow(ax, [s2.bottom(), s3.top()])
    arrow(ax, [s3.bottom(), s4.top()], "No", 0)
    arrow(ax, [s3.right(), (s7.x, s3.y), s7.top()], "Yes", 0)
    arrow(ax, [s4.left(), s5.right()], "No", 0, dx=-0.65, dy=0.15)
    arrow(ax, [s5.top(), (s5.x, s3.y), s3.left()])
    arrow(ax, [s4.bottom(), s6.top()], "Yes", 0)
    arrow(ax, [s6.bottom(), (s6.x, s8.y), s8.left()])
    arrow(ax, [s7.bottom(), (s7.x, s8.y), s8.right()])
    ax.text(8, 1.8, "Expected key comparisons: successful 1 + alpha/2, unsuccessful alpha  ->  Theta(1) when "
            "alpha <= 0.75;  worst case (all keys in one chain): n", ha="center", fontsize=8.5, style="italic")
    save(fig, "flowchart_C_hash_table.png")


def main():
    flowchart_sequential()
    flowchart_binary()
    flowchart_hash()


if __name__ == "__main__":
    main()
