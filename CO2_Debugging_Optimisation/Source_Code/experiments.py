"""
Experimental comparison of the CORRECTED (brute force as intended) and OPTIMISED alert-triage modules.

Batch sizes: 100, 500, 1,000, 2,000 and 5,000 alerts (seeded datasets from alert_data.py).
For every batch the script counts the basic operations of each algorithm (primary evidence), times it
with time.perf_counter (minimum of several repeats - secondary evidence, the machine is shared) and
checks that both versions return identical results:

  sorting          key comparisons and swaps/moves  - random arrival stream and a nearly sorted queue
  searching        key comparisons for 1,000 analyst look-ups (80 % hits, 20 % misses)
  string matching  character comparisons for 5 signatures on the shift's log (+ adversarial texts)
  closest pair     DISTANCE COMPUTATIONS - brute force vs divide & conquer vs x-sweep (+ same-x batch)

Writes CSV files to ../Supporting_Files/experimental_results/, the comparison table to
../Report/tables/comparison_summary.csv and the graphs (+ the plotted numbers as CSV) to ../Report/graphs/.
"""
import csv
import math
import os
import random
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import corrected_alert_triage as C  # noqa: E402
import optimised_alert_triage as O  # noqa: E402
from alert_data import (BATCH_SIZES, SIGNATURES, build, log_text, make_alert_rows,  # noqa: E402
                        make_nearly_sorted_rows, make_same_x_rows)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "Supporting_Files", "experimental_results")
GRAPHS = os.path.join(HERE, "..", "Report", "graphs")
TABLES = os.path.join(HERE, "..", "Report", "tables")
QUERIES = 1000
BLUE, ORANGE, AQUA, GREY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#52514e"


# ------------------------------------------------------------------ measurement helpers
def counted(mod, fn, *args):
    """Run fn once with fresh counters; return (result, copy of the counters)."""
    mod.reset_counters()
    result = fn(*args)
    return result, dict(mod.COUNTERS)


def timed(fn, *args, repeats=3):
    """Minimum wall-clock time of `repeats` runs (seconds)."""
    best = math.inf
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - t0)
    return best


def reps(n, quadratic):
    """Fewer repeats for the slow quadratic runs on the large batches."""
    return 1 if quadratic and n >= 2000 else (3 if quadratic else 5)


def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


# ------------------------------------------------------------------ 1. sorting
def exp_sort():
    rows = []
    print("1) SORTING  sort_alerts: bubble sort (corrected) vs adaptive merge sort (optimised)")
    print(f"   {'n':>5} {'input':<14} {'bubble cmp':>11} {'n(n-1)/2':>11} {'swaps':>10} {'0.38n(n-1)/2':>12}"
          f" {'merge cmp':>9} {'nlog2n':>8} {'moves':>7} {'t bubble':>9} {'t merge':>8} same")
    for n in BATCH_SIZES:
        for cond, maker in (("random stream", make_alert_rows), ("nearly sorted", make_nearly_sorted_rows)):
            data = maker(n)
            ac, ao = build(C, data), build(O, data)
            rc, cc = counted(C, C.sort_alerts, ac)
            ro, co = counted(O, O.sort_alerts, ao)
            same = [a.alert_id for a in rc] == [a.alert_id for a in ro]
            tc = timed(C.sort_alerts, ac, repeats=reps(n, True))
            to = timed(O.sort_alerts, ao, repeats=reps(n, False))
            pairs = n * (n - 1) // 2
            rows.append([n, cond, cc["sort_comparisons"], cc["sort_swaps"], tc, co["sort_comparisons"],
                         co["sort_moves"], to, pairs, round(n * math.log2(n)), round(0.38 * pairs), same])
            print(f"   {n:>5} {cond:<14} {cc['sort_comparisons']:>11,} {pairs:>11,} {cc['sort_swaps']:>10,}"
                  f" {round(0.38 * pairs):>12,} {co['sort_comparisons']:>9,} {round(n * math.log2(n)):>8,}"
                  f" {co['sort_moves']:>7,} {tc:>8.4f}s {to:>7.4f}s {'yes' if same else 'NO'}")
    write_csv(os.path.join(RESULTS, "sort_results.csv"),
              ["n", "input", "bubble_comparisons", "bubble_swaps", "bubble_time_s", "merge_comparisons",
               "merge_moves", "merge_time_s", "theory_n(n-1)/2", "theory_nlog2n", "theory_0.38n(n-1)/2",
               "identical_output"], rows)
    return rows


# ------------------------------------------------------------------ 2. searching
def exp_search():
    rows = []
    print("2) SEARCHING  1,000 look-ups per batch: sequential (corrected) vs sentinel vs AlertIndex (optimised)")
    print(f"   {'n':>5} {'hits':>5} {'seq cmp':>10} {'theory':>10} {'sentinel cmp':>12} {'index ops':>9}"
          f" {'t seq':>8} {'t sentinel':>10} {'t index':>8} {'cmp ratio':>9} same")
    for n in BATCH_SIZES:
        data = make_alert_rows(n)
        ac, ao = build(C, data), build(O, data)
        rng = random.Random(11)
        targets = [rng.randint(1, n) if rng.random() < 0.8 else n + rng.randint(1, n) for _ in range(QUERIES)]
        queries = ["-".join(["ALR", f"{t:06d}"]) for t in targets]      # strings built at run time
        hits = sum(t <= n for t in targets)
        theory = sum(t if t <= n else n for t in targets)               # first match at position t-1

        def seq(mod, alerts):
            return [mod.find_alert(alerts, q) for q in queries]

        def indexed(alerts):
            index = O.AlertIndex(alerts)
            return [index.find(q) for q in queries]

        rc, cc = counted(C, seq, C, ac)
        rs, cs = counted(O, seq, O, ao)
        ri, ci = counted(O, indexed, ao)
        same = rc == rs == ri
        tc = timed(seq, C, ac, repeats=reps(n, True))
        ts = timed(seq, O, ao, repeats=reps(n, True))
        ti = timed(indexed, ao, repeats=reps(n, False))
        index_ops = ci["index_inserts"] + ci["search_comparisons"]
        rows.append([n, QUERIES, hits, QUERIES - hits, cc["search_comparisons"], theory, tc,
                     cs["search_comparisons"], ts, ci["index_inserts"], ci["search_comparisons"], ti, same])
        print(f"   {n:>5} {hits:>5} {cc['search_comparisons']:>10,} {theory:>10,} {cs['search_comparisons']:>12,}"
              f" {index_ops:>9,} {tc:>7.4f}s {ts:>9.4f}s {ti:>7.4f}s {cc['search_comparisons'] / index_ops:>8.0f}x"
              f" {'yes' if same else 'NO'}")
    write_csv(os.path.join(RESULTS, "search_results.csv"),
              ["n", "queries", "hits", "misses", "sequential_comparisons", "theory_sequential", "sequential_time_s",
               "sentinel_comparisons", "sentinel_time_s", "index_inserts", "index_probes", "index_time_s",
               "identical_output"], rows)
    return rows


# ------------------------------------------------------------------ 3. string matching
def exp_matching():
    rows, worst = [], []
    print("3) STRING MATCHING  5 signatures on the shift log: brute force (corrected) vs Horspool vs KMP")
    print(f"   {'n':>5} {'text L':>8} {'hits':>5} {'brute cmp':>10} {'per char':>8} {'Horspool':>9} {'per char':>8}"
          f" {'KMP cmp':>9} {'per char':>8} {'t brute':>8} {'t Horsp.':>8} {'t KMP':>7} same")
    for n in BATCH_SIZES:
        text = log_text(make_alert_rows(n))
        L = len(text)

        def scan(fn):
            return [fn(text, s) for s in SIGNATURES]

        rb, cb = counted(C, scan, C.match_signature)
        rh, ch = counted(O, scan, O.match_signature)
        rk, ck = counted(O, scan, O.match_signature_kmp)
        same = rb == rh == rk
        hits = sum(len(r) for r in rb)
        tb = timed(scan, C.match_signature, repeats=3)
        th = timed(scan, O.match_signature, repeats=3)
        tk = timed(scan, O.match_signature_kmp, repeats=3)
        b, h, k = cb["char_comparisons"], ch["char_comparisons"], ck["char_comparisons"]
        rows.append([n, L, hits, b, tb, h, th, k, tk, same])
        print(f"   {n:>5} {L:>8,} {hits:>5} {b:>10,} {b / L / 5:>8.3f} {h:>9,} {h / L / 5:>8.3f} {k:>9,}"
              f" {k / L / 5:>8.3f} {tb:>7.4f}s {th:>7.4f}s {tk:>6.4f}s {'yes' if same else 'NO'}")
        # adversarial texts of the same length: worst cases of brute force and of Horspool
        adv = "a" * L
        for name, pat in (("a^9 b", "a" * 9 + "b"), ("b a^9", "b" + "a" * 9)):
            _, wb = counted(C, C.match_signature, adv, pat)
            _, wh = counted(O, O.match_signature, adv, pat)
            _, wk = counted(O, O.match_signature_kmp, adv, pat)
            worst.append([n, L, name, wb["char_comparisons"], wh["char_comparisons"], wk["char_comparisons"],
                          (L - 10 + 1) * 10, 2 * L])
    print("   adversarial text 'a' * L, m = 10 (character comparisons):")
    print(f"   {'text L':>8} {'pattern':<7} {'brute':>10} {'Horspool':>10} {'KMP':>9} {'(L-m+1)m':>10} {'2L':>9}")
    for n, L, name, b, h, k, bound, kb in worst:
        if n in (100, 5000):
            print(f"   {L:>8,} {name:<7} {b:>10,} {h:>10,} {k:>9,} {bound:>10,} {kb:>9,}")
    write_csv(os.path.join(RESULTS, "matching_results.csv"),
              ["n", "text_length", "matches", "brute_comparisons", "brute_time_s", "horspool_comparisons",
               "horspool_time_s", "kmp_comparisons", "kmp_time_s", "identical_output"], rows)
    write_csv(os.path.join(RESULTS, "matching_worst_case.csv"),
              ["n", "text_length", "pattern", "brute_comparisons", "horspool_comparisons", "kmp_comparisons",
               "theory_(L-m+1)m", "theory_2L"], worst)
    return rows, worst


# ------------------------------------------------------------------ 4. closest pair
def exp_closest():
    rows = []
    print("4) CLOSEST PAIR  distance computations: brute force (corrected) vs divide & conquer vs x-sweep")
    print(f"   {'n':>5} {'batch':<7} {'brute dist':>10} {'n(n-1)/2':>10} {'D&C dist':>8} {'nlog2n':>7} {'sweep':>7}"
          f" {'t brute':>8} {'t D&C':>7} {'t sweep':>7} {'saving':>7} {'closest pair':<22} same")
    for n in BATCH_SIZES:
        for batch, maker in (("random", make_alert_rows), ("same-x", make_same_x_rows)):
            data = maker(n)
            ac, ao = build(C, data), build(O, data)
            rb, cb = counted(C, C.closest_alert_pair, ac)
            rd, cd = counted(O, O.closest_alert_pair, ao)
            rs, cs = counted(O, O.closest_alert_pair_sweep, ao)
            same = rb[1:] == rd[1:] == rs[1:] and math.isclose(rb[0], rd[0]) and math.isclose(rb[0], rs[0])
            tb = timed(C.closest_alert_pair, ac, repeats=reps(n, True))
            td = timed(O.closest_alert_pair, ao, repeats=reps(n, False))
            ts = timed(O.closest_alert_pair_sweep, ao, repeats=reps(n, batch == "same-x"))
            b, d, s = cb["distance_computations"], cd["distance_computations"], cs["distance_computations"]
            pairs = n * (n - 1) // 2
            rows.append([n, batch, b, tb, d, td, s, ts, pairs, round(n * math.log2(n)), rb[0], rb[1], rb[2], same])
            pair = f"{rb[0]:.6f} ({rb[1]},{rb[2]})"
            print(f"   {n:>5} {batch:<7} {b:>10,} {pairs:>10,} {d:>8,} {round(n * math.log2(n)):>7,} {s:>7,}"
                  f" {tb:>7.3f}s {td:>6.3f}s {ts:>6.3f}s {100 * (1 - d / b):>6.2f}% {pair:<22} {'yes' if same else 'NO'}")
    write_csv(os.path.join(RESULTS, "closest_pair_results.csv"),
              ["n", "batch", "brute_distances", "brute_time_s", "dc_distances", "dc_time_s", "sweep_distances",
               "sweep_time_s", "theory_n(n-1)/2", "theory_nlog2n", "min_distance", "i", "j", "identical_output"],
              rows)
    return rows


# ------------------------------------------------------------------ graphs
def style(ax, title, ylabel, log=True):
    ax.set_title(title, fontsize=10, color="#0b0b0b")
    ax.set_xlabel("batch size n (alerts)", fontsize=9, color=INK)
    ax.set_ylabel(ylabel, fontsize=9, color=INK)
    if log:
        ax.set_xscale("log")
        ax.set_yscale("log")
    ax.grid(True, which="major", color="#e4e3df", linewidth=0.8)
    ax.grid(True, which="minor", color="#f1f0ed", linewidth=0.5)
    ax.tick_params(labelsize=8, colors=INK)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(fontsize=7.5, frameon=False)


def line(ax, x, y, label, color, marker="o", dashed=False, halo=False, hollow=False):
    """One series; halo = wide translucent underlay so a series hidden by an identical one stays visible."""
    if halo:
        ax.plot(x, y, "-", color=color, linewidth=6, alpha=0.3, solid_capstyle="round")
    ax.plot(x, y, ("--" if dashed else "-"), color=color, linewidth=1.6 if not dashed else 1.1,
            marker=None if dashed else marker, markersize=5, label=label,
            markerfacecolor="white" if hollow else color)


def graphs(sort_rows, search_rows, match_rows, worst_rows, closest_rows):
    os.makedirs(GRAPHS, exist_ok=True)
    ns = BATCH_SIZES
    nlogn = [n * math.log2(n) for n in ns]
    half_sq = [n * (n - 1) / 2 for n in ns]

    def save(fig, name, header, data):
        fig.tight_layout()
        fig.savefig(os.path.join(GRAPHS, name + ".png"), dpi=150)
        plt.close(fig)
        write_csv(os.path.join(GRAPHS, name + ".csv"), header, data)

    # sorting
    rnd = [r for r in sort_rows if r[1] == "random stream"]
    nst = [r for r in sort_rows if r[1] == "nearly sorted"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    line(a1, ns, [r[2] for r in rnd], "bubble sort, random stream", BLUE, halo=True)
    line(a1, ns, [r[2] for r in nst], "bubble sort, nearly sorted", BLUE, marker="s", hollow=True)
    line(a1, ns, [r[5] for r in rnd], "merge sort, random stream", ORANGE)
    line(a1, ns, [r[5] for r in nst], "merge sort, nearly sorted", ORANGE, marker="s")
    line(a1, ns, half_sq, "theory n(n-1)/2", GREY, dashed=True)
    line(a1, ns, nlogn, "theory n log2 n", INK, dashed=True)
    style(a1, "Key comparisons", "comparisons (log scale)")
    line(a2, ns, [r[4] for r in rnd], "bubble sort, random stream", BLUE)
    line(a2, ns, [r[4] for r in nst], "bubble sort, nearly sorted", BLUE, marker="s")
    line(a2, ns, [r[7] for r in rnd], "merge sort, random stream", ORANGE)
    line(a2, ns, [r[7] for r in nst], "merge sort, nearly sorted", ORANGE, marker="s")
    style(a2, "Running time (min of repeats)", "time (s, log scale)")
    fig.suptitle("sort_alerts: corrected bubble sort vs optimised merge sort", fontsize=11)
    save(fig, "fig_sort", ["n", "input", "bubble_comparisons", "merge_comparisons", "bubble_time_s", "merge_time_s"],
         [[r[0], r[1], r[2], r[5], r[4], r[7]] for r in sort_rows])

    # searching
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    line(a1, ns, [r[4] for r in search_rows], "sequential search (corrected, wide line)", BLUE, halo=True)
    line(a1, ns, [r[7] for r in search_rows], "sentinel search (optimised)", ORANGE)
    line(a1, ns, [r[9] + r[10] for r in search_rows], "AlertIndex: n inserts + q probes", AQUA)
    line(a1, ns, [r[5] for r in search_rows], "theory: sum of match positions", GREY, dashed=True)
    style(a1, f"Comparisons for q = {QUERIES:,} look-ups", "comparisons / operations (log scale)")
    line(a2, ns, [r[6] for r in search_rows], "sequential search (corrected)", BLUE)
    line(a2, ns, [r[8] for r in search_rows], "sentinel search (optimised)", ORANGE)
    line(a2, ns, [r[11] for r in search_rows], "AlertIndex (build + look-ups)", AQUA)
    style(a2, f"Time for q = {QUERIES:,} look-ups", "time (s, log scale)")
    fig.suptitle("find_alert: sequential vs sentinel vs hash index", fontsize=11)
    save(fig, "fig_search", ["n", "sequential_comparisons", "sentinel_comparisons", "index_operations",
                             "sequential_time_s", "sentinel_time_s", "index_time_s"],
         [[r[0], r[4], r[7], r[9] + r[10], r[6], r[8], r[11]] for r in search_rows])

    # string matching
    Ls = [r[1] for r in match_rows]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    line(a1, Ls, [r[3] for r in match_rows], "brute force (corrected, wide line)", BLUE, halo=True)
    line(a1, Ls, [r[5] for r in match_rows], "Horspool (optimised)", ORANGE)
    line(a1, Ls, [r[7] for r in match_rows], "KMP (optimised alternative)", AQUA)
    line(a1, Ls, [5 * L for L in Ls], "theory 5 x L (one comparison per character)", GREY, dashed=True)
    style(a1, "Character comparisons, 5 signatures on the shift log", "char comparisons (log scale)")
    a1.set_xlabel("log text length L (characters)", fontsize=9, color=INK)
    w = [r for r in worst_rows if r[2] == "b a^9"]
    v = [r for r in worst_rows if r[2] == "a^9 b"]
    line(a2, [r[1] for r in v], [r[3] for r in v], "brute force, pattern a^9 b (wide line)", BLUE, halo=True)
    line(a2, [r[1] for r in w], [r[4] for r in w], "Horspool, pattern b a^9", ORANGE)
    line(a2, [r[1] for r in v], [r[4] for r in v], "Horspool, pattern a^9 b", ORANGE, marker="s", hollow=True)
    line(a2, [r[1] for r in v], [r[5] for r in v], "KMP, pattern a^9 b", AQUA)
    line(a2, [r[1] for r in w], [r[5] for r in w], "KMP, pattern b a^9", AQUA, marker="s", hollow=True)
    line(a2, [r[1] for r in w], [r[6] for r in w], "theory (L-m+1)m", GREY, dashed=True)
    line(a2, [r[1] for r in w], [r[7] for r in w], "theory 2L (KMP bound)", INK, dashed=True)
    style(a2, "Adversarial text 'a' x L, m = 10", "char comparisons (log scale)")
    a2.set_ylim(top=a2.get_ylim()[1] * 60)                # head-room for the legend above the lines
    a2.legend(fontsize=7, frameon=False, loc="upper left", ncol=2)
    a2.set_xlabel("text length L (characters)", fontsize=9, color=INK)
    fig.suptitle("match_signature: brute force vs Horspool vs KMP", fontsize=11)
    save(fig, "fig_matching", ["n", "text_length", "brute", "horspool", "kmp", "brute_time_s", "horspool_time_s",
                               "kmp_time_s"], [[r[0], r[1], r[3], r[5], r[7], r[4], r[6], r[8]] for r in match_rows])

    # closest pair
    rnd = [r for r in closest_rows if r[1] == "random"]
    sx = [r for r in closest_rows if r[1] == "same-x"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
    line(a1, ns, [r[2] for r in rnd], "brute force (corrected, wide line)", BLUE, halo=True)
    line(a1, ns, [r[4] for r in rnd], "divide & conquer, random", ORANGE)
    line(a1, ns, [r[4] for r in sx], "divide & conquer, same-x", ORANGE, marker="s")
    line(a1, ns, [r[6] for r in rnd], "x-sweep, random", AQUA)
    line(a1, ns, [r[6] for r in sx], "x-sweep, same-x (its worst case)", AQUA, marker="s", hollow=True)
    line(a1, ns, half_sq, "theory n(n-1)/2", GREY, dashed=True)
    line(a1, ns, nlogn, "theory n log2 n", INK, dashed=True)
    style(a1, "Distance computations", "distance computations (log scale)")
    line(a2, ns, [r[3] for r in rnd], "brute force (corrected)", BLUE)
    line(a2, ns, [r[5] for r in rnd], "divide & conquer, random", ORANGE)
    line(a2, ns, [r[5] for r in sx], "divide & conquer, same-x", ORANGE, marker="s")
    line(a2, ns, [r[7] for r in rnd], "x-sweep, random", AQUA)
    line(a2, ns, [r[7] for r in sx], "x-sweep, same-x", AQUA, marker="s")
    style(a2, "Running time (min of repeats)", "time (s, log scale)")
    fig.suptitle("closest_alert_pair: brute force vs divide & conquer vs x-sweep", fontsize=11)
    save(fig, "fig_closest_pair", ["n", "batch", "brute_distances", "dc_distances", "sweep_distances",
                                   "brute_time_s", "dc_time_s", "sweep_time_s"],
         [[r[0], r[1], r[2], r[4], r[6], r[3], r[5], r[7]] for r in closest_rows])


def summary(sort_rows, search_rows, match_rows, closest_rows):
    """Operation-count reduction and time speed-up of the optimised version at every batch size."""
    out = []
    for n in BATCH_SIZES:
        s = next(r for r in sort_rows if r[0] == n and r[1] == "random stream")
        q = next(r for r in search_rows if r[0] == n)
        m = next(r for r in match_rows if r[0] == n)
        c = next(r for r in closest_rows if r[0] == n and r[1] == "random")
        out += [[n, "sort_alerts (random)", "key comparisons", s[2], s[5], s[2] / s[5], s[4] / s[7]],
                [n, "find_alert x 1,000 (AlertIndex)", "comparisons / probes", q[4], q[9] + q[10],
                 q[4] / (q[9] + q[10]), q[6] / q[11]],
                [n, "match_signature x 5 (Horspool)", "char comparisons", m[3], m[5], m[3] / m[5], m[4] / m[6]],
                [n, "closest_alert_pair (D&C)", "distance computations", c[2], c[4], c[2] / c[4], c[3] / c[5]]]
    write_csv(os.path.join(TABLES, "comparison_summary.csv"),
              ["n", "function", "operation", "corrected", "optimised", "op_reduction_x", "time_speedup_x"],
              [r[:5] + [round(r[5], 2), round(r[6], 2)] for r in out])
    print("5) SUMMARY  optimised vs corrected: operation-count reduction / time speed-up")
    print(f"   {'function':<34}" + "".join(f"{f'n={n:,}':>17}" for n in BATCH_SIZES))
    for k in range(4):
        cells = out[k::4]                                  # row k of every batch size
        print(f"   {cells[0][1]:<34}" + "".join(f"{r[5]:>8.1f}x /{r[6]:>6.1f}x" for r in cells))
    # speed-up bar chart at the largest batch
    big = [r for r in out if r[0] == BATCH_SIZES[-1]]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    labels = ["sort_alerts\n(merge sort)", "find_alert x 1,000\n(AlertIndex)", "match_signature x 5\n(Horspool)",
              "closest_alert_pair\n(divide & conquer)"]
    xs = range(len(big))
    ax.bar([x - 0.2 for x in xs], [r[5] for r in big], width=0.38, color=BLUE, label="operation-count reduction")
    ax.bar([x + 0.2 for x in xs], [r[6] for r in big], width=0.38, color=ORANGE, label="time speed-up")
    for x, r in zip(xs, big):
        ax.text(x - 0.2, r[5] * 1.08, f"{r[5]:.0f}x", ha="center", fontsize=8, color=INK)
        ax.text(x + 0.2, r[6] * 1.08, f"{r[6]:.0f}x", ha="center", fontsize=8, color=INK)
    ax.set_xticks(list(xs), labels, fontsize=8.5)
    ax.set_yscale("log")
    ax.set_ylim(1, max(max(r[5], r[6]) for r in big) * 2.5)
    ax.set_ylabel("factor: corrected / optimised (log)", fontsize=9, color=INK)
    ax.set_title(f"Improvement factors at n = {BATCH_SIZES[-1]:,} alerts", fontsize=11)
    ax.grid(True, axis="y", color="#e4e3df", linewidth=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(GRAPHS, "fig_speedup.png"), dpi=150)
    plt.close(fig)
    write_csv(os.path.join(GRAPHS, "fig_speedup.csv"), ["function", "op_reduction_x", "time_speedup_x"],
              [[r[1], round(r[5], 2), round(r[6], 2)] for r in big])


def load(name):
    """Read a results CSV back (numbers and booleans converted) - used by --graphs-only."""
    def conv(v):
        if v in ("True", "False"):
            return v == "True"
        for f in (int, float):
            try:
                return f(v)
            except ValueError:
                pass
        return v
    with open(os.path.join(RESULTS, name), encoding="utf-8") as fh:
        return [[conv(v) for v in row] for row in list(csv.reader(fh))[1:]]


def main():
    if "--graphs-only" in sys.argv:                 # redraw the figures from the saved CSV files
        rows = [load(f) for f in ("sort_results.csv", "search_results.csv", "matching_results.csv",
                                  "matching_worst_case.csv", "closest_pair_results.csv")]
        graphs(*rows)
        print("graphs redrawn from Supporting_Files/experimental_results/*.csv")
        return
    t0 = time.perf_counter()
    print("SentinelOps alert triage - experiments: corrected (brute force) vs optimised, batch sizes",
          ", ".join(f"{n:,}" for n in BATCH_SIZES))
    print("=" * 124)
    sort_rows = exp_sort()
    search_rows = exp_search()
    match_rows, worst_rows = exp_matching()
    closest_rows = exp_closest()
    summary(sort_rows, search_rows, match_rows, closest_rows)
    graphs(sort_rows, search_rows, match_rows, worst_rows, closest_rows)
    ok = all(r[-1] for r in sort_rows + search_rows + match_rows + closest_rows)
    print(f"identical results in every experiment: {'YES' if ok else 'NO'};  CSV -> Supporting_Files/"
          f"experimental_results, graphs -> Report/graphs;  total {time.perf_counter() - t0:.0f} s")


if __name__ == "__main__":
    main()
