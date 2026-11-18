"""Q7 part E - validate the redesign against the original on the SAME test conditions.

1. Identical datasets: the Q4 uniform fleets (n = 100 .. 10 000) and the Q4 clustered fleet, read from Q4's CSVs,
   plus two adversarial layouts created here (corridor, cross) - original and redesign run on the same lists.
2. Ablation: corridor fleet swept along a forced x-axis (no axis selection).
3. Scaling of the redesign alone (n = 20 000 .. 200 000); the original is EXTRAPOLATED with Q4's fitted constant.
4. Objective check: largest fleet within the 100 ms response limit, confirmed by direct runs.
Writes results/q7_validation.csv, results/q7_scaling.csv and two graphs in ../Output_Screenshots/.
"""

import csv
import math
import os
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from closest_pair_redesign import closest_pair_brute_force, closest_pair_sweep, make_drones  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")
Q4_RES = os.path.join(HERE, "..", "..", "Q4_Brute_Force_Closest_Pair", "Implementation_Code", "results")
T_ACCEPT = 0.100


def load_q4(layout, n):
    with open(os.path.join(Q4_RES, "datasets", f"q4_drones_{layout}_n{n}.csv")) as fh:
        return [(float(r["x_m"]), float(r["y_m"])) for r in csv.DictReader(fh)]


def save(points, name):
    os.makedirs(os.path.join(RESULTS, "datasets"), exist_ok=True)
    with open(os.path.join(RESULTS, "datasets", name), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["drone_id", "x_m", "y_m"])
        w.writerows((f"D{k + 1}", repr(x), repr(y)) for k, (x, y) in enumerate(points))


def timed(fn, pts, repeats, **kw):
    ts = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        out = fn(pts, **kw)
        ts.append(time.perf_counter() - t0)
    return out, statistics.median(ts)


def main():
    with open(os.path.join(Q4_RES, "q4_fit.csv")) as fh:
        c_bf = float(next(csv.DictReader(fh))["c_ns_per_pair"]) * 1e-9
    tests = [("uniform", n, load_q4("uniform", n)) for n in (100, 500, 1_000, 2_000, 5_000, 10_000)]
    tests.append(("clustered", 2_000, load_q4("clustered", 2_000)))
    for layout, n in (("corridor", 2_000), ("cross", 2_000), ("cross", 5_000)):
        pts = make_drones(n, layout, seed=72)
        save(pts, f"q7_drones_{layout}_n{n}.csv")
        tests.append((layout, n, pts))
    rows = []
    print("Q7-E ORIGINAL (Q4 brute force) vs REDESIGN (sort + sweep) on identical datasets   (time = median)")
    print(f"{'dataset':<10}{'n':>7}{'BF dist calcs':>15}{'RD sort cmp':>13}{'RD examined':>13}{'RD dist':>9}"
          f"{'calcs x':>12}{'BF time s':>11}{'RD time s':>11}{'speed-up':>10}  same d")
    print("-" * 117)
    for layout, n, pts in tests:
        reps = 3 if n <= 2_000 else 1
        (_, d0, c0), t0 = timed(closest_pair_brute_force, pts, reps)
        (_, d1, c1), t1 = timed(closest_pair_sweep, pts, 5 if n <= 2_000 else 3)
        same = d0 == d1
        red = c0["distance_calcs"] / max(c1["distance_calcs"], 1)
        rows.append({"dataset": layout, "n": n, "axis": c1["axis"], "bf_distance_calcs": c0["distance_calcs"],
                     "rd_sort_comparisons": c1["sort_comparisons"], "rd_candidates_examined": c1["candidates"],
                     "rd_distance_calcs": c1["distance_calcs"], "rd_pairs_never_examined": c1["pairs_never_examined"],
                     "calc_reduction": round(red, 1),
                     "key_op_reduction": round(c0["distance_calcs"] / (c1["sort_comparisons"] + c1["candidates"]), 1),
                     "bf_time_s": round(t0, 5), "rd_time_s": round(t1, 5), "speedup": round(t0 / t1, 1),
                     "closest_m": round(d0, 4), "same_distance": same})
        print(f"{layout:<10}{n:>7,}{c0['distance_calcs']:>15,}{c1['sort_comparisons']:>13,}{c1['candidates']:>13,}"
              f"{c1['distance_calcs']:>9,}{red:>11,.0f}x{t0:>11.4f}{t1:>11.4f}{t0 / t1:>9.1f}x  {'yes' if same else 'NO'}")
    corridor = next(p for lay, _, p in tests if lay == "corridor")
    (_, dx_, cx_), tx_ = timed(closest_pair_sweep, corridor, 3, axis="x")
    auto = next(r for r in rows if r["dataset"] == "corridor")
    print(f"\nAblation - corridor fleet swept along a FORCED x-axis: examined {cx_['candidates']:,} pairs,"
          f" {cx_['distance_calcs']:,} distance calcs, {tx_:.4f} s")
    print(f"           with automatic axis choice ({auto['axis']}): examined {auto['rd_candidates_examined']:,} pairs,"
          f" {auto['rd_distance_calcs']:,} distance calcs, {auto['rd_time_s']:.4f} s")
    rows.append({"dataset": "corridor (forced x)", "n": 2_000, "axis": "x", "bf_distance_calcs": auto["bf_distance_calcs"],
                 "rd_sort_comparisons": cx_["sort_comparisons"], "rd_candidates_examined": cx_["candidates"],
                 "rd_distance_calcs": cx_["distance_calcs"], "rd_pairs_never_examined": cx_["pairs_never_examined"],
                 "calc_reduction": round(auto["bf_distance_calcs"] / max(cx_["distance_calcs"], 1), 1),
                 "key_op_reduction": round(auto["bf_distance_calcs"] / (cx_["sort_comparisons"] + cx_["candidates"]), 1),
                 "bf_time_s": auto["bf_time_s"], "rd_time_s": round(tx_, 5),
                 "speedup": round(auto["bf_time_s"] / tx_, 1), "closest_m": round(dx_, 4),
                 "same_distance": dx_ == auto["closest_m"] or abs(dx_ - auto["closest_m"]) < 1e-4})

    print(f"\nSCALING of the redesign (uniform fleets); original EXTRAPOLATED as c * n(n-1)/2 with c = {c_bf * 1e9:.1f} ns"
          " (Q4 fit)")
    print(f"{'n':>9}{'sort cmp':>12}{'examined':>11}{'dist calcs':>12}{'examined/n':>12}{'RD time s':>11}"
          f"{'BF time s (extrap.)':>21}{'speed-up':>10}")
    scale = []
    for n in (1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000, 200_000):
        pts = make_drones(n, "uniform", seed=7000 + n)
        (_, d1, c1), t1 = timed(closest_pair_sweep, pts, 3 if n <= 20_000 else 1)
        bf = c_bf * n * (n - 1) / 2
        scale.append({"n": n, "sort_comparisons": c1["sort_comparisons"], "candidates": c1["candidates"],
                      "distance_calcs": c1["distance_calcs"], "candidates_per_drone": round(c1["candidates"] / n, 3),
                      "rd_time_s": round(t1, 5), "bf_time_extrapolated_s": round(bf, 3), "speedup": round(bf / t1, 1)})
        print(f"{n:>9,}{c1['sort_comparisons']:>12,}{c1['candidates']:>11,}{c1['distance_calcs']:>12,}"
              f"{c1['candidates'] / n:>12.2f}{t1:>11.4f}{bf:>21,.2f}{bf / t1:>9,.0f}x")
    k = sum(r["rd_time_s"] * r["n"] * math.log2(r["n"]) for r in scale) / sum((r["n"] * math.log2(r["n"])) ** 2 for r in scale)
    n_fit = max(n for n in range(2, 2_000_000, 50) if k * n * math.log2(n) <= T_ACCEPT)
    n_bf = int((1 + math.sqrt(1 + 8 * T_ACCEPT / c_bf)) / 2)
    print(f"\nOBJECTIVE CHECK (100 ms response): brute force n_max = {n_bf:,} (Q4);  redesign fit T = k n log2 n, "
          f"k = {k * 1e9:.0f} ns -> n_max ~ {n_fit:,}")
    n_rd = n_fit
    for _ in range(6):                         # confirm by direct runs; step down 5 % while over the limit (noise)
        (_, _, cchk), tchk = timed(closest_pair_sweep, make_drones(n_rd, "uniform", seed=99), 3)
        print(f"  direct run at n = {n_rd:,}: {tchk:.3f} s ({'within' if tchk <= T_ACCEPT else 'over'} 100 ms)")
        scale.append({"n": n_rd, "sort_comparisons": cchk["sort_comparisons"], "candidates": cchk["candidates"],
                      "distance_calcs": cchk["distance_calcs"],
                      "candidates_per_drone": round(cchk["candidates"] / n_rd, 3), "rd_time_s": round(tchk, 5),
                      "bf_time_extrapolated_s": round(c_bf * n_rd * (n_rd - 1) / 2, 3),
                      "speedup": round(c_bf * n_rd * (n_rd - 1) / 2 / tchk, 1)})
        if tchk <= T_ACCEPT:
            break
        n_rd = int(n_rd * 0.95)
    print(f"  confirmed: {n_rd:,} drones within 100 ms = {n_rd / n_bf:.1f}x the brute-force limit of {n_bf:,}")
    print(f"All redesign answers identical to the original: {'YES' if all(r['same_distance'] for r in rows) else 'NO'}")

    for name, data in (("q7_validation.csv", rows), ("q7_scaling.csv", scale)):
        with open(os.path.join(RESULTS, name), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)
    print("CSV  : results/q7_validation.csv, results/q7_scaling.csv   datasets: results/datasets/q7_drones_*.csv")

    uni = [r for r in rows if r["dataset"] == "uniform"]
    sc = scale[:8]                                   # the eight scaling sizes (boundary-check rows follow)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ns = [r["n"] for r in uni]
    axes[0].plot(ns, [r["bf_distance_calcs"] for r in uni], "o-", color="#C44E52", label="original: distance calcs")
    axes[0].plot([r["n"] for r in sc], [r["sort_comparisons"] for r in sc], "s--", color="#8172B2",
                 label="redesign: sort comparisons")
    axes[0].plot([r["n"] for r in sc], [r["candidates"] for r in sc], "^-", color="#DD8452",
                 label="redesign: pairs examined")
    axes[0].plot([r["n"] for r in sc], [r["distance_calcs"] for r in sc], "o-", color="#55A868",
                 label="redesign: distance calcs")
    xs = [r["n"] for r in sc]
    axes[0].plot(xs, [n * (n - 1) / 2 for n in xs], "k:", lw=1, label="n(n-1)/2")
    axes[0].plot(xs, [n * math.log2(n) for n in xs], "k-.", lw=1, label="n log2 n")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("number of drones n (log)")
    axes[0].set_ylabel("operations (log)")
    axes[0].set_title("Key operations: original vs redesign (uniform fleets)")
    axes[0].grid(True, which="both", alpha=0.3)
    axes[0].legend(fontsize=7)
    axes[1].plot(ns, [r["bf_time_s"] for r in uni], "o-", color="#C44E52", label="original: measured")
    axes[1].plot(xs, [r["bf_time_extrapolated_s"] for r in sc], ":", color="#C44E52", label="original: extrapolated")
    axes[1].plot(xs, [r["rd_time_s"] for r in sc], "o-", color="#55A868", label="redesign: measured")
    axes[1].axhline(T_ACCEPT, color="grey", ls="--", label="acceptable response 100 ms")
    axes[1].axvline(n_bf, color="#C44E52", lw=0.8)
    axes[1].axvline(n_rd, color="#55A868", lw=0.8)
    axes[1].text(n_bf * 1.08, 3e-4, f"{n_bf:,}", color="#C44E52", fontsize=8)
    axes[1].text(n_rd * 1.08, 3e-4, f"{n_rd:,}", color="#55A868", fontsize=8)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("number of drones n (log)")
    axes[1].set_ylabel("time per monitoring cycle (s, log)")
    axes[1].set_title("Time and the 100 ms response limit")
    axes[1].grid(True, which="both", alpha=0.3)
    axes[1].legend(fontsize=7, loc="upper left")
    fig.suptitle("Q7-E Original brute force vs redesigned sweep (same datasets, same answers)")
    fig.tight_layout()
    fig.savefig(os.path.join(SHOTS, "q7_original_vs_redesign.png"), dpi=150)
    plt.close(fig)

    lay = [r for r in rows if r["n"] == 2_000]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    width = 0.27
    for k2, (lab, key, col) in enumerate((("original: distance calcs", "bf_distance_calcs", "#C44E52"),
                                          ("redesign: pairs examined", "rd_candidates_examined", "#DD8452"),
                                          ("redesign: distance calcs", "rd_distance_calcs", "#55A868"))):
        ax.bar([i + (k2 - 1) * width for i in range(len(lay))], [r[key] for r in lay], width, label=lab, color=col)
    ax.set_xticks(range(len(lay)))
    ax.set_xticklabels([r["dataset"] for r in lay])
    ax.set_yscale("log")
    ax.set_ylabel("count (log)")
    ax.set_ylim(top=3e8)                                # room for the legend above the bars
    ax.set_title("Q7-E Same n = 2,000 drones, different layouts: where the redesign helps and where it does not")
    ax.grid(True, axis="y", which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(SHOTS, "q7_layouts_n2000.png"), dpi=150)
    plt.close(fig)
    print("Graph: ../Output_Screenshots/q7_original_vs_redesign.png, q7_layouts_n2000.png")


if __name__ == "__main__":
    main()
