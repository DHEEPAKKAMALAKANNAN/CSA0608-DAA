# Exercise 30 - 0-1 Knapsack problem (exhaustive search)
from itertools import combinations


def total_value(items, values):
    """Sum of the values of the selected item indices."""
    return sum(values[i] for i in items)


def is_feasible(items, weights, capacity):
    """True if the selected items do not exceed the knapsack capacity."""
    return sum(weights[i] for i in items) <= capacity


def knapsack_exhaustive(weights, values, capacity):
    """Examine all 2^n subsets of items; keep the best feasible one."""
    n = len(weights)
    best_items, best_value = [], 0
    for size in range(n + 1):
        for subset in combinations(range(n), size):
            if is_feasible(subset, weights, capacity):
                v = total_value(subset, values)
                if v > best_value:
                    best_items, best_value = list(subset), v
    return best_items, best_value


if __name__ == "__main__":
    tests = [
        ([2, 3, 1], [4, 5, 3], 4, [0, 2], 7),
        ([1, 2, 3, 4], [2, 4, 6, 3], 6, [0, 1, 2], 10),
    ]
    for n, (w, v, cap, doc_items, doc_value) in enumerate(tests, 1):
        items, value = knapsack_exhaustive(w, v, cap)
        print(f"Test Case {n}:")
        print(f"Input   : Weights = {w}, Values = {v}, Capacity = {cap}")
        print(f"Optimal Selection: {items} (item indices), total weight = {sum(w[i] for i in items)}")
        print(f"Total Value      : {value}")
        if items == doc_items and value == doc_value:
            print(f"Expected: {doc_items}, value {doc_value}")
        else:
            print(f"Note    : document lists {doc_items} with value {doc_value}; "
                  f"correct optimum is {items} with value {value}")
            print(f"          (the document's selection {doc_items} is actually worth "
                  f"{total_value(doc_items, v)})")
        print()
    print("Time complexity : O(2^n * n) - 2^n subsets, O(n) to weigh and value each")
    print("Space complexity: O(n)")
