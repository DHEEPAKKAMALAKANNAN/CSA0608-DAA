"""
Task 6.5 - State-space growth of the Held-Karp DP (and Task 6.6 extrapolation to 200 locations).

For n = 4, 5, 6, ... delivery locations (seeded random symmetric instances, seed 42) the program first PRINTS its
prediction (states n*2^(n-1), transitions n(n-1)*2^(n-2)+n, time scaled from the previous n by the ratio of
n^2*2^n), then runs the DP and prints the measured states, transitions, best-of-k wall time, tracemalloc peak
memory and the size of the DP + parent tables.  The exhaustive search (n! routes) is timed up to n = 9.
It stops at n = 16 (n = 16 already needs ~7 s per DP run and ~25 s under tracemalloc, all in pure Python;
every extra location multiplies the work by ~2.2).
Writes results/t6_state_growth.csv, results/t6_extrapolation.csv and the graph t6_state_growth.png
(in results/ and Report/Screenshots/).
Run:  py -3 tsp_state_growth.py
"""
import csv
import math
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import tsp_held_karp as hk  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "..", "Report", "Screenshots")
N_VALUES = list(range(4, 17))
EXHAUSTIVE_MAX_N = 9


def repeats_for(n):
    return 5 if n <= 12 else (3 if n <= 14 else 2)


def time_exhaustive(cost):
    t0 = time.perf_counter()
    best, _, tried = hk.exhaustive_tsp(cost)
    return time.perf_counter() - t0, best, tried


def draw(rows):
    ns = [r["n"] for r in rows]
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    ax = axes[0]
    ax.semilogy(ns, [r["states"] for r in rows], "o-", label="DP states evaluated (measured)")
    ax.semilogy(ns, [r["transitions"] for r in rows], "s-", label="DP transitions examined (measured)")
    ax.semilogy(ns, [n * n * 2 ** n / 4 for n in ns], "k--", label="theory n²·2ⁿ / 4")
    ax.semilogy(ns, [math.factorial(n) for n in ns], "^:", color="tab:red", label="routes n! (exhaustive)")
    ax.set(title="Work: DP states / transitions vs n! routes", xlabel="delivery locations n",
           ylabel="count (log scale)")
    ax2 = axes[1]
    ax2.semilogy(ns, [r["time_s"] for r in rows], "o-", label="Held-Karp DP (best of k runs)")
    ex = [r for r in rows if r["exhaustive_s"] != ""]
    ax2.semilogy([r["n"] for r in ex], [r["exhaustive_s"] for r in ex], "^-", color="tab:red",
                 label="exhaustive n! (measured)")
    c = rows[-1]["time_s"] / (ns[-1] ** 2 * 2 ** ns[-1])
    ax2.semilogy(ns, [c * n * n * 2 ** n for n in ns], "k--", label=f"c·n²·2ⁿ (fitted at n = {ns[-1]})")
    ax2.set(title="Execution time", xlabel="delivery locations n", ylabel="time (s, log scale)")
    ax3 = axes[2]
    ax3.semilogy(ns, [r["peak_mib"] for r in rows], "o-", color="tab:green", label="tracemalloc peak (MiB)")
    ax3.semilogy(ns, [r["table_cells"] * 8 / 2 ** 20 for r in rows], "k--",
                 label="table cells × 8 B (pointer slots only)")
    ax3.set(title="Memory", xlabel="delivery locations n", ylabel="MiB (log scale)")
    for a in axes:
        a.grid(True, which="both", alpha=0.3)
        a.legend(fontsize=8)
    fig.suptitle("Task 6.5 - Held-Karp state-space growth (random symmetric instances, seed 42)", fontweight="bold")
    fig.tight_layout()
    for folder in (RESULTS, SHOTS):
        fig.savefig(os.path.join(folder, "t6_state_growth.png"), dpi=150)
    plt.close(fig)


def main():
    print("TASK 6.5 - STATE-SPACE GROWTH OF THE HELD-KARP DP")
    print("=" * 122)
    print("Prediction columns are printed BEFORE each run; measured columns follow on the same line.")
    print(f"{'':>3} | {'---------- PREDICTION ----------':^34} | "
          f"{'---------------------- MEASURED ----------------------':^58} | {'exhaustive':>10}")
    print(f"{'n':>3} | {'states':>9} {'transitions':>11} {'time (s)':>11} | {'states':>9} {'transitions':>11} "
          f"{'time (s)':>9} {'peak MiB':>9} {'table cells':>11} {'opt':>4} | {'n! time s':>10}")
    rng, rows, prev = random.Random(42), [], None
    for n in N_VALUES:
        cost = hk.random_cost_matrix(n, rng, symmetric=True)
        p_states, p_trans = hk.predicted_states(n), hk.predicted_transitions(n)
        p_time = "-" if prev is None else f"{prev['time_s'] * (n * n * 2 ** n) / (prev['n'] ** 2 * 2 ** prev['n']):.4f}"
        print(f"{n:>3} | {p_states:>9,} {p_trans:>11,} {p_time:>11} | ", end="", flush=True)
        m = hk.measure_held_karp(cost, repeats_for(n))
        ex_s = ""
        if n <= EXHAUSTIVE_MAX_N:
            ex_s, ex_best, _ = time_exhaustive(cost)
            assert ex_best == m["cost"], "DP disagrees with exhaustive search"
        row = dict(n=n, predicted_states=p_states, predicted_transitions=p_trans,
                   predicted_time_s=p_time, states=m["states"], transitions=m["transitions"],
                   time_s=round(m["time_s"], 6), peak_mib=round(m["peak_bytes"] / 2 ** 20, 3),
                   table_cells=m["table_cells"], optimum=m["cost"], routes_n_factorial=math.factorial(n),
                   exhaustive_s=round(ex_s, 4) if ex_s != "" else "")
        rows.append(row)
        prev = row
        ex_txt = f"{ex_s:>10.3f}" if ex_s != "" else f"{'(skipped)':>10}"
        print(f"{row['states']:>9,} {row['transitions']:>11,} {row['time_s']:>9.4f} {row['peak_mib']:>9.2f} "
              f"{row['table_cells']:>11,} {row['optimum']:>4} | {ex_txt}")
    with open(os.path.join(RESULTS, "t6_state_growth.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    draw(rows)

    last, before = rows[-1], rows[-2]
    sec_per_trans = last["time_s"] / last["transitions"]
    bytes_per_cell = last["peak_mib"] * 2 ** 20 / last["table_cells"]
    ratio = {k: last[k] / before[k] for k in ("states", "transitions", "time_s", "peak_mib")}
    print(f"\nGrowth per extra location (n = {before['n']} -> {last['n']}): states x{ratio['states']:.2f}, "
          f"transitions x{ratio['transitions']:.2f}, time x{ratio['time_s']:.2f}, memory x{ratio['peak_mib']:.2f}")
    print(f"Measured constants at n = {last['n']}: {sec_per_trans * 1e9:.0f} ns per transition, "
          f"{bytes_per_cell:.1f} bytes per table cell.")
    print(f"Stopped at n = {last['n']}: n = {last['n'] + 1} would need ~2.2x the time and ~2.1x the memory "
          f"again (pure Python).")
    print("\nEXTRAPOLATION with the measured constants (Task 6.6 - not run)")
    print(f"{'n':>4} {'subsets 2^n':>12} {'DP states':>12} {'transitions':>12} {'projected time':>18} "
          f"{'projected memory':>18}")
    ext = []
    for n in (20, 25, 30, 40, 50, 200):
        trans, states = hk.predicted_transitions(n), hk.predicted_states(n)
        secs, mem = trans * sec_per_trans, 2 * (2 ** n) * (n + 1) * bytes_per_cell
        years = secs / (3600 * 24 * 365)
        t_txt = f"{secs:,.0f} s" if secs < 1e5 else (f"{secs / 86400:,.0f} days" if years < 1 else f"{years:.2e} years")
        m_txt = f"{mem / 2 ** 30:,.1f} GiB" if mem < 2 ** 50 else f"{mem:.2e} bytes"
        print(f"{n:>4} {2 ** n:>12.3e} {states:>12.3e} {trans:>12.3e} {t_txt:>18} {m_txt:>18}")
        ext.append(dict(n=n, subsets=f"{2 ** n:.4e}", states=f"{states:.4e}", transitions=f"{trans:.4e}",
                        projected_seconds=f"{secs:.4e}", projected_bytes=f"{mem:.4e}"))
    with open(os.path.join(RESULTS, "t6_extrapolation.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ext[0]))
        w.writeheader()
        w.writerows(ext)
    print("\nwritten: results/t6_state_growth.csv, results/t6_extrapolation.csv, t6_state_growth.png")


if __name__ == "__main__":
    main()
