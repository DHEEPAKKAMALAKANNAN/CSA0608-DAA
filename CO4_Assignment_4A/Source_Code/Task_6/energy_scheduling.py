"""
energy_scheduling.py - Task 6 (CO4 Assignment 4A): energy-aware job scheduling = weighted interval scheduling.

Jobs (id, start, finish, value); two jobs are compatible when one finishes no later than the other starts
(f <= s, touching endpoints allowed).  Select compatible jobs with maximum total energy-saving value.
Design (report, Stage 4, ALGORITHM EnergyAwareSchedule): SORT by finish time; p(j) = largest i < j with
f_i <= s_j (binary search); OPT[0] = 0, OPT[j] = max(OPT[j-1], v_j + OPT[p(j)]); trace back to report jobs.
Usage:  py energy_scheduling.py [jobs.csv | adversarial_jobs.csv]
The desk-check was done by hand first; this run confirms it and checks it against all 2^n subsets.
"""
import csv
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def read_jobs(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [(r["job"], int(r["start"]), int(r["finish"]), int(r["value"])) for r in csv.DictReader(f)]


def latest_compatible(jobs, j):
    """p(j): largest index i < j (1-based, jobs sorted by finish) with finish_i <= start_j, else 0."""
    lo, hi, ans = 1, j - 1, 0
    s = jobs[j - 1][1]
    while lo <= hi:                                   # binary search over finish times f_1 <= ... <= f_(j-1)
        mid = (lo + hi) // 2
        if jobs[mid - 1][2] <= s:
            ans, lo = mid, mid + 1
        else:
            hi = mid - 1
    return ans


def schedule(jobs):
    """Return (sorted jobs, p, OPT, decisions, selected ids, best value, reconstruction steps)."""
    J = sorted(jobs, key=lambda x: (x[2], x[1], x[0]))     # preprocessing: by finish, then start, then id
    n = len(J)
    p = [0] + [latest_compatible(J, j) for j in range(1, n + 1)]
    OPT = [0] * (n + 1)
    decisions = [None] * (n + 1)
    for j in range(1, n + 1):
        include = J[j - 1][3] + OPT[p[j]]
        exclude = OPT[j - 1]
        if include > exclude:                              # strict: on a tie keep the exclude branch
            OPT[j], decisions[j] = include, "INCLUDE"
        else:
            OPT[j], decisions[j] = exclude, "exclude"
        decisions[j] = (include, exclude, decisions[j])
    selected, steps, j = [], [], n
    while j > 0:                                           # reconstruction
        include, exclude, _ = decisions[j]
        if include > exclude:
            steps.append((j, J[j - 1][0], include, exclude, f"take {J[j - 1][0]}, jump to p({j}) = {p[j]}"))
            selected.append(J[j - 1][0])
            j = p[j]
        else:
            steps.append((j, J[j - 1][0], include, exclude, f"skip {J[j - 1][0]}, go to {j - 1}"))
            j -= 1
    selected.reverse()
    return J, p, OPT, decisions, selected, OPT[n], steps


def compatible(subset):
    s = sorted(subset, key=lambda x: x[1])
    return all(s[k][2] <= s[k + 1][1] for k in range(len(s) - 1))


def brute_force(jobs):
    best, arg, count = 0, (), 0
    for r in range(len(jobs) + 1):
        for sub in itertools.combinations(jobs, r):
            count += 1
            if compatible(sub) and sum(x[3] for x in sub) > best:
                best, arg = sum(x[3] for x in sub), tuple(x[0] for x in sub)
    return best, arg, count


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "jobs.csv"
    jobs = read_jobs(os.path.join(HERE, name))
    J, p, OPT, dec, sel, best, steps = schedule(jobs)
    print("=" * 104)
    print(f"TASK 6 - Energy-aware job scheduling, DP over jobs sorted by finish time   input: {name}")
    print("=" * 104)
    print("input order:", ", ".join(f"{j}[{s},{f})={v}" for j, s, f, v in jobs))
    print("\nPreprocessing: sorted by finish time, p(j) = latest earlier job with finish <= start_j")
    print(f"  {'j':>2} | {'job':<3} | {'start':>5} | {'finish':>6} | {'value':>5} | {'p(j)':>4} | "
          f"{'include = v_j + OPT[p(j)]':<26} | {'exclude = OPT[j-1]':<18} | {'OPT[j]':>6} | decision")
    print("  " + "-" * 100)
    print(f"  {0:>2} | {'-':<3} | {'':>5} | {'':>6} | {'':>5} | {'':>4} | {'base case':<26} | {'':<18} | "
          f"{0:>6} |")
    for j in range(1, len(J) + 1):
        jid, s, f, v = J[j - 1]
        inc, exc, d = dec[j]
        print(f"  {j:>2} | {jid:<3} | {s:>5} | {f:>6} | {v:>5} | {p[j]:>4} | "
              f"{f'{v} + OPT[{p[j]}] = {inc}':<26} | {f'OPT[{j - 1}] = {exc}':<18} | {OPT[j]:>6} | "
              f"{d}{'  (tie)' if inc == exc else ''}")
    print("  " + "-" * 100)
    print("\nReconstruction (start at j = n):")
    for j, jid, inc, exc, action in steps:
        print(f"  j = {j}: include {inc} vs exclude {exc}  ->  {action}")
    chosen = [x for x in J if x[0] in sel]
    print(f"\nSELECTED JOBS: {', '.join(sel)}   intervals: "
          + ", ".join(f"[{s},{f})" for _, s, f, _ in chosen)
          + f"   TOTAL ENERGY-SAVING VALUE = {best}")
    bf, arg, cnt = brute_force(jobs)
    print(f"Brute force over all 2^{len(jobs)} = {cnt} subsets: best {bf} with {', '.join(sorted(arg))}"
          f"  ->  {'MATCH' if bf == best else 'MISMATCH'}")


if __name__ == "__main__":
    main()
