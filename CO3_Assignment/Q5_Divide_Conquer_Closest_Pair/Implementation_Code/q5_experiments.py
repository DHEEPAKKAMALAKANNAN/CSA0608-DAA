"""Q5 - Experiments: Divide-and-Conquer closest pair against brute force (CSA06 DAA, Assignment 3 - CO3).

Four drone distributions over a 20 km x 20 km city (fixed seeds):
  uniform   - drones spread evenly over the city;
  clustered - 90 % of the drones within ~400 m of five delivery hubs (realistic rush-hour traffic);
  line      - every drone on the same north-south corridor (identical x): the strip contains ALL points;
  duplicate - uniform, plus one drone reported twice at the same position (closest distance 0).

For every run the program records distance computations (primary evidence), presort/merge comparisons, strip sizes,
the largest number of neighbours examined by one strip point (theory: <= 7), and the time. Brute force is run up to
8,000 drones; beyond that its n(n-1)/2 distance computations are exact and its time is EXTRAPOLATED from the measured
cost per distance (labelled "extrap."). Every comparable run checks that both algorithms return the same distance.

Writes results/q5_scaling.csv and results/q5_strip_histogram.csv.   Run:  py -3 q5_experiments.py
"""
import csv
import math
import os
import random
import time

from q5_closest_pair import closest_pair_brute_force, closest_pair_dc, Counters

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
AREA = 20000.0                                  # metres
HUBS = [(4000.0, 4000.0), (15000.0, 5000.0), (10000.0, 10000.0), (5000.0, 16000.0), (16000.0, 15000.0)]
DC_SIZES = [1000, 2000, 4000, 8000, 20000, 50000, 100000]
BF_SIZES = {"uniform": [1000, 2000, 4000, 8000], "clustered": [1000, 2000, 4000, 8000],
            "line": [1000, 2000, 4000], "duplicate": [1000, 2000, 4000]}
HIST_N = 20000


# ----------------------------------------------------------------------------------------------- datasets
def uniform_fleet(n, seed=42):
    """n drones uniformly distributed over the city."""
    rng = random.Random(seed)
    return [(rng.uniform(0, AREA), rng.uniform(0, AREA)) for _ in range(n)]


def clustered_fleet(n, seed=42):
    """90 % of the drones near one of five hubs (Gaussian, sigma 400 m), 10 % anywhere in the city."""
    rng = random.Random(seed)
    pts = []
    for _ in range(n):
        if rng.random() < 0.9:
            hx, hy = HUBS[rng.randrange(len(HUBS))]
            x = min(max(rng.gauss(hx, 400.0), 0.0), AREA)
            y = min(max(rng.gauss(hy, 400.0), 0.0), AREA)
        else:
            x, y = rng.uniform(0, AREA), rng.uniform(0, AREA)
        pts.append((x, y))
    return pts


def line_fleet(n, seed=42):
    """All drones on the corridor x = 10 km (identical x), spread along y."""
    rng = random.Random(seed)
    return [(10000.0, rng.uniform(0, AREA)) for _ in range(n)]


def duplicate_fleet(n, seed=42):
    """Uniform fleet of n - 1 drones plus a second report of one drone's position (closest distance = 0)."""
    rng = random.Random(seed)
    pts = uniform_fleet(n - 1, seed)
    pts.insert(rng.randrange(n), pts[rng.randrange(n - 1)])
    return pts


GENERATORS = {"uniform": uniform_fleet, "clustered": clustered_fleet, "line": line_fleet, "duplicate": duplicate_fleet}


def timed(fn, pts, repeats):
    """Run fn(pts) `repeats` times; return (result of the last run, minimum wall-clock time in seconds)."""
    best_t, res = math.inf, None
    for _ in range(repeats):
        t0 = time.perf_counter()
        res = fn(pts, Counters())
        best_t = min(best_t, time.perf_counter() - t0)
    return res, best_t


def main():
    os.makedirs(RESULTS, exist_ok=True)
    rows, hist_rows = [], []
    print("=" * 120)
    print("Q5  Closest pair of airborne drones: Divide-and-Conquer (D&C) vs brute force (BF)   (seed 42, 20 km x 20 km)")
    print("=" * 120)
    head = (f"{'distribution':<10}{'n':>8}{'D&C dist':>10}{'dist/n':>7}{'strip pts':>10}{'max nb':>7}{'sort+merge':>11}"
            f"{'D&C time s':>11}{'BF n(n-1)/2':>15}{'BF time s':>14}{'same':>6}{'closest m':>11}")
    for dist_name, gen in GENERATORS.items():
        print(head)
        print("-" * 120)
        cost_per_pair = None
        for n in DC_SIZES:
            pts = gen(n)
            (d_dc, pair_dc, c), t_dc = timed(closest_pair_dc, pts, 3 if n <= 20000 else 1)
            pairs = n * (n - 1) // 2
            if n in BF_SIZES[dist_name]:
                (d_bf, _, cb), t_bf = timed(closest_pair_brute_force, pts, 3 if n <= 2000 else 1)
                assert cb.distances == pairs
                cost_per_pair = t_bf / pairs
                status, same = "measured", ("YES" if d_bf == d_dc else "NO")
            else:
                t_bf, status, same = cost_per_pair * pairs, "extrap.", "-"
            sm = c.sort_comparisons + c.merge_comparisons
            rows.append({"distribution": dist_name, "n": n, "dc_distances": c.distances,
                         "dc_distances_per_n": round(c.distances / n, 3), "dc_strip_points": c.strip_points,
                         "dc_max_neighbours": c.max_neighbours, "dc_sort_comparisons": c.sort_comparisons,
                         "dc_merge_comparisons": c.merge_comparisons, "dc_calls": c.calls, "dc_max_depth": c.max_depth,
                         "n_log2_n": round(n * math.log2(n)), "dc_time_s": round(t_dc, 5), "bf_distances": pairs,
                         "bf_time_s": round(t_bf, 4), "bf_time_status": status, "same_distance": same,
                         "closest_distance_m": round(d_dc, 4)})
            if n == HIST_N:
                for k in range(9):
                    hist_rows.append({"distribution": dist_name, "n": n, "neighbours_examined": k if k < 8 else ">7",
                                      "strip_points": c.neighbour_hist[k]})
            bf_txt = f"{t_bf:.3f}" + ("    " if status == "measured" else " ext")
            print(f"{dist_name:<10}{n:>8,}{c.distances:>10,}{c.distances / n:>7.2f}{c.strip_points:>10,}"
                  f"{c.max_neighbours:>7}{sm:>11,}{t_dc:>11.4f}{pairs:>15,}{bf_txt:>14}{same:>6}{d_dc:>11.3f}")
        print()

    with open(os.path.join(RESULTS, "q5_scaling.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(RESULTS, "q5_strip_histogram.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hist_rows[0].keys()))
        w.writeheader()
        w.writerows(hist_rows)

    # ------------------------------------------------------------------ 1-second update cycle
    print("1-second update cycle (D&C measured; BF beyond 8,000 extrapolated from its measured cost per distance):")
    for dist_name in GENERATORS:
        r20 = next(r for r in rows if r["distribution"] == dist_name and r["n"] == 20000)
        r100 = next(r for r in rows if r["distribution"] == dist_name and r["n"] == 100000)
        print(f"  {dist_name:<10} n = 20,000: D&C {r20['dc_time_s']:.3f} s, BF {r20['bf_time_s']:.1f} s   |   "
              f"n = 100,000: D&C {r100['dc_time_s']:.3f} s, BF {r100['bf_time_s']:.0f} s")
    worst_nb = max(r["dc_max_neighbours"] for r in rows)
    mism = sum(1 for r in rows if r["same_distance"] == "NO")
    print(f"Largest number of neighbours examined by any strip point in all {len(rows)} runs: {worst_nb} (bound 7)")
    print(f"Runs where D&C and brute force disagreed: {mism}")
    print("CSV written: results/q5_scaling.csv, results/q5_strip_histogram.csv")


if __name__ == "__main__":
    main()
