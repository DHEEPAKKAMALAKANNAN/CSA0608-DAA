# Exercise 23 - Find the Index of the First Occurrence in a String


def str_str(haystack, needle):
    """Index of the first occurrence of needle in haystack, or -1 (sliding window)."""
    n, m = len(haystack), len(needle)
    if m == 0:
        return 0
    for start in range(n - m + 1):                 # every possible starting position
        k = 0
        while k < m and haystack[start + k] == needle[k]:
            k += 1                                 # extend the match character by character
        if k == m:
            return start
    return -1


if __name__ == "__main__":
    tests = [("sadbutsad", "sad", 0), ("leetcode", "leeto", -1)]
    for no, (haystack, needle, expected) in enumerate(tests, 1):
        result = str_str(haystack, needle)
        print(f"Test Case {no}")
        print(f'Input   : haystack = "{haystack}", needle = "{needle}"')
        print(f"Output  : {result}")
        print(f"Expected: {expected}")
        all_pos = [i for i in range(len(haystack)) if haystack.startswith(needle, i)]
        print(f"All occurrences (for reference): {all_pos}")
    print()
    print("Time complexity : O(n * m) worst case (n = len(haystack), m = len(needle))")
    print("Space complexity: O(1)  (KMP would improve the time to O(n + m))")
