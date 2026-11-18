# Exercise 8 - Bubble sort with Big-O analysis


def bubble_sort(values):
    """Repeatedly swap adjacent out-of-order items; the largest value
    'bubbles' to the end of the unsorted part after every pass.
    Returns (sorted_list, comparisons, swaps)."""
    items = list(values)
    n = len(items)
    comparisons = swaps = 0
    for pass_no in range(n - 1):
        for j in range(n - 1 - pass_no):
            comparisons += 1
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
                swaps += 1
    return items, comparisons, swaps


if __name__ == "__main__":
    tests = [
        ("Random array", [64, 34, 25, 12, 22, 11, 90]),
        ("Reverse sorted (worst case)", [5, 4, 3, 2, 1]),
        ("Already sorted", [1, 2, 3, 4, 5]),
    ]
    for number, (title, values) in enumerate(tests, start=1):
        result, comparisons, swaps = bubble_sort(values)
        n = len(values)
        print(f"Test Case {number}: {title}")
        print(f"Input   : {values}")
        print(f"Output  : {result}")
        print(f"Work    : {comparisons} comparisons (n(n-1)/2 = {n * (n - 1) // 2}), {swaps} swaps")
        print()
    print("Time complexity analysis (n = number of elements)")
    print("  Comparisons : (n-1) + (n-2) + ... + 1 = n(n-1)/2 in every case (no early exit)")
    print("  Worst case  : O(n^2)  (reverse sorted: every comparison also swaps)")
    print("  Average case: O(n^2)")
    print("  Best case   : O(n^2) for this basic version (O(n) only with an early-exit flag)")
    print("  Space       : O(1) extra - sorting is done in place; the sort is stable")
