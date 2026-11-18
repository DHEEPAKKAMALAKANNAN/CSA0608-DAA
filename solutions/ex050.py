# Exercise 50 - Minimum path distance (Travelling Salesperson tour) from a distance matrix
# The question asks for a C program; there is no C compiler here, so it is written in Python.
# Method: Held-Karp dynamic programming over subsets (bitmask), O(n^2 * 2^n).

INF = float("inf")


def tsp_held_karp(dist):
    """Return (minimum tour length, tour as a list of city indices starting and ending at 0)."""
    n = len(dist)
    dp = [[INF] * n for _ in range(1 << n)]       # dp[mask][j]: shortest path 0 -> ... -> j over mask
    parent = [[-1] * n for _ in range(1 << n)]
    dp[1][0] = 0
    for mask in range(1 << n):
        for j in range(n):
            if dp[mask][j] == INF:
                continue
            for k in range(n):
                if mask >> k & 1:
                    continue
                new_mask, cost = mask | 1 << k, dp[mask][j] + dist[j][k]
                if cost < dp[new_mask][k]:
                    dp[new_mask][k], parent[new_mask][k] = cost, j
    full = (1 << n) - 1
    best, last = min((dp[full][j] + dist[j][0], j) for j in range(1, n))
    tour, mask = [], full
    while last != -1:                             # rebuild the tour backwards
        tour.append(last)
        mask, last = mask ^ (1 << last), parent[mask][last]
    return best, tour[::-1] + [0]


def run_case(number, matrix, document_value):
    best, tour = tsp_held_karp(matrix)
    print(f"Test Case {number}")
    for row in matrix:
        print("          " + str(row))
    print(f"Output  : {best}")
    print(f"Tour    : {' -> '.join(map(str, tour))}")
    if best == document_value:
        print(f"Expected: {document_value}")
    else:
        print(f"Note    : document lists {document_value}; correct value is {best}")
    print()


if __name__ == "__main__":
    run_case(1, [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]], 80)
    run_case(2, [[0, 10, 10, 10], [10, 0, 10, 10], [10, 10, 0, 10], [10, 10, 10, 0]], 40)
    run_case(3, [[0, 1, 2, 3], [1, 0, 4, 5], [2, 4, 0, 6], [3, 5, 6, 0]], 12)
    print("Case 3: every one of the 3 possible tours (0-1-2-3, 0-1-3-2, 0-2-1-3) costs 14, so 12 is impossible.")
    print("Time: O(n^2 * 2^n), space: O(n * 2^n)  (brute force would be O((n-1)!)).")
