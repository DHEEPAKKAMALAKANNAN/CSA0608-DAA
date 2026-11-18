"""
Task 1 - Overlapping subproblems: the binomial coefficient C(n, k)        (CO4, Assignment 4A)

Application context: a QA team plans combinatorial test suites. The number of different k-flag
configurations that can be drawn from n feature flags is C(n, k). The recurrence
        C(n, k) = C(n-1, k-1) + C(n-1, k),   C(n, 0) = C(n, n) = 1
has OVERLAPPING SUBPROBLEMS, so plain recursion recomputes the same values again and again.

Instrumented algorithms (every function returns (value, counters)):
  binom_naive      plain recursion                         2*C(n,k) - 1 calls, C(n,k) - 1 additions
  binom_memo       top-down recursion + memo table         k(n-k) additions, Theta(nk) space
  binom_bottom_up  Levitin's Binomial(n, k) Pascal table   (k-1)k/2 + k(n-k) additions, Theta(nk) space
  binom_one_row    same recurrence on ONE row (j downward)  same additions, Theta(k) space
  fib_naive / fib_memo / fib_bottom_up                     Fibonacci warm-up (the classic overlap example)

Run:  py -3 binomial_dp.py      -> prints the manual-trace tables used in the report (C(6, 3)).
"""
import sys

sys.setrecursionlimit(10_000)


# ----------------------------------------------------------------------------------------- helpers
def _check(n, k):
    """Validate the arguments. Returns False when C(n, k) is trivially 0 (k < 0 or k > n)."""
    if not isinstance(n, int) or not isinstance(k, int):
        raise TypeError("n and k must be integers")
    if n < 0:
        raise ValueError("n must be non-negative")
    return 0 <= k <= n


def formula_bottom_up_additions(n, k):
    """Closed form for the additions of Binomial(n, k):  sum_{i=1..k}(i-1) + sum_{i=k+1..n} k."""
    return (k - 1) * k // 2 + k * (n - k)


# ----------------------------------------------------------------------------------- 1. naive recursion
def binom_naive(n, k):
    """Plain top-down recursion. Counts every call and every addition."""
    ops = {"calls": 0, "additions": 0, "max_depth": 0}
    if not _check(n, k):
        return 0, ops

    def rec(i, j, depth):
        ops["calls"] += 1
        ops["max_depth"] = max(ops["max_depth"], depth)
        if j == 0 or j == i:                      # base cases C(i, 0) = C(i, i) = 1
            return 1
        ops["additions"] += 1
        return rec(i - 1, j - 1, depth + 1) + rec(i - 1, j, depth + 1)

    return rec(n, k, 1), ops


# ------------------------------------------------------------------------------ 2. memoised recursion
def binom_memo(n, k, want_table=False):
    """Top-down DP (memory function): each sub-problem C(i, j) is solved at most once."""
    ops = {"calls": 0, "base": 0, "hits": 0, "additions": 0}
    memo, visited = {}, set()
    if not _check(n, k):
        return (0, ops, memo, visited) if want_table else (0, ops)

    def rec(i, j):
        ops["calls"] += 1
        visited.add((i, j))
        if j == 0 or j == i:
            ops["base"] += 1
            return 1
        if (i, j) in memo:                        # overlapping sub-problem -> reuse stored value
            ops["hits"] += 1
            return memo[(i, j)]
        ops["additions"] += 1
        memo[(i, j)] = rec(i - 1, j - 1) + rec(i - 1, j)
        return memo[(i, j)]

    value = rec(n, k)
    return (value, ops, memo, visited) if want_table else (value, ops)


# ------------------------------------------------------------------------- 3. bottom-up Pascal table
def binom_bottom_up(n, k, want_table=False):
    """Levitin's Binomial(n, k): fill rows i = 0..n, columns j = 0..min(i, k) of Pascal's triangle."""
    ops = {"additions": 0, "cells": 0}
    if not _check(n, k):
        return (0, ops, []) if want_table else (0, ops)
    C = [[None] * (k + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(min(i, k) + 1):
            ops["cells"] += 1
            if j == 0 or j == i:
                C[i][j] = 1                               # base cases on the two edges
            else:
                C[i][j] = C[i - 1][j - 1] + C[i - 1][j]   # the recurrence
                ops["additions"] += 1
    return (C[n][k], ops, C) if want_table else (C[n][k], ops)


# --------------------------------------------------------------------- 4. space-optimised single row
def binom_one_row(n, k, modulus=None, trace=None):
    """Theta(k)-space version: row[j] holds C(i, j); j runs DOWNWARD so row[j-1] is still C(i-1, j-1).
    Optional `modulus` keeps the numbers word-sized (C(n, k) mod p); optional list `trace` gets every row."""
    ops = {"additions": 0, "cells_stored": k + 1}
    if not _check(n, k):
        return 0, ops
    row = [1] + [0] * k                                   # row 0 of Pascal's triangle
    if trace is not None:
        trace.append(list(row))
    for i in range(1, n + 1):
        for j in range(min(i, k), 0, -1):
            if j == i:
                row[j] = 1                                # right edge C(i, i) = 1, no addition
            else:
                row[j] = row[j] + row[j - 1]              # C(i,j) = C(i-1,j) + C(i-1,j-1)
                if modulus:
                    row[j] %= modulus
                ops["additions"] += 1
        if trace is not None:
            trace.append(list(row))
    return row[k], ops


# --------------------------------------------------------------------------------- Fibonacci warm-up
def fib_naive(n):
    """F(n) = F(n-1) + F(n-2), F(0) = 0, F(1) = 1 by plain recursion: 2F(n+1) - 1 calls."""
    ops = {"calls": 0, "additions": 0}

    def rec(m):
        ops["calls"] += 1
        if m < 2:
            return m
        ops["additions"] += 1
        return rec(m - 1) + rec(m - 2)

    return rec(n), ops


def fib_memo(n):
    """Top-down Fibonacci with a memo dictionary: n - 1 additions, at most 2n - 1 calls."""
    ops = {"calls": 0, "additions": 0}
    memo = {}

    def rec(m):
        ops["calls"] += 1
        if m < 2:
            return m
        if m not in memo:
            ops["additions"] += 1
            memo[m] = rec(m - 1) + rec(m - 2)
        return memo[m]

    return rec(n), ops


def fib_bottom_up(n):
    """Iterative Fibonacci keeping only the last two values: n - 1 additions, Theta(1) space."""
    ops = {"calls": 0, "additions": 0}
    if n < 2:
        return n, ops
    prev, cur = 0, 1
    for _ in range(2, n + 1):
        prev, cur = cur, prev + cur
        ops["additions"] += 1
    return cur, ops


# ------------------------------------------------------------------------------------- demo printing
def print_pascal_table(C, n, k, title):
    print(title)
    print("    i \\ j |" + "".join(f"{j:>6}" for j in range(k + 1)))
    print("    ------+" + "-" * (6 * (k + 1)))
    for i in range(n + 1):
        cells = "".join(f"{C[i][j]:>6}" if C[i][j] is not None else f"{'':>6}" for j in range(k + 1))
        print(f"    {i:>5} |{cells}")


def main():
    n, k = 6, 3
    print("=" * 100)
    print(" TASK 1 - BINOMIAL COEFFICIENT C(n, k) BY DYNAMIC PROGRAMMING   (manual-trace instance: C(6, 3))")
    print(" Scenario: number of 3-flag test configurations that can be drawn from 6 feature flags")
    print("=" * 100)

    # [1] the full bottom-up table
    value, ops, C = binom_bottom_up(n, k, want_table=True)
    print_pascal_table(C, n, k, "\n[1] Bottom-up Pascal table C[i][j] = C(i, j), i = 0..6, j = 0..min(i, 3)")

    # [2] every addition in the order the algorithm performs it
    print("\n[2] Order of computation (row by row, left to right) - every addition performed")
    step = 0
    for i in range(2, n + 1):
        parts = []
        for j in range(1, min(i, k) + 1):
            if j == i:
                continue
            step += 1
            parts.append(f"#{step:<2} C[{i}][{j}]={C[i-1][j-1]}+{C[i-1][j]}={C[i][j]}")
        print(f"    row {i}: " + "   ".join(parts))
    f = formula_bottom_up_additions(n, k)
    print(f"    additions counted = {ops['additions']}   formula (k-1)k/2 + k(n-k) = {(k-1)*k//2} + {k*(n-k)} = {f}"
          f"   cells filled = {ops['cells']}   C(6,3) = {value}")

    # [3] memo table: which sub-problems the top-down version actually solved
    mv, mops, memo, visited = binom_memo(n, k, want_table=True)
    print("\n[3] Top-down memo table for C(6, 3):  number = solved by an addition, 1 = base case, . = never needed")
    print("    i \\ j |" + "".join(f"{j:>6}" for j in range(k + 1)))
    print("    ------+" + "-" * (6 * (k + 1)))
    for i in range(n + 1):
        cells = ""
        for j in range(k + 1):
            if j > i:
                cells += f"{'':>6}"
            elif (i, j) in memo:
                cells += f"{memo[(i, j)]:>6}"
            elif (i, j) in visited:
                cells += f"{1:>6}"
            else:
                cells += f"{'.':>6}"
        print(f"    {i:>5} |{cells}")
    print(f"    calls = {mops['calls']}  (base returns {mops['base']}, memo hits {mops['hits']}, "
          f"new sub-problems {mops['additions']})   additions = {mops['additions']} = k(n-k) = {k*(n-k)}")
    print("    -> C[5][1], C[6][1], C[6][2] are never needed for C(6,3): top-down saves 3 of the 12 additions.")

    # [4] single-row version
    trace = []
    rv, rops = binom_one_row(n, k, trace=trace)
    print("\n[4] Space-optimised single row (j runs downward): row contents after each i")
    for i, row in enumerate(trace):
        print(f"    after i = {i}: {row}")
    print(f"    additions = {rops['additions']}, storage = {rops['cells_stored']} cells instead of the "
          f"{ops['cells']} table cells; result {rv}")

    # [5] operation counts for several (n, k)
    print("\n[5] Operation counts: counted vs closed form")
    hdr = (f"    {'(n, k)':<9}{'C(n,k)':>10}{'naive calls':>13}{'2C-1':>10}{'naive adds':>12}"
           f"{'memo adds':>11}{'k(n-k)':>8}{'table adds':>12}{'formula':>9}{'1-row adds':>12}{'cells 2D/1D':>13}")
    print(hdr)
    print("    " + "-" * (len(hdr) - 4))
    for (nn, kk) in [(6, 3), (10, 5), (16, 8), (20, 10), (22, 3)]:
        v1, o1 = binom_naive(nn, kk)
        v2, o2 = binom_memo(nn, kk)
        v3, o3 = binom_bottom_up(nn, kk)
        v4, o4 = binom_one_row(nn, kk)
        assert v1 == v2 == v3 == v4
        print(f"    {str((nn, kk)):<9}{v1:>10}{o1['calls']:>13}{2*v1-1:>10}{o1['additions']:>12}"
              f"{o2['additions']:>11}{kk*(nn-kk):>8}{o3['additions']:>12}{formula_bottom_up_additions(nn, kk):>9}"
              f"{o4['additions']:>12}{str(o3['cells']) + '/' + str(kk + 1):>13}")

    # [6] Fibonacci warm-up
    print("\n[6] Fibonacci warm-up: the same overlap effect")
    print(f"    {'n':>4}{'F(n)':>10}{'naive calls':>13}{'2F(n+1)-1':>11}{'memo calls':>12}"
          f"{'memo adds':>11}{'bottom-up adds':>16}")
    for m in (10, 15, 20, 25):
        a, oa = fib_naive(m)
        b, ob = fib_memo(m)
        c, oc = fib_bottom_up(m)
        assert a == b == c
        f_next = fib_bottom_up(m + 1)[0]
        print(f"    {m:>4}{a:>10}{oa['calls']:>13}{2*f_next-1:>11}{ob['calls']:>12}{ob['additions']:>11}"
              f"{oc['additions']:>16}")
    print("\nConclusion: recursion repeats sub-problems (calls = 2C(n,k)-1); DP solves each (i, j) once -> Theta(nk).")


if __name__ == "__main__":
    main()
