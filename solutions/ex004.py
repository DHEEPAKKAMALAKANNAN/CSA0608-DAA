# Exercise 4 - Count pairs (i, j), i < j, with nums[i] == nums[j] and (i * j) % k == 0
from collections import defaultdict
from itertools import combinations


def count_equal_pairs_divisible(nums, k, show=False):
    """Group indices by value, then test every pair of indices inside a group."""
    positions = defaultdict(list)
    for index, value in enumerate(nums):
        positions[value].append(index)
    count = 0
    for value, indices in positions.items():
        for i, j in combinations(indices, 2):   # i < j because indices are increasing
            if (i * j) % k == 0:
                count += 1
                if show:
                    print(f"   nums[{i}] == nums[{j}] == {value}, {i} * {j} = {i * j} divisible by {k}")
    return count


if __name__ == "__main__":
    tests = [([3, 1, 2, 2, 2, 1, 3], 2, 4), ([1, 2, 3, 4], 1, 0)]
    for number, (nums, k, expected) in enumerate(tests, start=1):
        print(f"Test Case {number}")
        print(f"Input   : nums = {nums}, k = {k}")
        result = count_equal_pairs_divisible(nums, k, show=True)
        print(f"Output  : {result}")
        if result == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists {expected}; correct value is {result}")
        print()
    print("Time complexity : O(n^2) worst case (all values equal -> n(n-1)/2 pairs checked)")
    print("Space complexity: O(n)   for the index lists")
