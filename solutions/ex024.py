# Exercise 24 - String Matching in an Array (words that are substrings of other words)


def string_matching(words):
    """Return every word that is a substring of some other word in the list."""
    result = []
    for i, word in enumerate(words):
        for j, other in enumerate(words):
            if i != j and word in other:       # word occurs inside a different word
                result.append(word)
                break                          # one host word is enough
    return result


if __name__ == "__main__":
    tests = [
        (["mass", "as", "hero", "superhero"], ["as", "hero"]),
        (["leetcode", "et", "code"], ["et", "code"]),
        (["blue", "green", "bu"], []),
    ]
    for no, (words, expected) in enumerate(tests, 1):
        result = string_matching(words)
        print(f"Test Case {no}")
        print(f"Input   : words = {words}")
        print(f"Output  : {result}")
        print(f"Expected: {expected}  (any order is accepted)")
        print(f"Match   : {sorted(result) == sorted(expected)}")
    print()
    print("Time complexity : O(n^2 * L) for n words of length up to L (n^2 pairs, substring test)")
    print("Space complexity: O(1) extra (apart from the result list)")
