"""
Task 2 - test suite for knapsack_dp.py.

* Table-driven cases from test_data/knapsack_test_cases.csv (given + own + boundary): bottom-up table,
  memory function, single row and brute force must all return the expected optimum; the backtracked parcel set
  must be feasible, reach the optimum and (where the optimum is unique) equal the expected set.
* 300 random instances checked against brute force, operation-count properties, invalid-input handling.
Prints PASS/FAIL lines and "RESULT: k/k tests passed".   Run:  py -3 test_knapsack.py
"""
import csv
import os
import random

from knapsack_dp import (backtrack_items, greedy_by_ratio, knapsack_bottom_up, knapsack_brute_force,
                         knapsack_memory_function, knapsack_one_row, load_instance)

HERE = os.path.dirname(os.path.abspath(__file__))
results = []


def check(name, condition, detail=""):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


def ints(field):
    return [int(x) for x in field.split(";")] if field else []


def solve_all(wts, vals, W):
    """Run every algorithm; return (values found, backtracked set, table F)."""
    F, _ = knapsack_bottom_up(wts, vals, W)
    chosen = backtrack_items(F, wts, W)
    found = [F[len(wts)][W], knapsack_memory_function(wts, vals, W)[0], knapsack_one_row(wts, vals, W)[0],
             knapsack_brute_force(wts, vals, W)[0]]
    return found, chosen, F


def table_cases():
    with open(os.path.join(HERE, "test_data", "knapsack_test_cases.csv"), encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            W, wts, vals = int(row["W"]), ints(row["weights"]), ints(row["values"])
            exp = int(row["expected_value"])
            found, chosen, _ = solve_all(wts, vals, W)
            feasible = sum(wts[i - 1] for i in chosen) <= W and sum(vals[i - 1] for i in chosen) == exp
            set_ok = (not row["expected_items"]) or chosen == ints(row["expected_items"])
            ok = all(f == exp for f in found) and feasible and set_ok
            check(f"{row['case_id']:<4}({row['category']:<8}) W={W:<3} n={len(wts):<2} optimum {exp:<3} "
                  f"{row['description']}", ok, f"4 algorithms = {found[0]}, items {chosen}")


def property_tests():
    rng = random.Random(42)
    all_ok, sets_ok = True, True
    for _ in range(300):
        n, W = rng.randint(1, 12), rng.randint(0, 40)
        wts = [rng.randint(1, 15) for _ in range(n)]
        vals = [rng.randint(0, 30) for _ in range(n)]
        found, chosen, _ = solve_all(wts, vals, W)
        all_ok &= len(set(found)) == 1
        sets_ok &= sum(wts[i - 1] for i in chosen) <= W and sum(vals[i - 1] for i in chosen) == found[0]
    check("300 random instances (n <= 12, W <= 40): table = memory function = single row = brute force", all_ok)
    check("300 random instances: backtracked set is feasible and its value equals the optimum", sets_ok)

    names, wts, vals = load_instance()
    F, ops = knapsack_bottom_up(wts, vals, 10)
    check("given instance: bottom-up evaluates exactly n*W = 50 cells", ops["cells"] == 50)
    _, MF, mops = knapsack_memory_function(wts, vals, 10)
    check("given instance: memory function computes 23 < 50 cells and agrees with F where computed",
          mops["cells_computed"] == 23 and all(MF[i][j] in (-1, F[i][j]) for i in range(6) for j in range(11)))
    gv, _ = greedy_by_ratio(wts, vals, 10)
    check("given instance: greedy by value/weight gives 88 < 94 (DP needed for optimality)", gv == 88 < F[5][10])
    rng2 = random.Random(7)
    ok = True
    for _ in range(20):
        n, W = rng2.randint(5, 30), rng2.randint(10, 200)
        w = [rng2.randint(1, 40) for _ in range(n)]
        v = [rng2.randint(1, 50) for _ in range(n)]
        ok &= knapsack_one_row(w, v, W)[1]["cells"] == knapsack_bottom_up(w, v, W)[1]["cells"] == n * W
    check("20 random instances: both bottom-up versions evaluate exactly n*W cells", ok)

    for label, args in [("negative capacity", ([1], [1], -1)), ("zero weight", ([0, 2], [3, 4], 5)),
                        ("length mismatch", ([1, 2], [3], 5)), ("negative value", ([1], [-2], 5))]:
        try:
            knapsack_bottom_up(*args)
            ok = False
        except ValueError:
            ok = True
        check(f"invalid input rejected with ValueError: {label}", ok)


def main():
    print("Task 2 - 0/1 knapsack: test run")
    table_cases()
    property_tests()
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
