# Exercise 71 - Minimum Possible Maximum Working Time (backtracking + pruning)


def min_max_working_time(jobs, k):
    jobs = sorted(jobs, reverse=True)        # place big jobs first -> prunes early
    load = [0] * k                           # current working time of each worker
    best = [sum(jobs) + 1]                   # smallest maximum found so far
    assign = [[] for _ in range(k)]
    best_assign = [None]

    def place(i):
        if i == len(jobs):
            best[0] = max(load)
            best_assign[0] = [list(a) for a in assign]
            return
        tried = set()
        for w in range(k):
            # skip equal loads (symmetric) and anything that cannot beat `best`
            if load[w] in tried or load[w] + jobs[i] >= best[0]:
                continue
            tried.add(load[w])
            load[w] += jobs[i]
            assign[w].append(jobs[i])
            place(i + 1)
            assign[w].pop()
            load[w] -= jobs[i]

    place(0)
    return best[0], best_assign[0]


if __name__ == "__main__":
    tests = [([3, 2, 3], 3, 3), ([1, 2, 4, 7, 8], 2, 11)]
    for no, (jobs, k, expected) in enumerate(tests, 1):
        answer, assign = min_max_working_time(jobs, k)
        print(f"Test Case {no}")
        print(f"Input   : jobs = {jobs}, k = {k}")
        for w, a in enumerate(assign, 1):
            print(f"  Worker {w}: {sorted(a)} (working time = {sum(a)})")
        print(f"Output  : {answer}")
        print(f"Expected: {expected}")
        print()
    print("Method: backtracking over workers for every job, O(k^n) worst case, pruned")
