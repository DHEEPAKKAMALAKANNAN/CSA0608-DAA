"""q7_flowcharts.py - standard-symbol flowcharts of the Q7 designs (Maximum Subarray Sum).

Writes:
  ../Pseudocode/q7_flowchart_brute_force.png            baseline O(n^2)
  ../Pseudocode/q7_flowchart_joint_dc.png               joint final design: recursive solve with Theta(1) combine
  ../Student_A_Initial_Design/q7_flowchart_proposal_a.png   Student A's Stage-1 proposal (kept as evidence)
  ../Student_B_Initial_Design/q7_flowchart_proposal_b.png   Student B's Stage-1 proposal (kept as evidence)
Run:  py -3 q7_flowcharts.py
"""
import os

from matplotlib.patches import Rectangle

from flowchart_helpers import Node, arrow, new_canvas, save

HERE = os.path.dirname(os.path.abspath(__file__))
Q7 = os.path.dirname(HERE)


def flowchart_brute_force():
    fig, ax = new_canvas(11, 2.5, 15.4, "Baseline - brute force over every run of hours (Theta(n^2))")
    start = Node(ax, 5.5, 14.7, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.5, 13.6, "Input: hourly profits p[0..n-1]", "io", w=5.4)
    init = Node(ax, 5.5, 12.5, "best <- p[0];  (bi, bj) <- (0, 0);  i <- 0", "process", w=5.6)
    d1 = Node(ax, 5.5, 11.1, "i < n ?", "decision", w=2.6, h=1.2)
    run = Node(ax, 5.5, 9.8, "run <- 0;  j <- i", "process", w=3.2)
    d2 = Node(ax, 5.5, 8.5, "j < n ?", "decision", w=2.6, h=1.2)
    add = Node(ax, 5.5, 7.2, "run <- run + p[j]   (1 addition)", "process", w=4.6)
    d3 = Node(ax, 5.5, 5.8, "run > best ?\n(1 comparison)", "decision", w=3.4, h=1.5)
    upd = Node(ax, 9.0, 5.8, "best <- run\n(bi, bj) <- (i, j)", "process", w=2.6, h=1.0)
    incj = Node(ax, 5.5, 4.3, "j <- j + 1", "process", w=2.4)
    inci = Node(ax, 1.6, 8.5, "i <- i + 1", "process", w=2.0)
    out = Node(ax, 9.0, 11.1, "Output:\n(best, bi, bj)", "io", w=2.8, h=1.0)
    end = Node(ax, 9.0, 9.6, "End", "terminal", w=2.0)
    for a, b in ((start, inp), (inp, init), (init, d1), (run, d2), (add, d3)):
        arrow(ax, [a.bottom(), b.top()])
    arrow(ax, [d1.bottom(), run.top()], "Yes", 0)
    arrow(ax, [d1.right(), out.left()], "No", 0, dy=0.15)
    arrow(ax, [out.bottom(), end.top()])
    arrow(ax, [d2.bottom(), add.top()], "Yes", 0)
    arrow(ax, [d2.left(), inci.right()], "No", 0, dx=-0.6, dy=0.15)
    arrow(ax, [inci.top(), (inci.x, d1.y), d1.left()])
    arrow(ax, [d3.right(), upd.left()], "Yes", 0, dy=0.15)
    arrow(ax, [upd.bottom(), (upd.x, incj.y), incj.right()])
    arrow(ax, [d3.bottom(), incj.top()], "No", 0)
    arrow(ax, [incj.left(), (3.4, incj.y), (3.4, d2.y + 0.75), (d2.x, d2.y + 0.75)])
    ax.text(5.5, 3.1, "inner body runs n + (n-1) + ... + 1 = n(n+1)/2 times: n(n+1)/2 additions and comparisons",
            ha="center", fontsize=8.5, style="italic")
    save(fig, os.path.join(Q7, "Pseudocode", "q7_flowchart_brute_force.png"))


def flowchart_joint():
    fig, ax = new_canvas(16, -0.4, 16.2, "Joint final design - MaxRun(p, lo, hi) returning the summary "
                                          "(total, prefix, suffix, best) with hour indices")
    start = Node(ax, 3.3, 15.5, "Start", "terminal", w=2.2)
    inp = Node(ax, 3.3, 14.4, "Input: p[0..n-1]", "io", w=3.6)
    d0 = Node(ax, 3.3, 13.0, "n = 0 ?", "decision", w=2.4, h=1.2)
    err = Node(ax, 0.85, 13.0, "error:\nno hours", "terminal", w=1.4, h=0.9, size=8)
    call = Node(ax, 3.3, 11.6, "S <- MaxRun(p, 0, n-1)", "call", w=4.0)
    out = Node(ax, 3.3, 10.4, "Output: S.best,\nhours S.bi..S.bj", "io", w=3.6, h=1.0)
    end = Node(ax, 3.3, 9.2, "End", "terminal", w=2.0)
    for a, b in ((start, inp), (inp, d0), (call, out), (out, end)):
        arrow(ax, [a.bottom(), b.top()])
    arrow(ax, [d0.bottom(), call.top()], "No", 0)
    arrow(ax, [d0.left(), err.right()], "Yes", 0, dx=-0.55, dy=0.15)

    entry = Node(ax, 10.8, 15.5, "MaxRun(p, lo, hi)", "terminal", w=3.6)
    arrow(ax, [call.right(), (6.8, call.y), (6.8, 15.5), entry.left()], "call", 1, dx=0.1, dy=0.3, dashed=True)
    d1 = Node(ax, 10.8, 14.1, "lo = hi ?\n(one hour)", "decision", w=3.0, h=1.4)
    base = Node(ax, 14.4, 14.1, "return (p[lo], p[lo], p[lo], p[lo])\nall runs = hour lo",
                "terminal", w=3.0, h=1.1, size=7.5)
    mid = Node(ax, 10.8, 12.6, "DIVIDE: mid <- floor((lo + hi) / 2)", "process", w=5.0)
    left = Node(ax, 10.8, 11.4, "CONQUER: L <- MaxRun(p, lo, mid)", "call", w=5.4)
    right = Node(ax, 10.8, 10.2, "CONQUER: R <- MaxRun(p, mid+1, hi)", "call", w=5.4)
    c1 = Node(ax, 10.8, 8.9, "total <- L.total + R.total", "process", w=4.8)
    c2 = Node(ax, 10.8, 7.7, "prefix <- max(L.prefix, L.total + R.prefix)", "process", w=6.0)
    c3 = Node(ax, 10.8, 6.5, "suffix <- max(R.suffix, R.total + L.suffix)", "process", w=6.0)
    c4 = Node(ax, 10.8, 5.3, "cross <- L.suffix + R.prefix  (run over the split)", "process", w=6.6)
    d2 = Node(ax, 10.8, 3.9, "cross > max(L.best, R.best) ?", "decision", w=5.2, h=1.3)
    yes = Node(ax, 14.1, 2.5, "best <- cross\nhours L.suf_start..R.pre_end", "process", w=3.2, h=1.0, size=8)
    no = Node(ax, 7.0, 2.5, "best <- larger of\nL.best, R.best (+ hours)", "process", w=3.2, h=1.0, size=8)
    ret = Node(ax, 10.8, 1.0, "return (total, prefix, suffix, best) with indices", "terminal", w=6.2, size=8.5)
    for a, b in ((entry, d1), (mid, left), (left, right), (right, c1), (c1, c2), (c2, c3), (c3, c4), (c4, d2)):
        arrow(ax, [a.bottom(), b.top()])
    arrow(ax, [d1.right(), base.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d1.bottom(), mid.top()], "No", 0)
    arrow(ax, [d2.right(), (yes.x, d2.y), yes.top()], "Yes", 0)
    arrow(ax, [d2.left(), (no.x, d2.y), no.top()], "No", 0, dx=-0.6)
    arrow(ax, [yes.bottom(), (yes.x, ret.y), ret.right()])
    arrow(ax, [no.bottom(), (no.x, ret.y), ret.left()])
    ax.add_patch(Rectangle((7.35, 4.55), 6.9, 4.95, fill=False, ls="--", lw=1.0, ec="#555555"))
    ax.text(14.35, 9.1, "COMBINE\nTheta(1):\n4 additions\n4 comparisons", fontsize=8, style="italic", va="top")
    ax.text(3.3, 7.6, "Recurrence of the design:\nT(1) = Theta(1)\nT(n) = 2T(n/2) + Theta(1)\n=> T(n) = Theta(n)",
            ha="center", fontsize=9, style="italic",
            bbox=dict(boxstyle="round", facecolor="#f8f9f9", edgecolor="#999999"))
    save(fig, os.path.join(Q7, "Pseudocode", "q7_flowchart_joint_dc.png"))


def flowchart_proposal(title, combine_text, base_text, info_text, note, path, color_note):
    fig, ax = new_canvas(11, 0.2, 12.6, title)
    entry = Node(ax, 5.5, 11.9, "Solve(p, lo, hi)", "terminal", w=3.4)
    d1 = Node(ax, 5.5, 10.5, "lo = hi ?", "decision", w=2.6, h=1.2)
    base = Node(ax, 9.2, 10.5, base_text, "terminal", w=3.2, h=1.1, size=8)
    mid = Node(ax, 5.5, 9.0, "mid <- floor((lo + hi) / 2)", "process", w=4.0)
    left = Node(ax, 5.5, 7.8, "L <- Solve(p, lo, mid)", "call", w=4.0)
    right = Node(ax, 5.5, 6.6, "R <- Solve(p, mid+1, hi)", "call", w=4.0)
    info = Node(ax, 5.5, 5.3, info_text, "process", w=7.4, h=0.9, size=8)
    comb = Node(ax, 5.5, 3.9, combine_text, "process", w=8.6, h=1.1, size=8)
    ret = Node(ax, 5.5, 2.6, "return result", "terminal", w=3.0)
    for a, b in ((entry, d1), (mid, left), (left, right), (right, info), (info, comb), (comb, ret)):
        arrow(ax, [a.bottom(), b.top()])
    arrow(ax, [d1.right(), base.left()], "Yes", 0, dy=0.15)
    arrow(ax, [d1.bottom(), mid.top()], "No", 0)
    ax.text(5.5, 1.2, note, ha="center", fontsize=8.5, style="italic", color=color_note)
    save(fig, path)


def main():
    flowchart_brute_force()
    flowchart_joint()
    flowchart_proposal("Stage 1 - Student A's independent proposal (split at the middle)",
                       "combine: result <- the better of L and R\n(NO run crossing the split is considered)",
                       "return (p[lo], lo, lo)\none hour", "each half returns its best run: (sum, start, end)",
                       "Defect found in Stage 2: the best run may cross the split (demo: 410 returned, 690 correct)",
                       os.path.join(Q7, "Student_A_Initial_Design", "q7_flowchart_proposal_a.png"), "#a93226")
    flowchart_proposal("Stage 1 - Student B's independent proposal (4-number summary)",
                       "total = TL + TR;  prefix = max(PL, TL + PR);  suffix = max(SR, TR + SL)\n"
                       "best = max(bestL, bestR, SL + PR)   (crossing run in O(1))",
                       "x = p[lo]; return (x, max(x,0),\nmax(x,0), max(x,0))",
                       "each half returns 4 sums: (total, prefix, suffix, best) - no hour indices",
                       "Defects found in Stage 2: empty runs allowed (all-loss day gives 0), hours not reported",
                       os.path.join(Q7, "Student_B_Initial_Design", "q7_flowchart_proposal_b.png"), "#a93226")


if __name__ == "__main__":
    main()
