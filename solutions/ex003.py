# Exercise 3 - Sum of squares of distinct counts of all subarrays


def sum_of_squared_distinct_counts(nums, verbose=False):
    """For every start index i, extend the subarray to the right while
    maintaining a set of the values seen; add (distinct count)^2 each time."""
    total = 0
    for start in range(len(nums)):
        seen = set()
        for end in range(start, len(nums)):
            seen.add(nums[end])
            distinct = len(seen)
            total += distinct * distinct
            if verbose:
                print(f"   {nums[start:end + 1]}: {distinct} distinct value(s)")
    return total


if __name__ == "__main__":
    tests = [([1, 2, 1], 15), ([1, 1], 3)]
    for number, (nums, expected) in enumerate(tests, start=1):
        print(f"Test Case {number}")
        print(f"Input   : nums = {nums}")
        print("Subarrays:")
        result = sum_of_squared_distinct_counts(nums, verbose=True)
        print(f"Output  : {result}")
        if result == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists {expected}; correct value is {result}")
        print()
    print("Time complexity : O(n^2) - n(n+1)/2 subarrays, each updated in O(1) on average")
    print("Space complexity: O(n)   - the set of distinct values of the current subarray")
