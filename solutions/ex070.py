# Exercise 70 - Patching Coins so Every Value in [1, target] is Obtainable (greedy)


def patch_coins(coins, target):
    """Keep `miss` = smallest value in [1, target] that cannot yet be formed.
    If the next coin <= miss it extends the reachable range to miss + coin - 1,
    otherwise add a coin of value `miss` (doubles the reachable range)."""
    coins = sorted(coins)
    miss, i, added = 1, 0, []
    while miss <= target:
        if i < len(coins) and coins[i] <= miss:
            miss += coins[i]
            i += 1
        else:
            added.append(miss)
            miss *= 2
    return added


def all_obtainable(coins, target):
    """Verify by building every subset sum with a bitmask."""
    reach = 1
    for c in coins:
        reach |= reach << c
    return all(reach >> x & 1 for x in range(1, target + 1))


if __name__ == "__main__":
    tests = [([1, 4, 10], 19, 2), ([1, 4, 10, 5, 7, 19], 19, 1)]
    for no, (coins, target, expected) in enumerate(tests, 1):
        added = patch_coins(coins, target)
        final = sorted(coins + added)
        print(f"Test Case {no}")
        print(f"Input   : coins = {coins}, target = {target}")
        print(f"Added   : {added}  -> array {final}")
        print(f"Check   : all of 1..{target} obtainable = {all_obtainable(final, target)}")
        print(f"Output  : {len(added)}")
        print(f"Expected: {expected}")
        print()
    print("Time complexity : O(m log m + log target) (m = len(coins)); Space: O(m)")
