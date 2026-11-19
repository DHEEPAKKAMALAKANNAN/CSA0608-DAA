"""
test_energy_scheduling.py - checks the weighted-interval-scheduling DP (Task 6) against brute force over
all 2^n subsets, plus boundary cases (touching endpoints, equal finish times, empty input).
Prints PASS/FAIL lines and a RESULT line.
"""
import os
import random

from energy_scheduling import HERE, brute_force, compatible, latest_compatible, read_jobs, schedule


def main():
    random.seed(42)
    passed = total = 0

    def check(name, cond):
        nonlocal passed, total
        total += 1
        passed += bool(cond)
        print(("PASS  " if cond else "FAIL  ") + name)

    jobs = read_jobs(os.path.join(HERE, "jobs.csv"))
    J, p, OPT, _, sel, best, _ = schedule(jobs)
    check("official data: p(1..8) = 0 0 1 3 2 4 5 7", p[1:] == [0, 0, 1, 3, 2, 4, 5, 7])
    check("official data: OPT[0..8] = 0 20 50 50 90 110 120 160 200", OPT == [0, 20, 50, 50, 90, 110, 120, 160, 200])
    check("official data: selected J2, J5, J7, J8, value 200", sel == ["J2", "J5", "J7", "J8"] and best == 200)
    check("official data: 200 = brute force over 256 subsets", brute_force(jobs)[0] == 200)
    check("selected jobs are pairwise compatible", compatible([x for x in J if x[0] in sel]))
    adv = read_jobs(os.path.join(HERE, "adversarial_jobs.csv"))
    _, _, OPTa, _, sela, besta, _ = schedule(adv)
    check("adversarial set: OPT[4] = 100 (K1 tentatively best) but final optimum 150 with K2, K3, K4, K6",
          OPTa[4] == 100 and besta == 150 and sela == ["K2", "K3", "K4", "K6"] and brute_force(adv)[0] == 150)
    check("touching endpoints are compatible ([0,3) and [3,6))", schedule([("a", 0, 3, 5), ("b", 3, 6, 5)])[5] == 10)
    check("overlap by one unit is incompatible ([0,4) and [3,6))", schedule([("a", 0, 4, 5), ("b", 3, 6, 7)])[5] == 7)
    check("empty input -> value 0, no jobs", schedule([])[4:6] == ([], 0))
    check("p(j) binary search with equal finish times",
          latest_compatible([("a", 0, 5, 1), ("b", 2, 5, 1), ("c", 5, 7, 1)], 3) == 2)
    bad = 0
    for _ in range(500):
        n = random.randint(1, 10)
        js = []
        for i in range(n):
            s = random.randint(0, 15)
            js.append((f"T{i}", s, s + random.randint(1, 6), random.randint(1, 60)))
        Jr, _, _, _, s_ids, b, _ = schedule(js)
        chosen = [x for x in Jr if x[0] in s_ids]
        if b != brute_force(js)[0] or not compatible(chosen) or sum(x[3] for x in chosen) != b:
            bad += 1
    check("500 random instances (n <= 10): DP = brute force, reported jobs compatible and worth OPT[n]", bad == 0)
    print(f"RESULT: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
