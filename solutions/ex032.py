# Exercise 32 - Maximum and minimum of an array (divide and conquer)


def min_max_divide_conquer(a, lo, hi, counter):
    """Split the array in halves, solve each half, then combine with 2 comparisons.
    counter[0] counts element comparisons."""
    if lo == hi:                                    # one element: it is both min and max
        return a[lo], a[lo]
    if hi == lo + 1:                                # two elements: one comparison
        counter[0] += 1
        return (a[lo], a[hi]) if a[lo] < a[hi] else (a[hi], a[lo])
    mid = (lo + hi) // 2
    lmin, lmax = min_max_divide_conquer(a, lo, mid, counter)
    rmin, rmax = min_max_divide_conquer(a, mid + 1, hi, counter)
    counter[0] += 2                                 # compare the mins, compare the maxes
    return (lmin if lmin < rmin else rmin), (lmax if lmax > rmax else rmax)


if __name__ == "__main__":
    tests = [
        ([2, 4, 6, 8, 10, 12, 14, 18], (2, 18)),
        ([11, 13, 15, 17, 19, 21, 23, 35, 37], (11, 37)),
        ([22, 34, 35, 36, 43, 67, 12, 13, 15, 17], (12, 67)),
    ]
    for n, (arr, expected) in enumerate(tests, 1):
        counter = [0]
        lo, hi = min_max_divide_conquer(arr, 0, len(arr) - 1, counter)
        print(f"Test Case {n}")
        print(f"Input   : N = {len(arr)}, a[] = {arr}  (sorted: {arr == sorted(arr)})")
        print(f"Output  : Min = {lo}, Max = {hi}   (comparisons made: {counter[0]}, "
              f"naive scan needs up to {2 * (len(arr) - 1)})")
        print(f"Expected: Min = {expected[0]}, Max = {expected[1]}   -> "
              f"{'match' if (lo, hi) == expected else 'MISMATCH'}")
        print()
    print("Recurrence      : T(n) = 2T(n/2) + 2, T(2) = 1  ->  about 3n/2 - 2 comparisons")
    print("Time complexity : O(n); Space complexity: O(log n) recursion stack")
    print("Remark          : for an already sorted array min = a[0], max = a[n-1] in O(1);")
    print("                  the divide & conquer version also works for unsorted input (test 3).")
