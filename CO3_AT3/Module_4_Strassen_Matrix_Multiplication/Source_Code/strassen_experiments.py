"""SwiftLogix - Module 4 experiments: Strassen vs the naive product, the crossover point and the cutoff.

A  counted scalar operations (multiplications + additions) vs the closed forms, n = 2 ... 256
   (formula-only rows for 512 and the production size 1,024)
B  wall-clock time of naive vs Strassen with cutoffs 16 / 32 / 64 (min of 3 runs; 1 run at n = 256)
C  cutoff sweep at n = 256 (operations and time)
D  non-power-of-two sizes: next-power-of-two padding vs minimal s * 2^d padding
E  memory (tracemalloc peak) and floating-point error vs numpy float64
Matrices hold random integers 0..9 (exact arithmetic) except in E.  numpy is used only for checking.

Run:  py -3 strassen_experiments.py      (about 2-3 minutes)
"""
import csv
import math
import random
import sys
import time
import tracemalloc
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from strassen import OpCounter, naive_multiply, padded_size, strassen_multiply, strassen_ops  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "Supporting_Files" / "results"
GRAPHS = ROOT / "Module_4_Strassen_Matrix_Multiplication" / "Report" / "graphs"
SIZES = [2 ** k for k in range(1, 9)]            # 2 ... 256 (run);  512, 1024 by formula
CUTOFFS = [1, 8, 16, 32, 64]
PURE_MAX = 64                                    # pure Strassen (cutoff 1) is run up to this size


def rand_matrix(n, seed, floats=False):
    rng = random.Random(seed)
    if floats:
        return [[rng.random() for _ in range(n)] for _ in range(n)]
    return [[rng.randint(0, 9) for _ in range(n)] for _ in range(n)]


def naive_total(n):
    return 2 * n ** 3 - n ** 2


def strassen_total(n, cutoff):
    m, a = strassen_ops(n, cutoff)
    return m + a


def timed(fn, reps):
    best, out = float("inf"), None
    for _ in range(reps):
        t0 = time.perf_counter()
        out = fn()
        best = min(best, time.perf_counter() - t0)
    return best, out


def save_csv(name, header, rows):
    for folder in (RESULTS, GRAPHS):
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows_a, counted = [], {}
    print("=" * 117)
    print("M4 experiment A - scalar operations (mults + adds): counted by running vs closed form; ratio = Strassen / naive")
    print("=" * 117)
    print(f"{'n':>5} | {'naive 2n^3-n^2':>15} | {'pure Strassen':>15} {'ratio':>5} | {'cutoff 8':>14} {'ratio':>5} | "
          f"{'cutoff 16':>14} {'cutoff 32':>14} | {'counted = formula':>17}")
    for n in SIZES + [512, 1024]:
        A, B = rand_matrix(n, 1), rand_matrix(n, 2)
        ref = (np.array(A) @ np.array(B)).tolist() if n <= 256 else None
        ok = True
        vals = {"naive": naive_total(n)}
        if n <= 256:
            c = OpCounter()
            ok &= naive_multiply(A, B, c) == ref and c.total == vals["naive"]
        for cut in CUTOFFS:
            vals[cut] = strassen_total(n, cut)
            if n <= 256 and (cut > 1 or n <= PURE_MAX):
                c = OpCounter()
                ok &= strassen_multiply(A, B, cutoff=cut, counter=c) == ref and c.total == vals[cut]
                counted[n, cut] = c.total
        status = "yes (all run)" if n <= PURE_MAX else ("yes (cutoff>1)" if n <= 256 else "formula only")
        if n <= 256 and not ok:
            status = "MISMATCH"
        rows_a.append([n, vals["naive"]] + [vals[c] for c in CUTOFFS] + [status])
        print(f"{n:>5} | {vals['naive']:>15,} | {vals[1]:>15,} {vals[1] / vals['naive']:>5.2f} | {vals[8]:>14,} "
              f"{vals[8] / vals['naive']:>5.2f} | {vals[16]:>14,} {vals[32]:>14,} | {status:>17}")
    save_csv("m4_strassen_operations.csv", ["n", "naive_ops"] + [f"strassen_cutoff_{c}_ops" for c in CUTOFFS] +
             ["verified"], rows_a)
    pure_cross = next(n for n in [2 ** k for k in range(1, 15)] if strassen_total(n, 1) < naive_total(n))
    best_cut = min((2 ** k for k in range(11)), key=lambda k: strassen_total(1024, k))
    print(f"pure Strassen first needs fewer operations than naive at n = {pure_cross:,};")
    print("one Strassen level pays off when 2n^3 - n^2 > 1.75 n^3 + 2.75 n^2, i.e. 0.25 n^3 > 3.75 n^2, i.e. n > 15")
    print(f"operation-optimal cutoff for n = 1,024: n0 = {best_cut} -> {strassen_total(1024, best_cut):,} operations "
          f"({strassen_total(1024, best_cut) / naive_total(1024):.3f} x naive)")

    # --- B: wall-clock time
    rows_b = []
    print()
    print("M4 experiment B - wall-clock time in seconds (min of 3 runs; 1 run for n >= 256)")
    print(f"{'n':>5} | {'naive':>8} | {'pure':>8} {'cutoff 16':>9} {'cutoff 32':>9} {'cutoff 64':>9} | "
          f"{'best Strassen vs naive':>22}")
    cell = lambda t, w: f"{t:>{w}.4f}" if t is not None else f"{'-':>{w}}"
    for n in (16, 32, 64, 128, 256, 512):
        A, B = rand_matrix(n, 3), rand_matrix(n, 4)
        reps = 1 if n >= 256 else 3
        t_naive, ref = timed(lambda: naive_multiply(A, B), reps)
        times = {}
        for cut in (1, 16, 32, 64):
            if (cut == 1 and n > PURE_MAX) or (cut == 16 and n > 256):
                continue
            t, out = timed(lambda: strassen_multiply(A, B, cutoff=cut), reps)
            assert out == ref
            times[cut] = t
        best_cut = min((c for c in times if c > 1), key=times.get)
        rows_b.append([n, round(t_naive, 5)] + [round(times[c], 5) if c in times else "" for c in (1, 16, 32, 64)])
        print(f"{n:>5} | {t_naive:>8.4f} | {cell(times.get(1), 8)} {cell(times.get(16), 9)} {cell(times.get(32), 9)} "
              f"{cell(times.get(64), 9)} | cutoff {best_cut:>2}: {t_naive / times[best_cut]:>5.2f}x")
    save_csv("m4_strassen_time.csv", ["n", "naive_s", "pure_s", "cutoff16_s", "cutoff32_s", "cutoff64_s"], rows_b)

    # --- C: cutoff sweep at n = 256
    n = 256
    A, B = rand_matrix(n, 5), rand_matrix(n, 6)
    t_naive, ref = timed(lambda: naive_multiply(A, B), 1)
    rows_c = []
    print()
    print(f"M4 experiment C - cutoff sweep at n = {n} (naive below the cutoff; 1 run each)")
    print(f"{'cutoff':>6} | {'levels':>6} | {'operations':>12} {'vs naive':>8} | {'time s':>7} {'vs naive':>8}")
    for cut in (4, 8, 16, 32, 64, 128, 256):
        t, out = timed(lambda: strassen_multiply(A, B, cutoff=cut), 1)
        assert out == ref
        ops = strassen_total(n, cut)
        levels = int(math.log2(n // cut))
        rows_c.append([cut, levels, ops, round(t, 4)])
        print(f"{cut:>6} | {levels:>6} | {ops:>12,} {ops / naive_total(n):>8.3f} | {t:>7.3f} {t / t_naive:>8.3f}")
    print(f"(cutoff 256 = plain naive product; naive measured separately: {t_naive:.3f} s)")
    save_csv("m4_cutoff_sweep.csv", ["cutoff", "strassen_levels", "operations", "time_s"], rows_c)

    # --- D: padding
    rows_d = []
    print()
    print("M4 experiment D - sizes that are not powers of two (cutoff 32): padding policy")
    print(f"{'n':>4} | {'naive ops':>11} | {'pow2 size':>9} {'ops':>12} {'time s':>7} | {'minimal size':>12} {'ops':>12} "
          f"{'time s':>7} | {'saving':>6}")
    for n in (100, 129, 200):
        A, B = rand_matrix(n, 7), rand_matrix(n, 8)
        t_ref, ref = timed(lambda: naive_multiply(A, B), 1)
        res = {}
        for mode in ("pow2", "minimal"):
            c = OpCounter()
            t, out = timed(lambda: strassen_multiply(A, B, cutoff=32, padding=mode, counter=c), 1)
            assert out == ref
            res[mode] = (padded_size(n, 32, mode), c.total, t)
        rows_d.append([n, naive_total(n), *res["pow2"], *res["minimal"], round(t_ref, 4)])
        p, m = res["pow2"], res["minimal"]
        print(f"{n:>4} | {naive_total(n):>11,} | {p[0]:>9} {p[1]:>12,} {p[2]:>7.3f} | {m[0]:>12} {m[1]:>12,} "
              f"{m[2]:>7.3f} | {p[1] / m[1]:>5.2f}x")
    save_csv("m4_padding.csv", ["n", "naive_ops", "pow2_size", "pow2_ops", "pow2_time_s", "minimal_size",
                                "minimal_ops", "minimal_time_s", "naive_time_s"], rows_d)

    # --- E: memory and floating-point error
    rows_e = []
    print()
    print("M4 experiment E - peak traced memory (tracemalloc) and float64 error vs numpy (random reals in [0, 1))")
    print(f"{'n':>4} | {'naive peak KB':>13} {'Strassen-32 peak KB':>19} {'ratio':>5} {'peak/n^2 (B)':>12} | "
          f"{'naive max err':>13} {'Strassen max err':>16}")
    for n in (64, 128, 256):
        A, B = rand_matrix(n, 9, floats=True), rand_matrix(n, 10, floats=True)
        exact = np.array(A) @ np.array(B)
        peaks, errs = [], []
        for fn in (lambda: naive_multiply(A, B), lambda: strassen_multiply(A, B, cutoff=32)):
            tracemalloc.start()
            out = fn()
            peaks.append(tracemalloc.get_traced_memory()[1] / 1024)
            tracemalloc.stop()
            errs.append(float(np.max(np.abs(np.array(out) - exact))))
        rows_e.append([n, round(peaks[0], 1), round(peaks[1], 1), f"{errs[0]:.3e}", f"{errs[1]:.3e}"])
        print(f"{n:>4} | {peaks[0]:>13,.0f} {peaks[1]:>19,.0f} {peaks[1] / peaks[0]:>5.2f} "
              f"{peaks[1] * 1024 / n ** 2:>12.0f} | {errs[0]:>13.2e} {errs[1]:>16.2e}")
    save_csv("m4_memory_and_error.csv", ["n", "naive_peak_kb", "strassen32_peak_kb", "naive_max_abs_err",
                                         "strassen32_max_abs_err"], rows_e)
    plot(rows_a, counted, rows_b, rows_c)
    print("\nCSV : Supporting_Files/results/m4_strassen_operations.csv, m4_strassen_time.csv, m4_cutoff_sweep.csv,")
    print("      m4_padding.csv, m4_memory_and_error.csv")
    print("PNG : Module_4_Strassen_Matrix_Multiplication/Report/graphs/m4_operations.png, m4_time.png")


def plot(rows_a, counted, rows_b, rows_c):
    ns = [r[0] for r in rows_a]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    ax1.loglog(ns, [r[1] for r in rows_a], "r-", label="naive 2n^3 - n^2 (formula)")
    ax1.loglog(ns, [r[2] for r in rows_a], "b-", label="pure Strassen (formula)")
    ax1.loglog(ns, [r[3] for r in rows_a], "g-", label="Strassen, cutoff 8 (formula)")
    run_n = [n for n in ns if (n, 1) in counted]
    ax1.loglog(run_n, [counted[n, 1] for n in run_n], "bo", label="pure Strassen (counted)")
    run8 = [n for n in ns if (n, 8) in counted]
    ax1.loglog(run8, [counted[n, 8] for n in run8], "gs", label="cutoff 8 (counted)")
    ax1.loglog(ns, [7 * n ** math.log2(7) for n in ns], "k:", label="7 n^2.807 (leading term)")
    ax1.set(title="Scalar operations vs n", xlabel="n (matrix order)", ylabel="multiplications + additions")
    for col, cut in ((2, 1), (3, 8), (4, 16), (5, 32)):
        ax2.semilogx(ns, [r[col] / r[1] for r in rows_a], "o-", label=f"Strassen cutoff {cut} / naive")
    ax2.axhline(1, color="r", ls="--", label="break-even (= naive)")
    ax2.set(title="Operation ratio Strassen / naive (crossover where < 1)", xlabel="n (matrix order)",
            ylabel="ratio of operations")
    for ax in (ax1, ax2):
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Module 4 - Strassen vs naive multiplication (operation counts)")
    fig.tight_layout()
    fig.savefig(GRAPHS / "m4_operations.png", dpi=150)
    plt.close(fig)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    bn = [r[0] for r in rows_b]
    ax1.loglog(bn, [r[1] for r in rows_b], "r^-", label="naive")
    for col, lab, mk in ((2, "pure Strassen", "bo-"), (3, "cutoff 16", "gs-"), (4, "cutoff 32", "md-"),
                         (5, "cutoff 64", "cv-")):
        pts = [(r[0], r[col]) for r in rows_b if r[col] != ""]
        ax1.loglog([p[0] for p in pts], [p[1] for p in pts], mk, label=lab)
    k = rows_b[-1][1] / bn[-1] ** 3
    ax1.loglog(bn, [k * n ** 3 for n in bn], "k:", label="c n^3 (fitted to naive)")
    ax1.set(title="Wall-clock time (Python)", xlabel="n (matrix order)", ylabel="time (s)")
    ax1.set_xticks(bn, [str(n) for n in bn])
    ax1.minorticks_off()
    cuts = [r[0] for r in rows_c]
    ax2.bar([str(c) for c in cuts], [r[3] for r in rows_c], color="tab:blue", label="time (s)")
    ax2.set(title="Cutoff sweep at n = 256", xlabel="cutoff n0 (naive below)", ylabel="time (s)")
    ax3 = ax2.twinx()
    ax3.plot([str(c) for c in cuts], [r[2] / 1e6 for r in rows_c], "ro-", label="operations (millions)")
    ax3.set_ylabel("operations (millions)")
    ax2.legend(loc="upper left", fontsize=8)
    ax3.legend(loc="upper right", fontsize=8)
    for ax in (ax1, ax2):
        ax.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)
    fig.suptitle("Module 4 - measured time and the choice of cutoff")
    fig.tight_layout()
    fig.savefig(GRAPHS / "m4_time.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
