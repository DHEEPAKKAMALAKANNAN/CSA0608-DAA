"""Q1 experiments - Selection vs Bubble vs Insertion Sort under six designed input conditions.

For n = 100, 1 000 and 5 000 this script
    1. builds the six datasets (seeded, reproducible) and saves them to results/datasets/*.csv,
    2. runs the three instrumented algorithms on identical copies of each dataset,
    3. checks every result against Python's sorted() and every counter against the exact prediction
       derived from the input's inversion profile (Pred=Obs column),
    4. writes results/q1_results.csv and the graphs in ../Output_Screenshots/.

Counts are the primary evidence; time (median of repeats, perf_counter) is secondary.
"""

import csv
import os
import random
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from sorting_algorithms import ALGORITHMS, predicted_counts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
DATASETS = os.path.join(RESULTS, "datasets")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")
SIZES = [100, 1000, 5000]
ORDER = ["D1_Reverse", "D2_Nearly95_Batch5", "D3_UrgentLast", "R_Random", "S_Sorted", "E2_FewUnique"]
LABEL = {"D1_Reverse": "D1 Reverse", "D2_Nearly95_Batch5": "D2 95%+5% batch", "D3_UrgentLast": "D3 Urgent last",
         "R_Random": "R Random", "S_Sorted": "S Sorted", "E2_FewUnique": "E2 Few unique"}


def make_datasets(n, seed=42):
    """Return {name: [(score, order_id), ...]} for the six input conditions of size n."""
    rng = random.Random(seed + n)
    base = sorted(rng.sample(range(1, 10 * n + 1), n))           # n distinct priority scores
    shuffled = base[:]
    rng.shuffle(shuffled)
    k = max(1, round(0.05 * n))                                   # 5 % new orders
    new_idx = set(rng.sample(range(n), k))
    existing = [s for i, s in enumerate(base) if i not in new_idx]  # still in priority order
    new_batch = [s for i, s in enumerate(base) if i in new_idx]
    rng.shuffle(new_batch)                                        # new orders arrive in random order
    scores = {
        "D1_Reverse": base[::-1],
        "D2_Nearly95_Batch5": existing + new_batch,
        "D3_UrgentLast": base[1:] + base[:1],                     # highest-priority order arrives last
        "R_Random": shuffled,
        "S_Sorted": base,
        "E2_FewUnique": [rng.randint(1, 5) for _ in range(n)],    # many ties
    }
    return {name: [(s, i) for i, s in enumerate(sc)] for name, sc in scores.items()}


def save_dataset(name, n, records):
    os.makedirs(DATASETS, exist_ok=True)
    with open(os.path.join(DATASETS, f"q1_{name}_n{n}.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["order_id", "priority_score"])
        w.writerows((oid, s) for s, oid in records)


def timed_run(fn, records, repeats):
    """Run fn `repeats` times; return (sorted_list, counters, median_time_ms)."""
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        out, cnt = fn(records)
        times.append((time.perf_counter() - t0) * 1000)
    return out, cnt, statistics.median(times)


def run_experiments():
    rows = []
    for n in SIZES:
        data = make_datasets(n)
        repeats = 3 if n <= 1000 else 1
        print(f"\nn = {n:,}   (n(n-1)/2 = {n * (n - 1) // 2:,};  time = median of {repeats} run(s))")
        print(f"{'Dataset':<17}{'Algorithm':<10}{'Comparisons':>13}{'Swaps/Shifts':>14}{'Writes':>12}"
              f"{'Passes':>8}{'Time ms':>10}{'Inversions':>12}  Pred=Obs")
        print("-" * 106)
        for name in ORDER:
            recs = data[name]
            save_dataset(name, n, recs)
            pred = predicted_counts([r[0] for r in recs])
            expected = sorted(recs, key=lambda r: r[0])
            for alg, fn in ALGORITHMS.items():
                out, cnt, ms = timed_run(fn, recs, repeats)
                ok = ([r[0] for r in out] == [r[0] for r in expected]
                      and all(cnt[k] == v for k, v in pred[alg].items()))
                rows.append({"n": n, "dataset": name, "algorithm": alg, "comparisons": cnt["comparisons"],
                             "swaps_or_shifts": cnt["moves"], "writes": cnt["writes"], "passes": cnt["passes"],
                             "time_ms": round(ms, 3), "inversions": pred["inversions"],
                             "predicted_comparisons": pred[alg]["comparisons"], "pred_equals_obs": ok})
                print(f"{LABEL[name] if alg == 'Selection' else '':<17}{alg:<10}{cnt['comparisons']:>13,}"
                      f"{cnt['moves']:>14,}{cnt['writes']:>12,}{cnt['passes']:>8,}{ms:>10.2f}"
                      f"{pred['inversions'] if alg == 'Selection' else '':>12}  {'yes' if ok else 'NO'}")
    return rows


def write_csv(rows):
    path = os.path.join(RESULTS, "q1_results.csv")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


def plot_counts_n5000(rows):
    """Grouped bars: comparisons and array writes for every dataset at n = 5 000 (log scale)."""
    n = SIZES[-1]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    colors = {"Selection": "#4C72B0", "Bubble": "#DD8452", "Insertion": "#55A868"}
    width = 0.27
    for ax, metric, title in ((axes[0], "comparisons", "Key comparisons"),
                              (axes[1], "writes", "Array writes (data movement)")):
        for a_i, alg in enumerate(ALGORITHMS):
            vals = [next(r[metric] for r in rows if r["n"] == n and r["dataset"] == d and r["algorithm"] == alg)
                    for d in ORDER]
            xs = [i + (a_i - 1) * width for i in range(len(ORDER))]
            ax.bar(xs, [max(v, 0.8) for v in vals], width, label=alg, color=colors[alg])
            for x, v in zip(xs, vals):
                if v == 0:
                    ax.text(x, 1.0, "0", ha="center", va="bottom", fontsize=8)
        ax.set_yscale("log")
        ax.set_xticks(range(len(ORDER)))
        ax.set_xticklabels([LABEL[d] for d in ORDER], rotation=20, ha="right")
        ax.set_ylabel(f"{title} (count, log scale)")
        ax.set_title(f"{title} at n = {n:,}")
        ax.axhline(n * (n - 1) / 2, color="grey", ls="--", lw=1, label="n(n-1)/2")
        ax.grid(True, which="major", axis="y", alpha=0.4)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 0.94), fontsize=9)
    fig.suptitle("Q1 - Same algorithms, same n, very different work depending on input order")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    path = os.path.join(SHOTS, "q1_counts_by_dataset_n5000.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_growth(rows):
    """Comparisons vs n (log-log) per algorithm, one line per dataset, with n and n^2/2 references."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    for ax, alg in zip(axes, ALGORITHMS):
        for d in ORDER:
            ys = [next(r["comparisons"] for r in rows if r["n"] == n and r["dataset"] == d and r["algorithm"] == alg)
                  for n in SIZES]
            ax.plot(SIZES, ys, marker="o", label=LABEL[d])
        ax.plot(SIZES, [n * (n - 1) / 2 for n in SIZES], "k--", lw=1, label="theory n(n-1)/2")
        ax.plot(SIZES, [n - 1 for n in SIZES], "k:", lw=1, label="theory n-1")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(f"{alg} Sort")
        ax.set_xlabel("number of orders n (log)")
        ax.grid(True, which="both", alpha=0.3)
    axes[0].set_ylabel("key comparisons (log)")
    axes[2].legend(fontsize=7, loc="upper left")
    fig.suptitle("Q1 - Growth of comparisons with n for each input condition")
    fig.tight_layout()
    path = os.path.join(SHOTS, "q1_comparisons_growth.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main():
    rows = run_experiments()
    print("\nAll results sorted correctly and every counter equals its exact prediction:",
          "YES" if all(r["pred_equals_obs"] for r in rows) else "NO")
    print("CSV  :", os.path.relpath(write_csv(rows), HERE))
    print("Graph:", os.path.relpath(plot_counts_n5000(rows), HERE))
    print("Graph:", os.path.relpath(plot_growth(rows), HERE))


if __name__ == "__main__":
    main()
