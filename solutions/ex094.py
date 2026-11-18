# Exercise 94 - Generate all subsets of a set in lexicographical order, and handle duplicates
def subsets_in_order(S, skip_duplicates=True):
    """Backtracking. For each size r = 0..n build the r-element subsets in lexicographic order
    (the order shown in the question). With skip_duplicates the input is sorted and a value is
    never reused at the same position, so equal elements do not create repeated subsets."""
    S = sorted(S)
    result = []

    def build(start, current, size):
        if len(current) == size:
            result.append(current[:])
            return
        for i in range(start, len(S)):
            if skip_duplicates and i > start and S[i] == S[i - 1]:
                continue                      # this value was already tried at this position
            current.append(S[i])
            build(i + 1, current, size)
            current.pop()

    for size in range(len(S) + 1):
        build(0, [], size)
    return result


def subsets_dictionary_order(S):
    """Same subsets in strict dictionary order (pre-order walk of the subset tree)."""
    S, result = sorted(S), []

    def walk(start, current):
        result.append(current[:])
        for i in range(start, len(S)):
            if i > start and S[i] == S[i - 1]:
                continue
            walk(i + 1, current + [S[i]])

    walk(0, [])
    return result


if __name__ == "__main__":
    A = [1, 2, 3]
    expected = [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
    print("Test Case 1")
    print(f"Input   : A = {A}")
    out = subsets_in_order(A)
    print(f"Output  : Subsets: {out}")
    print(f"Expected: Subsets: {expected}")
    print(f"Match   : {out == expected}   (count = {len(out)} = 2^{len(A)})")
    print(f"Note    : strict dictionary order would be {subsets_dictionary_order(A)}")
    print("\nTest Case 2 (duplicates)")
    B = [1, 2, 2]
    print(f"Input   : A = {B}")
    print(f"Naive (no duplicate check)  : {subsets_in_order(B, skip_duplicates=False)}")
    print(f"With duplicate check        : {subsets_in_order(B)}")
    print("Handling of duplicates: a naive generator treats the two 2's as different elements and repeats")
    print("  [2] and [1, 2]. This code sorts S and skips an element equal to the previous one at the same")
    print("  position, so every distinct subset appears exactly once (6 subsets instead of 8).")
    print("Complexity: O(n * 2^n) time, because there are 2^n subsets of length up to n.")
