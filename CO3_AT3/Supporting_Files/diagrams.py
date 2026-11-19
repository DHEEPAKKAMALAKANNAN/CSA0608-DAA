"""SwiftLogix CO3 case study - flowcharts and divide/conquer/combine diagrams for the reports.

Part 2 (one flowchart per module, standard symbols: terminal = rounded box, process = rectangle,
decision = diamond with Yes/No labels, input/output = parallelogram, predefined process / recursive
call = rectangle with side bars):
  flow_m1_merge_sort, flow_m2_quick_sort, flow_m3_binary_search, flow_m4_strassen
Part 3 (decomposition of the GIVEN sample datasets, recomputed here and checked):
  m1_merge_sort_recursion_tree   divide / base / combine tree of the 12 shipment events (30 comparisons)
  m2_quick_sort_partition_tree   Lomuto partition tree of the 12 priority scores (32 comparisons)
  m3_binary_search_intervals     shrinking search interval for queries Q8 (present) and Q5 (absent)
  m4_strassen_blocks             2 x 2 block quadrants of the 4 x 4 matrices, M1-M7 and the combine step
Output: ../Final_Design_and_Analysis/diagrams/*.png        Run: py -3 diagrams.py
"""
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE / "datasets"
OUT_DIR = HERE.parent / "Final_Design_and_Analysis" / "diagrams"
FILL = {"terminal": "#d9ead3", "process": "#dbe8f6", "decision": "#fff2cc", "io": "#e8dff5",
        "call": "#fde3cf"}


# --------------------------------------------------------------------------- flowchart helpers
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
    """Blank axes in flowchart units (1 unit = 0.62 inch)."""
    fig, ax = plt.subplots(figsize=(width * 0.62, (y_high - y_low) * 0.62))
    ax.set_xlim(0, width)
    ax.set_ylim(y_low, y_high)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold")
    return fig, ax


def save(fig, name):
    """Write the figure as a 150-dpi PNG into Report/diagrams and print its path."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(path)


def divider(ax, x, y0, y1):
    ax.plot([x, x], [y0, y1], color="#999999", lw=0.8, ls=":")


# --------------------------------------------------------------------------- sample data (given datasets)
def load_events():
    with open(DATA / "m1_shipment_events_sample.csv", newline="", encoding="utf-8") as fh:
        return [(r["event_id"], (r["delivery_date"], r["event_time"])) for r in csv.DictReader(fh)]


def load_scores():
    with open(DATA / "m2_priority_scores_sample.csv", newline="", encoding="utf-8") as fh:
        return [int(r["priority_score"]) for r in csv.DictReader(fh)]


def load_index():
    with open(DATA / "m3_tracking_index_sample.csv", newline="", encoding="utf-8") as fh:
        return [r["tracking_id"] for r in csv.DictReader(fh)]


def load_matrices():
    with open(DATA / "m4_route_matrices_sample.json", encoding="utf-8") as fh:
        data = json.load(fh)
    return data["demand_D"]["matrix"], data["cost_C"]["matrix"]


# --------------------------------------------------------------------------- Part 2 flowcharts
def flowchart_merge_sort():
    fig, ax = new_canvas(19.4, 3.0, 15.4, "Module 1 - Merge Sort: MergeSort (left) and Merge (right)")
    divider(ax, 9.1, 3.4, 14.6)
    c = 4.3
    entry = Node(ax, c, 14.2, "MergeSort(A, lo, hi)", "terminal", w=4.2)
    d = Node(ax, c, 12.9, "hi - lo <= 1 ?", "decision", w=3.0, h=1.2)
    base = Node(ax, 7.5, 12.9, "return\n(base case)", "terminal", w=2.0, h=0.9, size=8.5)
    mid = Node(ax, c, 11.5, "mid <- floor((lo + hi) / 2)", "process", w=4.2)
    cl = Node(ax, c, 10.3, "MergeSort(A, lo, mid)", "call", w=4.0)
    cr = Node(ax, c, 9.1, "MergeSort(A, mid, hi)", "call", w=4.0)
    mg = Node(ax, c, 7.9, "Merge(A, lo, mid, hi)", "call", w=4.0)
    ret = Node(ax, c, 6.7, "return", "terminal", w=2.0)
    for node, tag in ((mid, "DIVIDE"), (cl, "CONQUER"), (mg, "COMBINE")):
        ax.text(node.x + node.w / 2, node.y + node.h / 2 + 0.04, tag, fontsize=7.5, color="#1f3864",
                fontweight="bold", ha="right", va="bottom")
    arrow(ax, [entry.bottom(), d.top()])
    arrow(ax, [d.right(), base.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d.bottom(), mid.top()], "No", 0)
    for a, b in ((mid, cl), (cl, cr), (cr, mg), (mg, ret)):
        arrow(ax, [a.bottom(), b.top()])
    arrow(ax, [cl.left(), (0.5, cl.y), (0.5, entry.y), entry.left()], "recursive", 1, dx=0.1, dy=-1.4,
          dashed=True)
    arrow(ax, [cr.left(), (0.5, cr.y), (0.5, cl.y)], dashed=True)
    ax.text(c, 5.6, "C(n) = C(ceil(n/2)) + C(floor(n/2)) + (n - 1)\n-> Theta(n log n), stable",
            ha="center", va="top", fontsize=8.5, style="italic")
    c2 = 12.6
    e2 = Node(ax, c2, 14.2, "Merge(A, lo, mid, hi)", "terminal", w=4.2)
    arrow(ax, [mg.right(), (8.8, mg.y), (8.8, 14.2), e2.left()], dashed=True)
    init = Node(ax, c2, 13.0, "Aux[lo..hi-1] <- A[lo..hi-1];  i <- lo;  j <- mid;  k <- lo", "process",
                w=6.0, size=8)
    dk = Node(ax, c2, 11.7, "k <= hi - 1 ?", "decision", w=2.8, h=1.1)
    rk = Node(ax, 17.0, 11.7, "return", "terminal", w=1.8)
    d1 = Node(ax, c2, 10.4, "i >= mid ?", "decision", w=2.6, h=1.0, size=8.5)
    d2 = Node(ax, c2, 9.1, "j >= hi ?", "decision", w=2.6, h=1.0, size=8.5)
    d3 = Node(ax, c2, 7.6, "key(Aux[j]) < key(Aux[i]) ?\n(basic operation)", "decision", w=4.6, h=1.6, size=8)
    a1 = Node(ax, 16.8, 10.4, "A[k] <- Aux[j];  j <- j + 1", "process", w=3.4, size=8)
    a2 = Node(ax, 16.8, 9.1, "A[k] <- Aux[i];  i <- i + 1", "process", w=3.4, size=8)
    a3 = Node(ax, 16.8, 7.6, "A[k] <- Aux[j];  j <- j + 1", "process", w=3.4, size=8)
    a4 = Node(ax, c2, 6.0, "A[k] <- Aux[i];  i <- i + 1\n(tie -> LEFT run first = stable)", "process", w=4.4,
              h=0.9, size=8)
    kinc = Node(ax, 16.0, 4.8, "k <- k + 1", "process", w=2.0)
    arrow(ax, [e2.bottom(), init.top()])
    arrow(ax, [init.bottom(), dk.top()])
    arrow(ax, [dk.right(), rk.left()], "No", 0, dy=0.15)
    arrow(ax, [dk.bottom(), d1.top()], "Yes", 0)
    arrow(ax, [d1.right(), a1.left()], "Yes", 0, dy=0.12)
    arrow(ax, [d1.bottom(), d2.top()], "No", 0)
    arrow(ax, [d2.right(), a2.left()], "Yes", 0, dy=0.12)
    arrow(ax, [d2.bottom(), d3.top()], "No", 0)
    arrow(ax, [d3.right(), a3.left()], "Yes", 0, dx=0.0, dy=0.12)
    arrow(ax, [d3.bottom(), a4.top()], "No", 0)
    for a in (a1, a2, a3):
        ax.plot([a.x + a.w / 2, 18.8], [a.y, a.y], color="#333333", lw=1.2)
    arrow(ax, [(18.8, a1.y), (18.8, kinc.y), kinc.right()])
    arrow(ax, [a4.bottom(), (c2, kinc.y), kinc.left()])
    arrow(ax, [kinc.bottom(), (kinc.x, 4.1), (9.6, 4.1), (9.6, dk.y), dk.left()])
    ax.text(c2 + 1.6, 3.5, "at most hi - lo - 1 key comparisons, 2(hi - lo) moves per merge", ha="center",
            fontsize=8.5, style="italic")
    save(fig, "flow_m1_merge_sort.png")


def flowchart_quick_sort():
    fig, ax = new_canvas(19.0, 4.2, 15.4, "Module 2 - Quick Sort: QuickSort (left) and Lomuto Partition, "
                         "pivot = last element (right)")
    divider(ax, 8.9, 4.6, 14.6)
    c = 4.3
    entry = Node(ax, c, 14.2, "QuickSort(A, lo, hi)", "terminal", w=4.2)
    d = Node(ax, c, 12.9, "lo < hi ?", "decision", w=2.6, h=1.1)
    base = Node(ax, 7.4, 12.9, "return\n(size 0 or 1)", "terminal", w=2.2, h=0.9, size=8.5)
    part = Node(ax, c, 11.5, "p <- Partition(A, lo, hi)", "call", w=4.2)
    cl = Node(ax, c, 10.3, "QuickSort(A, lo, p - 1)", "call", w=4.2)
    cr = Node(ax, c, 9.1, "QuickSort(A, p + 1, hi)", "call", w=4.2)
    ret = Node(ax, c, 7.8, "return  (COMBINE: nothing,\nsorted in place)", "terminal", w=4.2, h=0.9, size=8.5)
    for node, tag in ((part, "DIVIDE"), (cl, "CONQUER")):
        ax.text(node.x + node.w / 2, node.y + node.h / 2 + 0.04, tag, fontsize=7.5, color="#1f3864",
                fontweight="bold", ha="right", va="bottom")
    arrow(ax, [entry.bottom(), d.top()])
    arrow(ax, [d.right(), base.left()], "No", 0, dy=0.15)
    arrow(ax, [d.bottom(), part.top()], "Yes", 0)
    for a, b in ((part, cl), (cl, cr), (cr, ret)):
        arrow(ax, [a.bottom(), b.top()])
    arrow(ax, [cl.left(), (0.5, cl.y), (0.5, entry.y), entry.left()], "recursive", 1, dx=0.1, dy=-1.4,
          dashed=True)
    arrow(ax, [cr.left(), (0.5, cr.y), (0.5, cl.y)], dashed=True)
    ax.text(c, 6.9, "best/average T(n) = 2T(n/2) + n - 1;\nworst (sorted input) T(n) = T(n-1) + n - 1",
            ha="center", va="top", fontsize=8.5, style="italic")
    c2 = 12.6
    e2 = Node(ax, c2, 14.2, "Partition(A, lo, hi)", "terminal", w=4.0)
    arrow(ax, [part.right(), (8.6, part.y), (8.6, 14.2), e2.left()], dashed=True)
    init = Node(ax, c2, 13.0, "pivot <- A[hi];  i <- lo - 1;  j <- lo", "process", w=5.0)
    dj = Node(ax, c2, 11.6, "j <= hi - 1 ?", "decision", w=2.8, h=1.1)
    dp = Node(ax, c2, 9.9, "A[j] <= pivot ?\n(basic operation)", "decision", w=3.6, h=1.5, size=8.5)
    sw = Node(ax, c2, 8.3, "i <- i + 1;  swap A[i], A[j]", "process", w=3.8)
    jinc = Node(ax, 16.6, 9.9, "j <- j + 1", "process", w=1.9)
    fin = Node(ax, c2, 6.8, "swap A[i + 1], A[hi]   (pivot to its final place)", "process", w=5.4, size=8.5)
    r2 = Node(ax, c2, 5.6, "return i + 1", "terminal", w=2.6)
    arrow(ax, [e2.bottom(), init.top()])
    arrow(ax, [init.bottom(), dj.top()])
    arrow(ax, [dj.bottom(), dp.top()], "Yes", 0)
    arrow(ax, [dp.bottom(), sw.top()], "Yes", 0)
    arrow(ax, [dp.right(), jinc.left()], "No", 0, dy=0.15)
    arrow(ax, [sw.right(), (jinc.x, sw.y), jinc.bottom()])
    arrow(ax, [jinc.top(), (jinc.x, dj.y), dj.right()])
    arrow(ax, [dj.left(), (9.5, dj.y), (9.5, fin.y), fin.left()], "No", 0, dx=-0.6)
    arrow(ax, [fin.bottom(), r2.top()])
    ax.text(c2 + 0.4, 4.7, "invariant: A[lo..i] <= pivot < A[i+1..j-1];  exactly hi - lo comparisons",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "flow_m2_quick_sort.png")


def flowchart_binary_search():
    fig, ax = new_canvas(19.4, 1.0, 14.0, "Module 3 - Binary Search: iterative (left, production) and "
                         "recursive (right)")
    ax.text(4.6, 13.5, "BinarySearch(K, n, t)", ha="center", fontsize=10, fontweight="bold")
    ax.text(14.6, 13.5, "BinarySearchRec(K, lo, hi, t)", ha="center", fontsize=10, fontweight="bold")
    divider(ax, 9.7, 1.4, 13.3)
    start = Node(ax, 4.6, 12.7, "Start", "terminal", w=2.2)
    inp = Node(ax, 4.6, 11.7, "Input: sorted index K[0..n-1], target t", "io", w=6.0, size=8.5)
    init = Node(ax, 4.6, 10.7, "lo <- 0;  hi <- n - 1", "process", w=3.4)
    d1 = Node(ax, 4.6, 9.4, "lo <= hi ?", "decision", w=2.8, h=1.3)
    mid = Node(ax, 4.6, 8.0, "mid <- floor((lo + hi) / 2)", "process", w=3.8)
    d2 = Node(ax, 4.6, 6.5, "t = K[mid] ?\n(3-way comparison)", "decision", w=3.4, h=1.5, size=8.5)
    d3 = Node(ax, 4.6, 4.8, "t < K[mid] ?", "decision", w=3.0, h=1.2)
    hi = Node(ax, 2.0, 3.2, "hi <- mid - 1", "process", w=2.4)
    lo = Node(ax, 7.2, 3.2, "lo <- mid + 1", "process", w=2.4)
    r_nf = Node(ax, 8.0, 9.4, "return -1\n(lo = insertion pt)", "terminal", w=2.4, h=1.0, size=8)
    r_f = Node(ax, 8.0, 6.5, "return mid\n(found)", "terminal", w=2.2, h=1.0, size=8.5)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), d1.top()])
    arrow(ax, [d1.bottom(), mid.top()], "Yes", 0)
    arrow(ax, [d1.right(), r_nf.left()], "No", 0, dy=0.15)
    arrow(ax, [mid.bottom(), d2.top()])
    arrow(ax, [d2.right(), r_f.left()], "Yes", 0, dx=0.02, dy=0.15)
    arrow(ax, [d2.bottom(), d3.top()], "No", 0)
    arrow(ax, [d3.left(), (hi.x, d3.y), hi.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d3.right(), (lo.x, d3.y), lo.top()], "No", 0, dx=0.15)
    arrow(ax, [hi.bottom(), (hi.x, 2.1), (0.3, 2.1), (0.3, d1.y), d1.left()])
    arrow(ax, [lo.bottom(), (lo.x, 2.1), (hi.x + 0.05, 2.1)])
    ax.text(4.6, 1.5, "loop: Theta(1) extra space;  at most floor(log2 n) + 1 comparisons", ha="center",
            fontsize=8.5, style="italic")
    entry = Node(ax, 14.6, 12.7, "BinarySearchRec(K, lo, hi, t)", "terminal", w=5.0)
    e1 = Node(ax, 14.6, 11.3, "lo > hi ?", "decision", w=2.8, h=1.3)
    base = Node(ax, 11.5, 11.3, "return -1\n(empty: base case)", "terminal", w=2.4, h=1.0, size=8)
    emid = Node(ax, 14.6, 9.9, "mid <- floor((lo + hi) / 2)   DIVIDE", "process", w=4.6, size=8.5)
    e2 = Node(ax, 14.6, 8.4, "t = K[mid] ?", "decision", w=3.0, h=1.3)
    efound = Node(ax, 17.8, 8.4, "return mid\n(found)", "terminal", w=2.2, h=1.0, size=8.5)
    e3 = Node(ax, 14.6, 6.7, "t < K[mid] ?", "decision", w=3.0, h=1.3)
    left = Node(ax, 12.2, 4.9, "return BinarySearchRec\n(K, lo, mid - 1, t)", "call", w=3.7, h=1.0, size=8)
    right = Node(ax, 17.1, 4.9, "return BinarySearchRec\n(K, mid + 1, hi, t)", "call", w=3.7, h=1.0, size=8)
    arrow(ax, [entry.bottom(), e1.top()])
    arrow(ax, [e1.left(), base.right()], "Yes", 0, dx=-0.55, dy=0.15)
    arrow(ax, [e1.bottom(), emid.top()], "No", 0)
    arrow(ax, [emid.bottom(), e2.top()])
    arrow(ax, [e2.right(), efound.left()], "Yes", 0, dx=0.02, dy=0.15)
    arrow(ax, [e2.bottom(), e3.top()], "No", 0)
    arrow(ax, [e3.left(), (left.x, e3.y), left.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [e3.right(), (right.x, e3.y), right.top()], "No", 0, dx=0.15)
    arrow(ax, [left.left(), (10.05, left.y), (10.05, entry.y), entry.left()], "CONQUER one half", 1,
          dx=0.1, dy=1.6, dashed=True)
    arrow(ax, [right.right(), (19.15, right.y), (19.15, entry.y), entry.right()], dashed=True)
    ax.text(14.6, 3.6, "ONE recursive call per activation; COMBINE: the answer is returned unchanged\n"
            "C(n) = C(floor(n/2)) + 1 -> Theta(log n)", ha="center", va="top", fontsize=8.5, style="italic")
    save(fig, "flow_m3_binary_search.png")


def flowchart_strassen():
    fig, ax = new_canvas(12.6, 3.0, 15.4, "Module 4 - Strassen's matrix multiplication")
    c = 5.6
    entry = Node(ax, c, 14.6, "Strassen(A, B, n)   (n a power of two)", "terminal", w=5.6)
    d = Node(ax, c, 13.2, "n = 1 ?\n(hybrid: n <= n0)", "decision", w=3.2, h=1.4, size=8.5)
    base = Node(ax, 10.2, 13.2, "return [A11 x B11]\n(hybrid: NaiveMultiply)", "terminal", w=3.6, h=1.0,
                size=8)
    split = Node(ax, c, 11.7, "h <- n/2;  split A into A11, A12, A21, A22\nand B into B11, B12, B21, B22",
                 "process", w=6.0, h=1.0, size=8.5)
    sums = Node(ax, c, 10.4, "10 block sums / differences of h x h blocks\n(A11 + A22, B11 + B22, ..., "
                "B21 + B22)", "process", w=6.4, h=1.0, size=8.5)
    m = Node(ax, c, 8.8, "M1 <- Strassen(A11 + A22, B11 + B22, h)   ...\nM7 <- Strassen(A12 - A22, B21 + B22, h)"
             "\n(7 recursive products)", "call", w=6.8, h=1.4, size=8.5)
    comb = Node(ax, c, 7.0, "C11 <- M1 + M4 - M5 + M7     C12 <- M3 + M5\nC21 <- M2 + M4     C22 <- M1 - M2 + M3 + M6"
                "\n(8 block additions)", "process", w=6.8, h=1.4, size=8.5)
    ret = Node(ax, c, 5.5, "return C assembled from C11, C12, C21, C22", "terminal", w=5.6)
    for node, tag in ((split, "DIVIDE"), (m, "CONQUER"), (comb, "COMBINE")):
        ax.text(node.x + node.w / 2, node.y + node.h / 2 + 0.04, tag, fontsize=7.5, color="#1f3864",
                fontweight="bold", ha="right", va="bottom")
    arrow(ax, [entry.bottom(), d.top()])
    arrow(ax, [d.right(), base.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d.bottom(), split.top()], "No", 0)
    for a, b in ((split, sums), (sums, m), (m, comb), (comb, ret)):
        arrow(ax, [a.bottom(), b.top()])
    arrow(ax, [m.left(), (0.6, m.y), (0.6, entry.y), entry.left()], "7 recursive calls", 1, dx=0.1,
          dy=0.25, dashed=True)
    ax.text(6.3, 4.3, "M(n) = 7M(n/2) = n^log2(7) ~ n^2.807 multiplications;  A(n) = 7A(n/2) + 18(n/2)^2",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "flow_m4_strassen.png")


# --------------------------------------------------------------------------- Part 3 decomposition diagrams
def merge_tree_nodes(items, lo, hi, depth, out):
    """Top-down merge sort of items[lo:hi] (key = item[1]); records every node; returns merged list."""
    part = items[lo:hi]
    node = {"lo": lo, "hi": hi, "depth": depth, "input": [e for e, _ in part]}
    out.append(node)
    if hi - lo <= 1:
        node["merged"], node["cmp"] = list(part), 0
        return list(part)
    mid = (lo + hi) // 2
    left = merge_tree_nodes(items, lo, mid, depth + 1, out)
    right = merge_tree_nodes(items, mid, hi, depth + 1, out)
    merged, i, j, cmp = [], 0, 0, 0
    while i < len(left) and j < len(right):
        cmp += 1
        if right[j][1] < left[i][1]:
            merged.append(right[j]); j += 1
        else:
            merged.append(left[i]); i += 1
    merged += left[i:] + right[j:]
    node["merged"], node["cmp"], node["mid"] = merged, cmp, mid
    return merged


def cells(ax, lo, labels, y, color, size=7.5, edge="#333333", hl=()):
    for k, text in enumerate(labels):
        x = lo + k
        ax.add_patch(Rectangle((x + 0.04, y - 0.28), 0.92, 0.56, facecolor="#ffd966" if text in hl else color,
                               edgecolor=edge, lw=0.8))
        ax.text(x + 0.5, y, text, ha="center", va="center", fontsize=size)


def outline(ax, lo, hi, y, color="#1f3864"):
    """Thick frame around the cells lo..hi-1 of one sub-array (one tree node)."""
    ax.add_patch(Rectangle((lo + 0.01, y - 0.33), hi - lo - 0.02, 0.66, fill=False, edgecolor=color, lw=1.8))


def merge_sort_tree():
    events = load_events()
    nodes = []
    final = merge_tree_nodes(events, 0, len(events), 0, nodes)
    total = sum(nd["cmp"] for nd in nodes)
    assert total == 30 and [e for e, _ in final] == [e for e, _ in sorted(events, key=lambda r: r[1])]
    max_d = max(nd["depth"] for nd in nodes)
    dy = 1.05
    y_div = {d: 10.3 - d * dy for d in range(max_d + 1)}
    y_comb = {d: y_div[max_d] - (max_d - d) * dy for d in range(max_d)}
    fig, ax = plt.subplots(figsize=(13.5, 9.6))
    ax.set_xlim(-2.6, 13.8)
    ax.set_ylim(y_comb[0] - 1.6, 11.6)
    ax.axis("off")
    ax.set_title("Module 1 - merge sort recursion tree on the 12 sample shipment events: DIVIDE (top), "
                 "base cases, COMBINE (bottom)", fontsize=11, fontweight="bold")
    ties = ("E06", "E11", "E04", "E09")
    for nd in nodes:
        leaf = nd["hi"] - nd["lo"] == 1
        cells(ax, nd["lo"], nd["input"], y_div[nd["depth"]], "#d9ead3" if leaf else "#dbe8f6", hl=ties)
        outline(ax, nd["lo"], nd["hi"], y_div[nd["depth"]])
        if not leaf:
            mid = nd["mid"]
            for child in nodes:
                if child["depth"] == nd["depth"] + 1 and (child["lo"] == nd["lo"] or child["lo"] == mid) \
                        and nd["lo"] <= child["lo"] < nd["hi"]:
                    ax.plot([(nd["lo"] + nd["hi"]) / 2, (child["lo"] + child["hi"]) / 2],
                            [y_div[nd["depth"]] - 0.28, y_div[child["depth"]] + 0.28], color="#666666", lw=0.7)
                    y_from = y_div[child["depth"]] if child["hi"] - child["lo"] == 1 else y_comb[child["depth"]]
                    ax.plot([(child["lo"] + child["hi"]) / 2, (nd["lo"] + nd["hi"]) / 2],
                            [y_from - 0.28, y_comb[nd["depth"]] + 0.28], color="#b45f06", lw=0.7)
            cells(ax, nd["lo"], [e for e, _ in nd["merged"]], y_comb[nd["depth"]], "#fde3cf", hl=ties)
            outline(ax, nd["lo"], nd["hi"], y_comb[nd["depth"]], "#b45f06")
            ax.text(nd["hi"] - 0.08, y_comb[nd["depth"]] - 0.43, f"{nd['cmp']} cmp", fontsize=6.5,
                    color="#7f3f00", ha="right")
    for d in range(max_d + 1):
        ax.text(-0.3, y_div[d], f"divide, depth {d}", ha="right", va="center", fontsize=8, color="#1f3864")
    for d in range(max_d):
        ax.text(-0.3, y_comb[d], f"combine, depth {d}", ha="right", va="center", fontsize=8, color="#7f3f00")
    ax.text(5.6, y_comb[0] - 0.9, f"total {total} key comparisons (worst-case bound 33);  yellow = equal keys "
            "(E06/E11 and E04/E09) - they keep their input order: the merge is stable", ha="center",
            fontsize=8.5, style="italic")
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "m1_merge_sort_recursion_tree.png", dpi=150)
    plt.close(fig)
    print(OUT_DIR / "m1_merge_sort_recursion_tree.png")


def quick_partition_nodes(a, lo, hi, depth, out):
    """Lomuto quick sort (pivot = last) that records each partition call as a tree node."""
    if lo >= hi:
        if lo == hi:
            out.append({"lo": lo, "hi": hi, "depth": depth, "before": [a[lo]], "leaf": True})
        return
    before = a[lo:hi + 1]
    pivot, i, cmp = a[hi], lo - 1, 0
    for j in range(lo, hi):
        cmp += 1
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[hi] = a[hi], a[i + 1]
    p = i + 1
    out.append({"lo": lo, "hi": hi, "depth": depth, "before": before, "pivot": pivot, "p": p, "cmp": cmp,
                "leaf": False})
    quick_partition_nodes(a, lo, p - 1, depth + 1, out)
    quick_partition_nodes(a, p + 1, hi, depth + 1, out)


def quick_sort_tree():
    scores = load_scores()
    a, nodes = list(scores), []
    quick_partition_nodes(a, 0, len(a) - 1, 0, nodes)
    total = sum(nd.get("cmp", 0) for nd in nodes)
    assert a == sorted(scores) and total == 32
    max_d = max(nd["depth"] for nd in nodes)
    dy = 1.25
    fig, ax = plt.subplots(figsize=(13.5, 8.6))
    ax.set_xlim(-2.4, 15.2)
    ax.set_ylim(9.4 - (max_d + 2) * dy - 0.6, 10.6)
    ax.axis("off")
    ax.set_title("Module 2 - quick sort partition tree on the 12 sample priority scores (Lomuto, pivot = last "
                 "element)", fontsize=11, fontweight="bold")
    y = {d: 9.4 - d * dy for d in range(max_d + 1)}
    for nd in nodes:
        yy = y[nd["depth"]]
        if nd["leaf"]:
            cells(ax, nd["lo"], [str(nd["before"][0])], yy, "#d9ead3", size=8)
            continue
        labels = [str(v) for v in nd["before"]]
        cells(ax, nd["lo"], labels, yy, "#dbe8f6", size=8)
        x = nd["hi"]
        ax.add_patch(Rectangle((x + 0.04, yy - 0.28), 0.92, 0.56, facecolor="#f4cccc", edgecolor="#990000", lw=1.4))
        ax.text(x + 0.5, yy, labels[-1], ha="center", va="center", fontsize=8, fontweight="bold")
        outline(ax, nd["lo"], nd["hi"] + 1, yy)
        ax.text((nd["lo"] + nd["hi"] + 1) / 2, yy - 0.47, f"pivot {nd['pivot']} -> pos {nd['p']}, {nd['cmp']} cmp",
                fontsize=6.5, ha="center", va="center", color="#7f3f00")
        cx = (nd["lo"] + nd["hi"] + 1) / 2
        for child in nodes:
            if child["depth"] != nd["depth"] + 1:
                continue
            if (child["lo"] == nd["lo"] and child["hi"] == nd["p"] - 1) or \
                    (child["lo"] == nd["p"] + 1 and child["hi"] == nd["hi"]):
                ax.plot([cx, (child["lo"] + child["hi"] + 1) / 2], [yy - 0.28, y[child["depth"]] + 0.28],
                        color="#666666", lw=0.8)
        ax.plot([cx, nd["p"] + 0.5], [yy - 0.28, y[max_d] - dy + 0.28], color="#cc0000", lw=0.5, ls=":")
    yb = y[max_d] - dy
    cells(ax, 0, [str(v) for v in a], yb, "#fff2cc", size=8)
    ax.text(-0.3, yb, "sorted array", ha="right", va="center", fontsize=8, fontweight="bold")
    for d in range(max_d + 1):
        ax.text(-0.3, y[d], f"depth {d}", ha="right", va="center", fontsize=8, color="#1f3864")
    ax.text(6.5, yb - 0.8, f"red = pivot (DIVIDE puts it at its final position, dotted line);  green = size-1 "
            f"sub-array (base case);  total {total} comparisons, COMBINE does nothing", ha="center", fontsize=8.5,
            style="italic")
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "m2_quick_sort_partition_tree.png", dpi=150)
    plt.close(fig)
    print(OUT_DIR / "m2_quick_sort_partition_tree.png")


def search_steps(keys, t):
    lo, hi, steps = 0, len(keys) - 1, []
    while lo <= hi:
        mid = (lo + hi) // 2
        if t == keys[mid]:
            steps.append((lo, hi, mid, "found"))
            return steps, mid, lo
        steps.append((lo, hi, mid, "go left" if t < keys[mid] else "go right"))
        if t < keys[mid]:
            hi = mid - 1
        else:
            lo = mid + 1
    return steps, -1, lo


def binary_search_intervals():
    keys = load_index()
    queries = [("Q8", "SLX7720418833"), ("Q5", "SLX3000000000")]
    fig, axes = plt.subplots(2, 1, figsize=(13.5, 8.2))
    for ax, (qid, t) in zip(axes, queries):
        steps, pos, ins = search_steps(keys, t)
        assert pos == (keys.index(t) if t in keys else -1)
        rows = len(steps) + (1 if pos < 0 else 0)
        ax.set_xlim(-2.4, 16.6)
        ax.set_ylim(-rows - 0.9, 1.4)
        ax.axis("off")
        result = f"found at [{pos}]" if pos >= 0 else f"absent, insertion point lo = {ins}"
        ax.set_title(f"{qid}: t = {t} - {result}, {len(steps)} comparisons", fontsize=10.5, fontweight="bold")
        for k in range(16):
            ax.text(k + 0.5, 0.75, f"[{k}]", ha="center", fontsize=7.5, color="#555555")
            ax.text(k + 0.5, 0.35, keys[k][3:8] + "..", ha="center", fontsize=6.3, color="#555555")
        for r, (lo, hi, mid, decision) in enumerate(steps):
            yy = -r - 0.3
            for k in range(16):
                inside = lo <= k <= hi
                face = "#fde3cf" if k == mid else ("#dbe8f6" if inside else "#f3f3f3")
                ax.add_patch(Rectangle((k + 0.04, yy - 0.32), 0.92, 0.64, facecolor=face,
                                       edgecolor="#333333" if inside else "#cccccc", lw=0.8))
            ax.text(mid + 0.5, yy, "mid", ha="center", va="center", fontsize=7, fontweight="bold")
            ax.text(-0.2, yy, f"step {r + 1}: [{lo}, {hi}]", ha="right", va="center", fontsize=8)
            ax.text(16.2, yy, decision, ha="left", va="center", fontsize=8,
                    color="#38761d" if decision == "found" else "#7f3f00", fontweight="bold")
        if pos < 0:
            yy = -len(steps) - 0.3
            for k in range(16):
                ax.add_patch(Rectangle((k + 0.04, yy - 0.32), 0.92, 0.64, facecolor="#f3f3f3", edgecolor="#cccccc",
                                       lw=0.8))
            ax.annotate("", xy=(ins, yy), xytext=(ins, yy + 0.55),
                        arrowprops=dict(arrowstyle="-|>", color="#cc0000", lw=1.4))
            ax.text(-0.2, yy, f"lo = {ins} > hi = {ins - 1}", ha="right", va="center", fontsize=8)
            ax.text(16.2, yy, "empty -> -1", ha="left", va="center", fontsize=8, color="#cc0000", fontweight="bold")
    fig.text(0.5, 0.01, "blue = interval [lo, hi] still searched, orange = probe K[mid]; each step halves the "
             "interval (16 -> 8 -> 4 -> 2 -> 1), so at most floor(log2 16) + 1 = 5 comparisons",
             ha="center", fontsize=8.5, style="italic")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "m3_binary_search_intervals.png", dpi=150)
    plt.close(fig)
    print(OUT_DIR / "m3_binary_search_intervals.png")


def mat_add(x, y, s=1):
    return [[x[i][j] + s * y[i][j] for j in range(len(x))] for i in range(len(x))]


def mat_mul(x, y):
    n = len(x)
    return [[sum(x[i][k] * y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def block(m, r, c):
    return [row[c * 2:c * 2 + 2] for row in m[r * 2:r * 2 + 2]]


def draw_matrix(ax, x0, y0, m, title, colors, size=9):
    """4 x 4 matrix with its four 2 x 2 quadrants coloured; (x0, y0) = top-left corner."""
    ax.text(x0 + 2, y0 + 0.35, title, ha="center", fontsize=9.5, fontweight="bold")
    for i in range(4):
        for j in range(4):
            q = (i // 2) * 2 + j // 2
            ax.add_patch(Rectangle((x0 + j, y0 - i - 1), 1, 1, facecolor=colors[q], edgecolor="#777777", lw=0.6))
            ax.text(x0 + j + 0.5, y0 - i - 0.5, str(m[i][j]), ha="center", va="center", fontsize=size)
    ax.plot([x0 + 2, x0 + 2], [y0, y0 - 4], color="#333333", lw=2)
    ax.plot([x0, x0 + 4], [y0 - 2, y0 - 2], color="#333333", lw=2)
    ax.add_patch(Rectangle((x0, y0 - 4), 4, 4, fill=False, edgecolor="#333333", lw=1.5))


def strassen_blocks():
    A, B = load_matrices()
    a = {f"{r + 1}{c + 1}": block(A, r, c) for r in range(2) for c in range(2)}
    b = {f"{r + 1}{c + 1}": block(B, r, c) for r in range(2) for c in range(2)}
    M = [mat_mul(mat_add(a["11"], a["22"]), mat_add(b["11"], b["22"])),
         mat_mul(mat_add(a["21"], a["22"]), b["11"]),
         mat_mul(a["11"], mat_add(b["12"], b["22"], -1)),
         mat_mul(a["22"], mat_add(b["21"], b["11"], -1)),
         mat_mul(mat_add(a["11"], a["12"]), b["22"]),
         mat_mul(mat_add(a["21"], a["11"], -1), mat_add(b["11"], b["12"])),
         mat_mul(mat_add(a["12"], a["22"], -1), mat_add(b["21"], b["22"]))]
    C11 = mat_add(mat_add(mat_add(M[0], M[3]), M[4], -1), M[6])
    C12 = mat_add(M[2], M[4])
    C21 = mat_add(M[1], M[3])
    C22 = mat_add(mat_add(mat_add(M[0], M[1], -1), M[2]), M[5])
    C = [C11[0] + C12[0], C11[1] + C12[1], C21[0] + C22[0], C21[1] + C22[1]]
    assert C == mat_mul(A, B)
    qcol = ["#dbe8f6", "#d9ead3", "#fde3cf", "#e8dff5"]
    fig, ax = plt.subplots(figsize=(14, 7.6))
    ax.set_xlim(0, 25)
    ax.set_ylim(-0.6, 12.6)
    ax.axis("off")
    ax.set_title("Module 4 - Strassen on the 4 x 4 sample: DIVIDE into 2 x 2 blocks, CONQUER with 7 products, "
                 "COMBINE into C", fontsize=11, fontweight="bold")
    draw_matrix(ax, 0.6, 11.3, A, "A = demand D", qcol)
    draw_matrix(ax, 0.6, 5.5, B, "B = cost C", qcol)
    for k, name in enumerate(("11", "12", "21", "22")):
        ax.text(0.6 + (k % 2) * 2 + 1, 11.3 - (k // 2) * 2 - 1.85, f"A{name}", ha="center", fontsize=7,
                color="#444444", style="italic")
        ax.text(0.6 + (k % 2) * 2 + 1, 5.5 - (k // 2) * 2 - 1.85, f"B{name}", ha="center", fontsize=7,
                color="#444444", style="italic")
    forms = ["(A11 + A22)(B11 + B22)", "(A21 + A22) B11", "A11 (B12 - B22)", "A22 (B21 - B11)",
             "(A11 + A12) B22", "(A21 - A11)(B11 + B12)", "(A12 - A22)(B21 + B22)"]
    ax.text(10.9, 11.75, "CONQUER: 7 recursive (n/2) x (n/2) products", ha="center", fontsize=9.5,
            fontweight="bold")
    for k, (f, m) in enumerate(zip(forms, M)):
        yy = 11.0 - k * 1.55
        ax.add_patch(FancyBboxPatch((6.3, yy - 0.6), 9.2, 1.2, boxstyle="round,pad=0,rounding_size=0.2",
                                    facecolor="#fde3cf", edgecolor="#333333", lw=0.9))
        ax.text(6.6, yy, f"M{k + 1} = {f}", va="center", fontsize=9)
        ax.text(15.2, yy, f"= {m}", va="center", ha="right", fontsize=9, family="monospace")
    ax.annotate("", xy=(6.25, 7.0), xytext=(4.85, 9.3), arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2))
    ax.annotate("", xy=(6.25, 5.5), xytext=(4.85, 3.5), arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2))
    ax.text(5.55, 6.25, "10 block\nsums", ha="center", va="center", fontsize=7.5, color="#7f3f00")
    combos = [("C11 = M1 + M4 - M5 + M7", C11), ("C12 = M3 + M5", C12), ("C21 = M2 + M4", C21),
              ("C22 = M1 - M2 + M3 + M6", C22)]
    ax.text(20.6, 11.75, "COMBINE: 8 block additions", ha="center", fontsize=9.5, fontweight="bold")
    for k, (f, m) in enumerate(combos):
        yy = 11.0 - k * 1.1
        ax.text(17.0, yy, f"{f} = {m}", va="center", fontsize=8.5, family="monospace",
                bbox=dict(boxstyle="round", facecolor=qcol[k], edgecolor="#333333", lw=0.7))
    ax.annotate("", xy=(16.9, 9.3), xytext=(15.6, 7.0), arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2))
    draw_matrix(ax, 18.6, 6.3, C, "C = A x B (forecast cost F)", qcol)
    ax.text(12.5, -0.3, "one level shown; each Mi is again computed with 7 scalar products  ->  49 multiplications "
            "+ 198 additions (naive: 64 + 48);  result checked against the naive product", ha="center",
            fontsize=8.5, style="italic")
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "m4_strassen_blocks.png", dpi=150)
    plt.close(fig)
    print(OUT_DIR / "m4_strassen_blocks.png")


def main():
    flowchart_merge_sort()
    flowchart_quick_sort()
    flowchart_binary_search()
    flowchart_strassen()
    merge_sort_tree()
    quick_sort_tree()
    binary_search_intervals()
    strassen_blocks()


if __name__ == "__main__":
    main()
