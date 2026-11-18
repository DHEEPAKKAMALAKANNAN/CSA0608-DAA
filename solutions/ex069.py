# Exercise 69 - Maximum Coins You Can Get (greedy)


def max_coins(piles):
    """Sort; in each step Alice takes the largest, I take the second largest of
    the three chosen piles, Bob takes the smallest.  Greedy: always give Bob the
    smallest remaining pile and pair the two largest remaining piles."""
    piles = sorted(piles)
    lo, hi = 0, len(piles) - 1
    total, triplets = 0, []
    while lo < hi:
        alice, me, bob = piles[hi], piles[hi - 1], piles[lo]
        triplets.append((bob, me, alice))
        total += me
        hi -= 2
        lo += 1
    return total, triplets


if __name__ == "__main__":
    tests = [([2, 4, 1, 2, 7, 8], 9), ([2, 4, 5], 4)]
    for no, (piles, expected) in enumerate(tests, 1):
        total, triplets = max_coins(piles)
        print(f"Test Case {no}")
        print(f"Input   : piles = {piles}")
        print(f"Triplets: {triplets}  (Bob, me, Alice)")
        print(f"My coins: {[t[1] for t in triplets]}")
        print(f"Output  : {total}")
        print(f"Expected: {expected}")
        print()
    print("Time complexity : O(n log n) for sorting; Space: O(n)")
