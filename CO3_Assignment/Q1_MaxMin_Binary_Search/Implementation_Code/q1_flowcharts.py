"""q1_flowcharts.py - flowcharts of the two Q1 algorithms (standard flowchart symbols, matplotlib).

Writes to ../Pseudocode/:
  q1_flowchart_maxmin_dc.png        divide-and-conquer Max-Min (MaxMinDC)
  q1_flowchart_binary_search.png    recursive binary search (BinarySearch)
Run:  py q1_flowcharts.py
"""
import os

from flowchart_helpers import Node, arrow, new_canvas, save

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Pseudocode")


def flowchart_maxmin():
    fig, ax = new_canvas(13, 0.2, 17.6, "Divide-and-Conquer Max-Min: MaxMinDC(A, lo, hi)")
    start = Node(ax, 6.5, 16.9, "MaxMinDC(A, lo, hi)", "terminal", w=4.4)
    d1 = Node(ax, 6.5, 15.4, "lo = hi ?\n(one reading)", "decision", w=3.4, h=1.5)
    base1 = Node(ax, 11.0, 15.4, "return (A[lo], A[lo])\n0 comparisons", "terminal", w=3.6, h=1.0, size=8.5)
    d2 = Node(ax, 6.5, 13.4, "hi = lo + 1 ?\n(two readings)", "decision", w=3.6, h=1.5)
    d3 = Node(ax, 11.0, 13.4, "A[lo] < A[hi] ?\n1 comparison", "decision", w=3.4, h=1.5, size=8.5)
    r1 = Node(ax, 11.0, 11.6, "return (A[hi], A[lo])  if Yes\nreturn (A[lo], A[hi])  if No",
              "terminal", w=3.6, h=1.0, size=8)
    div = Node(ax, 6.5, 11.3, "DIVIDE: k <- LeftPartSize(hi - lo + 1)\n('half': ceil(n/2); 'even': even size)",
               "process", w=5.0, h=1.0, size=8.5)
    c1 = Node(ax, 6.5, 9.7, "(max1, min1) <- MaxMinDC(A, lo, lo + k - 1)", "call", w=6.0, size=8.5)
    c2 = Node(ax, 6.5, 8.5, "(max2, min2) <- MaxMinDC(A, lo + k, hi)", "call", w=6.0, size=8.5)
    d4 = Node(ax, 6.5, 6.9, "max1 > max2 ?\n(combine comparison 1)", "decision", w=4.2, h=1.5, size=8.5)
    m1 = Node(ax, 2.2, 5.4, "max <- max1", "process", w=2.4)
    m2 = Node(ax, 10.8, 5.4, "max <- max2", "process", w=2.4)
    d5 = Node(ax, 6.5, 4.0, "min1 < min2 ?\n(combine comparison 2)", "decision", w=4.2, h=1.5, size=8.5)
    n1 = Node(ax, 2.2, 2.6, "min <- min1", "process", w=2.4)
    n2 = Node(ax, 10.8, 2.6, "min <- min2", "process", w=2.4)
    end = Node(ax, 6.5, 1.2, "return (max, min)", "terminal", w=3.6)
    arrow(ax, [start.bottom(), d1.top()])
    arrow(ax, [d1.right(), base1.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d1.bottom(), d2.top()], "No", 0)
    arrow(ax, [d2.right(), d3.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d3.bottom(), (d3.x, 12.35), (r1.x, 12.35), r1.top()])
    arrow(ax, [d2.bottom(), div.top()], "No", 0)
    arrow(ax, [div.bottom(), c1.top()])
    arrow(ax, [c1.bottom(), c2.top()])
    arrow(ax, [c2.bottom(), d4.top()])
    arrow(ax, [d4.left(), (m1.x, d4.y), m1.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d4.right(), (m2.x, d4.y), m2.top()], "No", 0, dx=0.2)
    arrow(ax, [m1.bottom(), (m1.x, 4.9), (6.5, 4.9), d5.top()])
    arrow(ax, [m2.bottom(), (m2.x, 4.9), (6.5, 4.9)])
    arrow(ax, [d5.left(), (n1.x, d5.y), n1.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d5.right(), (n2.x, d5.y), n2.top()], "No", 0, dx=0.2)
    arrow(ax, [n1.bottom(), (n1.x, end.y), end.left()])
    arrow(ax, [n2.bottom(), (n2.x, end.y), end.right()])
    ax.text(6.5, 0.45, "C(n) = C(k) + C(n - k) + 2,  C(2) = 1,  C(1) = 0   ->   3n/2 - 2 comparisons for n = 2^k",
            ha="center", fontsize=8.5, style="italic")
    save(fig, os.path.join(OUT, "q1_flowchart_maxmin_dc.png"))


def flowchart_binary_search():
    fig, ax = new_canvas(12, 0.6, 12.6, "Recursive Binary Search: BinarySearch(A, key, lo, hi)")
    start = Node(ax, 6, 11.9, "BinarySearch(A, key, lo, hi)\n(A sorted ascending)", "terminal", w=5.0, h=1.0)
    d1 = Node(ax, 6, 10.3, "lo > hi ?\n(range empty)", "decision", w=3.4, h=1.5)
    nf = Node(ax, 10.2, 10.3, "return -1\n(not found)", "terminal", w=2.6, h=1.0, size=8.5)
    mid = Node(ax, 6, 8.7, "mid <- floor((lo + hi) / 2)", "process", w=4.2)
    d2 = Node(ax, 6, 7.1, "key = A[mid] ?\n(one probe)", "decision", w=3.6, h=1.5)
    fd = Node(ax, 10.2, 7.1, "return mid\n(found)", "terminal", w=2.6, h=1.0, size=8.5)
    d3 = Node(ax, 6, 5.3, "key < A[mid] ?", "decision", w=3.4, h=1.4)
    left = Node(ax, 2.6, 3.4, "eliminate A[mid..hi]\nreturn BinarySearch(A, key,\nlo, mid - 1)", "call",
                w=4.0, h=1.3, size=8.5)
    right = Node(ax, 9.4, 3.4, "eliminate A[lo..mid]\nreturn BinarySearch(A, key,\nmid + 1, hi)", "call",
                 w=4.0, h=1.3, size=8.5)
    arrow(ax, [start.bottom(), d1.top()])
    arrow(ax, [d1.right(), nf.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d1.bottom(), mid.top()], "No", 0)
    arrow(ax, [mid.bottom(), d2.top()])
    arrow(ax, [d2.right(), fd.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d2.bottom(), d3.top()], "No", 0)
    arrow(ax, [d3.left(), (left.x, d3.y), left.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d3.right(), (right.x, d3.y), right.top()], "No", 0, dx=0.2)
    arrow(ax, [left.left(), (0.3, left.y), (0.3, start.y), start.left()], "recursive call", 1,
          dx=0.1, dy=1.0, dashed=True)
    arrow(ax, [right.right(), (11.7, right.y), (11.7, 11.2), (start.x + 1.8, 11.2), (start.x + 1.8, 11.4)],
          dashed=True)
    ax.text(6, 1.6, "one recursive call per activation on at most floor(n/2) elements", ha="center",
            fontsize=8.5, style="italic")
    ax.text(6, 1.0, "C(n) = C(floor(n/2)) + 1, C(1) = 1   ->   worst case floor(log2 n) + 1 probes",
            ha="center", fontsize=8.5, style="italic")
    save(fig, os.path.join(OUT, "q1_flowchart_binary_search.png"))


def main():
    flowchart_maxmin()
    flowchart_binary_search()


if __name__ == "__main__":
    main()
