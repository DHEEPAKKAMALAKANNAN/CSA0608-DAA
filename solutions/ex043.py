# Exercise 43 - Meet in the Middle: subset whose sum is closest to a target
from bisect import bisect_left


def all_subset_sums(items):
    """List of (sum, subset) for every subset of items (2^len(items) entries)."""
    result = [(0, [])]
    for x in items:
        result += [(s + x, sub + [x]) for s, sub in result]
    return result


def closest_subset_sum(nums, target):
    """Split the array in two halves, enumerate each half, then combine with binary search."""
    mid = len(nums) // 2
    left = all_subset_sums(nums[:mid])
    right = sorted(all_subset_sums(nums[mid:]), key=lambda p: p[0])
    right_sums = [s for s, _ in right]
    best = {}                                    # candidate total -> subset achieving it
    for s, sub in left:
        i = bisect_left(right_sums, target - s)  # right sum just >= target - s
        for j in (i - 1, i):                     # check it and its predecessor
            if 0 <= j < len(right):
                best.setdefault(s + right_sums[j], sub + right[j][1])
    gap = min(abs(total - target) for total in best)
    ties = sorted(t for t in best if abs(t - target) == gap)
    return ties[0], best[ties[0]], ties


if __name__ == "__main__":
    cases = [([45, 34, 4, 12, 5, 2], 42), ([1, 3, 2, 7, 4, 6], 10)]
    for n, (nums, target) in enumerate(cases, 1):
        total, subset, ties = closest_subset_sum(nums, target)
        print(f"Test Case {'ab'[n - 1]})")
        print(f"Input   : Set = {nums}, target = {target}")
        print(f"Output  : closest sum = {total}, subset = {subset}, difference = {abs(total - target)}")
        if len(ties) > 1:
            print(f"Note    : sums {ties} are equally close to {target}; the smaller one is reported")
        print()
    print("Time: O(n * 2^(n/2)) (two halves of 2^(n/2) sums, sort + binary search); space: O(2^(n/2)).")
    print("Brute force over all subsets would need O(2^n).")
