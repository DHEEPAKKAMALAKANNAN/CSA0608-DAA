# Exercise 54 - Word Break (dynamic programming)

def word_break(s, word_dict):
    """dp[i] is True when the prefix s[:i] can be split into dictionary words.
    prev[i] remembers where the last word of such a split starts."""
    words = set(word_dict)
    max_len = max(map(len, words))
    dp = [False] * (len(s) + 1)
    prev = [-1] * (len(s) + 1)
    dp[0] = True                                   # empty prefix is always valid
    for i in range(1, len(s) + 1):
        for j in range(max(0, i - max_len), i):    # last word is s[j:i]
            if dp[j] and s[j:i] in words:
                dp[i], prev[i] = True, j
                break
    if not dp[len(s)]:
        return False, None
    parts, i = [], len(s)
    while i > 0:                                   # walk back to rebuild one split
        parts.append(s[prev[i]:i])
        i = prev[i]
    return True, " ".join(reversed(parts))


if __name__ == "__main__":
    tests = [
        ("leetcode", ["leet", "code"], True),
        ("applepenapple", ["apple", "pen"], True),
        ("catsandog", ["cats", "dog", "sand", "and", "cat"], False),
    ]
    for no, (s, word_dict, expected) in enumerate(tests, 1):
        ok, split = word_break(s, word_dict)
        print(f"Test Case {no}")
        print(f"Input   : s = {s!r}, wordDict = {word_dict}")
        print(f"Output  : {str(ok).lower()}")
        print(f"Expected: {str(expected).lower()}")
        print(f"Segmentation: {split!r}" if ok else "Segmentation: none possible")
        print()
    print("Time complexity : O(n * L^2) for n = len(s), L = longest dictionary word")
    print("Space complexity: O(n + total size of dictionary)")
