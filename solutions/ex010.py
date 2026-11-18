# Exercise 10 - Sort an array in O(n log n) time with the smallest space: heap sort
# No built-in sort function is used.  Heap sort is in place -> O(1) extra space
# (merge sort would need O(n) extra space, quick sort O(log n) stack, O(n) worst).


def sift_down(items, root, size):
    """Restore the max-heap property for the subtree rooted at `root`."""
    while True:
        largest = root
        left, right = 2 * root + 1, 2 * root + 2
        if left < size and items[left] > items[largest]:
            largest = left
        if right < size and items[right] > items[largest]:
            largest = right
        if largest == root:
            return
        items[root], items[largest] = items[largest], items[root]
        root = largest


def heap_sort(items):
    """Sort in place in ascending order and return the same list."""
    size = len(items)
    for root in range(size // 2 - 1, -1, -1):      # build a max-heap: O(n)
        sift_down(items, root, size)
    for end in range(size - 1, 0, -1):             # n-1 extractions: O(n log n)
        items[0], items[end] = items[end], items[0]
        sift_down(items, 0, end)
    return items


if __name__ == "__main__":
    tests = [
        [5, 2, 3, 1],
        [5, 1, 1, 2, 0, 0],
        [-4, 0, 7, -4, 10, 3, -1],
        [],
        [9],
    ]
    for number, nums in enumerate(tests, start=1):
        print(f"Test Case {number}")
        print(f"Input   : nums = {nums}")
        print(f"Output  : {heap_sort(list(nums))}")
        print()
    print("Time complexity : O(n log n) in best, average and worst case")
    print("                  (heap build O(n) + n extractions of O(log n) each)")
    print("Space complexity: O(1) auxiliary - the array is rearranged in place (sift_down is iterative)")
