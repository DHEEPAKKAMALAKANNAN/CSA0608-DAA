"""Q5 growth experiment - how the brute-force convex-hull work grows with the number of stations.

Prediction (made before running): full scan = C(n,2)(n-2) = n(n-1)(n-2)/2 orientation tests, i.e. Theta(n^3)
(x8 per doubling).  Early rejection can only shorten REJECTED pairs, so it helps on scattered stations but the
accepted edges (and near-boundary pairs) still need all n-2 tests.

Layouts: 'random' = stations uniform in a 100 km x 100 km square (integer metres);
         'circle' = all stations on the perimeter of a circle in random order (every station is a corner);
         'ordered' = the same circle stations listed in boundary order (as surveyed walking the fence) - the order
                     that defeats early rejection.
Full scan: n = 10 .. 320; early rejection: n = 10 .. 1 280 (ordered: up to 640).
Writes results/q5_growth.csv and ../Output_Screenshots/q5_growth.png.
"""

import csv
import math
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from convex_hull_bruteforce import brute_force_hull, monotone_chain, same_cycle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")
FULL_SIZES = [10, 20, 40, 80, 160, 320]
EARLY_SIZES = FULL_SIZES + [640, 1280]


def stations(n, layout, seed=5):
    rng = random.Random(seed * 100_000 + n)
    if layout == "random":
        pts = set()
        while len(pts) < n:
            pts.add((rng.randint(0, 100_000), rng.randint(0, 100_000)))
        return list(pts)
    pts = []                       # circle of radius 10^7 m, angles on a 0.1 degree grid: rounding keeps convexity
    for a in sorted(rng.sample(range(3600), n)):
        t = 2 * math.pi * a / 3600
        pts.append((round(10 ** 7 * math.cos(t)), round(10 ** 7 * math.sin(t))))
    if layout == "circle":
        rng.shuffle(pts)                                   # 'ordered' keeps the boundary (angular) order
    return pts


def main():
    rows = []
    print("Q5 GROWTH - orientation tests of the brute-force hull (prediction: full scan = n(n-1)(n-2)/2, x8 per doubling)")
    print(f"{'layout':<8}{'mode':<7}{'n':>6}{'pairs C(n,2)':>14}{'orientation tests':>19}{'n(n-1)(n-2)/2':>16}"
          f"{'x per 2n':>9}{'corners':>8}{'time (s)':>10}  oracle")
    print("-" * 109)
    plan = [("random", "full", FULL_SIZES), ("random", "early", EARLY_SIZES), ("circle", "full", FULL_SIZES),
            ("circle", "early", EARLY_SIZES), ("ordered", "early", EARLY_SIZES[:-1])]
    for layout, mode, sizes in plan:
        prev = None
        for n in sizes:
            pts = stations(n, layout)
            t0 = time.perf_counter()
            hull, st = brute_force_hull(pts, early_exit=(mode == "early"))
            t = time.perf_counter() - t0
            worst = n * (n - 1) * (n - 2) // 2
            ok = same_cycle(hull, monotone_chain(pts))
            growth = st["orientation_tests"] / prev if prev else float("nan")
            prev = st["orientation_tests"]
            rows.append({"layout": layout, "mode": mode, "n": n, "pairs": st["pairs_examined"],
                         "orientation_tests": st["orientation_tests"], "worst_case_formula": worst,
                         "fraction_of_worst": round(st["orientation_tests"] / worst, 4),
                         "growth_per_doubling": "" if math.isnan(growth) else round(growth, 2),
                         "hull_corners": len(hull), "time_s": round(t, 4), "matches_oracle": ok})
            print(f"{layout:<8}{mode:<7}{n:>6,}{st['pairs_examined']:>14,}{st['orientation_tests']:>19,}{worst:>16,}"
                  f"{'' if math.isnan(growth) else f'{growth:.2f}':>9}{len(hull):>8}{t:>10.3f}  {'OK' if ok else 'WRONG'}")
    full_exact = all(r["orientation_tests"] == r["worst_case_formula"] for r in rows if r["mode"] == "full")
    print(f"Full scan equals n(n-1)(n-2)/2 at every n: {'YES' if full_exact else 'NO'};"
          f"  every hull equals the monotone-chain oracle: {'YES' if all(r['matches_oracle'] for r in rows) else 'NO'}")
    for layout in ("random", "circle", "ordered"):
        r = next(x for x in rows if x["layout"] == layout and x["mode"] == "early" and x["n"] == 320)
        print(f"  early rejection at n = 320 ({layout}): {r['fraction_of_worst']:.1%} of the full-scan tests")

    with open(os.path.join(RESULTS, "q5_growth.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("CSV  : results/q5_growth.csv")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    styles = {("random", "full"): ("o-", "#4C72B0"), ("circle", "full"): ("s--", "#8172B2"),
              ("random", "early"): ("o-", "#55A868"), ("circle", "early"): ("s-", "#C44E52"),
              ("ordered", "early"): ("^-", "#DD8452")}
    for (layout, mode), (st, col) in styles.items():
        rs = [r for r in rows if r["layout"] == layout and r["mode"] == mode]
        lab = f"{layout}, {'full scan' if mode == 'full' else 'early rejection'}"
        axes[0].plot([r["n"] for r in rs], [r["orientation_tests"] for r in rs], st, color=col, label=lab)
        axes[1].plot([r["n"] for r in rs], [r["time_s"] for r in rs], st, color=col, label=lab)
    ns = EARLY_SIZES
    axes[0].plot(ns, [n * (n - 1) * (n - 2) / 2 for n in ns], "k:", lw=1, label="n(n-1)(n-2)/2 (Theta(n^3))")
    axes[0].plot(ns, [n * n for n in ns], color="grey", lw=1, ls="-.", label="n^2 reference")
    for ax, ylab in ((axes[0], "orientation tests (log)"), (axes[1], "time (s, log)")):
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xlabel("number of stations n (log2)")
        ax.set_ylabel(ylab)
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=7)
    axes[0].set_title("Orientation tests: full scan is exactly cubic")
    axes[1].set_title("Execution time (Python, secondary evidence)")
    fig.suptitle("Q5 - Growth of the brute-force convex hull")
    fig.tight_layout()
    fig.savefig(os.path.join(SHOTS, "q5_growth.png"), dpi=150)
    plt.close(fig)
    print("Graph: ../Output_Screenshots/q5_growth.png")


if __name__ == "__main__":
    main()
