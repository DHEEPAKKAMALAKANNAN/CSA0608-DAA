"""
Task 2 - 0/1 Knapsack by dynamic programming: cargo-drone loading        (CO4, Assignment 4A)

Application context: a same-day delivery drone can lift at most W kg. Each waiting parcel i has a weight w_i (kg)
and a delivery value v_i (revenue in hundreds of rupees). A parcel is either loaded completely or not at all.
Choose the subset of parcels with maximum total value whose total weight does not exceed W.

DP formulation (Levitin 8.2):  F(i, j) = best value using the first i parcels with capacity j
    F(0, j) = 0, F(i, 0) = 0
    F(i, j) = F(i-1, j)                                   if j < w_i
            = max(F(i-1, j), v_i + F(i-1, j - w_i))       if j >= w_i
Instrumented algorithms (all return value + operation counters):
  knapsack_bottom_up       full (n+1) x (W+1) table, row by row               Theta(nW) time and space
  backtrack_items          recovers the chosen parcels from the table           Theta(n) steps
  knapsack_memory_function Levitin's MFKnapsack: top-down, computes only the cells that are needed
  knapsack_one_row         Theta(W) memory (j runs downward), value only
  knapsack_brute_force     exhaustive search over all 2^n subsets (reference for verification)
  greedy_by_ratio          value/weight greedy (shown to be NOT optimal for 0/1 knapsack)
Run:  py -3 knapsack_dp.py      -> manual-trace tables for the 5-parcel, W = 10 kg instance
"""
import csv
import os
import sys

sys.setrecursionlimit(20_000)
HERE = os.path.dirname(os.path.abspath(__file__))
CAPACITY_KG = 10                                    # drone payload limit for the given instance


def load_instance(path=os.path.join(HERE, "test_data", "cargo_parcels.csv")):
    """Read parcel names, weights and values from the CSV test-data file."""
    names, weights, values = [], [], []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            names.append(row["parcel"])
            weights.append(int(row["weight_kg"]))
            values.append(int(row["value"]))
    return names, weights, values


def _validate(weights, values, W):
    if len(weights) != len(values):
        raise ValueError("weights and values must have the same length")
    if W < 0 or any(w <= 0 for w in weights) or any(v < 0 for v in values):
        raise ValueError("need W >= 0, positive weights and non-negative values")


# ------------------------------------------------------------------------------ 1. bottom-up table
def knapsack_bottom_up(weights, values, W):
    """Fill F[0..n][0..W] row by row. Returns (F, ops). ops['cells'] = n*W non-trivial cells evaluated."""
    _validate(weights, values, W)
    n = len(weights)
    ops = {"cells": 0, "comparisons": 0, "takes": 0}
    F = [[0] * (W + 1) for _ in range(n + 1)]       # row 0 and column 0 stay 0 (base cases)
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        prev, cur = F[i - 1], F[i]
        for j in range(1, W + 1):
            ops["cells"] += 1
            if j < w:                                 # parcel i does not fit
                cur[j] = prev[j]
            else:
                ops["comparisons"] += 1
                take = v + prev[j - w]
                if take > prev[j]:                    # strictly better -> load parcel i
                    cur[j] = take
                    ops["takes"] += 1
                else:
                    cur[j] = prev[j]
    return F, ops


def backtrack_items(F, weights, W, steps=None):
    """Recover an optimal subset: parcel i is loaded iff F[i][j] != F[i-1][j]. Returns 1-based indices."""
    chosen, j = [], W
    for i in range(len(weights), 0, -1):
        if F[i][j] != F[i - 1][j]:
            chosen.append(i)
            if steps is not None:
                steps.append(f"i={i}: F[{i}][{j}]={F[i][j]} != F[{i-1}][{j}]={F[i-1][j]} -> LOAD parcel {i}, "
                             f"j = {j} - {weights[i-1]} = {j - weights[i-1]}")
            j -= weights[i - 1]
        elif steps is not None:
            steps.append(f"i={i}: F[{i}][{j}]={F[i][j]} == F[{i-1}][{j}]={F[i-1][j]} -> skip parcel {i}")
    return sorted(chosen)


# -------------------------------------------------------------------- 2. memory function (top-down)
def knapsack_memory_function(weights, values, W):
    """Levitin's MFKnapsack: table initialised to -1 (row 0 / column 0 to 0); only needed cells are computed.
    Returns (best value, F with -1 for never-computed cells, ops)."""
    _validate(weights, values, W)
    n = len(weights)
    ops = {"calls": 0, "cells_computed": 0, "comparisons": 0}
    F = [[0] * (W + 1)] + [[0] + [-1] * W for _ in range(n)]

    def mf(i, j):
        ops["calls"] += 1
        if F[i][j] < 0:                               # not computed yet
            ops["cells_computed"] += 1
            w, v = weights[i - 1], values[i - 1]
            if j < w:
                value = mf(i - 1, j)
            else:
                ops["comparisons"] += 1
                value = max(mf(i - 1, j), v + mf(i - 1, j - w))
            F[i][j] = value
        return F[i][j]

    return mf(n, W), F, ops


# ------------------------------------------------------------------------ 3. Theta(W)-space version
def knapsack_one_row(weights, values, W, trace=None):
    """Single array best[0..W]; j runs DOWNWARD so best[j - w] still belongs to the previous row."""
    _validate(weights, values, W)
    ops = {"cells": 0, "comparisons": 0, "cells_stored": W + 1}
    best = [0] * (W + 1)
    for w, v in zip(weights, values):
        ops["cells"] += W                             # same n*W cells as the 2-D table (j < w is a no-op)
        for j in range(W, w - 1, -1):
            ops["comparisons"] += 1
            if v + best[j - w] > best[j]:
                best[j] = v + best[j - w]
        if trace is not None:
            trace.append(list(best))
    return best[W], ops


# ---------------------------------------------------------------------- 4. brute force (reference)
def knapsack_brute_force(weights, values, W):
    """Exhaustive search: include/exclude every parcel -> visits all 2^n subsets. Returns (value, subset, ops)."""
    _validate(weights, values, W)
    n = len(weights)
    ops = {"subsets": 0}
    best = [0, []]

    def explore(i, wt, val, taken):
        if i == n:
            ops["subsets"] += 1
            if wt <= W and val > best[0]:
                best[0], best[1] = val, list(taken)
            return
        explore(i + 1, wt, val, taken)                         # exclude parcel i+1
        taken.append(i + 1)
        explore(i + 1, wt + weights[i], val + values[i], taken)  # include parcel i+1
        taken.pop()

    explore(0, 0, 0, [])
    return best[0], best[1], ops


def greedy_by_ratio(weights, values, W):
    """Greedy heuristic: load parcels in decreasing value/weight order while they fit (NOT always optimal)."""
    order = sorted(range(len(weights)), key=lambda i: values[i] / weights[i], reverse=True)
    load, total, chosen = 0, 0, []
    for i in order:
        if load + weights[i] <= W:
            load += weights[i]
            total += values[i]
            chosen.append(i + 1)
    return total, sorted(chosen)


# ------------------------------------------------------------------------------------ demo printing
def print_table(F, W, title, names=None, mark=None):
    print(title)
    print("     i  parcel |" + "".join(f"{j:>5}" for j in range(W + 1)))
    print("    -----------+" + "-" * (5 * (W + 1)))
    for i, row in enumerate(F):
        cells = ""
        for j, x in enumerate(row):
            s = "-" if x < 0 else str(x)
            if mark and mark(i, j):
                s += "*"
            cells += f"{s:>5}"
        label = names[i - 1] if (names and i > 0) else "-"
        print(f"    {i:>2}  {label:<7}|{cells}")


def main():
    names, wts, vals = load_instance()
    W, n = CAPACITY_KG, len(wts)
    print("=" * 100)
    print(f" TASK 2 - 0/1 KNAPSACK BY DYNAMIC PROGRAMMING: drone payload W = {W} kg, {n} waiting parcels")
    print("=" * 100)
    print("[1] Instance (test_data/cargo_parcels.csv)")
    print("    parcel  weight w (kg)  value v  v/w")
    for name, w, v in zip(names, wts, vals):
        print(f"    {name:<8}{w:>13}{v:>9}{v / w:>6.2f}")

    F, ops = knapsack_bottom_up(wts, vals, W)
    print_table(F, W, "\n[2] Bottom-up table F[i][j]  (* = parcel i is loaded in the optimum for capacity j)",
                names, mark=lambda i, j: i > 0 and F[i][j] != F[i - 1][j])
    print(f"    cells evaluated = {ops['cells']} = n*W = {n}*{W};  comparisons (j >= w_i) = {ops['comparisons']};"
          f"  optimum F[{n}][{W}] = {F[n][W]}")

    print("\n[3] Key cells on the optimal path, computed by the recurrence")
    for (i, j) in [(1, 5), (2, 8), (3, 8), (4, 10), (5, 10)]:
        w, v = wts[i - 1], vals[i - 1]
        if j < w:
            print(f"    F[{i}][{j}]: j < w{i} = {w}  ->  F[{i-1}][{j}] = {F[i-1][j]}")
        else:
            print(f"    F[{i}][{j}] = max(F[{i-1}][{j}], v{i} + F[{i-1}][{j}-{w}]) = max({F[i-1][j]}, {v} + "
                  f"{F[i-1][j-w]}) = max({F[i-1][j]}, {v + F[i-1][j-w]}) = {F[i][j]}")

    print("\n[4] Backtracking from F[5][10] to recover the parcels")
    steps = []
    chosen = backtrack_items(F, wts, W, steps)
    for s in steps:
        print("    " + s)
    tw, tv = sum(wts[i - 1] for i in chosen), sum(vals[i - 1] for i in chosen)
    print(f"    loaded: {', '.join(names[i - 1] for i in chosen)}  ->  weight {tw} kg <= {W}, value {tv}")

    best, MF, mops = knapsack_memory_function(wts, vals, W)
    print_table(MF, W, "\n[5] Memory-function (top-down) table:  - = never computed", names)
    print(f"    cells computed = {mops['cells_computed']} of {n * W} non-trivial cells "
          f"({100 * mops['cells_computed'] / (n * W):.0f}%), recursive calls = {mops['calls']}, value = {best}")

    trace = []
    v1, o1 = knapsack_one_row(wts, vals, W, trace)
    print("\n[6] Theta(W)-space single row best[0..10] after each parcel (j updated downward)")
    for i, row in enumerate(trace, 1):
        print(f"    after {names[i-1]}: {' '.join(f'{x:>3}' for x in row)}")
    print(f"    value = {v1}, memory = {o1['cells_stored']} cells instead of {(n + 1) * (W + 1)};"
          " but the decisions are lost, so the parcels cannot be recovered (see Task 6)")

    bv, bset, bops = knapsack_brute_force(wts, vals, W)
    gv, gset = greedy_by_ratio(wts, vals, W)
    print("\n[7] Verification")
    print(f"    brute force: {bops['subsets']} subsets examined, best value {bv}, parcels "
          f"{', '.join(names[i - 1] for i in bset)}  -> DP {'MATCHES' if bv == F[n][W] else 'DIFFERS'}")
    print(f"    greedy by value/weight: parcels {', '.join(names[i - 1] for i in gset)}, value {gv} "
          f"(< {F[n][W]}: greedy is not optimal for 0/1 knapsack)")


if __name__ == "__main__":
    main()
