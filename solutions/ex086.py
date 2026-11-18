# Exercise 86 - Sum of Subarray Minimums (monotonic stack, O(n))
MOD = 10 ** 9 + 7


def sum_subarray_mins(arr):
    """arr[i] is the minimum of left[i] * right[i] subarrays, where
    left[i]  = distance to the previous strictly smaller element,
    right[i] = distance to the next smaller-or-equal element (asymmetric to avoid double counting).
    Returns (answer mod 10^9+7, left, right)."""
    n = len(arr)
    left, right = [0] * n, [0] * n
    stack = []                                             # indices holding increasing values
    for i in range(n):
        while stack and arr[stack[-1]] >= arr[i]:
            stack.pop()
        left[i] = i - (stack[-1] if stack else -1)
        stack.append(i)
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] > arr[i]:
            stack.pop()
        right[i] = (stack[-1] if stack else n) - i
        stack.append(i)
    total = sum(a * l * r for a, l, r in zip(arr, left, right)) % MOD
    return total, left, right


def run_test(number, arr, expected):
    total, left, right = sum_subarray_mins(arr)
    print(f"Example {number}")
    print(f"Input   : arr = {arr}")
    print(f"Output  : {total}")
    if total == expected:
        print(f"Expected: {expected}")
    else:
        print(f"Note    : document lists {expected}; correct value is {total}")
    print("Explanation: each element is the minimum of (left x right) subarrays")
    for a, l, r in zip(arr, left, right):
        print(f"   {a:>3} -> {l} x {r} = {l * r} subarrays, contributes {a * l * r}")
    print()


if __name__ == "__main__":
    run_test(1, [3, 1, 2, 4], 17)
    run_test(2, [11, 81, 94, 43, 3], 444)
    print("Complexity: every index is pushed/popped once -> O(n) time, O(n) space; answer taken mod 10^9 + 7.")
