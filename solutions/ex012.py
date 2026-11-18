# Exercise 12 - House Robber II (houses arranged in a circle)
# Circle trick: house 0 and house n-1 are neighbours, so they can never both be robbed.
# Best = max( best on houses 0..n-2 , best on houses 1..n-1 ), each a normal linear problem.


def rob_line(nums, lo, hi):
    """Best loot and chosen indices on the straight street nums[lo..hi]."""
    best = {lo - 1: (0, []), lo - 2: (0, [])}      # best[k] = (money, houses) using houses <= k
    for k in range(lo, hi + 1):
        skip = best[k - 1]
        take = (best[k - 2][0] + nums[k], best[k - 2][1] + [k])
        best[k] = take if take[0] > skip[0] else skip
    return best[hi]


def rob_circle(nums):
    if len(nums) == 1:
        return nums[0], [0]
    without_last = rob_line(nums, 0, len(nums) - 2)
    without_first = rob_line(nums, 1, len(nums) - 1)
    return max(without_last, without_first, key=lambda result: result[0])


if __name__ == "__main__":
    tests = [([2, 3, 2], 3), ([1, 2, 3, 1], 4)]
    for number, (nums, expected) in enumerate(tests, start=1):
        money, houses = rob_circle(nums)
        print(f"Test Case {number}")
        print(f"Input   : nums = {nums}")
        print(f"Output  : The maximum money you can rob without alerting the police is {money}")
        print(f"          (robbing house indices {houses} counting from 0, values "
              f"{[nums[h] for h in houses]})")
        if money == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists {expected}; correct value is {money}")
        print()
    print("Note    : the document names the houses inconsistently (0-based 'house 1' in example 1,")
    print("          1-based 'house 1 and house 3' in example 2); the money amounts are correct.")
    print("Time complexity : O(n) (two linear passes);  Space complexity: O(n) here (O(1) possible)")
