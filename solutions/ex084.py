# Exercise 84 - Sudoku Solver (bitmask constraints + "most constrained cell first" heuristic)
# Different approach from Exercise 83: instead of filling cells left-to-right, always pick the empty
# cell with the fewest candidate digits (MRV), using integer bitmasks for row / column / box.

BOARD = [["5", "3", ".", ".", "7", ".", ".", ".", "."],
         ["6", ".", ".", "1", "9", "5", ".", ".", "."],
         [".", "9", "8", ".", ".", ".", ".", "6", "."],
         ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
         ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
         ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
         [".", "6", ".", ".", ".", ".", "2", "8", "."],
         [".", ".", ".", "4", "1", "9", ".", ".", "5"],
         [".", ".", ".", ".", "8", ".", ".", "7", "9"]]
EXPECTED = [["5", "3", "4", "6", "7", "8", "9", "1", "2"], ["6", "7", "2", "1", "9", "5", "3", "4", "8"],
            ["1", "9", "8", "3", "4", "2", "5", "6", "7"], ["8", "5", "9", "7", "6", "1", "4", "2", "3"],
            ["4", "2", "6", "8", "5", "3", "7", "9", "1"], ["7", "1", "3", "9", "2", "4", "8", "5", "6"],
            ["9", "6", "1", "5", "3", "7", "2", "8", "4"], ["2", "8", "7", "4", "1", "9", "6", "3", "5"],
            ["3", "4", "5", "2", "8", "6", "1", "7", "9"]]


def solve_sudoku(board):
    """Solve in place with bitmask backtracking; returns (solved?, number of recursive calls)."""
    used = [0] * 27                                        # rows 0-8, columns 9-17, boxes 18-26
    empty = set()
    for r in range(9):
        for c in range(9):
            if board[r][c] == ".":
                empty.add((r, c))
            else:
                bit = 1 << int(board[r][c])
                used[r] |= bit; used[9 + c] |= bit; used[18 + r // 3 * 3 + c // 3] |= bit
    calls = [0]

    def candidates(r, c):
        return [d for d in range(1, 10)
                if not (used[r] | used[9 + c] | used[18 + r // 3 * 3 + c // 3]) >> d & 1]

    def search():
        calls[0] += 1
        if not empty:
            return True
        r, c = min(empty, key=lambda cell: len(candidates(*cell)))   # fewest options first
        empty.remove((r, c))
        for d in candidates(r, c):
            bit = 1 << d
            board[r][c] = str(d)
            used[r] |= bit; used[9 + c] |= bit; used[18 + r // 3 * 3 + c // 3] |= bit
            if search():
                return True
            used[r] ^= bit; used[9 + c] ^= bit; used[18 + r // 3 * 3 + c // 3] ^= bit
        board[r][c] = "."
        empty.add((r, c))
        return False

    return search(), calls[0]


if __name__ == "__main__":
    board = [row[:] for row in BOARD]
    print("Example 1")
    print("Input   : board =")
    for row in BOARD:
        print("  ", row)
    solved, calls = solve_sudoku(board)
    print(f"Output  : solved = {solved}  ({calls} recursive calls)")
    for row in board:
        print("  ", row)
    if board == EXPECTED:
        print("Expected: matches the solution given in the document (all 9 rows identical)")
    else:
        print("Note    : result differs from the document's solution")
