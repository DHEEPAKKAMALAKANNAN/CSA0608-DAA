# Exercise 66 - Number of Good Pairs
from collections import Counter


def good_pairs_brute_force(nums):
    """O(n^2): list every pair (i, j), i < j, with nums[i] == nums[j]."""
    return [(i, j) for i in range(len(nums))
            for j in range(i + 1, len(nums)) if nums[i] == nums[j]]


def count_good_pairs(nums):
    """O(n): a value occurring c times contributes c*(c-1)/2 good pairs."""
    return sum(c * (c - 1) // 2 for c in Counter(nums).values())


if __name__ == "__main__":
    tests = [([1, 2, 3, 1, 1, 3], 4), ([1, 1, 1, 1], 6)]
    for no, (nums, expected) in enumerate(tests, 1):
        pairs = good_pairs_brute_force(nums)
        print(f"Test Case {no}")
        print(f"Input   : nums = {nums}")
        print(f"Output  : {count_good_pairs(nums)}")
        print(f"Expected: {expected}")
        print(f"Pairs   : {pairs} (0-indexed, brute force count = {len(pairs)})")
        print()
    print("Time complexity : O(n) with a frequency table (O(n^2) for brute force)")
    print("Space complexity: O(k) for k distinct values")
