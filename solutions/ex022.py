# Exercise 22 - Find Peak Element in O(log n) (binary search)


def find_peak_element(nums):
    """Return the index of any peak (nums[-1] = nums[n] = -infinity)."""
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:     # rising slope: a peak lies to the right
            lo = mid + 1
        else:                             # falling slope: a peak is at mid or to the left
            hi = mid
    return lo


def is_peak(nums, i):
    left = nums[i - 1] if i > 0 else float("-inf")
    right = nums[i + 1] if i < len(nums) - 1 else float("-inf")
    return nums[i] > left and nums[i] > right


if __name__ == "__main__":
    tests = [
        ([1, 2, 3, 1], "2"),
        ([1, 2, 1, 3, 5, 6, 4], "5 (index 1 is also a valid answer)"),
    ]
    for no, (nums, expected) in enumerate(tests, 1):
        idx = find_peak_element(nums)
        print(f"Test Case {no}")
        print(f"Input   : nums = {nums}")
        print(f"Output  : {idx}")
        print(f"Expected: {expected}")
        print(f"Check   : nums[{idx}] = {nums[idx]} is a strict peak -> {is_peak(nums, idx)}")
    print()
    print("Time complexity : O(log n) - the search range is halved every step")
    print("Space complexity: O(1)")
