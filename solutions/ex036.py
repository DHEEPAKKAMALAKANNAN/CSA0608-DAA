# Exercise 36 - Quick Sort (middle element as pivot) with partition trace


def partition_middle_pivot(a, lo, hi):
    """Move the middle element to the front, then partition around it.
    Returns the final index of the pivot."""
    mid = (lo + hi) // 2
    a[lo], a[mid] = a[mid], a[lo]
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
    pivot = a[(lo + hi) // 2]
    p = partition_middle_pivot(a, lo, hi)
    print(f"{'  ' * depth}QS[{lo}..{hi}] pivot={pivot:<3} placed at index {p} -> {a}")
    quick_sort(a, lo, p - 1, depth + 1)       # left part: elements <= pivot
    quick_sort(a, p + 1, hi, depth + 1)       # right part: elements > pivot


if __name__ == "__main__":
    tests = [
        [19, 72, 35, 46, 58, 91, 22, 31],
        [31, 23, 35, 27, 11, 21, 15, 28],
        [22, 34, 25, 36, 43, 67, 52, 13, 65, 17],
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
    print("Time complexity : average/best O(n log n); worst case O(n^2) but a middle pivot avoids it")
    print("                  for sorted / reverse-sorted input. Space complexity: O(log n) stack")
