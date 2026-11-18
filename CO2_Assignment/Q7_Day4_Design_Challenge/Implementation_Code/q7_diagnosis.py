"""Q7 part A - diagnose where the brute-force closest pair (Q4) spends its effort.

On the SAME uniform drone datasets as Q4 (read from Q4's results/datasets/*.csv) this script measures
    * distance calculations performed (all n(n-1)/2 of them),
    * how many of them actually improved the best-so-far answer ("useful" work),
    * how many pairs could already be ruled out by their x-gap alone, |dx| >= final closest distance d*,
    * the cumulative share of pairs with |dx| < t for t = 1, 10, 100, 1 000, 10 000 x d*.
The |dx| counts use a sorted copy of the x coordinates and a two-pointer scan (diagnostic only).
Writes results/q7_diagnosis.csv and ../Output_Screenshots/q7_diagnosis.png.
"""

import csv
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from closest_pair_redesign import closest_pair_brute_force  # noqa: E402  (imports the Q4 original)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")
Q4_DATA = os.path.join(HERE, "..", "..", "Q4_Brute_Force_Closest_Pair", "Implementation_Code", "results", "datasets")
SIZES = [1_000, 2_000, 5_000, 10_000]
MULTIPLES = [1, 10, 100, 1_000, 10_000]


def load(layout, n):
    with open(os.path.join(Q4_DATA, f"q4_drones_{layout}_n{n}.csv")) as fh:
        return [(float(r["x_m"]), float(r["y_m"])) for r in csv.DictReader(fh)]


def pairs_with_xgap_below(xs_sorted, t):
    """Number of pairs (i < j) with |x_i - x_j| < t, by a two-pointer scan over sorted x."""
    count, lo = 0, 0
    for hi, x in enumerate(xs_sorted):
        while x - xs_sorted[lo] >= t:
            lo += 1
        count += hi - lo
    return count


def main():
    rows = []
    print("Q7-A DIAGNOSIS of the Q4 brute force on the Q4 uniform datasets (10 km x 10 km)")
    print(f"{'n':>7}{'distance calcs':>16}{'useful (improved)':>19}{'useful share':>14}{'closest d* (m)':>16}"
          f"{'pairs |dx| < d*':>17}{'ruled out by |dx|':>19}{'time (s)':>10}")
    print("-" * 118)
    for n in SIZES:
        pts = load("uniform", n)
        t0 = time.perf_counter()
        _, d, c = closest_pair_brute_force(pts)
        t = time.perf_counter() - t0
        xs = sorted(p[0] for p in pts)
        within = {k: pairs_with_xgap_below(xs, k * d) for k in MULTIPLES}
        total = c["distance_calcs"]
        rows.append({"n": n, "distance_calcs": total, "useful_improvements": c["improvements"],
                     "useful_share": c["improvements"] / total, "closest_m": round(d, 4), "time_s": round(t, 3),
                     **{f"pairs_dx_below_{k}d": within[k] for k in MULTIPLES}})
        print(f"{n:>7,}{total:>16,}{c['improvements']:>19,}{c['improvements'] / total:>14.2e}{d:>16.3f}"
              f"{within[1]:>17,}{1 - within[1] / total:>18.4%}{t:>10.2f}")
    print("\nCumulative share of ALL pairs whose x-gap is below t (t as a multiple of the final closest distance d*)")
    print(f"{'n':>7}" + "".join(f"{f'< {k:,} d*':>14}" for k in MULTIPLES))
    for r in rows:
        print(f"{r['n']:>7,}" + "".join(f"{r[f'pairs_dx_below_{k}d'] / r['distance_calcs']:>14.5%}" for k in MULTIPLES))
    big = rows[-1]
    print(f"\nAt n = {big['n']:,}: {big['distance_calcs']:,} distance calculations, only {big['useful_improvements']} improved"
          f" the answer; {1 - big['pairs_dx_below_1d'] / big['distance_calcs']:.4%} of the pairs are ruled out by")
    print(f"their x-gap alone (|dx| >= d* = {big['closest_m']} m) - the brute force still computes their full distance.")

    with open(os.path.join(RESULTS, "q7_diagnosis.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("CSV  : results/q7_diagnosis.csv")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    width = 0.27
    series = [("all distance calculations", "distance_calcs", "#4C72B0"),
              ("pairs with |dx| < d* (could matter)", "pairs_dx_below_1d", "#DD8452"),
              ("calculations that improved the answer", "useful_improvements", "#55A868")]
    for k, (lab, key, col) in enumerate(series):
        axes[0].bar([i + (k - 1) * width for i in range(len(rows))], [max(r[key], 0.8) for r in rows], width,
                    label=lab, color=col)
    axes[0].set_xticks(range(len(rows)))
    axes[0].set_xticklabels([f"n = {r['n']:,}" for r in rows])
    axes[0].set_yscale("log")
    axes[0].set_ylabel("count (log)")
    axes[0].set_title("Brute force: almost all work cannot change the answer")
    axes[0].grid(True, axis="y", which="both", alpha=0.3)
    axes[0].legend(fontsize=8)
    for r in rows:
        axes[1].plot(MULTIPLES, [r[f"pairs_dx_below_{k}d"] / r["distance_calcs"] for k in MULTIPLES], "o-",
                     label=f"n = {r['n']:,}")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("x-gap threshold t / d* (log)")
    axes[1].set_ylabel("share of all pairs with |dx| < t (log)")
    axes[1].set_title("Only a tiny share of pairs are close even in x")
    axes[1].grid(True, which="both", alpha=0.3)
    axes[1].legend(fontsize=8)
    fig.suptitle("Q7-A Diagnosis of the Q4 brute-force closest pair")
    fig.tight_layout()
    fig.savefig(os.path.join(SHOTS, "q7_diagnosis.png"), dpi=150)
    plt.close(fig)
    print("Graph: ../Output_Screenshots/q7_diagnosis.png")


if __name__ == "__main__":
    main()
