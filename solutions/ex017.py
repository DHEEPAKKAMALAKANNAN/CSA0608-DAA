# Exercise 17 - Champagne Tower (row-by-row simulation)


def tower_row(poured, row_index):
    """How full (0..1) each glass of the given row is after pouring `poured` cups."""
    row = [float(poured)]                         # liquid reaching each glass of row 0
    for _ in range(row_index):
        below = [0.0] * (len(row) + 1)
        for i, amount in enumerate(row):
            overflow = max(amount - 1.0, 0.0) / 2     # excess splits equally left / right
            below[i] += overflow
            below[i + 1] += overflow
        row = below
    return [min(1.0, x) for x in row]             # a glass holds at most one cup


def champagne_tower(poured, query_row, query_glass):
    return tower_row(poured, query_row)[query_glass]


if __name__ == "__main__":
    tests = [(1, 1, 1, "0.00000"), (2, 1, 1, "0.50000")]
    for no, (poured, row, glass, expected) in enumerate(tests, 1):
        result = champagne_tower(poured, row, glass)
        print(f"Test Case {no}")
        print(f"Input   : poured = {poured}, query_row = {row}, query_glass = {glass}")
        print(f"Output  : {result:.5f}")
        print(f"Expected: {expected}")
    # the 4-cup picture described in the question: third row = 1/4, 1/2, 1/4
    third_row = [f"{x:.5f}" for x in tower_row(4, 2)]
    print("Test Case 3 (picture from the question)")
    print("Input   : poured = 4, whole row 2")
    print(f"Output  : {third_row}")
    print("Expected: ['0.25000', '0.50000', '0.25000']")
    print()
    print("Time complexity : O(R^2) for R rows (R <= 100) - every glass is visited once")
    print("Space complexity: O(R) - only the current row is stored")
