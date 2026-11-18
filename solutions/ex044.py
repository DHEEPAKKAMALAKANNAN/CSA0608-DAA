# Exercise 44 - Meet in the Middle: does any subset sum exactly to E?


def subset_sums_with_subsets(items):
    """Dictionary {sum: one subset that gives it} for all subsets of items."""
    sums = {0: []}
    for x in items:
        for s, sub in list(sums.items()):
            sums.setdefault(s + x, sub + [x])
    return sums


def subset_with_exact_sum(nums, exact):
    """Return (True, subset) or (False, None) using meet in the middle."""
    mid = len(nums) // 2
    left = subset_sums_with_subsets(nums[:mid])
    right = subset_sums_with_subsets(nums[mid:])
    for s, sub in left.items():
        if exact - s in right:               # O(1) hash lookup for the complementary half
            return True, sub + right[exact - s]
    return False, None


if __name__ == "__main__":
    cases = [("a", [1, 3, 9, 2, 7, 12], 15), ("b", [3, 34, 4, 12, 5, 2], 15)]
    for label, nums, exact in cases:
        found, subset = subset_with_exact_sum(nums, exact)
        print(f"Test Case {label})")
        print(f"Input   : E = {nums}, exact sum = {exact}")
        print(f"Output  : {found}")
        if found:
            print(f"Subset  : {subset} -> sum = {sum(subset)}")
        print()
    # A case with answer False, to show the other branch of the algorithm
    found, _ = subset_with_exact_sum([3, 34, 4, 12, 5, 2], 100)
    print(f"Extra   : E = [3, 34, 4, 12, 5, 2], exact sum = 100 -> {found}")
    print()
    print("Time: O(n * 2^(n/2)) worst case, space: O(2^(n/2)); naive subset enumeration is O(2^n).")
