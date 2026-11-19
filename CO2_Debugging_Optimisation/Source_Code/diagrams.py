"""
SentinelOps alert triage - flowcharts for the report (saved to ../Report/diagrams).

Part B: one flowchart for each corrected (debugged brute-force) function and each optimised function:
  flow_1_sort_corrected / flow_1_sort_optimised        bubble sort with early exit / adaptive merge sort
  flow_2_find_corrected / flow_2_find_optimised        sequential search / sentinel search + hash index
  flow_3_match_corrected / flow_3_match_optimised      brute-force matching / Horspool
  flow_4_closest_corrected / flow_4_closest_optimised  brute-force closest pair / divide and conquer
Part C: flow_debugging_process - reproduce -> isolate -> fix -> re-test loop used for every defect.

Standard symbols: terminal = rounded box, process = rectangle, decision = diamond with Yes/No labels,
input/output = parallelogram, predefined process / recursive call = rectangle with side bars.
"""
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


# --------------------------------------------------------------------------- Part B flowcharts: sorting
def sort_corrected():
    fig, ax = new_canvas(11, 4.0, 18.0, "SortAlerts_Corrected - bubble sort with early exit (D1-D4 fixed)")
    c = 4.8
    start = Node(ax, c, 17.3, "Start", "terminal", w=2.2)
    inp = Node(ax, c, 16.3, "Input: alerts A[0..n-1]", "io", w=4.4)
    init = Node(ax, c, 15.2, "B <- copy of A  (D1);   i <- 0", "process", w=4.8)
    d_i = Node(ax, c, 13.9, "i <= n - 2 ?", "decision", w=3.0, h=1.3)
    sw = Node(ax, c, 12.5, "swapped <- false (D4);  j <- 0", "process", w=4.4)
    d_j = Node(ax, c, 11.1, "j <= n - i - 2 ?\n(D2)", "decision", w=3.2, h=1.4, size=8.5)
    d_c = Node(ax, c, 9.1, "ComesBefore(B[j+1], B[j]) ?\n(basic operation; D3 tie\n-> older first)",
               "decision", w=4.8, h=2.0, size=8)
    exch = Node(ax, c, 7.1, "exchange B[j], B[j+1];\nswapped <- true", "process", w=3.8, h=1.0)
    jinc = Node(ax, 8.9, 9.1, "j <- j + 1", "process", w=1.8)
    d_s = Node(ax, 1.5, 11.1, "swapped\n= false ?", "decision", w=2.6, h=1.4, size=8.5)
    iinc = Node(ax, 1.5, 12.9, "i <- i + 1", "process", w=1.9)
    ret = Node(ax, c, 5.4, "return B (sorted copy)", "terminal", w=3.8)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), d_i.top()])
    arrow(ax, [d_i.bottom(), sw.top()], "Yes", 0)
    arrow(ax, [sw.bottom(), d_j.top()])
    arrow(ax, [d_j.bottom(), d_c.top()], "Yes", 0)
    arrow(ax, [d_c.bottom(), exch.top()], "Yes", 0)
    arrow(ax, [d_c.right(), jinc.left()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [exch.right(), (jinc.x, exch.y), jinc.bottom()])
    arrow(ax, [jinc.top(), (jinc.x, d_j.y), d_j.right()])
    arrow(ax, [d_j.left(), d_s.right()], "No", 0, dx=-0.55, dy=0.15)
    arrow(ax, [d_s.top(), iinc.bottom()], "No", 0, dx=0.1, dy=0.05)
    arrow(ax, [iinc.top(), (iinc.x, d_i.y), d_i.left()])
    arrow(ax, [d_s.bottom(), (d_s.x, ret.y), ret.left()], "Yes", 0, dx=0.1, dy=-0.4)
    arrow(ax, [d_i.right(), (10.4, d_i.y), (10.4, ret.y), ret.right()], "No", 0, dx=0.1)
    ax.text(5.5, 4.4, "worst case n(n-1)/2 comparisons -> Theta(n^2);  a pass without exchanges stops early "
            "(best case n - 1)", ha="center", fontsize=8.5, style="italic")
    save(fig, "flow_1_sort_corrected.png")


def sort_optimised():
    fig, ax = new_canvas(11.6, 3.6, 18.2, "SortAlerts_Optimised - stable, adaptive merge sort")
    start = Node(ax, 1.2, 17.4, "Start", "terminal", w=1.8)
    inp = Node(ax, 4.2, 17.4, "Input: A[0..n-1]", "io", w=3.0)
    keys = Node(ax, 8.4, 17.4, "P <- (key(a), a) for all a\nkey = (-severity, timestamp)", "process",
                w=4.6, h=0.9, size=8.5)
    call = Node(ax, 8.4, 16.1, "MergeSort(P, Aux, 0, n)", "call", w=3.8)
    out = Node(ax, 4.0, 16.1, "Output: the alerts of P", "io", w=3.4)
    end = Node(ax, 1.2, 16.1, "End", "terminal", w=1.6)
    arrow(ax, [start.right(), inp.left()])
    arrow(ax, [inp.right(), keys.left()])
    arrow(ax, [keys.bottom(), call.top()])
    arrow(ax, [call.left(), out.right()])
    arrow(ax, [out.left(), end.right()])
    ax.add_patch(Rectangle((0.2, 4.2), 11.2, 11.0, fill=False, ls="--", lw=1.0, ec="#555555"))
    ax.text(0.4, 14.85, "function MergeSort(P, Aux, lo, hi)", fontsize=9, style="italic")
    c = 5.4
    entry = Node(ax, c, 14.2, "MergeSort(P, Aux, lo, hi)", "terminal", w=4.2)
    arrow(ax, [call.bottom(), (call.x, 15.0), (6.6, 15.0), (6.6, entry.y + entry.h / 2)], "first call", 1,
          dx=0.1, dy=-0.35, dashed=True)
    d1 = Node(ax, c, 12.9, "hi - lo < 2 ?", "decision", w=3.0, h=1.3)
    r1 = Node(ax, 9.3, 12.9, "return\n(0 or 1 alert)", "terminal", w=2.4, h=0.9, size=8.5)
    mid = Node(ax, c, 11.5, "mid <- floor((lo + hi) / 2)", "process", w=3.8)
    cl = Node(ax, c, 10.4, "MergeSort(P, Aux, lo, mid)", "call", w=4.0)
    cr = Node(ax, c, 9.3, "MergeSort(P, Aux, mid, hi)", "call", w=4.0)
    d2 = Node(ax, c, 7.8, "P[mid-1].key <= P[mid].key ?\n(halves already in order)", "decision", w=5.0,
              h=1.7, size=8.5)
    r2 = Node(ax, 9.75, 7.8, "return\n(merge skipped)", "terminal", w=2.5, h=0.9, size=8.5)
    merge = Node(ax, c, 6.1, "Aux <- left half;  merge: take P[j] if P[j].key < Aux[i].key\n"
                 "(strict <, stable), else Aux[i];  copy left leftovers", "process", w=6.4, h=1.0, size=7.5)
    r3 = Node(ax, c, 4.8, "return (P[lo..hi-1] sorted)", "terminal", w=4.0)
    arrow(ax, [entry.bottom(), d1.top()])
    arrow(ax, [d1.right(), r1.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d1.bottom(), mid.top()], "No", 0)
    arrow(ax, [mid.bottom(), cl.top()])
    arrow(ax, [cl.bottom(), cr.top()])
    arrow(ax, [cr.bottom(), d2.top()])
    arrow(ax, [d2.right(), r2.left()], "Yes", 0, dx=0.02, dy=0.15)
    arrow(ax, [d2.bottom(), merge.top()], "No", 0)
    arrow(ax, [merge.bottom(), r3.top()])
    arrow(ax, [cl.left(), (0.55, cl.y), (0.55, entry.y), entry.left()], "recursive calls", 1, dx=0.1,
          dy=-1.5, dashed=True)
    arrow(ax, [cr.left(), (0.55, cr.y), (0.55, cl.y)], dashed=True)
    ax.text(5.8, 3.9, "T(n) = 2T(n/2) + (n - 1) -> Theta(n log n);  ordered halves skip the merge "
            "(nearly sorted: ~n comparisons)", ha="center", fontsize=8, style="italic")
    save(fig, "flow_1_sort_optimised.png")


# --------------------------------------------------------------------------- searching
def find_corrected():
    fig, ax = new_canvas(10, 2.6, 14.4, "FindAlert_Corrected - sequential search (D5-D7 fixed)")
    start = Node(ax, 5, 13.6, "Start", "terminal", w=2.2)
    inp = Node(ax, 5, 12.4, "Input: alerts A[0..n-1], id", "io", w=5.0)
    init = Node(ax, 5, 11.1, "i <- 0   (D5: start at index 0)", "process", w=4.4)
    d1 = Node(ax, 5, 9.6, "i <= n - 1 ?", "decision", w=2.8, h=1.3)
    d2 = Node(ax, 5, 7.4, "A[i].alert_id = id ?\n(basic operation; D6\nvalue equality)", "decision", w=4.2,
              h=1.9, size=8.5)
    inc = Node(ax, 8.6, 7.4, "i <- i + 1", "process", w=2.0)
    found = Node(ax, 5.3, 5.3, "Output: return i\n(alert found)", "io", w=3.4, h=1.0)
    notf = Node(ax, 1.6, 5.3, "Output: return -1\n(D7: after the\nwhole scan)", "io", w=2.8, h=1.2, size=8.5)
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
    ax.text(5, 2.9, "found at position i: i + 1 comparisons;  absent: n comparisons (2 tests per element: "
            "i <= n-1 and the id test)", ha="center", fontsize=8.5, style="italic")
    save(fig, "flow_2_find_corrected.png")


def find_optimised():
    fig, ax = new_canvas(17, 1.8, 14.6, "FindAlert_Optimised - sentinel search (left) and hash index for "
                         "repeated look-ups (right)")
    ax.plot([9.1, 9.1], [2.4, 13.6], color="#999999", lw=0.8, ls=":")
    c = 4.5
    start = Node(ax, c, 13.5, "Start", "terminal", w=2.2)
    inp = Node(ax, c, 12.5, "Input: A[0..n-1], id", "io", w=4.0)
    init = Node(ax, c, 11.4, "A[n] <- sentinel with alert_id = id;  i <- 0", "process", w=6.0)
    d = Node(ax, c, 10.0, "A[i].alert_id != id ?\n(only test per element)", "decision", w=4.4, h=1.5,
             size=8.5)
    inc = Node(ax, c, 8.5, "i <- i + 1", "process", w=2.0)
    rem = Node(ax, c, 7.3, "remove A[n]", "process", w=2.6)
    d2 = Node(ax, c, 6.0, "i < n ?", "decision", w=2.4, h=1.1)
    r1 = Node(ax, 2.0, 4.5, "return i\n(found)", "terminal", w=2.2, h=0.9, size=8.5)
    r2 = Node(ax, 7.0, 4.5, "return -1\n(hit the sentinel)", "terminal", w=2.6, h=0.9, size=8.5)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), d.top()])
    arrow(ax, [d.bottom(), inc.top()], "Yes", 0)
    arrow(ax, [inc.left(), (1.0, inc.y), (1.0, d.y), d.left()])
    arrow(ax, [d.right(), (7.8, d.y), (7.8, rem.y), rem.right()], "No", 0, dx=0.05)
    arrow(ax, [rem.bottom(), d2.top()])
    arrow(ax, [d2.left(), (r1.x, d2.y), r1.top()], "Yes", 0, dx=-0.6)
    arrow(ax, [d2.right(), (r2.x, d2.y), r2.top()], "No", 0, dx=0.1)
    ax.text(c, 3.3, "n + 1 id tests at most, no bound test -> Theta(n)\nwith a smaller constant",
            ha="center", va="top", fontsize=8.5, style="italic")
    c2 = 13.0
    b0 = Node(ax, c2, 13.5, "BuildIndex(A, n)  - once per shift", "terminal", w=5.0)
    b1 = Node(ax, c2, 12.4, "H <- empty hash table;  i <- 0", "process", w=4.4)
    b2 = Node(ax, c2, 11.1, "i <= n - 1 ?", "decision", w=2.8, h=1.2)
    b3 = Node(ax, c2, 9.6, "A[i].alert_id in H ?", "decision", w=3.6, h=1.2, size=8.5)
    b4 = Node(ax, c2, 8.2, "H[A[i].alert_id] <- i\n(first occurrence wins)", "process", w=3.8, h=0.9, size=8.5)
    b5 = Node(ax, c2, 7.0, "i <- i + 1", "process", w=2.0)
    bret = Node(ax, 15.8, 11.1, "return H", "terminal", w=1.8)
    arrow(ax, [b0.bottom(), b1.top()])
    arrow(ax, [b1.bottom(), b2.top()])
    arrow(ax, [b2.bottom(), b3.top()], "Yes", 0)
    arrow(ax, [b2.right(), bret.left()], "No", 0, dx=0.0, dy=0.15)
    arrow(ax, [b3.bottom(), b4.top()], "No", 0)
    arrow(ax, [b3.right(), (16.2, b3.y), (16.2, b5.y), b5.right()], "Yes", 0, dx=0.05)
    arrow(ax, [b4.bottom(), b5.top()])
    arrow(ax, [b5.left(), (9.6, b5.y), (9.6, b2.y), b2.left()])
    f0 = Node(ax, c2, 5.7, "IndexFind(H, id)", "terminal", w=3.2)
    f1 = Node(ax, c2, 4.4, "id in H ?\n(one hash lookup)", "decision", w=3.2, h=1.3, size=8.5)
    f2 = Node(ax, 10.4, 3.1, "return H[id]", "terminal", w=2.2)
    f3 = Node(ax, 15.6, 3.1, "return -1", "terminal", w=2.0)
    arrow(ax, [f0.bottom(), f1.top()])
    arrow(ax, [f1.left(), (f2.x, f1.y), f2.top()], "Yes", 0, dx=-0.6)
    arrow(ax, [f1.right(), (f3.x, f1.y), f3.top()], "No", 0, dx=0.1)
    ax.text(c2, 2.2, "build Theta(n) once, then Theta(1) expected per look-up", ha="center", fontsize=8.5,
            style="italic")
    save(fig, "flow_2_find_optimised.png")


# --------------------------------------------------------------------------- string matching
def match_corrected():
    fig, ax = new_canvas(11, 3.0, 20.4, "MatchSignature_Corrected - brute-force matching (D8-D10 fixed)")
    c = 5.0
    start = Node(ax, c, 19.7, "Start", "terminal", w=2.2)
    inp = Node(ax, c, 18.7, "Input: text T (length n), signature P (length m)", "io", w=6.6)
    d0 = Node(ax, c, 17.4, "m = 0 or m > n ?\n(D10)", "decision", w=3.6, h=1.3, size=8.5)
    r0 = Node(ax, 9.2, 17.4, "return [ ]", "terminal", w=2.0)
    init = Node(ax, c, 16.0, "positions <- [ ];  i <- 0", "process", w=3.8)
    d_i = Node(ax, c, 14.7, "i <= n - m ?\n(D8)", "decision", w=2.8, h=1.3, size=8.5)
    rp = Node(ax, 9.0, 14.7, "return positions", "terminal", w=2.8)
    mj = Node(ax, c, 13.3, "matched <- true;  j <- 0", "process", w=3.8)
    d_j = Node(ax, c, 12.0, "j <= m - 1 ?", "decision", w=2.8, h=1.2)
    d_c = Node(ax, c, 10.3, "T[i+j] = P[j] ?\n(1 character comparison)", "decision", w=4.2, h=1.6, size=8.5)
    jinc = Node(ax, 9.0, 10.3, "j <- j + 1", "process", w=1.9)
    mf = Node(ax, c, 8.6, "matched <- false;  break (D9)", "process", w=4.2)
    d_m = Node(ax, c, 7.1, "matched ?", "decision", w=2.6, h=1.1)
    app = Node(ax, c, 5.7, "append i to positions", "process", w=3.6)
    iinc = Node(ax, c, 4.6, "i <- i + 1", "process", w=2.0)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), d0.top()])
    arrow(ax, [d0.right(), r0.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d0.bottom(), init.top()], "No", 0)
    arrow(ax, [init.bottom(), d_i.top()])
    arrow(ax, [d_i.right(), rp.left()], "No", 0, dy=0.15)
    arrow(ax, [d_i.bottom(), mj.top()], "Yes", 0)
    arrow(ax, [mj.bottom(), d_j.top()])
    arrow(ax, [d_j.bottom(), d_c.top()], "Yes", 0)
    arrow(ax, [d_c.right(), jinc.left()], "Yes", 0, dy=0.15)
    arrow(ax, [jinc.top(), (jinc.x, d_j.y), d_j.right()])
    arrow(ax, [d_c.bottom(), mf.top()], "No", 0)
    arrow(ax, [mf.bottom(), d_m.top()])
    arrow(ax, [d_j.left(), (1.5, d_j.y), (1.5, d_m.y), d_m.left()], "No", 0, dx=-0.9)
    arrow(ax, [d_m.bottom(), app.top()], "Yes", 0)
    arrow(ax, [d_m.right(), (8.6, d_m.y), (8.6, iinc.y), iinc.right()], "No", 0, dx=0.05)
    arrow(ax, [app.bottom(), iinc.top()])
    arrow(ax, [iinc.left(), (0.5, iinc.y), (0.5, d_i.y), d_i.left()])
    ax.text(5.5, 3.5, "n - m + 1 alignments x at most m comparisons -> worst case (n - m + 1)m = Theta(nm)",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "flow_3_match_corrected.png")


def match_optimised():
    fig, ax = new_canvas(11, 4.0, 20.4, "MatchSignature_Horspool - right-to-left window, bad-character "
                         "shift")
    c = 5.0
    start = Node(ax, c, 19.7, "Start", "terminal", w=2.2)
    inp = Node(ax, c, 18.7, "Input: text T (length n), signature P (length m)", "io", w=6.6)
    d0 = Node(ax, c, 17.4, "m = 0 or m > n ?", "decision", w=3.6, h=1.2, size=8.5)
    r0 = Node(ax, 9.2, 17.4, "return [ ]", "terminal", w=2.0)
    tbl = Node(ax, c, 16.0, "shift[c] <- m for every character c;\nshift[P[k]] <- m - 1 - k  (k = 0 .. m-2)",
               "process", w=5.8, h=1.0, size=8.5)
    init = Node(ax, c, 14.8, "positions <- [ ];  i <- 0", "process", w=3.8)
    d_i = Node(ax, c, 13.5, "i <= n - m ?", "decision", w=2.8, h=1.2)
    rp = Node(ax, 9.0, 13.5, "return positions", "terminal", w=2.8)
    js = Node(ax, c, 12.2, "j <- m - 1", "process", w=2.2)
    d_c = Node(ax, c, 10.6, "j >= 0 and\nT[i+j] = P[j] ?", "decision", w=4.0, h=1.7, size=8.5)
    jdec = Node(ax, c, 8.7, "j <- j - 1", "process", w=2.0)
    d_f = Node(ax, 8.8, 8.7, "j < 0 ?", "decision", w=2.4, h=1.1)
    app = Node(ax, 8.8, 7.2, "append i", "process", w=2.0)
    sh = Node(ax, c, 5.7, "i <- i + shift[T[i + m - 1]]", "process", w=4.4)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), d0.top()])
    arrow(ax, [d0.right(), r0.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d0.bottom(), tbl.top()], "No", 0)
    arrow(ax, [tbl.bottom(), init.top()])
    arrow(ax, [init.bottom(), d_i.top()])
    arrow(ax, [d_i.right(), rp.left()], "No", 0, dy=0.15)
    arrow(ax, [d_i.bottom(), js.top()], "Yes", 0)
    arrow(ax, [js.bottom(), d_c.top()])
    arrow(ax, [d_c.bottom(), jdec.top()], "Yes", 0)
    arrow(ax, [jdec.left(), (1.6, jdec.y), (1.6, d_c.y), d_c.left()])
    arrow(ax, [d_c.right(), (d_f.x, d_c.y), d_f.top()], "No", 0, dx=0.1)
    arrow(ax, [d_f.bottom(), app.top()], "Yes", 0)
    arrow(ax, [d_f.left(), (6.8, d_f.y), (6.8, sh.y + sh.h / 2)], "No", 0, dx=-0.55, dy=0.12)
    arrow(ax, [app.bottom(), (app.x, sh.y), sh.right()])
    arrow(ax, [sh.left(), (0.6, sh.y), (0.6, d_i.y), d_i.left()])
    ax.text(5.5, 4.6, "shift table Theta(m + alphabet); typical text ~ n/m windows checked, worst case "
            "Theta(nm)", ha="center", fontsize=8.5, style="italic")
    save(fig, "flow_3_match_optimised.png")


# --------------------------------------------------------------------------- closest pair
def closest_corrected():
    fig, ax = new_canvas(11.2, 3.6, 18.2, "ClosestAlertPair_Corrected - brute force over all pairs "
                         "(D11-D14 fixed)")
    c = 5.0
    start = Node(ax, c, 17.5, "Start", "terminal", w=2.2)
    inp = Node(ax, c, 16.5, "Input: alerts A[0..n-1] with (x, y)", "io", w=5.4)
    init = Node(ax, c, 15.4, "best <- inf;  bi, bj <- -1 (D11);  i <- 0", "process", w=5.4)
    d_i = Node(ax, c, 14.1, "i <= n - 1 ?", "decision", w=2.8, h=1.2)
    j0 = Node(ax, c, 12.8, "j <- i + 1   (D12)", "process", w=2.8)
    d_j = Node(ax, c, 11.5, "j <= n - 1 ?", "decision", w=2.8, h=1.2)
    dist = Node(ax, c, 10.0, "dx <- A[i].x - A[j].x;  dy <- A[i].y - A[j].y (D13)\n"
                "d <- sqrt(dx^2 + dy^2)   (basic operation)", "process", w=6.4, h=1.0, size=8.5)
    d_b = Node(ax, c, 8.5, "d < best ?", "decision", w=2.6, h=1.1)
    upd = Node(ax, c, 7.1, "best <- d;  bi <- i;  bj <- j  (D14)", "process", w=4.6)
    jinc = Node(ax, 9.6, 8.5, "j <- j + 1", "process", w=1.9)
    iinc = Node(ax, 1.4, 12.8, "i <- i + 1", "process", w=1.9)
    ret = Node(ax, c, 5.6, "return (best, bi, bj)", "terminal", w=3.6)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), d_i.top()])
    arrow(ax, [d_i.bottom(), j0.top()], "Yes", 0)
    arrow(ax, [j0.bottom(), d_j.top()])
    arrow(ax, [d_j.bottom(), dist.top()], "Yes", 0)
    arrow(ax, [dist.bottom(), d_b.top()])
    arrow(ax, [d_b.bottom(), upd.top()], "Yes", 0)
    arrow(ax, [d_b.right(), jinc.left()], "No", 0, dy=0.15)
    arrow(ax, [upd.right(), (jinc.x, upd.y), jinc.bottom()])
    arrow(ax, [jinc.top(), (jinc.x, 9.35), (8.65, 9.35), (8.65, d_j.y), d_j.right()])
    arrow(ax, [d_j.left(), (iinc.x, d_j.y), iinc.bottom()], "No", 0, dx=-0.9)
    arrow(ax, [iinc.top(), (iinc.x, d_i.y), d_i.left()])
    arrow(ax, [d_i.right(), (10.8, d_i.y), (10.8, ret.y), ret.right()], "No", 0, dx=0.1)
    ax.text(5.6, 4.3, "every unordered pair once: n(n-1)/2 distance computations -> Theta(n^2)",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "flow_4_closest_corrected.png")


def closest_optimised():
    fig, ax = new_canvas(12.6, 2.6, 18.4, "ClosestAlertPair_DC - divide and conquer with squared distances")
    start = Node(ax, 1.2, 17.6, "Start", "terminal", w=1.8)
    inp = Node(ax, 4.1, 17.6, "Input: A[0..n-1]", "io", w=3.0)
    d0 = Node(ax, 7.4, 17.6, "n < 2 ?", "decision", w=2.2, h=1.0)
    r0 = Node(ax, 10.7, 17.6, "return (inf, -1, -1)", "terminal", w=3.0)
    px = Node(ax, 7.4, 16.3, "Px <- points sorted by x (once)", "process", w=4.4)
    call = Node(ax, 3.3, 16.3, "ClosestRec(Px, 0, n)", "call", w=3.4)
    fin = Node(ax, 3.3, 15.2, "return (sqrt(d^2), i, j)", "terminal", w=3.4)
    arrow(ax, [start.right(), inp.left()])
    arrow(ax, [inp.right(), d0.left()])
    arrow(ax, [d0.right(), r0.left()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [d0.bottom(), px.top()], "No", 0)
    arrow(ax, [px.left(), call.right()])
    arrow(ax, [call.bottom(), fin.top()])
    ax.add_patch(Rectangle((0.2, 3.0), 12.2, 11.6, fill=False, ls="--", lw=1.0, ec="#555555"))
    ax.text(0.4, 14.25, "function ClosestRec(Px, lo, hi)", fontsize=9, style="italic")
    c = 6.2
    entry = Node(ax, c, 13.6, "ClosestRec(Px, lo, hi)", "terminal", w=3.8)
    arrow(ax, [call.left(), (0.5, call.y), (0.5, 13.9), (entry.x - entry.w / 2, 13.9)], "first call", 1,
          dx=0.1, dy=-0.5, dashed=True)
    d1 = Node(ax, c, 12.3, "hi - lo <= 3 ?", "decision", w=3.0, h=1.2)
    base = Node(ax, 2.5, 12.3, "brute force (<= 3 pairs);\nreturn (best, points by y)", "terminal",
                w=3.6, h=0.9, size=8)
    mid = Node(ax, c, 11.0, "mid <- floor((lo + hi) / 2);  xm <- Px[mid].x", "process", w=5.4)
    cl = Node(ax, c, 9.9, "(bl, L) <- ClosestRec(Px, lo, mid)", "call", w=5.0)
    cr = Node(ax, c, 8.8, "(br, R) <- ClosestRec(Px, mid, hi)", "call", w=5.0)
    comb = Node(ax, c, 7.7, "best <- min(bl, br);  Y <- merge of L and R by y", "process", w=6.0)
    strip = Node(ax, c, 6.6, "S <- points p of Y with (p.x - xm)^2 < best.d^2   (strip of width 2 delta)",
                 "process", w=8.6, size=8.5)
    scan = Node(ax, c, 5.3, "for each s in S: compare with the next t while (S[t].y - S[s].y)^2 < best.d^2\n"
                "(at most 7 successors);  best <- min(best, squared distance)", "process", w=9.8, h=1.0,
                size=8)
    ret = Node(ax, c, 3.9, "return (best, Y)", "terminal", w=3.0)
    arrow(ax, [entry.bottom(), d1.top()])
    arrow(ax, [d1.left(), base.right()], "Yes", 0, dx=-0.55, dy=0.15)
    arrow(ax, [d1.bottom(), mid.top()], "No", 0)
    for a, b in ((mid, cl), (cl, cr), (cr, comb), (comb, strip), (strip, scan), (scan, ret)):
        arrow(ax, [a.bottom(), b.top()])
    arrow(ax, [cl.right(), (11.4, cl.y), (11.4, 13.5), (entry.x + entry.w / 2, 13.5)], "recursive calls", 1,
          dx=-2.6, dy=0.25, dashed=True)
    arrow(ax, [cr.right(), (12.0, cr.y), (12.0, 13.75), (entry.x + entry.w / 2, 13.75)], dashed=True)
    ax.text(6.3, 2.75, "T(n) = 2T(n/2) + Theta(n) -> Theta(n log n) distance computations", ha="center",
            fontsize=8.5, style="italic")
    save(fig, "flow_4_closest_optimised.png")


# --------------------------------------------------------------------------- Part C: debugging process
def debugging_process():
    fig, ax = new_canvas(12.6, 2.8, 19.4, "Systematic debugging process applied to each of the 14 defects")
    c = 6.0
    start = Node(ax, c, 18.7, "Start: given faulty program original_alert_triage.py", "terminal", w=6.6)
    rep = Node(ax, c, 17.5, "REPRODUCE: run the 18 defect tests + 13 general tests\n"
               "on the untouched original (0/18 and 6/13 pass)", "process", w=7.4, h=1.0, size=8.5)
    iso = Node(ax, c, 16.1, "ISOLATE: trace the failing function with sys.settrace,\n"
               "print executed lines + loop variables -> faulty line(s)", "process", w=7.4, h=1.0, size=8.5)
    fix = Node(ax, c, 14.7, "FIX: apply ONE minimal line-level patch (# FIX Dn)", "process", w=7.0, size=8.5)
    ret = Node(ax, c, 13.5, "RE-TEST: reload the patched module, run ALL tests", "call", w=7.0, size=8.5)
    d1 = Node(ax, c, 11.9, "defect test\nFAIL -> PASS ?", "decision", w=3.6, h=1.6, size=8.5)
    d2 = Node(ax, c, 9.9, "regression: a previously\npassing test now fails ?", "decision", w=4.8, h=1.8,
              size=8.5)
    d3 = Node(ax, c, 7.9, "defects left ?\n(sort -> search ->\nmatch -> closest)", "decision", w=4.2, h=1.8,
              size=8)
    ver = Node(ax, c, 6.2, "VERIFY: fully patched text = corrected_alert_triage.py\n(original + 14 line fixes, not a "
               "rewrite)", "process", w=7.4, h=1.0, size=8.5)
    out = Node(ax, c, 4.9, "Output: corrected program, 31/31 tests pass", "io", w=6.4, size=8.5)
    end = Node(ax, c, 3.8, "End", "terminal", w=2.0)
    for a, b in ((start, rep), (rep, iso), (iso, fix), (fix, ret), (ret, d1)):
        arrow(ax, [a.bottom(), b.top()])
    arrow(ax, [d1.bottom(), d2.top()], "Yes", 0)
    arrow(ax, [d2.bottom(), d3.top()], "No", 0)
    arrow(ax, [d3.bottom(), ver.top()], "No", 0)
    arrow(ax, [ver.bottom(), out.top()])
    arrow(ax, [out.bottom(), end.top()])
    arrow(ax, [d1.left(), (1.5, d1.y), (1.5, iso.y), iso.left()], "No: isolate again", 0, dx=-2.3, dy=0.15)
    arrow(ax, [d2.right(), (11.0, d2.y), (11.0, fix.y), fix.right()], "Yes: revert, refine fix", 0,
          dx=-0.1, dy=0.2)
    arrow(ax, [d3.right(), (12.0, d3.y), (12.0, iso.y), iso.right()], "Yes: next defect", 0, dx=-0.3,
          dy=0.2)
    save(fig, "flow_debugging_process.png")


def main():
    sort_corrected()
    sort_optimised()
    find_corrected()
    find_optimised()
    match_corrected()
    match_optimised()
    closest_corrected()
    closest_optimised()
    debugging_process()


if __name__ == "__main__":
    main()
