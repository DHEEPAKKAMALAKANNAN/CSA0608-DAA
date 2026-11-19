"""q4_flowcharts.py - flowcharts of the two Q4 algorithms (standard flowchart symbols, matplotlib).

Writes into ../Pseudocode/:
  q4_flowchart_conventional.png  - triple-loop conventional multiplication
  q4_flowchart_strassen.png      - hybrid Strassen with cutoff and dynamic padding (recursive)
Run:  py -3 q4_flowcharts.py
"""
import os

from flowchart_helpers import Node, arrow, new_canvas, save

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Pseudocode")


def flowchart_conventional():
    fig, ax = new_canvas(11, 3.6, 16.4, "Conventional (triple-loop) matrix multiplication C = A x B")
    start = Node(ax, 5.5, 15.7, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.5, 14.6, "Input: A, B (n x n)", "io", w=4.2)
    i0 = Node(ax, 5.5, 13.5, "i <- 0", "process", w=2.2)
    di = Node(ax, 5.5, 12.2, "i < n ?", "decision", w=2.6, h=1.2)
    j0 = Node(ax, 5.5, 10.9, "j <- 0", "process", w=2.2)
    dj = Node(ax, 5.5, 9.6, "j < n ?", "decision", w=2.6, h=1.2)
    s0 = Node(ax, 5.5, 8.3, "s <- A[i][0] * B[0][j];  k <- 1", "process", w=4.8)
    dk = Node(ax, 5.5, 7.0, "k < n ?", "decision", w=2.6, h=1.2)
    acc = Node(ax, 5.5, 5.6, "s <- s + A[i][k] * B[k][j]\n(1 mult + 1 add);  k <- k + 1", "process", w=4.8, h=1.0)
    store = Node(ax, 9.2, 7.0, "C[i][j] <- s\nj <- j + 1", "process", w=2.4, h=1.0)
    inci = Node(ax, 1.7, 9.6, "i <- i + 1", "process", w=2.0)
    out = Node(ax, 9.2, 12.2, "Output: C", "io", w=2.4)
    end = Node(ax, 9.2, 11.1, "End", "terminal", w=2.0)
    for a, b in ((start, inp), (inp, i0), (i0, di), (j0, dj), (s0, dk)):
        arrow(ax, [a.bottom(), b.top()])
    arrow(ax, [di.bottom(), j0.top()], "Yes", 0)
    arrow(ax, [dj.bottom(), s0.top()], "Yes", 0)
    arrow(ax, [dk.bottom(), acc.top()], "Yes", 0)
    arrow(ax, [acc.left(), (2.6, acc.y), (2.6, dk.y), dk.left()])
    arrow(ax, [dk.right(), store.left()], "No", 0, dx=0.05)
    arrow(ax, [store.right(), (10.7, store.y), (10.7, 10.25), (5.5, 10.25)])
    arrow(ax, [dj.left(), inci.right()], "No", 0, dx=-0.6)
    arrow(ax, [inci.top(), (inci.x, di.y), di.left()])
    arrow(ax, [di.right(), out.left()], "No", 0, dx=0.05)
    arrow(ax, [out.bottom(), end.top()])
    ax.text(5.5, 4.3, "n² entries x (n multiplications + n - 1 additions) = n³ mults and n²(n - 1) adds, for every input",
            ha="center", fontsize=8.5, style="italic")
    save(fig, os.path.join(OUT, "q4_flowchart_conventional.png"))


def flowchart_strassen():
    fig, ax = new_canvas(12, -0.4, 17.6, "Strassen(A, B, n, c) - hybrid Strassen with cutoff c and dynamic padding")
    start = Node(ax, 6, 16.9, "Strassen(A, B, n, c)", "terminal", w=4.2)
    base = Node(ax, 6, 15.5, "n <= c ?", "decision", w=2.8, h=1.2)
    conv = Node(ax, 10.0, 15.5, "return\nConventional(A, B)", "call", w=3.0, h=1.0, size=8.5)
    half = Node(ax, 6, 14.1, "h <- ceil(n / 2)", "process", w=3.0)
    odd = Node(ax, 6, 12.8, "n odd ?", "decision", w=2.6, h=1.2)
    padn = Node(ax, 10.0, 12.8, "pad A, B with one\nzero row + column", "process", w=3.2, h=1.0, size=8.5)
    split = Node(ax, 6, 11.3, "split A -> A11, A12, A21, A22;  B -> B11 ... B22\n(h x h blocks, data movement only)",
                 "process", w=7.0, h=1.0)
    prep = Node(ax, 6, 9.9, "10 block additions/subtractions form the operands\n(A11 + A22, B11 + B22, B12 - B22, ...)",
                "process", w=7.0, h=1.0)
    rec = Node(ax, 6, 8.3, "M1 ... M7 <- Strassen(operands, h, c)\n7 recursive products (instead of 8)", "call",
               w=7.0, h=1.1)
    comb = Node(ax, 6, 6.7, "C11 = M1 + M4 - M5 + M7    C12 = M3 + M5\nC21 = M2 + M4    C22 = M1 - M2 + M3 + M6"
                "\n(8 block additions)", "process", w=7.0, h=1.3, size=8.5)
    join = Node(ax, 6, 5.0, "C <- join(C11, C12, C21, C22)", "process", w=5.0)
    wasodd = Node(ax, 6, 3.7, "padded ?", "decision", w=2.6, h=1.2)
    unpad = Node(ax, 10.0, 3.7, "C <- top-left\nn x n part", "process", w=2.6, h=1.0, size=8.5)
    ret = Node(ax, 6, 2.2, "return C", "terminal", w=2.6)
    arrow(ax, [start.bottom(), base.top()])
    arrow(ax, [base.right(), conv.left()], "Yes", 0, dx=0.05)
    arrow(ax, [base.bottom(), half.top()], "No", 0)
    arrow(ax, [half.bottom(), odd.top()])
    arrow(ax, [odd.right(), padn.left()], "Yes", 0, dx=0.05)
    arrow(ax, [odd.bottom(), split.top()], "No", 0)
    arrow(ax, [padn.bottom(), (padn.x, 12.0), (7.2, 12.0), (7.2, split.y + 0.5)])
    arrow(ax, [split.bottom(), prep.top()])
    arrow(ax, [prep.bottom(), rec.top()])
    arrow(ax, [rec.bottom(), comb.top()])
    arrow(ax, [comb.bottom(), join.top()])
    arrow(ax, [join.bottom(), wasodd.top()])
    arrow(ax, [wasodd.right(), unpad.left()], "Yes", 0, dx=0.05)
    arrow(ax, [wasodd.bottom(), ret.top()], "No", 0)
    arrow(ax, [unpad.bottom(), (unpad.x, ret.y), ret.right()])
    arrow(ax, [rec.left(), (1.2, rec.y), (1.2, start.y), start.left()], dashed=True)
    ax.text(0.85, 12.5, "7 recursive calls on h x h blocks", rotation=90, ha="center", va="center", fontsize=9,
            fontweight="bold", color="#7f3f00")
    ax.text(6, 0.4, "M(n) = 7 M(n/2) multiplications;  A(n) = 7 A(n/2) + 18 (n/2)² additions;  "
            "T(n) = 7 T(n/2) + Theta(n²) = Theta(n^log2 7)", ha="center", fontsize=8.5, style="italic")
    save(fig, os.path.join(OUT, "q4_flowchart_strassen.png"))


def main():
    flowchart_conventional()
    flowchart_strassen()


if __name__ == "__main__":
    main()
