# Exercise 72 - Maximum Profit in Job Scheduling (DP + binary search)
from bisect import bisect_right


def max_profit(start, end, profit):
    jobs = sorted(zip(start, end, profit), key=lambda j: j[1])   # by end time
    ends = [j[1] for j in jobs]
    dp = [0] * (len(jobs) + 1)          # dp[i] = best profit using first i jobs
    prev = [0] * (len(jobs) + 1)        # prev[i] = # of jobs ending <= start of job i
    for i, (s, e, p) in enumerate(jobs, 1):
        prev[i] = bisect_right(ends, s, 0, i - 1)    # a job ending at s may precede
        dp[i] = max(dp[i - 1], dp[prev[i]] + p)      # skip job i  or  take job i
    chosen, i = [], len(jobs)           # walk back to recover the chosen jobs
    while i > 0:
        if dp[i] != dp[i - 1]:
            chosen.append(jobs[i - 1])
            i = prev[i]
        else:
            i -= 1
    return dp[-1], chosen[::-1]


if __name__ == "__main__":
    tests = [
        ([1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70], 120),
        ([1, 2, 3, 4, 6], [3, 5, 10, 6, 9], [20, 20, 100, 70, 60], 150),
    ]
    for no, (s, e, p, expected) in enumerate(tests, 1):
        best, chosen = max_profit(s, e, p)
        print(f"Test Case {no}")
        print(f"Input   : startTime = {s}, endTime = {e}, profit = {p}")
        for js, je, jp in chosen:
            print(f"  job [{js}-{je}] profit {jp}")
        print(f"Output  : {best} = " + " + ".join(str(j[2]) for j in chosen))
        print(f"Expected: {expected}")
        print()
    print("Time complexity : O(n log n) (sort + binary search per job); Space: O(n)")
