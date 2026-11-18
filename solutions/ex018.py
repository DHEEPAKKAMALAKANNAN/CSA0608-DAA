# Exercise 18 - Selection Sort (with step-by-step trace and analysis)


def selection_sort(arr, trace=False):
    """Sort a copy of arr in ascending order; return (sorted_list, comparisons)."""
    a = list(arr)
    comparisons = 0
    for i in range(len(a) - 1):               # a[:i] is the sorted region
        smallest = i
        for j in range(i + 1, len(a)):        # scan the unsorted region a[i:]
            comparisons += 1
            if a[j] < a[smallest]:
                smallest = j
        a[i], a[smallest] = a[smallest], a[i]     # move the minimum to the boundary
        if trace:
            print(f"  Pass {i + 1}: min = {a[i]} (found at index {smallest}) -> {a}")
    return a, comparisons


if __name__ == "__main__":
    print("How it works: the array is split into a sorted region (left, empty at first) and an")
    print("unsorted region. Each pass selects the smallest element of the unsorted region, swaps it")
    print("with the leftmost unsorted element, and moves the boundary one place to the right.")
    print("Simple: only one loop idea (find min, swap). Inefficient: it always makes n(n-1)/2")
    print("comparisons, even for an already sorted list, so the time is O(n^2) (best = worst).")
    print()
    tests = [
        ("Empty list", [], []),
        ("One element", [1], [1]),
        ("All identical", [7, 7, 7, 7], [7, 7, 7, 7]),
        ("Negative numbers", [-5, -1, -3, -2, -4], [-5, -4, -3, -2, -1]),
        ("Random array", [5, 2, 9, 1, 5, 6], [1, 2, 5, 5, 6, 9]),
        ("Reverse sorted", [10, 8, 6, 4, 2], [2, 4, 6, 8, 10]),
        ("Already sorted", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
    ]
    for no, (name, data, expected) in enumerate(tests, 1):
        print(f"Test Case {no} ({name})")
        print(f"Input   : {data}")
        if name == "Random array":
            print("Steps   :")
        result, comps = selection_sort(data, trace=(name == "Random array"))
        print(f"Output  : {result}   (comparisons = {comps})")
        print(f"Expected: {expected}")
    print()
    print("Time: O(n^2) comparisons, at most n-1 swaps | Space: O(1) in-place | Not stable")
