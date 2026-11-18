"""Q4 experiments - growth of the brute-force closest pair and the scalability boundary.

* Uniform drone fleets n = 100, 500, 1 000, 2 000, 5 000, 10 000 (seeded; saved to results/datasets/) and a
  clustered fleet (5 delivery hubs) of n = 2 000 to show that the count does not depend on the layout.
* Records pairs examined, distance calculations, best-so-far updates and time (median of repeats).
* Fits T(n) = c * n(n-1)/2, then applies the acceptability criterion defined BEFORE measuring:
  acceptable response <= 100 ms per 1 Hz monitoring cycle (hard limit 1 s).
Writes results/q4_growth.csv, results/q4_fit.csv and ../Output_Screenshots/q4_growth.png.
"""

import csv
import math
import os
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from closest_pair_bruteforce import closest_pair_brute_force, make_drones  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
DATASETS = os.path.join(RESULTS, "datasets")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")
SIZES = [100, 500, 1_000, 2_000, 5_000, 10_000]
REPEATS = {100: 5, 500: 5, 1_000: 5, 2_000: 3, 5_000: 1, 10_000: 1}
T_ACCEPT, T_HARD = 0.100, 1.0          # seconds


def save_drones(points, name):
    os.makedirs(DATASETS, exist_ok=True)
    with open(os.path.join(DATASETS, name), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["drone_id", "x_m", "y_m"])
        w.writerows((f"D{k + 1}", repr(x), repr(y)) for k, (x, y) in enumerate(points))


def measure(points, repeats):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        pair, dist, cnt = closest_pair_brute_force(points)
        times.append(time.perf_counter() - t0)
    return pair, dist, cnt, statistics.median(times)


def n_max_for(budget_s, c):
    """Largest n with c * n(n-1)/2 <= budget (solve the quadratic)."""
    return int((1 + math.sqrt(1 + 8 * budget_s / c)) / 2)


def main():
    rows = []
    print("Q4 BRUTE-FORCE CLOSEST PAIR - growth experiment (uniform drones in 10 km x 10 km; time = median)")
    print(f"{'layout':<10}{'n':>7}{'pairs examined':>15}{'n(n-1)/2':>13}{'distance calcs':>15}{'updates':>8}"
          f"{'closest (m)':>12}{'time (s)':>10}{'ns/pair':>9}{'x pairs':>8}{'x time':>8}")
    print("-" * 115)
    prev = None
    for layout, n in [("uniform", n) for n in SIZES] + [("clustered", 2_000)]:
        pts = make_drones(n, layout)
        save_drones(pts, f"q4_drones_{layout}_n{n}.csv")
        pair, dist, cnt, t = measure(pts, REPEATS[n])
        theory = n * (n - 1) // 2
        ratios = ""
        if prev and layout == "uniform":                 # growth from the previous (smaller) size
            ratios = f"{theory / prev[0]:>8.1f}{t / prev[1]:>8.1f}"
        prev = (theory, t) if layout == "uniform" else prev
        rows.append({"layout": layout, "n": n, "pairs_examined": cnt["pairs_examined"], "theory_n(n-1)/2": theory,
                     "distance_calcs": cnt["distance_calcs"], "improvements": cnt["improvements"],
                     "closest_m": round(dist, 3), "pair": f"D{pair[0] + 1}-D{pair[1] + 1}", "time_s": round(t, 5),
                     "ns_per_pair": round(t / theory * 1e9, 1), "repeats": REPEATS[n]})
        print(f"{layout:<10}{n:>7,}{cnt['pairs_examined']:>15,}{theory:>13,}{cnt['distance_calcs']:>15,}"
              f"{cnt['improvements']:>8}{dist:>12.2f}{t:>10.4f}{t / theory * 1e9:>9.1f}{ratios}")
    exact = all(r["pairs_examined"] == r["distance_calcs"] == r["theory_n(n-1)/2"] for r in rows)
    print(f"pairs examined = distance calcs = n(n-1)/2 for every run (incl. clustered layout): {'YES' if exact else 'NO'}")

    fit_rows = [r for r in rows if r["layout"] == "uniform" and r["n"] >= 1_000]
    c = sum(r["time_s"] * r["theory_n(n-1)/2"] for r in fit_rows) / sum(r["theory_n(n-1)/2"] ** 2 for r in fit_rows)
    print(f"\nLeast-squares fit T(n) = c * n(n-1)/2 over n >= 1,000:  c = {c * 1e9:.1f} ns per pair")
    print(f"{'n':>9}{'n(n-1)/2':>17}{'predicted T':>14}{'measured T':>13}  status vs 100 ms / 1 s")
    fits = []
    for n in SIZES + [20_000, 50_000, 100_000]:
        p = n * (n - 1) // 2
        pred = c * p
        meas = next((r["time_s"] for r in rows if r["layout"] == "uniform" and r["n"] == n), None)
        status = "acceptable" if pred <= T_ACCEPT else ("too slow (>100 ms)" if pred <= T_HARD else "impractical (>1 s)")
        fits.append({"n": n, "pairs": p, "predicted_s": round(pred, 4), "measured_s": meas if meas else "",
                     "status": status, "c_ns_per_pair": round(c * 1e9, 2)})
        print(f"{n:>9,}{p:>17,}{pred:>13.3f}s{(f'{meas:.3f}s' if meas else '(extrapolated)'):>14}  {status}")
    n_acc, n_hard = n_max_for(T_ACCEPT, c), n_max_for(T_HARD, c)
    print(f"\nAcceptability boundary: n_max(100 ms) = {n_acc:,} drones;  n_max(1 s hard limit) = {n_hard:,} drones")
    for n_chk, budget in ((n_acc, T_ACCEPT), (n_hard, T_HARD)):     # validate the boundary by direct runs
        for _ in range(6):                     # step down 5 % while the measured time is over the budget (noise)
            _, _, cnt, t = measure(make_drones(n_chk, "uniform"), 3)
            rows.append({"layout": "uniform (boundary check)", "n": n_chk, "pairs_examined": cnt["pairs_examined"],
                         "theory_n(n-1)/2": n_chk * (n_chk - 1) // 2, "distance_calcs": cnt["distance_calcs"],
                         "improvements": cnt["improvements"], "closest_m": "", "pair": "", "time_s": round(t, 5),
                         "ns_per_pair": round(t / cnt["pairs_examined"] * 1e9, 1), "repeats": 3})
            print(f"  direct check: n = {n_chk:,} -> {cnt['pairs_examined']:,} pairs, measured {t:.3f} s"
                  f" (budget {budget:.1f} s): {'within' if t <= budget else 'over'}")
            if t <= budget:
                break
            n_chk = int(n_chk * 0.95)
    print(f"Doubling the fleet from {n_acc:,} to {2 * n_acc:,} would need about {c * (2 * n_acc) ** 2 / 2:.2f} s (x4).")

    for name, data in (("q4_growth.csv", rows), ("q4_fit.csv", fits)):
        with open(os.path.join(RESULTS, name), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)
    print("CSV  : results/q4_growth.csv, results/q4_fit.csv   datasets: results/datasets/q4_drones_*.csv")

    uni = [r for r in rows if r["layout"] == "uniform"]
    ns = [r["n"] for r in uni]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    axes[0].plot(ns, [r["distance_calcs"] for r in uni], "o", ms=8, color="#4C72B0", label="measured distance calcs")
    axes[0].plot(ns, [n * (n - 1) / 2 for n in ns], "k--", lw=1, label="theory n(n-1)/2")
    clu = next(r for r in rows if r["layout"] == "clustered")
    axes[0].plot([clu["n"]], [clu["distance_calcs"]], "x", ms=12, color="#C44E52", label="clustered fleet (n = 2,000)")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("number of drones n (log)")
    axes[0].set_ylabel("distance calculations (log)")
    axes[0].set_title("Work = n(n-1)/2 exactly (slope 2 on log-log)")
    axes[0].grid(True, which="both", alpha=0.3)
    axes[0].legend(fontsize=8)
    xs = [10 ** (k / 20) for k in range(40, 101)]
    axes[1].plot(ns, [r["time_s"] for r in uni], "o", ms=8, color="#4C72B0", label="measured time")
    axes[1].plot(xs, [c * x * (x - 1) / 2 for x in xs], "k--", lw=1, label=f"fit c n(n-1)/2, c = {c * 1e9:.0f} ns")
    axes[1].axhline(T_ACCEPT, color="#55A868", ls=":", label="acceptable: 100 ms")
    axes[1].axhline(T_HARD, color="#C44E52", ls=":", label="hard limit: 1 s (telemetry period)")
    axes[1].axvline(n_acc, color="#55A868", lw=0.8)
    axes[1].axvline(n_hard, color="#C44E52", lw=0.8)
    axes[1].text(n_acc * 1.05, 3e-3, f"n = {n_acc:,}", color="#55A868", fontsize=8)
    axes[1].text(n_hard * 1.05, 3e-2, f"n = {n_hard:,}", color="#C44E52", fontsize=8)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("number of drones n (log)")
    axes[1].set_ylabel("time per monitoring cycle (s, log)")
    axes[1].set_title("Time grows as n^2: where brute force becomes impractical")
    axes[1].grid(True, which="both", alpha=0.3)
    axes[1].legend(fontsize=8, loc="upper left")
    fig.suptitle("Q4 - Brute-force closest pair for drone collision-risk monitoring")
    fig.tight_layout()
    fig.savefig(os.path.join(SHOTS, "q4_growth.png"), dpi=150)
    plt.close(fig)
    print("Graph: ../Output_Screenshots/q4_growth.png")


if __name__ == "__main__":
    main()
