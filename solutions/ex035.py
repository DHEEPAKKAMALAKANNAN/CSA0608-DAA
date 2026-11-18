# Exercise 35 - Quick Sort (first element as pivot) with partition trace


def partition_first_pivot(a, lo, hi):
    """Pivot = a[lo]. i scans right for an element > pivot, j scans left for one <= pivot;
    swap them, repeat, finally put the pivot at position j. Returns j."""
    pivot, i, j = a[lo], lo + 1, hi
    while True:
        while i <= j and a[i] <= pivot:
            i += 1
        while i <= j and a[j] > pivot:
            j -= 1
        if i > j:
            break
        a[i], a[j] = a[j], a[i]
    a[lo], a[j] = a[j], a[lo]
    return j


def quick_sort(a, lo, hi, depth=0):
    if lo >= hi:
        return
    pivot = a[lo]
    p = partition_first_pivot(a, lo, hi)
    print(f"{'  ' * depth}QS[{lo}..{hi}] pivot={pivot:<3} placed at index {p} -> {a}")
    quick_sort(a, lo, p - 1, depth + 1)       # left part: elements <= pivot
    quick_sort(a, p + 1, hi, depth + 1)       # right part: elements > pivot


if __name__ == "__main__":
    tests = [
        [10, 16, 8, 12, 15, 6, 3, 9, 5],
        [12, 4, 78, 23, 45, 67, 89, 1],
        [38, 27, 43, 3, 9, 82, 10],
    ]
    for n, arr in enumerate(tests, 1):
        a = arr[:]
        print(f"Test Case {n}")
        print(f"Input   : N = {len(a)}, a[] = {a}")
        print("Array after each partition (indented = deeper recursive call):")
        quick_sort(a, 0, len(a) - 1)
        print(f"Output  : {','.join(map(str, a))}")
        print(f"Expected: {','.join(map(str, sorted(arr)))}   -> {'match' if a == sorted(arr) else 'MISMATCH'}")
        print()
    print("Time complexity : average/best O(n log n), worst case O(n^2) (already sorted input)")
    print("Space complexity: O(log n) average recursion stack (in-place partitioning)")
