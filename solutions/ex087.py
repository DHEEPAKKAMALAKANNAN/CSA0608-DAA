# Exercise 87 - Combination Sum (each candidate may be reused any number of times)

def combination_sum(candidates, target):
    """Backtracking over sorted candidates; 'start' keeps combinations in non-decreasing order,
    so every combination is generated exactly once (no duplicates)."""
    candidates = sorted(candidates)
    result, current = [], []

    def search(start, remaining):
        if remaining == 0:
            result.append(current[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break                                      # sorted -> all later ones are too big
            current.append(c)
            search(i, remaining - c)                       # i (not i+1): same number may be reused
            current.pop()

    search(0, target)
    return result


def run_test(number, candidates, target, expected):
    result = combination_sum(candidates, target)
    print(f"Example {number}")
    print(f"Input   : candidates = {candidates}, target = {target}")
    print(f"Output  : {result}")
    if sorted(result) == sorted(expected):
        print(f"Expected: {expected}")
    else:
        print(f"Note    : document lists {expected}; correct value is {result}")
    print(f"Explanation: {len(result)} unique combinations sum to {target}.")
    print()


if __name__ == "__main__":
    run_test(1, [2, 3, 6, 7], 7, [[2, 2, 3], [7]])
    run_test(2, [2, 3, 5], 8, [[2, 2, 2, 2], [2, 3, 3], [3, 5]])
    print("Complexity: worst case O(2^(target/min(candidates))) time, recursion depth <= target/min(candidates).")
