# Exercise 52 - Longest palindromic substring (expand around each centre, O(n^2))


def expand(s, left, right):
    """Grow outwards while the ends match; return the palindrome found."""
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    return s[left + 1:right]


def longest_palindromic_substring(s):
    """Return (first longest palindrome, list of all longest palindromes)."""
    longest = []
    for centre in range(len(s)):
        for pal in (expand(s, centre, centre),         # odd length, e.g. "aba"
                    expand(s, centre, centre + 1)):    # even length, e.g. "bb"
            if not longest or len(pal) > len(longest[0]):
                longest = [pal]
            elif len(pal) == len(longest[0]) and pal not in longest:
                longest.append(pal)
    return longest[0], longest


if __name__ == "__main__":
    cases = [("babad", '"bab" ("aba" is also valid)'), ("cbbd", '"bb"')]
    for n, (s, expected) in enumerate(cases, 1):
        assert 1 <= len(s) <= 1000 and s.isalnum()    # constraints from the question
        answer, every = longest_palindromic_substring(s)
        print(f"Example {n}")
        print(f'Input   : s = "{s}"')
        print(f'Output  : "{answer}"')
        print(f"Valid   : all longest palindromes = {every}")
        print(f"Expected: {expected}")
        print()
    print("Time: O(n^2) (2n-1 centres, each expands at most n/2 steps); space: O(1) besides the answer.")
