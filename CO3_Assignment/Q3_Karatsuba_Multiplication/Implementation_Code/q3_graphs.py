"""Q3 graphs - draws the figures of the Karatsuba question from the CSV files written by q3_experiments.py.

  results/q3_growth.png          single-digit multiplications and total digit operations against n (log-log)
  results/q3_time.png            execution time against n with scaled n^2 and n^log2(3) overlays
  results/q3_threshold.png       hybrid threshold sweep at 617 and 1,234 digits (operations and time)
  results/q3_recursion_tree.png  decomposition (recursion tree) of 1234 x 5678, with the level sums
Run:  py -3 q3_graphs.py   (after q3_experiments.py)
"""
import csv
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from q3_karatsuba import OpCounter, karatsuba_multiply, to_digits  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
LOG3 = math.log2(3)
C_SB, C_K, C_K16, C_TH = "tab:red", "tab:blue", "tab:green", "0.35"


def read_csv(name):
    """Rows of results/<name> as a list of dicts (numbers converted where possible)."""
    with open(os.path.join(RESULTS, name), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key, value in row.items():
            try:
                row[key] = float(value) if "." in value else int(value)
            except ValueError:
                pass
    return rows


def save(fig, name):
    """Save a figure into results/ and print its path."""
    path = os.path.join(RESULTS, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def plot_growth(rows):
    """Left: single-digit multiplications; right: total digit operations, both against n."""
    n = [r["n"] for r in rows]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    ax1.loglog(n, [r["sb_mults"] for r in rows], "o", color=C_SB, label="schoolbook (counted)")
    ax1.loglog(n, [r["k_mults"] for r in rows], "s", color=C_K, label="Karatsuba t = 1 (counted)")
    grid = [2 ** (i / 8) for i in range(24, 89)]
    ax1.loglog(grid, [x * x for x in grid], "--", color=C_SB, lw=1, label="n²")
    ax1.loglog(grid, [x ** LOG3 for x in grid], "--", color=C_K, lw=1, label="n^log₂3 = n^1.585")
    ax1.step(grid, [3 ** math.ceil(math.log2(x) - 1e-12) for x in grid], where="post", color=C_TH, lw=1,
             label="3^⌈log₂ n⌉ (step)")
    ax1.set_title("Single-digit multiplications")
    ax1.set_xlabel("number of digits n")
    ax1.set_ylabel("single-digit multiplications")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)

    ax2.loglog(n, [r["sb_total"] for r in rows], "o-", color=C_SB, label="schoolbook (3n²)")
    ax2.loglog(n, [r["k_total"] for r in rows], "s-", color=C_K, label="Karatsuba t = 1")
    ax2.loglog(n, [r["k16_total"] for r in rows], "^-", color=C_K16, label="Karatsuba t = 16 (hybrid)")
    for r in rows:
        if r["n"] in (617, 1234):
            ax2.annotate(f"{r['n']}", (r["n"], r["k_total"]), textcoords="offset points", xytext=(4, 6),
                         fontsize=7, color=C_K)
    ax2.set_title("Total digit operations (multiplications + additions)")
    ax2.set_xlabel("number of digits n")
    ax2.set_ylabel("digit operations")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.suptitle("Q3 – Schoolbook vs Karatsuba: counted operations (random operands, seed 42)", fontsize=11)
    save(fig, "q3_growth.png")


def plot_time(rows):
    """Execution time against n with theory curves scaled to the largest measurement."""
    n = [r["n"] for r in rows]
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.loglog(n, [r["sb_ms"] for r in rows], "o", color=C_SB, label="schoolbook")
    ax.loglog(n, [r["k_ms"] for r in rows], "s", color=C_K, label="Karatsuba t = 1")
    ax.loglog(n, [r["k16_ms"] for r in rows], "^", color=C_K16, label="Karatsuba t = 16")
    big = rows[-1]
    grid = [2 ** (i / 8) for i in range(24, 89)]
    c2 = big["sb_ms"] / big["n"] ** 2
    ck = big["k16_ms"] / big["n"] ** LOG3
    ax.loglog(grid, [c2 * x * x for x in grid], "--", color=C_SB, lw=1, label="c·n² (scaled)")
    ax.loglog(grid, [ck * x ** LOG3 for x in grid], "--", color=C_K16, lw=1, label="c·n^1.585 (scaled)")
    ax.set_title("Q3 – Execution time (minimum of repeated runs)")
    ax.set_xlabel("number of digits n")
    ax.set_ylabel("time (ms)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    save(fig, "q3_time.png")


def plot_threshold(rows):
    """Threshold sweep: total operations (left) and time (right) against the threshold t."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.4))
    for n, marker in ((617, "o"), (1234, "s")):
        sub = [r for r in rows if r["n"] == n and r["threshold"] != "schoolbook"]
        sb = next(r for r in rows if r["n"] == n and r["threshold"] == "schoolbook")
        t = [r["threshold"] for r in sub]
        line = ax1.semilogx(t, [r["total"] for r in sub], marker + "-", base=2, label=f"Karatsuba, n = {n}")[0]
        ax1.axhline(sb["total"], ls="--", lw=1, color=line.get_color(), label=f"schoolbook, n = {n}")
        line = ax2.semilogx(t, [r["ms"] for r in sub], marker + "-", base=2, label=f"Karatsuba, n = {n}")[0]
        ax2.axhline(sb["ms"], ls="--", lw=1, color=line.get_color(), label=f"schoolbook, n = {n}")
    ax1.set_title("Total digit operations vs threshold")
    ax1.set_ylabel("digit operations")
    ax2.set_title("Time vs threshold")
    ax2.set_ylabel("time (ms)")
    for ax in (ax1, ax2):
        ax.set_xlabel("threshold t (schoolbook used for n ≤ t digits)")
        ax.set_xticks(t)
        ax.set_xticklabels([str(v) for v in t])
        ax.set_yscale("log")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Q3 – Hybrid Karatsuba: choosing the base-case threshold", fontsize=11)
    save(fig, "q3_threshold.png")


def build_tree(trace):
    """Turn the post-order trace (depth, label, a, b, product) into nested dicts."""
    stack = []
    for depth, label, a, b, product in trace:
        node = {"depth": depth, "label": label, "a": a, "b": b, "p": product, "kids": []}
        while stack and stack[-1]["depth"] == depth + 1:
            node["kids"].insert(0, stack.pop())
        stack.append(node)
    return stack[0]


def plot_recursion_tree():
    """Recursion tree of 1234 x 5678 with the per-level cost on the right."""
    trace = []
    karatsuba_multiply(to_digits(1234), to_digits(5678), OpCounter(), 1, trace=trace)
    root = build_tree(trace)
    leaves = []

    def place(node):
        if not node["kids"]:
            node["x"] = len(leaves)
            leaves.append(node)
        else:
            for kid in node["kids"]:
                place(kid)
            node["x"] = sum(k["x"] for k in node["kids"]) / len(node["kids"])

    place(root)
    fig, ax = plt.subplots(figsize=(13, 5.2))
    colours = {"z0": "#dbe9f6", "z2": "#fde3cf", "root": "#e8e8e8"}

    def draw(node):
        y = -node["depth"] * 1.6
        for kid in node["kids"]:
            ax.plot([node["x"], kid["x"]], [y - 0.28, -kid["depth"] * 1.6 + 0.28], color="0.5", lw=1)
            draw(kid)
        key = node["label"] if node["label"] in colours else "z1"
        text = f"{node['label']}\n{node['a']} × {node['b']}\n= {node['p']}"
        ax.text(node["x"], y, text, ha="center", va="center", fontsize=8.5 if node["depth"] < 2 else 7.5,
                bbox=dict(boxstyle="round,pad=0.35", fc=colours.get(key, "#dff0d8"), ec="0.4"))

    draw(root)
    notes = ["level 0: 1 problem of n = 4 digits",
             "level 1: 3 problems of n/2 = 2 digits",
             "level 2: 3² = 9 problems of 1 digit (leaves)"]
    for d, note in enumerate(notes):
        ax.text(len(leaves) + 0.2, -d * 1.6, note, ha="left", va="center", fontsize=9, color="0.25")
    ax.text(-0.6, -3.95, "General level i: 3^i sub-problems of n/2^i digits, combine work 3^i·c·n/2^i = (3/2)^i·c·n;  "
            "leaves: 3^⌈log₂ n⌉ single-digit multiplications (here 9 instead of 16).   "
            "z1' = |a0 − a1|·|b1 − b0|, (−) = negative sign.", fontsize=8.5, color="0.2")
    ax.set_xlim(-0.8, len(leaves) + 3.6)
    ax.set_ylim(-4.2, 0.7)
    ax.axis("off")
    ax.set_title("Q3 – Karatsuba recursion tree for 1234 × 5678 (split at m = ⌈n/2⌉, three sub-products per node)",
                 fontsize=11)
    save(fig, "q3_recursion_tree.png")


def main():
    plot_growth(read_csv("q3_sizes.csv"))
    plot_time(read_csv("q3_sizes.csv"))
    plot_threshold(read_csv("q3_threshold.csv"))
    plot_recursion_tree()


if __name__ == "__main__":
    main()
