# Exercise 49 - Scheduling on three assembly lines with transfer times and dependencies
# Assumption: the dependency chain (0->1->2) means station j can only start after station j-1 has
# finished, so the stations are processed in order; no entry/exit times are given (taken as 0).


def schedule_three_lines(station_times, transfer, dependencies):
    """Dynamic programming over (station, line). Returns (min total time, line per station, table)."""
    lines, n = len(station_times), len(station_times[0])
    for before, after in dependencies:           # the dependencies must form the chain 0->1->...->n-1
        assert after == before + 1, "only sequential dependencies are supported"
    finish = [[station_times[l][0] for l in range(lines)]]      # finish[j][l]
    came_from = [[None] * lines]
    for j in range(1, n):
        row, back = [], []
        for l in range(lines):
            # previous station on line p, then move from p to l (transfer[p][l] is 0 when p == l)
            cost, prev = min((finish[j - 1][p] + transfer[p][l], p) for p in range(lines))
            row.append(cost + station_times[l][j])
            back.append(prev)
        finish.append(row)
        came_from.append(back)
    total, line = min((finish[-1][l], l) for l in range(lines))
    path = [line]
    for j in range(n - 1, 0, -1):
        line = came_from[j][line]
        path.append(line)
    return total, path[::-1], finish


if __name__ == "__main__":
    times = [[5, 9, 3], [6, 8, 4], [7, 6, 5]]
    transfer = [[0, 2, 3], [2, 0, 4], [3, 4, 0]]
    deps = [(0, 1), (1, 2)]
    total, path, finish = schedule_three_lines(times, transfer, deps)
    print("Test Case 1")
    print("Input   : stations = 3")
    for l, row in enumerate(times, 1):
        print(f"          Line {l}: {row}")
    print(f"          transfer times = {transfer}, dependencies = {deps}")
    print("DP table (earliest finish time of each station on each line):")
    for l in range(3):
        print(f"          Line {l + 1}: {[finish[j][l] for j in range(3)]}")
    print(f"Output  : minimum total production time = {total}")
    print("Schedule: " + " -> ".join(f"Station {j + 1} on Line {l + 1}" for j, l in enumerate(path)))
    spent = sum(times[l][j] for j, l in enumerate(path))
    moves = sum(transfer[path[j]][path[j + 1]] for j in range(2))
    print(f"Check   : processing {spent} + transfers {moves} = {spent + moves}")
    print()
    print("Time: O(n * k^2) for n stations and k lines (here 3*3*3), space: O(n * k).")
