"""q6_flowcharts.py - flowcharts of the Q6 algorithms (CSA06 DAA, Assignment 3 - CO3).

Draws, with the standard symbols of flowchart_helpers.py:
  ../Pseudocode/q6_flowchart_median_of_medians.png      Select(A, k) by Median of Medians (groups of 5)
  ../Pseudocode/q6_flowchart_quickselect.png            QuickSelect with a pluggable pivot rule (random / first)
  ../Pseudocode/q6_flowchart_meet_in_the_middle.png     BestFillMITM(w, W) + SortedSubsetSums(H)
Run:  py -3 q6_flowcharts.py
"""
import os

from matplotlib.patches import Rectangle

from flowchart_helpers import Node, arrow, new_canvas, save

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Pseudocode")


def flowchart_mom():
    fig, ax = new_canvas(12, 3.2, 19.6, "Median of Medians - Select(A, k), k-th smallest (0-based), groups of 5")
    start = Node(ax, 6, 18.9, "Start: Select(A, k)", "terminal", w=3.6)
    d0 = Node(ax, 6, 17.5, "n = |A| <= 5 ?", "decision", w=3.4, h=1.3)
    base = Node(ax, 10.0, 17.5, "insertion-sort A\nreturn A[k]", "terminal", w=3.0, h=1.0, size=8.5)
    div = Node(ax, 6, 15.8, "DIVIDE: split A into ceil(n/5) groups of 5;\ninsertion-sort each group (<= 10 comparisons)",
               "process", w=7.4, h=1.0)
    med = Node(ax, 6, 14.4, "M <- list of the group medians  (|M| = ceil(n/5))", "process", w=7.0)
    piv = Node(ax, 6, 13.0, "CONQUER 1: p <- Select(M, floor((|M|-1)/2))\n(median of the medians = pivot)",
               "call", w=7.0, h=1.0)
    par = Node(ax, 6, 11.5, "COMBINE: (L, E, R) <- Partition3(A, p)\nL < p,  E = p,  R > p  (<= 2n comparisons)",
               "process", w=7.0, h=1.0)
    d1 = Node(ax, 6, 9.8, "k < |L| ?", "decision", w=2.8, h=1.3)
    left = Node(ax, 2.2, 8.2, "CONQUER 2:\nreturn Select(L, k)", "call", w=3.4, h=1.0, size=8.5)
    d2 = Node(ax, 6, 8.0, "k < |L| + |E| ?", "decision", w=3.6, h=1.3)
    hit = Node(ax, 10.0, 8.0, "return p\n(pivot has rank k)", "terminal", w=3.0, h=1.0, size=8.5)
    right = Node(ax, 6, 6.0, "CONQUER 2: return Select(R, k - |L| - |E|)", "call", w=6.4, h=0.9)
    note = ("Guarantee: >= half of the group medians are <= p and each such full group has >= 3 values <= p\n"
            "=> >= 3n/10 - 6 values are <= p (and >= p): |L|, |R| <= 7n/10 + 6\n"
            "T(n) <= T(ceil(n/5)) + T(7n/10 + 6) + cn  =>  T(n) = Theta(n) in the WORST case")
    ax.add_patch(Rectangle((0.5, 3.45), 11.0, 1.7, fill=False, ls="--", lw=1.0, ec="#555555"))
    ax.text(6, 4.3, note, ha="center", va="center", fontsize=8.8, style="italic")
    arrow(ax, [start.bottom(), d0.top()])
    arrow(ax, [d0.right(), base.left()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [d0.bottom(), div.top()], "No", 0)
    arrow(ax, [div.bottom(), med.top()])
    arrow(ax, [med.bottom(), piv.top()])
    arrow(ax, [piv.bottom(), par.top()])
    arrow(ax, [par.bottom(), d1.top()])
    arrow(ax, [d1.left(), (left.x, d1.y), left.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d1.bottom(), d2.top()], "No", 0)
    arrow(ax, [d2.right(), hit.left()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [d2.bottom(), right.top()], "No", 0)
    arrow(ax, [left.left(), (0.25, left.y), (0.25, start.y), start.left()], dashed=True)
    arrow(ax, [right.right(), (11.75, right.y), (11.75, start.y), start.right()], dashed=True)
    ax.text(0.35, 12.6, "recursive call", fontsize=8.5, color="#7f3f00", rotation=90)
    ax.text(11.45, 12.6, "recursive call", fontsize=8.5, color="#7f3f00", rotation=90)
    save(fig, os.path.join(OUT, "q6_flowchart_median_of_medians.png"))


def flowchart_quickselect():
    fig, ax = new_canvas(12, 2.6, 15.4, "QuickSelect(A, k) - pivot rule: RANDOM element or FIRST element")
    start = Node(ax, 6, 14.7, "Start: QuickSelect(A, k)", "terminal", w=4.2)
    d0 = Node(ax, 6, 13.3, "|A| = 1 ?", "decision", w=2.8, h=1.3)
    base = Node(ax, 10.0, 13.3, "return A[0]", "terminal", w=2.6, size=8.5)
    piv = Node(ax, 6, 11.6, "p <- A[random index]   (randomised)\nor  p <- A[0]   (deterministic first-element rule)",
               "process", w=7.6, h=1.0)
    par = Node(ax, 6, 10.1, "(L, E, R) <- Partition3(A, p)", "process", w=5.4)
    d1 = Node(ax, 6, 8.5, "k < |L| ?", "decision", w=2.8, h=1.3)
    keepL = Node(ax, 2.2, 7.0, "A <- L", "process", w=2.2)
    d2 = Node(ax, 6, 6.7, "k < |L| + |E| ?", "decision", w=3.6, h=1.3)
    hit = Node(ax, 10.0, 6.7, "return p", "terminal", w=2.4, size=8.5)
    keepR = Node(ax, 6, 5.0, "k <- k - |L| - |E|;   A <- R", "process", w=5.0)
    arrow(ax, [start.bottom(), d0.top()])
    arrow(ax, [d0.right(), base.left()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [d0.bottom(), piv.top()], "No", 0)
    arrow(ax, [piv.bottom(), par.top()])
    arrow(ax, [par.bottom(), d1.top()])
    arrow(ax, [d1.left(), (keepL.x, d1.y), keepL.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d1.bottom(), d2.top()], "No", 0)
    arrow(ax, [d2.right(), hit.left()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [d2.bottom(), keepR.top()], "No", 0)
    arrow(ax, [keepL.left(), (0.5, keepL.y), (0.5, d0.y), d0.left()])
    arrow(ax, [keepR.left(), (0.5, keepR.y), (0.5, keepL.y)])
    ax.text(0.65, 10.3, "next round\n(one side only)", fontsize=8.5, color="#7f3f00")
    ax.text(6, 3.4, "Pivot quality decides the cost: a pivot near the median halves A (expected Theta(n) for a random\n"
            "pivot); a pivot at an extreme keeps n - 1 elements -> on SORTED input the first-element rule makes\n"
            "~ 3n^2/4 comparisons (Theta(n^2)); a random pivot only makes that case unlikely, not impossible.",
            ha="center", va="center", fontsize=8.8, style="italic")
    save(fig, os.path.join(OUT, "q6_flowchart_quickselect.png"))


def flowchart_mitm():
    fig, ax = new_canvas(17, 2.7, 17.4, "Meet-in-the-Middle - BestFillMITM(w, W): heaviest load <= W")
    ax.text(5.0, 16.75, "Main algorithm", ha="center", fontsize=10, fontweight="bold")
    ax.text(13.3, 16.75, "SortedSubsetSums(H)", ha="center", fontsize=10, fontweight="bold")
    s = Node(ax, 5, 16.0, "Start", "terminal", w=2.2)
    inp = Node(ax, 5, 14.9, "Input: weights w[0..n-1], capacity W", "io", w=6.2)
    div = Node(ax, 5, 13.6, "DIVIDE: H1 <- w[0..n/2-1],  H2 <- w[n/2..n-1]", "process", w=7.0)
    con = Node(ax, 5, 12.3, "CONQUER: A <- SortedSubsetSums(H1);\nB <- SortedSubsetSums(H2)",
               "call", w=6.4, h=1.0)
    ini = Node(ax, 5, 11.0, "best <- 0;  i <- 0 (A ascending)", "process", w=5.2)
    d1 = Node(ax, 5, 9.5, "i < |A| and A[i] <= W ?", "decision", w=4.8, h=1.4)
    bs = Node(ax, 5, 7.7, "COMBINE: j <- largest index with B[j] <= W - A[i]\n(binary search, ~n/2 probes)",
              "process", w=7.0, h=1.0)
    upd = Node(ax, 5, 6.3, "best <- max(best, A[i] + B[j]);  i <- i + 1", "process", w=6.4)
    out = Node(ax, 9.0, 4.6, "Output: best", "io", w=2.8)
    end = Node(ax, 9.0, 3.4, "End", "terminal", w=2.0)
    arrow(ax, [s.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), div.top()])
    arrow(ax, [div.bottom(), con.top()])
    arrow(ax, [con.bottom(), ini.top()])
    arrow(ax, [ini.bottom(), d1.top()])
    arrow(ax, [d1.bottom(), bs.top()], "Yes", 0)
    arrow(ax, [bs.bottom(), upd.top()])
    arrow(ax, [upd.left(), (0.5, upd.y), (0.5, d1.y), d1.left()])
    arrow(ax, [d1.right(), (out.x, d1.y), out.top()], "No", 0, dx=0.1)
    arrow(ax, [out.bottom(), end.top()])
    t0 = Node(ax, 13.3, 16.0, "Start", "terminal", w=2.2)
    t1 = Node(ax, 13.3, 14.9, "L <- [0]", "process", w=2.6)
    t2 = Node(ax, 13.3, 13.4, "another weight\nw in H ?", "decision", w=3.6, h=1.6)
    t3 = Node(ax, 13.3, 11.6, "L' <- [s + w for s in L]\n(still ascending)", "process", w=4.2, h=1.0)
    t4 = Node(ax, 13.3, 10.1, "L <- Merge(L, L')\n(|L| doubles)", "process", w=4.2, h=1.0)
    t5 = Node(ax, 13.3, 7.7, "return L\n(2^|H| sums, ascending)", "terminal", w=4.0, h=1.0)
    arrow(ax, [t0.bottom(), t1.top()])
    arrow(ax, [t1.bottom(), t2.top()])
    arrow(ax, [t2.bottom(), t3.top()], "Yes", 0)
    arrow(ax, [t3.bottom(), t4.top()])
    arrow(ax, [t4.right(), (16.4, t4.y), (16.4, t2.y), t2.right()])
    arrow(ax, [t2.left(), (10.6, t2.y), (10.6, t5.y), t5.left()], "No", 0, dx=-0.6)
    ax.text(13.3, 5.6, "Time: generation Theta(2^(n/2)) per half,\ncombine Theta(n 2^(n/2)) (binary search)\n"
            "or Theta(2^(n/2)) (two-pointer scan)\nMemory: 2 x 2^(n/2) stored sums",
            ha="center", va="center", fontsize=8.8, style="italic")
    save(fig, os.path.join(OUT, "q6_flowchart_meet_in_the_middle.png"))


def main():
    flowchart_mom()
    flowchart_quickselect()
    flowchart_mitm()


if __name__ == "__main__":
    main()
