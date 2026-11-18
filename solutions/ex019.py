# Exercise 19 - Optimised Bubble Sort (stops early when a pass makes no swap)


def bubble_sort_optimised(arr):
    """Return (sorted copy, number of passes made). Exits as soon as the list is sorted."""
    a = list(arr)
    n = len(a)
    passes = 0
    for i in range(n - 1):
        passes += 1
        swapped = False
        for j in range(n - 1 - i):            # the last i items are already in place
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:                       # no swap in a full pass => already sorted
            break
    return a, passes


if __name__ == "__main__":
    tests = [
        ([64, 25, 12, 22, 11], [11, 12, 22, 25, 64], ""),
        ([29, 10, 14, 37, 13], [10, 13, 14, 29, 37], ""),
        ([3, 5, 2, 1, 4], [1, 2, 3, 4, 5], ""),
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], " (already sorted list)"),
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5], " (reverse sorted list)"),
    ]
    for no, (data, expected, label) in enumerate(tests, 1):
        result, passes = bubble_sort_optimised(data)
        print(f"Test Case {no}{label}")
        print(f"Input   : {data}")
        print(f"Output  : {result}")
        print(f"Expected: {expected}")
        print(f"Passes  : {passes} (plain bubble sort always makes {len(data) - 1})")
    print()
    print("Best case (already sorted): O(n) - one pass, no swap, stop.")
    print("Worst / average case: O(n^2). Space: O(1).")
