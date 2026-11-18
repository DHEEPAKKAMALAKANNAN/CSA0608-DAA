# Exercise 85 - Target Sum (count sign assignments that reach the target)
from collections import defaultdict
from itertools import product


def count_expressions(nums, target):
    """DP over reachable sums: ways[s] = number of sign choices so far that give sum s."""
    ways = {0: 1}
    for x in nums:
        nxt = defaultdict(int)
        for s, cnt in ways.items():
            nxt[s + x] += cnt                              # put '+' before x
            nxt[s - x] += cnt                              # put '-' before x
        ways = nxt
    return ways.get(target, 0)


def format_expression(signs, nums):
    parts = []
    for i, (s, x) in enumerate(zip(signs, nums)):
        sign = "+" if s > 0 else "-"
        parts.append(sign + str(x) if i == 0 else f"{sign} {x}")
    return " ".join(parts)


def list_expressions(nums, target):
    """Brute force (2^n sign patterns) - only used to display the expressions."""
    return [f"{format_expression(signs, nums)} = {target}"
            for signs in product((-1, 1), repeat=len(nums))
            if sum(s * x for s, x in zip(signs, nums)) == target]


def run_test(number, nums, target, expected):
    count = count_expressions(nums, target)
    print(f"Example {number}")
    print(f"Input   : nums = {nums}, target = {target}")
    print(f"Output  : {count}")
    if count == expected:
        print(f"Expected: {expected}")
    else:
        print(f"Note    : document lists {expected}; correct value is {count}")
    expressions = list_expressions(nums, target)
    print(f"Explanation: There are {len(expressions)} way(s) to assign symbols to make the sum of nums be target {target}.")
    for e in expressions:
        print("  " + e)
    print()


if __name__ == "__main__":
    run_test(1, [1, 1, 1, 1, 1], 3, 5)
    run_test(2, [1], 1, 1)
    print("Complexity: DP is O(n * S) time where S = sum(nums) (number of distinct reachable sums).")
