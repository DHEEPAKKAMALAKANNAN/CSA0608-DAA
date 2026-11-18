# Exercise 83 - Sudoku Solver (backtracking with row / column / box sets)

PUZZLE = ["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1",
          "7...2...6", ".6....28.", "...419..5", "....8..79"]
EXPECTED = ["534678912", "672195348", "198342567", "859761423", "426853791",
            "713924856", "961537284", "287419635", "345286179"]


def solve_sudoku(board):
    """Fill the '.' cells of a 9x9 list-of-lists board in place; return True if solvable."""
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empty = []
    for r in range(9):
        for c in range(9):
            if board[r][c] == ".":
                empty.append((r, c))
            else:
                rows[r].add(board[r][c]); cols[c].add(board[r][c]); boxes[r // 3 * 3 + c // 3].add(board[r][c])

    def fill(k):
        if k == len(empty):
            return True                                    # every empty cell is filled
        r, c = empty[k]
        b = r // 3 * 3 + c // 3
        for d in "123456789":
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                continue                                   # digit already used in row/col/box
            board[r][c] = d
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)
            if fill(k + 1):
                return True
            board[r][c] = "."                              # undo (backtrack)
            rows[r].remove(d); cols[c].remove(d); boxes[b].remove(d)
        return False

    return fill(0)


def print_board(rows):
    for r, row in enumerate(rows):
        if r in (3, 6):
            print("  ------+-------+------")
        print("  " + " | ".join(" ".join(row[i:i + 3]) for i in (0, 3, 6)))


if __name__ == "__main__":
    board = [list(row) for row in PUZZLE]
    print("Example 1")
    print("Input   : board =")
    print_board(PUZZLE)
    solved = solve_sudoku(board)
    result = ["".join(row) for row in board]
    print(f"Output  : solved = {solved}")
    print_board(result)
    if result == EXPECTED:
        print("Expected: matches the solution given in the document (all 9 rows identical)")
    else:
        print("Note    : result differs from the document's solution")
    valid = all(sorted(r) == list("123456789") for r in result) and \
        all(sorted(result[r][c] for r in range(9)) == list("123456789") for c in range(9))
    print(f"Check   : every row and column contains digits 1-9 exactly once -> {valid}")
