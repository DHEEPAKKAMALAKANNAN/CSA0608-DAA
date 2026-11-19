"""
job_sequencing.py - Task 2 (CO4 Assignment 4A): greedy Job Sequencing with Deadlines.

Problem: unit-time jobs (id, deadline, profit); a job earns its profit only if it is processed in a slot
t <= deadline; one job per slot.  Maximise total profit.  This program implements the report's pseudocode
ALGORITHM JobSequencing(J, n): SORT by profit (descending), then place each job in the LATEST free slot
on or before its deadline, else reject it.  It reproduces the manual desk-check (Task 2.4) and the
modified-instance check (Task 2.5); the traces were first done by hand, this run only confirms them.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def read_jobs(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [(r["job"], int(r["deadline"]), int(r["profit"])) for r in csv.DictReader(f)]


def job_sequencing(jobs, trace=None):
    """Return (slot list, total profit, rejected ids).  slot[t] = job id in slot t (1-based), None if free."""
    order = sorted(jobs, key=lambda j: (-j[2], j[1], j[0]))     # profit desc; ties: earlier deadline, id
    max_d = max((d for _, d, _ in jobs), default=0)
    n = len(jobs)
    m = min(max_d, n)                                          # never need more than n slots
    slot = [None] * (m + 1)                                    # slot[0] unused
    total, rejected = 0, []
    for job_id, d, p in order:
        t = min(d, m)
        checked = []
        while t >= 1 and slot[t] is not None:                  # feasibility: search latest free slot <= d
            checked.append(f"{t}:busy")
            t -= 1
        if t >= 1:
            slot[t] = job_id                                   # placement
            total += p                                         # profit update
            checked.append(f"{t}:free")
            decision = f"ACCEPT -> slot {t}"
        else:
            rejected.append(job_id)
            decision = "REJECT (no free slot <= d)"
        if trace is not None:
            trace.append((job_id, d, p, " ".join(checked) or "-", decision,
                          "[" + " ".join(s or "-" for s in slot[1:]) + "]", total))
    return slot, total, rejected


def print_run(title, jobs):
    print(title)
    print("  jobs:", ", ".join(f"{j}(d={d},p={p})" for j, d, p in jobs))
    print("  sorted by profit desc:", " > ".join(f"{j}{p}" for j, _, p in
                                                 sorted(jobs, key=lambda j: (-j[2], j[1], j[0]))))
    trace = []
    slot, total, rejected = job_sequencing(jobs, trace)
    print(f"  {'job':<3} | {'d':>1} | {'p':>3} | {'slots examined':<22} | {'decision':<27} | "
          f"{'slots [1..m]':<12} | {'total':>5}")
    print("  " + "-" * 92)
    for row in trace:
        print("  {:<3} | {:>1} | {:>3} | {:<22} | {:<27} | {:<12} | {:>5}".format(*row))
    print("  " + "-" * 92)
    schedule = [f"t{t}={slot[t]}" for t in range(1, len(slot)) if slot[t]]
    print(f"  final schedule: {', '.join(schedule)}   rejected: {', '.join(rejected) or '-'}"
          f"   TOTAL PROFIT = {total}\n")
    return slot, total


def main():
    jobs = read_jobs(os.path.join(HERE, "jobs.csv"))
    print("=" * 96)
    print("TASK 2 - Job Sequencing with Deadlines (greedy: max profit first, latest free slot)  - verification")
    print("=" * 96)
    print_run("Task 2.4 - desk-check instance", jobs)
    modified = [(j, d, 90 if j == "B" else p) for j, d, p in jobs]
    print_run("Task 2.5 - modified instance: profit of B changed 35 -> 90", modified)


if __name__ == "__main__":
    main()
