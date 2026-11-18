# Exercise 14 - Unique Paths in an m x n grid (dynamic programming)
from math import comb


def unique_paths(m, n):
    """Number of down/right paths from top-left to bottom-right of an m x n grid."""
    row = [1] * n                    # first row: only one way to reach each cell
    for _ in range(1, m):            # process the remaining rows one by one
        for c in range(1, n):
            row[c] += row[c - 1]     # ways(cell) = ways(from above) + ways(from left)
    return row[-1]


if __name__ == "__main__":
    tests = [(7, 3, 28), (3, 2, 3)]
    for no, (m, n, expected) in enumerate(tests, 1):
        result = unique_paths(m, n)
        print(f"Test Case {no}")
        print(f"Input   : m = {m}, n = {n}")
        print(f"Output  : {result}")
        print(f"Expected: {expected}")
        # independent check: choose which (m-1) of the (m+n-2) moves go down
        print(f"Check   : C({m + n - 2}, {m - 1}) = {comb(m + n - 2, m - 1)}")
    print()
    print("Time complexity : O(m * n) - every cell of the grid is computed once")
    print("Space complexity: O(n) - only one row of the DP table is kept")
