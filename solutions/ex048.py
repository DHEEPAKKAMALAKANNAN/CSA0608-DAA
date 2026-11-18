# Exercise 48 - Assembly Line Scheduling (two lines, dynamic programming)
# The exercise gives no numbers, so two standard textbook instances are used as test cases.
# t1[i] = transfer time line 1 -> line 2 after station i, t2[i] = line 2 -> line 1 after station i.


def assembly_line_schedule(a1, a2, t1, t2, e1, e2, x1, x2):
    """Return (minimum total time, list of line numbers used at each station)."""
    n = len(a1)
    f1, f2 = [e1 + a1[0]], [e2 + a2[0]]          # best time to finish station i on line 1 / line 2
    from1, from2 = [0], [0]                      # line used at station i-1 (for path rebuilding)
    for i in range(1, n):
        stay1, switch1 = f1[i - 1] + a1[i], f2[i - 1] + t2[i - 1] + a1[i]
        stay2, switch2 = f2[i - 1] + a2[i], f1[i - 1] + t1[i - 1] + a2[i]
        f1.append(min(stay1, switch1))
        from1.append(1 if stay1 <= switch1 else 2)
        f2.append(min(stay2, switch2))
        from2.append(2 if stay2 <= switch2 else 1)
    end1, end2 = f1[-1] + x1, f2[-1] + x2
    line, best = (1, end1) if end1 <= end2 else (2, end2)
    path = [line]
    for i in range(n - 1, 0, -1):                # walk back through the choices
        line = from1[i] if line == 1 else from2[i]
        path.append(line)
    return best, path[::-1], f1, f2


def run_case(number, a1, a2, t1, t2, e1, e2, x1, x2, expected):
    best, path, f1, f2 = assembly_line_schedule(a1, a2, t1, t2, e1, e2, x1, x2)
    print(f"Test Case {number}")
    print(f"Input   : n = {len(a1)}, a1 = {a1}, a2 = {a2}")
    print(f"          t1 = {t1}, t2 = {t2}, e1 = {e1}, e2 = {e2}, x1 = {x1}, x2 = {x2}")
    print(f"DP      : f1 = {f1}")
    print(f"          f2 = {f2}")
    print(f"Output  : minimum time = {best}")
    print(f"Path    : line used at stations 1..n = {path}")
    print(f"Expected: {expected}")
    print()


if __name__ == "__main__":
    run_case(1, [7, 9, 3, 4, 8, 4], [8, 5, 6, 4, 5, 7], [2, 3, 1, 3, 4], [2, 1, 2, 2, 1],
             2, 4, 3, 2, 38)
    run_case(2, [4, 5, 3, 2], [2, 10, 1, 4], [7, 4, 5], [9, 2, 8], 10, 12, 18, 7, 35)
    print("Time: O(n) (each station needs two comparisons), space: O(n) (O(1) without the path).")
