# Exercise 81 - Visualizing N-Queens solutions (N = 4, 5, 8)

def solve_all(n):
    """Backtracking: one queen per row. Returns (all solutions, nodes visited)."""
    sols, nodes = [], [0]
    cols, d1, d2 = set(), set(), set()
    placed = []

    def place(row):
        if row == n:
            sols.append(placed[:])
            return
        for c in range(n):
            if c in cols or (row - c) in d1 or (row + c) in d2:
                continue                                   # column or diagonal attacked
            nodes[0] += 1
            cols.add(c); d1.add(row - c); d2.add(row + c); placed.append(c)
            place(row + 1)
            cols.remove(c); d1.remove(row - c); d2.remove(row + c); placed.pop()

    place(0)
    return sols, nodes[0]


def board_rows(sol):
    """Text rows of the board: Q = queen, . = empty."""
    n = len(sol)
    return [" ".join("Q" if sol[r] == c else "." for c in range(n)) for r in range(n)]


def show_side_by_side(sol_a, sol_b):
    for a, b in zip(board_rows(sol_a), board_rows(sol_b)):
        print("    " + a + "      " + b)


if __name__ == "__main__":
    print("Why visualize? A picture of the board shows at a glance that no two Q share a row,")
    print("column or diagonal, exposes symmetric/mirrored solutions, and helps debugging: a wrong")
    print("diagonal test shows up as two queens lined up diagonally. Counting nodes visited also")
    print("shows how fast the search grows with N (complexity insight).")
    stats = []
    for label, n, picks in (("a", 4, (0, 1)), ("b", 5, (0, 1)), ("c", 8, (0, 1))):
        sols, nodes = solve_all(n)
        stats.append((n, len(sols), nodes))
        print(f"\n{label}. Visualization for {n}-Queens")
        print(f"Input   : N = {n}")
        print(f"Output  : {len(sols)} solutions found; showing solution #{picks[0] + 1} (left)"
              f" and #{picks[1] + 1} (right)")
        print(f"          columns (0-based, per row): {sols[picks[0]]}  and  {sols[picks[1]]}")
        show_side_by_side(sols[picks[0]], sols[picks[1]])
    print("\nN   solutions   placements tried by backtracking")
    for n, count, nodes in stats:
        print(f"{n}   {count:<9}   {nodes}")
    print("Explanation: each 'Q' is a queen and '.' an empty square; for N = 4 the two solutions are")
    print("mirror images of each other, which a picture makes obvious.")
