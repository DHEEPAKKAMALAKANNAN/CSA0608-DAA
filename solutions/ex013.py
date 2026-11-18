# Exercise 13 - Climbing stairs: distinct ways to climb n steps taking 1 or 2 steps at a time
# ways(n) = ways(n-1) + ways(n-2): the last move was either a 1-step or a 2-step.


def count_ways(n):
    """Bottom-up DP keeping only the last two values: O(n) time, O(1) space."""
    previous, current = 1, 1              # ways(0) = 1, ways(1) = 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


def list_ways(n):
    """Enumerate every distinct sequence of 1s and 2s that sums to n (for illustration)."""
    if n == 0:
        return [[]]
    ways = [[1] + rest for rest in list_ways(n - 1)]
    if n >= 2:
        ways += [[2] + rest for rest in list_ways(n - 2)]
    return ways


if __name__ == "__main__":
    tests = [(4, 5), (3, 3)]
    for number, (n, expected) in enumerate(tests, start=1):
        result = count_ways(n)
        print(f"Test Case {number}")
        print(f"Input   : n = {n}")
        print(f"Output  : {result}")
        if result == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists {expected}; correct value is {result}")
        print("Ways    :")
        for way in list_ways(n):
            print("   " + " + ".join(map(str, way)))
        print()
    print("Table   : n    = " + "  ".join(f"{n:2d}" for n in range(0, 11)))
    print("          ways = " + "  ".join(f"{count_ways(n):2d}" for n in range(0, 11)) + "  (Fibonacci numbers)")
    print("Time complexity : O(n);  Space complexity: O(1)")
