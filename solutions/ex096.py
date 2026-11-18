# Exercise 96 - Word Subsets (universal strings)
from collections import Counter


def required_counts(words2):
    """For every letter keep the largest multiplicity demanded by any word of words2.
    A word is universal iff it has at least that many copies of each letter."""
    need = Counter()
    for b in words2:
        for letter, count in Counter(b).items():
            need[letter] = max(need[letter], count)
    return need


def universal_words(words1, words2):
    need = required_counts(words2)
    result = []
    for a in words1:
        have = Counter(a)
        if all(have[letter] >= count for letter, count in need.items()):
            result.append(a)
    return result


if __name__ == "__main__":
    shop = ["amazon", "apple", "facebook", "google", "leetcode"]
    tests = [
        (shop, ["e", "o"], ["facebook", "google", "leetcode"]),
        (shop, ["l", "e"], ["apple", "google", "leetcode"]),
        (["warrior", "world"], ["wrr"], ["warrior"]),       # multiplicity example from the question text
    ]
    for number, (words1, words2, expected) in enumerate(tests, 1):
        print(f"Test Case {number}")
        print(f"Input   : words1 = {words1}, words2 = {words2}")
        out = universal_words(words1, words2)
        print(f"Output  : {out}")
        print(f"Expected: {expected}   Match: {out == expected}")
        print()
    print("Merged requirement for words2 = ['wrr', 'e'] :", dict(required_counts(["wrr", "e"])))
    print("Complexity: O(total letters in words1 + words2); the requirement table has at most 26 entries.")
