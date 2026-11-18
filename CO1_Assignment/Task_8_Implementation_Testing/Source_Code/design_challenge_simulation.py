"""
design_challenge_simulation.py - Task 12, Day-4 Design Challenge.

Changed requirement: 50,000 search requests per hour on a database of 1,000,000 student records;
new records are added only once per day.  This program measures, on the real 1,000,000-record dataset,
what one day of operation costs for every design and every way of absorbing the daily batch:

  STEP 1  initial preprocessing (paid once at deployment)
  STEP 2  one simulated day: 24 hours x 50,000 searches (80% successful, 20% unsuccessful, seed = hour).
          B and both hash tables execute ALL 1,200,000 searches; sequential search (A) executes the
          first 200 searches of hour 1 and is extrapolated (a full hour would need ~25 min in Python)
  STEP 3  nightly update with a batch of b = 5,000 new records, six strategies:
            A   append to the unsorted list                                  Theta(b)
            B1  re-sort all n + b records with merge sort                     Theta((n+b) log(n+b))
            B2  merge sort the batch only, then merge it into the array       Theta(n + b log b)
            C1  rebuild the whole hash table                                   Theta(n + b)
            C2  insert the batch into the Task-11 table (sized for n)          Theta(b) + a rehash Theta(n)
            C3  insert the batch into a table built with reserved capacity     Theta(b), never rehashes
          every result is verified (new keys found, old keys still found, absent keys rejected)
  STEP 4  day 2: one hour of 50,000 searches that also asks for the new records
  STEP 5  cost per day = nightly update + 24 hours of searching, CPU utilisation, headroom
  STEP 6  sensitivity of the daily cost to the search rate (10 ... 10^7 searches per hour)
Outputs: CSV files (Task_12_Design_Challenge + Report/Tables_and_Graphs) and two graphs.
"""
import csv
import gc
import math
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from search_algorithms import (OpCounter, StudentHashTable, binary_search, hash_search,  # noqa: E402
                               merge_sort_records, merge_sorted_batch, sequential_search)
from student_records import REG_MAX, REG_MIN, generate_new_records, generate_records  # noqa: E402

N_RECORDS = 1_000_000
SEARCHES_PER_HOUR = 50_000
HIT_SHARE = 0.8
DAILY_BATCH = 5_000
RESERVED_CAPACITY = 2_000_000            # C3: room for 200 busy days of 5,000 new records at alpha <= 0.75
SEQ_SAMPLE = 200
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SOURCE_DIR, "..", ".."))
TASK12_DIR = os.path.join(ROOT, "Task_12_Design_Challenge")
GRAPH_DIR = os.path.join(ROOT, "Report", "Tables_and_Graphs")


def write_csv(name, header, rows):
    for folder in (TASK12_DIR, GRAPH_DIR):
        with open(os.path.join(folder, name), "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            writer.writerows(rows)


def hourly_queries(records, key_set, hour):
    """50,000 registration numbers for one hour: 80% stored (random record), 20% absent, shuffled."""
    rng = random.Random(1_000 + hour)
    n_hits = int(SEARCHES_PER_HOUR * HIT_SHARE)
    queries = [records[int(rng.random() * len(records))].reg_no for _ in range(n_hits)]
    while len(queries) < SEARCHES_PER_HOUR:
        key = REG_MIN + int(rng.random() * (REG_MAX - REG_MIN + 1))
        if key not in key_set:
            queries.append(key)
    rng.shuffle(queries)
    return queries, n_hits


def run_searches(search, structure, queries):
    """Execute a batch of searches (GC off); return (comparisons, other ops, seconds, records found)."""
    counter, found = OpCounter(), 0
    gc.collect()
    gc.disable()
    start = time.perf_counter()
    for key in queries:
        if search(structure, key, counter) is not None:
            found += 1
    seconds = time.perf_counter() - start
    gc.enable()
    return counter.comparisons, counter.hash_computations + counter.calls, seconds, found


def timed_update(function):
    """Run one update strategy (GC off) and return (result, counter, seconds)."""
    counter = OpCounter()
    gc.collect()
    gc.disable()
    start = time.perf_counter()
    result = function(counter)
    seconds = time.perf_counter() - start
    gc.enable()
    return result, counter, seconds


def build_reserved(records, counter):
    """C3: hash table created with capacity reserved for RESERVED_CAPACITY records."""
    table = StudentHashTable(RESERVED_CAPACITY)
    for record in records:
        table.insert(record, counter)
    return table


def insert_batch(table, batch, counter):
    for record in batch:
        table.insert(record, counter)
    return table


def verify(search, structure, batch, old_sample, absent_sample):
    """True if every new key and every sampled old key is found and every absent key is rejected."""
    c = OpCounter()
    return (all(search(structure, r.reg_no, c) is r for r in batch)
            and all(search(structure, r.reg_no, c) is r for r in old_sample)
            and all(search(structure, k, c) is None for k in absent_sample))


def main():
    start_all = time.perf_counter()
    print("=" * 112)
    print(f" Day-4 design challenge: {SEARCHES_PER_HOUR:,} searches/hour on {N_RECORDS:,} records, "
          f"{DAILY_BATCH:,} new records once per day")
    print("=" * 112)
    records = generate_records(N_RECORDS)
    key_set = {r.reg_no for r in records}

    # STEP 1 - initial preprocessing (once)
    sorted_records, c_sort, t_sort = timed_update(lambda c: merge_sort_records(records, c))
    table, c_tab, t_tab = timed_update(lambda c: StudentHashTable.build(records, c))
    table3, c_tab3, t_tab3 = timed_update(lambda c: build_reserved(records, c))
    print("STEP 1 - initial preprocessing, paid once at deployment")
    print(f"  B  merge sort of 1,000,000 records        : {c_sort.comparisons:>12,} comparisons "
          f"{t_sort:8.2f} s")
    print(f"  C  hash table sized for n (Task 11 design): {c_tab.hash_computations + c_tab.comparisons:>12,} "
          f"operations  {t_tab:8.2f} s   m = {table.size:,}, alpha = {table.load_factor:.3f}")
    ops3 = c_tab3.hash_computations + c_tab3.comparisons
    print(f"  C3 hash table, capacity for {RESERVED_CAPACITY:,}    : {ops3:>12,} operations  {t_tab3:8.2f} s   "
          f"m = {table3.size:,}, alpha = {table3.load_factor:.3f}")

    # STEP 2 - one simulated day of searching
    print(f"\nSTEP 2 - day 1: 24 hours x {SEARCHES_PER_HOUR:,} searches ({HIT_SHARE:.0%} successful), "
          f"every search executed for B, C and C3")
    print(f"  {'hour':>4} | {'B comparisons':>13} {'B s':>6} | {'C comparisons':>13} {'C s':>6} | "
          f"{'C3 comparisons':>14} {'C3 s':>6} | {'found (B/C/C3)':>20}")
    hourly_rows, day = [], {"B": [0, 0, 0.0], "C": [0, 0, 0.0], "C3": [0, 0, 0.0]}
    for hour in range(1, 25):
        queries, n_hits = hourly_queries(records, key_set, hour)
        out = {"B": run_searches(binary_search, sorted_records, queries),
               "C": run_searches(hash_search, table, queries),
               "C3": run_searches(hash_search, table3, queries)}
        for name, (cmp_, ops, sec, _) in out.items():
            day[name][0] += cmp_
            day[name][1] += ops
            day[name][2] += sec
        ok = all(v[3] == n_hits for v in out.values())
        found = "/".join(f"{v[3]:,}" for v in out.values())
        print(f"  {hour:>4} | {out['B'][0]:>13,} {out['B'][2]:>6.3f} | {out['C'][0]:>13,} "
              f"{out['C'][2]:>6.3f} | {out['C3'][0]:>14,} {out['C3'][2]:>6.3f} | {found:>20} "
              f"{'ok' if ok else 'ERROR'}")
        hourly_rows.append([hour, out["B"][0], round(out["B"][2], 4), out["C"][0], round(out["C"][2], 4),
                            out["C3"][0], round(out["C3"][2], 4), n_hits, ok])
        if hour == 1:
            sample = queries[:SEQ_SAMPLE]
    write_csv("design_challenge_hourly.csv",
              ["hour", "B_comparisons", "B_seconds", "C_comparisons", "C_seconds", "C3_comparisons",
               "C3_seconds", "successful_searches", "all_correct"], hourly_rows)
    a_cmp, _, a_sec, a_found = run_searches(sequential_search, records, sample)
    a_hits = sum(1 for k in sample if k in key_set)
    scale = SEARCHES_PER_HOUR / SEQ_SAMPLE
    print(f"  A sequential: {SEQ_SAMPLE} searches of hour 1 ({a_hits} successful, found {a_found}) -> "
          f"{a_cmp / SEQ_SAMPLE:,.0f} comparisons and {a_sec / SEQ_SAMPLE * 1e3:.1f} ms per search")
    print(f"  A extrapolated to one hour: {a_cmp * scale:,.0f} comparisons, {a_sec * scale:,.0f} s of CPU "
          f"({a_sec * scale / 36:.1f}% of one core)")
    day["A"] = [a_cmp * scale * 24, 0, a_sec * scale * 24]
    for name in ("B", "C", "C3"):
        print(f"  {name:<3} whole day: {day[name][0]:>13,} comparisons, {day[name][2]:7.2f} s "
              f"({day[name][2] / 1_200_000 * 1e6:.2f} us per search)")

    # STEP 3 - nightly update with the daily batch
    batch = generate_new_records(DAILY_BATCH, key_set, seed=2026)
    rng = random.Random(99)
    old_sample = rng.sample(records, 1_000)
    new_key_set = key_set | {r.reg_no for r in batch}
    absent_sample = []
    while len(absent_sample) < 1_000:
        k = REG_MIN + int(rng.random() * (REG_MAX - REG_MIN + 1))
        if k not in new_key_set:
            absent_sample.append(k)
    print(f"\nSTEP 3 - nightly update: b = {DAILY_BATCH:,} new records (seed 2026) added to n = {N_RECORDS:,}")
    print(f"  {'strategy':<52} {'comparisons':>12} {'other ops':>11} {'seconds':>9} {'rehash':>6}  verified")
    updates = {}
    list_a = list(records)
    _, c, sec = timed_update(lambda c: list_a.extend(batch))
    updates["A"] = (0, len(batch), sec, 0, verify(sequential_search, list_a, batch[-20:], old_sample[:20],
                                                   absent_sample[:5]))
    del list_a
    merged_b1, c, sec = timed_update(lambda c: merge_sort_records(records + batch, c))
    updates["B1"] = (c.comparisons, c.moves, sec, 0, verify(binary_search, merged_b1, batch, old_sample,
                                                            absent_sample))
    merged_b2, c, sec = timed_update(lambda c: merge_sorted_batch(sorted_records, batch, c))
    same = [r.reg_no for r in merged_b1] == [r.reg_no for r in merged_b2]
    updates["B2"] = (c.comparisons, c.moves, sec, 0,
                     same and verify(binary_search, merged_b2, batch, old_sample, absent_sample))
    del merged_b1
    rebuilt, c, sec = timed_update(lambda c: StudentHashTable.build(records + batch, c))
    updates["C1"] = (c.comparisons, c.hash_computations, sec, 0, verify(hash_search, rebuilt, batch, old_sample,
                                                                       absent_sample))
    del rebuilt
    _, c, sec = timed_update(lambda c: insert_batch(table, batch, c))
    updates["C2"] = (c.comparisons, c.hash_computations, sec, table.resizes,
                     verify(hash_search, table, batch, old_sample, absent_sample))
    _, c, sec = timed_update(lambda c: insert_batch(table3, batch, c))
    updates["C3"] = (c.comparisons, c.hash_computations, sec, table3.resizes,
                     verify(hash_search, table3, batch, old_sample, absent_sample))
    labels = {"A": "A  append batch to the unsorted list",
              "B1": "B1 re-sort all n + b records (merge sort)",
              "B2": "B2 sort batch, merge into sorted array",
              "C1": "C1 rebuild the whole hash table",
              "C2": "C2 insert batch, Task-11 table sized for n",
              "C3": "C3 insert batch, table with reserved capacity"}
    update_rows = []
    for key, (cmp_, other, sec, rehash, ok) in updates.items():
        print(f"  {labels[key]:<52} {cmp_:>12,} {other:>11,} {sec:>9.4f} {rehash:>6}  "
              f"{'PASS' if ok else 'FAIL'}")
        update_rows.append([key, labels[key][3:], cmp_, other, round(sec, 5), rehash, ok])
    print(f"  after the update: C2 m = {table.size:,} (alpha {table.load_factor:.3f}), C3 m = {table3.size:,} "
          f"(alpha {table3.load_factor:.3f}); B1 array == B2 array: {same}")
    write_csv("design_challenge_updates.csv", ["strategy", "description", "comparisons", "other_ops", "seconds",
                                               "rehashes", "verified"], update_rows)

    # STEP 4 - day 2: the new records are searchable
    all_records = records + batch
    queries, n_hits = hourly_queries(all_records, new_key_set, 25)
    new_asked = sum(1 for k in queries if k in {r.reg_no for r in batch})
    print(f"\nSTEP 4 - day 2, hour 1: {SEARCHES_PER_HOUR:,} searches over {len(all_records):,} records "
          f"({new_asked} of them for new records)")
    for name, search, structure in (("B2", binary_search, merged_b2), ("C3", hash_search, table3)):
        cmp_, _, sec, found = run_searches(search, structure, queries)
        print(f"  {name}: {cmp_:>10,} comparisons, {sec:6.3f} s, found {found:,} of {n_hits:,} "
              f"{'PASS' if found == n_hits else 'FAIL'}")

    # STEP 5 - cost per day
    print("\nSTEP 5 - cost per day = nightly update + 24 h x 50,000 searches (one CPU core, Python)")
    print(f"  {'design':<52} {'ops per day':>15} {'CPU s/day':>10} {'search % core':>13} {'headroom':>9}")
    designs = [("A", "A", "A"), ("B1", "B", "B1"), ("B2", "B", "B2"), ("C1", "C", "C1"), ("C2", "C", "C2"),
               ("C3", "C3", "C3")]
    daily_rows, unit = [], {}
    for name, search_key, update_key in designs:
        u_cmp, u_other, u_sec = updates[update_key][:3]
        ops = day[search_key][0] + day[search_key][1] + u_cmp + u_other
        total = day[search_key][2] + u_sec
        busy = day[search_key][2] / 24 / 3600
        unit[name] = (u_sec, day[search_key][2] / (24 * SEARCHES_PER_HOUR))
        print(f"  {labels[name]:<52} {ops:>15,.0f} {total:>10.2f} {busy * 100:>12.4f}% {1 / busy:>8,.0f}x")
        daily_rows.append([name, labels[name][3:], round(ops), round(u_sec, 5), round(day[search_key][2], 4),
                           round(total, 4), round(busy * 100, 6), round(1 / busy, 1),
                           round(unit[name][1] * 1e6, 4)])
    write_csv("design_challenge_daily_cost.csv", ["design", "description", "operations_per_day",
                                                  "update_seconds",
                                                  "search_seconds_per_day", "total_cpu_seconds_per_day",
                                                  "search_cpu_utilisation_percent", "load_headroom_factor",
                                                  "us_per_search"], daily_rows)

    # STEP 6 - sensitivity to the search rate
    rates = [10 ** (i / 4) for i in range(0, 29)]
    sens_rows = [[round(r, 2)] + [round(unit[d][0] + 24 * r * unit[d][1], 6) for d, _, _ in designs]
                 for r in rates]
    write_csv("design_challenge_sensitivity.csv",
              ["searches_per_hour"] + [f"{d}_cpu_s_per_day" for d, _, _ in designs], sens_rows)
    print("\nSTEP 6 - search rate at which each design's daily cost equals sequential search (A)")
    for d in ("B1", "B2", "C1", "C2", "C3"):
        rate = (unit[d][0] - unit["A"][0]) / (24 * (unit["A"][1] - unit[d][1]))
        if rate > 0:
            print(f"  {labels[d]:<52} pays off above {rate:10.3f} searches per hour")
        else:
            print(f"  {labels[d]:<52} pays off at every rate (its update is no dearer than A's append)")
    make_graphs(daily_rows, rates, unit, designs, labels)
    best = min(daily_rows, key=lambda row: row[5])
    print(f"\nLowest total daily cost: {best[0]} ({best[1]}) = {best[5]:.2f} CPU s/day "
          f"vs {daily_rows[0][5]:,.0f} s/day for sequential search")
    print(f"Total run time {time.perf_counter() - start_all:.1f} s; CSV + graphs written to Task_12 and "
          f"Report/Tables_and_Graphs")


def make_graphs(daily_rows, rates, unit, designs, labels):
    colors = {"A": "#d62728", "B1": "#1f77b4", "B2": "#17becf",
              "C1": "#98df8a", "C2": "#bcbd22", "C3": "#2ca02c"}
    fig, ax = plt.subplots(figsize=(10, 4.8))
    names = [row[0] for row in daily_rows]
    updates = [row[3] for row in daily_rows]
    searches = [row[4] for row in daily_rows]
    y = range(len(names))
    ax.barh([i + 0.2 for i in y], searches, height=0.4, color="#4c72b0", label="24 h of searching (CPU s/day)")
    ax.barh([i - 0.2 for i in y], updates, height=0.4, color="#dd8452", label="nightly update (CPU s/day)")
    for i, (s, u) in enumerate(zip(searches, updates)):
        ax.text(s * 1.15, i + 0.2, f"{s:,.2f} s", va="center", fontsize=8)
        ax.text(u * 1.15, i - 0.2, f"{u:,.4f} s", va="center", fontsize=8)
    ax.set_yticks(list(y))
    ax.set_yticklabels([labels[n] for n in names], fontsize=8)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(1e-4, 1e6)
    ax.set_xlabel("CPU seconds per day (log scale)")
    ax.set_title("Cost of one day: 1,200,000 searches + one batch of 5,000 new records (n = 1,000,000)",
                 fontsize=11)
    ax.grid(True, axis="x", which="both", alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(GRAPH_DIR, "fig7_daily_cost_by_design.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.2))
    for d, _, _ in designs:
        ax.plot(rates, [unit[d][0] + 24 * r * unit[d][1] for r in rates], color=colors[d], lw=2,
                label=labels[d])
    ax.axvline(SEARCHES_PER_HOUR, color="grey", ls=":", lw=1)
    ax.text(SEARCHES_PER_HOUR, 0.97, " 50,000 searches/hour", transform=ax.get_xaxis_transform(), fontsize=8,
            color="grey", va="top")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("search requests per hour (log scale)")
    ax.set_ylabel("CPU seconds per day (log scale)")
    ax.set_title("Daily cost vs search frequency (measured unit costs, n = 1,000,000, b = 5,000/day)",
                 fontsize=11)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(GRAPH_DIR, "fig8_daily_cost_vs_search_rate.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
