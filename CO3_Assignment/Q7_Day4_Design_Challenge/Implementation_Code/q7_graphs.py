"""Q7 graphs and diagrams - Maximum Subarray Sum (reads results/*.csv written by q7_experiments.py).

Writes to results/:
  q7_growth.png          counted operations and median time against n (log-log) with theoretical curves
  q7_small_n.png         time per call for small n: where the D&C design overtakes the O(n^2) baseline
  q7_three_cases.png     the decomposition: best run in the left half, in the right half, or crossing the split
  q7_recursion_tree.png  recursion tree of the 8-hour demo with the 4-tuple returned by every node
Run:  py -3 q7_graphs.py
"""
import csv
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

from q7_max_subarray import Counter, dc_joint  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
DEMO = [-120, 340, -60, 410, -380, 150, 220, -90]


def load(name):
    with open(os.path.join(RESULTS, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(fig, name):
    path = os.path.join(RESULTS, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(path)


def growth_figure():
    rows = sorted(load("q7_growth.csv"), key=lambda r: int(r["n"]))
    n = [int(r["n"]) for r in rows]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.8))
    nb = [int(r["n"]) for r in rows if r["brute_ops"]]
    a1.loglog(nb, [int(r["brute_ops"]) for r in rows if r["brute_ops"]], "o-", color="#c0392b",
              label="brute force (counted)")
    a1.loglog(n, [int(r["brute_formula"]) for r in rows], ":", color="#c0392b", label="n(n+1) (formula)")
    a1.loglog(n, [int(r["crossing_ops"]) for r in rows], "s-", color="#2e86c1", label="D&C crossing scan (counted)")
    a1.loglog(n, [2 * x * math.log2(x) for x in n], ":", color="#2e86c1", label="2 n log2 n")
    a1.loglog(n, [int(r["joint_ops"]) for r in rows], "^-", color="#1e8449", label="joint D&C 4-tuple (counted)")
    a1.set_title("Counted additions + comparisons")
    a1.set_xlabel("hours n")
    a1.set_ylabel("basic operations")
    a1.grid(True, which="both", alpha=0.3)
    a1.legend(fontsize=8)
    a2.loglog(nb, [float(r["brute_ms"]) for r in rows if r["brute_ms"]], "o-", color="#c0392b", label="brute force")
    a2.loglog(n, [float(r["crossing_ms"]) for r in rows], "s-", color="#2e86c1", label="D&C crossing scan")
    a2.loglog(n, [float(r["joint_ms"]) for r in rows], "^-", color="#1e8449", label="joint D&C 4-tuple")
    big = rows[-1]
    scale = float(big["joint_ms"]) / int(big["n"])
    a2.loglog(n, [scale * x for x in n], "--", color="#7f8c8d", label="c·n (scaled to largest n)")
    a2.set_title("Median wall-clock time (noisy, supporting evidence)")
    a2.set_xlabel("hours n")
    a2.set_ylabel("time (ms)")
    a2.grid(True, which="both", alpha=0.3)
    a2.legend(fontsize=8)
    save(fig, "q7_growth.png")


def small_n_figure():
    rows = load("q7_small_n.csv")
    n = [int(r["n"]) for r in rows]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5))
    a1.plot(n, [float(r["brute_us"]) for r in rows], "o-", color="#c0392b", label="brute force O(n²)")
    a1.plot(n, [float(r["crossing_us"]) for r in rows], "s-", color="#2e86c1", label="D&C crossing scan")
    a1.plot(n, [float(r["joint_us"]) for r in rows], "^-", color="#1e8449", label="joint D&C 4-tuple")
    a1.set_xscale("log", base=2)
    a1.set_yscale("log")
    a1.set_title("Median time per call for small n")
    a1.set_xlabel("hours n")
    a1.set_ylabel("time per call (µs)")
    a1.grid(True, which="both", alpha=0.3)
    a1.legend(fontsize=8)
    a2.plot(n, [float(r["joint_over_brute"]) for r in rows], "^-", color="#1e8449", label="time ratio joint / brute")
    a2.plot(n, [int(r["joint_ops"]) / int(r["brute_ops"]) for r in rows], "o--", color="#8e44ad",
            label="operation ratio joint / brute")
    a2.axhline(1, color="black", lw=1)
    a2.set_xscale("log", base=2)
    a2.set_yscale("log")
    a2.set_title("Ratio < 1: the D&C design is cheaper")
    a2.set_xlabel("hours n")
    a2.set_ylabel("ratio (log scale)")
    a2.grid(True, which="both", alpha=0.3)
    a2.legend(fontsize=8)
    save(fig, "q7_small_n.png")


def three_cases_figure():
    fig, ax = plt.subplots(figsize=(11, 4.6))
    hours = range(len(DEMO))
    ax.bar(hours, DEMO, color=["#1e8449" if v > 0 else "#c0392b" for v in DEMO], alpha=0.8)
    for h, v in zip(hours, DEMO):
        ax.text(h, v + (25 if v > 0 else -55), f"{v}", ha="center", fontsize=9)
    ax.axvline(3.5, color="black", lw=2, ls="--")
    ax.text(2.6, -440, "split: mid = 3", fontsize=9)
    ax.axhline(0, color="black", lw=0.8)
    spans = [(1, 3, 660, "#1e8449", "best run in LEFT half [0..3]: hours 1..3 = 690 (crosses ITS split 1|2)"),
             (5, 6, 330, "#2e86c1", "best run in RIGHT half [4..7]: hours 5..6 = 370"),
             (1, 6, 530, "#8e44ad", "CROSSING run = best suffix of left (1..3 = 690) + best prefix of right "
                                     "(4..6 = -10) = 680")]
    for i, j, y, col, txt in spans:
        ax.annotate("", xy=(j + 0.4, y), xytext=(i - 0.4, y),
                    arrowprops=dict(arrowstyle="<->", color=col, lw=2))
        ax.text(i - 0.4, y + 22, txt, fontsize=8.5, color=col)
    ax.set_ylim(-470, 740)
    ax.set_xticks(list(hours))
    ax.set_xlabel("operating hour")
    ax.set_ylabel("net profit (Rs)")
    ax.set_title("Decomposition: the best run lies in the left half, in the right half, or crosses the split "
                 "(answer = max of the three = 690)", fontsize=10)
    save(fig, "q7_three_cases.png")


def recursion_tree_figure():
    trace = []
    dc_joint(DEMO, Counter(), trace)
    fig, ax = plt.subplots(figsize=(14, 6.4))
    ax.axis("off")
    ax.set_xlim(-0.6, 7.6)
    ax.set_ylim(-0.7, 3.75)
    pos = {}
    for depth, lo, hi, s in trace:
        x = (lo + hi) / 2
        y = 3.2 - depth
        pos[(lo, hi)] = (x, y)
        best_path = lo <= 1 and hi >= 3
        face = "#d5f5e3" if best_path else "#eaf2f8"
        w = min(1.75, 0.9 * (hi - lo + 1)) if depth < 3 else 0.92
        ax.add_patch(FancyBboxPatch((x - w / 2, y - 0.33), w, 0.66, boxstyle="round,pad=0.02",
                                    facecolor=face, edgecolor="#2c3e50", lw=1.1))
        if depth < 3:
            txt = (f"[{lo}..{hi}]\nT={s.total} P={s.pre} S={s.suf}\nbest={s.best} ({s.bi}..{s.bj})")
        else:
            txt = f"h{lo}: {DEMO[lo]}\n(base case)"
        ax.text(x, y, txt, ha="center", va="center", fontsize=7.6 if depth < 3 else 7.2)
    for depth, lo, hi, s in trace:
        if lo < hi:
            mid = (lo + hi) // 2
            x, y = pos[(lo, hi)]
            for child in ((lo, mid), (mid + 1, hi)):
                cx, cy = pos[child]
                ax.plot([x, cx], [y - 0.33, cy + 0.33], color="#7f8c8d", lw=1)
    ax.text(3.5, -0.62, "T = total, P = best prefix, S = best suffix; combine: T = TL + TR, P = max(PL, TL + PR), "
            "S = max(SR, TR + SL), best = max(bestL, bestR, SL + PR).  Green: nodes containing the answer "
            "(hours 1..3).", ha="center", fontsize=8.2, style="italic")
    ax.set_title("Joint design - recursion tree of the 8-hour demo: every node returns (T, P, S, best) to its parent "
                 "(15 calls = 2n - 1, depth 3)", fontsize=10.5)
    save(fig, "q7_recursion_tree.png")


def main():
    growth_figure()
    small_n_figure()
    three_cases_figure()
    recursion_tree_figure()


if __name__ == "__main__":
    main()
