# Exercise 77 - Maximum Weight Loadable into a Container (greedy, heaviest first)
# Interpretation: go through the items from heaviest to lightest and load an item
# whenever it still fits; an item that does not fit is skipped (not the end of the loop).


def greedy_max_load(weights, capacity):
    load, taken = 0, []
    for w in sorted(weights, reverse=True):
        if load + w <= capacity:
            load += w
            taken.append(w)
    return load, taken


def best_possible_load(weights, capacity):
    """Reference: exact subset-sum by bitmask, to see whether greedy was optimal."""
    reach = 1
    for w in weights:
        reach |= reach << w
    return max(x for x in range(capacity + 1) if reach >> x & 1)


if __name__ == "__main__":
    tests = [([10, 20, 30, 40, 50], 60, 50), ([5, 10, 15, 20, 25, 30], 50, 50)]
    for no, (weights, cap, doc) in enumerate(tests, 1):
        load, taken = greedy_max_load(weights, cap)
        print(f"Test Case {no}")
        print(f"Input   : n = {len(weights)}, weights = {weights}, max_capacity = {cap}")
        print(f"Loaded  : {taken} (heaviest first)")
        print(f"Output  : {load}")
        if load == doc:
            print(f"Expected: {doc}")
        else:
            print(f"Note    : document lists {doc}; correct value is {load} "
                  f"({' + '.join(map(str, taken))} fits exactly within {cap})")
        best = best_possible_load(weights, cap)
        print(f"Optimal : {best} (subset-sum check; greedy "
              f"{'matches' if best == load else 'is not optimal here'})")
        print()
    print("Time complexity : O(n log n) for sorting; Space: O(n)")
