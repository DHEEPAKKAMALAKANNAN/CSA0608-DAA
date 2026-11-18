"""Q1 - Sorting under different data conditions (E-commerce order processing).

Problem
    A fulfilment centre sorts customer orders by a dispatch priority score (ascending: score 1 is dispatched
    first).  This module implements the three brute-force sorting algorithms that the team is considering,
    each instrumented with explicit operation counters:

        * Selection Sort  - comparisons, swaps
        * Bubble Sort     - comparisons, swaps, passes  (uses the "swapped" early-exit flag)
        * Insertion Sort  - comparisons, shifts

    An order record is a tuple (priority_score, order_id).  Only the score is compared; the order_id lets us
    check stability (equal scores must keep their arrival order).

    It also provides inversion_profile(), an O(n log n) Fenwick-tree routine that predicts the exact counts
    from properties of the input (inversions I, maximum left-displacement L, new strict minima F).  It is used
    only to cross-check the counters - it is not part of the sorting algorithms.

Run this file to execute the correctness tests and a small demonstration.
"""

import random


# ----------------------------------------------------------------------------------------------- algorithms
def selection_sort(records):
    """Selection Sort on a copy of `records`; returns (sorted_list, counters).

    Each pass scans the whole unsorted suffix for the minimum score, then swaps it into place (at most one
    swap per pass, skipped when the minimum is already in place)."""
    a = list(records)
    n = len(a)
    comparisons = swaps = 0
    for i in range(n - 1):
        smallest = i
        for j in range(i + 1, n):
            comparisons += 1
            if a[j][0] < a[smallest][0]:
                smallest = j
        if smallest != i:
            a[i], a[smallest] = a[smallest], a[i]
            swaps += 1
    return a, {"comparisons": comparisons, "moves": swaps, "writes": 2 * swaps, "passes": max(n - 1, 0)}


def bubble_sort(records):
    """Bubble Sort with the early-exit flag on a copy of `records`; returns (sorted_list, counters).

    Pass p compares neighbours a[j], a[j+1] for j = 0 .. n-2-p and swaps them when out of order (strict '>'
    keeps equal keys in arrival order).  If a whole pass makes no swap the list is sorted and we stop."""
    a = list(records)
    n = len(a)
    comparisons = swaps = passes = 0
    for p in range(n - 1):
        swapped = False
        passes += 1
        for j in range(n - 1 - p):
            comparisons += 1
            if a[j][0] > a[j + 1][0]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:                       # early exit: no inversions left
            break
    return a, {"comparisons": comparisons, "moves": swaps, "writes": 2 * swaps, "passes": passes}


def insertion_sort(records):
    """Insertion Sort on a copy of `records`; returns (sorted_list, counters).

    a[0..i-1] is always sorted; a[i] is saved, larger keys are shifted one place right, and the saved record is
    written into the gap.  Every shift removes exactly one inversion."""
    a = list(records)
    n = len(a)
    comparisons = shifts = placements = 0
    for i in range(1, n):
        current = a[i]
        key = current[0]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j][0] > key:
                a[j + 1] = a[j]               # shift the larger record one place to the right
                shifts += 1
                j -= 1
            else:
                break
        if j + 1 != i:                        # only write the saved record back if it actually moved
            a[j + 1] = current
            placements += 1
    return a, {"comparisons": comparisons, "moves": shifts, "writes": shifts + placements, "passes": max(n - 1, 0)}


ALGORITHMS = {"Selection": selection_sort, "Bubble": bubble_sort, "Insertion": insertion_sort}


# --------------------------------------------------------------------------------------- theory cross-check
def inversion_profile(scores):
    """Return (I, L, F) for a list of scores using a Fenwick tree (O(n log n)).

    I = total inversions (pairs i<j with s[i] > s[j]);
    L = max over k of the number of EARLIER scores strictly greater than s[k] (how far k must travel left);
    F = number of positions k >= 1 whose score is a new strict minimum of the prefix s[0..k]."""
    ranks = {v: r + 1 for r, v in enumerate(sorted(set(scores)))}
    size = len(ranks)
    tree = [0] * (size + 1)
    total = longest = new_minima = 0
    prefix_min = None
    for seen, s in enumerate(scores):
        r = ranks[s]
        # count earlier scores <= s, then earlier scores > s = seen - that
        k, not_greater = r, 0
        while k > 0:
            not_greater += tree[k]
            k -= k & -k
        greater = seen - not_greater
        total += greater
        longest = max(longest, greater)
        if prefix_min is not None and s < prefix_min:
            new_minima += 1
        prefix_min = s if prefix_min is None else min(prefix_min, s)
        k = r
        while k <= size:
            tree[k] += 1
            k += k & -k
    return total, longest, new_minima


def predicted_counts(scores):
    """Exact counter values predicted from the input's inversion profile (see Pseudocode section 4.4)."""
    n = len(scores)
    inv, max_left, new_min = inversion_profile(scores)
    passes = min(max_left + 1, n - 1) if n > 1 else 0
    return {
        "Selection": {"comparisons": n * (n - 1) // 2},
        "Bubble": {"comparisons": passes * (n - 1) - passes * (passes - 1) // 2, "moves": inv, "passes": passes},
        "Insertion": {"comparisons": inv + (n - 1) - new_min if n > 1 else 0, "moves": inv},
        "inversions": inv,
    }


def is_stable(sorted_records):
    """True if records with equal scores appear in increasing order_id (= arrival) order."""
    return all(not (a[0] == b[0] and a[1] > b[1]) for a, b in zip(sorted_records, sorted_records[1:]))


# ------------------------------------------------------------------------------------------------- tests
def run_tests():
    """Correctness tests: every algorithm vs Python's sorted(), plus predicted vs counted operations."""
    rng = random.Random(42)
    cases = {
        "empty": [],
        "single": [(7, 0)],
        "two reversed": [(9, 0), (3, 1)],
        "sorted": [(s, i) for i, s in enumerate(range(1, 21))],
        "reverse": [(s, i) for i, s in enumerate(range(20, 0, -1))],
        "duplicates": [(rng.randint(1, 3), i) for i in range(25)],
        "random": [(rng.randint(1, 1000), i) for i in range(200)],
    }
    print("CORRECTNESS TESTS  (expected order = Python sorted(); expected counts = exact prediction from the")
    print("                    inversion profile; Bubble/Insertion must also be stable)")
    passed = total = 0
    for name, recs in cases.items():
        expected = sorted(recs, key=lambda r: r[0])          # Python's sort is stable
        pred = predicted_counts([r[0] for r in recs])
        for alg, fn in ALGORITHMS.items():
            out, cnt = fn(recs)
            order_ok = [r[0] for r in out] == [r[0] for r in expected]
            counts_ok = all(cnt[k] == v for k, v in pred[alg].items())
            stable = is_stable(out)
            ok = order_ok and counts_ok and (stable or alg == "Selection")
            total += 1
            passed += ok
            print(f"{'PASS' if ok else 'FAIL'}  Q1 {alg:<9} {name:<12} n={len(recs):<4}"
                  f" sorted={'yes' if order_ok else 'NO '}  comparisons={cnt['comparisons']:>6,}"
                  f" predicted={pred[alg]['comparisons']:>6,}  stable={'yes' if stable else 'no'}")
    print(f"RESULT: {passed}/{total} tests passed   (Selection Sort may be unstable - a property of the algorithm)")
    return passed == total


def demo():
    """Sort ten sample orders with each algorithm and show the counters side by side."""
    orders = [(5, 101), (2, 102), (9, 103), (2, 104), (7, 105), (1, 106), (5, 107), (8, 108), (3, 109), (1, 110)]
    print("\nDEMO - 10 incoming orders as (priority score, order id):")
    print("  input :", " ".join(f"{s}/{o}" for s, o in orders))
    for alg, fn in ALGORITHMS.items():
        out, c = fn(orders)
        print(f"  {alg:<9}:", " ".join(f"{s}/{o}" for s, o in out),
              f"| comp={c['comparisons']:>2} moves={c['moves']:>2} writes={c['writes']:>2} passes={c['passes']}"
              f" | stable={'yes' if is_stable(out) else 'NO'}")
        for a, b in zip(out, out[1:]):                     # explain the first stability violation found
            if a[0] == b[0] and a[1] > b[1]:
                print(f"  -> {alg} placed order {a[1]} before order {b[1]} (both score {a[0]}, {b[1]} arrived first):"
                      " a long-distance swap broke stability")
                break


def main():
    ok = run_tests()
    demo()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
