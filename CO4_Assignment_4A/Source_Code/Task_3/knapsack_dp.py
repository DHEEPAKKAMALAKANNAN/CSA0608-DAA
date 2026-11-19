"""
knapsack_dp.py - Task 3 (CO4 Assignment 4A): 0/1 knapsack by bottom-up dynamic programming.

State DP[i][w] = maximum total value obtainable using only the first i items (in the given order) with a
carrying capacity of w kg.  Recurrence: DP[i][w] = DP[i-1][w] if wt[i] > w, else
max(DP[i-1][w], val[i] + DP[i-1][w - wt[i]]);  DP[0][w] = 0, DP[i][0] = 0.
This program implements the report's pseudocode Knapsack01(...) row by row, prints the full table, the
include/exclude decisions of the states on the optimal path, and the reconstruction.  The table was first
filled by hand (Task 3.4); this run only confirms the manual desk-check.
"""
import csv
import itertools
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def read_items(path):
    items, cap = [], None
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["item"] == "CAPACITY":
                cap = int(r["weight"])
            else:
                items.append((r["item"], int(r["weight"]), int(r["value"])))
    return items, cap


def knapsack(items, W):
    """Return (DP table, optimum value, selected item ids in selection order, reconstruction steps)."""
    n = len(items)
    DP = [[0] * (W + 1) for _ in range(n + 1)]          # row 0 and column 0 are the boundary (all 0)
    for i in range(1, n + 1):                           # rows in increasing i: row i-1 is complete first
        _, wt, val = items[i - 1]
        for w in range(1, W + 1):
            exclude = DP[i - 1][w]
            if wt <= w:                                 # item i can be included
                include = val + DP[i - 1][w - wt]
                DP[i][w] = max(include, exclude)
            else:                                       # item i too heavy for capacity w
                DP[i][w] = exclude
    # reconstruction: walk back from DP[n][W]
    selected, steps, w = [], [], W
    for i in range(n, 0, -1):
        iid, wt, val = items[i - 1]
        if DP[i][w] != DP[i - 1][w]:                    # value changed -> item i was included
            steps.append((i, iid, w, DP[i][w], DP[i - 1][w], "INCLUDE", w - wt))
            selected.append(iid)
            w -= wt
        else:
            steps.append((i, iid, w, DP[i][w], DP[i - 1][w], "exclude", w))
    selected.reverse()
    return DP, DP[n][W], selected, steps


def brute_force(items, W):
    best = (0, ())
    for r in range(len(items) + 1):
        for sub in itertools.combinations(items, r):
            if sum(x[1] for x in sub) <= W:
                best = max(best, (sum(x[2] for x in sub), tuple(x[0] for x in sub)))
    return best


def main():
    items, W = read_items(os.path.join(HERE, "items.csv"))
    DP, best, selected, steps = knapsack(items, W)
    print("=" * 92)
    print("TASK 3 - 0/1 Knapsack, bottom-up DP  (verification of the manual desk-check)")
    print("=" * 92)
    print(f"W = {W}   items:", ", ".join(f"{i}(w={w},v={v})" for i, w, v in items))
    print("\nDP table  DP[i][w]  (rows = first i items, columns = capacity w)")
    print("   i  item(w,v) | " + " ".join(f"w={w:<3}" for w in range(W + 1)))
    print("  " + "-" * 64)
    for i in range(len(items) + 1):
        label = "-" if i == 0 else f"{items[i - 1][0]}({items[i - 1][1]},{items[i - 1][2]})"
        print(f"  {i:>2}  {label:<9} | " + " ".join(f"{DP[i][w]:<5}" for w in range(W + 1)))
    print("\nKey decisions in the last row (i = 4, item S):")
    for w in (5, 7):
        print(f"  DP[4][{w}] = max(exclude DP[3][{w}] = {DP[3][w]}, include 30 + DP[3][{w - 5}] = "
              f"{30 + DP[3][w - 5]}) = {DP[4][w]}")
    print(f"  DP[3][7] = max(exclude DP[2][7] = {DP[2][7]}, include 25 + DP[2][3] = {25 + DP[2][3]})"
          f" = {DP[3][7]}")
    print("\nReconstruction from DP[4][7]:")
    print(f"  {'i':>2} {'item':<4} | {'w':>2} | {'DP[i][w]':>8} | {'DP[i-1][w]':>10} | {'decision':<8} | next w")
    for i, iid, w, a, b, dec, nw in steps:
        print(f"  {i:>2} {iid:<4} | {w:>2} | {a:>8} | {b:>10} | {dec:<8} | {nw}")
    wsum = sum(x[1] for x in items if x[0] in selected)
    print(f"\nOPTIMUM VALUE = {best}   items selected = {', '.join(selected)}   total weight = {wsum} <= {W}")
    bf = brute_force(items, W)
    print(f"Brute force over all 2^{len(items)} = {2 ** len(items)} subsets: best value {bf[0]} "
          f"with {', '.join(bf[1])}  ->  {'MATCH' if bf[0] == best else 'MISMATCH'}")


if __name__ == "__main__":
    main()
