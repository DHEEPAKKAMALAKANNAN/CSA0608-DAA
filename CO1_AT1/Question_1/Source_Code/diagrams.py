"""ShopSphere audit - flowcharts and explanatory diagrams for the report (saved to Report/diagrams).

Flowcharts use the standard symbols: terminal = rounded box, process = rectangle, decision = diamond with
Yes/No labels, input/output = parallelogram, predefined process / recursive call = rectangle with side bars.

Diagrams written
  flowchart_m1_nested.png          M1 duplicate detector as given (all pairs, nested loops)
  flowchart_m1_hash.png            M1 redesign: one pass with a hash set keyed on (title, seller)
  flowchart_m2_rate_limiter.png    M2 doubling-window audit loop
  flowchart_s1_sequential.png      M3 version S1: sequential search
  flowchart_s2_binary.png          M3 version S2: binary search, iterative and recursive
  s2_backward_substitution.png     backward-substitution chain of T(n) = T(n/2) + 1
  m4_recursion_trees.png           recursion trees of 4T(n/2) + n and 2T(n/2) + n with level costs
  m5_recursion_tree.png            recursion tree of 2T(n/2) + n log n with level costs (n = 1,024)
"""
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "Report" / "diagrams"
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


# --------------------------------------------------------------------------- M1 and M2 flowcharts
def flowchart_m1_nested():
    fig, ax = new_canvas(12, 3.6, 17.8, "M1 - Duplicate-Listing Detector as given (compare every pair)")
    start = Node(ax, 5, 17.1, "Start", "terminal", w=2.2)
    inp = Node(ax, 5, 16.0, "Input: Product[0..n-1]", "io", w=4.4)
    i0 = Node(ax, 5, 14.9, "i <- 0", "process", w=2.2)
    d_i = Node(ax, 5, 13.6, "i <= n - 2 ?", "decision", w=3.0, h=1.3)
    j0 = Node(ax, 5, 12.2, "j <- i + 1", "process", w=2.4)
    d_j = Node(ax, 5, 10.8, "j <= n - 1 ?", "decision", w=3.0, h=1.3)
    d_eq = Node(ax, 5, 8.7, "title[i] = title[j] AND\nseller[i] = seller[j] ?\n(basic operation)",
                "decision", w=4.8, h=2.2, size=8.5)
    mark = Node(ax, 5, 6.6, "MarkDuplicate(j)", "call", w=3.2)
    jinc = Node(ax, 9.3, 8.7, "j <- j + 1", "process", w=2.0)
    iinc = Node(ax, 1.6, 10.8, "i <- i + 1", "process", w=2.0)
    end = Node(ax, 5, 5.2, "End (all duplicates marked)", "terminal", w=4.4)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), i0.top()])
    arrow(ax, [i0.bottom(), d_i.top()])
    arrow(ax, [d_i.bottom(), j0.top()], "Yes", 0)
    arrow(ax, [j0.bottom(), d_j.top()])
    arrow(ax, [d_j.bottom(), d_eq.top()], "Yes", 0)
    arrow(ax, [d_eq.bottom(), mark.top()], "Yes", 0)
    arrow(ax, [d_eq.right(), jinc.left()], "No", 0, dy=0.15)
    arrow(ax, [mark.right(), (jinc.x, mark.y), jinc.bottom()])
    arrow(ax, [jinc.top(), (jinc.x, d_j.y), d_j.right()])
    arrow(ax, [d_j.left(), iinc.right()], "No", 0, dx=-0.6, dy=0.15)
    arrow(ax, [iinc.top(), (iinc.x, d_i.y), d_i.left()])
    arrow(ax, [d_i.right(), (11.2, d_i.y), (11.2, end.y), end.right()], "No", 0, dx=0.1)
    ax.text(6, 4.1, "inner loop runs n - 1 - i times  ->  C(n) = (n-1) + (n-2) + ... + 1 = n(n-1)/2 in "
            "every case  ->  Theta(n^2)", ha="center", fontsize=8.5, style="italic")
    save(fig, "flowchart_m1_nested.png")


def flowchart_m1_hash():
    fig, ax = new_canvas(11.5, 3.4, 15.4, "M1 redesign - one pass with a hash set keyed on (title, seller)")
    start = Node(ax, 5.5, 14.7, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.5, 13.6, "Input: Product[0..n-1]", "io", w=4.4)
    init = Node(ax, 5.5, 12.5, "seen <- empty hash set;  j <- 0", "process", w=4.6)
    d_loop = Node(ax, 5.5, 11.1, "j <= n - 1 ?", "decision", w=3.0, h=1.3)
    key = Node(ax, 5.5, 9.7, "key <- (Product[j].title, Product[j].seller)", "process", w=5.4)
    d_in = Node(ax, 5.5, 8.1, "key in seen ?\n(one hash lookup)", "decision", w=3.6, h=1.6)
    mark = Node(ax, 2.4, 6.6, "MarkDuplicate(j)", "call", w=3.0)
    ins = Node(ax, 8.6, 6.6, "insert key into seen", "process", w=3.2)
    jinc = Node(ax, 5.5, 5.4, "j <- j + 1", "process", w=2.2)
    end = Node(ax, 9.9, 11.1, "End", "terminal", w=2.0)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), d_loop.top()])
    arrow(ax, [d_loop.bottom(), key.top()], "Yes", 0)
    arrow(ax, [d_loop.right(), end.left()], "No", 0, dy=0.15)
    arrow(ax, [key.bottom(), d_in.top()])
    arrow(ax, [d_in.left(), (mark.x, d_in.y), mark.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d_in.right(), (ins.x, d_in.y), ins.top()], "No", 0, dx=0.15)
    arrow(ax, [mark.bottom(), (mark.x, jinc.y), jinc.left()])
    arrow(ax, [ins.bottom(), (ins.x, jinc.y), jinc.right()])
    arrow(ax, [jinc.bottom(), (jinc.x, 4.7), (0.4, 4.7), (0.4, d_loop.y), d_loop.left()])
    ax.text(5.75, 3.9, "n hash lookups (expected O(1) each)  ->  Theta(n) expected time, Theta(n) extra space",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "flowchart_m1_hash.png")


def flowchart_m2():
    fig, ax = new_canvas(11, 4.2, 16.4, "M2 - API Rate Limiter (audit windows of doubling size)")
    start = Node(ax, 5.5, 15.7, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.5, 14.6, "Input: Request[0..n-1]", "io", w=4.4)
    i1 = Node(ax, 5.5, 13.5, "i <- 1", "process", w=2.2)
    d_i = Node(ax, 5.5, 12.2, "i < n ?", "decision", w=2.8, h=1.3)
    j0 = Node(ax, 5.5, 10.8, "j <- 0", "process", w=2.2)
    d_j = Node(ax, 5.5, 9.4, "j <= i - 1 ?", "decision", w=3.0, h=1.3)
    audit = Node(ax, 5.5, 7.9, "Audit(Request[j])\n(basic operation)", "call", w=3.4, h=1.0)
    jinc = Node(ax, 5.5, 6.6, "j <- j + 1", "process", w=2.2)
    idbl = Node(ax, 1.7, 9.4, "i <- i x 2", "process", w=2.2)
    end = Node(ax, 9.3, 6.6, "End", "terminal", w=2.0)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), i1.top()])
    arrow(ax, [i1.bottom(), d_i.top()])
    arrow(ax, [d_i.bottom(), j0.top()], "Yes", 0)
    arrow(ax, [j0.bottom(), d_j.top()])
    arrow(ax, [d_j.bottom(), audit.top()], "Yes", 0)
    arrow(ax, [audit.bottom(), jinc.top()])
    arrow(ax, [jinc.right(), (7.8, jinc.y), (7.8, d_j.y), d_j.right()])
    arrow(ax, [d_j.left(), idbl.right()], "No", 0, dx=-0.6, dy=0.15)
    arrow(ax, [idbl.top(), (idbl.x, d_i.y), d_i.left()])
    arrow(ax, [d_i.right(), (end.x, d_i.y), end.top()], "No", 0, dx=0.1)
    ax.text(5.5, 5.2, "pass k has i = 2^k  ->  2^k audits;  A(n) = 1 + 2 + ... + 2^(m-1) = 2^m - 1,  "
            "m = ceil(log2 n)  ->  Theta(n)", ha="center", fontsize=8.5, style="italic")
    save(fig, "flowchart_m2_rate_limiter.png")


# --------------------------------------------------------------------------- S1 and S2 flowcharts
def flowchart_s1():
    fig, ax = new_canvas(10, 2.6, 14.4, "S1 - Sequential search of the unsorted catalogue")
    start = Node(ax, 5, 13.6, "Start", "terminal", w=2.2)
    inp = Node(ax, 5, 12.4, "Input: catalogue[0..n-1] (unsorted), key", "io", w=6.2)
    init = Node(ax, 5, 11.1, "i <- 0", "process", w=2.4)
    d1 = Node(ax, 5, 9.6, "i < n ?", "decision", w=2.8, h=1.3)
    d2 = Node(ax, 5, 7.4, "catalogue[i] = key ?\n(basic operation)", "decision", w=4.2, h=1.8)
    inc = Node(ax, 8.6, 7.4, "i <- i + 1", "process", w=2.0)
    found = Node(ax, 5.3, 5.3, "Output: return i\n(product found)", "io", w=3.4, h=1.0)
    notf = Node(ax, 1.6, 5.3, "Output: return -1\n(not found)", "io", w=2.6, h=1.0)
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
    ax.text(5, 2.9, "found at position i: i + 1 comparisons (best 1);  last entry or absent: n comparisons "
            "(worst)", ha="center", fontsize=8.5, style="italic")
    save(fig, "flowchart_s1_sequential.png")


def flowchart_s2():
    fig, ax = new_canvas(19.4, 1.0, 14.0, "S2 - Binary search on the sorted index: iterative (left) "
                         "and recursive (right)")
    ax.text(4.6, 13.5, "BinarySearchIterative(A, n, key)", ha="center", fontsize=10, fontweight="bold")
    ax.text(14.6, 13.5, "BinarySearchRecursive(A, lo, hi, key)", ha="center", fontsize=10,
            fontweight="bold")
    ax.plot([9.7, 9.7], [1.4, 13.3], color="#999999", lw=0.8, ls=":")
    # iterative version
    start = Node(ax, 4.6, 12.7, "Start", "terminal", w=2.2)
    inp = Node(ax, 4.6, 11.7, "Input: sorted A[0..n-1], key", "io", w=5.0)
    init = Node(ax, 4.6, 10.7, "lo <- 0;  hi <- n - 1", "process", w=3.4)
    d1 = Node(ax, 4.6, 9.4, "lo <= hi ?", "decision", w=2.8, h=1.3)
    mid = Node(ax, 4.6, 8.0, "mid <- floor((lo + hi) / 2)", "process", w=3.8)
    d2 = Node(ax, 4.6, 6.5, "key = A[mid] ?\n(1 comparison)", "decision", w=3.4, h=1.5)
    d3 = Node(ax, 4.6, 4.8, "key < A[mid] ?", "decision", w=3.2, h=1.3)
    hi = Node(ax, 2.0, 3.2, "hi <- mid - 1", "process", w=2.4)
    lo = Node(ax, 7.2, 3.2, "lo <- mid + 1", "process", w=2.4)
    r_nf = Node(ax, 8.0, 9.4, "return -1\n(not found)", "terminal", w=2.2, h=1.0, size=8.5)
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
    ax.text(4.6, 1.5, "loop: Theta(1) extra space (lo, hi, mid)", ha="center", fontsize=8.5, style="italic")
    # recursive version
    entry = Node(ax, 14.6, 12.7, "BinarySearchRecursive(A, lo, hi, key)", "terminal", w=5.6)
    e1 = Node(ax, 14.6, 11.3, "lo > hi ?", "decision", w=2.8, h=1.3)
    base = Node(ax, 11.5, 11.3, "return -1\n(base case)", "terminal", w=2.2, h=1.0, size=8.5)
    emid = Node(ax, 14.6, 9.9, "mid <- floor((lo + hi) / 2)", "process", w=3.8)
    e2 = Node(ax, 14.6, 8.4, "key = A[mid] ?\n(1 comparison)", "decision", w=3.4, h=1.5)
    efound = Node(ax, 17.8, 8.4, "return mid\n(found)", "terminal", w=2.2, h=1.0, size=8.5)
    e3 = Node(ax, 14.6, 6.7, "key < A[mid] ?", "decision", w=3.2, h=1.3)
    left = Node(ax, 12.2, 4.9, "return BinarySearch-\nRecursive(A, lo, mid-1, key)", "call", w=3.7,
                h=1.0, size=8)
    right = Node(ax, 17.1, 4.9, "return BinarySearch-\nRecursive(A, mid+1, hi, key)", "call", w=3.7,
                 h=1.0, size=8)
    arrow(ax, [entry.bottom(), e1.top()])
    arrow(ax, [e1.left(), base.right()], "Yes", 0, dx=-0.55, dy=0.15)
    arrow(ax, [e1.bottom(), emid.top()], "No", 0)
    arrow(ax, [emid.bottom(), e2.top()])
    arrow(ax, [e2.right(), efound.left()], "Yes", 0, dx=0.02, dy=0.15)
    arrow(ax, [e2.bottom(), e3.top()], "No", 0)
    arrow(ax, [e3.left(), (left.x, e3.y), left.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [e3.right(), (right.x, e3.y), right.top()], "No", 0, dx=0.15)
    arrow(ax, [left.left(), (10.05, left.y), (10.05, entry.y), entry.left()], "recursive call", 1,
          dx=0.1, dy=1.6, dashed=True)
    arrow(ax, [right.right(), (19.15, right.y), (19.15, entry.y), entry.right()], dashed=True)
    ax.text(14.6, 3.6, "one recursive call per activation on half of the range:\n"
            "T(n) = T(n/2) + 1  ->  depth floor(log2 n) + 1  ->  Theta(log n) stack space",
            ha="center", va="top", fontsize=8.5, style="italic")
    save(fig, "flowchart_s2_binary.png")


# --------------------------------------------------------------------------- S2 substitution chain
def s2_substitution_chain():
    fig, ax = plt.subplots(figsize=(11, 7.4))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 10.6)
    ax.axis("off")
    ax.set_title("S2 - backward substitution of T(n) = T(n/2) + 1, T(1) = 1 (example n = 1,024)",
                 fontsize=12, fontweight="bold")
    ax.text(2.2, 10.0, "size still to search", ha="center", fontsize=9.5, fontweight="bold")
    ax.text(9.6, 10.0, "expression after i substitutions", ha="center", fontsize=9.5, fontweight="bold")
    rows = [("n = 1,024", "T(n) = T(n/2) + 1", "i = 1"),
            ("n/2 = 512", "T(n) = [T(n/4) + 1] + 1 = T(n/2²) + 2", "i = 2"),
            ("n/4 = 256", "T(n) = [T(n/8) + 1] + 2 = T(n/2³) + 3", "i = 3"),
            ("n/8 = 128", "T(n) = [T(n/16) + 1] + 3 = T(n/2⁴) + 4", "i = 4"),
            ("...", "...", ""),
            ("n/2ⁱ", "T(n) = T(n/2ⁱ) + i   (general pattern)", "i"),
            ("n/2ᵏ = 1", "stop at T(1):  n/2ⁱ = 1  ⇔  i = log₂ n = k = 10", "i = k")]
    ys = [9.1 - 1.12 * r for r in range(len(rows))]
    for (size, expr, tag), y in zip(rows, ys):
        if size == "...":
            ax.text(2.2, y, "⋮", ha="center", va="center", fontsize=16)
            ax.text(9.6, y, "⋮", ha="center", va="center", fontsize=16)
            continue
        Node(ax, 2.2, y, size, "process", w=3.0, h=0.7, size=9.5)
        Node(ax, 9.6, y, expr, "process", w=8.4, h=0.7, size=9.5)
        ax.text(14.2, y, tag, ha="center", va="center", fontsize=9, color="#555555")
        arrow(ax, [(3.7, y), (5.4, y)])
    for y0, y1 in zip(ys[:-1], ys[1:]):
        if y1 == ys[4] or y0 == ys[4]:
            continue
        arrow(ax, [(2.2, y0 - 0.35), (2.2, y1 + 0.35)])
        ax.text(2.35, (y0 + y1) / 2, "+1 comparison, discard half", fontsize=7.5, color="#7f3f00",
                va="center")
    res = Node(ax, 7.5, 0.9, "T(n) = T(1) + log₂ n = log₂ n + 1    (n = 1,024: 11 comparisons;  any n: "
               "⌊log₂ n⌋ + 1 → Θ(log n))", "terminal", w=13.6, h=0.8, size=10)
    arrow(ax, [(9.6, ys[-1] - 0.35), (9.6, res.y + 0.4)])
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "s2_backward_substitution.png", dpi=150)
    plt.close(fig)
    print(OUT_DIR / "s2_backward_substitution.png")


# --------------------------------------------------------------------------- recursion trees
def tree_level(ax, x0, x1, y, count, label, size, color, max_w=1.4):
    """Draw `count` equally spaced nodes on one level; return their x positions."""
    xs = [x0 + (x1 - x0) * (k + 0.5) / count for k in range(count)]
    w = min(max_w, 0.85 * (x1 - x0) / count)
    for x in xs:
        ax.add_patch(FancyBboxPatch((x - w / 2, y - 0.25), w, 0.5, boxstyle="round,pad=0,rounding_size=0.12",
                                    facecolor=color, edgecolor="#333333", lw=0.8))
        ax.text(x, y, label, ha="center", va="center", fontsize=size)
    return xs


def tree_edges(ax, parents, children, y_parent, y_child):
    per = len(children) // len(parents)
    for p, x in enumerate(parents):
        for c in children[p * per:(p + 1) * per]:
            ax.plot([x, c], [y_parent - 0.25, y_child + 0.25], color="#666666", lw=0.6)


def draw_tree(ax, a, labels, costs, total, title, x0=0.2, x1=9.4, color="#dbe8f6", max_w=1.4):
    """Recursion tree with `a` children per node: three explicit levels, a gap, the leaves, and level costs."""
    ax.set_xlim(0, 15)
    ax.set_ylim(-0.6, 7.2)
    ax.axis("off")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ys = [6.3, 5.1, 3.9]
    prev = None
    for lvl, y in enumerate(ys):
        size = 9 if lvl < 2 else (7 if a ** lvl <= 8 else 5.5)
        xs = tree_level(ax, x0, x1, y, a ** lvl, labels[lvl], size, color, max_w)
        if prev:
            tree_edges(ax, prev, xs, ys[lvl - 1], y)
        prev = xs
    ax.text((x0 + x1) / 2, 2.85, "⋮", ha="center", va="center", fontsize=18)
    ax.add_patch(Rectangle((x0, 1.4), x1 - x0, 0.5, facecolor="#d9ead3", edgecolor="#333333", lw=0.8))
    ax.text((x0 + x1) / 2, 1.65, labels[3], ha="center", va="center", fontsize=8.5)
    ax.text(12.2, 6.95, "cost of the level", ha="center", fontsize=9, fontweight="bold")
    for y, text in zip(ys + [2.85, 1.65], costs):
        ax.text(12.2, y, text, ha="center", va="center", fontsize=9)
        ax.plot([x1 + 0.2, 10.0], [y, y], color="#bbbbbb", lw=0.6, ls=":")
    ax.text(7.5, 0.3, total, ha="center", va="center", fontsize=9.5, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="#fff2cc", edgecolor="#333333"))


def m4_recursion_trees():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 10.4))
    draw_tree(ax1, 4, ["n", "n/2", "n/4", "leaves: 4ᵏ = n² sub-problems of size 1 (k = log₂ n)"],
              ["n", "4 · n/2 = 2n", "16 · n/4 = 4n", "level i: 4ⁱ · n/2ⁱ = 2ⁱ n", "n² · T(1) = n²"],
              "total = n(1 + 2 + … + 2ᵏ⁻¹) + n² = n(n − 1) + n² = 2n² − n  →  Θ(n²)  "
              "(n = 1,024: 2,096,128)",
              "(a) M4 current design: T(n) = 4T(n/2) + n  –  level costs double, the leaves dominate (Case 1)")
    draw_tree(ax2, 2, ["n", "n/2", "n/4", "leaves: 2ᵏ = n sub-problems of size 1"],
              ["n", "2 · n/2 = n", "4 · n/4 = n", "level i: 2ⁱ · n/2ⁱ = n", "n · T(1) = n"],
              "total = n · log₂ n (internal levels) + n (leaves) = n log₂ n + n  →  Θ(n log n)  "
              "(n = 1,024: 11,264)",
              "(b) M4 redesign: T(n) = 2T(n/2) + n  –  every one of the log₂ n + 1 levels costs n (Case 2)",
              color="#e8f3e0")
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "m4_recursion_trees.png", dpi=150)
    plt.close(fig)
    print(OUT_DIR / "m4_recursion_trees.png")


def m5_recursion_tree():
    n, k = 1024, 10
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.6), gridspec_kw={"width_ratios": [1.55, 1]})
    draw_tree(ax1, 2, ["n log n", "(n/2) log(n/2)", "(n/4) log(n/4)", "leaves: n sub-problems of size 1"],
              ["n log₂ n", "n (log₂ n − 1)", "n (log₂ n − 2)", "level i: n (log₂ n − i)", "n · T(1) = n"],
              "total = n[k + (k−1) + … + 1] + n = n·k(k+1)/2 + n  →  Θ(n log² n)",
              "(a) M5: T(n) = 2T(n/2) + n log n", color="#fde3cf", max_w=2.6)
    levels = list(range(k)) + ["leaves"]
    costs = [n * (k - i) for i in range(k)] + [n]
    ax2.barh(range(len(levels)), costs, color=["#e69138"] * k + ["#6aa84f"], edgecolor="#333333", lw=0.6)
    ax2.set_yticks(range(len(levels)))
    ax2.set_yticklabels([f"level {i}" if i != "leaves" else "leaves" for i in levels], fontsize=8)
    ax2.invert_yaxis()
    for r, c in enumerate(costs):
        ax2.text(c + 150, r, f"{c:,}", va="center", fontsize=7.5)
    ax2.set_xlim(0, 12500)
    ax2.set_xlabel("operations on the level (n = 1,024, k = log₂ n = 10)")
    ax2.set_title(f"(b) level costs n(k − i) fall by n per level\nsum = {sum(costs):,} = "
                  f"1,024·10·11/2 + 1,024", fontsize=10, fontweight="bold")
    ax2.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "m5_recursion_tree.png", dpi=150)
    plt.close(fig)
    print(OUT_DIR / "m5_recursion_tree.png")
    assert sum(costs) == n * k * (k + 1) // 2 + n == 57344
    assert math.log2(n) == k


def main():
    flowchart_m1_nested()
    flowchart_m1_hash()
    flowchart_m2()
    flowchart_s1()
    flowchart_s2()
    s2_substitution_chain()
    m4_recursion_trees()
    m5_recursion_tree()


if __name__ == "__main__":
    main()
