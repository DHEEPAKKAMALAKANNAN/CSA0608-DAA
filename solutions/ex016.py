# Exercise 16 - Conway's Game of Life (next generation)


def next_generation(board):
    """Apply the four Life rules to every cell simultaneously; return the new board."""
    rows, cols = len(board), len(board[0])

    def live_neighbours(r, c):
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if (dr or dc) and 0 <= nr < rows and 0 <= nc < cols:
                    count += board[nr][nc]
        return count

    new_board = [[0] * cols for _ in range(rows)]     # old board stays untouched
    for r in range(rows):
        for c in range(cols):
            n = live_neighbours(r, c)
            if board[r][c] == 1:
                new_board[r][c] = 1 if n in (2, 3) else 0    # under/over-population
            else:
                new_board[r][c] = 1 if n == 3 else 0         # reproduction
    return new_board


if __name__ == "__main__":
    tests = [
        ([[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]], [[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 1, 0]]),
        ([[1, 1], [1, 0]], [[1, 1], [1, 1]]),
    ]
    for no, (board, expected) in enumerate(tests, 1):
        result = next_generation(board)
        print(f"Test Case {no}")
        print(f"Input   : board = {board}")
        print(f"Output  : {result}")
        print(f"Expected: {expected}")
        print(f"Match   : {result == expected}")
    print()
    print("Time complexity : O(m * n) - each cell looks at its 8 neighbours (constant work)")
    print("Space complexity: O(m * n) for the new board")
