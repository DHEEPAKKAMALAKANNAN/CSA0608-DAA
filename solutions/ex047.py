# Exercise 47 - Dice Throw Problem (dynamic programming)


def count_dice_ways(num_sides, num_dice, target):
    """ways[d][s] = number of ways to get sum s with d dice of num_sides faces."""
    ways = [[0] * (target + 1) for _ in range(num_dice + 1)]
    ways[0][0] = 1                                   # zero dice give sum 0 in exactly one way
    for d in range(1, num_dice + 1):
        for s in range(1, target + 1):
            # the last die shows face f (1..num_sides), the other d-1 dice make s-f
            ways[d][s] = sum(ways[d - 1][s - f] for f in range(1, min(num_sides, s) + 1))
    return ways


def run_case(number, title, num_sides, num_dice, target, document_value):
    ways = count_dice_ways(num_sides, num_dice, target)
    result = ways[num_dice][target]
    print(f"Test Case {number}: {title}")
    print(f"Input   : sides = {num_sides}, dice = {num_dice}, target = {target}")
    print(f"Output  : Number of ways to reach sum {target}: {result}")
    print(f"Table   : ways to reach each sum 0..{target} with {num_dice} dice = {ways[num_dice]}")
    if result == document_value:
        print(f"Expected: {document_value}")
    else:
        print(f"Note    : document lists {document_value}; correct value is {result} "
              f"(sum {target} with {num_dice} dice of {num_sides} sides, total outcomes {num_sides ** num_dice})")
    print()


if __name__ == "__main__":
    run_case(1, "Simple case", 6, 2, 7, 6)
    run_case(2, "More complex case", 4, 3, 10, 27)
    print("Time: O(num_dice * target * num_sides), space: O(num_dice * target).")
