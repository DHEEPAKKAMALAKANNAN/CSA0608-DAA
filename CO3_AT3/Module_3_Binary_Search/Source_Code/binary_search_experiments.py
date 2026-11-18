"""SwiftLogix - Module 3 experiments: binary search vs linear search, interpolation search and a hash index.

Index arrangements (sorted, unique 10-digit tracking IDs):
    uniform   - IDs drawn uniformly from the 10-digit range (randomised ID issue)
    clustered - 8 hubs each issue a block of nearly consecutive IDs at a random base (sequential ID issue)
Counted comparisons are the primary evidence (a three-way comparison counts as one; interpolation search
also pays 2 range-check comparisons per step).  For binary search the counts are checked against the
exact decision-tree totals S(n) (successful) and E(n) (unsuccessful).  Times are per lookup, best of 3.

Run:  py -3 binary_search_experiments.py      (about 1-2 minutes)
"""
import bisect
import csv
import math
import random
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from binary_search import (OpCounter, binary_search, guarded_interpolation_search,  # noqa: E402
                           interpolation_search, linear_search)

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "Supporting_Files" / "results"
GRAPHS = ROOT / "Module_3_Binary_Search" / "Report" / "graphs"
SIZES = [2 ** k for k in range(10, 21)]          # 1,024 ... 1,048,576 IDs
EXACT_MAX = 2 ** 16                              # enumerate every key / gap up to this n, else sample
SAMPLE_Q = 20000
LINEAR_MAX = 2 ** 14


def make_keys(n, kind, seed=42):
    rng = random.Random(seed + n)
    if kind == "uniform":
        return sorted(rng.sample(range(10 ** 9, 10 ** 10), n))
    blocks = 8                                   # clustered: 8 hub blocks of nearly consecutive IDs
    bases = sorted(rng.sample(range(10 ** 9, 10 ** 10 - 10 ** 7), blocks))
    keys = []
    for b, base in enumerate(bases):
        k = base
        for _ in range(n // blocks + (1 if b < n % blocks else 0)):
            k += rng.randint(1, 3)
            keys.append(k)
    return keys


_S, _E = {0: 0}, {0: 0}


def total_successful(n):
    """S(n): total comparisons of the n successful searches = internal path length of the decision tree."""
    if n not in _S:
        left = (n - 1) // 2
        _S[n] = n + total_successful(left) + total_successful(n - 1 - left)
    return _S[n]


def total_unsuccessful(n):
    """E(n): total comparisons of the n + 1 unsuccessful searches (one per gap)."""
    if n not in _E:
        left = (n - 1) // 2
        _E[n] = (n + 1) + total_unsuccessful(left) + total_unsuccessful(n - 1 - left)
    return _E[n]


def avg_count(fn, keys, queries):
    """Average and maximum comparisons per query, plus the average number of probes (index accesses)."""
    total, worst, probes = 0, 0, 0
    for q in queries:
        c = OpCounter()
        fn(keys, q, counter=c)
        total += c.comparisons
        probes += c.probes
        worst = max(worst, c.comparisons)
    return total / len(queries), worst, probes / len(queries)


def time_per_lookup(fn, keys, queries):
    best = float("inf")
    for _ in range(3):
        t0 = time.perf_counter()
        for q in queries:
            fn(keys, q)
        best = min(best, time.perf_counter() - t0)
    return best / len(queries) * 1e6               # microseconds


def save_csv(name, header, rows):
    for folder in (RESULTS, GRAPHS):
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.setrecursionlimit(10000)
    rows_a, rows_b, rows_c = [], [], []
    print("=" * 116)
    print("M3 experiment A - binary search, counted vs exact decision-tree formulas (uniform IDs)")
    print("=" * 116)
    print(f"{'n':>9} | {'avg succ':>8} {'S(n)/n':>8} {'lg n - 1':>8} {'max succ':>8} {'lg n+1':>6} | "
          f"{'avg fail':>8} {'E(n)/(n+1)':>10} {'max fail':>8} | queries")
    for n in SIZES:
        keys = make_keys(n, "uniform")
        rng = random.Random(n)
        if n <= EXACT_MAX:
            succ = keys
            gaps = list(range(n + 1))
            mode = "all"
        else:
            succ = rng.sample(keys, SAMPLE_Q)
            gaps = rng.sample(range(n + 1), SAMPLE_Q)
            mode = "sample"
        fail = [keys[0] - 0.5 if g == 0 else keys[g - 1] + 0.5 for g in gaps]   # one absent key in each gap
        a_s, m_s, _ = avg_count(binary_search, keys, succ)
        a_f, m_f, _ = avg_count(binary_search, keys, fail)
        f_s, f_f = total_successful(n) / n, total_unsuccessful(n) / (n + 1)
        rows_a.append([n, round(a_s, 4), round(f_s, 4), m_s, n.bit_length(), round(a_f, 4), round(f_f, 4), m_f, mode])
        print(f"{n:>9,} | {a_s:>8.3f} {f_s:>8.3f} {math.log2(n) - 1:>8.3f} {m_s:>8} {n.bit_length():>6} | "
              f"{a_f:>8.3f} {f_f:>10.3f} {m_f:>8} | {mode} ({len(succ):,} + {len(fail):,})")
    save_csv("m3_binary_search_exact.csv", ["n", "avg_success_counted", "avg_success_formula", "max_success",
                                            "floor_lg_n_plus_1", "avg_fail_counted", "avg_fail_formula",
                                            "max_fail", "query_mode"], rows_a)

    print()
    print("M3 experiment B - average comparisons / average probes per SUCCESSFUL lookup "
          "(min(n, 2,000) random queries per size)")
    print(f"{'n':>9} | {'linear':>9} {'(n+1)/2':>9} | {'binary':>11} | {'interpolation':>13} {'guarded':>11} | "
          f"{'interpolation':>15} {'max':>5} | {'guarded':>11} {'max':>3} | {'lg lg n':>7}")
    print(f"{'':>9} | {'uniform':>9} {'':>9} | {'uniform':>11} | {'uniform':>13} {'uniform':>11} | "
          f"{'clustered':>15} {'':>5} | {'clustered':>11} {'':>3} |")
    for n in SIZES:
        ku, kc = make_keys(n, "uniform"), make_keys(n, "clustered")
        rng = random.Random(n + 1)
        qu, qc = rng.sample(ku, min(2000, n)), rng.sample(kc, min(2000, n))
        lin = avg_count(linear_search, ku, qu[:300])[0] if n <= LINEAR_MAX else None
        b, _, bp = avg_count(binary_search, ku, qu)
        iu, _, iup = avg_count(interpolation_search, ku, qu)
        gu, _, gup = avg_count(guarded_interpolation_search, ku, qu)
        ic, icm, icp = avg_count(interpolation_search, kc, qc)
        gc, gcm, gcp = avg_count(guarded_interpolation_search, kc, qc)
        rows_b.append([n, round(lin, 2) if lin else "", round(b, 3), round(iu, 3), round(iup, 3), round(gu, 3),
                       round(gup, 3), round(ic, 3), icm, round(icp, 3), round(gc, 3), gcm, round(gcp, 3)])
        lin_txt = f"{lin:>9,.1f}" if lin else f"{'-':>9}"
        print(f"{n:>9,} | {lin_txt} {(n + 1) / 2:>9,.1f} | {b:>5.2f}/{bp:<5.2f} | {iu:>6.2f}/{iup:<6.2f} "
              f"{gu:>5.2f}/{gup:<5.2f} | {ic:>8.1f}/{icp:<6.1f} {icm:>5} | {gc:>5.2f}/{gcp:<5.2f} {gcm:>3} | "
              f"{math.log2(math.log2(n)):>7.2f}")
    save_csv("m3_search_comparisons.csv", ["n", "linear_uniform", "binary_uniform", "interp_uniform",
                                           "interp_uniform_probes", "guarded_uniform", "guarded_uniform_probes",
                                           "interp_clustered", "interp_clustered_max", "interp_clustered_probes",
                                           "guarded_clustered", "guarded_clustered_max", "guarded_clustered_probes"],
             rows_b)
    print("cells = comparisons/probes.  Interpolation pays 3 comparisons per probe (2 range checks + 1 three-way);")
    print("binary pays 1.  A probe is one access to the index array (a likely cache miss at production size).")

    print()
    print("M3 experiment C - time per lookup in microseconds (best of 3 runs over 2,000 successful queries)")
    print(f"{'n':>9} | {'linear':>8} {'binary (Py)':>11} {'interp (Py)':>11} {'guarded (Py)':>12} | "
          f"{'bisect (C)':>10} {'dict / hash':>11}")
    for n in (2 ** 10, 2 ** 12, 2 ** 14, 2 ** 17, 2 ** 20):
        keys = make_keys(n, "uniform")
        q = random.Random(n + 2).sample(keys, min(2000, n))
        table = {k: i for i, k in enumerate(keys)}
        lin = time_per_lookup(linear_search, keys, q[:200]) if n <= LINEAR_MAX else None
        tb = time_per_lookup(binary_search, keys, q)
        ti = time_per_lookup(interpolation_search, keys, q)
        tg = time_per_lookup(guarded_interpolation_search, keys, q)
        tc = time_per_lookup(lambda k, t: bisect.bisect_left(k, t), keys, q)
        th = time_per_lookup(lambda k, t: table.get(t, -1), keys, q)
        rows_c.append([n, round(lin, 3) if lin else "", round(tb, 3), round(ti, 3), round(tg, 3), round(tc, 3),
                       round(th, 3)])
        lin_txt = f"{lin:>8.1f}" if lin else f"{'-':>8}"
        print(f"{n:>9,} | {lin_txt} {tb:>11.2f} {ti:>11.2f} {tg:>12.2f} | {tc:>10.3f} {th:>11.3f}")
    save_csv("m3_time_per_lookup.csv", ["n", "linear_us", "binary_us", "interp_us", "guarded_us", "bisect_c_us",
                                        "dict_us"], rows_c)
    plot(rows_a, rows_b, rows_c)
    print("\nCSV : Supporting_Files/results/m3_binary_search_exact.csv, m3_search_comparisons.csv, "
          "m3_time_per_lookup.csv")
    print("PNG : Module_3_Binary_Search/Report/graphs/m3_comparisons.png, m3_time_per_lookup.png")


def plot(rows_a, rows_b, rows_c):
    ns = [r[0] for r in rows_b]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    lin_ns = [r[0] for r in rows_b if r[1] != ""]
    ax1.loglog(lin_ns, [r[1] for r in rows_b if r[1] != ""], "^-", label="linear search (counted)")
    ax1.loglog(ns, [(n + 1) / 2 for n in ns], "r:", label="theory (n + 1) / 2")
    ax1.loglog(ns, [r[1] for r in rows_a], "o-", label="binary search, average (counted)")
    ax1.loglog(ns, [r[3] for r in rows_a], "s-", label="binary search, worst (counted)")
    ax1.loglog(ns, [math.floor(math.log2(n)) + 1 for n in ns], "k--", label="theory floor(log2 n) + 1")
    ax1.set(title="Linear vs binary search", xlabel="n (tracking IDs in the index)", ylabel="comparisons per lookup")
    ax2.semilogx(ns, [r[2] for r in rows_b], "o-", label="binary (uniform IDs)")
    ax2.semilogx(ns, [r[3] for r in rows_b], "s-", label="interpolation (uniform IDs)")
    ax2.semilogx(ns, [r[5] for r in rows_b], "v-", label="guarded interpolation (uniform IDs)")
    ax2.semilogx(ns, [r[10] for r in rows_b], "d-", label="guarded interpolation (clustered IDs)")
    ax2.semilogx(ns, [min(r[7], 60) for r in rows_b], "x:", label="interpolation (clustered IDs, clipped at 60)")
    ax2.semilogx(ns, [math.log2(n) for n in ns], "k--", label="theory log2 n")
    ax2.semilogx(ns, [3 * math.log2(math.log2(n)) for n in ns], "g:", label="theory 3 log2 log2 n")
    ax2.set(title="Binary vs interpolation search", xlabel="n (tracking IDs in the index)",
            ylabel="average comparisons per successful lookup")
    ax2.set_ylim(0, 105)
    ax1.legend(fontsize=8)
    ax2.legend(fontsize=7, loc="upper left", ncol=2)
    for ax in (ax1, ax2):
        ax.grid(True, which="both", alpha=0.3)
    fig.suptitle("Module 3 - comparisons per lookup")
    fig.tight_layout()
    fig.savefig(GRAPHS / "m3_comparisons.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ns_c = [r[0] for r in rows_c]
    labels = ["linear", "binary (Python)", "interpolation (Python)", "guarded interp. (Python)",
              "bisect (C)", "dict / hash (C)"]
    for col, (lab, mk) in enumerate(zip(labels, "^osdvx"), start=1):
        pts = [(r[0], r[col]) for r in rows_c if r[col] != ""]
        ax.loglog([p[0] for p in pts], [p[1] for p in pts], mk + "-", label=lab)
    ax.set(title="Module 3 - time per lookup (best of 3)", xlabel="n (tracking IDs in the index)",
           ylabel="time per lookup (microseconds)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(GRAPHS / "m3_time_per_lookup.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
