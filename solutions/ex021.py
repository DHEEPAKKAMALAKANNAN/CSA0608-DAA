# Exercise 21 - Kth Missing Positive Number (binary search)


def kth_missing_positive(arr, k):
    """arr is strictly increasing. arr[i] - (i + 1) = how many positives are missing
    before arr[i]. Binary-search the first index whose missing-count reaches k."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] - (mid + 1) < k:      # fewer than k missing up to arr[mid]: go right
            lo = mid + 1
        else:
            hi = mid
    return lo + k                          # lo array elements lie below the answer


def missing_list(arr, count):
    """First `count` missing positives (simple scan, only used to display the explanation)."""
    present, out, x = set(arr), [], 1
    while len(out) < count:
        if x not in present:
            out.append(x)
        x += 1
    return out


if __name__ == "__main__":
    tests = [([2, 3, 4, 7, 11], 5, 9), ([1, 2, 3, 4], 2, 6)]
    for no, (arr, k, expected) in enumerate(tests, 1):
        result = kth_missing_positive(arr, k)
        print(f"Test Case {no}")
        print(f"Input   : arr = {arr}, k = {k}")
        print(f"Output  : {result}")
        print(f"Expected: {expected}")
        listed = missing_list(arr, k)
        print(f"Missing positives (first {k}): {listed} -> the last one is {listed[-1]}")
    print()
    print("Time complexity : O(log n) - binary search on arr[i] - (i + 1)")
    print("Space complexity: O(1)")
