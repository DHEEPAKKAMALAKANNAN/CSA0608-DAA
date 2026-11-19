"""
Task 6.3 - Route optimisation engine (driver / I/O layer for tsp_held_karp.py).

Loads the hub + 6 delivery locations (test_data/delivery_costs.csv, travel time in minutes), prints the input
cost matrix and the expected behaviour (state/transition counts predicted BEFORE the run), runs the Held-Karp DP,
then shows the intermediate evidence (how DP[S][j] was built along the optimal route, state counts per subset
size), the optimal route leg by leg, an independent exhaustive cross-check and the boundary / failure tests.
Run:  py -3 tsp_route_engine.py
"""
import os
from collections import Counter, defaultdict

import tsp_held_karp as hk

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "test_data")


def subset_label(mask, n, names):
    return "{" + ",".join(sorted(names[j] for j in hk.members(mask, n))) + "}"


def fmt(c):
    return "inf" if c == hk.INF else f"{c:g}"


def route_text(route, names):
    return " -> ".join(names[v] for v in route)


def print_matrix(names, cost):
    print("    from\\to " + "".join(f"{nm:>6}" for nm in names))
    for nm, row in zip(names, cost):
        print(f"    {nm:<8}" + "".join(f"{fmt(c):>6}" for c in row))


def main():
    names, cost = hk.load_cost_matrix(os.path.join(DATA, "delivery_costs.csv"))
    n = len(names) - 1
    print("TASK 6.3 - LAST-MILE DELIVERY ROUTE OPTIMISATION (Held-Karp dynamic programming)")
    print("=" * 100)
    print(f"TEST INPUT  test_data/delivery_costs.csv - 1 hub + {n} delivery locations, travel time in minutes")
    print_matrix(names, cost)
    print(f"\nEXPECTED BEHAVIOUR (predicted before running)")
    print(f"    DP states n*2^(n-1) = {hk.predicted_states(n)};  transitions n(n-1)*2^(n-2) + n = "
          f"{hk.predicted_transitions(n)};  routes an exhaustive search would try: n! = 720")
    print("    the route must start and end at the Hub and visit A..F exactly once; cost = sum of its legs")

    ops, trace = Counter(), []
    result = hk.held_karp(cost, ops, trace)
    table = {(mask, j): (value, k) for mask, j, value, k in trace}

    print("\nINTERMEDIATE DP EVIDENCE - states built along the optimal route  DP[S][j] = min_k DP[S-{j}][k] + c(k,j)")
    mask = 0
    for step, j in enumerate(result.route[1:-1], 1):
        mask |= 1 << (j - 1)
        value, best_k = table[(mask, j)]
        prev = mask ^ (1 << (j - 1))
        if prev == 0:
            detail = f"base: c(Hub,{names[j]}) = {fmt(value)}"
        else:
            cands = [f"{names[k]}:{fmt(table[(prev, k)][0])}+{fmt(cost[k][j])}={fmt(table[(prev, k)][0] + cost[k][j])}"
                     for k in hk.members(prev, n)]
            detail = "  ".join(cands)
        print(f"    |S|={step} DP[{subset_label(mask, n, names)}][{names[j]}] = {fmt(value):>4} "
              f"(via {names[best_k]})  {detail}"[:124])
    full = (1 << n) - 1
    closes = [f"{names[j]}:{fmt(table[(full, j)][0])}+{fmt(cost[j][0])}={fmt(table[(full, j)][0] + cost[j][0])}"
              for j in range(1, n + 1)]
    print("    return to Hub: min_j DP[ALL][j] + c(j,Hub):  " + "  ".join(closes[:3]))
    print("                                                 " + "  ".join(closes[3:]))

    per_size = defaultdict(list)
    for mask, j, value, _ in trace:
        per_size[bin(mask).count("1")].append(value)
    print(f"\n    {'|S|':>4} {'subsets':>8} {'states DP[S][j]':>16} {'cheapest DP value':>18} {'dearest DP value':>17}")
    for size in sorted(per_size):
        vals = per_size[size]
        print(f"    {size:>4} {len(vals) // size:>8} {len(vals):>16} {fmt(min(vals)):>18} {fmt(max(vals)):>17}")
    print(f"    total states evaluated = {ops['states']} (predicted {hk.predicted_states(n)}), transitions = "
          f"{ops['transitions']} (predicted {hk.predicted_transitions(n)})")

    print("\nACTUAL OUTPUT")
    print(f"    {'leg':>3}  {'from':<5} {'to':<5} {'leg cost':>8} {'cumulative':>10}")
    total = 0
    for leg, (a, b) in enumerate(zip(result.route, result.route[1:]), 1):
        total += cost[a][b]
        print(f"    {leg:>3}  {names[a]:<5} {names[b]:<5} {fmt(cost[a][b]):>8} {fmt(total):>10}")
    print(f"    Visiting order : " + ", ".join(f"{i}.{names[v]}" for i, v in enumerate(result.route[1:-1], 1))
          + "  then return to Hub")
    print(f"    Optimal route  : {route_text(result.route, names)}")
    print(f"    Minimum Travel Cost = {fmt(result.cost)} minutes   (legs re-added independently = "
          f"{fmt(hk.tour_cost(cost, result.route))}, valid tour: {hk.is_valid_tour(result.route, n)})")
    best, optimal, tried = hk.exhaustive_tsp(cost)
    print(f"    Cross-check by exhaustive enumeration of {tried} routes: optimum = {fmt(best)}; optimal routes:")
    for r in optimal:
        print(f"        {route_text(r, names)}")
    print("    (the two optimal routes are the same tour driven in opposite directions - symmetric costs)")

    print("\nBOUNDARY / FAILURE TESTS")
    cases = [("1 delivery location", [[0, 7], [9, 0]]),
             ("2 delivery locations", [[0, 4, 6], [5, 0, 3], [8, 2, 0]])]
    for label, m in cases:
        r = hk.held_karp(m)
        print(f"    {label:<24} -> route {route_text(r.route, ['Hub', '1', '2'])}, cost {fmt(r.cost)}, "
              f"states {r.states}, transitions {r.transitions}")
    u_names, u_cost = hk.load_cost_matrix(os.path.join(DATA, "unreachable_hub3.csv"))
    r = hk.held_karp(u_cost)
    print(f"    {'unreachable C (inf legs)':<24} -> cost {fmt(r.cost)}, route {r.route}: no feasible tour reported "
          f"(exhaustive: {fmt(hk.exhaustive_tsp(u_cost)[0])})")
    bad = [("hub only", [[0]]), ("non-square", [[0, 1, 2], [1, 0]]),
           ("negative cost", [[0, -3], [3, 0]]), ("non-zero diagonal", [[5, 1], [1, 0]]),
           ("non-numeric", [[0, "x"], [1, 0]])]
    for label, m in bad:
        try:
            hk.held_karp(m)
            print(f"    {label:<24} -> ACCEPTED (defect!)")
        except hk.InvalidCostMatrix as exc:
            print(f"    {label:<24} -> rejected: {exc}")


if __name__ == "__main__":
    main()
