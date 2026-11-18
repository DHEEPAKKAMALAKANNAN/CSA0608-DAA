"""Q3 experiments - schoolbook vs Karatsuba on n-digit numbers (CSA06 DAA, Assignment 3 - CO3).

E1  Growth: n = 8 ... 2,048 (powers of 2) plus 617, 1,000 and 1,234 digits (RSA-2048 / RSA-4096 sizes).
    Counts single-digit multiplications and digit additions of both methods, compares them with n^2 and
    3^ceil(log2 n), measures the time, and checks every product against Python's built-in int multiplication.
E2  Threshold sweep: hybrid Karatsuba that falls back to the schoolbook method for n <= t,
    t in {1, 2, 4, 8, 16, 32, 64, 128}, at n = 617 and n = 1,234 digits.
Writes results/q3_sizes.csv and results/q3_threshold.csv.   Run:  py -3 q3_experiments.py
"""
import csv
import math
import os
import random
import time

from q3_karatsuba import (OpCounter, from_digits, karatsuba_multiply, predicted_karatsuba_mults,
                          random_digits, schoolbook_multiply)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SIZES = [8, 16, 32, 64, 128, 256, 512, 617, 1000, 1024, 1234, 2048]
THRESHOLDS = [1, 2, 4, 8, 16, 32, 64, 128]


def timed_run(func, a, b, repeats, *args):
    """Run func(a, b, ops, *args) `repeats` times; return (digits, OpCounter of one run, minimum seconds)."""
    best = float("inf")
    for _ in range(repeats):
        ops = OpCounter()
        start = time.perf_counter()
        digits = func(a, b, ops, *args)
        best = min(best, time.perf_counter() - start)
    return digits, ops, best


def repeats_for(n):
    """Repeat every measurement and keep the minimum (other programs share the processor)."""
    return 7 if n <= 256 else (5 if n <= 1234 else 3)


def experiment_growth(rng):
    """E1: schoolbook, Karatsuba (threshold 1) and hybrid Karatsuba (threshold 16) on random n-digit operands;
    returns the rows written to q3_sizes.csv."""
    print("E1  GROWTH - single-digit multiplications, total digit operations (mults + adds) and time (seed 42)")
    print(f"{'n':>5} | {'SB mults':>10} | {'K mults':>8} {'3^ceil(lgn)':>11} | {'SB total':>10} {'K total':>9} "
          f"{'K/SB':>5} | {'K16 total':>9} {'K16/SB':>6} | {'SB ms':>7} {'K ms':>7} {'K16 ms':>7} | ok")
    print("-" * 121)
    rows = []
    for n in SIZES:
        a, b = random_digits(n, rng), random_digits(n, rng)
        expected = from_digits(a) * from_digits(b)
        reps = repeats_for(n)
        ds, sb, t_sb = timed_run(schoolbook_multiply, a, b, reps)
        dk, ka, t_k = timed_run(karatsuba_multiply, a, b, reps, 1)
        dh, hy, t_h = timed_run(karatsuba_multiply, a, b, reps, 16)
        formula = 3 ** math.ceil(math.log2(n))
        ok = (from_digits(ds) == expected and from_digits(dk) == expected and from_digits(dh) == expected
              and sb.mults == n * n and ka.mults == formula)
        rows.append({"n": n, "power_of_2": int(n & (n - 1) == 0), "sb_mults": sb.mults, "n_squared": n * n,
                     "sb_adds": sb.adds, "sb_total": sb.total, "k_mults": ka.mults, "k_formula_3pow": formula,
                     "k_adds": ka.adds, "k_total": ka.total, "k_calls": ka.calls, "k_depth": ka.max_depth,
                     "k16_mults": hy.mults, "k16_adds": hy.adds, "k16_total": hy.total,
                     "sb_ms": round(t_sb * 1000, 3), "k_ms": round(t_k * 1000, 3), "k16_ms": round(t_h * 1000, 3),
                     "correct": int(ok)})
        print(f"{n:>5} | {sb.mults:>10,} | {ka.mults:>8,} {formula:>11,} | {sb.total:>10,} {ka.total:>9,} "
              f"{ka.total / sb.total:>5.2f} | {hy.total:>9,} {hy.total / sb.total:>6.2f} | "
              f"{t_sb * 1000:>7.1f} {t_k * 1000:>7.1f} {t_h * 1000:>7.1f} | {'yes' if ok else 'NO'}")
    print("ok = all three products equal Python's int product, SB mults = n^2 and K mults = 3^ceil(log2 n)")
    return rows


def experiment_threshold(rng):
    """E2: hybrid Karatsuba (schoolbook for n <= t) at the two RSA sizes; returns the CSV rows."""
    print("\nE2  THRESHOLD SWEEP - hybrid Karatsuba: schoolbook below the threshold t (min of 5 runs)")
    print(f"{'n':>5} {'t':>4} | {'mults':>9} {'predicted':>9} | {'adds':>10} {'total ops':>10} {'calls':>7} | "
          f"{'ms':>7} | {'vs schoolbook (ops)':>19} {'(time)':>7} | ok")
    print("-" * 104)
    rows = []
    for n in (617, 1234):
        a, b = random_digits(n, rng), random_digits(n, rng)
        expected = from_digits(a) * from_digits(b)
        _, sb, t_sb = timed_run(schoolbook_multiply, a, b, 5)
        rows.append({"n": n, "threshold": "schoolbook", "mults": sb.mults, "predicted_mults": n * n,
                     "adds": sb.adds, "total": sb.total, "calls": 1, "ms": round(t_sb * 1000, 3), "correct": 1})
        print(f"{n:>5} {'SB':>4} | {sb.mults:>9,} {n * n:>9,} | {sb.adds:>10,} {sb.total:>10,} {1:>7} | "
              f"{t_sb * 1000:>7.1f} | {'1.00x':>19} {'1.00x':>7} | yes")
        for t in THRESHOLDS:
            dk, ka, t_k = timed_run(karatsuba_multiply, a, b, 5, t)
            ok = from_digits(dk) == expected
            pred = predicted_karatsuba_mults(n, t)
            rows.append({"n": n, "threshold": t, "mults": ka.mults, "predicted_mults": pred, "adds": ka.adds,
                         "total": ka.total, "calls": ka.calls, "ms": round(t_k * 1000, 3), "correct": int(ok)})
            print(f"{n:>5} {t:>4} | {ka.mults:>9,} {pred:>9,} | {ka.adds:>10,} {ka.total:>10,} {ka.calls:>7,} | "
                  f"{t_k * 1000:>7.1f} | {sb.total / ka.total:>18.2f}x {t_sb / t_k:>6.2f}x | {'yes' if ok else 'NO'}")
    return rows


def write_csv(name, rows):
    """Write a list of dicts to results/<name>."""
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return os.path.relpath(path, HERE)


def main():
    os.makedirs(RESULTS, exist_ok=True)
    rng = random.Random(42)
    print("Q3 EXPERIMENTS - SCHOOLBOOK vs KARATSUBA (SB = schoolbook, K = Karatsuba with threshold 1)")
    print("=" * 123)
    growth = experiment_growth(rng)
    sweep = experiment_threshold(rng)

    # crossover: first size from which a Karatsuba variant needs fewer operations / less time than schoolbook
    def first(key_k, key_sb, above=0):
        n = next((r["n"] for r in growth if r["n"] > above and r[key_k] < r[key_sb]), None)
        return f"n = {n}" if n else "not reached up to 2,048"
    print("\nCROSSOVER against schoolbook (sizes of E1)")
    print(f"  Karatsuba t = 1 : fewer single-digit mults from {first('k_mults', 'sb_mults')}; fewer total digit "
          f"operations from {first('k_total', 'sb_total')};")
    print(f"                    less time: {first('k_ms', 'sb_ms')}")
    print(f"  Karatsuba t = 16: fewer total digit operations from {first('k16_total', 'sb_total', 16)}; "
          f"less time from {first('k16_ms', 'sb_ms', 16)} (for n <= 16 it is the schoolbook method)")
    for n in (617, 1234):
        rows = [r for r in sweep if r["n"] == n and r["threshold"] != "schoolbook"]
        best_ops = min(rows, key=lambda r: r["total"])
        best_time = min(rows, key=lambda r: r["ms"])
        print(f"  n = {n}: fewest total operations at t = {best_ops['threshold']} ({best_ops['total']:,}); "
              f"fastest at t = {best_time['threshold']} ({best_time['ms']:.1f} ms)")
    print(f"\nCSV written: {write_csv('q3_sizes.csv', growth)}")
    print(f"CSV written: {write_csv('q3_threshold.csv', sweep)}")


if __name__ == "__main__":
    main()
