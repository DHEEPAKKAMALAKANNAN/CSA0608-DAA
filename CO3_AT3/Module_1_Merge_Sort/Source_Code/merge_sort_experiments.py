"""SwiftLogix - Module 1 experiments: merge sort vs the insertion-sort baseline and the improved variants.

Inputs are event timestamps (seconds in a 3-day window, so duplicates occur) in four arrangements:
    random     - events in arbitrary order
    hub_feeds  - the nightly file as delivered: 64 hub feeds, each already in time order, concatenated
    sorted     - already sorted          reversed - sorted in descending order
Operation counts are the primary evidence; wall-clock times (median of 3 runs) are secondary.
Writes CSVs to Supporting_Files/results (+ copies next to the graphs) and graphs to Report/graphs.

Run:  py -3 merge_sort_experiments.py        (about 1-2 minutes)
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

from merge_sort import OpCounter, insertion_sort, merge_sort, merge_sort_hybrid, natural_merge_sort  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "Supporting_Files" / "results"
GRAPHS = ROOT / "Module_1_Merge_Sort" / "Report" / "graphs"
SIZES = [2 ** k for k in range(10, 18)]          # 1,024 ... 131,072
INSERTION_MAX = 4096                             # insertion sort is Theta(n^2): keep it small
DISTS = ["random", "hub_feeds", "sorted", "reversed"]
HUBS = 64
ALGOS = {"top_down": merge_sort, "hybrid16": merge_sort_hybrid, "natural": natural_merge_sort,
         "insertion": insertion_sort}
REPS = 3


def make_input(dist, n, seed=42):
    """Deterministic event-timestamp keys for one experiment."""
    rng = random.Random(seed + n)
    keys = [rng.randrange(3 * 86400) for _ in range(n)]
    if dist == "hub_feeds":                      # 64 chronologically ordered hub feeds, concatenated
        size = math.ceil(n / HUBS)
        keys = [k for h in range(0, n, size) for k in sorted(keys[h:h + size])]
    elif dist == "sorted":
        keys.sort()
    elif dist == "reversed":
        keys.sort(reverse=True)
    return keys


def measure(algo, data):
    """Return (OpCounter, median time in ms) of sorting a copy of data; checks the result."""
    times, c = [], None
    for _ in range(REPS):
        c = OpCounter()
        t0 = time.perf_counter()
        out = ALGOS[algo](data, counter=c)
        times.append((time.perf_counter() - t0) * 1000)
    assert out == sorted(data), f"{algo} produced a wrong result"
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
    rows, res = [], {}
    for dist in DISTS:
        for n in SIZES:
            data = make_input(dist, n)
            for algo in ALGOS:
                if algo == "insertion" and n > INSERTION_MAX:
                    continue
                c, ms = measure(algo, data)
                res[dist, n, algo] = (c, ms)
                rows.append([dist, n, algo, c.comparisons, c.moves, c.calls, c.max_depth, round(ms, 3)])
    save_csv("m1_merge_sort_experiments.csv",
             ["distribution", "n", "algorithm", "comparisons", "moves", "calls", "max_depth", "time_ms"], rows)

    print("=" * 112)
    print("M1 experiment A - top-down merge sort on RANDOM event keys: counted vs theory (time = median of 3 runs)")
    print("=" * 112)
    print(f"{'n':>7} | {'comparisons':>11} {'n lg n':>9} {'worst':>9} {'ratio':>5} | "
          f"{'moves':>9} {'2n*ceil(lg n)':>13} | {'time ms':>7} | {'insertion cmp':>13} {'n(n-1)/4':>13} {'ins ms':>6}")
    print(f"{'':>7} | {'(counted)':>11} {'':>9} {'bound':>9} {'':>5} | {'(counted)':>9} {'(formula)':>13} | "
          f"{'':>7} | {'(n <= 4,096)':>13} {'(theory)':>13} {'':>6}")
    for n in SIZES:
        c, ms = res["random", n, "top_down"]
        lg = math.log2(n)
        clg = math.ceil(lg)
        worst = n * clg - 2 ** clg + 1
        ins = res.get(("random", n, "insertion"))
        ins_txt = f"{ins[0].comparisons:>13,} {n * (n - 1) // 4:>13,} {ins[1]:>6.0f}" if ins else \
            f"{'-':>13} {n * (n - 1) // 4:>13,} {'-':>6}"
        print(f"{n:>7,} | {c.comparisons:>11,} {n * lg:>9,.0f} {worst:>9,} {c.comparisons / (n * lg):>5.3f} | "
              f"{c.moves:>9,} {2 * n * clg:>13,} | {ms:>7.1f} | {ins_txt}")
    print("ratio = counted comparisons / (n lg n);  worst bound = n*ceil(lg n) - 2^ceil(lg n) + 1")

    big = SIZES[-1]
    print()
    print(f"M1 experiment B - all arrangements at n = {big:,}: comparisons and time (ms) of the three merge sorts")
    print(f"{'arrangement':<11} | {'top-down cmp':>12} {'hybrid16 cmp':>12} {'natural cmp':>12} | "
          f"{'top-down':>9} {'hybrid16':>9} {'natural':>9} | {'natural vs top-down':>19}")
    for dist in DISTS:
        cs = [res[dist, big, a][0].comparisons for a in ("top_down", "hybrid16", "natural")]
        ts = [res[dist, big, a][1] for a in ("top_down", "hybrid16", "natural")]
        print(f"{dist:<11} | {cs[0]:>12,} {cs[1]:>12,} {cs[2]:>12,} | {ts[0]:>9.1f} {ts[1]:>9.1f} {ts[2]:>9.1f} | "
              f"{cs[0] / cs[2]:>8.2f}x fewer cmp")
    print(f"(hub_feeds: natural merge sort = (n - 1) run checks + n*lg(64) = {big - 1 + big * 6:,} comparisons at most)")

    # --- cutoff tuning for the hybrid (random keys)
    n = 2 ** 16
    data = make_input("random", n)
    tune = []
    print()
    print(f"M1 experiment C - insertion-sort cutoff n0 of the hybrid merge sort (random keys, n = {n:,})")
    print(f"{'n0':>4} | {'comparisons':>11} {'moves':>10} {'calls':>7} | {'time ms (min of 5)':>18}")
    for cut in (1, 4, 8, 16, 32, 64):
        times = []
        for _ in range(5):
            c = OpCounter()
            t0 = time.perf_counter()
            merge_sort_hybrid(data, cutoff=cut, counter=c)
            times.append((time.perf_counter() - t0) * 1000)
        tune.append([cut, c.comparisons, c.moves, c.calls, round(min(times), 3)])
        print(f"{cut:>4} | {c.comparisons:>11,} {c.moves:>10,} {c.calls:>7,} | {min(times):>18.1f}")
    save_csv("m1_cutoff_tuning.csv", ["cutoff", "comparisons", "moves", "calls", "time_ms"], tune)

    # --- stability check with many equal keys
    rng = random.Random(7)
    recs = [(rng.randrange(100), i) for i in range(20000)]       # (key, arrival number)
    ref = sorted(recs, key=lambda r: r[0])
    print()
    print("M1 experiment D - stability on 20,000 records with only 100 distinct keys (equal keys keep arrival order)")
    for name, f in (("top_down", merge_sort), ("hybrid16", merge_sort_hybrid), ("natural", natural_merge_sort)):
        print(f"  {name:<9} stable = {f(recs, key=lambda r: r[0]) == ref}")

    plot(res)
    print("\nCSV : Supporting_Files/results/m1_merge_sort_experiments.csv, m1_cutoff_tuning.csv")
    print("PNG : Module_1_Merge_Sort/Report/graphs/m1_merge_vs_insertion.png, m1_improvements.png")


def plot(res):
    ns = SIZES
    ins_ns = [n for n in ns if n <= INSERTION_MAX]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    ax1.loglog(ns, [res["random", n, "top_down"][0].comparisons for n in ns], "o-", label="merge sort (random)")
    ax1.loglog(ns, [res["hub_feeds", n, "top_down"][0].comparisons for n in ns], "s-", label="merge sort (hub feeds)")
    ax1.loglog(ins_ns, [res["random", n, "insertion"][0].comparisons for n in ins_ns], "^-",
               label="insertion sort (random)")
    ax1.loglog(ns, [n * math.log2(n) for n in ns], "k--", label="theory n log2 n")
    ax1.loglog(ns, [n * (n - 1) / 4 for n in ns], "r:", label="theory n(n-1)/4")
    ax1.set(title="Key comparisons vs n", xlabel="n (records)", ylabel="comparisons")
    t_ms = [res["random", n, "top_down"][1] for n in ns]
    k = t_ms[-1] / (ns[-1] * math.log2(ns[-1]))
    ax2.loglog(ns, t_ms, "o-", label="merge sort (random)")
    ax2.loglog(ns, [k * n * math.log2(n) for n in ns], "k--", label="c * n log2 n (fitted at largest n)")
    ins_t = [res["random", n, "insertion"][1] for n in ins_ns]
    k2 = ins_t[-1] / ins_ns[-1] ** 2
    ax2.loglog(ins_ns, ins_t, "^-", label="insertion sort (random)")
    ax2.loglog(ns, [k2 * n * n for n in ns], "r:", label="c * n^2 (fitted, extrapolated)")
    ax2.set(title="Running time vs n (median of 3)", xlabel="n (records)", ylabel="time (ms)")
    for ax in (ax1, ax2):
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Module 1 - merge sort vs insertion sort baseline")
    fig.tight_layout()
    fig.savefig(GRAPHS / "m1_merge_vs_insertion.png", dpi=150)
    plt.close(fig)

    big = SIZES[-1]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    width = 0.27
    for i, (algo, lab) in enumerate((("top_down", "top-down (baseline)"), ("hybrid16", "hybrid, cutoff 16"),
                                      ("natural", "natural (run-aware)"))):
        xs = [d + (i - 1) * width for d in range(len(DISTS))]
        ax1.bar(xs, [res[d, big, algo][0].comparisons for d in DISTS], width, label=lab)
        ax2.bar(xs, [res[d, big, algo][1] for d in DISTS], width, label=lab)
    ax1.axhline(big * math.log2(big), color="k", ls="--", lw=1, label="n log2 n")
    ax1.set(title=f"Comparisons at n = {big:,}", ylabel="comparisons")
    ax2.set(title=f"Time at n = {big:,} (median of 3)", ylabel="time (ms)")
    for ax in (ax1, ax2):
        ax.set_xticks(range(len(DISTS)), DISTS)
        ax.set_xlabel("input arrangement")
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Module 1 - effect of the improvements")
    fig.tight_layout()
    fig.savefig(GRAPHS / "m1_improvements.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
