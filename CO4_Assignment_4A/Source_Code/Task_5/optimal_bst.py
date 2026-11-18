"""
Task 5 - Optimal Binary Search Tree: intent-keyword lookup in a support chatbot       (CO4, Assignment 4A)

Application context: a customer-support chatbot maps each user message to one of four intent keywords that are
stored in a binary search tree (alphabetical order: billing < login < refund < shipping). Last month's logs give
the access probability of every keyword (lookups per 100). Build the BST that minimises the AVERAGE number of key
comparisons per (successful) lookup.

DP formulation (Levitin 8.3), keys a_1 < ... < a_n with probabilities p_1..p_n:
    C(i, j) = minimum average comparisons for a BST built from keys a_i..a_j
    C(i, i-1) = 0 (empty tree),  C(i, i) = p_i
    C(i, j) = min_{i <= k <= j} { C(i, k-1) + C(k+1, j) } + sum_{s=i..j} p_s        (1 <= i < j <= n)
    R(i, j) = the k that attains the minimum (root of the optimal subtree);  answer C(1, n), tree from R.
Exact integer arithmetic: probabilities are kept as counts per 100 lookups, so C(1, n) / 100 = average cost.
Instrumented functions:
  optimal_bst        Levitin's algorithm, diagonal by diagonal (prefix sums for the weight)   Theta(n^3)
  optimal_bst_knuth  Knuth's improvement R(i, j-1) <= R(i, j) <= R(i+1, j)                   Theta(n^2)
  build_tree / depths_from_roots / tree_cost, all_bst_costs (exhaustive check over all Catalan(n) BSTs),
  balanced_depths (median-root "balanced" BST), greedy_depths (most-probable key as root)
Run:  py -3 optimal_bst.py
"""
import csv
import os
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))


def load_keys(path=os.path.join(HERE, "test_data", "intent_keywords.csv")):
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [r["key"] for r in rows], [int(r["lookups_per_100"]) for r in rows]


def _prefix(p):
    pre = [0]
    for x in p:
        pre.append(pre[-1] + x)
    return pre


def optimal_bst(p, trace=None):
    """Levitin's OptimalBST(P[1..n]). Tables are 1-based: C[i][j] for 1 <= i <= n+1, 0 <= j <= n.
    Returns (C, R, ops). ops['candidates'] = number of root candidates k examined (the basic operation)."""
    n = len(p)
    if any(x < 0 for x in p):
        raise ValueError("probabilities / frequencies must be non-negative")
    pre = _prefix(p)
    C = [[0] * (n + 1) for _ in range(n + 2)]
    R = [[0] * (n + 1) for _ in range(n + 2)]
    ops = {"candidates": 0, "cells": 0}
    for i in range(1, n + 1):
        C[i][i], R[i][i] = p[i - 1], i
    for d in range(1, n):                                  # diagonal d: subtrees with d + 1 keys
        for i in range(1, n - d + 1):
            j = i + d
            ops["cells"] += 1
            best, kmin, cands = None, i, []
            for k in range(i, j + 1):
                ops["candidates"] += 1
                q = C[i][k - 1] + C[k + 1][j]
                cands.append((k, q))
                if best is None or q < best:
                    best, kmin = q, k
            C[i][j] = best + pre[j] - pre[i - 1]           # + sum p_i..p_j  (every key one level deeper)
            R[i][j] = kmin
            if trace is not None:
                trace.append((i, j, cands, kmin, best, pre[j] - pre[i - 1]))
    return C, R, ops


def optimal_bst_knuth(p):
    """Same tables, but the root search for (i, j) is limited to R[i][j-1] .. R[i+1][j] (Knuth 1971)."""
    n = len(p)
    if any(x < 0 for x in p):
        raise ValueError("probabilities / frequencies must be non-negative")
    pre = _prefix(p)
    C = [[0] * (n + 1) for _ in range(n + 2)]
    R = [[0] * (n + 1) for _ in range(n + 2)]
    ops = {"candidates": 0, "cells": 0}
    for i in range(1, n + 1):
        C[i][i], R[i][i] = p[i - 1], i
    for d in range(1, n):
        for i in range(1, n - d + 1):
            j = i + d
            ops["cells"] += 1
            best, kmin = None, R[i][j - 1]
            for k in range(R[i][j - 1], R[i + 1][j] + 1):
                ops["candidates"] += 1
                q = C[i][k - 1] + C[k + 1][j]
                if best is None or q < best:
                    best, kmin = q, k
            C[i][j] = best + pre[j] - pre[i - 1]
            R[i][j] = kmin
    return C, R, ops


def build_tree(R, i, j):
    """Nested tuple (root, left, right) of 1-based key indices for keys i..j; None for an empty tree."""
    if i > j:
        return None
    k = R[i][j]
    return (k, build_tree(R, i, k - 1), build_tree(R, k + 1, j))


def depths_of(tree, depth=1, out=None):
    out = {} if out is None else out
    if tree:
        out[tree[0]] = depth
        depths_of(tree[1], depth + 1, out)
        depths_of(tree[2], depth + 1, out)
    return out


def tree_cost(depths, p):
    """Total weighted comparisons: sum p_k * depth(k)  (root has depth 1 = one comparison)."""
    return sum(p[k - 1] * d for k, d in depths.items())


def balanced_depths(i, j, depth=1, out=None):
    """'Balanced' BST: the median key of each range is the root (minimum height, ignores probabilities)."""
    out = {} if out is None else out
    if i <= j:
        k = (i + j) // 2
        out[k] = depth
        balanced_depths(i, k - 1, depth + 1, out)
        balanced_depths(k + 1, j, depth + 1, out)
    return out


def greedy_depths(p, i, j, depth=1, out=None):
    """Greedy heuristic: the most probable key of each range becomes the root."""
    out = {} if out is None else out
    if i <= j:
        k = max(range(i, j + 1), key=lambda t: p[t - 1])
        out[k] = depth
        greedy_depths(p, i, k - 1, depth + 1, out)
        greedy_depths(p, k + 1, j, depth + 1, out)
    return out


def all_bsts(i, j):
    """Generate every BST shape over keys i..j as nested tuples (root, left, right): Catalan(j - i + 1) trees."""
    if i > j:
        yield None
        return
    for k in range(i, j + 1):
        for left in all_bsts(i, k - 1):
            for right in all_bsts(k + 1, j):
                yield (k, left, right)


def all_bst_costs(p):
    """Exhaustive reference: (cost, height) of ALL Catalan(n) BSTs over keys 1..n (feasible for n <= ~10)."""
    out = []
    for tree in all_bsts(1, len(p)):
        d = depths_of(tree)
        out.append((tree_cost(d, p), max(d.values()) if d else 0))
    return out


def print_tree(tree, keys, p, prefix="", is_left=None):
    if tree is None:
        return
    k, left, right = tree
    tag = "" if is_left is None else ("L: " if is_left else "R: ")
    print(f"    {prefix}{tag}{keys[k - 1]} (p = {p[k - 1] / 100:.2f})")
    child_prefix = prefix + ("" if is_left is None else "|   ")
    print_tree(left, keys, p, child_prefix, True)
    print_tree(right, keys, p, child_prefix, False)


def main():
    keys, p = load_keys()
    n, total = len(keys), sum(p)
    print("=" * 100)
    print(" TASK 5 - OPTIMAL BINARY SEARCH TREE FOR 4 CHATBOT INTENT KEYWORDS (test_data/intent_keywords.csv)")
    print("=" * 100)
    print("[1] Keys in BST order and access probabilities: " +
          ", ".join(f"{i}:{k} {x / total:.2f}" for i, (k, x) in enumerate(zip(keys, p), 1)))
    trace = []
    C, R, ops = optimal_bst(p, trace)

    print("\n[2] Diagonal-by-diagonal computation  C[i][j] = min_k (C[i][k-1] + C[k+1][j]) + sum p[i..j]")
    for (i, j, cands, kmin, best, w) in trace:
        cs = ", ".join(f"k={k}: {q / 100:.2f}" for k, q in cands)
        print(f"    C[{i}][{j}]: {cs}  -> min {best / 100:.2f} at k={kmin}; + {w / 100:.2f} = {C[i][j] / 100:.2f}")

    print("\n[3] Main table C[i][j] (average comparisons)        Root table R[i][j]")
    print("      j=" + "".join(f"{j:>6}" for j in range(n + 1)) + "            j=" +
          "".join(f"{j:>4}" for j in range(1, n + 1)))
    for i in range(1, n + 2):
        cells = "".join(f"{C[i][j] / 100:>6.2f}" if j >= i - 1 else f"{'':>6}" for j in range(n + 1))
        roots = "".join(f"{R[i][j]:>4}" if (i <= n and j >= i) else f"{'':>4}" for j in range(1, n + 1))
        print(f"    i={i}{cells}" + (f"          i={i}{roots}" if i <= n else ""))
    print(f"    candidates examined = {ops['candidates']} = n(n-1)(n+4)/6 = {n * (n - 1) * (n + 4) // 6}")

    tree = build_tree(R, 1, n)
    print("\n[4] Optimal BST built from R (R[1][4] is the root, then R[i][k-1] and R[k+1][j] recursively)")
    print_tree(tree, keys, p)
    d_opt = depths_of(tree)
    print(f"    average cost = sum p*depth = " +
          " + ".join(f"{p[k - 1] / 100:.2f}*{d}" for k, d in sorted(d_opt.items())) +
          f" = {tree_cost(d_opt, p) / 100:.2f} = C[1][{n}]")

    print("\n[5] Comparison with other BSTs over the same keys")
    d_bal, d_gr = balanced_depths(1, n), greedy_depths(p, 1, n)
    every = all_bst_costs(p)
    allc = [c for c, _ in every]
    for name, d in [("optimal BST (DP)", d_opt), ("balanced BST (median root)", d_bal),
                    ("greedy (most probable key as root)", d_gr)]:
        shape = ", ".join(f"{keys[k - 1]}@{lvl}" for k, lvl in sorted(d.items(), key=lambda t: (t[1], t[0])))
        print(f"    {name:<36}{tree_cost(d, p) / 100:>6.2f} comparisons   levels: {shape}")
    print(f"    all {len(allc)} possible BSTs: best {min(allc) / 100:.2f}, worst {max(allc) / 100:.2f}, "
          f"mean {sum(allc) / len(allc) / 100:.2f}  -> DP optimum confirmed: {min(allc) == C[1][n]}")
    hmin = min(h for _, h in every)
    low = sorted(c for c, h in every if h == hmin)
    print(f"    {len(low)} of the {len(every)} BSTs have the minimum height {hmin}; their costs range "
          f"{low[0] / 100:.2f} .. {low[-1] / 100:.2f} -> height alone does not decide the cost")
    gain = (tree_cost(d_bal, p) - C[1][n]) / tree_cost(d_bal, p) * 100
    print(f"    saving vs balanced BST: {gain:.1f}% fewer comparisons per lookup")
    Ck, Rk, ok = optimal_bst_knuth(p)
    print(f"\n[6] Knuth's improvement: same C[1][{n}] = {Ck[1][n] / 100:.2f} with {ok['candidates']} candidates "
          f"instead of {ops['candidates']}")


if __name__ == "__main__":
    main()
