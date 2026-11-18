# Exercise 38 - Binary Search: mid-point steps, and what happens on unsorted input


def binary_search_steps(a, key):
    """Binary search that prints every mid-point calculation. Returns the 0-based index or -1."""
    low, high, step = 0, len(a) - 1, 0
    while low <= high:
        step += 1
        mid = (low + high) // 2
        line = f"  Step {step}: low={low} high={high} mid=({low}+{high})//2={mid} a[{mid}]={a[mid]}"
        if a[mid] == key:
            print(line + f" == {key} -> found")
            return mid
        if a[mid] < key:
            print(line + f" < {key} -> go right, low={mid + 1}")
            low = mid + 1
        else:
            print(line + f" > {key} -> go left, high={mid - 1}")
            high = mid - 1
    print(f"  Stop: low={low} > high={high} -> not found")
    return -1


if __name__ == "__main__":
    tests = [
        ([3, 9, 14, 19, 25, 31, 42, 47, 53], 31, 6),
        ([13, 19, 24, 29, 35, 41, 42], 42, 7),
        ([20, 40, 60, 80, 100, 120], 60, 3),
    ]
    for n, (arr, key, expected_pos) in enumerate(tests, 1):
        print(f"Test Case {n}")
        print(f"Input   : N = {len(arr)}, a[] = {arr}, search key = {key}")
        index = binary_search_steps(arr, key)
        print(f"Output  : index (0-based) = {index}, position (1-based) = {index + 1}")
        print(f"Expected: {expected_pos} (positions counted from 1)   -> "
              f"{'match' if index + 1 == expected_pos else 'MISMATCH'}")
        print()
    # What if the array is NOT sorted?  Same numbers, shuffled (fixed order, deterministic).
    shuffled = [25, 9, 47, 3, 53, 14, 31, 42, 19]
    print(f"Unsorted demo: a[] = {shuffled}, search key = 31  (31 IS present at index {shuffled.index(31)})")
    result = binary_search_steps(shuffled, 31)
    print(f"  Binary search result: {result}  -> wrong, it reports 'not found' for an element that exists")
    print("Impact on correctness : each step discards half the array assuming a[mid] < key means the key")
    print("  is on the right; without sorting that assumption fails, so the key can be thrown away")
    print("  (false 'not found'); the answer cannot be trusted.")
    print("Impact on performance : it still takes O(log n) steps but gives a wrong answer. To be correct on")
    print("  unsorted data use linear search O(n), or sort first O(n log n) and then search O(log n).")
