# Exercise 101 - Bin Packing heuristics: Next-Fit, First-Fit, Best-Fit, First-Fit Decreasing
from math import ceil
from time import perf_counter


def next_fit(items, cap):
    """Keep only the last bin open. O(n)."""
    bins = [[items[0]]]
    for w in items[1:]:
        if sum(bins[-1]) + w <= cap:
            bins[-1].append(w)
        else:
            bins.append([w])
    return bins


def first_fit(items, cap):
    """Put each item into the first bin it fits in. O(n * bins) = O(n^2) worst case."""
    bins = []
    for w in items:
        for b in bins:
            if sum(b) + w <= cap:
                b.append(w)
                break
        else:
            bins.append([w])
    return bins


def best_fit(items, cap):
    """Put each item into the fullest bin that still has room. O(n^2) worst case."""
    bins = []
    for w in items:
        fits = [b for b in bins if sum(b) + w <= cap]
        if fits:
            max(fits, key=sum).append(w)
        else:
            bins.append([w])
    return bins


def first_fit_decreasing(items, cap):
    return first_fit(sorted(items, reverse=True), cap)


def average_time_us(func, items, cap, repeats=2000):
    t0 = perf_counter()
    for _ in range(repeats):
        func(items, cap)
    return (perf_counter() - t0) / repeats * 1e6


if __name__ == "__main__":
    items, cap = [4, 8, 1, 4, 2, 1], 10
    algorithms = [("Next-Fit", next_fit), ("First-Fit", first_fit), ("Best-Fit", best_fit),
                  ("First-Fit Decreasing", first_fit_decreasing)]
    print("Test Case 1")
    print(f"Input   : item weights = {items}, bin capacity = {cap}")
    print(f"Lower bound on bins = ceil(sum / capacity) = ceil({sum(items)} / {cap}) = {ceil(sum(items) / cap)}")
    for name, func in algorithms:
        bins = func(items, cap)
        packing = ", ".join(f"Bin {i}: {b}" for i, b in enumerate(bins, 1))
        print(f"{name:21s}: Number of Bins Used: {len(bins)} | {packing}")
        assert sorted(sum(bins, [])) == sorted(items)       # every item packed exactly once
    print("Note    : document lists 3 bins (Bin 1 [4,4,2], Bin 2 [8,1,1], Bin 3 [1]), but that packing uses three")
    print("          1's and only two exist, so Bin 3 is spurious. Correct: 2 bins, [4,4,2] + [8,1,1] (Best-Fit),")
    print("          which meets the lower bound of 2 (Next-Fit alone needs 3).")
    print("\nTest Case 2 - computational time on larger inputs (weights 1..9, capacity 10)")
    print("  n     Next-Fit(us)  First-Fit(us)  Best-Fit(us)   bins NF / FF / BF")
    for n in (250, 500, 1000, 2000):
        big = [(i * 7) % 9 + 1 for i in range(n)]
        times = [average_time_us(f, big, cap, 3) for _, f in algorithms[:3]]
        counts = [len(f(big, cap)) for _, f in algorithms[:3]]
        print(f"{n:5d} {times[0]:12.0f} {times[1]:14.0f} {times[2]:13.0f}   {counts[0]} / {counts[1]} / {counts[2]}")
    print("Computational Time: Next-Fit O(n); First-Fit / Best-Fit O(n^2) as coded (O(n log n) with a tree);")
    print("  FFD adds an O(n log n) sort. First-Fit and Best-Fit use at most about 1.7 x the optimal number of bins.")
