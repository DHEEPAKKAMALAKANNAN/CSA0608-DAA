"""
draw_diagrams_t1.py - flowchart and diagrams for Task 1 (word-wrap DP), written to Report/Screenshots/.

  t1_flowchart_word_wrap.png   flowchart of the suffix DP + reconstruction (standard flowchart symbols)
  t1_line_layout.png           the W = 21 layout: DP optimum vs greedy first-fit, unused cells hatched, s and s^2
  t1_dp_dependency.png         DP states best[i] as nodes; arcs = the chosen next_break[i]; the optimal chain
  t1_width_sweep.png           total penalty vs W (DP vs greedy) from results/t1_width_sweep.csv
All numbers are computed by word_wrap_dp.py at drawing time (nothing typed in by hand).
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

import word_wrap_dp as ww  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "Report", "Screenshots"))
FILL = {"terminal": "#d9ead3", "process": "#dbe8f6", "decision": "#fff2cc", "io": "#e8dff5",
        "call": "#fde3cf"}


# ----------------------------------------------------------------------------- flowchart helpers
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
    """Polyline through points with an arrow head at the end; optional label near a vertex."""
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


# ----------------------------------------------------------------------------- figures
def load_words():
    with open(os.path.join(HERE, "test_data", "layout_text.txt"), encoding="utf-8") as f:
        return ww.tokenize(f.read())


def flowchart():
    fig, ax = new_canvas(15, 0.3, 19.6, "Word Wrap DP - minimum total penalty (suffix formulation)")
    start = Node(ax, 5.5, 19.0, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.5, 17.9, "Input: words w0..w(n-1), width W", "io", w=5.4)
    val = Node(ax, 5.5, 16.6, "validate: W >= 1 and every\nlen(w_k) <= W ?", "decision", w=4.8, h=1.5)
    err = Node(ax, 11.6, 16.6, "Output: reject input\n(LayoutError / ValueError)", "io", w=4.2, h=1.0)
    init = Node(ax, 5.5, 15.0, "best[n] <- 0;  i <- n - 1", "process", w=4.4)
    d_i = Node(ax, 5.5, 13.6, "i >= 0 ?", "decision", w=2.6, h=1.2)
    init_j = Node(ax, 5.5, 12.2, "best[i] <- inf;  j <- i + 1", "process", w=4.4)
    d_fit = Node(ax, 5.5, 10.6, "j <= n and words i..j-1\nfit (s = slack(i, j) >= 0) ?", "decision", w=5.4, h=1.7)
    cost = Node(ax, 5.5, 8.7, "cost <- (0 if j = n else s^2) + best[j]", "process", w=5.6)
    d_better = Node(ax, 5.5, 7.2, "cost < best[i] ?", "decision", w=3.4, h=1.2)
    keep = Node(ax, 5.5, 5.8, "best[i] <- cost;  next[i] <- j", "process", w=4.8)
    inc_j = Node(ax, 5.5, 4.6, "j <- j + 1", "process", w=2.4)
    dec_i = Node(ax, 11.6, 10.6, "i <- i - 1", "process", w=2.4)
    rec = Node(ax, 11.6, 13.6, "Reconstruct: i <- 0; repeat\nline = words i..next[i]-1;\ni <- next[i] until i = n",
               "call", w=4.6, h=1.5, size=8.5)
    out = Node(ax, 11.6, 6.2, "Output: best[0], lines,\nunused s and penalty per line", "io", w=4.6, h=1.0)
    end = Node(ax, 11.6, 4.6, "End", "terminal", w=2.2)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), val.top()])
    arrow(ax, [val.right(), err.left()], "No", 0, dx=0.1)
    arrow(ax, [val.bottom(), init.top()], "Yes", 0)
    arrow(ax, [init.bottom(), d_i.top()])
    arrow(ax, [d_i.bottom(), init_j.top()], "Yes", 0)
    arrow(ax, [init_j.bottom(), d_fit.top()])
    arrow(ax, [d_fit.bottom(), cost.top()], "Yes", 0)
    arrow(ax, [cost.bottom(), d_better.top()])
    arrow(ax, [d_better.bottom(), keep.top()], "Yes", 0)
    arrow(ax, [keep.bottom(), inc_j.top()])
    arrow(ax, [d_better.left(), (1.6, d_better.y), (1.6, inc_j.y), inc_j.left()], "No", 0, dx=-0.7)
    arrow(ax, [inc_j.bottom(), (5.5, 3.7), (0.6, 3.7), (0.6, d_fit.y), d_fit.left()])
    arrow(ax, [d_fit.right(), dec_i.left()], "No", 0, dx=0.1)
    arrow(ax, [dec_i.top(), (dec_i.x, 12.2), (8.6, 12.2), (8.6, 14.4), (d_i.x, 14.4)])
    arrow(ax, [d_i.right(), rec.left()], "No", 0, dx=0.15, dy=-0.4)
    arrow(ax, [rec.right(), (14.3, rec.y), (14.3, out.y), out.right()])
    arrow(ax, [out.bottom(), end.top()])
    ax.text(7.5, 1.6, "Inner loop stops at the first word that does not fit (longer lines fit even less):\n"
            "Theta(n * L) candidate checks, L = most words per line;  memory: best[0..n] and next[0..n]",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "t1_flowchart_word_wrap.png")


def draw_layout(ax, lines, width, title):
    """One row per line, one cell per character; unused cells hatched."""
    for r, line in enumerate(lines):
        y = -r
        text = " ".join(line.words)
        for c in range(width):
            used = c < len(text)
            ax.add_patch(Rectangle((c, y), 1, 0.8, facecolor="#dbe8f6" if used else "white",
                                   edgecolor="#b0b0b0", lw=0.5, hatch=None if used else "///"))
            if used and text[c] != " ":
                ax.text(c + 0.5, y + 0.4, text[c], ha="center", va="center", fontsize=7, family="monospace")
        final = r == len(lines) - 1
        ax.text(width + 0.6, y + 0.4, f"s = {line.unused:>2}   " + ("final: 0" if final else f"s² = {line.penalty}"),
                va="center", fontsize=8.5, color="#7f3f00" if line.penalty else "#2e7d32")
    ax.plot([width, width], [-len(lines) + 0.8, 0.9], color="red", lw=1.5)
    ax.text(width, 1.05, f"W = {width}", color="red", ha="center", fontsize=8.5)
    ax.set_xlim(-0.5, width + 9)
    ax.set_ylim(-len(lines) - 0.6, 1.5)
    ax.axis("off")
    ax.set_title(f"{title}: total penalty {sum(line.penalty for line in lines)}", fontsize=10.5, fontweight="bold")


def line_layout(words, width=21):
    _, dp_lines, _ = ww.word_wrap_dp(words, width)
    _, g_lines = ww.greedy_first_fit(words, width)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.4))
    draw_layout(axes[0], dp_lines, width, "DP optimum")
    draw_layout(axes[1], g_lines, width, "Greedy first-fit")
    fig.suptitle("Line layout of the test text at W = 21 (blue = characters, hatched = unused spaces s)",
                 fontsize=11.5, fontweight="bold")
    save(fig, "t1_line_layout.png")


def dp_dependency(words, width=21):
    _, lines, states = ww.word_wrap_dp(words, width, record_states=True)
    n = len(words)
    by_i = {st.i: st for st in states}
    chain = {line.first for line in lines}
    fig, ax = plt.subplots(figsize=(15, 4.6))
    for i in range(n + 1):
        on = i in chain or i == n
        ax.add_patch(Rectangle((i - 0.38, -0.38), 0.76, 0.76, facecolor="#fde3cf" if on else "#eef3f8",
                               edgecolor="#c55a11" if on else "#888888", lw=1.6 if on else 0.8))
        best = 0 if i == n else by_i[i].best
        ax.text(i, 0.08, f"{best}", ha="center", va="center", fontsize=8.5, fontweight="bold")
        ax.text(i, -0.2, f"i={i}", ha="center", va="center", fontsize=6.5)
        if i < n:
            ax.text(i, -0.62, words[i], ha="center", va="top", fontsize=6.5, rotation=60)
    for i in range(n):
        st = by_i[i]
        for c in st.candidates:                     # every feasible candidate in light grey
            ax.annotate("", xy=(c.j, 0.38), xytext=(i, 0.38),
                        arrowprops=dict(arrowstyle="-", color="#d0d0d0", lw=0.6,
                                        connectionstyle=f"arc3,rad=-{0.25 + 0.04 * (c.j - i)}"))
    for line in lines:                              # the optimal chain of decisions
        ax.annotate("", xy=(line.last + 1, 0.38), xytext=(line.first, 0.38),
                    arrowprops=dict(arrowstyle="-|>", color="#c55a11", lw=2.0,
                                    connectionstyle=f"arc3,rad=-{0.25 + 0.04 * (line.last + 1 - line.first)}"))
        mid = (line.first + line.last + 1) / 2
        ax.text(mid, 0.55 + 0.22 * (line.last + 1 - line.first), f"s²={line.penalty}", ha="center", fontsize=8,
                color="#c55a11")
    ax.set_xlim(-0.8, n + 0.8)
    ax.set_ylim(-1.9, 2.6)
    ax.axis("off")
    ax.set_title("DP states best[i] (number in each box) for W = 21: grey arcs = every feasible first line i -> j,\n"
                 "orange arcs = the decisions next[i] on the optimal chain 0 -> 3 -> 7 -> 9 -> 11 -> 14 -> 19 -> 20",
                 fontsize=10.5, fontweight="bold")
    save(fig, "t1_dp_dependency.png")


def width_sweep():
    path = os.path.join(HERE, "results", "t1_width_sweep.csv")
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    w = [int(r["width"]) for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].plot(w, [int(r["dp_penalty"]) for r in rows], "o-", label="DP optimum", color="#1f77b4")
    axes[0].plot(w, [int(r["greedy_penalty"]) for r in rows], "s--", label="greedy first-fit", color="#d62728",
                 ms=4)
    for x in (18, 21, 26, 30):
        axes[0].axvline(x, color="#999999", lw=0.7, ls=":")
    axes[0].set_xlabel("line width W (characters)")
    axes[0].set_ylabel("total penalty Σ s² (non-final lines)")
    axes[0].set_title("Total penalty vs line width (dotted: widths used in 1.3)")
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    axes[1].bar(w, [int(r["candidates"]) for r in rows], color="#2ca02c", label="feasible candidates examined")
    axes[1].plot(w, [int(r["lines"]) * 10 for r in rows], "k.-", label="number of lines × 10")
    axes[1].set_xlabel("line width W (characters)")
    axes[1].set_ylabel("count")
    axes[1].set_title("DP work grows with W (more words fit per line)")
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    save(fig, "t1_width_sweep.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    words = load_words()
    flowchart()
    line_layout(words)
    dp_dependency(words)
    width_sweep()


if __name__ == "__main__":
    main()
