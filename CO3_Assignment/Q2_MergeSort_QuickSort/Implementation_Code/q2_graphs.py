"""Q2 graphs - decomposition diagrams and result graphs of Merge Sort vs Quick Sort.

Writes to results/: q2_mergesort_tree.png, q2_quicksort_trees.png, q2_comparisons_by_input.png, q2_bars_n8000.png
Run after q2_experiments.py:  py q2_graphs.py
"""
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
ALGS = ("Merge", "Quick-last", "Quick-random", "Quick-median3")
COLORS = {"Merge": "#1f77b4", "Quick-last": "#d62728", "Quick-random": "#2ca02c", "Quick-median3": "#ff7f0e"}
MARKS = {"Merge": "o", "Quick-last": "s", "Quick-random": "^", "Quick-median3": "D"}
INPUTS = ("random", "sorted", "reverse", "slots", "all-equal")


def read_rows():
    with open(os.path.join(RESULTS, "q2_results.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def layout(node, depth=0, counter=None):
    """Leaves left to right, parents centred above their children."""
    counter = counter if counter is not None else [0]
    node["y"] = -depth
    if not node["children"]:
        node["x"] = counter[0]
        counter[0] += 1
    else:
        for c in node["children"]:
            layout(c, depth + 1, counter)
        node["x"] = sum(c["x"] for c in node["children"]) / len(node["children"])


def draw_tree(ax, root, fontsize=8):
    layout(root)

    def draw(node):
        for c in node["children"]:
            ax.plot([node["x"], c["x"]], [node["y"], c["y"]], color="#555555", lw=1.1, zorder=1)
            draw(c)
        ax.text(node["x"], node["y"], node["text"], ha="center", va="center", fontsize=fontsize, zorder=2,
                bbox=dict(boxstyle="round,pad=0.3", fc=node.get("fc", "#eef3fb"), ec="#1f3864"))
    draw(root)
    ax.axis("off")
    ax.margins(x=0.06, y=0.15)


def fig_mergesort_tree():
    """Divide phase (unsorted halves) with the merged result written under each node."""
    data = [53, 8, 71, 107, 3, 19, 125, 85]          # deadlines in minutes after 06:00 (example)

    def build(lo, hi):
        part = data[lo:hi + 1]
        if lo == hi:
            return {"text": f"{part[0]}", "children": [], "fc": "#e2efda"}
        mid = (lo + hi) // 2
        node = {"text": f"{part}\nmerge -> {sorted(part)}", "children": [build(lo, mid), build(mid + 1, hi)]}
        return node
    fig, ax = plt.subplots(figsize=(12, 4.6))
    draw_tree(ax, build(0, 7), fontsize=8)
    ax.set_title("Merge Sort decomposition of 8 deadlines: divide in the middle down to single orders (depth log2 8 = 3),\n"
                 "then merge on the way back; every level merges n = 8 elements (<= n - 1 comparisons per level)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q2_mergesort_tree.png"), dpi=150)
    plt.close(fig)


def quick_tree(values, rule):
    """Recursion tree of Lomuto quick sort (same pivot rules as q2_sorting) on a copy of values."""
    a = list(values)

    def median3(lo, hi):
        mid = (lo + hi) // 2
        trio = sorted([(a[lo], lo), (a[mid], mid), (a[hi], hi)])
        return trio[1][1]

    def sort(lo, hi):
        if lo > hi:
            return None
        if lo == hi:
            return {"text": f"{a[lo]}", "children": [], "fc": "#e2efda"}
        p = median3(lo, hi) if (rule == "median3" and hi - lo >= 2) else hi
        a[p], a[hi] = a[hi], a[p]
        x, i = a[hi], lo - 1
        for j in range(lo, hi):
            if a[j] <= x:
                i += 1
                a[i], a[j] = a[j], a[i]
        a[i + 1], a[hi] = a[hi], a[i + 1]
        p = i + 1
        node = {"text": f"[{lo}..{hi}]\npivot {a[p]}\n{p - lo} | {hi - p}", "children": []}
        for child in (sort(lo, p - 1), sort(p + 1, hi)):
            if child is not None:
                node["children"].append(child)
        return node
    return sort(0, len(a) - 1)


def fig_quicksort_trees():
    sorted_export = [3, 8, 19, 53, 71, 85, 107, 125]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={"width_ratios": [1, 1.3]})
    draw_tree(ax1, quick_tree(sorted_export, "last"), fontsize=7.5)
    ax1.set_title("pivot = last element on the sorted export:\nevery split is (n-1) | 0, depth n - 1 = 7, "
                  "28 comparisons", fontsize=10)
    draw_tree(ax2, quick_tree(sorted_export, "median3"), fontsize=7.5)
    ax2.set_title("pivot = median of three on the same data:\nbalanced splits, depth 3", fontsize=10)
    fig.suptitle("Quick Sort recursion trees (labels: sub-array, pivot, left | right sizes)", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q2_quicksort_trees.png"), dpi=150)
    plt.close(fig)


def fig_comparisons_by_input(rows):
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for ax, inp in zip(axes.flat, INPUTS):
        for alg in ALGS:
            pts = [(int(r["n"]), int(r["comparisons"])) for r in rows if r["algorithm"] == alg and r["input"] == inp]
            ax.loglog([p[0] for p in pts], [p[1] for p in pts], MARKS[alg] + "-", color=COLORS[alg], label=alg,
                      mfc="none" if alg == "Merge" else None, ms=7)
        ref = [r for r in rows if r["algorithm"] == "Merge" and r["input"] == inp]
        ns = [int(r["n"]) for r in ref]
        ax.loglog(ns, [float(r["n_log2_n"]) for r in ref], "k--", lw=1, label="n log2 n")
        ax.loglog(ns, [int(r["n_n_minus_1_over_2"]) for r in ref], "k:", lw=1.2, label="n(n-1)/2")
        ax.set_title(f"input: {inp}")
        ax.set_xlabel("number of orders n")
        ax.set_ylabel("comparisons")
        ax.grid(True, which="both", alpha=0.3)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    axes.flat[5].axis("off")
    axes.flat[5].legend(handles, labels, loc="center", fontsize=11, title="algorithm / theory (dashed)")
    fig.suptitle("Comparisons of Merge Sort and Quick Sort on five input conditions (log-log)", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q2_comparisons_by_input.png"), dpi=150)
    plt.close(fig)


def fig_bars(rows):
    n = 8000
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    width = 0.2
    for ax, key, title in zip(axes, ("comparisons", "moves", "max_depth"),
                              ("Comparisons", "Moves (element writes)", "Maximum recursion depth")):
        for k, alg in enumerate(ALGS):
            vals = []
            for inp in INPUTS:
                r = next(r for r in rows if r["algorithm"] == alg and r["input"] == inp and int(r["n"]) == n)
                vals.append(max(int(r[key]), 1))
            ax.bar([i + (k - 1.5) * width for i in range(len(INPUTS))], vals, width, color=COLORS[alg], label=alg)
        ax.set_yscale("log")
        ax.set_xticks(range(len(INPUTS)))
        ax.set_xticklabels(INPUTS)
        ax.set_title(f"{title}, n = 8,000")
        ax.set_xlabel("input condition")
        ax.set_ylabel(title.split(" (")[0].lower() + " (log scale)")
        ax.grid(True, axis="y", which="both", alpha=0.3)
    axes[0].legend(fontsize=8)
    axes[1].text(0.02, 0.97, "moves of 0 drawn as 1", transform=axes[1].transAxes, fontsize=7, va="top")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "q2_bars_n8000.png"), dpi=150)
    plt.close(fig)


def main():
    rows = read_rows()
    fig_mergesort_tree()
    fig_quicksort_trees()
    fig_comparisons_by_input(rows)
    fig_bars(rows)
    print("Q2 graphs written to", RESULTS)


if __name__ == "__main__":
    main()
