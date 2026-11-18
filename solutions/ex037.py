# Exercise 37 - Binary Search with a count of comparisons


def binary_search(a, key):
    """Iterative binary search on a sorted list.
    Returns (index or -1, comparisons); one key-vs-a[mid] comparison is counted per probe."""
    low, high, comparisons = 0, len(a) - 1, 0
    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        if a[mid] == key:
            return mid, comparisons
        if a[mid] < key:
            low = mid + 1
        else:
            high = mid - 1
    return -1, comparisons


if __name__ == "__main__":
    tests = [
        ([5, 10, 15, 20, 25, 30, 35, 40, 45], 20, 4),
        ([10, 20, 30, 40, 50, 60], 50, 5),
        ([21, 32, 40, 54, 65, 76, 87], 32, 2),
    ]
    for n, (arr, key, expected_pos) in enumerate(tests, 1):
        index, comps = binary_search(arr, key)
        print(f"Test Case {n}")
        print(f"Input   : N = {len(arr)}, a[] = {arr}, search key = {key}")
        print(f"Output  : index (0-based) = {index}, position (1-based) = {index + 1}")
        print(f"Expected: {expected_pos} (the document counts positions from 1)   -> "
              f"{'match' if index + 1 == expected_pos else 'MISMATCH'}")
        print(f"Number of comparisons: {comps}")
        print()
    print("Time complexity : O(log n) - the search range halves each step (worst case ~ log2(n)+1 comparisons)")
    print("Space complexity: O(1) for the iterative version")
