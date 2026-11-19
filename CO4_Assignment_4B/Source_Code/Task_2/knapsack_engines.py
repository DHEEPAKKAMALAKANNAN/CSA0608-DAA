"""
Task 2 - Greedy vs Dynamic Programming for loading a delivery vehicle of limited capacity W.

Every item has (Item ID, weight, value).
  Solution A  fractional_greedy   Fractional knapsack: items may be split. Sort by value/weight (merge sort,
                                  comparisons counted), take whole items while they fit, then a fraction of
                                  the next one. Optimal for the fractional problem. Work Theta(n log n), memory
                                  Theta(n), independent of W.
  Solution B  knapsack_01_dp      0/1 knapsack: items are indivisible. Table best[i][c] = best value using the
                                  first i items within capacity c. Optimal. Work Theta(n * W) cells, memory
                                  (n + 1)(W + 1) cells (pseudo-polynomial: grows with the NUMBER W, not its size).
  greedy_01_ratio                 the same value/weight intuition applied to the 0/1 problem (take an item
                                  whole if it still fits, else skip it) - fast but NOT always optimal.
  first_blocking_commitment       for every greedy commitment, the best value still reachable afterwards
                                  (computed exactly by DP on the undecided items); the first commitment after
                                  which the optimum is unreachable is the one that prevents the optimum.
  greedy_01_best_of_two           max(greedy_01_ratio, single most valuable item) - guaranteed >= OPT / 2.
  knapsack_01_bruteforce          independent 2^n reference for the tests.
Only algorithm logic lives here (no printing); decision traces are returned as lists of tuples.
"""
from collections import Counter, namedtuple
from fractions import Fraction

Item = namedtuple("Item", "item_id weight value")
GreedyStep = namedtuple("GreedyStep", "item ratio decision fraction room_after value_after")


def validate(items, capacity):
    """Reject inputs that would make the algorithms silently wrong."""
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 0:
        raise ValueError(f"capacity must be a non-negative integer, got {capacity!r}")
    ids = set()
    for it in items:
        if not isinstance(it.weight, int) or it.weight <= 0:
            raise ValueError(f"item {it.item_id}: weight must be a positive integer, got {it.weight!r}")
        if it.value < 0:
            raise ValueError(f"item {it.item_id}: value must be >= 0, got {it.value!r}")
        if it.item_id in ids:
            raise ValueError(f"duplicate item id {it.item_id}")
        ids.add(it.item_id)


def ratio(it):
    """Value per unit weight as an exact fraction (no floating-point ties)."""
    return Fraction(it.value, it.weight)


def sort_by_ratio(items, ops):
    """Stable merge sort by decreasing value/weight (ties keep the input order).
    Counts key comparisons in ops['comparisons']."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left, right = sort_by_ratio(items[:mid], ops), sort_by_ratio(items[mid:], ops)
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        ops["comparisons"] += 1
        if ratio(right[j]) > ratio(left[i]):
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    return merged + left[i:] + right[j:]


# ----------------------------------------------------------------------------- Solution A
def fractional_greedy(items, capacity, ops=None):
    """Returns (max value as Fraction, [(item, fraction taken)], decision trace)."""
    ops = Counter() if ops is None else ops
    validate(items, capacity)
    room, total, plan, trace = Fraction(capacity), Fraction(0), [], []
    for it in sort_by_ratio(list(items), ops):
        ops["items_examined"] += 1
        if room == 0:
            trace.append(GreedyStep(it, ratio(it), "not needed (vehicle full)", Fraction(0), room, total))
            continue
        take = min(Fraction(1), room / it.weight)
        room -= take * it.weight
        total += take * it.value
        plan.append((it, take))
        trace.append(GreedyStep(it, ratio(it), "take whole" if take == 1 else "take fraction", take, room, total))
    ops["memory_cells"] = len(items)                 # the sorted list
    return total, plan, trace


# ----------------------------------------------------------------------------- greedy intuition on 0/1
def greedy_01_ratio(items, capacity, ops=None):
    """Value/weight greedy for indivisible items. Returns (value, chosen items, decision trace)."""
    ops = Counter() if ops is None else ops
    validate(items, capacity)
    room, total, chosen, trace = capacity, 0, [], []
    for it in sort_by_ratio(list(items), ops):
        ops["items_examined"] += 1
        if it.weight <= room:
            room -= it.weight
            total += it.value
            chosen.append(it)
            trace.append(GreedyStep(it, ratio(it), "COMMIT (take)", 1, room, total))
        else:
            trace.append(GreedyStep(it, ratio(it), "skip (does not fit)", 0, room, total))
    ops["memory_cells"] = len(items)
    return total, chosen, trace


def greedy_01_best_of_two(items, capacity):
    """max(ratio greedy, best single item that fits): never below OPT / 2. Returns (value, chosen)."""
    value, chosen, _ = greedy_01_ratio(items, capacity)
    single = max((it for it in items if it.weight <= capacity), key=lambda it: it.value, default=None)
    if single is not None and single.value > value:
        return single.value, [single]
    return value, chosen


# ----------------------------------------------------------------------------- Solution B
def knapsack_01_dp(items, capacity, ops=None, keep_table=False):
    """Exact 0/1 knapsack. Returns (optimum, chosen items, table or None).

    best[i][c] = max(best[i-1][c], best[i-1][c - w_i] + v_i if w_i <= c). Trace-back from best[n][W]:
    item i was taken iff best[i][c] != best[i-1][c].
    """
    ops = Counter() if ops is None else ops
    validate(items, capacity)
    n = len(items)
    best = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i, it in enumerate(items, 1):
        prev, row = best[i - 1], best[i]
        for c in range(capacity + 1):
            ops["dp_cells"] += 1
            row[c] = prev[c]
            if it.weight <= c:
                ops["comparisons"] += 1
                if prev[c - it.weight] + it.value > row[c]:
                    row[c] = prev[c - it.weight] + it.value
    ops["memory_cells"] = (n + 1) * (capacity + 1)
    chosen, c = [], capacity
    for i in range(n, 0, -1):
        if best[i][c] != best[i - 1][c]:
            chosen.append(items[i - 1])
            c -= items[i - 1].weight
    return best[n][capacity], chosen[::-1], (best if keep_table else None)


def knapsack_01_value_1d(items, capacity, ops=None):
    """Optimum VALUE only with one row of W + 1 cells (memory-optimised DP; no item reconstruction)."""
    ops = Counter() if ops is None else ops
    validate(items, capacity)
    row = [0] * (capacity + 1)
    for it in items:
        for c in range(capacity, it.weight - 1, -1):
            ops["dp_cells"] += 1
            if row[c - it.weight] + it.value > row[c]:
                row[c] = row[c - it.weight] + it.value
    ops["memory_cells"] = capacity + 1
    return row[capacity]


def knapsack_01_bruteforce(items, capacity):
    """Independent reference: best value over all 2^n subsets (n <= 20)."""
    validate(items, capacity)
    n = len(items)
    if n > 20:
        raise ValueError("brute force limited to n <= 20 items")
    best = 0
    for mask in range(1 << n):
        w = v = 0
        for k in range(n):
            if mask >> k & 1:
                w += items[k].weight
                v += items[k].value
        if w <= capacity and v > best:
            best = v
    return best


# ----------------------------------------------------------------------------- diagnosis of the greedy failure
def first_blocking_commitment(items, capacity):
    """Walk through the ratio-greedy decisions; after each one compute (exactly, by DP over the items not yet
    decided) the best total value that is still reachable. Returns (optimum, rows, first_blocking_index) with
    rows = [(step, item, decision, committed value, room, best reachable)]. first_blocking_index is the step of
    the first COMMIT after which best reachable < optimum (None if the greedy is optimal)."""
    optimum, _, _ = knapsack_01_dp(items, capacity)
    order = sort_by_ratio(list(items), Counter())
    room, committed, rows, blocking = capacity, 0, [], None
    for step, it in enumerate(order, 1):
        if it.weight <= room:
            room -= it.weight
            committed += it.value
            decision = "COMMIT"
        else:
            decision = "skip"
        rest = order[step:]
        reachable = committed + (knapsack_01_dp(rest, room)[0] if rest else 0)
        rows.append((step, it, decision, committed, room, reachable))
        if blocking is None and decision == "COMMIT" and reachable < optimum:
            blocking = step
    return optimum, rows, blocking
