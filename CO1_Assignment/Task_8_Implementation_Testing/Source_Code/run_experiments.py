"""
run_experiments.py - experimental performance of the three search approaches (Tasks 9 and 10).

Problem: measure how sequential search (A), recursive binary search with merge-sort preprocessing (B)
and hashing with separate chaining (C) behave as the database grows from 1,000 to 1,000,000 records,
and compare every measured operation count with the value predicted by the mathematical analysis.

Procedure (identical for every approach):
  * datasets   : nested seed-42 datasets of n = 1,000 / 10,000 / 100,000 / 1,000,000 records
  * queries    : for each n ONE batch of 500 present + 500 absent keys (seed = n) used by all three
                 approaches; sequential search at n = 1,000,000 uses the first 100 + 100 keys of that
                 batch (one search takes 25-55 ms in Python), still at random positions
  * counts     : basic operations counted inside the algorithms (primary evidence)
  * time       : time.perf_counter, garbage collector off while timing, MINIMUM of R repetitions
                 (other processes can only add time, so the minimum is the least disturbed run)
  * memory     : bytes of the search structure (sys.getsizeof accounting; shared records excluded)
  * exhaustive : every stored key searched once with B and C -> exact average vs the closed form
Outputs: CSV tables (Task_9 folder + Report/Tables_and_Graphs) and PNG graphs (Report/Tables_and_Graphs).
"""
import bisect
import csv
import gc
import math
import os
import platform
import statistics
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from search_algorithms import (OpCounter, StudentHashTable, binary_search, hash_search,  # noqa: E402
                               merge_sort_records, next_prime, sequential_search)
from student_records import REG_MAX, REG_MIN, generate_records, make_query_batch  # noqa: E402

SIZES = (1_000, 10_000, 100_000, 1_000_000)
HITS, MISSES = 500, 500
SEQ_QUERIES_AT_1M = 100                  # per type (successful / unsuccessful)
KEY_UNIVERSE = REG_MAX - REG_MIN + 1     # U = 10,000,000 possible registration numbers
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SOURCE_DIR, "..", ".."))
TASK9_DIR = os.path.join(ROOT, "Task_9_Experimental_Performance")
GRAPH_DIR = os.path.join(ROOT, "Report", "Tables_and_Graphs")
COLORS = {"A": "#d62728", "B": "#1f77b4", "C": "#2ca02c"}
NAMES = {"A": "A: sequential search", "B": "B: recursive binary search", "C": "C: hash table (chaining)"}


# ----------------------------------------------------------------------------------------- helpers
def timed(function, repeats):
    """Run function() `repeats` times with the GC disabled; return (minimum seconds, last result)."""
    times, result = [], None
    for _ in range(repeats):
        gc.collect()
        gc.disable()
        try:
            start = time.perf_counter()
            result = function()
            times.append(time.perf_counter() - start)
        finally:
            gc.enable()
    return min(times), result


def search_all(search, structure, keys):
    """The timed loop: search every key of the batch once."""
    counter = OpCounter()
    for key in keys:
        search(structure, key, counter)


def write_csv(name, header, rows):
    """Save a table as CSV in the Task 9 folder and in Report/Tables_and_Graphs."""
    for folder in (TASK9_DIR, GRAPH_DIR):
        with open(os.path.join(folder, name), "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            writer.writerows(rows)


def exact_binary_success_total(n, memo={0: 0}):
    """S(n) = n + S(floor((n-1)/2)) + S(ceil((n-1)/2)) = total three-way comparisons of all n hits."""
    if n not in memo:
        left = (n - 1) // 2
        memo[n] = n + exact_binary_success_total(left) + exact_binary_success_total(n - 1 - left)
    return memo[n]


def hash_pair_sum(m, universe=KEY_UNIVERSE):
    """Sum over buckets of c_j(c_j - 1), where c_j = number of possible keys with h(k) = j."""
    q, r = divmod(universe, m)
    return r * (q + 1) * q + (m - r) * q * (q - 1)


def theory(n, m):
    """Closed-form predictions from Tasks 3-7 (m = hash-table size)."""
    s = exact_binary_success_total(n)
    k = math.ceil(math.log2(n))
    u = KEY_UNIVERSE
    pairs = hash_pair_sum(m)
    return {"A_hit": (n + 1) / 2, "A_miss": n,
            "B_hit": s / n, "B_miss": (s + n) / (n + 1), "B_worst": math.floor(math.log2(n)) + 1,
            # uniform hashing of n keys drawn without replacement from the U = 10^7 possible numbers
            "C_hit": 1 + (n - 1) * pairs / (2 * u * (u - 1)), "C_miss": n * pairs / (u * (u - 1)),
            "C_hit_clrs": 1 + (n - 1) / (2 * m), "C_miss_clrs": n / m,       # textbook limit U -> infinity
            "sort_worst": n * k - 2 ** k + 1, "nlogn": n * math.log2(n),
            "build_cmp": n * (n - 1) / (2 * m), "alpha": n / m}


def measure_search(search, structure, hits, misses, reference, repeats):
    """Count operations per query (verification pass) and time the batch (timed passes)."""
    out = {}
    for label, keys in (("hit", hits), ("miss", misses)):
        counter, per_query, correct = OpCounter(), [], 0
        for key in keys:
            before = counter.comparisons
            found = search(structure, key, counter)
            per_query.append(counter.comparisons - before)
            correct += found is reference.get(key)
        seconds, _ = timed(lambda: search_all(search, structure, keys), repeats)
        out[label] = {"q": len(keys), "avg": sum(per_query) / len(keys), "max": max(per_query),
                      "extra": (counter.calls + counter.hash_computations) / len(keys),
                      "us": seconds / len(keys) * 1e6, "correct": correct}
    return out


def sort_with_counter(records):
    counter = OpCounter()
    return merge_sort_records(records, counter), counter


def build_with_counter(records):
    counter = OpCounter()
    return StudentHashTable.build(records, counter), counter


# ------------------------------------------------------------------------------------- experiment
def run(sizes):
    print("=" * 118)
    print(" CO1 experiments - sequential (A) vs recursive binary (B) vs hashing (C), "
          "1,000 ... 1,000,000 records")
    print(f" Python {platform.python_version()} on {platform.system()} {platform.release()} | perf_counter, "
          f"GC off while timing, minimum of R runs | {HITS}+{MISSES} queries per n "
          f"(A at 10^6: {SEQ_QUERIES_AT_1M}+{SEQ_QUERIES_AT_1M})")
    print("=" * 118)
    master = generate_records(max(sizes))
    res = {}
    for n in sizes:
        t_start = time.perf_counter()
        records = master[:n]
        reference = {r.reg_no: r for r in records}
        hits, misses = make_query_batch(records, HITS, MISSES, seed=n, key_set=reference.keys())
        reps_prep = 3 if n < 1_000_000 else 2
        r = {"n": n}
        # ---- preprocessing
        t_sort, (sorted_records, c_sort) = timed(lambda: sort_with_counter(records), reps_prep)
        t_build, (table, c_build) = timed(lambda: build_with_counter(records), reps_prep)
        r["prep"] = {"B": (c_sort.comparisons, c_sort.moves, t_sort),
                     "C": (c_build.comparisons, c_build.hash_computations, t_build)}
        r["m"], r["alpha"], r["max_chain"] = table.size, table.load_factor, max(table.chain_lengths())
        # ---- searching (same batch for all; A at 10^6 uses the first 100 + 100 keys of it)
        seq_hits = hits if n < 1_000_000 else hits[:SEQ_QUERIES_AT_1M]
        seq_misses = misses if n < 1_000_000 else misses[:SEQ_QUERIES_AT_1M]
        reps_seq = 5 if n <= 10_000 else (3 if n <= 100_000 else 1)
        r["A"] = measure_search(sequential_search, records, seq_hits, seq_misses, reference, reps_seq)
        r["B"] = measure_search(binary_search, sorted_records, hits, misses, reference, 7)
        r["C"] = measure_search(hash_search, table, hits, misses, reference, 7)
        # ---- exhaustive check: every stored key searched once with B and C
        for label, search, structure in (("B", binary_search, sorted_records), ("C", hash_search, table)):
            counter, worst = OpCounter(), 0
            for rec in records:
                before = counter.comparisons
                search(structure, rec.reg_no, counter)
                worst = max(worst, counter.comparisons - before)
            r["exh_" + label] = (counter.comparisons / n, worst)
        # ---- memory of the search structures (the records themselves are shared and excluded)
        per_record = sys.getsizeof(records[0]) + sys.getsizeof(records[0].reg_no)
        r["mem"] = {"records": sys.getsizeof(records) + n * per_record, "A": 0,
                    "B": sys.getsizeof(sorted_records), "B_peak": 2 * sys.getsizeof(sorted_records),
                    "C": table.memory_bytes()}
        # ---- reference: the same ideas implemented in C inside CPython (constant-factor comparison)
        keys_sorted = [rec.reg_no for rec in sorted_records]
        t_sorted, _ = timed(lambda: sorted(records, key=lambda x: x.reg_no), reps_prep)
        t_dict, d = timed(lambda: {rec.reg_no: rec for rec in records}, reps_prep)
        t_bisect, _ = timed(lambda: [bisect.bisect_left(keys_sorted, k) for k in hits], 7)
        t_dget, _ = timed(lambda: [d.get(k) for k in hits], 7)
        r["builtin"] = (t_sorted, t_dict, t_bisect / len(hits) * 1e6, t_dget / len(hits) * 1e6)
        if n == max(sizes):
            r["chains"] = table.chain_lengths()
        res[n] = r
        print(f" n = {n:>9,}: done in {time.perf_counter() - t_start:5.1f} s  (m = {table.size:,}, "
              f"alpha = {table.load_factor:.3f}, longest chain = {r['max_chain']})")
        del sorted_records, table, reference, d, keys_sorted
        gc.collect()
    return res


# ---------------------------------------------------------------------------------------- tables
def report_tables(res, sizes):
    th = {n: theory(n, res[n]["m"]) for n in sizes}
    print("\nTABLE 1 - preprocessing cost (once per dataset)")
    print(f"{'n':>10} | {'B: merge sort cmp':>17} {'n lg n':>12} {'worst bound':>12} {'moves':>11} "
          f"{'time ms':>9} | {'C: hash h(k)':>12} {'chain cmp':>9} {'theory':>9} {'time ms':>8}")
    prep_rows = []
    for n in sizes:
        cb, mv, tb = res[n]["prep"]["B"]
        cc, hc, tc = res[n]["prep"]["C"]
        t = th[n]
        print(f"{n:>10,} | {cb:>17,} {t['nlogn']:>12,.0f} {t['sort_worst']:>12,} {mv:>11,} {tb * 1e3:>9.1f} | "
              f"{hc:>12,} {cc:>9,} {t['build_cmp']:>9,.0f} {tc * 1e3:>8.1f}")
        prep_rows += [[n, "A", 0, 0, 0.0, 0, "no preprocessing"],
                      [n, "B", cb, mv, round(tb * 1e3, 3), t["sort_worst"],
                       "merge sort; other_ops = moves; theory = worst-case bound"],
                      [n, "C", cc, hc, round(tc * 1e3, 3), round(t["build_cmp"], 1),
                       "hash build; other_ops = hash computations; theory = n(n-1)/2m comparisons"]]
    write_csv("preprocessing_cost.csv", ["n", "approach", "comparisons", "other_ops", "time_ms",
                                         "theory_comparisons", "note"], prep_rows)

    print("\nTABLE 2 - search cost per query (average over the batch; time = minimum of R runs)")
    print(f"{'n':>10} {'approach':<4} {'queries':>8} {'avg cmp hit':>12} {'avg cmp miss':>13} {'max cmp':>9} "
          f"{'extra ops/q':>11} {'us/hit':>10} {'us/miss':>10} {'correct':>9}")
    rows = []
    for n in sizes:
        for a in "ABC":
            h, m = res[n][a]["hit"], res[n][a]["miss"]
            ok = h["correct"] + m["correct"] == h["q"] + m["q"]
            print(f"{n:>10,} {a:<4} {h['q'] + m['q']:>8,} {h['avg']:>12,.2f} {m['avg']:>13,.2f} "
                  f"{max(h['max'], m['max']):>9,} {(h['extra'] + m['extra']) / 2:>11.2f} {h['us']:>10,.2f} "
                  f"{m['us']:>10,.2f} {'all' if ok else 'ERROR':>9}")
            rows.append([n, a, h["q"], m["q"], round(h["avg"], 3), round(m["avg"], 3), h["max"], m["max"],
                         round(h["extra"], 3), round(m["extra"], 3), round(h["us"], 3), round(m["us"], 3),
                         round((h["us"] + m["us"]) / 2, 3), ok])
    write_csv("search_performance.csv", ["n", "approach", "hit_queries", "miss_queries", "avg_cmp_hit",
                                         "avg_cmp_miss", "max_cmp_hit", "max_cmp_miss", "extra_ops_hit",
                                         "extra_ops_miss", "time_us_hit", "time_us_miss", "time_us_mixed",
                                         "all_correct"], rows)

    print("\nTABLE 3 - theory vs measurement (average key comparisons per search)")
    print(f"{'n':>10} {'approach':<4} {'theory hit':>12} {'measured':>12} {'ratio':>7} | {'theory miss':>12} "
          f"{'measured':>12} {'ratio':>7}")
    rows = []
    for n in sizes:
        for a in "ABC":
            t_h, t_m = th[n][a + "_hit"], th[n][a + "_miss"]
            m_h, m_m = res[n][a]["hit"]["avg"], res[n][a]["miss"]["avg"]
            print(f"{n:>10,} {a:<4} {t_h:>12,.2f} {m_h:>12,.2f} {m_h / t_h:>7.3f} | {t_m:>12,.2f} "
                  f"{m_m:>12,.2f} {m_m / t_m:>7.3f}")
            rows += [[n, a, "successful", round(t_h, 4), round(m_h, 4), round(m_h / t_h, 4)],
                     [n, a, "unsuccessful", round(t_m, 4), round(m_m, 4), round(m_m / t_m, 4)]]
    write_csv("theory_vs_measured.csv", ["n", "approach", "case", "theory", "measured", "ratio"], rows)

    print("\nTABLE 4 - exhaustive check: every stored key searched once (exact averages)")
    print(f"{'n':>10} | {'B avg meas.':>11} {'S(n)/n':>9} {'B max':>6} {'lg bound':>8} | {'C avg meas.':>11} "
          f"{'model U=1e7':>11} {'1+(n-1)/2m':>11} {'C max':>6} {'alpha':>6}")
    rows = []
    for n in sizes:
        (b_avg, b_max), (c_avg, c_max) = res[n]["exh_B"], res[n]["exh_C"]
        t = th[n]
        print(f"{n:>10,} | {b_avg:>11.4f} {t['B_hit']:>9.4f} {b_max:>6} {t['B_worst']:>8} | {c_avg:>11.4f} "
              f"{t['C_hit']:>11.4f} {t['C_hit_clrs']:>11.4f} {c_max:>6} {t['alpha']:>6.3f}")
        rows.append([n, round(b_avg, 6), round(t["B_hit"], 6), b_max, t["B_worst"], round(c_avg, 6),
                     round(t["C_hit"], 6), round(t["C_hit_clrs"], 6), c_max, round(t["alpha"], 6), res[n]["m"]])
    write_csv("exhaustive_verification.csv", ["n", "B_avg_measured", "B_avg_theory_S(n)/n", "B_max_measured",
                                              "B_worst_theory", "C_avg_measured", "C_avg_theory_finite_U",
                                              "C_avg_theory_clrs", "C_max_comparisons", "alpha", "m"], rows)

    print("\nTABLE 5 - growth when n grows 10x (measured ratios) and log-log slope of time per search vs n")
    print(f"{'n step':>22} | {'A cmp':>7} {'A time':>7} | {'B cmp':>7} {'B time':>7} | {'C cmp':>7} "
          f"{'C time':>7} | {'theory A':>8} {'theory B':>8} {'theory C':>8}")
    rows = []
    for n1, n2 in zip(sizes, sizes[1:]):
        cells, out = [], [f"{n1:,}->{n2:,}"]
        for a in "ABC":
            c1, c2 = mixed(res[n1], a, "avg"), mixed(res[n2], a, "avg")
            t1, t2 = mixed(res[n1], a, "us"), mixed(res[n2], a, "us")
            cells.append(f"{c2 / c1:>7.2f} {t2 / t1:>7.2f}")
            out += [round(c2 / c1, 4), round(t2 / t1, 4)]
        theo = [n2 / n1, math.log2(n2) / math.log2(n1), 1.0]
        print(f"{out[0]:>22} | " + " | ".join(cells) + f" | {theo[0]:>8.2f} {theo[1]:>8.2f} {theo[2]:>8.2f}")
        rows.append(out + [round(x, 4) for x in theo])
    slopes = [loglog_slope(sizes, [mixed(res[n], a, "us") for n in sizes]) for a in "ABC"]
    print(f"{'log-log slope of time':>22} | {slopes[0]:>15.3f} | {slopes[1]:>15.3f} | {slopes[2]:>15.3f} | "
          f"(theory: A = 1, B -> 0 slowly (log n), C = 0)")
    rows.append(["loglog_time_slope", "", round(slopes[0], 4), "", round(slopes[1], 4), "", round(slopes[2], 4),
                 1.0, "", 0.0])
    write_csv("growth_factors.csv", ["n_step", "A_cmp_ratio", "A_time_ratio", "B_cmp_ratio", "B_time_ratio",
                                     "C_cmp_ratio", "C_time_ratio", "theory_A", "theory_B", "theory_C"], rows)

    print("\nTABLE 6 - extra memory of the search structure (records shared, not counted) "
          "and break-even searches")
    print(f"{'n':>10} | {'records MB':>10} {'A':>3} {'B sorted MB':>11} {'B peak MB':>9} {'C table MB':>10} | "
          f"{'A->B q* ops':>11} {'A->B q* time':>12} {'A->C q* ops':>11} {'A->C q* time':>12}")
    mem_rows, be_rows = [], []
    for n in sizes:
        mem = res[n]["mem"]
        be = break_even(res[n])
        print(f"{n:>10,} | {mem['records'] / 1e6:>10.2f} {0:>3} {mem['B'] / 1e6:>11.2f} "
              f"{mem['B_peak'] / 1e6:>9.2f} {mem['C'] / 1e6:>10.2f} | {be[0]:>11.2f} {be[1]:>12.2f} "
              f"{be[2]:>11.2f} {be[3]:>12.2f}")
        mem_rows.append([n, mem["records"], 0, mem["B"], mem["B_peak"], mem["C"], res[n]["m"],
                         round(res[n]["alpha"], 4)])
        be_rows.append([n] + [round(x, 3) for x in be])
    write_csv("memory_usage.csv", ["n", "records_bytes", "A_extra_bytes", "B_sorted_copy_bytes",
                                   "B_peak_extra_bytes_during_sort", "C_table_bytes", "hash_table_size_m",
                                   "alpha"], mem_rows)
    write_csv("break_even.csv", ["n", "A_to_B_by_operations", "A_to_B_by_time", "A_to_C_by_operations",
                                 "A_to_C_by_time"], be_rows)

    print("\nTABLE 7 - reference: the same ideas as C code inside CPython "
          "(shows the interpreter constant factor)")
    print(f"{'n':>10} | {'merge sort ms':>13} {'sorted() ms':>11} {'ratio':>6} | {'hash build ms':>13} "
          f"{'dict ms':>8} {'ratio':>6} | {'B us':>6} {'bisect us':>9} | {'C us':>6} {'dict.get us':>11}")
    rows = []
    for n in sizes:
        t_sorted, t_dict, us_bisect, us_dget = res[n]["builtin"]
        tb, tc = res[n]["prep"]["B"][2], res[n]["prep"]["C"][2]
        ub, uc = res[n]["B"]["hit"]["us"], res[n]["C"]["hit"]["us"]
        print(f"{n:>10,} | {tb * 1e3:>13.1f} {t_sorted * 1e3:>11.1f} {tb / t_sorted:>6.1f} | {tc * 1e3:>13.1f} "
              f"{t_dict * 1e3:>8.1f} {tc / t_dict:>6.1f} | {ub:>6.2f} {us_bisect:>9.3f} | {uc:>6.2f} "
              f"{us_dget:>11.3f}")
        rows.append([n, round(tb * 1e3, 3), round(t_sorted * 1e3, 3), round(tc * 1e3, 3),
                     round(t_dict * 1e3, 3), round(ub, 4), round(us_bisect, 4), round(uc, 4),
                     round(us_dget, 4)])
    write_csv("builtin_reference.csv", ["n", "merge_sort_ms", "builtin_sorted_ms", "hash_build_ms",
                                        "builtin_dict_ms", "binary_us_hit", "bisect_us_hit", "hash_us_hit",
                                        "dict_get_us_hit"], rows)
    return th


def mixed(r, a, key):
    """50/50 mix of successful and unsuccessful searches."""
    return (r[a]["hit"][key] + r[a]["miss"][key]) / 2


def loglog_slope(xs, ys):
    """Least-squares slope of log10(y) against log10(x)."""
    lx, ly = [math.log10(x) for x in xs], [math.log10(y) for y in ys]
    mx, my = statistics.mean(lx), statistics.mean(ly)
    return sum((x - mx) * (y - my) for x, y in zip(lx, ly)) / sum((x - mx) ** 2 for x in lx)


def break_even(r):
    """Number of searches after which preprocessing pays for itself compared with sequential search."""
    ops_a, ops_b = mixed(r, "A", "avg"), mixed(r, "B", "avg")
    ops_c = mixed(r, "C", "avg") + 1                       # + one hash computation per search
    prep_b_ops = r["prep"]["B"][0]
    prep_c_ops = r["prep"]["C"][0] + r["prep"]["C"][1]
    t_a, t_b, t_c = (mixed(r, x, "us") * 1e-6 for x in "ABC")
    return (prep_b_ops / (ops_a - ops_b), r["prep"]["B"][2] / (t_a - t_b),
            prep_c_ops / (ops_a - ops_c), r["prep"]["C"][2] / (t_a - t_c))


# ---------------------------------------------------------------------------------------- graphs
def style(ax, title, xlabel, ylabel, legend_loc="best"):
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8, loc=legend_loc)


def save(fig, name):
    path = os.path.join(GRAPH_DIR, name)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def make_graphs(res, sizes):
    ns = list(sizes)
    dense = sorted({int(round(10 ** (3 + i * 3 / 60))) for i in range(61)})
    dense_th = {n: theory(n, next_prime(math.ceil(n / 0.75))) for n in dense}
    paths = []

    # Figure 1 - comparisons vs n with the theoretical curves
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, case in zip(axes, ("hit", "miss")):
        for a in "ABC":
            ax.plot(ns, [res[n][a][case]["avg"] for n in ns], "o", color=COLORS[a], ms=7,
                    label=NAMES[a] + " (measured)")
        labels = {"hit": ("theory (n+1)/2", "theory S(n)/n ~ log2 n - 1", "theory 1 + alpha/2 (alpha <= 0.75)"),
                  "miss": ("theory n", "theory (S(n)+n)/(n+1) ~ log2 n", "theory alpha (alpha <= 0.75)")}[case]
        for a, label in zip("ABC", labels):
            ax.plot(dense, [dense_th[n][f"{a}_{case}"] for n in dense], "--", color=COLORS[a], label=label)
        ax.set_xscale("log")
        ax.set_yscale("log")
        style(ax, f"{'Successful' if case == 'hit' else 'Unsuccessful'} search: key comparisons vs n",
              "number of records n (log scale)", "average key comparisons per search (log scale)",
              "center right")
    fig.tight_layout()
    paths.append(save(fig, "fig1_comparisons_vs_n.png"))

    # Figure 2 - time per search vs n with fitted theory curves
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    models = {"A": (lambda n: n, "c*n"), "B": (lambda n: math.log2(n), "c*log2 n"), "C": (lambda n: 1.0, "c*1")}
    for a in "ABC":
        ys = [mixed(res[n], a, "us") for n in ns]
        f, label = models[a]
        c = math.exp(statistics.mean(math.log(y / f(n)) for y, n in zip(ys, ns)))
        ax.plot(ns, ys, "o-", color=COLORS[a], ms=7, label=NAMES[a] + " (measured)")
        ax.plot(dense, [c * f(n) for n in dense], "--", color=COLORS[a], alpha=0.7, label=f"fitted {label}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    style(ax, "Time per search vs n (50% successful / 50% unsuccessful)", "number of records n (log scale)",
          "time per search (microseconds, log scale)")
    paths.append(save(fig, "fig2_time_per_search_vs_n.png"))

    # Figure 3 - preprocessing cost
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    ax = axes[0]
    ax.plot(ns, [res[n]["prep"]["B"][0] for n in ns], "o", color=COLORS["B"], ms=7,
            label="B: merge sort comparisons (measured)")
    ax.plot(dense, [n * math.log2(n) for n in dense], "--", color=COLORS["B"], label="n log2 n")
    ax.plot(ns, [res[n]["prep"]["C"][0] + res[n]["prep"]["C"][1] for n in ns], "s", color=COLORS["C"], ms=7,
            label="C: hash computations + chain comparisons (measured)")
    ax.plot(dense, [n + dense_th[n]["build_cmp"] for n in dense], "--", color=COLORS["C"],
            label="n + n(n-1)/2m  (~1.37 n)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    style(ax, "Preprocessing: basic operations vs n", "number of records n (log scale)",
          "operations (log scale)")
    ax = axes[1]
    for a, f, label in (("B", lambda n: n * math.log2(n), "fitted c*n log2 n"),
                        ("C", lambda n: n, "fitted c*n")):
        ys = [res[n]["prep"][a][2] * 1e3 for n in ns]
        c = math.exp(statistics.mean(math.log(y / f(n)) for y, n in zip(ys, ns)))
        ax.plot(ns, ys, "o-", color=COLORS[a], ms=7, label=("B: merge sort" if a == "B" else "C: hash build")
                + " time (measured)")
        ax.plot(dense, [c * f(n) for n in dense], "--", color=COLORS[a], alpha=0.7, label=label)
    ax.set_xscale("log")
    ax.set_yscale("log")
    style(ax, "Preprocessing: time vs n", "number of records n (log scale)", "time (milliseconds, log scale)")
    fig.tight_layout()
    paths.append(save(fig, "fig3_preprocessing_cost.png"))

    # Figure 4 - amortised total cost vs number of searches q
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    rows = []
    qs = sorted({int(round(10 ** (i / 10))) for i in range(0, 71)})
    for ax, n in zip(axes, (ns[0], ns[-1])):
        r = res[n]
        prep = {"A": 0.0, "B": r["prep"]["B"][2], "C": r["prep"]["C"][2]}
        per = {a: mixed(r, a, "us") * 1e-6 for a in "ABC"}
        for a in "ABC":
            ax.plot(qs, [prep[a] + q * per[a] for q in qs], "-", color=COLORS[a], lw=2, label=NAMES[a])
        be = break_even(r)
        for q_star, a, label, offset, align in ((be[1], "B", "A = B", (-10, 10), "right"),
                                                (be[3], "C", "A = C", (10, -14), "left")):
            point = (q_star, prep[a] + q_star * per[a])
            ax.plot(*point, "k*", ms=11)
            ax.annotate(f"{label} at q = {q_star:.0f}", point, textcoords="offset points", xytext=offset,
                        fontsize=8, ha=align)
        ax.axvline(50_000, color="grey", ls=":", lw=1)
        ax.text(50_000, 0.03, " 50,000 searches", transform=ax.get_xaxis_transform(), fontsize=8, color="grey")
        ax.set_xscale("log")
        ax.set_yscale("log")
        style(ax, f"Total cost = preprocessing + q searches (n = {n:,})", "number of searches q (log scale)",
              "total time (seconds, log scale)", "upper left")
        for q in (1, 10, 100, 1_000, 10_000, 50_000, 100_000, 1_000_000):
            rows.append([n, q] + [round(prep[a] + q * per[a], 6) for a in "ABC"])
    fig.tight_layout()
    paths.append(save(fig, "fig4_amortised_cost_vs_searches.png"))
    write_csv("amortised_cost.csv", ["n", "searches_q", "A_total_s", "B_total_s", "C_total_s"], rows)

    # Figure 5 - memory
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.plot(ns, [res[n]["mem"]["records"] / 1e6 for n in ns], "k^-", label="the records themselves (shared)")
    ax.plot(ns, [res[n]["mem"]["B"] / 1e6 for n in ns], "o-", color=COLORS["B"],
            label="B: sorted copy (array of references)")
    ax.plot(ns, [res[n]["mem"]["B_peak"] / 1e6 for n in ns], "o--", color=COLORS["B"], alpha=0.6,
            label="B: peak during merge sort (+ buffer)")
    ax.plot(ns, [res[n]["mem"]["C"] / 1e6 for n in ns], "s-", color=COLORS["C"],
            label="C: bucket array + chains")
    ax.set_xscale("log")
    ax.set_yscale("log")
    style(ax, "Extra memory of the search structure (A needs none)", "number of records n (log scale)",
          "memory (MB, log scale)")
    paths.append(save(fig, "fig5_memory_vs_n.png"))

    # Figure 6 - chain-length distribution: observed vs Poisson vs finite-key-space model
    chains = res[ns[-1]]["chains"]
    m, n = len(chains), ns[-1]
    alpha, p = n / m, n / KEY_UNIVERSE
    q, r = divmod(KEY_UNIVERSE, m)
    xs = list(range(max(chains) + 2))
    observed = [chains.count(L) for L in xs]
    poisson = [m * math.exp(-alpha) * alpha ** L / math.factorial(L) for L in xs]
    finite = [r * binom(q + 1, L, p) + (m - r) * binom(q, L, p) for L in xs]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.bar([x - 0.27 for x in xs], observed, width=0.27, color=COLORS["C"], label="observed buckets")
    ax.bar(xs, finite, width=0.27, color="#9467bd",
           label=f"model: {q}-{q + 1} possible keys per bucket, p = {p}")
    ax.bar([x + 0.27 for x in xs], poisson, width=0.27, color="grey", label=f"Poisson(alpha = {alpha:.3f})")
    ax.set_yscale("log")
    ax.set_ylim(0.5, m)
    style(ax, f"Hash chain lengths at n = {n:,} (m = {m:,})", "chain length L", "number of buckets (log scale)")
    paths.append(save(fig, "fig6_chain_length_distribution.png"))
    write_csv("chain_length_distribution.csv", ["chain_length", "observed_buckets", "finite_key_space_model",
                                                "poisson_expected"],
              [[L, observed[L], round(finite[L], 2), round(poisson[L], 2)] for L in xs])
    return paths


def binom(trials, k, p):
    """Binomial probability P(X = k) for X ~ Bin(trials, p)."""
    return math.comb(trials, k) * p ** k * (1 - p) ** (trials - k) if k <= trials else 0.0


def main():
    start = time.perf_counter()
    res = run(SIZES)
    report_tables(res, SIZES)
    paths = make_graphs(res, SIZES)
    print("\nFiles written: 10 CSV tables (Task_9_Experimental_Performance + Report/Tables_and_Graphs) "
          "and graphs:")
    for i in range(0, len(paths), 3):
        print("  " + ", ".join(os.path.basename(p) for p in paths[i:i + 3]))
    print(f"Total experiment time: {time.perf_counter() - start:.1f} s")


if __name__ == "__main__":
    main()
