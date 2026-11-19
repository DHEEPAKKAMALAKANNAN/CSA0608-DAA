"""q3_flowcharts.py - flowcharts of the two multiplication methods of Q3 (schoolbook and Karatsuba).

Draws standard-symbol flowcharts (see flowchart_helpers.py) and writes them to ../Pseudocode/:
  q3_flowchart_schoolbook.png   grade-school multiplication of two digit arrays (n*m digit products)
  q3_flowchart_karatsuba.png    recursive Karatsuba (subtractive variant) with the schoolbook base case
Run:  py -3 q3_flowcharts.py
"""
import os

from flowchart_helpers import Node, arrow, new_canvas, save

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Pseudocode")


def flowchart_schoolbook():
    fig, ax = new_canvas(11, 2.7, 15.2, "Schoolbook multiplication of digit arrays a (n digits) and b (m digits)")
    start = Node(ax, 5.5, 14.5, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.5, 13.35, "Input: a[0..n-1], b[0..m-1] (little-endian digits)", "io", w=6.6)
    init = Node(ax, 5.5, 12.15, "r[0..n+m-1] <- 0;   i <- 0", "process", w=4.6)
    d1 = Node(ax, 5.5, 10.75, "i < n ?", "decision", w=2.6, h=1.2)
    c0 = Node(ax, 5.5, 9.35, "carry <- 0;   j <- 0", "process", w=3.8)
    d2 = Node(ax, 5.5, 7.95, "j < m ?", "decision", w=2.6, h=1.2)
    body = Node(ax, 5.5, 6.3, "t <- a[i]*b[j] + r[i+j] + carry\n(1 digit multiplication, 2 additions)\n"
                "r[i+j] <- t mod 10;  carry <- t div 10;  j <- j + 1", "process", w=5.0, h=1.5, size=8)
    tail = Node(ax, 9.3, 7.95, "r[i+m] <- carry\ni <- i + 1", "process", w=2.4, h=1.0, size=8.5)
    out = Node(ax, 1.85, 5.0, "Output: r\n(n + m digits)", "io", w=2.8, h=1.0)
    end = Node(ax, 1.85, 3.7, "End", "terminal", w=2.0)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), d1.top()])
    arrow(ax, [d1.bottom(), c0.top()], "Yes", 0)
    arrow(ax, [c0.bottom(), d2.top()])
    arrow(ax, [d2.bottom(), body.top()], "Yes", 0)
    arrow(ax, [body.left(), (2.6, body.y), (2.6, d2.y), d2.left()])
    arrow(ax, [d2.right(), tail.left()], "No", 0, dx=0.05, dy=0.15)
    arrow(ax, [tail.top(), (tail.x, d1.y), d1.right()])
    arrow(ax, [d1.left(), (out.x, d1.y), out.top()], "No", 0, dx=-0.6)
    arrow(ax, [out.bottom(), end.top()])
    ax.text(6.6, 4.6, "Basic operation: the digit multiplication inside the inner loop", ha="center",
            fontsize=8.5, style="italic")
    ax.text(6.6, 3.7, "executed exactly n·m times for every input\n->  Θ(n²) for two n-digit numbers",
            ha="center", fontsize=8.5, style="italic")
    save(fig, os.path.join(OUT, "q3_flowchart_schoolbook.png"))


def flowchart_karatsuba():
    fig, ax = new_canvas(13, 1.6, 19.0, "Karatsuba(a, b, t) - subtractive variant, schoolbook below the threshold t")
    start = Node(ax, 6.5, 18.3, "Karatsuba(a, b, t)", "terminal", w=3.6)
    inp = Node(ax, 6.5, 17.15, "Input: digit arrays a, b of equal length n; threshold t", "io", w=7.0)
    d1 = Node(ax, 6.5, 15.75, "n <= t ?", "decision", w=2.8, h=1.3)
    base = Node(ax, 11.0, 15.75, "return Schoolbook(a, b)\n(base case)", "call", w=3.4, h=1.0, size=8.5)
    div = Node(ax, 6.5, 14.1, "DIVIDE:  m <- ceil(n/2)\na = a1·10^m + a0,   b = b1·10^m + b0\n"
               "(high halves zero-padded to m digits)", "process", w=6.6, h=1.4, size=8.5)
    z0 = Node(ax, 3.2, 12.2, "z0 <- Karatsuba(a0, b0, t)", "call", w=4.4, size=8.5)
    z2 = Node(ax, 9.8, 12.2, "z2 <- Karatsuba(a1, b1, t)", "call", w=4.4, size=8.5)
    dif = Node(ax, 6.5, 10.65, "da <- |a0 - a1|,  db <- |b1 - b0|\ns <- sign(a0 - a1) · sign(b1 - b0)",
               "process", w=5.6, h=1.1, size=8.5)
    z1 = Node(ax, 6.5, 9.15, "z1' <- Karatsuba(da, db, t)   (third and last product)", "call", w=6.6, size=8.5)
    comb = Node(ax, 6.5, 7.6, "COMBINE:  z1 <- z0 + z2 + s·z1'   ( = a0·b1 + a1·b0 )", "process", w=7.0,
                size=8.5)
    place = Node(ax, 6.5, 6.15, "r <- z2·10^(2m) + z1·10^m + z0\n(z0, z2 placed side by side; one shifted "
                 "addition)", "process", w=7.0, h=1.1, size=8.5)
    out = Node(ax, 6.5, 4.75, "return r[0..2n-1]", "terminal", w=3.6)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), d1.top()])
    arrow(ax, [d1.right(), base.left()], "Yes", 0, dx=0.05, dy=0.15)
    arrow(ax, [d1.bottom(), div.top()], "No", 0)
    arrow(ax, [(div.x - 1.5, div.y - div.h / 2), (z0.x, 13.1), z0.top()])
    arrow(ax, [(div.x + 1.5, div.y - div.h / 2), (z2.x, 13.1), z2.top()])
    arrow(ax, [z0.bottom(), (z0.x, 11.5), (dif.x - 1.5, 11.5), (dif.x - 1.5, dif.y + dif.h / 2)])
    arrow(ax, [z2.bottom(), (z2.x, 11.5), (dif.x + 1.5, 11.5), (dif.x + 1.5, dif.y + dif.h / 2)])
    arrow(ax, [dif.bottom(), z1.top()])
    arrow(ax, [z1.bottom(), comb.top()])
    arrow(ax, [comb.bottom(), place.top()])
    arrow(ax, [place.bottom(), out.top()])
    ax.text(6.5, 3.5, "3 recursive calls on m = ceil(n/2) digits instead of 4  ->  T(n) = 3T(n/2) + Θ(n)",
            ha="center", fontsize=9, style="italic")
    ax.text(6.5, 2.85, "with t = 1: exactly 3^ceil(log2 n) single-digit multiplications;  Θ(n^log2 3) ≈ Θ(n^1.585)",
            ha="center", fontsize=9, style="italic")
    ax.text(6.5, 2.2, "|a0 - a1| < 10^m, so every sub-problem has exactly m digits (no carry digit as in "
            "(a0 + a1)(b0 + b1))", ha="center", fontsize=8.5, style="italic")
    save(fig, os.path.join(OUT, "q3_flowchart_karatsuba.png"))


def main():
    flowchart_schoolbook()
    flowchart_karatsuba()


if __name__ == "__main__":
    main()
