"""ShopSphere audit - M4 and M5 executed for real: recursive skeletons with operation counters (part (d)).

M4 current  : the recommendation engine splits the customer-product data into FOUR parts of size n/2
              (each half is replicated) and merges the partial results in linear time.
M4 redesign : replication removed - two parts of size n/2, same linear merge.
M5          : the analytics engine sorts the sales records by revenue at the current level (hand-written
              merge sort, comparisons counted) and recurses on the two halves.

Every call of size 1 costs 1 basic operation and every merge step costs 1, so the counters must equal
T(n) = 4T(n/2) + n -> 2n^2 - n and T(n) = 2T(n/2) + n -> n log2 n + n exactly. For M5 the counter holds
the real number of key comparisons made by the sorts; its ratio to n log2^2 n must level off.
Wall-clock times are measured as secondary evidence of the "what happens when data doubles" answer.
"""
import math
import random

from audit_common import (banner, check, fmt_int, min_time, print_table, section, verdict,
                          write_csv)


# --------------------------------------------------------------------------- M4 (both designs)
def recommend(scores, replicated, counter):
    """Recursive recommendation engine; returns one combined score per item of `scores`.

    replicated=True  -> 4 recursive calls on halves (current design, a = 4)
    replicated=False -> 2 recursive calls on halves (redesign, a = 2)
    counter[0] counts basic operations: 1 per base case + 1 per merged output element.
    """
    n = len(scores)
    if n == 1:
        counter[0] += 1                                   # T(1) = 1
        return [scores[0]]
    left, right = scores[: n // 2], scores[n // 2:]
    if replicated:                                        # replicated partitions: L, R, L, R
        parts = [recommend(p, True, counter) for p in (left, right, left, right)]
        halves = [[(a + b) / 2 for a, b in zip(parts[0], parts[2])],
                  [(a + b) / 2 for a, b in zip(parts[1], parts[3])]]
    else:
        halves = [recommend(left, False, counter), recommend(right, False, counter)]
    merged = []
    for half in halves:                                   # linear-time merge: n basic operations
        for value in half:
            counter[0] += 1
            merged.append(value)
    return merged


# --------------------------------------------------------------------------- M5
def merge_sort_by_revenue(records, counter):
    """Hand-written merge sort on revenue; counter[0] counts key comparisons."""
    if len(records) <= 1:
        return records
    mid = len(records) // 2
    left = merge_sort_by_revenue(records[:mid], counter)
    right = merge_sort_by_revenue(records[mid:], counter)
    out, a, b = [], 0, 0
    while a < len(left) and b < len(right):
        counter[0] += 1
        if left[a] >= right[b]:                           # highest revenue first
            out.append(left[a])
            a += 1
        else:
            out.append(right[b])
            b += 1
    return out + left[a:] + right[b:]


def sales_analytics(records, counter, ranking_ok):
    """M5: sort this level's records by revenue, then recurse on both halves (T(1) = 1)."""
    n = len(records)
    if n == 1:
        counter[0] += 1
        return
    ranked = merge_sort_by_revenue(records, counter)
    ranking_ok[0] &= ranked == sorted(records, reverse=True)   # reference check
    sales_analytics(records[: n // 2], counter, ranking_ok)
    sales_analytics(records[n // 2:], counter, ranking_ok)


def count_ops(func, data, *extra):
    """Run one of the engines with a fresh counter and return the counted basic operations."""
    counter = [0]
    func(data, *extra, counter) if extra else func(data, counter)
    return counter[0]


def run_m4(replicated, exponents, closed):
    """Counted operations and timings of M4 for n = 2^k; returns (rows, csv_rows, all_match)."""
    rng = random.Random(42)
    rows, csv_rows, prev, all_ok = [], [], None, True
    for k in exponents:
        n = 2 ** k
        data = [rng.random() for _ in range(n)]
        counter = [0]
        recommend(data, replicated, counter)
        secs = min_time(recommend, data, replicated, [0], repeats=3)
        match = counter[0] == closed(n, k)
        all_ok &= match
        rows.append([fmt_int(n), fmt_int(counter[0]), fmt_int(closed(n, k)), verdict(match),
                     f"{counter[0] / prev[0]:.3f}" if prev else "-", f"{secs:.4f}",
                     f"{secs / prev[1]:.2f}" if prev else "-"])
        csv_rows.append([n, counter[0], closed(n, k), f"{secs:.6f}"])
        prev = (counter[0], secs)
    return rows, csv_rows, all_ok


def main():
    banner("ShopSphere audit - M4 / M5 recursive engines executed with operation counters")
    headers = ["n", "ops counted", "closed form", "match", "ops ratio", "time (s)", "time ratio"]

    section("1. M4 current design, 4 replicated parts: T(n) = 4T(n/2) + n = 2n^2 - n")
    rows, csv_cur, ok = run_m4(True, range(4, 11), lambda n, k: 2 * n * n - n)
    print_table(headers, rows)

    section("2. M4 redesign, 2 parts: T(n) = 2T(n/2) + n = n log2 n + n")
    rows, csv_new, ok2 = run_m4(False, range(4, 17), lambda n, k: n * k + n)
    print_table(headers, rows)
    print("Doubling n: current design ~4x the work, redesign ~2(lg n + 2)/(lg n + 1), just over 2x.")
    ok &= ok2
    write_csv("m4_simulation.csv", ["design", "n", "ops_counted", "closed_form", "seconds"],
              [["current", *r] for r in csv_cur] + [["redesign", *r] for r in csv_new])

    section("3. M5 analytics: real merge-sort comparisons at every level vs Theta(n log^2 n)")
    rng = random.Random(7)
    rows, csv_rows, prev = [], [], None
    for k in range(6, 15):
        n = 2 ** k
        records = [round(rng.uniform(10, 5000), 2) for _ in range(n)]
        counter, ranking_ok = [0], [True]
        sales_analytics(records, counter, ranking_ok)
        model = n * k * (k + 1) // 2 + n              # recurrence with sort cost exactly n log2 n
        ok &= ranking_ok[0]
        rows.append([fmt_int(n), fmt_int(counter[0]), fmt_int(model), f"{counter[0] / model:.3f}",
                     f"{counter[0] / (n * k * k):.4f}", f"{counter[0] / (n * k):.2f}",
                     f"{counter[0] / prev:.2f}" if prev else "-", verdict(ranking_ok[0])])
        csv_rows.append([n, counter[0], model])
        prev = counter[0]
    print_table(["n", "comparisons", "model T(n)", "real/model", "/(n lg^2 n)", "/(n lg n)",
                 "T(2n)/T(n)", "sorted ok"], rows)
    write_csv("m5_simulation.csv", ["n", "comparisons_counted", "model_closed_form"], csv_rows)
    print("Real comparisons / (n log2^2 n) levels off near a constant while / (n log2 n) keeps rising:")
    print("the engine is Theta(n log^2 n), not Theta(n log n). (Merge sort uses slightly fewer than")
    print("n log2 n comparisons per level, so real/model stays a little below 1.)")
    print(f"\nSelf-check (counters equal closed forms, every level sorted correctly): {verdict(ok)}")


if __name__ == "__main__":
    main()
