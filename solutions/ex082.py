# Exercise 82 - Generalized N-Queens (rectangular board, obstacles, restricted squares)
# Interpretation: rows/columns are 1-based (row, col); an obstacle / restricted square is a cell
# where NO queen may be placed (it does not block lines of attack). One queen per row (rows <= cols).

def placements(rows, cols, blocked=frozenset()):
    """Backtracking generator yielding every valid list of 1-based columns (one per row)."""
    sol, used_cols, diag1, diag2 = [], set(), set(), set()

    def place(r):
        if r > rows:
            yield sol[:]
            return
        for c in range(1, cols + 1):
            if (r, c) in blocked or c in used_cols or (r - c) in diag1 or (r + c) in diag2:
                continue                                   # blocked cell or attacked square
            sol.append(c); used_cols.add(c); diag1.add(r - c); diag2.add(r + c)
            yield from place(r + 1)
            sol.pop(); used_cols.remove(c); diag1.remove(r - c); diag2.remove(r + c)

    yield from place(1)


def why_invalid(sol, rows, cols, blocked):
    """None if the placement is valid, otherwise the reason it is not."""
    for i, c in enumerate(sol, 1):
        if not 1 <= c <= cols:
            return f"column {c} is outside the board"
        if (i, c) in blocked:
            return f"queen at ({i}, {c}) is on a forbidden square"
    for i in range(len(sol)):
        for j in range(i + 1, len(sol)):
            if sol[i] == sol[j]:
                return f"queens in rows {i + 1} and {j + 1} share a column"
            if abs(sol[i] - sol[j]) == j - i:
                return f"queens in rows {i + 1} and {j + 1} share a diagonal"
    return None if len(sol) == rows else "wrong number of queens"


def draw(sol, cols, blocked):
    for r, qc in enumerate(sol, 1):
        print("    " + " ".join("Q" if c == qc else "X" if (r, c) in blocked else "."
                                for c in range(1, cols + 1)))


def run_case(title, rows, cols, blocked, note, sample):
    all_solutions = list(placements(rows, cols, blocked))
    sol = all_solutions[0]
    print(title)
    print(f"Input   : {rows} rows x {cols} columns, forbidden squares (row, col) = {sorted(blocked)}")
    print(f"Output  : Possible solution {sol}   ({len(all_solutions)} solutions in total)")
    draw(sol, cols, blocked)
    reason = why_invalid(sample, rows, cols, blocked)
    if sample == sol:
        print(f"Expected: {sample}")
    elif reason is None:
        print(f"Note    : document lists {sample}, which is also valid (any valid answer is accepted)")
    else:
        print(f"Note    : document lists {sample}; it is invalid")
        print(f"          ({reason}); a correct value is {sol}")
    print(f"Explanation: {note}\n")


if __name__ == "__main__":
    print("Generalization: the attack rule (same column or |dr| == |dc|) is unchanged; only the search")
    print("space changes. On a rows x cols board at most min(rows, cols) queens fit, so we place one")
    print("queen per row of the shorter side; forbidden squares are skipped when trying columns.\n")
    run_case("a. 8x10 board", 8, 10, frozenset(),
             "place 8 queens on an 8x10 board, columns 1..10 are available to every row.",
             [1, 3, 5, 7, 9, 2, 4, 6])
    run_case("b. 5x5 board with obstacles at (2, 2) and (4, 4)", 5, 5, frozenset({(2, 2), (4, 4)}),
             "squares with obstacles are skipped, the rest of the search is unchanged.",
             [1, 3, 5, 2, 4])
    run_case("c. 6x6 board, first queen may not use columns 2 and 4", 6, 6, frozenset({(1, 2), (1, 4)}),
             "squares (1, 2) and (1, 4) are restricted, so the first queen must use another column.",
             [1, 3, 5, 2, 4, 6])
    print("Complexity: worst case O(cols^rows); pruning by columns/diagonals/forbidden squares keeps it small.")
