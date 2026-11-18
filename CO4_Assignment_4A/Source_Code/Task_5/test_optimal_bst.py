"""
Task 5 - test suite for optimal_bst.py.

* Table-driven cases from test_data/obst_test_cases.csv (given + own + boundary) with hand-derived optimal costs
  (total weighted comparisons) and roots.
* 200 random instances (n <= 8) vs exhaustive search over all Catalan(n) BSTs; tree rebuilt from R has cost C(1, n);
  Knuth's version gives the same optimum on 100 random instances up to n = 60; candidate counts; invalid input.
Prints PASS/FAIL lines and "RESULT: k/k tests passed".   Run:  py -3 test_optimal_bst.py
"""
import csv
import os
import random

from optimal_bst import (all_bst_costs, balanced_depths, build_tree, depths_of, load_keys, optimal_bst,
                         optimal_bst_knuth, tree_cost)

HERE = os.path.dirname(os.path.abspath(__file__))
results = []


def check(name, condition, detail=""):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


def table_cases():
    with open(os.path.join(HERE, "test_data", "obst_test_cases.csv"), encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            p = [int(x) for x in row["frequencies"].split(";")] if row["frequencies"] else []
            n = len(p)
            C, R, _ = optimal_bst(p)
            Ck, _, _ = optimal_bst_knuth(p)
            cost = C[1][n] if n else 0
            root = R[1][n] if n else 0
            tree_ok = (not n) or tree_cost(depths_of(build_tree(R, 1, n)), p) == cost
            ok = cost == int(row["expected_cost"]) and root == int(row["expected_root"]) and tree_ok \
                and (not n or Ck[1][n] == cost)
            check(f"{row['case_id']:<3}({row['category']:<8}) n={n} {row['description']}", ok,
                  f"cost {cost}, root {root}")


def property_tests():
    keys, p = load_keys()
    C, R, ops = optimal_bst(p)
    check("given instance: root table R = [[1,1,1,3],[2,3,3],[3,4],[4]] (hand trace)",
          [R[1][1:5], R[2][2:5], R[3][3:5], R[4][4:5]] == [[1, 1, 1, 3], [2, 3, 3], [3, 4], [4]])
    check("given instance: optimal 1.85 beats balanced BST 2.20",
          C[1][4] == 185 and tree_cost(balanced_depths(1, 4), p) == 220)
    rng = random.Random(42)
    ok_ex, ok_tree = True, True
    for _ in range(200):
        n = rng.randint(1, 8)
        q = [rng.randint(0, 50) for _ in range(n)]
        Cq, Rq, _ = optimal_bst(q)
        ok_ex &= Cq[1][n] == min(c for c, _ in all_bst_costs(q))
        ok_tree &= tree_cost(depths_of(build_tree(Rq, 1, n)), q) == Cq[1][n]
    check("200 random instances (n <= 8): DP optimum = minimum over ALL Catalan(n) BSTs", ok_ex)
    check("200 random instances: tree rebuilt from R has exactly the cost C[1][n]", ok_tree)
    ok_k, ok_cnt = True, True
    for _ in range(100):
        n = rng.randint(1, 60)
        q = [rng.randint(0, 100) for _ in range(n)]
        Cq, _, oq = optimal_bst(q)
        Ck, _, ok = optimal_bst_knuth(q)
        ok_k &= Cq[1][n] == Ck[1][n] and ok["candidates"] <= oq["candidates"]
        ok_cnt &= oq["candidates"] == n * (n - 1) * (n + 4) // 6
    check("100 random instances (n <= 60): Knuth's version = Levitin's optimum, never more candidates", ok_k)
    check("100 random instances: Levitin's version examines exactly n(n-1)(n+4)/6 root candidates", ok_cnt)
    try:
        optimal_bst([3, -1, 2])
        ok = False
    except ValueError:
        ok = True
    check("negative frequency rejected with ValueError", ok)


def main():
    print("Task 5 - optimal binary search tree: test run")
    table_cases()
    property_tests()
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
