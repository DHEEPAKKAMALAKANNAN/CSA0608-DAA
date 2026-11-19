"""
test_job_sequencing.py - checks the greedy JobSequencing (Task 2) against exhaustive search.

Reference: try all 2^n subsets; a subset is feasible iff for every t, at most t of its jobs have
deadline <= t (then sorting it by deadline gives a valid schedule).  Prints PASS/FAIL and RESULT.
"""
import itertools
import random

from job_sequencing import job_sequencing


def feasible(subset):
    ds = sorted(d for _, d, _ in subset)
    return all(ds[k] >= k + 1 for k in range(len(ds)))


def brute_force(jobs):
    best = 0
    for r in range(len(jobs) + 1):
        for sub in itertools.combinations(jobs, r):
            if feasible(sub):
                best = max(best, sum(p for _, _, p in sub))
    return best


def main():
    random.seed(42)
    passed = total = 0

    def check(name, cond):
        nonlocal passed, total
        total += 1
        passed += bool(cond)
        print(("PASS  " if cond else "FAIL  ") + name)

    jobs = [("A", 2, 80), ("B", 1, 35), ("C", 2, 60), ("D", 3, 40), ("E", 1, 25)]
    slot, profit, rej = job_sequencing(jobs)
    check("given instance: schedule t1=C, t2=A, t3=D", slot[1:] == ["C", "A", "D"])
    check("given instance: total profit 180, B and E rejected", profit == 180 and rej == ["B", "E"])
    check("given instance: 180 = exhaustive optimum over 2^5 subsets", brute_force(jobs) == 180)
    mod = [(j, d, 90 if j == "B" else p) for j, d, p in jobs]
    slot2, profit2, rej2 = job_sequencing(mod)
    check("modified (B=90): schedule t1=B, t2=A, t3=D; C displaced",
          slot2[1:] == ["B", "A", "D"] and "C" in rej2)
    check("modified (B=90): profit 210 = exhaustive optimum", profit2 == 210 == brute_force(mod))
    check("no jobs -> empty schedule, profit 0", job_sequencing([])[1] == 0)
    check("all deadlines 1 -> only the most profitable job", job_sequencing(
        [("X", 1, 5), ("Y", 1, 9), ("Z", 1, 7)])[0][1:] == ["Y"])
    check("deadline larger than n is capped (no out-of-range slot)",
          job_sequencing([("X", 100, 5), ("Y", 1, 3)])[1] == 8)
    bad = 0
    for _ in range(400):
        n = random.randint(1, 8)
        js = [(f"J{i}", random.randint(1, 5), random.randint(1, 100)) for i in range(n)]
        s, p, _ = job_sequencing(js)
        placed = [(t, x) for t, x in enumerate(s) if x]
        ok_deadlines = all(t <= dict((j, d) for j, d, _ in js)[x] for t, x in placed)
        if p != brute_force(js) or not ok_deadlines:
            bad += 1
    check("400 random instances (n <= 8): greedy profit = exhaustive optimum, deadlines respected", bad == 0)
    print(f"RESULT: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
