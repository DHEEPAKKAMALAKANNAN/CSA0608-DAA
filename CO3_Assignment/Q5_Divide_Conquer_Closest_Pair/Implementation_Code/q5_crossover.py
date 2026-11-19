"""Q5 - Small-n crossover: from which fleet size is Divide-and-Conquer closest pair worth it? (CSA06 DAA, CO3)

Student B's question: brute force (CO2) makes n(n-1)/2 distance computations and has no overhead; the D&C algorithm
makes O(n) distance computations but pays for a presort, list slicing, merging by y, building strips and recursion.
For small fleets the overhead can dominate, so we measure on EQUIVALENT datasets (the very same point list is given
to both algorithms):

  n = 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256; uniform drones over 20 km x 20 km; 5 seeds per n.

Recorded per n (mean over the 5 seeds):
  distance computations          - the primary basic operation (brute force: exactly n(n-1)/2);
  total basic operations         - distances + key comparisons of the presort and of the merges by y
                                   (the best-so-far test follows every distance in BOTH algorithms, so it is not
                                   counted separately);
  time                           - median of 7 timed loops (each loop repeats the call k times so that it lasts
                                   a few milliseconds), averaged over the seeds. Times are noisy (other programs ran
                                   on the same computer); the counts are exact.

Crossover n = the smallest tested n from which D&C is lower than brute force for every larger tested n.
Writes results/q5_crossover.csv.   Run:  py -3 q5_crossover.py
"""
import csv
import os
import statistics
import time

from q5_closest_pair import closest_pair_brute_force, closest_pair_dc, Counters
from q5_experiments import uniform_fleet

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SIZES = [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]
SEEDS = [42, 43, 44, 45, 46]
TIMED_LOOPS = 7


def loop_time(fn, pts, k):
    """Median over TIMED_LOOPS loops of the time of one call fn(pts) (each loop makes k calls)."""
    samples = []
    for _ in range(TIMED_LOOPS):
        t0 = time.perf_counter()
        for _ in range(k):
            fn(pts, Counters())
        samples.append((time.perf_counter() - t0) / k)
    return statistics.median(samples)


def crossover(rows, key_bf, key_dc):
    """Smallest n from which D&C < brute force for this and every larger tested n (None if never)."""
    answer = None
    for r in reversed(rows):
        if r[key_dc] < r[key_bf]:
            answer = r["n"]
        else:
            break
    return answer


def main():
    os.makedirs(RESULTS, exist_ok=True)
    print("=" * 112)
    print("Q5  SMALL-n CROSSOVER - brute force (BF) vs Divide-and-Conquer (D&C) on the same uniform fleets (5 seeds)")
    print("=" * 112)
    print(f"{'n':>5} | {'BF dist':>8} {'D&C dist':>9} | {'BF ops':>8} {'D&C ops':>8} {'ops D&C/BF':>10} | "
          f"{'BF us':>9} {'D&C us':>9} {'time D&C/BF':>11} | {'same':>4} | {'calls':>5} {'depth':>5}")
    print("-" * 112)
    rows = []
    for n in SIZES:
        bf_d, dc_d, dc_ops, t_bf, t_dc, calls, depth, same = [], [], [], [], [], [], [], True
        k = max(5, 20000 // (n * (n - 1) // 2 + 10 * n))
        for seed in SEEDS:
            pts = uniform_fleet(n, seed)
            d1, _, cb = closest_pair_brute_force(pts, Counters())
            d2, _, cd = closest_pair_dc(pts, Counters())
            same &= (d1 == d2)
            bf_d.append(cb.distances)
            dc_d.append(cd.distances)
            dc_ops.append(cd.distances + cd.sort_comparisons + cd.merge_comparisons)
            calls.append(cd.calls)
            depth.append(cd.max_depth)
            t_bf.append(loop_time(closest_pair_brute_force, pts, k))
            t_dc.append(loop_time(closest_pair_dc, pts, k))
        r = {"n": n, "bf_distances": statistics.mean(bf_d), "dc_distances": statistics.mean(dc_d),
             "bf_total_ops": statistics.mean(bf_d), "dc_total_ops": statistics.mean(dc_ops),
             "bf_time_us": statistics.mean(t_bf) * 1e6, "dc_time_us": statistics.mean(t_dc) * 1e6,
             "dc_calls": statistics.mean(calls), "dc_max_depth": max(depth), "same_distance": "YES" if same else "NO",
             "calls_per_loop": k}
        rows.append(r)
        print(f"{n:>5} | {r['bf_distances']:>8,.0f} {r['dc_distances']:>9,.1f} | {r['bf_total_ops']:>8,.0f} "
              f"{r['dc_total_ops']:>8,.1f} {r['dc_total_ops'] / r['bf_total_ops']:>10.2f} | {r['bf_time_us']:>9.1f} "
              f"{r['dc_time_us']:>9.1f} {r['dc_time_us'] / r['bf_time_us']:>11.2f} | {r['same_distance']:>4} | "
              f"{r['dc_calls']:>5.0f} {r['dc_max_depth']:>5}")
    with open(os.path.join(RESULTS, "q5_crossover.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({key: (round(v, 3) if isinstance(v, float) else v) for key, v in r.items()})
    print("-" * 112)
    c_dist = crossover(rows, "bf_distances", "dc_distances")
    c_ops = crossover(rows, "bf_total_ops", "dc_total_ops")
    c_time = crossover(rows, "bf_time_us", "dc_time_us")
    print("Crossover (smallest tested n from which D&C stays below brute force):")
    print(f"   distance computations : n = {c_dist}")
    print(f"   total basic operations: n = {c_ops}")
    print(f"   measured time (median): n = {c_time}")
    last = rows[-1]
    print(f"At n = {last['n']}: D&C needs {last['dc_distances'] / last['bf_distances'] * 100:.1f}% of the distance "
          f"computations, {last['dc_total_ops'] / last['bf_total_ops'] * 100:.1f}% of the operations and "
          f"{last['dc_time_us'] / last['bf_time_us'] * 100:.1f}% of the time of brute force")
    print(f"All {len(SIZES) * len(SEEDS)} fleets: both algorithms returned the same distance: "
          f"{all(r['same_distance'] == 'YES' for r in rows)}")
    print("CSV written: results/q5_crossover.csv")


if __name__ == "__main__":
    main()
