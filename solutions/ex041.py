# Exercise 41 - Median of Medians: k-th smallest element in worst-case O(n)


def insertion_sort(items):
    """Sort a tiny list (at most 5 elements) - constant work per group."""
    items = list(items)
    for i in range(1, len(items)):
        key, j = items[i], i - 1
        while j >= 0 and items[j] > key:
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = key
    return items


def select(a, i):
    """Return the i-th smallest (0-based) element of list a."""
    if len(a) <= 5:
        return insertion_sort(a)[i]
    # 1) split into groups of 5 and take the median of each group
    medians = [insertion_sort(a[g:g + 5])[len(a[g:g + 5]) // 2] for g in range(0, len(a), 5)]
    # 2) the pivot is the median of those medians (found recursively)
    pivot = select(medians, (len(medians) - 1) // 2)
    # 3) partition around the pivot and recurse into one side only
    low = [x for x in a if x < pivot]
    equal = [x for x in a if x == pivot]
    high = [x for x in a if x > pivot]
    if i < len(low):
        return select(low, i)
    if i < len(low) + len(equal):
        return pivot
    return select(high, i - len(low) - len(equal))


def kth_smallest(arr, k):
    """k is 1-based (k = 1 is the minimum)."""
    return select(list(arr), k - 1)


if __name__ == "__main__":
    cases = [([12, 3, 5, 7, 19], 2, 5),
             ([12, 3, 5, 7, 4, 19, 26], 3, 5),
             ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 6, 6)]
    for n, (arr, k, expected) in enumerate(cases, 1):
        print(f"Test Case {n}")
        print(f"Input   : arr = {arr}, k = {k}")
        print(f"Output  : {kth_smallest(arr, k)}")
        print(f"Expected: {expected}")
        print()
    print("Why worst-case O(n): the median of medians is larger than at least 30% and smaller than")
    print("at least 30% of the elements, so T(n) <= T(n/5) + T(7n/10) + O(n) = O(n).")
