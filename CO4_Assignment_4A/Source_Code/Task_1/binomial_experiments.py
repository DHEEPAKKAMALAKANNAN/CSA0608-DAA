"""
Task 1 - experiments: growth of the four binomial-coefficient algorithms.

E1  n = 6..24 (k = n // 2): naive calls vs 2C(n,k)-1, memo additions vs k(n-k), table additions vs
    (k-1)k/2 + k(n-k), and wall-clock times (median of 3 runs).
E2  n = 100..1600 (k = n // 2): bottom-up table vs single row (exact big integers) vs single row mod p,
    additions vs closed form, stored cells, times (median of 3) -> shows the Theta(nk) growth and the big-integer
    effect (C(n, n/2) has about 0.3n decimal digits, so one "addition" is no longer O(1)).
Outputs: results/binomial_E1.csv, results/binomial_E2.csv, ../../Report/Screenshots/task1_binomial_growth.png
Run:  py -3 binomial_experiments.py
"""
import csv
import os
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from binomial_dp import (binom_bottom_up, binom_memo, binom_naive, binom_one_row,  # noqa: E402
                         formula_bottom_up_additions)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.normpath(os.path.join(HERE, "..", "..", "Report", "Screenshots"))
MOD = 1_000_000_007


def timed(fn, *args, repeats=3, **kw):
    """Median wall-clock time (seconds) of `repeats` runs; also returns the last result."""
    times, res = [], None
    for _ in range(repeats):
        t0 = time.perf_counter()
        res = fn(*args, **kw)
        times.append(time.perf_counter() - t0)
    return statistics.median(times), res


def experiment_1():
    rows = []
    print("E1  naive vs memo vs bottom-up, k = n // 2 (times: median of 3 runs)")
    hdr = (f"  {'n':>3}{'k':>4}{'C(n,k)':>10}{'naive calls':>13}{'=2C-1?':>8}{'memo adds':>11}{'=k(n-k)?':>10}"
           f"{'table adds':>12}{'=formula?':>11}{'naive ms':>11}{'memo ms':>10}{'table ms':>10}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for n in range(6, 25, 2):
        k = n // 2
        t_naive, (v1, o1) = timed(binom_naive, n, k)
        t_memo, (v2, o2) = timed(binom_memo, n, k)
        t_tab, (v3, o3) = timed(binom_bottom_up, n, k)
        assert v1 == v2 == v3
        ok1 = o1["calls"] == 2 * v1 - 1
        ok2 = o2["additions"] == k * (n - k)
        ok3 = o3["additions"] == formula_bottom_up_additions(n, k)
        rows.append({"n": n, "k": k, "C": v1, "naive_calls": o1["calls"], "naive_additions": o1["additions"],
                     "memo_calls": o2["calls"], "memo_additions": o2["additions"],
                     "table_additions": o3["additions"], "naive_s": t_naive, "memo_s": t_memo, "table_s": t_tab})
        print(f"  {n:>3}{k:>4}{v1:>10}{o1['calls']:>13}{'yes' if ok1 else 'NO':>8}{o2['additions']:>11}"
              f"{'yes' if ok2 else 'NO':>10}{o3['additions']:>12}{'yes' if ok3 else 'NO':>11}"
              f"{t_naive*1e3:>11.2f}{t_memo*1e3:>10.3f}{t_tab*1e3:>10.3f}")
    r = rows[-1]["naive_calls"] / rows[-2]["naive_calls"]
    print(f"  naive calls grow by x{r:.2f} per +2 in n (-> 4 = 2^2, since C(n, n/2) ~ 2^n / sqrt(n)),")
    print("  while the DP additions grow only quadratically in n when k = n/2.")
    return rows


def experiment_2():
    rows = []
    print("\nE2  large n, k = n // 2: 2-D table vs single row (exact) vs single row mod p (median of 3 runs)")
    hdr = (f"  {'n':>5}{'k':>5}{'n*k':>9}{'additions':>11}{'formula':>10}{'digits':>7}{'2D cells':>10}"
           f"{'1D cells':>9}{'2D table s':>12}{'1-row s':>10}{'1-row mod p s':>15}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for n in (100, 200, 400, 800, 1600, 3200):
        k = n // 2
        t2d, (v2d, o2d) = timed(binom_bottom_up, n, k)
        t1d, (v1d, o1d) = timed(binom_one_row, n, k)
        tmod, (vmod, omod) = timed(binom_one_row, n, k, modulus=MOD)
        assert v2d == v1d and vmod == v1d % MOD
        assert o2d["additions"] == o1d["additions"] == omod["additions"] == formula_bottom_up_additions(n, k)
        rows.append({"n": n, "k": k, "nk": n * k, "additions": o1d["additions"], "digits": len(str(v1d)),
                     "cells_2d": o2d["cells"], "cells_1d": o1d["cells_stored"],
                     "table_s": t2d, "one_row_s": t1d, "one_row_mod_s": tmod})
        print(f"  {n:>5}{k:>5}{n*k:>9}{o1d['additions']:>11}{formula_bottom_up_additions(n, k):>10}"
              f"{len(str(v1d)):>7}{o2d['cells']:>10}{o1d['cells_stored']:>9}{t2d:>12.4f}{t1d:>10.4f}{tmod:>15.4f}")
    g_exact = rows[-1]["one_row_s"] / rows[-2]["one_row_s"]
    g_mod = rows[-1]["one_row_mod_s"] / rows[-2]["one_row_mod_s"]
    print(f"  last doubling of n (n*k x4): exact big-int time x{g_exact:.1f}, mod-p time x{g_mod:.1f}")
    print("  (unit-cost theory predicts x4; if every addition cost O(digits) the ratio would tend to x8)")
    return rows


def save_csv(rows, name):
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


def plot(e1, e2):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    n1 = [r["n"] for r in e1]
    ax1.semilogy(n1, [r["naive_calls"] for r in e1], "o-", label="naive recursion: calls")
    ax1.semilogy(n1, [r["naive_additions"] for r in e1], "s--", label="naive recursion: additions")
    ax1.semilogy(n1, [r["table_additions"] for r in e1], "^-", label="bottom-up table: additions")
    ax1.semilogy(n1, [r["memo_additions"] for r in e1], "v-", label="memoised: additions = k(n-k)")
    ax1.set_title("Operation counts for C(n, n/2)")
    ax1.set_xlabel("n (k = n/2)")
    ax1.set_ylabel("operations (log scale)")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)

    nk = [r["nk"] for r in e2]
    ax2.loglog(nk, [r["table_s"] for r in e2], "o-", label="2-D table (exact big integers)")
    ax2.loglog(nk, [r["one_row_s"] for r in e2], "s-", label="single row (exact big integers)")
    ax2.loglog(nk, [r["one_row_mod_s"] for r in e2], "^-", label="single row mod p (word-size)")
    scale = e2[0]["one_row_mod_s"] / nk[0]
    ax2.loglog(nk, [scale * x for x in nk], "k:", label="theory c * n*k (scaled)")
    ax2.set_title("Bottom-up time vs n*k (k = n/2)")
    ax2.set_xlabel("n * k (log scale)")
    ax2.set_ylabel("time in seconds (log scale)")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    path = os.path.join(SHOTS, "task1_binomial_growth.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main():
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    print("=" * 112)
    print(" TASK 1 - EXPERIMENTS: OVERLAPPING SUB-PROBLEMS AND THE GROWTH OF C(n, k) ALGORITHMS")
    print("=" * 112)
    e1 = experiment_1()
    e2 = experiment_2()
    print("\nSaved:", os.path.relpath(save_csv(e1, "binomial_E1.csv"), HERE), ",",
          os.path.relpath(save_csv(e2, "binomial_E2.csv"), HERE))
    print("Graph:", os.path.relpath(plot(e1, e2), HERE))


if __name__ == "__main__":
    main()
