# Exercise 20 - Insertion Sort with duplicate elements (stability check)


def insertion_sort(values):
    """Sort values; return (sorted values, original indices in output order, shifts).

    Each value is tagged with its original index so that we can show whether equal
    values keep their relative order. We shift only while left_item > key (strict),
    so an equal element is never jumped over -> the sort is stable.
    """
    items = list(enumerate(values))                  # (original_index, value)
    shifts = 0
    for i in range(1, len(items)):
        key = items[i]
        j = i - 1
        while j >= 0 and items[j][1] > key[1]:       # strict '>' keeps duplicates in order
            items[j + 1] = items[j]
            shifts += 1
            j -= 1
        items[j + 1] = key
    return [v for _, v in items], [idx for idx, _ in items], shifts


def duplicate_positions(sorted_values, index_order):
    """Original indices of every duplicated value, in the order they appear in the output."""
    groups = {}
    for v, idx in zip(sorted_values, index_order):
        groups.setdefault(v, []).append(idx)
    return {v: g for v, g in groups.items() if len(g) > 1}


if __name__ == "__main__":
    tests = [
        ("Array with duplicates", [3, 1, 4, 1, 5, 9, 2, 6, 5, 3], [1, 1, 2, 3, 3, 4, 5, 5, 6, 9]),
        ("All identical elements", [5, 5, 5, 5, 5], [5, 5, 5, 5, 5]),
        ("Mixed duplicates", [2, 3, 1, 3, 2, 1, 1, 3], [1, 1, 1, 2, 2, 3, 3, 3]),
    ]
    for no, (name, data, expected) in enumerate(tests, 1):
        result, order, shifts = insertion_sort(data)
        groups = duplicate_positions(result, order)
        stable = all(g == sorted(g) for g in groups.values())
        print(f"Test Case {no} ({name})")
        print(f"Input   : {data}")
        print(f"Output  : {result}")
        print(f"Expected: {expected}")
        print(f"Shifts  : {shifts}")
        print(f"Original indices of duplicates, in output order: {groups}")
        print(f"Stable  : {stable} (equal values keep their original left-to-right order)")
    print()
    print("Duplicates are handled by the strict '>' test: equal elements stop the shifting, so they")
    print("stay in original order (stable) and an all-equal list needs 0 shifts (O(n) best case).")
    print("Time: O(n^2) worst/average, O(n) best | Space: O(1) in-place.")
