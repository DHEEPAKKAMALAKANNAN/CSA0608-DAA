# Exercise 62 - Optimal Binary Search Tree (top-down recursion with memoization)
from fractions import Fraction
from functools import lru_cache


def optimal_bst(freq):
    """Return (cost, root) dictionaries indexed by (i, j) = keys i..j, 0-based inclusive."""
    n = len(freq)
    pre = [0]
    for f in freq:
        pre.append(pre[-1] + f)
    root = {}

    @lru_cache(maxsize=None)
    def best_cost(i, j):
        if i > j:
            return 0                                   # empty subtree costs nothing
        # try every key r as root: left part + right part (+ one extra level for all keys)
        total, r = min((best_cost(i, r - 1) + best_cost(r + 1, j), r) for r in range(i, j + 1))
        root[(i, j)] = r
        return total + pre[j + 1] - pre[i]

    cost = {(i, j): best_cost(i, j) for i in range(n) for j in range(i, n)}
    return cost, root


def print_tree(keys, root, i, j, prefix="", last=True, top=True):
    if i > j:
        return
    r = root[(i, j)]
    print(keys[r] if top else prefix + ("`-- " if last else "|-- ") + str(keys[r]))
    kids = [(i, r - 1), (r + 1, j)]
    kids = [k for k in kids if k[0] <= k[1]]
    for idx, (a, b) in enumerate(kids):
        print_tree(keys, root, a, b, prefix + ("" if top else ("    " if last else "|   ")),
                   idx == len(kids) - 1, False)


def nested(keys, root, i, j):
    """One-line tree: key(left, right), '-' marks an empty subtree, a leaf is just its key."""
    if i > j:
        return "-"
    r = root[(i, j)]
    if i == j:
        return str(keys[r])
    return f"{keys[r]}({nested(keys, root, i, r - 1)}, {nested(keys, root, r + 1, j)})"


def show_matrices(cost, root, n):
    print("Cost matrix (row i = first key, column j = last key, 0-based)")
    print("   " + "".join(f"{j:>5}" for j in range(n)))
    for i in range(n):
        print(f"{i:>2} " + "".join(f"{cost[(i, j)] if j >= i else '':>5}" for j in range(n)))
    print("Root matrix (entry = index of the root key of keys i..j)")
    print("   " + "".join(f"{j:>5}" for j in range(n)))
    for i in range(n):
        print(f"{i:>2} " + "".join(f"{root[(i, j)] if j >= i else '':>5}" for j in range(n)))


if __name__ == "__main__":
    keys, freq = [10, 12, 16, 21], [4, 2, 6, 3]
    cost, root = optimal_bst(freq)
    print(f"Test Case 1\nInput   : N = 4, Keys = {keys}, Frequencies = {freq}")
    print("Probabilities p = freq/%d = %s" % (sum(freq), [str(Fraction(f, sum(freq))) for f in freq]))
    print(f"Output  : {cost[(0, 3)]}")
    print("Expected: 26")
    show_matrices(cost, root, 4)
    print(f"Optimal BST (root = {keys[root[(0, 3)]]}):")
    print_tree(keys, root, 0, 3)
    print(f"Cost = {cost[(0, 3)]} (frequency-weighted); expected search cost = "
          f"{cost[(0, 3)]}/{sum(freq)} = {cost[(0, 3)] / sum(freq):.4f} comparisons")

    for name, ks, fs, expected in [("a", [10, 12], [34, 50], 118), ("b", [10, 12, 20], [34, 8, 50], 142)]:
        c, r = optimal_bst(fs)
        print(f"\nTest Case {2 if name == 'a' else 3} ({name})\nInput   : keys = {ks}, freq = {fs}")
        print(f"Output  : {c[(0, len(ks) - 1)]}\nExpected: {expected}")
        print(f"Tree    : {nested(ks, r, 0, len(ks) - 1)}")
    print("\nTime complexity : O(n^3);  Space complexity: O(n^2)")
