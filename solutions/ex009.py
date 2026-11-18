# Exercise 9 - Binary search for a key (with Big-O analysis)
#
# Binary search only works on SORTED data, but the array in the document,
# X = {3, 4, 6, -9, 10, 8, 9, 30}, is not sorted.  So the array is first
# sorted (keeping each value's original 1-based position), then searched.


def binary_search(sorted_pairs, key):
    """sorted_pairs: list of (value, original_position) ordered by value.
    Returns (index_in_sorted_list or -1, number_of_comparisons)."""
    low, high, steps = 0, len(sorted_pairs) - 1, 0
    while low <= high:
        mid = (low + high) // 2
        steps += 1
        if sorted_pairs[mid][0] == key:
            return mid, steps
        if sorted_pairs[mid][0] < key:
            low = mid + 1
        else:
            high = mid - 1
    return -1, steps


if __name__ == "__main__":
    X = [3, 4, 6, -9, 10, 8, 9, 30]
    pairs = sorted((value, pos) for pos, value in enumerate(X, start=1))
    tests = [(10, "Element 10 is found at position 5"), (100, "Element 100 is not found")]
    for number, (key, expected) in enumerate(tests, start=1):
        index, steps = binary_search(pairs, key)
        print(f"Test Case {number}")
        print(f"Input   : X = {X}, KEY = {key}")
        print(f"Sorted  : {[value for value, _ in pairs]}")
        if index == -1:
            result = f"Element {key} is not found"
            sorted_note = ""
        else:
            result = f"Element {key} is found at position {pairs[index][1]}"
            sorted_note = f" (in the sorted array: position {index + 1})"
        print(f"Output  : {result}   [{steps} comparisons]{sorted_note}")
        if result == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists '{expected}'; correct value is '{result}'")
        print()
    print("Note    : the document's array is not sorted. The position reported above is the 1-based")
    print("          position in the ORIGINAL array X (matches the document); binary search itself")
    print("          runs on the sorted copy, where the same element sits at a different position.")
    print("Time complexity : O(log n) for the search (the range halves every step);")
    print("                  best case O(1). The sort needed for unsorted input costs O(n log n).")
    print("Space complexity: O(1) for the iterative search.")
