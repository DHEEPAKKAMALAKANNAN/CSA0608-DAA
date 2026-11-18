"""Q1 design decision - the fulfilment-centre scenario (about 95 % of orders already in priority order).

Two interpretations of "95 % already in the correct order" are tested with n = 5 000 orders:

  (a) BATCH APPENDED  - the existing orders are sorted and a batch of k new orders (random priorities) is
                        appended at the end; k = 1, 5, 25, 50, 100, 250 (= 5 %), 500 (= 10 %).
  (b) LOCAL DISORDER  - 95 % / 90 % / 99 % of orders sit in their correct place; the rest have been displaced by
                        at most 10 positions (e.g. late scanning of an order).

The three instrumented algorithms run on identical copies; results go to results/q1_scenario_95.csv and the
graph ../Output_Screenshots/q1_scenario_95.png.
"""

import csv
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from sorting_algorithms import ALGORITHMS, predicted_counts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")
N = 5000
BATCHES = [1, 5, 25, 50, 100, 250, 500]
LOCAL_FRACTIONS = [0.01, 0.05, 0.10]


def batch_appended(k, seed=7):
    """n-k sorted existing orders followed by k new orders with random priority scores."""
    rng = random.Random(seed * 1000 + k)
    base = sorted(rng.sample(range(1, 10 * N + 1), N))
    new_idx = set(rng.sample(range(N), k))
    existing = [s for i, s in enumerate(base) if i not in new_idx]
    batch = [s for i, s in enumerate(base) if i in new_idx]
    rng.shuffle(batch)
    return [(s, i) for i, s in enumerate(existing + batch)]


def local_disorder(fraction, max_shift=10, seed=11):
    """Sorted list in which `fraction` of the orders are moved by at most `max_shift` places."""
    rng = random.Random(seed + int(fraction * 1000))
    scores = sorted(rng.sample(range(1, 10 * N + 1), N))
    for i in rng.sample(range(N), round(fraction * N)):
        j = min(N - 1, max(0, i + rng.randint(-max_shift, max_shift)))
        scores.insert(j, scores.pop(i))
    return [(s, i) for i, s in enumerate(scores)]


def measure(label, records, rows, extra):
    pred = predicted_counts([r[0] for r in records])
    cells = []
    for alg, fn in ALGORITHMS.items():
        t0 = time.perf_counter()
        out, cnt = fn(records)
        ms = (time.perf_counter() - t0) * 1000
        ok = all(a[0] <= b[0] for a, b in zip(out, out[1:])) and cnt["comparisons"] == pred[alg]["comparisons"]
        rows.append({"scenario": label, **extra, "algorithm": alg, "comparisons": cnt["comparisons"],
                     "swaps_or_shifts": cnt["moves"], "writes": cnt["writes"], "passes": cnt["passes"],
                     "time_ms": round(ms, 2), "inversions": pred["inversions"], "verified": ok})
        cells.append((cnt["comparisons"], cnt["moves"], ms, ok))
    return pred["inversions"], cells


def main():
    rows = []
    print(f"Q1 DESIGN DECISION - n = {N:,} orders; selection sort always needs n(n-1)/2 = {N * (N - 1) // 2:,}"
          " comparisons")
    head = (f"{'condition':<22}{'inversions':>11} | {'Selection comp':>15} | {'Bubble comp':>12}{'passes*':>8}"
            f"{'swaps':>11} | {'Insertion comp':>15}{'shifts':>11} | ok")
    print("\n(a) Sorted existing orders + batch of k NEW orders appended at the end")
    print(head)
    print("-" * len(head))
    for k in BATCHES:
        recs = batch_appended(k)
        inv, c = measure("batch_appended", recs, rows, {"k_new": k, "fraction_displaced": ""})
        passes = next(r["passes"] for r in rows if r["scenario"] == "batch_appended" and r["k_new"] == k
                      and r["algorithm"] == "Bubble")
        print(f"{f'k = {k} ({100 * k / N:.2f} %)':<22}{inv:>11,} | {c[0][0]:>15,} | {c[1][0]:>12,}{passes:>8,}"
              f"{c[1][1]:>11,} | {c[2][0]:>15,}{c[2][1]:>11,} | {'yes' if all(x[3] for x in c) else 'NO'}")
    print("\n(b) Local disorder: a fraction of orders displaced by at most 10 positions")
    print(head)
    print("-" * len(head))
    for f in LOCAL_FRACTIONS:
        recs = local_disorder(f)
        inv, c = measure("local_disorder", recs, rows, {"k_new": "", "fraction_displaced": f})
        passes = next(r["passes"] for r in rows if r["scenario"] == "local_disorder"
                      and r["fraction_displaced"] == f and r["algorithm"] == "Bubble")
        print(f"{f'{100 * f:.0f} % moved <=10':<22}{inv:>11,} | {c[0][0]:>15,} | {c[1][0]:>12,}{passes:>8,}"
              f"{c[1][1]:>11,} | {c[2][0]:>15,}{c[2][1]:>11,} | {'yes' if all(x[3] for x in c) else 'NO'}")
    print("* passes = Bubble Sort passes actually executed (early-exit flag); ok = sorted and counts = prediction")

    t = {(r["scenario"], r["k_new"], r["fraction_displaced"], r["algorithm"]): r["time_ms"] for r in rows}
    print("\nExecution time for the 5 % batch case (k = 250):  "
          + "   ".join(f"{a} {t[('batch_appended', 250, '', a)]:,.0f} ms" for a in ALGORITHMS))

    path = os.path.join(RESULTS, "q1_scenario_95.csv")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("CSV  :", os.path.relpath(path, HERE))

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    colors = {"Selection": "#4C72B0", "Bubble": "#DD8452", "Insertion": "#55A868"}
    for alg in ALGORITHMS:
        ys = [next(r["comparisons"] for r in rows if r["scenario"] == "batch_appended" and r["k_new"] == k
                   and r["algorithm"] == alg) for k in BATCHES]
        axes[0].plot(BATCHES, ys, marker="o", label=alg, color=colors[alg])
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("new orders k appended to 5 000 - k sorted orders (log)")
    axes[0].set_ylabel("key comparisons (log)")
    axes[0].set_title("(a) Batch of new orders appended")
    axes[0].axvline(250, color="grey", ls=":", lw=1)
    axes[0].text(260, 2e4, "5 % batch", fontsize=8, color="grey")
    axes[0].grid(True, which="both", alpha=0.3)
    axes[0].legend()
    width = 0.27
    for a_i, alg in enumerate(ALGORITHMS):
        ys = [next(r["comparisons"] for r in rows if r["scenario"] == "local_disorder"
                   and r["fraction_displaced"] == f and r["algorithm"] == alg) for f in LOCAL_FRACTIONS]
        axes[1].bar([i + (a_i - 1) * width for i in range(len(LOCAL_FRACTIONS))], ys, width, label=alg,
                    color=colors[alg])
    axes[1].set_yscale("log")
    axes[1].set_xticks(range(len(LOCAL_FRACTIONS)))
    axes[1].set_xticklabels([f"{100 * f:.0f} % moved <=10" for f in LOCAL_FRACTIONS])
    axes[1].set_ylabel("key comparisons (log)")
    axes[1].set_title("(b) Local disorder (displacement <= 10)")
    axes[1].grid(True, axis="y", alpha=0.3)
    axes[1].legend()
    fig.suptitle("Q1 design decision - n = 5 000 orders, about 95 % already in priority order")
    fig.tight_layout()
    gpath = os.path.join(SHOTS, "q1_scenario_95.png")
    fig.savefig(gpath, dpi=150)
    plt.close(fig)
    print("Graph:", os.path.relpath(gpath, HERE))


if __name__ == "__main__":
    main()
