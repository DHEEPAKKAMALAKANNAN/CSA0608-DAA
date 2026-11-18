# Exercise 65 - Unique Paths in an m x n grid (dynamic programming)
from math import comb


def unique_paths(m, n):
    """paths[j] = number of ways to reach column j of the current row.
    A cell is reached from above or from the left, so paths[j] += paths[j-1]."""
    paths = [1] * n                          # first row: only one way to reach each cell
    for _ in range(1, m):
        for j in range(1, n):
            paths[j] += paths[j - 1]         # (from above, already in paths[j]) + (from left)
    return paths[-1]


def list_paths(m, n, r=0, c=0, so_far=""):
    """Enumerate the actual routes (R = right, D = down) - only used for tiny grids."""
    if r == m - 1 and c == n - 1:
        return [so_far]
    routes = []
    if c + 1 < n:
        routes += list_paths(m, n, r, c + 1, so_far + "R")
    if r + 1 < m:
        routes += list_paths(m, n, r + 1, c, so_far + "D")
    return routes


if __name__ == "__main__":
    names = {"R": "Right", "D": "Down"}
    for no, (m, n, expected) in enumerate([(3, 7, 28), (3, 2, 3)], 1):
        answer = unique_paths(m, n)
        print(f"Test Case {no}")
        print(f"Input   : m = {m}, n = {n}")
        print(f"Output  : {answer}")
        print(f"Expected: {expected}")
        print(f"Check   : C(m+n-2, m-1) = C({m + n - 2}, {m - 1}) = {comb(m + n - 2, m - 1)}")
        if m * n <= 12:                      # list the routes for the small grid
            for k, route in enumerate(list_paths(m, n), 1):
                print(f"   {k}. " + " -> ".join(names[ch] for ch in route))
        print()
    print("Time complexity : O(m * n)    Space complexity: O(n)  (one row of the DP table)")
