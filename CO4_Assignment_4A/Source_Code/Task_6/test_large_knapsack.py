"""
Task 6 - test suite for large_knapsack.py (redesigned planner).

* Table-driven cases (test_data/large_knapsack_test_cases.csv): R1 and R2 return the hand-derived optimum and a
  feasible item set whose values add up to it.
* 300 random small instances: R1 = R2 = Task 2 table = brute force; R1 recovers exactly the Task 2 item set.
* A medium instance (n = 200, W = 5,000): R1 = R2 = original; cell-count bounds (R1 = sum of (W - w + 1),
  R2 <= 2nW); R1's stored decision bits <= n(W + 1)/8 bytes plus object headers.
* Planner decisions, invalid input, reproducible instance file.
Prints PASS/FAIL lines and "RESULT: k/k tests passed".   Run:  py -3 test_large_knapsack.py
"""
import csv
import os
import random
import sys

from large_knapsack import (INSTANCE_CSV, choose_design, generate_instance, knapsack_bitpacked,
                            knapsack_divide_conquer, load_instance, plan_load)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Task_2"))
from knapsack_dp import backtrack_items, knapsack_bottom_up, knapsack_brute_force  # noqa: E402

results = []


def check(name, condition, detail=""):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


def ints(field):
    return [int(x) for x in field.split(";")] if field else []


def consistent(weights, values, W, value, items):
    return sum(weights[i - 1] for i in items) <= W and sum(values[i - 1] for i in items) == value


def table_cases():
    with open(os.path.join(HERE, "test_data", "large_knapsack_test_cases.csv"), encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            W, w, v, exp = int(row["W"]), ints(row["weights"]), ints(row["values"]), int(row["expected_value"])
            v1, s1, _ = knapsack_bitpacked(w, v, W)
            v2, s2, _ = knapsack_divide_conquer(w, v, W)
            ok = v1 == v2 == exp and consistent(w, v, W, v1, s1) and consistent(w, v, W, v2, s2)
            check(f"{row['case_id']:<4}({row['category']:<8}) W={W:<3} n={len(w)} {row['description']}", ok,
                  f"R1 {v1} {s1}, R2 {v2} {s2}")


def property_tests():
    rng = random.Random(42)
    ok_val, ok_set, ok_r2 = True, True, True
    for _ in range(300):
        n, W = rng.randint(1, 12), rng.randint(0, 50)
        w = [rng.randint(1, 15) for _ in range(n)]
        v = [rng.randint(0, 30) for _ in range(n)]
        F, _ = knapsack_bottom_up(w, v, W)
        v1, s1, _ = knapsack_bitpacked(w, v, W)
        v2, s2, _ = knapsack_divide_conquer(w, v, W)
        ok_val &= v1 == v2 == F[n][W] == knapsack_brute_force(w, v, W)[0]
        ok_set &= s1 == backtrack_items(F, w, W)
        ok_r2 &= consistent(w, v, W, v2, s2)
    check("300 random instances: R1 = R2 = Task 2 table = brute force (optimum value)", ok_val)
    check("300 random instances: R1 recovers exactly the item set of Task 2's backtracking", ok_set)
    check("300 random instances: R2's item set is feasible and its values add up to the optimum", ok_r2)

    w, v = generate_instance(200, seed=7)
    W = 5_000
    F, _ = knapsack_bottom_up(w, v, W)
    v1, s1, o1 = knapsack_bitpacked(w, v, W)
    v2, s2, o2 = knapsack_divide_conquer(w, v, W)
    check("medium instance (n = 200, W = 5,000): R1 = R2 = original optimum, R1 items = original items",
          v1 == v2 == F[200][W] and s1 == backtrack_items(F, w, W), f"optimum {v1}")
    check("medium instance: R1 evaluates exactly sum over items of (W - w_i + 1) cells",
          o1["cells"] == sum(W - x + 1 for x in w if x <= W))
    check("medium instance: R2 evaluates at most 2nW cells", o2["cells"] <= 2 * 200 * W,
          f"{o2['cells']:,} <= {2 * 200 * W:,}")
    check("medium instance: R1 stores at most n(W+1)/8 bytes of decision bits",
          o1["bit_bytes"] <= 200 * (W + 1) / 8, f"{o1['bit_bytes']:,} bytes")
    rng2 = random.Random(3)
    ok = True
    for _ in range(30):
        n, W = rng2.randint(2, 40), rng2.randint(1, 400)
        ww = [rng2.randint(1, 60) for _ in range(n)]
        vv = [rng2.randint(1, 60) for _ in range(n)]
        ok &= knapsack_divide_conquer(ww, vv, W)[2]["cells"] <= 2 * n * W
    check("30 random instances: R2 never exceeds the 2nW cell bound", ok)

    check("planner: n = 200, W = 100,000, 32 MB -> R1", choose_design(200, 100_000, 32) == "R1 bit-packed")
    check("planner: n = 3,000, W = 100,000, 32 MB -> R2", choose_design(3000, 100_000, 32) == "R2 divide&conquer")
    try:
        plan_load([5] * 200, [7] * 200, 1_000_000, 32)
        ok = False
    except MemoryError:
        ok = True
    check("planner: W = 1,000,000 under 32 MB is refused with MemoryError", ok)
    for fn in (knapsack_bitpacked, knapsack_divide_conquer):
        try:
            fn([1, 0], [2, 3], 5)
            ok = False
        except ValueError:
            ok = True
        check(f"{fn.__name__}: zero weight rejected with ValueError", ok)
    w_file, v_file = load_instance(INSTANCE_CSV)
    check("instance file has 200 consignments and is reproduced exactly by seed 42",
          (w_file, v_file) == generate_instance(200, seed=42) and len(w_file) == 200)


def main():
    print("Task 6 - large-capacity knapsack redesign: test run")
    table_cases()
    property_tests()
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
