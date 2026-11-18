# Exercise 34 - Merge Sort with a count of comparisons


def merge(left, right, counter):
    """Merge two sorted lists; counter[0] counts every element-to-element comparison."""
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        counter[0] += 1
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    return result + left[i:] + right[j:]


def merge_sort(a, counter):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    return merge(merge_sort(a[:mid], counter), merge_sort(a[mid:], counter), counter)


if __name__ == "__main__":
    tests = [
        ([12, 4, 78, 23, 45, 67, 89, 1], [1, 4, 12, 23, 45, 67, 78, 89]),
        ([38, 27, 43, 3, 9, 82, 10], [3, 9, 10, 27, 38, 43, 82]),
    ]
    for n, (arr, expected) in enumerate(tests, 1):
        counter = [0]
        result = merge_sort(arr, counter)
        print(f"Test Case {n}")
        print(f"Input   : N = {len(arr)}, a[] = {arr}")
        print(f"Output  : {','.join(map(str, result))}")
        print(f"Expected: {','.join(map(str, expected))}   -> {'match' if result == expected else 'MISMATCH'}")
        print(f"Number of comparisons: {counter[0]}")
        print()
    print("For n a power of 2 the count lies between (n/2)*log2(n) (best) and n*log2(n) - n + 1 (worst),")
    print("so merge sort always needs Theta(n log n) comparisons.")
