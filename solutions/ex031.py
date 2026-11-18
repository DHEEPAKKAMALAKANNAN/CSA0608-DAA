# Exercise 31 - Maximum and minimum of an array (single linear scan)


def find_min_max(a):
    """Scan once keeping a running minimum and maximum. Returns (min, max, comparisons)."""
    lo = hi = a[0]
    comparisons = 0
    for x in a[1:]:
        comparisons += 1              # compare x with the current minimum
        if x < lo:
            lo = x
        else:
            comparisons += 1          # x is not a new minimum, so compare with the maximum
            if x > hi:
                hi = x
    return lo, hi, comparisons


if __name__ == "__main__":
    tests = [
        ([5, 7, 3, 4, 9, 12, 6, 2], (2, 12)),
        ([1, 3, 5, 7, 9, 11, 13, 15, 17], (1, 17)),
        ([22, 34, 35, 36, 43, 67, 12, 13, 15, 17], (12, 67)),
    ]
    for n, (arr, (exp_min, exp_max)) in enumerate(tests, 1):
        lo, hi, comps = find_min_max(arr)
        print(f"Test Case {n}")
        print(f"Input   : N = {len(arr)}, a[] = {arr}")
        print(f"Output  : Min = {lo}, Max = {hi}   (comparisons made: {comps})")
        print(f"Expected: Min = {exp_min}, Max = {exp_max}   -> {'match' if (lo, hi) == (exp_min, exp_max) else 'MISMATCH'}")
        print()
    print("Time complexity : O(n) - at most 2(n-1) comparisons; Space complexity: O(1)")
