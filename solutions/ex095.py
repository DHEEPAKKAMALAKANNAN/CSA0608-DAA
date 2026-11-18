# Exercise 95 - Subset generation: subsets containing a given element, and the full power set
from itertools import combinations


def subsets_containing(elements, x):
    """Choose any subset of the other elements and add x (kept in sorted position)."""
    others = [e for e in elements if e != x]
    result = []
    for size in range(len(others) + 1):
        for combo in combinations(others, size):
            result.append(sorted(combo + (x,)))
    return result


def power_set(nums):
    """Cascading method: every element doubles the list by appending itself to all earlier subsets."""
    subsets = [[]]
    for n in nums:
        subsets += [s + [n] for s in subsets]
    return subsets


if __name__ == "__main__":
    E, x = [2, 3, 4, 5], 3
    expected = [[3], [2, 3], [3, 4], [3, 5], [2, 3, 4], [2, 3, 5], [3, 4, 5], [2, 3, 4, 5]]
    print("Test Case 1 - subsets that contain x")
    print(f"Input   : E = {E}, x = {x}")
    out = subsets_containing(E, x)
    print(f"Output  : {out}")
    print(f"Expected: {expected}")
    print(f"Match   : {out == expected}   (count = {len(out)} = 2^{len(E) - 1})")

    print("\nTest Case 2 - power set")
    nums = [1, 2, 3]
    expected = [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
    print(f"Input   : nums = {nums}")
    out = power_set(nums)
    print(f"Output  : {out}")
    print(f"Expected: {expected}")
    print(f"Match   : {out == expected}")

    print("\nTest Case 3 - power set")
    nums = [0]
    out = power_set(nums)
    print(f"Input   : nums = {nums}")
    print(f"Output  : {out}")
    print(f"Expected: [[], [0]]")
    print(f"Match   : {out == [[], [0]]}")
    print("\nComplexity: O(n * 2^n) time and output size; subsets with x are the power set of n-1 other elements.")
