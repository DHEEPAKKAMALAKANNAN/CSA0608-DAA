# Exercise 6 - Sort a list with an efficient sort (merge sort), then take the maximum


def merge_sort(items):
    """Divide and conquer sort: O(n log n) time in every case, O(n) extra space."""
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left, right = merge_sort(items[:middle]), merge_sort(items[middle:])
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    return merged + left[i:] + right[j:]


def max_after_sorting(numbers):
    """Sort the list, then the maximum is simply the last element."""
    if not numbers:
        return None, []
    ordered = merge_sort(numbers)
    return ordered[-1], ordered


if __name__ == "__main__":
    tests = [
        ("Empty List", [], None),
        ("Single Element List", [5], 5),
        ("All Elements are the Same", [3, 3, 3, 3, 3], 3),
    ]
    for number, (title, numbers, expected) in enumerate(tests, start=1):
        maximum, ordered = max_after_sorting(numbers)
        print(f"Test Case {number}: {title}")
        print(f"Input   : {numbers}")
        print(f"Sorted  : {ordered}")
        if maximum is None:
            print("Output  : None (the list is empty, so there is no maximum)")
        else:
            print(f"Output  : {maximum}")
        if maximum == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists {expected}; correct value is {maximum}")
        print()
    # One extra, more interesting case
    maximum, ordered = max_after_sorting([8, -2, 15, 4, 15, 0])
    print("Test Case 4 (extra)")
    print(f"Input   : [8, -2, 15, 4, 15, 0]")
    print(f"Sorted  : {ordered}")
    print(f"Output  : {maximum}")
    print()
    print("Time complexity : O(n log n) for the merge sort + O(1) to read the last element")
    print("Space complexity: O(n) for the temporary lists used while merging")
