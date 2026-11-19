"""Q6(b) - Memory of Meet-in-the-Middle and the time-memory trade-off (CSA06 DAA, Assignment 3 - CO3).

Question bullets answered with evidence:
  * "Analyse additional memory requirements"  - stored subset sums (exact count) and the measured peak memory
    (tracemalloc) of Meet-in-the-Middle against Gray-code brute force, n = 16 ... 32, extrapolated to n = 40/50/60;
  * "Explain the time-memory trade-off"      - best_fill_mitm_split stores only the 2^k sums of the first k parcels
    and enumerates the other n - k: memory 2^k sums, time ~ 3*2^k + k*2^(n-k) operations (k = n/2 is balanced).
Instances are the same as in q6_meet_in_the_middle.py (make_instance, seeded per n); every answer is checked
against the dynamic-programming reference.

Run:  py -3 q6_mitm_memory.py     (writes ../Meet_in_the_Middle/results/q6_mitm_memory.csv, q6_mitm_tradeoff.csv)
"""
import csv
import os
import time
import tracemalloc

from q6_meet_in_the_middle import (PackCounter, best_fill_brute_force, best_fill_dp, best_fill_mitm,
                                   best_fill_mitm_split, make_instance)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "Meet_in_the_Middle", "results")
MEM_SIZES = [16, 20, 24, 28, 32]
BF_MEM_SIZES = [16, 20]
TRADE_N = 26
TRADE_K = [8, 10, 12, 13, 14, 16, 18, 20]


def peak_bytes(fn):
    """Run fn() under tracemalloc; return (result, peak bytes allocated during the call)."""
    tracemalloc.start()
    tracemalloc.reset_peak()
    base = tracemalloc.get_traced_memory()[0]
    res = fn()
    peak = tracemalloc.get_traced_memory()[1] - base
    tracemalloc.stop()
    return res, peak


def main():
    os.makedirs(RESULTS, exist_ok=True)
    print("=" * 112)
    print("Q6(b) MEMORY OF MEET-IN-THE-MIDDLE (tracemalloc peak during one call) vs Gray-code brute force")
    print("=" * 112)
    rows = []
    print(f"{'n':>4} {'method':<22}{'stored sums':>13}{'2*2^(n/2)':>12}{'peak KiB':>12}{'bytes/sum':>11}"
          f"{'operations':>14}  = DP")
    print("-" * 100)
    for n in MEM_SIZES:
        weights, W = make_instance(n)
        ref = best_fill_dp(weights, W)
        jobs = [("MitM (both halves)", lambda c: best_fill_mitm(weights, W, c, "binary")[0])]
        if n in BF_MEM_SIZES:
            jobs.insert(0, ("brute force (Gray)", lambda c: best_fill_brute_force(weights, W, c)[0]))
        for name, job in jobs:
            c = PackCounter()
            best, peak = peak_bytes(lambda: job(c))
            per = peak / c.stored_sums if c.stored_sums else 0
            rows.append({"n": n, "method": name, "stored_sums": c.stored_sums, "theory_sums": 2 * 2 ** (n // 2)
                         if c.stored_sums else 0, "peak_bytes": peak, "bytes_per_stored_sum": round(per, 1),
                         "operations": c.total_ops(), "correct": best == ref})
            print(f"{n:>4} {name:<22}{c.stored_sums:>13,}{rows[-1]['theory_sums']:>12,}{peak / 1024:>12,.1f}"
                  f"{per:>11.1f}{c.total_ops():>14,}  {'yes' if best == ref else 'NO'}")
    with open(os.path.join(RESULTS, "q6_mitm_memory.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    per_sum = rows[-1]["bytes_per_stored_sum"]
    print(f"\nExtrapolated memory of MitM with {per_sum:.0f} bytes per stored sum (Python lists of int sums + masks, "
          f"measured at n = {MEM_SIZES[-1]})")
    print(f"{'n':>4}{'stored sums':>17}{'Python lists':>16}{'packed 8-byte array':>22}{'brute force':>14}")
    print("-" * 75)
    for n in (32, 40, 50, 60):
        sums = 2 * 2 ** (n // 2)
        print(f"{n:>4}{sums:>17,}{sums * per_sum / 2 ** 30:>13.2f} GiB{sums * 8 / 2 ** 30:>19.2f} GiB"
              f"{'O(n) ~ 0':>14}")

    # ------------------------------------------------------------------ time-memory trade-off
    weights, W = make_instance(TRADE_N)
    ref = best_fill_dp(weights, W)
    trows = []
    print(f"\nTIME-MEMORY TRADE-OFF at n = {TRADE_N}: store the sorted sums of k parcels, enumerate the other n - k")
    print(f"{'variant':<24}{'k':>4}{'stored sums':>13}{'enumerated':>12}{'operations':>13}{'3*2^k+k*2^(n-k)':>20}"
          f"{'time s':>9}{'peak KiB':>11}  = DP")
    print("-" * 112)
    for k in TRADE_K:
        c = PackCounter()
        t0 = time.perf_counter()
        best = best_fill_mitm_split(weights, W, k, c)
        t = time.perf_counter() - t0
        _, peak = peak_bytes(lambda: best_fill_mitm_split(weights, W, k, PackCounter()))
        model = 3 * 2 ** k + k * 2 ** (TRADE_N - k)    # generation ~3 ops per sum + k probes per subset
        trows.append({"variant": "store k, enumerate n-k", "n": TRADE_N, "k": k, "stored_sums": c.stored_sums,
                      "enumerated_subsets": c.subsets, "operations": c.total_ops(), "model_ops": model,
                      "time_s": round(t, 4), "peak_bytes": peak, "correct": best == ref})
        print(f"{'store k, enumerate n-k':<24}{k:>4}{c.stored_sums:>13,}{c.subsets:>12,}{c.total_ops():>13,}"
              f"{model:>20,}{t:>9.3f}{peak / 1024:>11,.1f}  {'yes' if best == ref else 'NO'}")
    c = PackCounter()
    t0 = time.perf_counter()
    best = best_fill_mitm(weights, W, c, "two_pointer")[0]
    t = time.perf_counter() - t0
    _, peak = peak_bytes(lambda: best_fill_mitm(weights, W, PackCounter(), "two_pointer"))
    trows.append({"variant": "both halves, two-pointer", "n": TRADE_N, "k": TRADE_N // 2,
                  "stored_sums": c.stored_sums, "enumerated_subsets": 0, "operations": c.total_ops(),
                  "model_ops": 8 * 2 ** (TRADE_N // 2), "time_s": round(t, 4), "peak_bytes": peak,
                  "correct": best == ref})
    print(f"{'both halves, two-pointer':<24}{TRADE_N // 2:>4}{c.stored_sums:>13,}{0:>12,}{c.total_ops():>13,}"
          f"{8 * 2 ** (TRADE_N // 2):>20,}{t:>9.3f}{peak / 1024:>11,.1f}  {'yes' if best == ref else 'NO'}")
    bf_ops = 2 * 2 ** TRADE_N
    print(f"{'brute force (k = 0)':<24}{0:>4}{0:>13,}{2 ** TRADE_N:>12,}{bf_ops:>13,}{bf_ops:>20,}"
          f"{'not run':>9}{'~0':>11}")
    with open(os.path.join(RESULTS, "q6_mitm_tradeoff.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(trows[0].keys()))
        w.writeheader()
        w.writerows(trows)
    best_row = min(trows[:-1], key=lambda r: r["operations"])
    print(f"\nFewest operations of the one-list variant at k = {best_row['k']} ({best_row['operations']:,}). Below k ~ n/2, "
          f"moving 2 parcels from 'enumerate'")
    print("to 'store' cuts the time ~4x and multiplies the memory by 4; above n/2 both time and memory grow.")
    print(f"All {len(rows) + len(trows)} runs agree with the DP reference: "
          f"{all(r['correct'] for r in rows + trows)}")
    print("CSV written: Meet_in_the_Middle/results/q6_mitm_memory.csv, q6_mitm_tradeoff.csv")


if __name__ == "__main__":
    main()
