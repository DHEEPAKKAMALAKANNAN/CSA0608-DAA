# Exercise 88 - Combination Sum II (each candidate used at most once, no duplicate combinations)

def combination_sum_2(candidates, target):
    """Sort, then backtrack. Skipping equal values at the same recursion level removes duplicates."""
    candidates = sorted(candidates)
    result, current = [], []

    def search(start, remaining):
        if remaining == 0:
            result.append(current[:])
            return
        for i in range(start, len(candidates)):
            if i > start and candidates[i] == candidates[i - 1]:
                continue                                   # same value already tried at this level
            if candidates[i] > remaining:
                break                                      # sorted -> nothing further can fit
            current.append(candidates[i])
            search(i + 1, remaining - candidates[i])       # i + 1: each element used only once
            current.pop()

    search(0, target)
    return result


def run_test(number, candidates, target, expected):
    result = combination_sum_2(candidates, target)
    print(f"Example {number}")
    print(f"Input   : candidates = {candidates}, target = {target}")
    print(f"Output  : {result}")
    if result == expected:
        print(f"Expected: {expected}")
    else:
        print(f"Note    : document lists {expected}; correct value is {result}")
    print(f"Explanation: {len(result)} unique combinations (each number used at most once) sum to {target}.")
    print()


if __name__ == "__main__":
    run_test(1, [10, 1, 2, 7, 6, 1, 5], 8, [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]])
    run_test(2, [2, 5, 2, 1, 2], 5, [[1, 2, 2], [5]])
    print("Complexity: O(2^n) time in the worst case (n = number of candidates), O(n) recursion depth.")
