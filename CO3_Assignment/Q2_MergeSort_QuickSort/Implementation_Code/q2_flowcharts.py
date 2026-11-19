"""q2_flowcharts.py - flowcharts of Merge Sort (with Merge) and Quick Sort (with Lomuto partition, pivot = last).

Standard symbols (see flowchart_helpers.py). Writes ../Pseudocode/q2_flowchart_merge_sort.png and
../Pseudocode/q2_flowchart_quick_sort.png.
Run:  py q2_flowcharts.py
"""
import os

from flowchart_helpers import Node, arrow, new_canvas, save

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Pseudocode")


def merge_sort_chart():
    fig, ax = new_canvas(18, 4.2, 16.2, "Merge Sort - MergeSort(A, lo, hi) and Merge(A, lo, mid, hi)")
    # ---- MergeSort (left column)
    s = Node(ax, 3.5, 15.3, "MergeSort(A, lo, hi)", "terminal", w=4.4)
    d = Node(ax, 3.5, 13.8, "lo >= hi ?", "decision", w=2.8, h=1.2)
    mid = Node(ax, 3.5, 12.2, "mid <- floor((lo + hi) / 2)\n(DIVIDE: by position)", "process", w=4.4, h=1.0)
    c1 = Node(ax, 3.5, 10.6, "MergeSort(A, lo, mid)\n(CONQUER left half)", "call", w=4.4, h=1.0)
    c2 = Node(ax, 3.5, 9.1, "MergeSort(A, mid + 1, hi)\n(CONQUER right half)", "call", w=4.4, h=1.0)
    c3 = Node(ax, 3.5, 7.6, "Merge(A, lo, mid, hi)\n(COMBINE)", "call", w=4.4, h=1.0)
    ret = Node(ax, 3.5, 5.9, "return", "terminal", w=2.4)
    arrow(ax, [s.bottom(), d.top()])
    arrow(ax, [d.bottom(), mid.top()], "No", 0)
    arrow(ax, [d.left(), (0.6, d.y), (0.6, ret.y), ret.left()], "Yes (0 or 1 order)", 0, dx=-1.25, dy=-0.45)
    for a, b in ((mid, c1), (c1, c2), (c2, c3), (c3, ret)):
        arrow(ax, [a.bottom(), b.top()])
    # ---- Merge (right column)
    ms = Node(ax, 11.5, 15.3, "Merge(A, lo, mid, hi)", "terminal", w=4.4)
    cp = Node(ax, 11.5, 14.0, "copy A[lo..hi] to AUX  (n moves)\ni <- lo;  j <- mid + 1;  k <- lo", "process",
              w=5.6, h=1.0)
    lp = Node(ax, 11.5, 12.5, "k <= hi ?", "decision", w=2.8, h=1.2)
    end = Node(ax, 8.2, 12.5, "return", "terminal", w=2.2)
    d1 = Node(ax, 11.5, 10.9, "i > mid ?\n(left exhausted)", "decision", w=3.2, h=1.3, size=8.5)
    d2 = Node(ax, 11.5, 9.3, "j > hi ?\n(right exhausted)", "decision", w=3.2, h=1.3, size=8.5)
    d3 = Node(ax, 11.5, 7.6, "AUX[j] < AUX[i] ?\n(1 comparison)", "decision", w=3.8, h=1.5, size=8.5)
    tr = Node(ax, 15.3, 10.9, "take right:\nA[k] <- AUX[j]; j <- j + 1", "process", w=3.6, h=1.0, size=8.5)
    tl = Node(ax, 8.0, 9.3, "take left (ties: stable):\nA[k] <- AUX[i]; i <- i + 1", "process", w=3.6, h=1.0,
              size=8.5)
    inc = Node(ax, 11.5, 5.9, "k <- k + 1", "process", w=2.4)
    arrow(ax, [ms.bottom(), cp.top()])
    arrow(ax, [cp.bottom(), lp.top()])
    arrow(ax, [lp.left(), end.right()], "No", 0, dx=-0.6, dy=0.15)
    arrow(ax, [lp.bottom(), d1.top()], "Yes", 0)
    arrow(ax, [d1.right(), tr.left()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [d1.bottom(), d2.top()], "No", 0)
    arrow(ax, [d2.left(), tl.right()], "Yes", 0, dx=-0.55, dy=0.15)
    arrow(ax, [d2.bottom(), d3.top()], "No", 0)
    arrow(ax, [d3.right(), (tr.x, d3.y), tr.bottom()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [d3.left(), (tl.x, d3.y), tl.bottom()], "No", 0, dx=-0.6, dy=0.15)
    arrow(ax, [tr.right(), (17.4, tr.y), (17.4, inc.y), inc.right()])
    arrow(ax, [tl.left(), (5.95, tl.y), (5.95, 6.6), (inc.x - 0.6, 6.6), (inc.x - 0.6, inc.y + 0.4)])
    arrow(ax, [inc.bottom(), (inc.x, 5.0), (17.8, 5.0), (17.8, lp.y), lp.right()], dashed=True)
    ax.text(9, 4.5, "Division never looks at the data: halves ceil(m/2) | floor(m/2), depth ceil(log2 n); "
            "each level merges n orders (<= n - 1 comparisons)  ->  T(n) = 2T(n/2) + n - 1", ha="center",
            fontsize=8.5, style="italic")
    save(fig, os.path.join(OUT, "q2_flowchart_merge_sort.png"))


def quick_sort_chart():
    fig, ax = new_canvas(18.2, 4.2, 16.2, "Quick Sort - QuickSort(A, lo, hi) and Lomuto Partition, pivot = LAST element")
    s = Node(ax, 3.5, 15.3, "QuickSort(A, lo, hi)", "terminal", w=4.4)
    d = Node(ax, 3.5, 13.8, "lo >= hi ?", "decision", w=2.8, h=1.2)
    p = Node(ax, 3.5, 12.2, "p <- Partition(A, lo, hi)\n(DIVIDE: by value, pivot A[hi])", "call", w=4.6, h=1.0)
    rec = Node(ax, 3.5, 10.6, "record (depth, p - lo, hi - p)\n(partition sizes L | R)", "process", w=4.6, h=1.0)
    c1 = Node(ax, 3.5, 9.1, "QuickSort(A, lo, p - 1)\n(CONQUER left part, L keys)", "call", w=4.6, h=1.0)
    c2 = Node(ax, 3.5, 7.6, "QuickSort(A, p + 1, hi)\n(CONQUER right part, R keys)", "call", w=4.6, h=1.0)
    ret = Node(ax, 3.5, 5.9, "return (no combine step)", "terminal", w=4.0)
    arrow(ax, [s.bottom(), d.top()])
    arrow(ax, [d.bottom(), p.top()], "No", 0)
    arrow(ax, [d.left(), (0.6, d.y), (0.6, ret.y), ret.left()], "Yes", 0, dx=-0.5, dy=0.2)
    for a, b in ((p, rec), (rec, c1), (c1, c2), (c2, ret)):
        arrow(ax, [a.bottom(), b.top()])
    ps = Node(ax, 11.5, 15.3, "Partition(A, lo, hi)", "terminal", w=4.4)
    init = Node(ax, 11.5, 14.0, "x <- A[hi]   (pivot = last element)\ni <- lo - 1;  j <- lo", "process", w=5.6,
                h=1.0)
    lp = Node(ax, 11.5, 12.5, "j <= hi - 1 ?", "decision", w=3.0, h=1.2)
    fin = Node(ax, 16.1, 12.5, "swap A[i + 1], A[hi]\n(pivot to final place)", "process", w=3.6, h=1.0, size=8.5)
    out = Node(ax, 16.1, 11.0, "return p = i + 1", "terminal", w=3.0, h=0.8, size=8.5)
    cmp_ = Node(ax, 11.5, 10.8, "A[j] <= x ?\n(1 comparison)", "decision", w=3.4, h=1.4)
    sw = Node(ax, 11.5, 9.1, "i <- i + 1\nswap A[i], A[j]  (if i != j)", "process", w=4.2, h=1.0)
    inc = Node(ax, 11.5, 7.6, "j <- j + 1", "process", w=2.4)
    arrow(ax, [ps.bottom(), init.top()])
    arrow(ax, [init.bottom(), lp.top()])
    arrow(ax, [lp.right(), fin.left()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [fin.bottom(), out.top()])
    arrow(ax, [lp.bottom(), cmp_.top()], "Yes", 0)
    arrow(ax, [cmp_.bottom(), sw.top()], "Yes", 0)
    arrow(ax, [cmp_.right(), (13.95, cmp_.y), (13.95, inc.y), inc.right()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [sw.bottom(), inc.top()])
    arrow(ax, [inc.left(), (8.6, inc.y), (8.6, lp.y), lp.left()], dashed=True)
    ax.text(9.1, 5.2, "every partition of m keys makes m - 1 comparisons; split L | R decides the tree:", ha="center",
            fontsize=8.5, style="italic")
    ax.text(9.1, 4.6, "L = R (designed balanced input) -> T(n) = 2T(n/2) + n - 1 = Theta(n log n);   "
            "L = m - 1, R = 0 (sorted export) -> T(n) = T(n - 1) + n - 1 = n(n - 1)/2", ha="center", fontsize=8.5,
            style="italic")
    save(fig, os.path.join(OUT, "q2_flowchart_quick_sort.png"))


def main():
    merge_sort_chart()
    quick_sort_chart()


if __name__ == "__main__":
    main()
