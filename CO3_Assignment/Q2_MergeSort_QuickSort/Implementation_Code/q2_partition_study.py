"""Q2 - partition-quality study of Quick Sort with the LAST-element pivot (Lomuto), compared with Merge Sort.

Student A's task: design one input that gives BALANCED partitions and one that gives SEVERELY UNBALANCED
partitions for the group's stated pivot strategy (pivot = last element, Lomuto partition), then record the
partition sizes and the maximum recursion depth. Student B compares the recursion structure with Merge Sort.

Designed inputs (values 0..n-1 are deadline ranks; any distinct deadlines behave the same):
  balanced  - built recursively so that the last element of EVERY sub-array is its median
              -> every partition splits m elements into floor((m-1)/2) | ceil((m-1)/2)
  90:10     - built the same way with the pivot at rank 0.9(m-1)  (the viva "90:10 split" transfer question)
  random    - a random permutation (seed 42)
  sorted    - already sorted export: the last element is always the maximum -> (m-1) | 0
  reversed  - reverse-sorted export: the last element is the minimum -> 0 | (m-1) on the first call

Why the construction works: Lomuto with x = a[hi] leaves a prefix of small keys in place when they come first,
and its final swap(a[i+1], a[hi]) moves the FIRST element of the right part to the end. So if the designed right
part is DR, the input must hold [DR[-1]] + DR[:-1]; after partitioning the right sub-array is exactly DR.

Run:  py q2_partition_study.py      (writes results/q2_partition_study.csv and results/q2_depth_sweep.csv)
"""
import csv
import math
import os
import random

from q2_sorting import designed_input, merge_sort, quick_sort

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
INPUTS = ("balanced", "90:10", "random", "sorted", "reversed")


def make_input(kind, n, seed=42):
    """One of the five study inputs of size n."""
    if kind == "balanced":
        return designed_input(n, 0.5)
    if kind == "90:10":
        return designed_input(n, 0.9)
    if kind == "random":
        a = list(range(n))
        random.Random(seed).shuffle(a)
        return a
    if kind == "sorted":
        return list(range(n))
    return list(range(n - 1, -1, -1))


def balance(record):
    """(mean, worst) of min(L, R) / (L + R) over all partitions with L + R > 0 (0.5 = perfect, 0 = useless)."""
    ratios = [min(l, r) / (l + r) for _, l, r in record if l + r > 0]
    return sum(ratios) / len(ratios), min(ratios)


def worst_large(record, min_size=32):
    """Worst balance among partitions of at least min_size elements (small sub-arrays round badly)."""
    ratios = [min(l, r) / (l + r) for _, l, r in record if l + r + 1 >= min_size]
    return min(ratios) if ratios else float("nan")


def predicted_depth(n, left_fraction):
    """Depth of the longest branch when every partition of m keeps int(f(m - 1)) on the larger side."""
    m, d = n, 0
    while m > 1:
        m = int(left_fraction * (m - 1)) if left_fraction != 0.5 else m // 2
        d += 1
    return d


def largest_by_depth(record, n):
    """Largest sub-array size handled at each recursion depth (depth 0 = whole list)."""
    big = {}
    for d, l, r in record:
        big[d] = max(big.get(d, 0), l + r + 1)
    return [big[d] for d in sorted(big)]


def study(kind, n):
    """Run last-pivot Quick Sort and Merge Sort on one input; return a dict of the recorded quantities."""
    data = make_input(kind, n)
    qrec, mrec = [], []
    a = list(data)
    qs = quick_sort(a, "last", record=qrec)
    assert a == sorted(data)
    b = list(data)
    ms = merge_sort(b, record=mrec)
    assert b == sorted(data)
    mean_b, worst_b = balance(qrec)
    severe = sum(1 for _, l, r in qrec if min(l, r) < 0.1 * (l + r)) / len(qrec)
    return {"input": kind, "n": n, "partitions": len(qrec), "qs_depth": qs.max_depth,
            "qs_comparisons": qs.comparisons, "qs_moves": qs.moves, "balance_mean": mean_b,
            "balance_worst": worst_b, "worst_m32": worst_large(qrec), "severe_fraction": severe,
            "ms_divisions": len(mrec), "ms_depth": ms.max_depth, "ms_comparisons": ms.comparisons,
            "ms_balance_worst": balance(mrec)[1], "qrec": qrec, "largest": largest_by_depth(qrec, n)}


def splits_at(record, depth, limit=4):
    """Text 'L|R' of the partitions at a given depth (at most `limit`, left to right)."""
    parts = [f"{l}|{r}" for d, l, r in record if d == depth]
    return " ".join(parts[:limit]) + (" ..." if len(parts) > limit else "")


def main():
    print("=" * 120)
    print("Q2 PARTITION STUDY - Quick Sort, pivot = LAST element (Lomuto), on designed inputs; Merge Sort on the same")
    print("=" * 120)
    rows, cache = [], {}
    for n in (1023, 4095, 8191):
        lg = math.ceil(math.log2(n))
        print(f"\nn = {n:,}  ceil(log2 n) = {lg}  n - 1 = {n - 1:,}  n log2 n = {n * math.log2(n):,.0f}"
              f"  n(n-1)/2 = {n * (n - 1) // 2:,}  perfect (n+1)lg(n+1)-2n = "
              f"{(n + 1) * round(math.log2(n + 1)) - 2 * n:,}")
        print(f"{'input':>9} | {'partitions':>10} {'QS depth':>8} {'QS comparisons':>14} {'/ n lg n':>8} |"
              f" {'balance mean':>12} {'worst':>6} {'m>=32':>6} {'<10:90':>7} | {'MS depth':>8} {'MS comps':>9}"
              f" {'MS worst':>8}")
        for kind in INPUTS:
            r = study(kind, n)
            cache[(kind, n)] = r
            rows.append({k: v for k, v in r.items() if k not in ("qrec", "largest")})
            print(f"{kind:>9} | {r['partitions']:>10,} {r['qs_depth']:>8,} {r['qs_comparisons']:>14,} "
                  f"{r['qs_comparisons'] / (n * math.log2(n)):>8.2f} | {r['balance_mean']:>12.3f} "
                  f"{r['balance_worst']:>6.3f} {r['worst_m32']:>6.3f} {r['severe_fraction']:>6.1%} | "
                  f"{r['ms_depth']:>8} "
                  f"{r['ms_comparisons']:>9,} {r['ms_balance_worst']:>8.3f}")
    print("   balance = min(L, R)/(L + R) per partition (0.5 perfect, 0 empty side); m>=32 = worst balance of"
          " partitions\n   with >= 32 keys; <10:90 = share of partitions worse than 10:90 (mostly tiny sub-arrays);"
          "\n   MS = Merge Sort on the same input; MS worst = worst balance of its divisions")

    n = 1023
    print(f"\nPartition sizes L|R (elements left | right of the pivot) at the first recursion levels, n = {n:,}")
    for kind in INPUTS:
        rec = cache[(kind, n)]["qrec"]
        print(f"{kind:>9} | d0: {splits_at(rec, 0):<10} d1: {splits_at(rec, 1, 2):<16} "
              f"d2: {splits_at(rec, 2, 3)}")
    print(f"\nLargest sub-array size at depth d, n = 8,191 (how fast the problem shrinks)")
    depths = (0, 1, 2, 3, 5, 10, 20, 50, 100)
    print(f"{'input':>9} | " + " ".join(f"{'d=' + str(d):>7}" for d in depths))
    for kind in INPUTS:
        big = cache[(kind, 8191)]["largest"]
        print(f"{kind:>9} | " + " ".join(f"{big[d]:>7,}" if d < len(big) else f"{'-':>7}" for d in depths))

    print("\nMaximum recursion depth against n (n = 2^k - 1) with the theoretical heights")
    print(f"{'n':>6} | {'balanced':>8} {'log2(n+1)-1':>11} | {'90:10':>6} {'pred.':>5} {'log10/9 n':>9} | "
          f"{'random':>6} | {'sorted':>6} {'n-1':>6} | {'Merge':>5} {'ceil lg n':>9}")
    sweep = []
    for k in range(4, 14):
        n = 2 ** k - 1
        res = {kind: cache.get((kind, n)) or study(kind, n) for kind in ("balanced", "90:10", "random", "sorted")}
        row = {"n": n, "balanced": res["balanced"]["qs_depth"], "theory_balanced": k - 1,
               "90:10": res["90:10"]["qs_depth"], "predicted_90_10": predicted_depth(n, 0.9),
               "theory_90_10": round(math.log(n) / math.log(10 / 9), 1),
               "random": res["random"]["qs_depth"], "sorted": res["sorted"]["qs_depth"], "theory_sorted": n - 1,
               "merge": res["balanced"]["ms_depth"], "theory_merge": math.ceil(math.log2(n))}
        sweep.append(row)
        print(f"{n:>6,} | {row['balanced']:>8} {row['theory_balanced']:>11} | {row['90:10']:>6} "
              f"{row['predicted_90_10']:>5} {row['theory_90_10']:>9} | {row['random']:>6} | "
              f"{row['sorted']:>6,} {row['theory_sorted']:>6,} | "
              f"{row['merge']:>5} {row['theory_merge']:>9}")

    print("   pred. = longest branch of m -> int(0.9(m - 1)); log10/9 n = asymptotic 90:10 height (upper estimate,"
          " it ignores\n   that the pivot itself leaves every sub-array)")

    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "q2_partition_study.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})
    with open(os.path.join(RESULTS, "q2_depth_sweep.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sweep[0]))
        w.writeheader()
        w.writerows(sweep)
    with open(os.path.join(RESULTS, "q2_largest_by_depth.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["input", "depth", "largest_subarray"])
        for kind in INPUTS:
            for d, size in enumerate(cache[(kind, 8191)]["largest"]):
                w.writerow([kind, d, size])
    print("\nCSV written to results/: q2_partition_study.csv, q2_depth_sweep.csv, q2_largest_by_depth.csv")


if __name__ == "__main__":
    main()
