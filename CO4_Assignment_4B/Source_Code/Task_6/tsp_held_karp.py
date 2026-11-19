r"""
Task 6 - Last-mile delivery route optimisation: Travelling Salesperson Problem by Dynamic Programming.

Model. Vertex 0 is the distribution HUB, vertices 1..n are the delivery locations. cost[i][j] >= 0 is the travel
cost from i to j (asymmetric costs allowed, float('inf') = no direct road). A tour starts at the hub, visits every
location exactly once and returns to the hub; we want the tour of minimum total cost.

Held-Karp DP. S is a set of delivery locations (bit j-1 of a bitmask <=> location j in S), j in S is the current
location.
    DP[S][j] = minimum cost of a path that starts at the hub, visits exactly the locations of S, and ends at j.
    base      DP[{j}][j] = cost[hub][j]
    recurrence DP[S][j] = min over k in S \ {j} of  DP[S \ {j}][k] + cost[k][j]
    answer    OPT = min over j of DP[ALL][j] + cost[j][hub]          (the return to the hub)
PARENT[S][j] stores the minimising k, so the route is rebuilt backwards from the best last location.
States: n * 2^(n-1);  transitions examined: n(n-1) * 2^(n-2) (+ n final);  time Theta(n^2 2^n), memory Theta(n 2^n).

The algorithm functions do no printing (separation of logic and I/O); the drivers tsp_route_engine.py,
tsp_validate.py and tsp_state_growth.py produce the evidence.  exhaustive_tsp() is the independent reference
(all n! visiting orders).
"""
import csv
import itertools
import math
import time
import tracemalloc
from collections import Counter, namedtuple

INF = float("inf")
HUB = 0
TourResult = namedtuple("TourResult", "cost route states transitions")


class InvalidCostMatrix(ValueError):
    """Raised when the cost matrix cannot describe a delivery network."""


# ----------------------------------------------------------------------------- model + validation
def validate_cost_matrix(cost, names=None):
    """Check that cost is a square (n+1)x(n+1) matrix with n >= 1, zero diagonal and non-negative entries
    (inf allowed off the diagonal = no road).  Raises InvalidCostMatrix with a precise message."""
    if not isinstance(cost, (list, tuple)) or len(cost) < 2:
        raise InvalidCostMatrix("need the hub and at least 1 delivery location (matrix of size >= 2)")
    size = len(cost)
    for i, row in enumerate(cost):
        if len(row) != size:
            raise InvalidCostMatrix(f"matrix is not square: row {i} has {len(row)} entries, expected {size}")
        for j, c in enumerate(row):
            if not isinstance(c, (int, float)) or isinstance(c, bool) or c != c:     # c != c  <=> NaN
                raise InvalidCostMatrix(f"cost[{i}][{j}] = {c!r} is not a number")
            if c < 0:
                raise InvalidCostMatrix(f"cost[{i}][{j}] = {c} is negative (travel cost must be >= 0)")
            if i == j and c != 0:
                raise InvalidCostMatrix(f"cost[{i}][{i}] = {c}: diagonal must be 0")
    if names is not None and len(names) != size:
        raise InvalidCostMatrix(f"{len(names)} names for a {size}x{size} matrix")


def load_cost_matrix(path):
    """CSV with a header row 'from,<name0>,<name1>,...' and one row per location; '' or 'inf' = no road.
    The first location is the hub.  Returns (names, cost)."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    names = rows[0][1:]
    cost = [[INF if cell.strip().lower() in ("", "inf") else float(cell) for cell in r[1:]] for r in rows[1:]]
    cost = [[int(c) if c != INF and c == int(c) else c for c in row] for row in cost]
    validate_cost_matrix(cost, names)
    return names, cost


def tour_cost(cost, route):
    """Total cost of a route given as a vertex list starting and ending at the hub (independent re-check)."""
    return sum(cost[a][b] for a, b in zip(route, route[1:]))


def is_valid_tour(route, n_locations):
    """True if route = [hub, every location 1..n exactly once, hub]."""
    return (len(route) == n_locations + 2 and route[0] == HUB and route[-1] == HUB
            and sorted(route[1:-1]) == list(range(1, n_locations + 1)))


def members(mask, n):
    """Locations (1-based) contained in the bitmask."""
    return [j + 1 for j in range(n) if mask >> j & 1]


# ----------------------------------------------------------------------------- Held-Karp DP
def held_karp(cost, ops=None, trace=None):
    """Exact minimum-cost tour by Held-Karp DP.
    ops   : Counter receiving 'states' (DP[S][j] entries evaluated) and 'transitions' (k candidates examined)
    trace : optional list receiving (mask, j, value, best_k) for every state, in evaluation order
    Returns TourResult(cost, route or None if no feasible tour, states, transitions)."""
    validate_cost_matrix(cost)
    ops = Counter() if ops is None else ops
    n = len(cost) - 1
    full = (1 << n) - 1
    dp = [[INF] * (n + 1) for _ in range(1 << n)]          # dp[mask][j], j = 1..n (column 0 unused)
    parent = [[-1] * (n + 1) for _ in range(1 << n)]
    for j in range(1, n + 1):                               # base states: hub -> j directly
        mask = 1 << (j - 1)
        dp[mask][j] = cost[HUB][j]
        parent[mask][j] = HUB
        ops["states"] += 1
        if trace is not None:
            trace.append((mask, j, dp[mask][j], HUB))
    for mask in range(1, full + 1):                         # increasing masks => every subset before superset
        if mask & (mask - 1) == 0:                          # single-location sets are the base case
            continue
        for j in range(1, n + 1):
            bit = 1 << (j - 1)
            if not mask & bit:
                continue
            prev_mask, best, best_k = mask ^ bit, INF, -1
            prev_row = dp[prev_mask]
            for k in range(1, n + 1):
                if prev_mask >> (k - 1) & 1:
                    ops["transitions"] += 1
                    candidate = prev_row[k] + cost[k][j]
                    if candidate < best:
                        best, best_k = candidate, k
            dp[mask][j], parent[mask][j] = best, best_k
            ops["states"] += 1
            if trace is not None:
                trace.append((mask, j, best, best_k))
    best, last = INF, -1                                    # close the tour: return to the hub
    for j in range(1, n + 1):
        ops["transitions"] += 1
        if dp[full][j] + cost[j][HUB] < best:
            best, last = dp[full][j] + cost[j][HUB], j
    if best == INF:
        return TourResult(INF, None, ops["states"], ops["transitions"])
    route, mask, j = [HUB], full, last                      # reconstruct backwards via PARENT
    while j != HUB:
        route.append(j)
        mask, j = mask ^ (1 << (j - 1)), parent[mask][j]
    route.append(HUB)
    route.reverse()
    return TourResult(best, route, ops["states"], ops["transitions"])


def predicted_states(n):
    """Number of DP[S][j] entries: each of the n locations j is the end of 2^(n-1) subsets containing it."""
    return n * 2 ** (n - 1)


def predicted_transitions(n):
    """k-candidates examined: sum over |S| = s of C(n,s) s (s-1) = n(n-1) 2^(n-2), plus n closing edges."""
    return (n * (n - 1) * 2 ** (n - 2) if n >= 2 else 0) + n


# ----------------------------------------------------------------------------- exhaustive reference
def all_routes(cost):
    """Yield (route, cost) for every one of the n! visiting orders (hub fixed at both ends)."""
    n = len(cost) - 1
    for order in itertools.permutations(range(1, n + 1)):
        route = (HUB,) + order + (HUB,)
        yield list(route), tour_cost(cost, route)


def exhaustive_tsp(cost):
    """Independent reference: try all n! routes. Returns (best cost, list of all optimal routes, routes tried)."""
    validate_cost_matrix(cost)
    best, optimal, tried = INF, [], 0
    for route, c in all_routes(cost):
        tried += 1
        if c < best:
            best, optimal = c, [route]
        elif c == best and c != INF:
            optimal.append(route)
    return best, (optimal if best != INF else []), tried


# ----------------------------------------------------------------------------- measurement helpers
def measure_held_karp(cost, repeats=1):
    """Run held_karp `repeats` times (minimum wall time = least disturbed run) and once under tracemalloc.
    Returns dict(cost, route, states, transitions, time_s, peak_bytes, table_cells)."""
    times, result = [], None
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = held_karp(cost)
        times.append(time.perf_counter() - t0)
    tracemalloc.start()
    held_karp(cost)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    n = len(cost) - 1
    times.sort()
    return dict(cost=result.cost, route=result.route, states=result.states, transitions=result.transitions,
                time_s=times[0], peak_bytes=peak, table_cells=2 * (1 << n) * (n + 1))


def random_cost_matrix(n, rng, symmetric=True, low=1, high=99):
    """Random integer cost matrix for the hub + n locations (seeded rng supplied by the caller)."""
    size = n + 1
    cost = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if i == j:
                continue
            if symmetric and j < i:
                cost[i][j] = cost[j][i]
            else:
                cost[i][j] = rng.randint(low, high)
    return cost


def euclid(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])
