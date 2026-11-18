# Exercise 40 - 4Sum II: count tuples (i, j, k, l) with A[i] + B[j] + C[k] + D[l] == 0
from collections import defaultdict


def four_sum_zero_tuples(A, B, C, D):
    """Meet in the middle: hash every pair (i, j) by A[i]+B[j], then look up -(C[k]+D[l])."""
    pair_sums = defaultdict(list)
    for i, a in enumerate(A):
        for j, b in enumerate(B):
            pair_sums[a + b].append((i, j))
    tuples = []
    for k, c in enumerate(C):
        for l, d in enumerate(D):
            for i, j in pair_sums.get(-(c + d), []):
                tuples.append((i, j, k, l))
    return tuples


def run_case(number, A, B, C, D, expected):
    tuples = four_sum_zero_tuples(A, B, C, D)
    print(f"Test Case {number}")
    print(f"Input   : A = {A}, B = {B}, C = {C}, D = {D}")
    print(f"Output  : {len(tuples)}")
    print(f"Expected: {expected}")
    for i, j, k, l in tuples:
        print(f"  tuple ({i}, {j}, {k}, {l}): {A[i]} + {B[j]} + {C[k]} + {D[l]} = "
              f"{A[i] + B[j] + C[k] + D[l]}")
    print()


if __name__ == "__main__":
    run_case(1, [1, 2], [-2, -1], [-1, 2], [0, 2], 2)
    run_case(2, [0], [0], [0], [0], 1)
    print("Complexity: O(n^2) time and O(n^2) space (instead of O(n^4) for four nested loops).")
