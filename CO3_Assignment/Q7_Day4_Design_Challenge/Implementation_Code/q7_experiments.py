"""Q7 Stage 4 (Student B) - experimental validation of the joint D&C design against the O(n^2) baseline.

Experiments (seed 42, synthetic hourly profit/loss of a delivery hub, see q7_max_subarray.hourly_profits):
  E1  growth: counted additions + comparisons and median time of brute force (n <= 4,096), the D&C crossing-scan
      variant and the joint 4-tuple design (n up to 1,048,576), against the closed forms
  E2  data conditions at n = 4,096: counts must not depend on the data; all methods must agree
  E3  small n: median time per call (many repeats) -> from which n is D&C faster than brute force?
  E4  recursion overhead of the joint design: calls, depth, time per hour compared with a plain linear loop
CSV files: results/q7_growth.csv, q7_conditions.csv, q7_small_n.csv, q7_overhead.csv
Run:  py -3 q7_experiments.py   (about 1-2 minutes)
"""
import csv
import math
import os
import random
import statistics
import sys
import time

from q7_max_subarray import Counter, brute_force_max_subarray, dc_crossing, dc_joint, hourly_profits, kadane

sys.setrecursionlimit(10_000)
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def timed(fn, p, repeats):
    """Median and minimum wall-clock seconds of `repeats` runs of fn(p); also returns the last result."""
    times, res = [], None
    for _ in range(repeats):
        t0 = time.perf_counter()
        res = fn(p)
        times.append(time.perf_counter() - t0)
    return res, statistics.median(times), min(times)


def write_csv(name, rows):
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def fmt_big(x):
    """Width-13 number: thousands separators, scientific notation when too wide."""
    return f"{x:>13,}" if x < 10 ** 12 else f"{x:>13.3e}"


def counts(fn, p):
    c = Counter()
    r = fn(p, c)
    return r, c


def experiment_growth():
    print("E1  GROWTH - additions + comparisons (counted) vs closed forms; median time of repeats")
    print(f"{'n':>9} | {'brute ops':>13} {'n(n+1)':>13} | {'crossing ops':>12} {'formula':>11} | "
          f"{'joint ops':>9} {'8(n-1)':>9} | {'brute ms':>9} {'cross ms':>9} {'joint ms':>9} | same")
    print("-" * 122)
    rows = []
    for n in (16, 64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, 1000, 100000):
        p = hourly_profits(n)
        reps = 5 if n <= 65536 else 3
        rx, cx = counts(dc_crossing, p)
        rj, cj = counts(dc_joint, p)
        _, tx, _ = timed(dc_crossing, p, reps)
        _, tj, _ = timed(dc_joint, p, reps)
        lg = math.log2(n)
        cross_formula = 2 * n * lg + n - 1 if lg.is_integer() else float("nan")
        if n <= 4096:
            rb, cb = counts(brute_force_max_subarray, p)
            _, tb, _ = timed(brute_force_max_subarray, p, 3 if n == 4096 else 5)
            same = rb[0] == rx[0] == rj[0] == kadane(p)
            b_ops, b_txt, tb_txt = cb.total, f"{cb.total:>13,}", f"{tb * 1e3:>9.1f}"
        else:
            same = rx[0] == rj[0] == kadane(p)
            b_ops, b_txt, tb_txt, tb = None, f"{'-':>13}", f"{'-':>9}", None
        cf_txt = f"{int(cross_formula):>11,}" if lg.is_integer() else f"{'(not 2^k)':>11}"
        print(f"{n:>9,} | {b_txt} {fmt_big(n * (n + 1))} | {cx.total:>12,} {cf_txt} | {cj.total:>9,} {8 * (n - 1):>9,} | "
              f"{tb_txt} {tx * 1e3:>9.1f} {tj * 1e3:>9.1f} | {'yes' if same else 'NO'}")
        rows.append(dict(n=n, brute_ops=b_ops, brute_formula=n * (n + 1), crossing_ops=cx.total,
                         crossing_additions=cx.additions, crossing_comparisons=cx.comparisons,
                         joint_ops=cj.total, joint_formula=8 * (n - 1), joint_calls=cj.calls, joint_depth=cj.max_depth,
                         brute_ms=None if tb is None else round(tb * 1e3, 3), crossing_ms=round(tx * 1e3, 3),
                         joint_ms=round(tj * 1e3, 3), best=rj[0], same=same))
    print("   formulas: brute n(n+1)/2 additions + n(n+1)/2 comparisons; joint 4(n-1) + 4(n-1) for EVERY n;")
    print("             crossing (n = 2^k) n log2 n + n - 1 additions + n log2 n comparisons")
    write_csv("q7_growth.csv", rows)
    return rows


def experiment_conditions():
    n = 4096
    rng = random.Random(42)
    data = {
        "hourly cycle": hourly_profits(n),
        "random +-400": [rng.randint(-400, 400) for _ in range(n)],
        "all profit": [rng.randint(1, 400) for _ in range(n)],
        "all loss": [rng.randint(-400, -1) for _ in range(n)],
        "alternating": [300 if i % 2 == 0 else -301 for i in range(n)],
        "ascending": sorted(rng.randint(-400, 400) for _ in range(n)),
    }
    print(f"\nE2  DATA CONDITIONS at n = {n:,} - counts are data-independent; answers checked against brute force")
    print(f"{'input':>13} | {'best (Rs)':>10} {'hours':>11} | {'brute ops':>11} {'crossing ops':>12} {'joint ops':>9} |"
          f" {'run valid':>9} {'= brute':>7}")
    print("-" * 96)
    rows = []
    for name, p in data.items():
        rb, cb = counts(brute_force_max_subarray, p)
        rx, cx = counts(dc_crossing, p)
        rj, cj = counts(dc_joint, p)
        valid = sum(p[rj[1]:rj[2] + 1]) == rj[0]
        ok = rb[0] == rx[0] == rj[0]
        print(f"{name:>13} | {rj[0]:>10,} {f'{rj[1]}..{rj[2]}':>11} | {cb.total:>11,} {cx.total:>12,} {cj.total:>9,} |"
              f" {str(valid):>9} {str(ok):>7}")
        rows.append(dict(input=name, n=n, best=rj[0], start=rj[1], end=rj[2], brute_ops=cb.total,
                         crossing_ops=cx.total, joint_ops=cj.total, run_valid=valid, equal_to_brute=ok))
    write_csv("q7_conditions.csv", rows)


def experiment_small_n():
    print("\nE3  SMALL n - median time per call (us) over many repeats: when does D&C beat the O(n^2) baseline?")
    print(f"{'n':>6} | {'brute ops':>9} {'joint ops':>9} | {'brute us':>9} {'cross us':>9} {'joint us':>9} |"
          f" {'joint/brute time':>16}")
    print("-" * 80)
    rows = []
    for n in (2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128):
        p = hourly_profits(n, seed=7)
        loops = max(20, 20000 // n)

        def per_call(fn):
            samples = []
            for _ in range(7):
                t0 = time.perf_counter()
                for _ in range(loops):
                    fn(p)
                samples.append((time.perf_counter() - t0) / loops)
            return statistics.median(samples) * 1e6

        tb, tx, tj = per_call(brute_force_max_subarray), per_call(dc_crossing), per_call(dc_joint)
        _, cb = counts(brute_force_max_subarray, p)
        _, cj = counts(dc_joint, p)
        print(f"{n:>6} | {cb.total:>9,} {cj.total:>9,} | {tb:>9.1f} {tx:>9.1f} {tj:>9.1f} | {tj / tb:>16.2f}")
        rows.append(dict(n=n, brute_ops=cb.total, joint_ops=cj.total, brute_us=round(tb, 2),
                         crossing_us=round(tx, 2), joint_us=round(tj, 2), joint_over_brute=round(tj / tb, 3)))
    ops_x = next(r["n"] for r in rows if r["joint_ops"] < r["brute_ops"])
    time_x = next((r["n"] for r in rows if r["joint_us"] < r["brute_us"]), None)
    print(f"   joint design needs fewer operations from n = {ops_x}; it is faster in time from n = {time_x}")
    write_csv("q7_small_n.csv", rows)


def linear_loop(p):
    """A plain loop touching every hour once (one addition each): the cost floor any method must pay."""
    s = 0
    for x in p:
        s += x
    return s


def experiment_overhead():
    print("\nE4  RECURSION OVERHEAD of the joint design (median of 3 runs)")
    print(f"{'n':>9} | {'calls':>9} {'2n-1':>9} {'depth':>5} {'ceil lg n':>9} | {'joint ns/hour':>13} "
          f"{'loop ns/hour':>12} {'Kadane ns/hour':>14} | {'joint/loop':>10}")
    print("-" * 104)
    rows = []
    for n in (1024, 16384, 262144, 1048576):
        p = hourly_profits(n)
        _, cj = counts(dc_joint, p)
        _, tj, _ = timed(dc_joint, p, 3)
        _, tl, _ = timed(linear_loop, p, 3)
        _, tk, _ = timed(kadane, p, 3)
        print(f"{n:>9,} | {cj.calls:>9,} {2 * n - 1:>9,} {cj.max_depth:>5} {math.ceil(math.log2(n)):>9} | "
              f"{tj / n * 1e9:>13.0f} {tl / n * 1e9:>12.1f} {tk / n * 1e9:>14.1f} | {tj / tl:>10.1f}")
        rows.append(dict(n=n, calls=cj.calls, depth=cj.max_depth, joint_ns_per_hour=round(tj / n * 1e9, 1),
                         loop_ns_per_hour=round(tl / n * 1e9, 1), kadane_ns_per_hour=round(tk / n * 1e9, 1)))
    print("   the recursion costs ~2n calls and one Summary object per call: same Theta(n) as a loop, larger constant")
    write_csv("q7_overhead.csv", rows)


def main():
    print("=" * 122)
    print("Q7 EXPERIMENTS - Maximum Subarray Sum: brute force O(n^2) vs D&C crossing scan vs joint D&C 4-tuple design")
    print("=" * 122)
    experiment_growth()
    experiment_conditions()
    experiment_small_n()
    experiment_overhead()
    print("\nCSV written to results/: q7_growth.csv, q7_conditions.csv, q7_small_n.csv, q7_overhead.csv")


if __name__ == "__main__":
    main()
