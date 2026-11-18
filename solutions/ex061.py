# Exercise 61 - Optimal Binary Search Tree (bottom-up dynamic programming)
from fractions import Fraction


def optimal_bst(freq):
    """cost[i][j] = minimum cost of a BST on keys i..j (1-based), root[i][j] = its root.
    cost[i][j] = min over r in i..j of cost[i][r-1] + cost[r+1][j] + sum(freq[i..j])."""
    n = len(freq)
    pre = [0]
    for f in freq:
        pre.append(pre[-1] + f)                          # prefix sums of the frequencies
    cost = [[Fraction(0)] * (n + 1) for _ in range(n + 2)]
    root = [[0] * (n + 1) for _ in range(n + 2)]
    for length in range(1, n + 1):                       # chain length = number of keys
        for i in range(1, n - length + 2):
            j = i + length - 1
            weight = pre[j] - pre[i - 1]
            cost[i][j], root[i][j] = min(
                (cost[i][r - 1] + cost[r + 1][j] + weight, r) for r in range(i, j + 1))
    return cost, root


def show_tree(keys, root, i, j, label="root", indent=0):
    if i > j:
        return
    r = root[i][j]
    print("    " * indent + f"{label}: {keys[r - 1]}")
    show_tree(keys, root, i, r - 1, "left ", indent + 1)
    show_tree(keys, root, r + 1, j, "right", indent + 1)


def fmt(x):
    return str(x.numerator) if x.denominator == 1 else f"{float(x):g}"


def run(title, keys, freq, expected=None):
    freq = [Fraction(str(f)) for f in freq]
    cost, root = optimal_bst(freq)
    n = len(keys)
    print(title)
    print(f"Input   : N = {n}, Keys = {keys}, Frequencies = [{', '.join(fmt(f) for f in freq)}]")
    print(f"Output  : {fmt(cost[1][n])}")
    if expected is not None:
        print(f"Expected: {expected}")
    return cost, root


if __name__ == "__main__":
    keys = ["A", "B", "C", "D"]
    cost, root = run("Test Case 1", keys, [0.1, 0.2, 0.4, 0.3], "1.7")
    n = len(keys)
    print("\nCost table C[i][j]   (row i = 1..n+1, column j = 0..n)")
    print("      " + "".join(f"{j:>6}" for j in range(n + 1)))
    for i in range(1, n + 2):
        cells = [f"{float(cost[i][j]):.1f}" if j >= i - 1 else "" for j in range(n + 1)]
        print(f"{i:>5} " + "".join(f"{c:>6}" for c in cells))
    print("\nRoot table R[i][j]   (row i = 1..n, column j = 1..n)")
    print("      " + "".join(f"{j:>6}" for j in range(1, n + 1)))
    for i in range(1, n + 1):
        cells = [str(root[i][j]) if j >= i else "" for j in range(1, n + 1)]
        print(f"{i:>5} " + "".join(f"{c:>6}" for c in cells))
    print(f"\nResulting OBST (root = key {keys[root[1][n] - 1]}, minimum cost = {fmt(cost[1][n])}):")
    show_tree(keys, root, 1, n)

    print()
    run("Test Case 2 (a)", [10, 12], [34, 50], "118")
    print()
    run("Test Case 3 (b)", [10, 12, 20], [34, 8, 50], "142")
    print("\nTime complexity : O(n^3) - O(n^2) table entries, each minimised over up to n roots")
    print("Space complexity: O(n^2) for the cost and root tables")
