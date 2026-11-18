"""
Task 2 - Greedy loading of a relief truck (knapsack) and greedy change-making at relief cash counters.

(a) Fractional knapsack: divisible supplies (water, rice, fuel ...) of weight w_i and priority value v_i,
    truck capacity W. Greedy by value density v_i / w_i is OPTIMAL.  Two implementations:
      fractional_sort - merge-sort all items by density, Theta(n log n) comparisons;
      fractional_heap - bottom-up max-heap (<= 2n comparisons) + pop only the k items that are loaded,
                        Theta(n + k log n)  (the optimisation when the truck fills after a few items).
(b) 0/1 knapsack: indivisible equipment. Greedy (by density / value / weight) is NOT optimal; the exact
    answer comes from DP (Theta(nW)) or brute force (2^n). max(greedy, best single item) >= OPT/2.
(c) Coin change: greedy (largest coin first) is optimal for canonical systems (Indian rupee coins/notes)
    but not for e.g. {1, 3, 4}; DP gives the exact minimum; smallest_counterexample() checks a system
    exhaustively up to c_(m-1) + c_m (Kozen & Zaks, 1994).
Run:  py -3 knapsack_coin_change.py      (demo on the given test cases with every greedy step printed)
"""
import csv
import os
from collections import Counter, namedtuple
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
Item = namedtuple("Item", "name weight value")
INR = (1, 2, 5, 10, 20, 50, 100, 200, 500)


def load_items(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [Item(r["item"], int(r["weight_kg"]), int(r["value"])) for r in csv.DictReader(f)]


def validate_items(items, capacity):
    if capacity < 0:
        raise ValueError("capacity must be >= 0")
    for it in items:
        if it.weight <= 0 or it.value < 0:
            raise ValueError(f"item {it.name}: weight must be > 0 and value >= 0")


def density(it):
    return Fraction(it.value, it.weight)          # exact rational: no floating-point ties


# ----------------------------------------------------------------------------- (a) fractional knapsack
def merge_sort_desc(items, key, ops):
    """Stable merge sort in DECREASING key order; counts key comparisons."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left, right = merge_sort_desc(items[:mid], key, ops), merge_sort_desc(items[mid:], key, ops)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        ops["comparisons"] += 1
        if key(right[j]) > key(left[i]):
            out.append(right[j]); j += 1
        else:
            out.append(left[i]); i += 1
    return out + left[i:] + right[j:]


def _load(order, capacity, ops, trace):
    """Common greedy loop: take whole items while they fit, then a fraction of the next one."""
    room, total, plan = Fraction(capacity), Fraction(0), []
    for it in order:
        if room == 0:
            break
        ops["items_considered"] += 1
        take = min(Fraction(1), room / it.weight)
        room -= take * it.weight
        total += take * it.value
        plan.append((it, take))
        if trace is not None:
            trace.append((it, density(it), take, room, total))
    return total, plan


def fractional_sort(items, capacity, ops=None, trace=None):
    """Greedy by density after a full sort. Returns (max value as Fraction, [(item, fraction taken)])."""
    ops = Counter() if ops is None else ops
    validate_items(items, capacity)
    return _load(merge_sort_desc(list(items), density, ops), capacity, ops, trace)


def fractional_heap(items, capacity, ops=None, trace=None):
    """Same greedy, but items are popped lazily from a max-heap built bottom-up in O(n)."""
    ops = Counter() if ops is None else ops
    validate_items(items, capacity)
    h = list(items)
    key = [density(it) for it in h]

    def sift_down(i, n):
        while True:
            big, l, r = i, 2 * i + 1, 2 * i + 2
            if l < n:
                ops["comparisons"] += 1
                if key[l] > key[big]:
                    big = l
            if r < n:
                ops["comparisons"] += 1
                if key[r] > key[big]:
                    big = r
            if big == i:
                return
            h[i], h[big], key[i], key[big] = h[big], h[i], key[big], key[i]
            i = big

    n = len(h)
    for i in range(n // 2 - 1, -1, -1):          # bottom-up heapify: at most 2n comparisons
        sift_down(i, n)

    def pop_order():
        size = n
        while size:
            top = h[0]
            size -= 1
            h[0], key[0] = h[size], key[size]
            sift_down(0, size)
            yield top
    return _load(pop_order(), capacity, ops, trace)


# ----------------------------------------------------------------------------- (b) 0/1 knapsack
def greedy_01(items, capacity, rule="density", ops=None):
    """Greedy for INDIVISIBLE items: scan in rule order, take an item if it still fits (skip otherwise)."""
    ops = Counter() if ops is None else ops
    validate_items(items, capacity)
    key = {"density": density, "value": lambda it: it.value, "lightest": lambda it: -it.weight}[rule]
    room, total, chosen = capacity, 0, []
    for it in merge_sort_desc(list(items), key, ops):
        if it.weight <= room:
            room -= it.weight
            total += it.value
            chosen.append(it)
    return total, chosen


def greedy_01_half_approx(items, capacity):
    """max(greedy-by-density, most valuable single item that fits) - guaranteed >= OPT / 2."""
    g, chosen = greedy_01(items, capacity, "density")
    single = max((it for it in items if it.weight <= capacity), key=lambda it: it.value, default=None)
    if single is not None and single.value > g:
        return single.value, [single]
    return g, chosen


def knapsack_01_dp(items, capacity, ops=None):
    """Exact 0/1 knapsack by dynamic programming over capacities, Theta(n W) table cells."""
    ops = Counter() if ops is None else ops
    validate_items(items, capacity)
    n = len(items)
    best = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i, it in enumerate(items, 1):
        prev, row = best[i - 1], best[i]
        for c in range(capacity + 1):
            ops["dp_cells"] += 1
            row[c] = prev[c]
            if it.weight <= c and prev[c - it.weight] + it.value > row[c]:
                row[c] = prev[c - it.weight] + it.value
    chosen, c = [], capacity                       # trace back the chosen items
    for i in range(n, 0, -1):
        if best[i][c] != best[i - 1][c]:
            chosen.append(items[i - 1])
            c -= items[i - 1].weight
    return best[n][capacity], chosen[::-1]


def knapsack_01_bruteforce(items, capacity):
    """Exact answer by trying all 2^n subsets (n <= 20); independent check of the DP."""
    n, best = len(items), 0
    if n > 20:
        raise ValueError("brute force limited to n <= 20")
    for mask in range(1 << n):
        w = v = 0
        for i in range(n):
            if mask >> i & 1:
                w += items[i].weight
                v += items[i].value
        if w <= capacity and v > best:
            best = v
    return best


# ----------------------------------------------------------------------------- (c) coin change
def greedy_change(coins, amount, trace=None):
    """Largest-coin-first. Returns the list of coins, or None if the greedy gets stuck with a remainder."""
    if amount < 0 or not coins or min(coins) <= 0:
        raise ValueError("amount must be >= 0 and coins positive")
    left, used = amount, []
    for c in sorted(set(coins), reverse=True):
        k = left // c
        if k:
            used += [c] * k
            left -= k * c
            if trace is not None:
                trace.append((c, k, left))
    return used if left == 0 else None


def dp_change(coins, amount, ops=None):
    """Exact minimum number of coins (unbounded supply) by DP, Theta(amount * m). None if impossible."""
    ops = Counter() if ops is None else ops
    if amount < 0 or not coins or min(coins) <= 0:
        raise ValueError("amount must be >= 0 and coins positive")
    INF = float("inf")
    best, last = [0] + [INF] * amount, [0] * (amount + 1)
    for a in range(1, amount + 1):
        for c in coins:
            ops["dp_steps"] += 1
            if c <= a and best[a - c] + 1 < best[a]:
                best[a], last[a] = best[a - c] + 1, c
    if best[amount] == INF:
        return None
    used, a = [], amount
    while a:
        used.append(last[a])
        a -= last[a]
    return sorted(used, reverse=True)


def smallest_counterexample(coins):
    """First amount where greedy uses more coins than the optimum (or gets stuck although a solution
    exists). Checking amounts < c_(m-1) + c_m is sufficient (Kozen & Zaks). Returns (amount|None, bound)."""
    cs = sorted(set(coins))
    bound = cs[-1] + cs[-2] if len(cs) >= 2 else cs[-1]
    INF = float("inf")
    best = [0] + [INF] * bound
    for a in range(1, bound + 1):
        best[a] = min((best[a - c] + 1 for c in cs if c <= a), default=INF)
    for a in range(1, bound + 1):
        g = greedy_change(cs, a)
        if best[a] != INF and (g is None or len(g) > best[a]):
            return a, bound
    return None, bound


# ----------------------------------------------------------------------------- demo
def fmt_frac(x):
    return f"{float(x):,.2f}"


def main():
    print("TASK 2 - GREEDY KNAPSACK AND COIN CHANGE (relief-truck loading, relief cash counters)")
    print("=" * 108)
    supplies = load_items(os.path.join(HERE, "test_data", "given_G1_relief_supplies.csv"))
    W = 1000
    print(f"G1  Fractional knapsack - divisible relief supplies, truck capacity W = {W} kg")
    print(f"    {'step':>4} {'item':<16} {'w (kg)':>6} {'value':>6} {'v/w':>6} {'taken':>6} {'room left':>9} "
          f"{'value so far':>12}")
    ops, trace = Counter(), []
    total, plan = fractional_sort(supplies, W, ops, trace)
    for k, (it, dens, take, room, acc) in enumerate(trace, 1):
        print(f"    {k:>4} {it.name:<16} {it.weight:>6} {it.value:>6} {float(dens):>6.2f} {float(take):>6.2f} "
              f"{fmt_frac(room):>9} {fmt_frac(acc):>12}")
    hops = Counter()
    htotal, _ = fractional_heap(supplies, W, hops)
    print(f"    Optimal load value = {fmt_frac(total)}  (sort: {ops['comparisons']} comparisons; "
          f"heap: {hops['comparisons']} comparisons, same value {fmt_frac(htotal)})")

    print("\nG2  0/1 knapsack (indivisible) - textbook instance W = 50: (w, v) = (10, 60), (20, 100), (30, 120)")
    g2 = [Item("A", 10, 60), Item("B", 20, 100), Item("C", 30, 120)]
    gv, gc = greedy_01(g2, 50)
    dv, dc = knapsack_01_dp(g2, 50)
    fv, _ = fractional_sort(g2, 50)
    print(f"    greedy by density -> {gv} ({'+'.join(i.name for i in gc)})   DP optimum -> {dv} "
          f"({'+'.join(i.name for i in dc)})   fractional bound -> {fmt_frac(fv)}")

    equipment = load_items(os.path.join(HERE, "test_data", "given_G3_relief_equipment.csv"))
    print(f"\nG3  0/1 knapsack - indivisible relief equipment, truck bay {W} kg")
    code = {it.name: chr(65 + i) for i, it in enumerate(equipment)}          # short labels A, B, C ...
    print(f"    {'':<2} {'item':<20} {'w (kg)':>6} {'value':>6} {'v/w':>6}")
    for it in sorted(equipment, key=density, reverse=True):
        print(f"    {code[it.name]:<2} {it.name:<20} {it.weight:>6} {it.value:>6} {float(density(it)):>6.2f}")
    print(f"    {'strategy':<28} {'value':>6}  {'load (kg)':>9}  items")
    show = lambda ch: " + ".join(code[i.name] for i in ch)               # noqa: E731
    for rule in ("density", "value", "lightest"):
        v, ch = greedy_01(equipment, W, rule)
        print(f"    {'greedy by ' + rule:<28} {v:>6}  {sum(i.weight for i in ch):>9}  {show(ch)}")
    v, ch = greedy_01_half_approx(equipment, W)
    print(f"    {'max(greedy, best single)':<28} {v:>6}  {sum(i.weight for i in ch):>9}  {show(ch)}")
    dops = Counter()
    v, ch = knapsack_01_dp(equipment, W, dops)
    print(f"    {'DP optimum (' + format(dops['dp_cells'], ',') + ' cells)':<28} {v:>6}  "
          f"{sum(i.weight for i in ch):>9}  {show(ch)}")
    print(f"    brute force over 2^{len(equipment)} subsets confirms optimum = "
          f"{knapsack_01_bruteforce(equipment, W)}")

    print("\nG4  Coin change, Indian rupee system {1, 2, 5, 10, 20, 50, 100, 200, 500}, amount Rs 289")
    tr = []
    g = greedy_change(INR, 289, tr)
    print("    " + "  ".join(f"[{c} x{k} -> left {left}]" for c, k, left in tr))
    print(f"    greedy: {len(g)} coins/notes; DP optimum: {len(dp_change(INR, 289))}")
    print("\nG5  Coin change failure - system {1, 3, 4}, amount 6")
    print(f"    greedy: {greedy_change((1, 3, 4), 6)} = 3 coins;  DP optimum: {dp_change((1, 3, 4), 6)} = 2 coins")
    print("F1  Greedy stuck - system {2, 5}, amount 6")
    print(f"    greedy: {greedy_change((2, 5), 6)} (takes 5, remainder 1 cannot be paid);  "
          f"DP: {dp_change((2, 5), 6)}")
    print("\nCanonical-system check (exhaustive up to c_(m-1) + c_m):")
    print(f"    {'coin system':<32} {'bound':>5}  {'smallest counter-example':<26} greedy vs optimum")
    for name, cs in [("Indian rupee", INR), ("US cents", (1, 5, 10, 25)), ("{1, 3, 4}", (1, 3, 4)),
                     ("{1, 10, 25}", (1, 10, 25)), ("{1, 7, 10}", (1, 7, 10)),
                     ("UK pre-1971 {1,3,6,12,24,30}", (1, 3, 6, 12, 24, 30))]:
        a, bound = smallest_counterexample(cs)
        if a is None:
            print(f"    {name:<32} {bound:>5}  {'none -> CANONICAL':<26} greedy always optimal")
        else:
            print(f"    {name:<32} {bound:>5}  {'amount ' + str(a):<26} {greedy_change(cs, a)} vs "
                  f"{dp_change(cs, a)}")


if __name__ == "__main__":
    main()
