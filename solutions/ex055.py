# Exercise 55 - Word Break: can the string be segmented? (backtracking with memoization)
from functools import lru_cache

WORD_LIST = ["i", "like", "sam", "sung", "samsung", "mobile", "ice",
             "cream", "icecream", "man", "go", "mango"]
DICTIONARY = set(WORD_LIST)


def all_segmentations(text):
    """Return every way to split text into dictionary words (as lists of words)."""
    @lru_cache(maxsize=None)
    def solve(start):
        if start == len(text):
            return [[]]                              # one way to split the empty rest
        result = []
        for end in range(start + 1, len(text) + 1):  # try every first word text[start:end]
            word = text[start:end]
            if word in DICTIONARY:
                for rest in solve(end):
                    result.append([word] + rest)
        return result
    return solve(0)


if __name__ == "__main__":
    print("Dictionary: { " + ", ".join(WORD_LIST) + " }")
    print()
    tests = [("ilike", "Yes"), ("ilikesamsung", "Yes"),
             ("ilikesamsungx", "No")]           # last one is an extra negative case
    for no, (text, expected) in enumerate(tests, 1):
        splits = all_segmentations(text)
        answer = "Yes" if splits else "No"
        print(f"Test Case {no}" + ("   (extra)" if no == 3 else ""))
        print(f"Input   : {text}")
        print(f"Output  : {answer}")
        print(f"Expected: {expected}")
        for sp in splits:
            print(f"   can be segmented as \"{' '.join(sp)}\"")
        print()
    print("Time complexity : O(n^2) substring checks to decide Yes/No; listing every segmentation")
    print("                  can cost more, since a string may have exponentially many")
    print("Space complexity: O(n) recursion depth plus the memo table")
