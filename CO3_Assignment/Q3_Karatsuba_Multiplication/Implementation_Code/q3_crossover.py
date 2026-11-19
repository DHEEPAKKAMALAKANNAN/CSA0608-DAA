"""Q3 crossover investigation - repeated timing of schoolbook vs Karatsuba (CSA06 DAA, Assignment 3 - CO3).

Student B's experiment for the official Q3 bullets: design the input sizes, conduct REPEATED timing experiments,
record multiplication counts, determine the approximate crossover range, and identify the recursion /
decomposition overhead that makes Karatsuba worse for small inputs.

C1  Pure Karatsuba (threshold 1, recursion down to single digits) vs schoolbook at n = 256 ... 4,096 digits,
    including 1,536 and 3,072 (not powers of 2) to show the 3^ceil(log2 n) step effect.
    5 repeats per measurement (3 when one run takes more than 1 s); median, minimum and maximum are reported.
C2  Hybrid Karatsuba (schoolbook for n <= t, t = 16 and t = 32) vs schoolbook at fine sizes 8 ... 128 digits,
    21 repeats per measurement (median).
C3  Overhead breakdown per recursion level for n = 64 and n = 1,024 (threshold 1 and 16): nodes (calls),
    own single-digit multiplications, own digit additions/subtractions and digits held in temporary lists.
Every product is checked against Python's built-in int multiplication.
Writes results/q3_crossover_pure.csv, results/q3_crossover_hybrid.csv, results/q3_overhead_levels.csv.
Run:  py -3 q3_crossover.py      (about 2-3 minutes)
"""
import csv
import math
import os
import random
import statistics
import time

from q3_karatsuba import OpCounter, from_digits, karatsuba_multiply, random_digits, schoolbook_multiply

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
PURE_SIZES = [256, 512, 1024, 1536, 2048, 3072, 4096]
HYBRID_SIZES = [8, 12, 16, 20, 24, 32, 40, 48, 64, 96, 128]
HYBRID_THRESHOLDS = [16, 32]


def repeated(func, a, b, repeats, *args):
    """Run func(a, b, ops, *args) `repeats` times; return (digits, OpCounter of one run, list of seconds)."""
    times = []
    digits = ops = None
    for _ in range(repeats):
        ops = OpCounter()
        start = time.perf_counter()
        digits = func(a, b, ops, *args)
        times.append(time.perf_counter() - start)
    return digits, ops, times


def adaptive(func, a, b, *args):
    """5 repeats, or 3 when one run takes more than 1 s (keeps the experiment under a few minutes)."""
    digits, ops, first = repeated(func, a, b, 1, *args)
    reps = 2 if first[0] > 1.0 else 4
    _, _, more = repeated(func, a, b, reps, *args)
    return digits, ops, first + more


def write_csv(name, rows):
    """Write a list of dicts to results/<name>."""
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


def experiment_pure(rng):
    """C1: pure Karatsuba (t = 1) against the schoolbook method at large sizes."""
    print("C1  PURE KARATSUBA (t = 1) vs SCHOOLBOOK - repeated timing (5 runs, 3 if a run > 1 s), times in ms")
    print(f"{'n':>5} | {'SB mults':>10} {'K mults':>8} {'K/SB':>5} | {'SB ops':>10} {'K ops':>10} {'K/SB':>5} | "
          f"{'SB med':>7} {'SB min':>7} {'SB max':>7} | {'K med':>7} {'K min':>7} {'K max':>7} | "
          f"{'tK/tSB':>6} {'reps':>4}")
    print("-" * 124)
    rows = []
    for n in PURE_SIZES:
        a, b = random_digits(n, rng), random_digits(n, rng)
        ref = from_digits(a) * from_digits(b)
        ds, sb, t_sb = adaptive(schoolbook_multiply, a, b)
        dk, ka, t_k = adaptive(karatsuba_multiply, a, b, 1)
        assert from_digits(ds) == ref and from_digits(dk) == ref
        assert ka.mults == 3 ** math.ceil(math.log2(n))
        sm, km = statistics.median(t_sb) * 1e3, statistics.median(t_k) * 1e3
        rows.append({"n": n, "sb_mults": sb.mults, "k_mults": ka.mults, "sb_total": sb.total,
                     "k_total": ka.total, "k_calls": ka.calls, "sb_ms_median": round(sm, 2),
                     "sb_ms_min": round(min(t_sb) * 1e3, 2), "sb_ms_max": round(max(t_sb) * 1e3, 2),
                     "k_ms_median": round(km, 2), "k_ms_min": round(min(t_k) * 1e3, 2),
                     "k_ms_max": round(max(t_k) * 1e3, 2), "repeats": len(t_k), "correct": 1})
        print(f"{n:>5} | {sb.mults:>10,} {ka.mults:>8,} {ka.mults / sb.mults:>5.2f} | {sb.total:>10,} "
              f"{ka.total:>10,} {ka.total / sb.total:>5.2f} | {sm:>7.1f} {min(t_sb) * 1e3:>7.1f} "
              f"{max(t_sb) * 1e3:>7.1f} | {km:>7.1f} {min(t_k) * 1e3:>7.1f} {max(t_k) * 1e3:>7.1f} | "
              f"{km / sm:>6.2f} {len(t_k):>4}")
    return rows


def experiment_hybrid(rng):
    """C2: hybrid Karatsuba (t = 16, 32) against the schoolbook method at small sizes (21 repeats, median)."""
    reps = 21
    print(f"\nC2  HYBRID KARATSUBA vs SCHOOLBOOK at small sizes - median of {reps} runs, times in microseconds")
    print(f"{'n':>4} | {'SB ops':>7} {'K16 ops':>8} {'K32 ops':>8} | {'SB us':>8} {'K16 us':>8} {'K32 us':>8} | "
          f"{'tK16/tSB':>8} {'tK32/tSB':>8} | {'K1 ops':>8} {'K1 us':>8} {'tK1/tSB':>7}")
    print("-" * 112)
    rows = []
    for n in HYBRID_SIZES:
        a, b = random_digits(n, rng), random_digits(n, rng)
        ref = from_digits(a) * from_digits(b)
        ds, sb, t_sb = repeated(schoolbook_multiply, a, b, reps)
        res = {}
        for t in HYBRID_THRESHOLDS + [1]:
            dk, ka, tk = repeated(karatsuba_multiply, a, b, reps, t)
            assert from_digits(dk) == ref
            res[t] = (ka, statistics.median(tk) * 1e6)
        assert from_digits(ds) == ref
        s_us = statistics.median(t_sb) * 1e6
        rows.append({"n": n, "sb_total": sb.total, "sb_us": round(s_us, 2),
                     "k16_total": res[16][0].total, "k16_us": round(res[16][1], 2),
                     "k32_total": res[32][0].total, "k32_us": round(res[32][1], 2),
                     "k1_total": res[1][0].total, "k1_calls": res[1][0].calls, "k1_us": round(res[1][1], 2),
                     "repeats": reps})
        print(f"{n:>4} | {sb.total:>7,} {res[16][0].total:>8,} {res[32][0].total:>8,} | {s_us:>8.1f} "
              f"{res[16][1]:>8.1f} {res[32][1]:>8.1f} | {res[16][1] / s_us:>8.2f} {res[32][1] / s_us:>8.2f} | "
              f"{res[1][0].total:>8,} {res[1][1]:>8.1f} {res[1][1] / s_us:>7.2f}")
    return rows


def experiment_overhead(rng):
    """C3: per-level breakdown of the work of one Karatsuba multiplication."""
    print("\nC3  OVERHEAD PER RECURSION LEVEL (own work of the nodes at each depth; temp = digits in temporary lists)")
    rows = []
    for n, t in ((64, 1), (64, 16), (1024, 16)):
        a, b = random_digits(n, rng), random_digits(n, rng)
        ops = OpCounter(per_level=True)
        karatsuba_multiply(a, b, ops, t)
        print(f"  n = {n}, threshold t = {t}: {ops.calls:,} calls, {ops.mults:,} mults, {ops.adds:,} adds "
              f"({ops.adds / ops.mults:.1f} adds per mult)")
        print(f"    {'depth':>5} {'nodes':>7} {'digits/node':>11} {'own mults':>10} {'own adds':>9} {'temp digits':>11}")
        for depth in sorted(ops.levels):
            calls, mults, adds, temp = ops.levels[depth]
            size = math.ceil(n / 2 ** depth)
            rows.append({"n": n, "threshold": t, "depth": depth, "nodes": calls, "digits_per_node": size,
                         "own_mults": mults, "own_adds": adds, "temp_digits": temp})
            print(f"    {depth:>5} {calls:>7,} {size:>11} {mults:>10,} {adds:>9,} {temp:>11,}")
    return rows


def first_size(rows, better):
    """Smallest n from which `better(row)` holds for that size and every larger size; None if never."""
    result = None
    for row in reversed(rows):
        if better(row):
            result = row["n"]
        else:
            break
    return result


def main():
    rng = random.Random(42)
    print("Q3 CROSSOVER INVESTIGATION - schoolbook (SB) vs Karatsuba (K), random operands, seed 42")
    print("=" * 124)
    pure = experiment_pure(rng)
    hybrid = experiment_hybrid(rng)
    levels = experiment_overhead(rng)
    print("\nCROSSOVER RANGES (operation counts are exact; times are noisy - other programs shared the CPU)")
    small_ops = first_size(hybrid, lambda r: r["k1_total"] < r["sb_total"])
    time_pure = first_size(pure, lambda r: r["k_ms_median"] < r["sb_ms_median"])
    print(f"  pure K (t = 1): fewer single-digit mults at every size; fewer total ops from n = {small_ops} "
          f"(C2) and at every size of C1; median time lower from n = {time_pure}")
    for t in HYBRID_THRESHOLDS:
        o = first_size(hybrid, lambda r: r[f"k{t}_total"] < r["sb_total"])
        tt = first_size(hybrid, lambda r: r[f"k{t}_us"] < r["sb_us"])
        print(f"  hybrid t = {t}: fewer total ops from n = {o}; median time lower from n = {tt} "
              f"(n <= {t} is the schoolbook method itself)")
    k1_ratio = min(r["k1_us"] / r["sb_us"] for r in hybrid)
    print(f"  pure K at small sizes (8..128): never faster than SB (best time ratio {k1_ratio:.2f})")
    print(f"CSV written: {os.path.relpath(write_csv('q3_crossover_pure.csv', pure), HERE)}, "
          f"{os.path.relpath(write_csv('q3_crossover_hybrid.csv', hybrid), HERE)}, "
          f"{os.path.relpath(write_csv('q3_overhead_levels.csv', levels), HERE)}")


if __name__ == "__main__":
    main()
