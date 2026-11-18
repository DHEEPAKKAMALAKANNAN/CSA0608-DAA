"""Q3 experiments - how text/pattern structure, not just input size, drives brute-force matching work.

S1  size sweep     : n = 1 000, 10 000, 100 000, 1 000 000 for the three designed conditions (m = 38);
S2  pattern sweep  : n = 100 000, m = 2, 4, 8, ..., 128 for C1 (rare first character) and C2 (A...AB in A...A).
Every observed count is printed next to its prediction.  Writes results/q3_size_sweep.csv,
results/q3_pattern_sweep.csv and the graphs ../Output_Screenshots/q3_conditions_bar.png, q3_growth.png.
"""

import csv
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from brute_force_string_match import SIG_IOC, brute_force_match, conditions  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")
SIZES = [1_000, 10_000, 100_000, 1_000_000]
PATTERN_LENGTHS = [2, 4, 8, 16, 32, 64, 128]


def write_csv(name, rows):
    with open(os.path.join(RESULTS, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def size_sweep():
    rows = []
    print("S1  SIZE SWEEP (m = 38)        prediction: C1 = n-m+1, C2 = m(n-m+1), C3 ~ 1.0-1.3 (n-m+1)")
    print(f"{'n':>11}{'C1 observed':>14}{'C2 observed':>14}{'C2 predicted':>14}{'C3 observed':>14}"
          f"{'C3/(n-m+1)':>12}{'C2/C1':>8}")
    print("-" * 87)
    for n in SIZES:
        obs = {}
        for name, _, text, pattern, predict in conditions(n):
            pred, _ = predict(text, pattern)
            t0 = time.perf_counter()
            matches, comp = brute_force_match(text, pattern)
            ms = (time.perf_counter() - t0) * 1000
            obs[name[:2]] = (comp, pred)
            rows.append({"n": n, "condition": name, "m": len(pattern), "predicted": pred, "observed": comp,
                         "per_shift": round(comp / (n - len(pattern) + 1), 4), "matches": len(matches),
                         "time_ms": round(ms, 2)})
        shifts = n - 38 + 1
        print(f"{n:>11,}{obs['C1'][0]:>14,}{obs['C2'][0]:>14,}{obs['C2'][1]:>14,}{obs['C3'][0]:>14,}"
              f"{obs['C3'][0] / shifts:>12.3f}{obs['C2'][0] / obs['C1'][0]:>8.1f}")
    return rows


def pattern_sweep(n=100_000):
    rows = []
    log = conditions(n)[0][2]
    print(f"\nS2  PATTERN-LENGTH SWEEP (n = {n:,})   prediction: C1 = n-m+1 (flat), C2 = m(n-m+1) (grows with m)")
    print(f"{'m':>6}{'C1 observed':>14}{'C1 predicted':>14}{'C2 observed':>14}{'C2 predicted':>14}{'C2/C1':>9}  pred=obs")
    print("-" * 82)
    for m in PATTERN_LENGTHS:
        p1 = (SIG_IOC * 4)[:m]                       # starts with '#', which never occurs in the log
        p2 = "A" * (m - 1) + "B"
        _, c1 = brute_force_match(log, p1)
        _, c2 = brute_force_match("A" * n, p2)
        e1, e2 = n - m + 1, m * (n - m + 1)
        rows.append({"n": n, "m": m, "C1_observed": c1, "C1_predicted": e1, "C2_observed": c2, "C2_predicted": e2})
        print(f"{m:>6}{c1:>14,}{e1:>14,}{c2:>14,}{e2:>14,}{c2 / c1:>9.1f}  {'yes' if (c1, c2) == (e1, e2) else 'NO'}")
    return rows


def plot(size_rows, pat_rows):
    colors = {"C1": "#55A868", "C2": "#C44E52", "C3": "#4C72B0"}
    # bar chart of the three conditions at n = 100 000
    sel = [r for r in size_rows if r["n"] == 100_000]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    names = [r["condition"] for r in sel]
    vals = [r["observed"] for r in sel]
    bars = ax.bar(names, vals, color=[colors[nm[:2]] for nm in names])
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.15, f"{v:,}", ha="center", fontsize=9)
    shifts = 100_000 - 38 + 1
    ax.axhline(shifts, color="grey", ls=":", label=f"lower bound n-m+1 = {shifts:,}")
    ax.axhline(38 * shifts, color="black", ls="--", label=f"upper bound m(n-m+1) = {38 * shifts:,}")
    ax.set_yscale("log")
    ax.set_ylim(5e4, 1.2e7)
    ax.set_ylabel("character comparisons (log)")
    ax.set_title("Q3 - Same n = 100,000 and m = 38, very different work")
    ax.grid(True, axis="y", which="both", alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(SHOTS, "q3_conditions_bar.png"), dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    for key in ("C1", "C2", "C3"):
        rs = [r for r in size_rows if r["condition"].startswith(key)]
        axes[0].plot([r["n"] for r in rs], [r["observed"] for r in rs], "o-", color=colors[key],
                     label=rs[0]["condition"])
    axes[0].plot(SIZES, [n - 37 for n in SIZES], "k:", lw=1, label="theory n-m+1")
    axes[0].plot(SIZES, [38 * (n - 37) for n in SIZES], "k--", lw=1, label="theory m(n-m+1)")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("text length n (characters, log)")
    axes[0].set_ylabel("character comparisons (log)")
    axes[0].set_title("Linear in n for every condition - but slopes differ by m")
    axes[0].grid(True, which="both", alpha=0.3)
    axes[0].legend(fontsize=8)
    ms = [r["m"] for r in pat_rows]
    axes[1].plot(ms, [r["C1_observed"] for r in pat_rows], "o-", color=colors["C1"], label="C1 observed")
    axes[1].plot(ms, [r["C2_observed"] for r in pat_rows], "s-", color=colors["C2"], label="C2 observed")
    axes[1].plot(ms, [r["C2_predicted"] for r in pat_rows], "k--", lw=1, label="m(n-m+1)")
    axes[1].set_xscale("log", base=2)
    axes[1].set_yscale("log")
    axes[1].set_xlabel("pattern length m (log2)")
    axes[1].set_ylabel("character comparisons (log)")
    axes[1].set_title("n = 100,000: work vs pattern length")
    axes[1].grid(True, which="both", alpha=0.3)
    axes[1].legend(fontsize=8)
    fig.suptitle("Q3 - Brute-force string matching: growth with n and with m")
    fig.tight_layout()
    fig.savefig(os.path.join(SHOTS, "q3_growth.png"), dpi=150)
    plt.close(fig)


def main():
    size_rows = size_sweep()
    pat_rows = pattern_sweep()
    write_csv("q3_size_sweep.csv", size_rows)
    write_csv("q3_pattern_sweep.csv", pat_rows)
    plot(size_rows, pat_rows)
    print("\nCSV  : results/q3_size_sweep.csv, results/q3_pattern_sweep.csv")
    print("Graph: ../Output_Screenshots/q3_conditions_bar.png, q3_growth.png")


if __name__ == "__main__":
    main()
