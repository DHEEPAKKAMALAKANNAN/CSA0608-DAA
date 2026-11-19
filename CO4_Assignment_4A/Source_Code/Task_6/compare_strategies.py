"""
compare_strategies.py - Task 6 Stage 2 (CO4 Assignment 4A): candidate strategies vs the DP optimum.

Greedy rules tried (each takes jobs in its own order and keeps a job if it is compatible with all jobs
kept so far): earliest finish time, highest value, shortest duration, highest value per unit time.
They are compared with the DP of energy_scheduling.py (= brute-force optimum) on the official 8-job data,
on one small counter-example per rule, and on the Stage-6 adversarial set.
"""
import os

from energy_scheduling import HERE, brute_force, read_jobs, schedule

RULES = {
    "earliest finish": lambda x: (x[2], x[1]),
    "highest value": lambda x: (-x[3], x[2]),
    "shortest duration": lambda x: (x[2] - x[1], x[2]),
    "value per unit time": lambda x: (-x[3] / (x[2] - x[1]), x[2]),
}


def greedy(jobs, key):
    kept = []
    for job in sorted(jobs, key=key):
        if all(job[2] <= k[1] or k[2] <= job[1] for k in kept):      # compatible with every kept job
            kept.append(job)
    return sum(j[3] for j in kept), sorted(j[0] for j in kept)


COUNTER = {                                       # small hand-made counter-examples (id, start, finish, value)
    "earliest finish": [("X1", 0, 2, 1), ("X2", 1, 10, 100)],
    "highest value": [("X1", 0, 10, 50), ("X2", 0, 5, 30), ("X3", 5, 10, 30)],
    "shortest duration": [("X1", 4, 6, 10), ("X2", 0, 5, 40), ("X3", 5, 10, 40)],
    "value per unit time": [("X1", 0, 1, 10), ("X2", 0, 10, 50)],
}


def table(title, jobs):
    best = schedule(jobs)[5]
    print(f"{title}   (DP optimum = {best}, brute force = {brute_force(jobs)[0]})")
    for name, key in RULES.items():
        val, ids = greedy(jobs, key)
        verdict = "optimal" if val == best else f"SUBOPTIMAL by {best - val}"
        print(f"   {name:<20} value {val:>4}   jobs {', '.join(ids):<26} {verdict}")
    _, _, _, _, sel, v, _ = schedule(jobs)
    print(f"   {'DP (my design)':<20} value {v:>4}   jobs {', '.join(sorted(sel)):<26} optimal\n")


def main():
    print("=" * 96)
    print("TASK 6 Stage 2 - candidate strategies compared with the DP optimum")
    print("=" * 96)
    table("Official 8-job data", read_jobs(os.path.join(HERE, "jobs.csv")))
    print("One counter-example per greedy rule:")
    for name, jobs in COUNTER.items():
        best = schedule(jobs)[5]
        val, ids = greedy(jobs, RULES[name])
        print(f"   {name:<20} jobs " + ", ".join(f"{j}[{s},{f})={v}" for j, s, f, v in jobs))
        print(f"   {'':<20} greedy keeps {', '.join(ids)} = {val};  optimum (DP) = {best}")
    print()
    table("Stage 6 adversarial set", read_jobs(os.path.join(HERE, "adversarial_jobs.csv")))


if __name__ == "__main__":
    main()
