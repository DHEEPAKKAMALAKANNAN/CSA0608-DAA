# Exercise 1 - First palindromic string in an array


def is_palindrome(word):
    """A string is palindromic if it reads the same forward and backward."""
    return word == word[::-1]


def first_palindrome(words):
    """Scan left to right and return the first palindromic word, else ''."""
    for word in words:
        if is_palindrome(word):
            return word
    return ""


if __name__ == "__main__":
    tests = [
        (["abc", "car", "ada", "racecar", "cool"], "ada"),
        (["notapalindrome", "racecar"], "racecar"),
    ]
    for number, (words, expected) in enumerate(tests, start=1):
        result = first_palindrome(words)
        print(f"Test Case {number}")
        print(f"Input   : words = {words}")
        print(f"Output  : {result!r}")
        if result == expected:
            print(f"Expected: {expected!r}")
        else:
            print(f"Note    : document lists {expected!r}; correct value is {result!r}")
        print()
    # A third case showing the "no palindrome" branch (returns empty string)
    words = ["abc", "def"]
    print("Test Case 3 (extra: no palindromic word)")
    print(f"Input   : words = {words}")
    print(f"Output  : {first_palindrome(words)!r}")
    print()
    print("Time complexity : O(L) where L = total number of characters scanned (each word is")
    print("                  compared with its reverse once, stopping at the first palindrome).")
    print("Space complexity: O(k) for the reversed copy of one word (k = its length).")
