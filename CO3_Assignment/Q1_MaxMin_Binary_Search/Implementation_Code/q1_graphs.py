"""Q1 graphs - draws the recursion trees and the result graphs of Q1 from results/*.csv.

Writes to results/: q1_maxmin_tree.png, q1_split_rules.png, q1_bsearch_tree.png,
                    q1_maxmin_comparisons.png, q1_maxmin_time.png, q1_binary_search.png
Run after q1_experiments.py:  py q1_graphs.py
"""
import csv
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from q1_maxmin_binsearch import left_part_size  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
C_NAIVE, C_HALF, C_EVEN, C_PAIR, C_THEORY = "#7f7f7f", "#d62728", "#1f77b4", "#2ca02c", "black"


def read_csv(name):
    with open(os.path.join(RESULTS, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def layout(node, depth=0, counter=None):
    """Give every node (dict with 'children') an (x, y): leaves left to right, parents centred."""
    counter = counter if counter is not None else [0]
    node["y"] = -depth
    if not node["children"]:
        node["x"] = counter[0]
        counter[0] += 1
    else:
        for child in node["children"]:
            layout(child, depth + 1, counter)
        node["x"] = sum(c["x"] for c in node["children"]) / len(node["children"])


def draw_tree(ax, root, fontsize=8):
    """Draw boxes and edges of a laid-out tree on ax."""
    layout(root)

    def draw(node):
        for child in node["children"]:
            style = dict(color=child.get("edge", "#555555"), lw=child.get("lw", 1.2))
            ax.plot([node["x"], child["x"]], [node["y"], child["y"]], zorder=1, **style)
            draw(child)
        ax.text(node["x"], node["y"], node["text"], ha="center", va="center", fontsize=fontsize, zorder=2,
                bbox=dict(boxstyle="round,pad=0.35", fc=node.get("fc", "#eef3fb"), ec=node.get("ec", "#1f3864")))
    draw(root)
    ax.axis("off")
    ax.margins(x=0.08, y=0.18)


def maxmin_tree(a, lo, hi, rule="half"):
    """Build the recursion tree of D&C Max-Min (same division as maxmin_dc) with labels."""
    n = hi - lo + 1
    if n == 1:
        return {"text": f"[{lo}]\n{a[lo]}\n0 cmp", "children": [], "fc": "#fde9d9"}, a[lo], a[lo]
    if n == 2:
        big, small = max(a[lo], a[hi]), min(a[lo], a[hi])
        return {"text": f"[{lo}..{hi}]\n{a[lo]}, {a[hi]}\nmax {big} / min {small}\n1 cmp", "children": [],
                "fc": "#e2efda"}, big, small
    k = left_part_size(n, rule)
    left, mx1, mn1 = maxmin_tree(a, lo, lo + k - 1, rule)
    right, mx2, mn2 = maxmin_tree(a, lo + k, hi, rule)
    big, small = max(mx1, mx2), min(mn1, mn2)
    return {"text": f"[{lo}..{hi}]\nmax {big} / min {small}\n+2 cmp", "children": [left, right]}, big, small


def size_tree(n, rule):
    """Tree of sub-problem sizes for a division rule, with comparisons per node."""
    if n == 1:
        return {"text": "n=1\n0", "children": [], "fc": "#fde9d9"}
    if n == 2:
        return {"text": "n=2\n1", "children": [], "fc": "#e2efda"}
    k = left_part_size(n, rule) if rule != "pairs" else 2
    return {"text": f"n={n}\n+2", "children": [size_tree(k, rule), size_tree(n - k, rule)]}


def count_tree(node):
    """Total comparisons stored in the size-tree labels."""
    own = int(node["text"].split("\n")[1].replace("+", ""))
    return own + sum(count_tree(c) for c in node["children"])


def fig_maxmin_tree():
    temps = [31.5, 28.0, 44.2, 39.9, 25.1, 47.3, 30.6, 41.8]
    root, _, _ = maxmin_tree(temps, 0, 7)
    fig, ax = plt.subplots(figsize=(11, 4.6))
    draw_tree(ax, root, fontsize=8.5)
    ax.set_title("D&C Max-Min recursion tree for one 8-reading flight (deg C)\n"
                 "4 leaves x 1 comparison + 3 combine steps x 2 comparisons = 10 = 3n/2 - 2 "
                 "(straightforward scan: 2n - 2 = 14)", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q1_maxmin_tree.png"), dpi=150)
    plt.close(fig)


def fig_split_rules():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax, rule, title in zip(axes, ("half", "even", "pairs"),
                               ("rule 'half' (3 | 3)", "rule 'even' (4 | 2)", "'2 | rest' = pairwise loop")):
        root = size_tree(6, rule)
        draw_tree(ax, root, fontsize=9)
        ax.set_title(f"n = 6, {title}: {count_tree(root)} comparisons", fontsize=10)
    fig.suptitle("Division rule when n is not a power of 2: every lone-reading leaf (red) wastes half a comparison; "
                 "optimum ceil(3n/2) - 2 = 7", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q1_split_rules.png"), dpi=150)
    plt.close(fig)


def fig_bsearch_tree():
    manifest = [10210, 10342, 10477, 10519, 10604, 10788, 10835, 10912,
                11050, 11163, 11297, 11348, 11402, 11586, 11621, 11799]
    path_found = {7, 11}            # probes for parcel 11348
    path_absent = {7, 3, 5, 4}      # probes for parcel 10600 (absent)

    def build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = {"text": f"a[{mid}]\n{manifest[mid]}", "children": []}
        if mid in path_found:
            node["fc"], node["ec"] = "#e2efda", "#2ca02c"
        elif mid in path_absent:
            node["fc"], node["ec"] = "#fde9d9", "#d62728"
        for child in (build(lo, mid - 1), build(mid + 1, hi)):
            if child is not None:
                node["children"].append(child)
        return node
    fig, ax = plt.subplots(figsize=(13, 4.4))
    draw_tree(ax, build(0, 15), fontsize=7.5)
    ax.set_title("Binary-search decision tree of the 16-parcel manifest: every look-up follows one root-to-node path; "
                 "height = floor(log2 16) + 1 = 5 probes\n"
                 "green = path of parcel 11348 (found after 2 probes), red = path of parcel 10600 "
                 "(absent, 4 probes)", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q1_bsearch_tree.png"), dpi=150)
    plt.close(fig)


def fig_maxmin_comparisons():
    growth, sweep = read_csv("q1_maxmin_growth.csv"), read_csv("q1_maxmin_sweep.csv")
    n = [int(r["n"]) for r in growth]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))
    ax1.loglog(n, [int(r["naive_comparisons"]) for r in growth], "s", color=C_NAIVE, label="naive scan (counted)")
    ax1.loglog(n, [int(r["half_comparisons"]) for r in growth], "^", color=C_HALF, label="D&C 'half' (counted)")
    ax1.loglog(n, [int(r["even_comparisons"]) for r in growth], "o", color=C_EVEN, mfc="none", ms=9,
               label="D&C 'even' (counted)")
    ax1.loglog(n, [int(r["pairwise_comparisons"]) for r in growth], "x", color=C_PAIR, label="pairwise loop (counted)")
    nn = [10 ** (3 + i / 20) for i in range(61)]
    ax1.loglog(nn, [2 * x - 2 for x in nn], "--", color=C_NAIVE, lw=1, label="theory 2n - 2")
    ax1.loglog(nn, [1.5 * x - 2 for x in nn], "--", color=C_THEORY, lw=1, label="theory 3n/2 - 2")
    ax1.set_xlabel("number of readings n")
    ax1.set_ylabel("element comparisons")
    ax1.set_title("Comparisons grow linearly; D&C saves 25%")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)
    ns = [int(r["n"]) for r in sweep]
    ax2.plot(ns, [int(r["naive"]) / int(r["n"]) for r in sweep], color=C_NAIVE, lw=1, label="naive: (2n - 2)/n")
    ax2.plot(ns, [int(r["dc_half"]) / int(r["n"]) for r in sweep], color=C_HALF, lw=0.8, label="D&C 'half'")
    ax2.plot(ns, [int(r["dc_even"]) / int(r["n"]) for r in sweep], color=C_EVEN, lw=1.2,
             label="D&C 'even' = pairwise = optimum")
    for k in range(2, 12):
        ax2.axvline(2 ** k, color="#bbbbbb", lw=0.6, ls=":")
    ax2.set_ylim(1.2, 2.05)
    ax2.set_xscale("log", base=2)
    ax2.set_xlabel("number of readings n (log scale; dotted lines = powers of 2)")
    ax2.set_ylabel("comparisons per reading")
    ax2.set_title("Every n from 2 to 2,048: 'half' is optimal only at powers of 2")
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q1_maxmin_comparisons.png"), dpi=150)
    plt.close(fig)


def fig_maxmin_time():
    growth = read_csv("q1_maxmin_growth.csv")
    n = [int(r["n"]) for r in growth]
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for key, color, mark, label in (("time_naive_ms", C_NAIVE, "s", "naive scan"),
                                    ("time_half_ms", C_HALF, "^", "D&C 'half' (recursive)"),
                                    ("time_even_ms", C_EVEN, "o", "D&C 'even' (recursive)"),
                                    ("time_pairwise_ms", C_PAIR, "x", "pairwise loop")):
        ax.loglog(n, [max(float(r[key]), 0.01) for r in growth], mark + "-", color=color, label=label)
    ref = float(growth[-1]["time_naive_ms"]) / n[-1]
    ax.loglog(n, [ref * x for x in n], "--", color=C_THEORY, lw=1, label="c * n (scaled to naive at 10^6)")
    ax.set_xlabel("number of readings n")
    ax.set_ylabel("time (ms, min of 3 runs)")
    ax.set_title("Time: all linear, but recursion costs ~8x in Python")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q1_maxmin_time.png"), dpi=150)
    plt.close(fig)


def fig_binary_search():
    rows = read_csv("q1_binary_search.csv")
    n = [int(r["n"]) for r in rows]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))
    nn = sorted({int(10 ** (2.7 + e / 400)) for e in range(0, 1330)})
    ax1.step(nn, [math.floor(math.log2(x)) + 1 for x in nn], where="post", color=C_THEORY, lw=1,
             label="theory worst case floor(log2 n) + 1")
    ax1.plot(nn, [math.log2(x) - 1 for x in nn], "--", color=C_EVEN, lw=1, label="approximation log2 n - 1")
    ax1.plot(n, [int(r["max_probes_successful"]) for r in rows], "s", color=C_HALF, ms=8, mfc="none",
             label="measured worst case (all keys)")
    ax1.plot(n, [float(r["avg_probes_successful"]) for r in rows], "o", color=C_EVEN, label="measured average, found")
    ax1.plot(n, [float(r["avg_probes_unsuccessful"]) for r in rows], "^", color=C_PAIR,
             label="measured average, absent")
    ax1.set_xscale("log")
    ax1.set_xlabel("manifest size n (parcels)")
    ax1.set_ylabel("probes (three-way comparisons) per look-up")
    ax1.set_title("Binary search: probes grow by 1 per doubling of n")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.loglog(n, [float(r["sequential_avg_successful"]) for r in rows], "s-", color=C_NAIVE,
               label="sequential search, average (n + 1)/2")
    ax2.loglog(n, [float(r["sequential_unsuccessful"]) for r in rows], "s--", color=C_NAIVE, mfc="none",
               label="sequential search, absent (n)")
    ax2.loglog(n, [float(r["avg_probes_successful"]) for r in rows], "o-", color=C_EVEN,
               label="binary search, average found")
    ax2.loglog(n, [int(r["max_probes_unsuccessful"]) for r in rows], "^-", color=C_PAIR,
               label="binary search, worst case")
    ax2.set_xlabel("manifest size n (parcels)")
    ax2.set_ylabel("comparisons per look-up")
    ax2.set_title("Binary vs sequential search (log-log)")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q1_binary_search.png"), dpi=150)
    plt.close(fig)


def main():
    fig_maxmin_tree()
    fig_split_rules()
    fig_bsearch_tree()
    fig_maxmin_comparisons()
    fig_maxmin_time()
    fig_binary_search()
    print("Q1 graphs written to", RESULTS)


if __name__ == "__main__":
    main()
