"""Q4 experiments - conventional vs Strassen matrix multiplication (CSA06 DAA, Assignment 3 - CO3).

E1  Growth (n = 16 ... 256, powers of 2): conventional and pure Strassen (cutoff 1); counted operations
    against n^3, n^2 (n - 1), 7^k and 6 (7^k - 4^k); time; every product checked against conventional and numpy.
E2  Cutoff sweep at n = 128 and 256: Strassen switches to the conventional method for n <= c,
    c in {1, 2, 4, 8, 16, 32, 64}; counted operations against the recurrence prediction; time.
E3  Sizes that are not powers of 2 (n = 100, 129, 200): conventional vs Strassen with STATIC padding (once, to
    the next power of 2) vs DYNAMIC padding (one zero row/column whenever the current size is odd).
E4  Crossover calculated from the closed forms for n = 2 ... 2,048.
Writes results/q4_growth.csv, q4_cutoff.csv, q4_padding.csv, q4_crossover_formula.csv.   Run:  py -3 q4_experiments.py
"""
import csv
import os
import random
import time

import numpy as np   # used ONLY to verify the products

from q4_strassen import (OpCounter, closed_form_strassen, conventional_multiply, next_power_of_two,
                         predicted_strassen_counts, random_matrix, strassen_multiply, strassen_static_padding)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
GROWTH_SIZES = [16, 32, 64, 128, 256]
CUTOFFS = [1, 2, 4, 8, 16, 32, 64]
PAD_SIZES = [100, 129, 200]
PAD_CUTOFFS = [8, 32]


def timed(func, A, B, repeats, *args):
    """Run func(A, B, ops, *args) `repeats` times; return (C, OpCounter of one run, minimum seconds)."""
    best, C, ops = float("inf"), None, None
    for _ in range(repeats):
        ops = OpCounter()
        start = time.perf_counter()
        C = func(A, B, ops, *args)
        best = min(best, time.perf_counter() - start)
    return C, ops, best


def numpy_check(A, B, C):
    """True if C equals the numpy (int64) product of A and B."""
    return bool(np.array_equal(np.array(A, dtype=np.int64) @ np.array(B, dtype=np.int64), np.array(C)))


def write_csv(name, rows):
    """Write a list of dicts to results/<name> and return the path."""
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return os.path.relpath(path, HERE)


def experiment_growth(rng):
    """E1: conventional vs pure Strassen on powers of 2."""
    print("E1  GROWTH - counted operations against the closed forms (cutoff 1 = recursion down to 1 x 1)")
    print(f"{'n':>4} | {'conv mults':>11} {'= n^3':>5} {'conv adds':>11} {'= n2(n-1)':>9} | {'Str mults':>11} "
          f"{'= 7^k':>5} {'Str adds':>11} {'= 6(7^k-4^k)':>12} | {'ratio mults':>11} {'ratio total':>11}")
    print("-" * 120)
    rows = []
    for n in GROWTH_SIZES:
        A, B = random_matrix(n, rng), random_matrix(n, rng)
        reps = 3 if n <= 128 else 1
        Cc, conv, t_c = timed(conventional_multiply, A, B, reps)
        Cs, st, t_s = timed(strassen_multiply, A, B, reps, 1)
        m7, a7 = closed_form_strassen(n)
        ok = Cs == Cc and numpy_check(A, B, Cs)
        rows.append({"n": n, "conv_mults": conv.mults, "n_cubed": n ** 3, "conv_adds": conv.adds,
                     "conv_total": conv.total, "str_mults": st.mults, "formula_7k": m7, "str_adds": st.adds,
                     "formula_adds": a7, "str_total": st.total, "str_calls": st.calls, "str_depth": st.max_depth,
                     "conv_ms": round(t_c * 1000, 2), "str_ms": round(t_s * 1000, 2), "correct": int(ok)})
        yes = lambda c: "yes" if c else "NO"  # noqa: E731
        print(f"{n:>4} | {conv.mults:>11,} {yes(conv.mults == n ** 3):>5} {conv.adds:>11,} "
              f"{yes(conv.adds == n * n * (n - 1)):>9} | {st.mults:>11,} {yes(st.mults == m7):>5} {st.adds:>11,} "
              f"{yes(st.adds == a7):>12} | {st.mults / conv.mults:>11.3f} {st.total / conv.total:>11.3f}")
    print(f"\n{'n':>4} | {'conv total':>11} {'Str total':>11} | {'conv ms':>9} {'Str ms':>9} {'Str/conv time':>13} | "
          f"{'calls':>7} {'depth':>5} | product correct (conventional + numpy)")
    print("-" * 112)
    for r in rows:
        print(f"{r['n']:>4} | {r['conv_total']:>11,} {r['str_total']:>11,} | {r['conv_ms']:>9.1f} {r['str_ms']:>9.1f} "
              f"{r['str_ms'] / r['conv_ms']:>13.2f} | {r['str_calls']:>7,} {r['str_depth']:>5} | "
              f"{'yes' if r['correct'] else 'NO'}")
    return rows


def experiment_cutoff(rng):
    """E2: cutoff sweep at n = 128 and 256."""
    print("\nE2  CUTOFF SWEEP - conventional multiplication for n <= c (minimum of 3 runs, 1 run for c <= 2 at 256)")
    print(f"{'n':>4} {'c':>5} | {'mults':>11} {'adds':>11} {'total':>11} {'predicted':>9} | {'ms':>8} | "
          f"{'ops vs conv':>11} {'time vs conv':>12} | ok")
    print("-" * 98)
    rows = []
    for n in (128, 256):
        A, B = random_matrix(n, rng), random_matrix(n, rng)
        Cc, conv, t_c = timed(conventional_multiply, A, B, 3)
        rows.append({"n": n, "cutoff": "conventional", "mults": conv.mults, "adds": conv.adds, "total": conv.total,
                     "pred_mults": n ** 3, "pred_adds": n * n * (n - 1), "calls": 1, "ms": round(t_c * 1000, 2),
                     "correct": 1})
        print(f"{n:>4} {'conv':>5} | {conv.mults:>11,} {conv.adds:>11,} {conv.total:>11,} {'yes':>9} | "
              f"{t_c * 1000:>8.1f} | {'1.00x':>11} {'1.00x':>12} | yes")
        for c in CUTOFFS:
            reps = 1 if (n == 256 and c <= 2) else 3
            Cs, st, t_s = timed(strassen_multiply, A, B, reps, c)
            pm, pa = predicted_strassen_counts(n, c)
            ok = Cs == Cc
            rows.append({"n": n, "cutoff": c, "mults": st.mults, "adds": st.adds, "total": st.total,
                         "pred_mults": pm, "pred_adds": pa, "calls": st.calls, "ms": round(t_s * 1000, 2),
                         "correct": int(ok)})
            print(f"{n:>4} {c:>5} | {st.mults:>11,} {st.adds:>11,} {st.total:>11,} "
                  f"{'yes' if (st.mults, st.adds) == (pm, pa) else 'NO':>9} | {t_s * 1000:>8.1f} | "
                  f"{conv.total / st.total:>10.2f}x {t_c / t_s:>11.2f}x | {'yes' if ok else 'NO'}")
    return rows


def experiment_padding(rng):
    """E3: static vs dynamic padding for sizes that are not powers of 2."""
    print("\nE3  PADDING - sizes that are not powers of 2 (minimum of 3 runs)")
    print(f"{'n':>4} {'method':<22} {'c':>3} | {'mults':>11} {'adds':>11} {'total':>11} | {'ms':>8} | "
          f"{'ops vs conv':>11} {'time vs conv':>12} | ok")
    print("-" * 110)
    rows = []
    for n in PAD_SIZES:
        A, B = random_matrix(n, rng), random_matrix(n, rng)
        Cc, conv, t_c = timed(conventional_multiply, A, B, 3)
        rows.append({"n": n, "method": "conventional", "cutoff": "", "padded_to": n, "mults": conv.mults,
                     "adds": conv.adds, "total": conv.total, "ms": round(t_c * 1000, 2), "correct": 1})
        print(f"{n:>4} {'conventional':<22} {'':>3} | {conv.mults:>11,} {conv.adds:>11,} {conv.total:>11,} | "
              f"{t_c * 1000:>8.1f} | {'1.00x':>11} {'1.00x':>12} | yes")
        for c in PAD_CUTOFFS:
            for label, func in (("static", strassen_static_padding), ("dynamic", strassen_multiply)):
                C, st, t_s = timed(func, A, B, 3, c)
                ok = C == Cc and (n != 100 or numpy_check(A, B, C))
                size = next_power_of_two(n) if label == "static" else n
                name = f"Strassen {label}" + (f" (->{size})" if label == "static" else "")
                pm, pa = predicted_strassen_counts(size, c)
                rows.append({"n": n, "method": f"strassen_{label}", "cutoff": c, "padded_to": size,
                             "mults": st.mults, "adds": st.adds, "total": st.total, "ms": round(t_s * 1000, 2),
                             "correct": int(ok and (st.mults, st.adds) == (pm, pa))})
                print(f"{n:>4} {name:<22} {c:>3} | {st.mults:>11,} {st.adds:>11,} {st.total:>11,} | "
                      f"{t_s * 1000:>8.1f} | {conv.total / st.total:>10.2f}x {t_c / t_s:>11.2f}x | "
                      f"{'yes' if rows[-1]['correct'] else 'NO'}")
    return rows


def crossover_from_formulas():
    """E4: total operations from the closed forms (no multiplication is run) for n = 2 ... 2048:
    conventional 2n^3 - n^2, pure Strassen 7^k + 6(7^k - 4^k), hybrid Strassen with cutoff 8."""
    print("\nE4  CROSSOVER FROM THE CLOSED FORMS (calculated, not measured): total scalar operations")
    print(f"{'n':>5} | {'conventional':>15} | {'Strassen c = 1':>15} {'ratio':>6} | {'Strassen c = 8':>15} {'ratio':>6}")
    print("-" * 75)
    rows = []
    for k in range(1, 12):
        n = 2 ** k
        conv = 2 * n ** 3 - n * n
        m1, a1 = predicted_strassen_counts(n, 1)
        m8, a8 = predicted_strassen_counts(n, 8)
        rows.append({"n": n, "conv_total": conv, "str1_total": m1 + a1, "str8_total": m8 + a8})
        print(f"{n:>5} | {conv:>15,} | {m1 + a1:>15,} {(m1 + a1) / conv:>6.3f} | {m8 + a8:>15,} "
              f"{(m8 + a8) / conv:>6.3f}")
    first1 = next(r["n"] for r in rows if r["str1_total"] < r["conv_total"])
    first8 = next(r["n"] for r in rows if r["str8_total"] < r["conv_total"])
    print(f"pure Strassen needs fewer operations than conventional from n = {first1}; "
          f"hybrid (c = 8) from n = {first8}")
    return rows


def main():
    os.makedirs(RESULTS, exist_ok=True)
    rng = random.Random(42)
    print("Q4 EXPERIMENTS - CONVENTIONAL vs STRASSEN (integer matrices with entries 0..9, seed 42)")
    print("=" * 120)
    growth = experiment_growth(rng)
    cutoff = experiment_cutoff(rng)
    padding = experiment_padding(rng)
    formulas = crossover_from_formulas()
    print("\nBEST CUTOFF (E2)")
    for n in (128, 256):
        sub = [r for r in cutoff if r["n"] == n and r["cutoff"] != "conventional"]
        by_ops, by_time = min(sub, key=lambda r: r["total"]), min(sub, key=lambda r: r["ms"])
        print(f"  n = {n}: fewest operations at c = {by_ops['cutoff']} ({by_ops['total']:,}); "
              f"fastest at c = {by_time['cutoff']} ({by_time['ms']:.1f} ms)")
    for name, rows in (("q4_growth.csv", growth), ("q4_cutoff.csv", cutoff), ("q4_padding.csv", padding),
                       ("q4_crossover_formula.csv", formulas)):
        print("CSV written:", write_csv(name, rows))


if __name__ == "__main__":
    main()
