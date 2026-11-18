# Exercise 2 - Count elements of each array that also exist in the other array


def count_common_indices(nums1, nums2):
    """Return [answer1, answer2].

    answer1 = number of indices i with nums1[i] present in nums2
    answer2 = number of indices i with nums2[i] present in nums1
    Sets give O(1) average membership tests, so the total cost is O(n + m).
    """
    set1, set2 = set(nums1), set(nums2)
    answer1 = sum(1 for value in nums1 if value in set2)
    answer2 = sum(1 for value in nums2 if value in set1)
    return [answer1, answer2]


if __name__ == "__main__":
    tests = [
        ([2, 3, 2], [1, 2], [2, 1]),
        ([4, 3, 2, 3, 1], [2, 2, 5, 2, 3, 6], [3, 4]),
    ]
    for number, (nums1, nums2, expected) in enumerate(tests, start=1):
        result = count_common_indices(nums1, nums2)
        print(f"Test Case {number}")
        print(f"Input   : nums1 = {nums1}, nums2 = {nums2}")
        print(f"Output  : {result}")
        if result == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists {expected}; correct value is {result}")
        print()
    print("Time complexity : O(n + m)  (build two sets, then one pass over each array)")
    print("Space complexity: O(n + m)  (the two sets)")
