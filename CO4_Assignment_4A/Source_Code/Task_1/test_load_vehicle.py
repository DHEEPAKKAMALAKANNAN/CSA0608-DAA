"""
test_load_vehicle.py - checks the repaired LoadVehicle (Task 1) against an independent reference.

Reference: an optimal fractional loading always fills packages in SOME order, taking each whole until the
last one is cut.  Trying every order (n! permutations, n <= 6) and keeping the best value is therefore an
exhaustive optimum that does not use the value/weight rule.  Prints PASS/FAIL lines and a RESULT line.
"""
import itertools
import random

from load_vehicle import load_vehicle


def fill_in_order(order, capacity):
    """Value obtained by loading packages in the given order, cutting the last one."""
    remaining, total = capacity, 0.0
    for _, w, v in order:
        if remaining <= 0:
            break
        take = min(w, remaining)
        total += v * take / w
        remaining -= take
    return total


def brute_force(packages, capacity):
    return max((fill_in_order(p, capacity) for p in itertools.permutations(packages)), default=0.0)


def main():
    random.seed(42)
    passed = total = 0

    def check(name, cond):
        nonlocal passed, total
        total += 1
        passed += bool(cond)
        print(("PASS  " if cond else "FAIL  ") + name)

    given = [("P1", 10, 60), ("P2", 20, 100), ("P3", 30, 120), ("P4", 15, 45)]
    value, load = load_vehicle(given, 50)
    check("desk-check instance: total value = 240", abs(value - 240) < 1e-9)
    check("desk-check instance: P1, P2 whole, P3 fraction 2/3, P4 not loaded",
          [(p, round(f, 4)) for p, f, _, _ in load] == [("P1", 1.0), ("P2", 1.0), ("P3", 0.6667)])
    check("capacity never exceeded", sum(x[2] for x in load) <= 50 + 1e-9)
    check("capacity 0 -> nothing loaded, value 0", load_vehicle(given, 0) == (0.0, []))
    check("no packages -> value 0 (loop terminates)", load_vehicle([], 50) == (0.0, []))
    check("everything fits -> all whole, value = sum of values",
          abs(load_vehicle(given, 1000)[0] - 325) < 1e-9 and all(f == 1.0 for _, f, _, _ in
                                                                  load_vehicle(given, 1000)[1]))
    check("single package heavier than C -> one fraction C/w",
          abs(load_vehicle([("X", 80, 400)], 20)[0] - 100) < 1e-9)
    check("greedy-by-value would be worse here (value order gives 220 < 240)",
          fill_in_order(sorted(given, key=lambda p: -p[2]), 50) < value)
    bad = 0
    for _ in range(300):
        n = random.randint(1, 6)
        pk = [(f"X{i}", random.randint(1, 30), random.randint(1, 100)) for i in range(n)]
        cap = random.randint(0, 80)
        if abs(load_vehicle(pk, cap)[0] - brute_force(pk, cap)) > 1e-6:
            bad += 1
    check("300 random instances (n <= 6): greedy value = exhaustive optimum over all n! orders", bad == 0)
    print(f"RESULT: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
