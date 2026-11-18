# Exercise 33 - Merge Sort


def merge(left, right):
    """Merge two sorted lists into one sorted list."""
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    return result + left[i:] + right[j:]


def merge_sort(a):
    """Divide into halves, sort each recursively, then merge."""
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    return merge(merge_sort(a[:mid]), merge_sort(a[mid:]))


if __name__ == "__main__":
    tests = [
        [31, 23, 35, 27, 11, 21, 15, 28],
        [22, 34, 25, 36, 43, 67, 52, 13, 65, 17],
    ]
    expected = [
        [11, 15, 21, 23, 27, 28, 31, 35],
        [13, 17, 22, 25, 34, 36, 43, 52, 65, 67],
    ]
    for n, (arr, exp) in enumerate(zip(tests, expected), 1):
        result = merge_sort(arr)
        print(f"Test Case {n}")
        print(f"Input   : N = {len(arr)}, a[] = {arr}")
        print(f"Output  : {','.join(map(str, result))}")
        print(f"Expected: {','.join(map(str, exp))}   -> {'match' if result == exp else 'MISMATCH'}")
        print()
    print("Time complexity : O(n log n) in best, average and worst case (T(n) = 2T(n/2) + O(n))")
    print("Space complexity: O(n) for the temporary merged lists")
