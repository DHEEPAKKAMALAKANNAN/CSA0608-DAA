# Exercise 53 - Longest substring without repeating characters (sliding window)

def longest_unique_substring(s):
    """Sliding window: remember the last index of every character.
    When a character repeats inside the window, move the left edge past it."""
    last_seen = {}            # char -> most recent index
    left = 0                  # left edge of the current window
    best_len, best_start = 0, 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1          # shrink window past the duplicate
        last_seen[ch] = right
        if right - left + 1 > best_len:       # window s[left..right] is unique
            best_len, best_start = right - left + 1, left
    return best_len, s[best_start:best_start + best_len]


if __name__ == "__main__":
    tests = [("abcabcbb", 3), ("bbbbb", 1), ("pwwkew", 3), ("", 0)]
    for no, (s, expected) in enumerate(tests, 1):
        length, sub = longest_unique_substring(s)
        print(f"Test Case {no}" + ("   (extra: empty-string edge case)" if s == "" else ""))
        print(f"Input   : s = {s!r}")
        print(f"Output  : {length}")
        print(f"Expected: {expected}")
        print(f"Longest substring: {sub!r}")
        print()
    print("Time complexity : O(n)  - every character is visited once by the right pointer")
    print("Space complexity: O(min(n, k)) - hash map of at most k distinct characters")
