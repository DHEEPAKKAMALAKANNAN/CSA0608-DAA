"""
Task 4 - Smart manufacturing: Assembly Line Scheduling by Dynamic Programming (two parallel lines).

Input (stations numbered 1..n):
    a[i][j]  processing time of station j on line i (i = 1, 2)
    t[i][j]  transfer time to move the product from line i, after station j, to the OTHER line (j = 1..n-1)
    e[i]     entry time onto line i;  x[i] exit time from line i
DP state:  f[i][j] = fastest time to leave station j on line i (product entered at the start).
    f[1][1] = e[1] + a[1][1]                f[2][1] = e[2] + a[2][1]
    f[1][j] = min( f[1][j-1] + a[1][j]                    (stay on line 1),
                   f[2][j-1] + t[2][j-1] + a[1][j] )      (transfer from line 2)
    f[2][j] = min( f[2][j-1] + a[2][j],  f[1][j-1] + t[1][j-1] + a[2][j] )
    f*      = min( f[1][n] + x[1],  f[2][n] + x[2] )
    pred[i][j] = line used at station j-1 on the fastest way to (i, j)  ->  route reconstruction backwards.
Work Theta(n) (2 comparisons per station + 1 at the exit), memory Theta(n) for pred (f could be 2 variables).

Only algorithm logic lives here (no printing): validation, the DP with a per-station decision trace, route
reconstruction (stations, transfer points), a route-cost recomputation and an exhaustive 2^n reference.
"""
from collections import namedtuple
from itertools import product

Decision = namedtuple("Decision", "station stay1 transfer1 choice1 f1 stay2 transfer2 choice2 f2")
Schedule = namedtuple("Schedule", "min_time route transfers final_line f pred trace exit_costs")


class ProblemInstance:
    """Two-line assembly problem; lists are 0-based internally but stations are reported 1..n."""

    def __init__(self, a1, a2, t1, t2, e1, e2, x1, x2, name=""):
        self.a = (list(a1), list(a2))
        self.t = (list(t1), list(t2))          # t[0][j]: line 1 -> line 2 after station j+1
        self.e = (e1, e2)
        self.x = (x1, x2)
        self.name = name
        self.validate()

    @property
    def n(self):
        return len(self.a[0])

    def validate(self):
        n = len(self.a[0])
        if n < 1:
            raise ValueError("there must be at least one station per line")
        if len(self.a[1]) != n:
            raise ValueError(f"line 1 has {n} stations but line 2 has {len(self.a[1])}")
        for line in (0, 1):
            if len(self.t[line]) != n - 1:
                raise ValueError(f"line {line + 1} needs {n - 1} transfer times, got {len(self.t[line])}")
        values = self.a[0] + self.a[1] + self.t[0] + self.t[1] + list(self.e) + list(self.x)
        for v in values:
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
                raise ValueError(f"all times must be non-negative numbers, got {v!r}")

    def copy_with(self, **changes):
        """A modified copy, e.g. copy_with(a2={3: 15}) or copy_with(t1={2: 12}) - keys are 1-based stations."""
        a = [list(self.a[0]), list(self.a[1])]
        t = [list(self.t[0]), list(self.t[1])]
        for key, edits in changes.items():
            target = {"a1": a[0], "a2": a[1], "t1": t[0], "t2": t[1]}[key]
            for station, value in edits.items():
                target[station - 1] = value
        return ProblemInstance(a[0], a[1], t[0], t[1], *self.e, *self.x, name=self.name)


def schedule(inst):
    """Run the DP. Returns a Schedule with the minimum time, the route [(station, line)], transfer points
    [(after_station, from_line, to_line, transfer_time)], f, pred and the per-station decision trace."""
    inst.validate()
    n, a, t, e, x = inst.n, inst.a, inst.t, inst.e, inst.x
    f = [[0] * n, [0] * n]
    pred = [[None] * n, [None] * n]
    f[0][0], f[1][0] = e[0] + a[0][0], e[1] + a[1][0]
    trace = [Decision(1, e[0] + a[0][0], None, "entry", f[0][0], e[1] + a[1][0], None, "entry", f[1][0])]
    for j in range(1, n):
        options = []
        for line in (0, 1):
            other = 1 - line
            stay = f[line][j - 1] + a[line][j]
            transfer = f[other][j - 1] + t[other][j - 1] + a[line][j]
            if stay <= transfer:                     # ties: prefer staying (no needless transfer)
                f[line][j], pred[line][j], choice = stay, line, "stay"
            else:
                f[line][j], pred[line][j], choice = transfer, other, "transfer"
            options.append((stay, transfer, choice))
        trace.append(Decision(j + 1, options[0][0], options[0][1], options[0][2], f[0][j],
                              options[1][0], options[1][1], options[1][2], f[1][j]))
    exit_costs = (f[0][n - 1] + x[0], f[1][n - 1] + x[1])
    final_line = 0 if exit_costs[0] <= exit_costs[1] else 1
    route = reconstruct(pred, final_line, n)
    transfers = [(route[k][0], route[k][1], route[k + 1][1], t[route[k][1] - 1][route[k][0] - 1])
                 for k in range(n - 1) if route[k][1] != route[k + 1][1]]
    return Schedule(exit_costs[final_line], route, transfers, final_line + 1, f, pred, trace, exit_costs)


def reconstruct(pred, final_line, n):
    """Walk pred backwards from the exit; returns [(station, line)] with 1-based station and line numbers."""
    line, route = final_line, []
    for j in range(n - 1, -1, -1):
        route.append((j + 1, line + 1))
        if j > 0:
            line = pred[line][j]
    return route[::-1]


def route_time(inst, lines):
    """Recompute the total time of a route given as the line (1 or 2) used at every station."""
    a, t, e, x = inst.a, inst.t, inst.e, inst.x
    total = e[lines[0] - 1]
    for j, line in enumerate(lines):
        if j > 0 and lines[j - 1] != line:
            total += t[lines[j - 1] - 1][j - 1]
        total += a[line - 1][j]
    return total + x[lines[-1] - 1]


def exhaustive_min_time(inst):
    """Independent reference: try all 2^n line sequences (n <= 20). Returns (min time, best line sequence)."""
    if inst.n > 20:
        raise ValueError("exhaustive reference limited to n <= 20 stations")
    best = None
    for lines in product((1, 2), repeat=inst.n):
        cost = route_time(inst, lines)
        if best is None or cost < best[0]:
            best = (cost, list(lines))
    return best
