"""SwiftLogix CO3 case study - production-workload calculations (Part 4 / Part 6) and cross-module graphs.

Assumed production workloads (reconstructed paper) and machine model
    M1  5,000,000 shipment events per night, 64-byte records, delivered as 64 time-ordered hub feeds
    M2  2,000,000 open orders per dispatch cycle, priority scores 0..100 (k = 101 distinct values)
    M3  10,000,000 tracking IDs in the index, 20,000,000 lookups per day, 16-byte entries (ID + offset)
    M4  1,024 x 1,024 route-demand and cost matrices (8-byte reals), 96 forecasts per day
    Server: 10^8 basic operations per second;  1 MB = 10^6 bytes.
Operation counts use the closed forms of Part 4; the two empirical constants (3-way quick sort on
duplicate-heavy scores, guarded interpolation probes) are read from the experiment CSVs.

Run:  py -3 production_workload.py      (needs the CSVs written by the four *_experiments.py scripts)
"""
import csv
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = HERE / "results"
GRAPHS = ROOT / "Final_Design_and_Analysis" / "graphs"
sys.path.insert(0, str(ROOT / "Module_4_Strassen_Matrix_Multiplication" / "Source_Code"))
from strassen import strassen_ops  # noqa: E402

OPS = 1e8
MB = 1e6
N1, REC1, KEY1, IDX1, FEEDS = 5_000_000, 64, 8, 4, 64
N2, K2, REC2 = 2_000_000, 101, 8
N3, Q3, ENT3, PEAK_QPS, MISS_NS = 10_000_000, 20_000_000, 16, 2_000, 100
N4, ELEM4, RUNS4 = 1024, 8, 96


def read_csv(name):
    with open(RESULTS / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def secs(ops):
    return ops / OPS


def fmt_t(s):
    if s < 1:
        return f"{s * 1000:,.1f} ms"
    if s < 3600:
        return f"{s:,.2f} s"
    if s < 86400 * 2:
        return f"{s / 3600:,.2f} h"
    return f"{s / 86400:,.1f} days"


def binary_totals(n):
    """Exact S(n) and E(n) of the binary-search decision tree (iterative, memoised by size)."""
    sizes, stack = {}, [n]
    while stack:
        m = stack.pop()
        if m in sizes or m == 0:
            continue
        left = (m - 1) // 2
        kids = [k for k in (left, m - 1 - left) if k and k not in sizes]
        if kids:
            stack.append(m)
            stack.extend(kids)
            continue
        s = m + sum(sizes.get(k, (0, 0))[0] for k in (left, m - 1 - left))
        e = m + 1 + sum(sizes.get(k, (0, 0))[1] for k in (left, m - 1 - left))
        sizes[m] = (s, e)
    return sizes[n]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = []

    def add(module, design, ops, mem_mb, note):
        rows.append([module, design, f"{ops:.0f}", f"{secs(ops):.6f}", f"{mem_mb:.1f}", note])
        print(f"  {design:<44} {ops:>19,.0f} {fmt_t(secs(ops)):>11} {mem_mb:>8,.1f}  {note}")

    hdr = f"  {'design':<44} {'basic operations':>19} {'time':>11} {'MB':>8}  note"
    print("=" * 120)
    print("Production-workload estimates (closed forms of Part 4; 10^8 basic operations per second; 1 MB = 10^6 B)")
    print("=" * 120)

    # ---------------------------------------------------------------- M1
    lg = math.ceil(math.log2(N1))
    print(f"M1 merge sort - n = {N1:,} events/night, {REC1}-byte records, {FEEDS} hub feeds  (ceil(lg n) = {lg})")
    print(hdr)
    add("M1", "insertion sort, average n(n-1)/4", N1 * (N1 - 1) / 4, N1 * REC1 / MB, "comparisons; infeasible")
    worst = N1 * lg - 2 ** lg + 1
    add("M1", "top-down merge sort, worst comparisons", worst, 2 * N1 * REC1 / MB, "records + n-record buffer")
    add("M1", "  + record moves 2n*ceil(lg n)", worst + 2 * N1 * lg, 2 * N1 * REC1 / MB, "comparisons + moves")
    nat = (N1 - 1) + N1 * math.ceil(math.log2(FEEDS))
    add("M1", "natural merge sort on 64 feeds (cmp)", nat, 2 * N1 * (KEY1 + IDX1) / MB, "(key, index) pairs")
    add("M1", "  + moves 2n*lg 64", nat + 2 * N1 * 6, 2 * N1 * (KEY1 + IDX1) / MB, "final design")

    # ---------------------------------------------------------------- M2
    lg2 = math.log2(N2)
    h = sum(1 / k for k in range(1, N2 + 1))
    print(f"\nM2 quick sort - n = {N2:,} orders per cycle, scores 0..100 (k = {K2}),  lg n = {lg2:.2f}")
    print(hdr)
    add("M2", "baseline Lomuto, sorted/all-equal n(n-1)/2", N2 * (N2 - 1) / 2, N2 * REC2 / MB + N2 * 100 / MB,
        "depth n: 2M stack frames")
    add("M2", "baseline Lomuto, duplicate scores n^2/(2k)", N2 ** 2 / (2 * K2), N2 * REC2 / MB, "measured model, Exp C")
    add("M2", "baseline, random distinct keys 2(n+1)H_n-4n", 2 * (N2 + 1) * h - 4 * N2, N2 * REC2 / MB,
        "expected ~1.386 n lg n")
    qs = [r for r in read_csv("m2_quick_sort_experiments.csv") if r["distribution"] == "scores" and
          r["variant"] == "hybrid"]
    big = max(qs, key=lambda r: int(r["n"]))
    c_hyb = int(big["comparisons"]) / (int(big["n"]) * math.log2(K2))
    add("M2", f"hybrid (3-way) on scores {c_hyb:.3f} n lg k", c_hyb * N2 * math.log2(K2), N2 * REC2 / MB,
        f"from n = {int(big['n']):,}; final design")
    print(f"  stack: hybrid <= lg n = {math.ceil(lg2)} frames; baseline worst = {N2 - 1:,} frames")

    # ---------------------------------------------------------------- M3
    s_tot, e_tot = binary_totals(N3)
    worst3 = N3.bit_length()
    print(f"\nM3 binary search - index n = {N3:,} IDs, {Q3:,} lookups/day, peak {PEAK_QPS:,}/s  "
          f"(floor(lg n) + 1 = {worst3})")
    print(hdr)
    add("M3", "linear search, (n+1)/2 per hit x Q/day", Q3 * (N3 + 1) / 2, N3 * ENT3 / MB, "per day; infeasible")
    add("M3", "binary search, worst 24 per lookup x Q", Q3 * worst3, N3 * ENT3 / MB, "per day (CPU)")
    add("M3", f"binary search, average hit {s_tot / N3:.3f} x Q", Q3 * s_tot / N3, N3 * ENT3 / MB,
        f"S(n)/n exact; miss {e_tot / (N3 + 1):.3f}")
    gi = read_csv("m3_search_comparisons.csv")[-1]
    scale = math.log2(math.log2(N3)) / math.log2(math.log2(int(gi["n"])))
    g_probes = float(gi["guarded_uniform_probes"]) * scale
    g_cmp = float(gi["guarded_uniform"]) * scale
    add("M3", f"guarded interpolation ~{g_cmp:.1f} cmp/lookup x Q", Q3 * g_cmp, N3 * ENT3 / MB,
        f"~{g_probes:.1f} probes vs {worst3}")
    add("M3", "hash index (dict), ~1.5 probes x Q", Q3 * 1.5, 2 * N3 * ENT3 / MB, "load 0.5; no range queries")
    rebuild = N3 * math.ceil(math.log2(N3)) - 2 ** math.ceil(math.log2(N3)) + 1
    add("M3", "nightly index rebuild (merge sort, worst)", rebuild, 2 * N3 * ENT3 / MB, "runs in Module 1 window")
    cpu_cap = OPS / worst3
    mem_cap = 1e9 / (worst3 * MISS_NS)
    print(f"  capacity per core: CPU-bound {cpu_cap:,.0f} lookups/s; cache-miss-bound ({MISS_NS} ns/probe) "
          f"{mem_cap:,.0f} lookups/s;")
    print(f"  the assumed peak of {PEAK_QPS:,} lookups/s uses {PEAK_QPS / mem_cap:.2%} of one core")

    # ---------------------------------------------------------------- M4
    naive = 2 * N4 ** 3 - N4 ** 2
    print(f"\nM4 Strassen - n = {N4:,}, {RUNS4} forecasts/day, 8-byte reals  (inputs + output = 3n^2 words)")
    print(hdr)
    base_mem = 3 * N4 ** 2 * ELEM4 / MB
    str_mem = (2 + 5.75) * N4 ** 2 * ELEM4 / MB
    add("M4", "naive product 2n^3 - n^2", naive, base_mem, f"{fmt_t(secs(naive) * RUNS4)}/day")
    pm, pa = strassen_ops(N4, 1)
    add("M4", "pure Strassen 7n^2.807 - 6n^2", pm + pa, str_mem, f"{pm:,} mults")
    for cut in (8, 64):
        m, a = strassen_ops(N4, cut)
        add("M4", f"hybrid Strassen, cutoff {cut}", m + a, str_mem,
            ("op-optimal" if cut == 8 else "time-tuned (Python)") + f"; {fmt_t(secs(m + a) * RUNS4)}/day")
    m_w, a_w = winograd_ops(N4, 8)
    add("M4", "Strassen-Winograd (15 adds), cutoff 8", m_w + a_w, str_mem, "formula only (next step)")
    print(f"  Strassen live workspace ~ 5.75 n^2 words = {5.75 * N4 ** 2 * ELEM4 / MB:.1f} MB "
          f"(S(n) = S(n/2) + 16(n/2)^2 while recursing,")
    print("  23(n/2)^2 = 5.75 n^2 at the top-level combine) + 2 n^2 words of input")

    for folder in (RESULTS, GRAPHS):
        with open(folder / "production_workload.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["module", "design", "basic_operations", "seconds_at_1e8_ops", "memory_MB", "note"])
            w.writerows(rows)
    plot(rows)
    print("\nCSV : Supporting_Files/results/production_workload.csv (+ copy in Final_Design_and_Analysis/graphs)")
    print("PNG : Final_Design_and_Analysis/graphs/final_production_time.png, final_memory.png, "
          "final_theory_vs_experiment.png")


def winograd_ops(n, cutoff):
    if n <= cutoff:
        return n ** 3, n * n * (n - 1)
    m, a = winograd_ops(n // 2, cutoff)
    return 7 * m, 7 * a + 15 * (n // 2) ** 2


def plot(rows):
    pick = {"M1": ["insertion sort, average n(n-1)/4", "  + record moves 2n*ceil(lg n)", "  + moves 2n*lg 64"],
            "M2": ["baseline Lomuto, sorted/all-equal n(n-1)/2", "baseline Lomuto, duplicate scores n^2/(2k)",
                   None],
            "M3": ["linear search, (n+1)/2 per hit x Q/day", "binary search, worst 24 per lookup x Q", None],
            "M4": ["naive product 2n^3 - n^2", "pure Strassen 7n^2.807 - 6n^2", "hybrid Strassen, cutoff 8"]}
    final_names = {"M2": None, "M3": None}
    for r in rows:
        if r[0] == "M2" and r[1].startswith("hybrid"):
            final_names["M2"] = r[1]
        if r[0] == "M3" and r[1].startswith("guarded"):
            final_names["M3"] = r[1]
    pick["M2"][2], pick["M3"][2] = final_names["M2"], final_names["M3"]
    lookup = {(r[0], r[1]): r for r in rows}
    labels = ["brute force / worst case", "D&C as designed in Part 2", "final improved design"]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    mods = list(pick)
    for i, lab in enumerate(labels):
        vals = [float(lookup[m, pick[m][i]][3]) for m in mods]
        xs = [k + (i - 1) * 0.27 for k in range(len(mods))]
        bars = ax.bar(xs, vals, 0.27, label=lab)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v * 1.3, fmt_t(v), ha="center", fontsize=7, rotation=90)
    ax.set_yscale("log")
    ax.set_xticks(range(len(mods)), ["M1 nightly sort\n(5M events)", "M2 ranking\n(2M scores, k=101)",
                                     "M3 lookups/day\n(20M on 10M IDs)", "M4 forecast\n(1,024 x 1,024)"])
    ax.set(title="Estimated production time per job at 10^8 basic operations/s (log scale)",
           ylabel="time (s, log scale)", xlabel="module")
    ax.grid(True, axis="y", which="both", alpha=0.3)
    ax.set_ylim(top=ax.get_ylim()[1] * 30)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(GRAPHS / "final_production_time.png", dpi=150)
    plt.close(fig)

    mem = {"M1": [2 * N1 * REC1 / MB, 2 * N1 * (KEY1 + IDX1) / MB],
           "M2": [N2 * REC2 / MB + (N2 - 1) * 100 / MB, N2 * REC2 / MB],
           "M3": [2 * N3 * ENT3 / MB, N3 * ENT3 / MB],
           "M4": [3 * N4 ** 2 * ELEM4 / MB, (2 + 5.75) * N4 ** 2 * ELEM4 / MB]}
    notes = {"M1": ["records + buffer", "(key, idx) + buffer"], "M2": ["array + worst stack", "array, lg n stack"],
             "M3": ["hash index", "sorted array"], "M4": ["naive", "Strassen n0=8"]}
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, lab in enumerate(["alternative / as built", "final design"]):
        xs = [k + (i - 0.5) * 0.36 for k in range(4)]
        bars = ax.bar(xs, [mem[m][i] for m in mem], 0.36, label=lab)
        for b, m in zip(bars, mem):
            ax.text(b.get_x() + b.get_width() / 2, mem[m][i] + 8, f"{mem[m][i]:.0f} MB\n{notes[m][i]}", ha="center",
                    fontsize=7)
    ax.set_xticks(range(4), ["M1 merge sort", "M2 quick sort", "M3 binary search", "M4 Strassen"])
    ax.set(title="Memory requirement at the production sizes", ylabel="memory (MB = 10^6 bytes)", xlabel="module")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(GRAPHS / "final_memory.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    m1 = [r for r in read_csv("m1_merge_sort_experiments.csv") if r["distribution"] == "random"
          and r["algorithm"] == "top_down"]
    ns = [int(r["n"]) for r in m1]
    axes[0, 0].semilogx(ns, [int(r["comparisons"]) / (n * math.log2(n)) for r, n in zip(m1, ns)], "o-",
                        label="counted / (n log2 n)")
    axes[0, 0].semilogx(ns, [(n * math.log2(n) - 1.2645 * n) / (n * math.log2(n)) for n in ns], "k--",
                        label="theory (n lg n - 1.26 n) / (n lg n)")
    axes[0, 0].set(title="M1 merge sort, random keys", ylabel="ratio")
    m2 = [r for r in read_csv("m2_quick_sort_experiments.csv") if r["distribution"] == "random"
          and r["variant"] == "last"]
    ns2 = [int(r["n"]) for r in m2]
    exp2 = [2 * (n + 1) * sum(1 / k for k in range(1, n + 1)) - 4 * n for n in ns2]
    axes[0, 1].semilogx(ns2, [int(r["comparisons"]) / e for r, e in zip(m2, exp2)], "o-",
                        label="counted / (2(n+1)H_n - 4n)")
    axes[0, 1].axhline(1, color="k", ls="--", label="theory = 1")
    axes[0, 1].set(title="M2 quick sort (baseline), random keys", ylabel="ratio")
    m3 = read_csv("m3_binary_search_exact.csv")
    ns3 = [int(r["n"]) for r in m3]
    axes[1, 0].semilogx(ns3, [float(r["avg_success_counted"]) for r in m3], "o-", label="average hit (counted)")
    axes[1, 0].semilogx(ns3, [int(r["max_success"]) for r in m3], "s-", label="worst hit (counted)")
    axes[1, 0].semilogx(ns3, [math.log2(n) - 1 for n in ns3], "k--", label="theory lg n - 1")
    axes[1, 0].semilogx(ns3, [math.floor(math.log2(n)) + 1 for n in ns3], "r:", label="theory floor(lg n) + 1")
    axes[1, 0].set(title="M3 binary search", ylabel="comparisons per lookup")
    m4 = read_csv("m4_strassen_operations.csv")
    ns4 = [int(r["n"]) for r in m4]
    axes[1, 1].semilogx(ns4, [int(r["naive_ops"]) / n ** 3 for r, n in zip(m4, ns4)], "^-", label="naive / n^3")
    axes[1, 1].semilogx(ns4, [int(r["strassen_cutoff_1_ops"]) / n ** math.log2(7) for r, n in zip(m4, ns4)], "o-",
                        label="pure Strassen / n^2.807")
    axes[1, 1].axhline(2, color="r", ls=":", label="naive limit 2")
    axes[1, 1].axhline(7, color="k", ls="--", label="Strassen limit 7")
    axes[1, 1].set(title="M4 Strassen (operations / leading power)", ylabel="ratio")
    for ax in axes.flat:
        ax.set_xlabel("n (problem size)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Theory vs experiment - counted operations normalised by the derived complexity")
    fig.tight_layout()
    fig.savefig(GRAPHS / "final_theory_vs_experiment.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
