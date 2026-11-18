# Exercise 29 - Assignment problem (exhaustive search)
from itertools import permutations


def total_cost(assignment, cost_matrix):
    """assignment[i] = task given to worker i; add up cost_matrix[worker][task]."""
    return sum(cost_matrix[worker][task] for worker, task in enumerate(assignment))


def assignment_problem(cost_matrix):
    """Try every permutation of task indices (no repeats) and keep the cheapest."""
    n = len(cost_matrix)
    best_cost, best_assignment = float("inf"), None
    for assignment in permutations(range(n)):
        c = total_cost(assignment, cost_matrix)
        if c < best_cost:
            best_cost, best_assignment = c, assignment
    return best_assignment, best_cost


def show(assignment):
    return "[" + ", ".join(f"(worker {w + 1}, task {t + 1})" for w, t in enumerate(assignment)) + "]"


if __name__ == "__main__":
    tests = [
        ([[3, 10, 7], [8, 5, 12], [4, 6, 9]], (1, 0, 2), 19),
        ([[15, 9, 4], [8, 7, 18], [6, 12, 11]], (2, 0, 1), 24),
    ]
    for n, (matrix, doc_assign, doc_cost) in enumerate(tests, 1):
        best, cost = assignment_problem(matrix)
        print(f"Test Case {n}:")
        print(f"Input   : Cost Matrix = {matrix}")
        print(f"Optimal Assignment: {show(best)}")
        print(f"Total Cost        : {cost}")
        if cost == doc_cost and best == doc_assign:
            print(f"Expected: {show(doc_assign)}, cost {doc_cost}")
        else:
            print(f"Note    : document lists cost {doc_cost} with {show(doc_assign)}")
            print(f"          correct minimum is {cost}; that document assignment really costs "
                  f"{total_cost(doc_assign, matrix)}")
        print()
    print("Time complexity : O(n! * n) - n! permutations, O(n) to cost each one")
    print("Space complexity: O(n)")
