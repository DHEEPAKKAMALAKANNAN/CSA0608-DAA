# Exercise 7 - New list containing only the unique elements of a list


def unique_elements(numbers):
    """Keep the first occurrence of every value (original order preserved).

    A set remembers the values already seen, so each element is handled in
    O(1) average time -> O(n) time overall."""
    seen = set()
    unique = []
    for value in numbers:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


if __name__ == "__main__":
    tests = [
        ("Some Duplicate Elements", [3, 7, 3, 5, 2, 5, 9, 2], [3, 7, 5, 2, 9]),
        ("Negative and Positive Numbers", [-1, 2, -1, 3, 2, -2], [-1, 2, 3, -2]),
        ("List with Large Numbers", [1000000, 999999, 1000000], [1000000, 999999]),
    ]
    for number, (title, numbers, expected) in enumerate(tests, start=1):
        result = unique_elements(numbers)
        print(f"Test Case {number}: {title}")
        print(f"Input   : {numbers}")
        print(f"Output  : {result}")
        if result == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists {expected}; correct value is {result}")
        print()
    print("Time complexity : O(n) on average (one pass, O(1) set lookups)")
    print("Space complexity: O(n) - the 'seen' set plus the result list can each hold up to n")
    print("                  values (worst case: all elements distinct), i.e. O(n) extra space.")
