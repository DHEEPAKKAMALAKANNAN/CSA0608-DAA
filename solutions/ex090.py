# Exercise 90 - Permutations II (input may contain duplicates, unique permutations only)
from collections import Counter


def unique_permutations(nums):
    """Backtrack over a multiset (value -> remaining count). Choosing each distinct VALUE once per
    position (instead of each index) never generates the same permutation twice."""
    counts = Counter(nums)
    result, current = [], []

    def build():
        if len(current) == len(nums):
            result.append(current[:])
            return
        for value in sorted(counts):
            if counts[value] == 0:
                continue
            counts[value] -= 1
            current.append(value)
            build()
            current.pop()                                  # backtrack
            counts[value] += 1

    build()
    return result


def run_test(number, nums, expected):
    result = unique_permutations(nums)
    print(f"Example {number}")
    print(f"Input   : nums = {nums}")
    print(f"Output  : {result}")
    if sorted(result) == sorted(expected):
        print(f"Expected: {expected}")
    else:
        print(f"Note    : document lists {expected}; correct value is {result}")
    print(f"Explanation: {len(result)} unique permutations.")
    print()


if __name__ == "__main__":
    run_test(1, [1, 1, 2], [[1, 1, 2], [1, 2, 1], [2, 1, 1]])
    run_test(2, [1, 2, 3], [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]])
    print("Complexity: at most n! / (c1! c2! ...) permutations, each built in O(n) -> O(n * n!) worst case.")
