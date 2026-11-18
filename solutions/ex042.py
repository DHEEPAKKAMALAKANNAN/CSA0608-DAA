# Exercise 42 - median_of_medians(arr, k): k-th smallest element (iterative version)


def median_of_five(group):
    """Median of a list of at most 5 numbers (selection of the middle by counting)."""
    for x in group:
        smaller = sum(1 for y in group if y < x)
        equal = sum(1 for y in group if y == x)
        if smaller <= (len(group) - 1) // 2 < smaller + equal:
            return x


def choose_pivot(arr):
    """Pivot = median of the medians of the groups of 5 (recursive call on the medians)."""
    if len(arr) <= 5:
        return median_of_five(arr)
    medians = [median_of_five(arr[i:i + 5]) for i in range(0, len(arr), 5)]
    return median_of_medians(medians, (len(medians) + 1) // 2)


def median_of_medians(arr, k):
    """Return the k-th smallest element (k is 1-based) of an unsorted array."""
    arr = list(arr)
    while True:
        if len(arr) == 1:
            return arr[0]
        pivot = choose_pivot(arr)
        low = [x for x in arr if x < pivot]
        equal = [x for x in arr if x == pivot]
        if k <= len(low):                       # answer lies among the smaller elements
            arr = low
        elif k <= len(low) + len(equal):        # the pivot itself is the answer
            return pivot
        else:                                   # answer lies among the larger elements
            k -= len(low) + len(equal)
            arr = [x for x in arr if x > pivot]


if __name__ == "__main__":
    cases = [([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 6),
             ([23, 17, 31, 44, 55, 21, 20, 18, 19, 27], 5)]
    for n, (arr, k) in enumerate(cases, 1):
        result = median_of_medians(arr, k)
        print(f"Test Case {n}")
        print(f"Input   : arr = {arr}, k = {k}")
        print(f"Output  : {result}")
        print(f"Check   : sorted(arr) = {sorted(arr)} -> element number {k} is {sorted(arr)[k - 1]}")
        print()
    print("Time: O(n) worst case (pivot always discards >= 30% of the elements). Extra space: O(n).")
