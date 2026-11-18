"""SwiftLogix - Module 2 experiments: quick-sort pivot rules, worst cases, duplicates and the final hybrid.

Arrangements of the priority data:
    random    - distinct-looking integers 0..10^9          scores   - real priority scores 0..100 (duplicate-heavy)
    sorted    - already ranked (e.g. re-ranking an almost unchanged queue)       reversed - descending order
Variants: last (baseline Lomuto, last-element pivot), median3, random pivot, 3way (random pivot + Dijkstra
3-way partition) and hybrid (introsort-style final design).  Merge sort (Module 1) is run on the same data
for the cross-module comparison.  Quadratic cases are capped at small n so the script finishes in ~2 minutes.
Counts are the primary evidence; times are the median of 3 runs (1 run for the slow quadratic cases).

Run:  py -3 quick_sort_experiments.py
"""
import csv
import math
import random
import statistics
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from quick_sort import OpCounter, quick_sort, quick_sort_3way, quick_sort_hybrid  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Module_1_Merge_Sort" / "Source_Code"))
import merge_sort as m1  # noqa: E402

RESULTS = ROOT / "Supporting_Files" / "results"
GRAPHS = ROOT / "Module_2_Quick_Sort" / "Report" / "graphs"
SIZES = [2 ** k for k in range(10, 18)]                 # 1,024 ... 131,072
DISTS = ["random", "scores", "sorted", "reversed"]
VARIANTS = ["last", "median3", "random", "3way", "hybrid", "hybrid_fixed"]
# largest n run for combinations that are quadratic (Lomuto on sorted input / on heavy duplicates)
CAP = {("last", "sorted"): 4096, ("last", "reversed"): 4096, ("last", "scores"): 32768,
       ("median3", "scores"): 32768, ("random", "scores"): 32768}


def make_input(dist, n, seed=42):
    rng = random.Random(seed + n)
    if dist == "scores":
        return [rng.randint(0, 100) for _ in range(n)]
    data = [rng.randrange(10 ** 9) for _ in range(n)]
    if dist == "sorted":
        data.sort()
    elif dist == "reversed":
        data.sort(reverse=True)
    return data


def run(variant, data):
    b = list(data)
    c = OpCounter()
    if variant == "3way":
        quick_sort_3way(b, counter=c)
    elif variant == "hybrid":
        quick_sort_hybrid(b, counter=c)
    elif variant == "hybrid_fixed":
        quick_sort_hybrid(b, counter=c, pivot_sample="fixed")
    else:
        quick_sort(b, pivot=variant, counter=c)
    return b, c


def measure(variant, data, dist):
    """Counts + median time; the quadratic (capped) combinations are timed once to save time."""
    reps = 1 if (variant, dist) in CAP and len(data) >= 4096 else 3
    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        b, c = run(variant, data)
        times.append((time.perf_counter() - t0) * 1000)
    assert b == sorted(data), f"{variant} failed"
    return c, statistics.median(times)


def save_csv(name, header, rows):
    for folder in (RESULTS, GRAPHS):
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    res, rows = {}, []
    for dist in DISTS:
        for n in SIZES:
            data = make_input(dist, n)
            for v in VARIANTS:
                if n > CAP.get((v, dist), 10 ** 9):
                    continue
                c, ms = measure(v, data, dist)
                res[dist, n, v] = (c, ms)
                rows.append([dist, n, v, c.comparisons, c.swaps, c.partitions, c.max_depth, c.fallbacks,
                             round(ms, 3)])
    save_csv("m2_quick_sort_experiments.csv", ["distribution", "n", "variant", "comparisons", "swaps",
                                               "partitions", "max_depth", "heap_fallbacks", "time_ms"], rows)

    print("=" * 112)
    print("M2 experiment A - RANDOM input: counted comparisons vs theory (expected 2(n+1)H_n - 4n ~ 1.386 n lg n)")
    print("=" * 112)
    print(f"{'n':>7} | {'baseline':>10} {'expected':>10} {'ratio':>5} | {'median3':>10} {'random':>10} {'3way':>10} "
          f"{'hybrid':>10} | {'base ms':>7} {'hyb ms':>7} | {'depth b/h':>9}")
    for n in SIZES:
        h = sum(1 / k for k in range(1, n + 1))
        exp = 2 * (n + 1) * h - 4 * n
        cb = res["random", n, "last"][0]
        cells = [res["random", n, v][0].comparisons for v in VARIANTS]
        print(f"{n:>7,} | {cells[0]:>10,} {exp:>10,.0f} {cells[0] / exp:>5.3f} | {cells[1]:>10,} {cells[2]:>10,} "
              f"{cells[3]:>10,} {cells[4]:>10,} | {res['random', n, 'last'][1]:>7.1f} "
              f"{res['random', n, 'hybrid'][1]:>7.1f} | {cb.max_depth:>4}/{res['random', n, 'hybrid'][0].max_depth:<4}")

    print()
    print("M2 experiment B - WORST CASE for the baseline: already-sorted input (comparisons / max recursion depth)")
    print(f"{'n':>7} | {'baseline':>15} {'n(n-1)/2':>13} | {'median3':>12} {'random':>12} {'hybrid':>12} | "
          f"{'hybrid fixed-m3':>15} {'fallbk':>6} | {'base ms':>7} {'hyb ms':>6}")
    for n in [s for s in SIZES if s <= 4096] + SIZES[-2:]:
        b = res.get(("sorted", n, "last"))
        btxt = f"{b[0].comparisons:>9,}/{b[0].max_depth:<5}" if b else f"{'(not run)':>15}"
        cells = [f"{res['sorted', n, v][0].comparisons:,}/{res['sorted', n, v][0].max_depth}"
                 for v in ("median3", "random", "hybrid", "hybrid_fixed")]
        print(f"{n:>7,} | {btxt} {n * (n - 1) // 2:>13,} | {cells[0]:>12} {cells[1]:>12} {cells[2]:>12} | "
              f"{cells[3]:>15} {res['sorted', n, 'hybrid_fixed'][0].fallbacks:>6} | "
              f"{(f'{b[1]:.1f}' if b else '-'):>7} {res['sorted', n, 'hybrid'][1]:>6.1f}")
    print("baseline: comparisons = n(n-1)/2 exactly and depth = n - 1.  hybrid fixed-m3 = median of a[lo], a[mid], a[hi]:")
    print("the 3-way partition rotates sorted data so the fixed sample picks bad pivots -> heap-sort fallback triggers;")
    print("sampling the three candidates at random positions (final hybrid) avoids this.")

    print()
    print("M2 experiment C - DUPLICATE-HEAVY priority scores (k = 101 distinct values 0..100)")
    print(f"{'n':>7} | {'baseline':>11} {'n^2/(2k)':>11} | {'median3':>11} {'random':>11} | {'3way':>9} {'hybrid':>9} "
          f"{'1.39 n lg k':>11} | {'base ms':>8} {'hyb ms':>7}")
    for n in SIZES:
        cells = []
        for v in VARIANTS:
            r = res.get(("scores", n, v))
            cells.append(f"{r[0].comparisons:,}" if r else "-")
        b = res.get(("scores", n, "last"))
        print(f"{n:>7,} | {cells[0]:>11} {n * n / 202:>11,.0f} | {cells[1]:>11} {cells[2]:>11} | {cells[3]:>9} "
              f"{cells[4]:>9} {1.386 * n * math.log2(101):>11,.0f} | {(f'{b[1]:.1f}' if b else '-'):>8} "
              f"{res['scores', n, 'hybrid'][1]:>7.1f}")
    print("Lomuto sends every key equal to the pivot to one side -> quadratic on equal keys; 3-way partitioning fixes it")

    # --- cross-module comparison with merge sort (Module 1) on the same data
    n = SIZES[-1]
    cmp_rows = []
    print()
    print(f"M2 experiment D - quick sort vs merge sort (Module 1) on the same data, n = {n:,}")
    print(f"{'data':<8} {'algorithm':<22} | {'comparisons':>11} {'moves/swaps':>11} | {'time ms':>8} | extra memory")
    for dist in ("random", "scores"):
        data = make_input(dist, n)
        for name, fn in (("merge sort (top-down)", None), ("quick sort (hybrid)", "hybrid"),
                         ("quick sort (3-way)", "3way")):
            if fn is None:
                times = []
                for _ in range(3):
                    c = m1.OpCounter()
                    t0 = time.perf_counter()
                    m1.merge_sort(data, counter=c)
                    times.append((time.perf_counter() - t0) * 1000)
                comps, moves, mem = c.comparisons, c.moves, "n-element buffer"
            else:
                c, ms = measure(fn, data, dist)
                times = [ms]
                comps, moves, mem = c.comparisons, c.swaps, "O(log n) stack"
            ms = statistics.median(times)
            cmp_rows.append([dist, n, name, comps, moves, round(ms, 3)])
            print(f"{dist:<8} {name:<22} | {comps:>11,} {moves:>11,} | {ms:>8.1f} | {mem}")
    save_csv("m2_merge_vs_quick.csv", ["distribution", "n", "algorithm", "comparisons", "moves_or_swaps",
                                       "time_ms"], cmp_rows)
    plot(res, cmp_rows)
    print("\nCSV : Supporting_Files/results/m2_quick_sort_experiments.csv, m2_merge_vs_quick.csv")
    print("PNG : Module_2_Quick_Sort/Report/graphs/m2_worst_case.png, m2_random_and_duplicates.png, "
          "m2_merge_vs_quick.png")


def plot(res, cmp_rows):
    labels = {"last": "baseline (last pivot)", "median3": "median-of-3", "random": "random pivot",
              "3way": "3-way + random", "hybrid": "hybrid (final)", "hybrid_fixed": "hybrid, fixed median-of-3"}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    for v, mk in zip(VARIANTS, "os^dvx"):
        ns = [n for n in SIZES if ("sorted", n, v) in res]
        ax1.loglog(ns, [res["sorted", n, v][0].comparisons for n in ns], mk + "-", label=labels[v])
        ax2.loglog(ns, [max(res["sorted", n, v][0].max_depth, 1) for n in ns], mk + "-", label=labels[v])
    ax1.loglog(SIZES, [n * (n - 1) / 2 for n in SIZES], "r:", label="theory n(n-1)/2")
    ax1.loglog(SIZES, [1.386 * n * math.log2(n) for n in SIZES], "k--", label="theory 1.39 n log2 n")
    ax2.loglog(SIZES, [n - 1 for n in SIZES], "r:", label="theory n - 1")
    ax2.loglog(SIZES, [math.log2(n) for n in SIZES], "k--", label="theory log2 n")
    ax1.set(title="Comparisons on ALREADY-SORTED input", xlabel="n (orders)", ylabel="comparisons")
    ax2.set(title="Maximum recursion depth on ALREADY-SORTED input", xlabel="n (orders)", ylabel="depth (frames)")
    for ax in (ax1, ax2):
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Module 2 - quick sort worst case and the effect of the pivot rule")
    fig.tight_layout()
    fig.savefig(GRAPHS / "m2_worst_case.png", dpi=150)
    plt.close(fig)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    for v, mk in zip(VARIANTS, "os^dv"):
        ax1.semilogx(SIZES, [res["random", n, v][0].comparisons / (n * math.log2(n)) for n in SIZES], mk + "-",
                     label=labels[v])
        ns = [n for n in SIZES if ("scores", n, v) in res]
        ax2.loglog(ns, [res["scores", n, v][0].comparisons for n in ns], mk + "-", label=labels[v])
    exact = [(2 * (n + 1) * sum(1 / k for k in range(1, n + 1)) - 4 * n) / (n * math.log2(n)) for n in SIZES]
    ax1.semilogx(SIZES, exact, "k--", label="theory (2(n+1)H_n - 4n) / (n log2 n)")
    ax1.axhline(2 * math.log(2), color="k", ls=":", label="asymptote 2 ln 2 = 1.386")
    ax2.loglog(SIZES, [n * n / 202 for n in SIZES], "r:", label="theory n^2 / (2k), k = 101")
    ax2.loglog(SIZES, [1.386 * n * math.log2(101) for n in SIZES], "k--", label="theory 1.39 n log2 k")
    ax1.set(title="RANDOM input: comparisons / (n log2 n)", xlabel="n (orders)", ylabel="comparisons / (n log2 n)")
    ax2.set(title="DUPLICATE-HEAVY scores 0..100: comparisons", xlabel="n (orders)", ylabel="comparisons")
    for ax in (ax1, ax2):
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Module 2 - average case and duplicate keys")
    fig.tight_layout()
    fig.savefig(GRAPHS / "m2_random_and_duplicates.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    names = ["merge sort (top-down)", "quick sort (hybrid)", "quick sort (3-way)"]
    for ai, (col, title) in enumerate(((3, "Comparisons"), (4, "Moves / swaps"), (5, "Time (ms, median of 3)"))):
        for di, dist in enumerate(("random", "scores")):
            vals = [r[col] for r in cmp_rows if r[0] == dist]
            axes[ai].bar([i + (di - 0.5) * 0.38 for i in range(3)], vals, 0.38, label=f"{dist} data")
        axes[ai].set_xticks(range(3), ["merge", "quick hybrid", "quick 3-way"])
        axes[ai].set(title=title, xlabel="algorithm", ylabel=title.split(" (")[0].lower())
        axes[ai].grid(True, axis="y", alpha=0.3)
        axes[ai].legend(fontsize=8)
    fig.suptitle(f"Merge sort vs quick sort on the same {SIZES[-1]:,} keys")
    fig.tight_layout()
    fig.savefig(GRAPHS / "m2_merge_vs_quick.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
