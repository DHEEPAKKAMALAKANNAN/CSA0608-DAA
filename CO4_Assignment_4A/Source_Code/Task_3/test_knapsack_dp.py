"""
test_knapsack_dp.py - checks the 0/1 knapsack DP (Task 3) against brute force over all subsets.
Prints PASS/FAIL lines and a RESULT line.
"""
import random

from knapsack_dp import brute_force, knapsack


def main():
    random.seed(42)
    passed = total = 0

    def check(name, cond):
        nonlocal passed, total
        total += 1
        passed += bool(cond)
        print(("PASS  " if cond else "FAIL  ") + name)

    items = [("P", 2, 12), ("Q", 3, 20), ("R", 4, 25), ("S", 5, 30)]
    DP, best, sel, _ = knapsack(items, 7)
    check("given instance: optimum 45", best == 45)
    check("given instance: reconstruction selects Q and R", sel == ["Q", "R"])
    check("given instance: 45 = brute-force optimum over 16 subsets", brute_force(items, 7)[0] == 45)
    check("rows are non-decreasing in w (more capacity never hurts)",
          all(DP[i][w] <= DP[i][w + 1] for i in range(5) for w in range(7)))
    check("capacity 0 -> value 0, nothing selected", knapsack(items, 0)[1:3] == (0, []))
    check("no items -> value 0", knapsack([], 10)[1] == 0)
    check("item heavier than W is never selected", knapsack([("X", 9, 100), ("Y", 1, 1)], 5)[2] == ["Y"])
    bad = 0
    for _ in range(400):
        n = random.randint(1, 9)
        its = [(f"I{i}", random.randint(1, 10), random.randint(1, 60)) for i in range(n)]
        W = random.randint(0, 25)
        _, b, s, _ = knapsack(its, W)
        chosen = [x for x in its if x[0] in s]
        if b != brute_force(its, W)[0] or sum(x[2] for x in chosen) != b or sum(x[1] for x in chosen) > W:
            bad += 1
    check("400 random instances (n <= 9): DP value = brute force, reconstructed set is feasible and "
          "worth exactly DP[n][W]", bad == 0)
    print(f"RESULT: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
