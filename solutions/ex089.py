# Exercise 89 - Permutations (distinct integers, backtracking)

def permutations(nums):
    """Build each permutation position by position, marking numbers already used."""
    result, current = [], []
    used = [False] * len(nums)

    def build():
        if len(current) == len(nums):
            result.append(current[:])
            return
        for i, x in enumerate(nums):
            if used[i]:
                continue
            used[i] = True
            current.append(x)
            build()
            current.pop()                                  # backtrack
            used[i] = False

    build()
    return result


def run_test(number, nums, expected):
    result = permutations(nums)
    print(f"Example {number}")
    print(f"Input   : nums = {nums}")
    print(f"Output  : {result}")
    if result == expected:
        print(f"Expected: {expected}")
    else:
        print(f"Note    : document lists {expected}; correct value is {result}")
    print(f"Explanation: {len(result)} permutation(s), {len(nums)}! = {len(result)}.")
    print()


if __name__ == "__main__":
    run_test(1, [1, 2, 3], [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]])
    run_test(2, [0, 1], [[0, 1], [1, 0]])
    run_test(3, [1], [[1]])
    print("Complexity: n! permutations, each copied in O(n) -> O(n * n!) time, O(n) extra space for recursion.")
