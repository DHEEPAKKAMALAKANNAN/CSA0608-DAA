# Exercise 11 - Number of ways a ball can move out of an m x n grid boundary
# DP over steps: ways[r][c] = number of paths that are on cell (r, c) after t moves.
# Interpretation: the document says "exactly N steps", but its expected outputs
# (6 and 12) count paths that leave the grid at ANY move <= N (the classic
# "Out of Boundary Paths" problem).  Both counts are printed.

MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def out_of_boundary_paths(m, n, N, i, j):
    """Return (paths leaving within N moves, paths leaving exactly on move N)."""
    ways = [[0] * n for _ in range(m)]
    ways[i][j] = 1
    total_out = last_step_out = 0
    for _step in range(N):
        nxt = [[0] * n for _ in range(m)]
        last_step_out = 0
        for r in range(m):
            for c in range(n):
                if ways[r][c] == 0:
                    continue
                for dr, dc in MOVES:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < m and 0 <= nc < n:
                        nxt[nr][nc] += ways[r][c]       # still inside the grid
                    else:
                        last_step_out += ways[r][c]     # ball leaves the grid
        total_out += last_step_out
        ways = nxt
    return total_out, last_step_out


if __name__ == "__main__":
    tests = [((2, 2, 2, 0, 0), 6), ((1, 3, 3, 0, 1), 12)]
    for number, (args, expected) in enumerate(tests, start=1):
        m, n, N, i, j = args
        within, exact = out_of_boundary_paths(*args)
        print(f"Test Case {number}")
        print(f"Input   : m={m}, n={n}, N={N}, i={i}, j={j}")
        print(f"Output  : {within}   (ways to leave the grid in at most {N} moves)")
        if within == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists {expected}; correct value is {within}")
        print(f"Extra   : {exact} of them leave exactly on move {N}")
        print()
    print("Note    : 'exactly N steps' in the statement only matches the expected outputs if the ball")
    print("          may leave at any move up to N; counting only exits on move N gives the Extra values.")
    print("Time complexity : O(N * m * n * 4) = O(N * m * n);  Space complexity: O(m * n)")
