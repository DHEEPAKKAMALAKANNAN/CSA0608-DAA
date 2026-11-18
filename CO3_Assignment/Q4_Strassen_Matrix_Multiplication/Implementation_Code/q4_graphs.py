"""Q4 graphs - draws the figures of the Strassen question from the CSV files written by q4_experiments.py.

  results/q4_growth.png         multiplications and additions against n (log-log) with theory overlays
  results/q4_cutoff.png         cutoff sweep at n = 128 and 256: total operations and time against the cutoff
  results/q4_padding.png        static vs dynamic padding for n = 100, 129, 200 (operations and time)
  results/q4_decomposition.png  block decomposition (7 products) and the 7-way recursion tree with level sums
Run:  py -3 q4_graphs.py   (after q4_experiments.py)
"""
import csv
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
LOG7 = math.log2(7)
C_CONV, C_STR, C_TH = "tab:red", "tab:blue", "0.35"


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


def plot_growth(rows, formula_rows):
    """Left: multiplications; middle: additions; right: total operations incl. the calculated crossover."""
    n = [r["n"] for r in rows]
    grid = [2 ** (i / 4) for i in range(16, 33)]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    ax = axes[0]
    ax.loglog(n, [r["conv_mults"] for r in rows], "o", color=C_CONV, label="conventional (counted)")
    ax.loglog(n, [r["str_mults"] for r in rows], "s", color=C_STR, label="Strassen c = 1 (counted)")
    ax.loglog(grid, [x ** 3 for x in grid], "--", color=C_CONV, lw=1, label="n³ = 8^k")
    ax.loglog(grid, [x ** LOG7 for x in grid], "--", color=C_STR, lw=1, label="n^log₂7 = 7^k")
    ax.set_title("Scalar multiplications")
    ax.set_ylabel("multiplications")
    ax = axes[1]
    ax.loglog(n, [r["conv_adds"] for r in rows], "o", color=C_CONV, label="conventional (counted)")
    ax.loglog(n, [r["str_adds"] for r in rows], "s", color=C_STR, label="Strassen c = 1 (counted)")
    ax.loglog(grid, [x * x * (x - 1) for x in grid], "--", color=C_CONV, lw=1, label="n²(n − 1)")
    ax.loglog(grid, [6 * (x ** LOG7 - x * x) for x in grid], "--", color=C_STR, lw=1, label="6(7^k − 4^k)")
    ax.set_title("Scalar additions / subtractions")
    ax.set_ylabel("additions")
    ax = axes[2]
    fn = [r["n"] for r in formula_rows]
    ax.loglog(fn, [r["conv_total"] for r in formula_rows], "--", color=C_CONV, lw=1, label="conventional (formula)")
    ax.loglog(fn, [r["str1_total"] for r in formula_rows], "--", color=C_STR, lw=1, label="Strassen c = 1 (formula)")
    ax.loglog(fn, [r["str8_total"] for r in formula_rows], "--", color="tab:green", lw=1,
              label="Strassen c = 8 (formula)")
    ax.loglog(n, [r["conv_total"] for r in rows], "o", color=C_CONV, label="conventional (counted)")
    ax.loglog(n, [r["str_total"] for r in rows], "s", color=C_STR, label="Strassen c = 1 (counted)")
    ax.axvline(1024, color=C_TH, lw=0.8, ls=":")
    ax.text(1024, 30, " pure Strassen\n cheaper from\n n = 1024", fontsize=7, color=C_TH)
    ax.set_title("Total operations (crossover)")
    ax.set_ylabel("multiplications + additions")
    for ax in axes:
        ax.set_xlabel("matrix size n (zones)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=7)
    fig.suptitle("Q4 – Conventional vs Strassen: counted operations against the closed forms", fontsize=11)
    save(fig, "q4_growth.png")


def plot_cutoff(rows):
    """Cutoff sweep: total operations (left) and time (right) against the cutoff c."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.4))
    for n, marker in ((128, "o"), (256, "s")):
        sub = [r for r in rows if r["n"] == n and r["cutoff"] != "conventional"]
        conv = next(r for r in rows if r["n"] == n and r["cutoff"] == "conventional")
        c = [r["cutoff"] for r in sub]
        line = ax1.plot(c, [r["total"] for r in sub], marker + "-", label=f"Strassen, n = {n}")[0]
        ax1.axhline(conv["total"], ls="--", lw=1, color=line.get_color(), label=f"conventional, n = {n}")
        line = ax2.plot(c, [r["ms"] for r in sub], marker + "-", label=f"Strassen, n = {n}")[0]
        ax2.axhline(conv["ms"], ls="--", lw=1, color=line.get_color(), label=f"conventional, n = {n}")
    ax1.axvline(8, color=C_TH, lw=0.8, ls=":")
    ax1.text(8, ax1.get_ylim()[1] * 0.6, " analytic optimum c = 8", fontsize=8, color=C_TH)
    ax1.set_title("Total scalar operations vs cutoff")
    ax1.set_ylabel("multiplications + additions")
    ax2.set_title("Time vs cutoff (Python)")
    ax2.set_ylabel("time (ms)")
    for ax in (ax1, ax2):
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(c)
        ax.set_xticklabels([str(v) for v in c])
        ax.set_xlabel("cutoff c (conventional multiplication for n ≤ c)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Q4 – Hybrid Strassen: choosing the cutoff", fontsize=11)
    save(fig, "q4_cutoff.png")


def plot_padding(rows):
    """Grouped bars: total operations and time for conventional / static / dynamic padding (cutoff 32 and 8)."""
    sizes = sorted({r["n"] for r in rows})
    variants = [("conventional", "", "conventional", C_CONV), ("strassen_static", 8, "static, c = 8", "#9ecae1"),
                ("strassen_dynamic", 8, "dynamic, c = 8", "#3182bd"), ("strassen_static", 32, "static, c = 32", "#c7e9c0"),
                ("strassen_dynamic", 32, "dynamic, c = 32", "#31a354")]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.4))
    width = 0.16
    for i, (method, cutoff, label, colour) in enumerate(variants):
        sel = [next(r for r in rows if r["n"] == n and r["method"] == method and r["cutoff"] == cutoff)
               for n in sizes]
        xs = [k + (i - 2) * width for k in range(len(sizes))]
        ax1.bar(xs, [r["total"] / 1e6 for r in sel], width, color=colour, label=label, edgecolor="0.3", lw=0.5)
        ax2.bar(xs, [r["ms"] for r in sel], width, color=colour, label=label, edgecolor="0.3", lw=0.5)
    for ax, title, ylabel in ((ax1, "Total scalar operations", "operations (millions)"),
                              (ax2, "Time (Python, minimum of 3 runs)", "time (ms)")):
        ax.set_xticks(range(len(sizes)))
        ax.set_xticklabels([f"n = {n}" for n in sizes])
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Q4 – Sizes that are not powers of 2: static padding (to 128/256) vs dynamic padding", fontsize=11)
    save(fig, "q4_padding.png")


def plot_decomposition():
    """Left: the 2 x 2 block decomposition and the 7 products; right: the 7-way recursion tree with level sums."""
    fig = plt.figure(figsize=(15, 6))
    ax = fig.add_axes([0.0, 0.0, 0.42, 1.0])
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    def block_matrix(x0, y0, name):
        for r in range(2):
            for c in range(2):
                ax.add_patch(Rectangle((x0 + c * 1.1, y0 + (1 - r) * 1.1), 1.1, 1.1, fc="#dbe9f6", ec="0.3"))
                ax.text(x0 + c * 1.1 + 0.55, y0 + (1 - r) * 1.1 + 0.55, f"{name}{r + 1}{c + 1}", ha="center",
                        va="center", fontsize=10)
        ax.text(x0 + 1.1, y0 + 2.45, f"{name} (n × n)", ha="center", fontsize=9)

    block_matrix(0.3, 7.0, "A")
    ax.text(2.85, 8.1, "×", fontsize=16, ha="center", va="center")
    block_matrix(3.3, 7.0, "B")
    ax.text(5.85, 8.1, "=", fontsize=16, ha="center", va="center")
    block_matrix(6.3, 7.0, "C")
    lines = ["DIVIDE: 4 blocks of (n/2) × (n/2) each",
             "CONQUER: 7 products (10 block additions prepare them)",
             "  M1 = (A11 + A22)(B11 + B22)     M2 = (A21 + A22) B11",
             "  M3 = A11 (B12 − B22)            M4 = A22 (B21 − B11)",
             "  M5 = (A11 + A12) B22            M6 = (A21 − A11)(B11 + B12)",
             "  M7 = (A12 − A22)(B21 + B22)",
             "COMBINE (8 more block additions):",
             "  C11 = M1 + M4 − M5 + M7        C12 = M3 + M5",
             "  C21 = M2 + M4                  C22 = M1 − M2 + M3 + M6",
             "Per call: 7 products + 18 additions of (n/2)² entries"]
    for i, line in enumerate(lines):
        ax.text(0.3, 6.0 - i * 0.6, line, fontsize=9, family="monospace")

    ax = fig.add_axes([0.44, 0.0, 0.56, 1.0])
    ax.axis("off")
    ax.set_xlim(-0.5, 49.5)
    ax.set_ylim(-5.4, 0.8)
    ax.text(24.5, 0, "n × n", ha="center", va="center", fontsize=9, bbox=dict(boxstyle="round", fc="#e8e8e8"))
    xs1 = [3.5 + 7 * i for i in range(7)]
    for i, x in enumerate(xs1):
        ax.plot([24.5, x], [-0.3, -1.7], color="0.5", lw=0.8)
        ax.text(x, -2.0, f"M{i + 1}\nn/2", ha="center", va="center", fontsize=8,
                bbox=dict(boxstyle="round", fc="#dbe9f6"))
        for j in range(7):
            xx = x - 3 + j
            ax.plot([x, xx], [-2.35, -3.55], color="0.7", lw=0.5)
            ax.plot(xx, -3.7, "o", ms=3.5, color="tab:blue")
    ax.text(24.5, -4.35, "level 2: 7² = 49 products of size n/4    …    level k = log₂ n: 7^k = n^log₂7 ≈ n^2.807 "
            "scalar products (leaves)", ha="center", fontsize=8.5, color="0.2")
    ax.text(24.5, -5.0, "Additions: level i has 7^i calls × 18·(n/2^(i+1))² = (9/2)·n²·(7/4)^i  →  "
            "Σ over i < k = 6(7^k − 4^k)", ha="center", fontsize=8.5, color="0.2")
    ax.text(49.5, 0, "level 0: 1 call", ha="right", fontsize=8.5, color="0.25")
    ax.text(49.5, -1.2, "level 1: 7 calls", ha="right", fontsize=8.5, color="0.25")
    fig.suptitle("Q4 – Strassen decomposition: 2 × 2 blocks, 7 products per call, 7-way recursion tree", fontsize=12,
                 y=1.05)
    save(fig, "q4_decomposition.png")


def main():
    plot_growth(read_csv("q4_growth.csv"), read_csv("q4_crossover_formula.csv"))
    plot_cutoff(read_csv("q4_cutoff.csv"))
    plot_padding(read_csv("q4_padding.csv"))
    plot_decomposition()


if __name__ == "__main__":
    main()
