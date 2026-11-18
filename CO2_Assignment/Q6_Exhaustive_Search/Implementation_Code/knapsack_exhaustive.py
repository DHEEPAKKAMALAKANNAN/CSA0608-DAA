"""Q6 - Exhaustive search for humanitarian airlift planning (0/1 knapsack).

Problem
    A helicopter has a strict payload limit C (kg).  Each package has (Package ID, Weight, Humanitarian Value).
    Choose a combination of packages whose total weight does not exceed C and whose total value is maximal.

Design (student-designed enumeration)
    * representation : an n-bit vector stored as an integer mask; bit i = 1 <=> package i is loaded;
    * generation     : count mask = 0, 1, ..., 2^n - 1 (every subset exactly once);
    * feasibility    : W(mask) = sum of selected weights <= C;
    * evaluation     : V(mask) = sum of selected values;
    * retention      : keep the best (V, then lower W as tie-break) seen so far.
    Counters: candidates generated, feasible candidates, bit checks (n per candidate), best-so-far updates.

Run this file for the tests (DP cross-check) and the fully printed 32-row enumeration of the n = 5 instance.
"""

import itertools
import random

# Designed verification instance: greedy "highest value per kg first" gives 101, the true optimum is 102.
SMALL_INSTANCE = [("P1", "Surgical kit", 9, 61), ("P2", "Water purification", 5, 32),
                  ("P3", "Vaccine cold-box", 6, 41), ("P4", "Satellite phone", 3, 18),
                  ("P5", "Infant formula", 4, 28)]
SMALL_CAPACITY = 15


def exhaustive_airlift(weights, values, capacity, trace=None):
    """Examine all 2^n loading plans; return (best_mask, best_value, best_weight, counters).

    If a list is passed as `trace`, one row (mask, weight, value, feasible, best_value_so_far) is appended per
    candidate - used to print the full enumeration table of the small instance."""
    n = len(weights)
    best_value, best_weight, best_mask = -1, 0, 0
    generated = feasible = bit_checks = updates = 0
    for mask in range(1 << n):                       # generation: binary counting
        generated += 1
        w = v = 0
        for i in range(n):                           # decode the bit vector
            if mask >> i & 1:
                w += weights[i]
                v += values[i]
        bit_checks += n
        ok = w <= capacity                           # feasibility
        if ok:
            feasible += 1
            if v > best_value or (v == best_value and w < best_weight):   # evaluation + retention
                best_value, best_weight, best_mask = v, w, mask
                updates += 1
        if trace is not None:
            trace.append((mask, w, v, ok, best_value))
    counters = {"generated": generated, "feasible": feasible, "bit_checks": bit_checks, "updates": updates}
    return best_mask, best_value, best_weight, counters


def dp_knapsack(weights, values, capacity):
    """Independent cross-check: 0/1 knapsack dynamic programming, best[c] = max value with weight <= c."""
    best = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):
            best[c] = max(best[c], best[c - w] + v)
    return best[capacity]


def greedy_by_ratio(weights, values, capacity):
    """Heuristic used only for comparison: take packages in decreasing value/weight while they fit."""
    order = sorted(range(len(weights)), key=lambda i: values[i] / weights[i], reverse=True)
    w = v = 0
    chosen = []
    for i in order:
        if w + weights[i] <= capacity:
            w, v = w + weights[i], v + values[i]
            chosen.append(i)
    return sorted(chosen), v, w


def random_instance(n, seed):
    """Random airlift manifest: weights 5..60 kg, values 10..100, payload = 40 % of the total weight."""
    rng = random.Random(seed)
    weights = [rng.randint(5, 60) for _ in range(n)]
    values = [rng.randint(10, 100) for _ in range(n)]
    return weights, values, int(0.4 * sum(weights))


def selected(mask, n):
    return [i for i in range(n) if mask >> i & 1]


# ------------------------------------------------------------------------------------------------- tests
def run_tests():
    print("CORRECTNESS TESTS  (expected optimum from independent 0/1-knapsack DP; feasible count from itertools)")
    passed = total = 0

    def check(name, ok, detail):
        nonlocal passed, total
        total += 1
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  Q6 {name:<33} {detail}")

    ws, vs = [p[2] for p in SMALL_INSTANCE], [p[3] for p in SMALL_INSTANCE]
    mask, val, wt, c = exhaustive_airlift(ws, vs, SMALL_CAPACITY)
    check("designed n=5 instance optimum", val == 102 == dp_knapsack(ws, vs, SMALL_CAPACITY),
          f"expected 102 (hand + DP), actual {val} = {'+'.join(SMALL_INSTANCE[i][0] for i in selected(mask, 5))},"
          f" {wt} kg")
    check("candidates generated = 2^n", c["generated"] == 32, f"expected 32, actual {c['generated']}")
    check("empty manifest", exhaustive_airlift([], [], 10)[1] == 0, "expected value 0 (load nothing)")
    check("nothing fits", exhaustive_airlift([20, 30], [5, 9], 10)[:2] == (0, 0), "expected empty load, value 0")
    check("everything fits", exhaustive_airlift([1, 2, 3], [4, 5, 6], 100)[1] == 15, "expected value 15 (all)")
    check("tie -> lighter load kept", exhaustive_airlift([4, 3], [10, 10], 5)[2] == 3, "expected weight 3 kg")
    rng = random.Random(1)
    agree = feas_ok = True
    for trial in range(40):
        n = rng.randint(1, 14)
        w, v, cap = random_instance(n, 100 + trial)
        m, best, bw, cnt = exhaustive_airlift(w, v, cap)
        agree &= best == dp_knapsack(w, v, cap) and bw <= cap and sum(w[i] for i in selected(m, n)) == bw
        feas = sum(1 for r in range(n + 1) for s in itertools.combinations(range(n), r) if sum(w[i] for i in s) <= cap)
        feas_ok &= cnt["feasible"] == feas and cnt["generated"] == 2 ** n and cnt["bit_checks"] == n * 2 ** n
    check("40 random manifests (n = 1..14)", agree, "optimum equals DP and decoded load is consistent")
    check("40 random manifests: counters", feas_ok, "feasible = itertools, generated = 2^n, checks = n*2^n")
    print(f"RESULT: {passed}/{total} tests passed")
    return passed == total


def enumeration_table():
    """Print every one of the 2^5 = 32 candidate loading plans of the designed instance."""
    ws, vs = [p[2] for p in SMALL_INSTANCE], [p[3] for p in SMALL_INSTANCE]
    print(f"\nSMALL INSTANCE - payload limit {SMALL_CAPACITY} kg")
    for pid, name, w, v in SMALL_INSTANCE:
        print(f"   {pid}  {name:<19} {w:>2} kg  value {v:>3}  ({v / w:.2f} per kg)")
    trace = []
    mask, val, wt, c = exhaustive_airlift(ws, vs, SMALL_CAPACITY, trace)
    print(f"\nFULL ENUMERATION (bits shown P5..P1; '*' = new best feasible plan)")
    head = f"{'mask':>5}  {'bits':<5}  {'packages':<15}{'kg':>4}{'value':>7}  {'feasible':<9}{'best':>5}"
    print(f"{head:<64}  {head}")
    prev_best = -1
    lines = []
    for m, w, v, ok, best in trace:
        star = "*" if ok and best != prev_best else " "
        prev_best = best
        names = "+".join(SMALL_INSTANCE[i][0] for i in selected(m, 5)) or "(none)"
        lines.append(f"{m:>5}  {m:05b}  {names:<15}{w:>4}{v:>7}  {'yes' if ok else 'NO':<9}{best:>4}{star}")
    for left, right in zip(lines[:16], lines[16:]):
        print(f"{left:<64}  {right}")
    chosen = [SMALL_INSTANCE[i][0] for i in selected(mask, 5)]
    g_sel, g_val, g_w = greedy_by_ratio(ws, vs, SMALL_CAPACITY)
    print(f"\nOPTIMUM: load {' + '.join(chosen)} = {wt} kg, value {val}   [generated {c['generated']}, feasible"
          f" {c['feasible']}, bit checks {c['bit_checks']}, best-so-far updates {c['updates']}]")
    print(f"Check  : DP optimum = {dp_knapsack(ws, vs, SMALL_CAPACITY)};  greedy by value/kg loads "
          f"{' + '.join(SMALL_INSTANCE[i][0] for i in g_sel)} = {g_w} kg, value {g_val} (misses the optimum by "
          f"{val - g_val})")


def main():
    ok = run_tests()
    enumeration_table()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
