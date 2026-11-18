# Exercise 15 - Positions of Large Groups


def large_groups(s):
    """Return [start, end] of every run of 3 or more equal characters."""
    result = []
    start = 0                                    # start index of the current group
    for i in range(1, len(s) + 1):
        if i == len(s) or s[i] != s[start]:      # the current group ends at i - 1
            if i - start >= 3:
                result.append([start, i - 1])
            start = i
    return result


if __name__ == "__main__":
    tests = [
        ("abbxxxxzzy", [[3, 6]]),
        ("abc", []),
        ("abbxxxxzyy", [[3, 6]]),      # the example string used in the problem statement
    ]
    for no, (s, expected) in enumerate(tests, 1):
        print(f"Test Case {no}")
        print(f'Input   : s = "{s}"')
        print(f"Output  : {large_groups(s)}")
        print(f"Expected: {expected}")
    print()
    print("Time complexity : O(n) - the string is scanned once")
    print("Space complexity: O(1) extra (apart from the returned list)")
