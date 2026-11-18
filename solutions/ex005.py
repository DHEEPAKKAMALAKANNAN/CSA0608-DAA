# Exercise 5 - Maximum element of an array with the least time complexity


def find_maximum(values):
    """Single linear scan: O(n) time, O(1) extra space.

    Any correct algorithm must look at every element at least once, so
    O(n) is optimal (sorting first would cost O(n log n))."""
    largest = values[0]
    for value in values[1:]:
        if value > largest:
            largest = value
    return largest


if __name__ == "__main__":
    # The document writes the arrays with braces {..}; they are Python lists here.
    tests = [
        ([1, 2, 3, 4, 5], 5),
        ([7, 7, 7, 7, 7], 7),
        ([-10, 2, 3, -4, 5], 5),
    ]
    for number, (values, expected) in enumerate(tests, start=1):
        result = find_maximum(values)
        print(f"Test Case {number}")
        print(f"Input   : {values}")
        print(f"Output  : {result}")
        if result == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists {expected}; correct value is {result}")
        print()
    print("Time complexity : O(n)  - exactly n - 1 comparisons, which is the lower bound")
    print("Space complexity: O(1)  - only one variable (the running maximum) is kept")
