"""Q2 experiments - Sequential Search comparisons by position, outcome and list size; operating boundary.

E1  successful searches at controlled positions (first, 25 %, middle, 75 %, last) and an unsuccessful search,
    for n = 50 ... 1 000 000 issued-tool records;
E2  average successful search: every position for n <= 5 000 (exact average), a random sample of targets above;
E3  time per comparison t_c from unsuccessful scans (median of repeats) - secondary evidence;
E4  operating boundary n_max(lambda) = min(L_max / t_c, U_max / (lambda * t_c)).
Writes results/q2_*.csv, small datasets to results/datasets/, and ../Output_Screenshots/q2_comparisons.png.
"""

import csv
import hashlib
import os
import random
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from sequential_search import make_tool_records, sequential_search  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")
SIZES = [50, 500, 5_000, 50_000, 500_000, 1_000_000]
SAMPLE_TARGETS = {50_000: 2000, 500_000: 200, 1_000_000: 100}   # random successful targets for large n
L_MAX = 0.050          # s   - worst-case latency allowed for one lookup (half of a 100 ms "instant" response)
U_MAX = 0.05           # CPU share of one core that lookups may use (5 %)
RATES = [0.1, 1, 10, 100, 1000]


def write_csv(name, rows):
    with open(os.path.join(RESULTS, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def save_dataset(records, n):
    """Small lists are saved in full; every list's Tool-ID sequence is fingerprinted in the manifest."""
    os.makedirs(os.path.join(RESULTS, "datasets"), exist_ok=True)
    if n <= 5_000:
        with open(os.path.join(RESULTS, "datasets", f"q2_tools_n{n}.csv"), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["tool_id", "technician_id", "issue_time", "work_bay"])
            w.writerows(records)
    digest = hashlib.sha256("|".join(r[0] for r in records).encode()).hexdigest()[:16]
    return {"n": n, "seed": 42 + n, "sha256_tool_ids_16": digest, "first_tool": records[0][0],
            "last_tool": records[-1][0], "saved_in_full": n <= 5_000}


def time_unsuccessful(records, repeats):
    """Median time (s) of one unsuccessful search; tiny lists are timed in a batch of 2 000 calls."""
    batch = 2000 if len(records) < 50_000 else 1
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        for _ in range(batch):
            sequential_search(records, "T-0")
        samples.append((time.perf_counter() - t0) / batch)
    return statistics.median(samples)


def main():
    pos_rows, avg_rows, time_rows, manifest = [], [], [], []
    per_position_5000 = []
    print("E1  COMPARISONS BY TARGET POSITION   (prediction: position p -> exactly p comparisons; absent -> n)")
    print(f"{'n':>10}{'first':>9}{'25 %':>10}{'middle':>10}{'75 %':>10}{'last':>11}{'absent':>11}  observed = predicted?")
    print("-" * 94)
    for n in SIZES:
        recs = make_tool_records(n)
        manifest.append(save_dataset(recs, n))
        positions = {"first": 1, "25 %": max(1, n // 4), "middle": (n + 1) // 2, "75 %": 3 * n // 4, "last": n}
        cells, all_ok = [], True
        for label, p in positions.items():
            idx, comp = sequential_search(recs, recs[p - 1][0])
            ok = idx == p - 1 and comp == p
            all_ok &= ok
            cells.append(comp)
            pos_rows.append({"n": n, "case": label, "position": p, "comparisons": comp, "predicted": p, "match": ok})
        idx, comp = sequential_search(recs, "T-0")
        ok = idx == -1 and comp == n
        all_ok &= ok
        pos_rows.append({"n": n, "case": "absent", "position": "", "comparisons": comp, "predicted": n, "match": ok})
        print(f"{n:>10,}" + "".join(f"{c:>{w},}" for c, w in zip(cells, (9, 10, 10, 10, 11)))
              + f"{comp:>11,}  {'yes' if all_ok else 'NO'}")

        # E2 average successful search
        if n <= 5_000:
            targets = [r[0] for r in recs]                       # every position once: exact average
            kind = "all positions"
        else:
            rng = random.Random(7 + n)
            targets = [recs[rng.randrange(n)][0] for _ in range(SAMPLE_TARGETS[n])]
            kind = f"{len(targets)} random"
        comps = [sequential_search(recs, t)[1] for t in targets]
        if n == 5_000:
            per_position_5000 = comps
        mean = statistics.fmean(comps)
        sd = statistics.stdev(comps) if len(comps) > 1 else 0.0
        avg_rows.append({"n": n, "targets": kind, "mean_comparisons": round(mean, 2),
                         "predicted_(n+1)/2": (n + 1) / 2, "ratio": round(mean / ((n + 1) / 2), 4),
                         "ci95_half_width": round(1.96 * sd / len(comps) ** 0.5, 1) if n > 5_000 else 0.0})

        # E3 timing of an unsuccessful search
        t = time_unsuccessful(recs, 5)
        time_rows.append({"n": n, "unsuccessful_search_ms": round(t * 1000, 4), "ns_per_comparison": round(t / n * 1e9, 2)})
        del recs

    print("\nE2  AVERAGE SUCCESSFUL SEARCH   (prediction: (n+1)/2 comparisons)")
    print(f"{'n':>10}{'targets used':>16}{'mean observed':>16}{'(n+1)/2':>13}{'ratio':>9}{'95% CI +/-':>13}")
    print("-" * 77)
    for r in avg_rows:
        print(f"{r['n']:>10,}{r['targets']:>16}{r['mean_comparisons']:>16,.1f}{r['predicted_(n+1)/2']:>13,.1f}"
              f"{r['ratio']:>9.4f}{r['ci95_half_width']:>13,.1f}")

    print("\nE3  TIME OF ONE UNSUCCESSFUL SEARCH (median of 5; secondary evidence)")
    print(f"{'n':>10}{'time (ms)':>14}{'ns / comparison':>18}")
    for r in time_rows:
        print(f"{r['n']:>10,}{r['unsuccessful_search_ms']:>14,.3f}{r['ns_per_comparison']:>18.1f}")
    t_c = statistics.median(r["ns_per_comparison"] for r in time_rows if r["n"] >= 50_000) * 1e-9
    print(f"t_c (median over n >= 50,000) = {t_c * 1e9:.1f} ns per comparison")

    print(f"\nE4  OPERATING BOUNDARY  latency: n*t_c <= {L_MAX * 1000:.0f} ms;  load: lambda*n*t_c <= {U_MAX:.0%} of a core"
          " (worst case n comparisons per lookup)")
    n_lat = L_MAX / t_c
    bound_rows = []
    print(f"{'lookups/s':>10}{'n_max (latency)':>18}{'n_max (load)':>15}{'n_max':>13}  binding constraint")
    for lam in RATES:
        n_load = U_MAX / (lam * t_c)
        n_max = min(n_lat, n_load)
        binding = "both" if abs(n_lat - n_load) < 1 else ("latency" if n_lat < n_load else "load")
        bound_rows.append({"lookups_per_s": lam, "n_max_latency": int(n_lat), "n_max_load": int(n_load),
                           "n_max": int(n_max), "binding": binding, "t_c_ns": round(t_c * 1e9, 2)})
        print(f"{lam:>10}{int(n_lat):>18,}{int(n_load):>15,}{int(n_max):>13,}  {binding}")

    os.makedirs(RESULTS, exist_ok=True)
    write_csv("q2_positions.csv", pos_rows)
    write_csv("q2_average.csv", avg_rows)
    write_csv("q2_timing.csv", time_rows)
    write_csv("q2_boundary.csv", bound_rows)
    write_csv("q2_datasets_manifest.csv", manifest)
    print("\nAll position / absent counts equal the prediction:", "YES" if all(r["match"] for r in pos_rows) else "NO")
    print("CSV  : results/q2_positions.csv, q2_average.csv, q2_timing.csv, q2_boundary.csv, q2_datasets_manifest.csv")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    ps = range(1, len(per_position_5000) + 1)
    axes[0].plot(ps, per_position_5000, color="#4C72B0", lw=2, label="successful: measured")
    axes[0].axhline(5000, color="#C44E52", ls="--", label="unsuccessful: n = 5,000")
    axes[0].axhline(5001 / 2, color="grey", ls=":", label="average (n+1)/2 = 2,500.5")
    axes[0].set_xlabel("position of the tool record in the list (1-based)")
    axes[0].set_ylabel("key comparisons")
    axes[0].set_title("n = 5,000: comparisons = position p")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=8)
    for case, style in (("first", "o-"), ("middle", "s-"), ("last", "^-"), ("absent", "x--")):
        ys = [r["comparisons"] for r in pos_rows if r["case"] == case]
        axes[1].plot(SIZES, ys, style, label=f"{case} (measured)")
    axes[1].plot(SIZES, [r["mean_comparisons"] for r in avg_rows], "d:", label="average successful (measured)")
    axes[1].plot(SIZES, SIZES, color="grey", lw=6, alpha=0.25, label="theory: n")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("number of active records n (log)")
    axes[1].set_ylabel("key comparisons (log)")
    axes[1].set_title("Growth with list size")
    axes[1].grid(True, which="both", alpha=0.3)
    axes[1].legend(fontsize=8)
    fig.suptitle("Q2 - Sequential Search comparison counts (tool-tracking list)")
    fig.tight_layout()
    fig.savefig(os.path.join(SHOTS, "q2_comparisons.png"), dpi=150)
    plt.close(fig)
    print("Graph: ../Output_Screenshots/q2_comparisons.png")


if __name__ == "__main__":
    main()
