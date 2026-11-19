"""
Task 6.4 - Validate the Held-Karp DP against an independent exhaustive enumeration.

Part 1: hub + 4 delivery locations (test_data/validation_hub4.csv) - every one of the 4! = 24 routes is listed with
        its cost (computed leg by leg, no DP involved), the minimum is marked and compared with the DP result.
Part 2: extra evidence - DP vs exhaustive on seeded random instances, n = 1..8, symmetric and asymmetric costs.
Writes results/t6_validation_hub4_routes.csv and results/t6_random_agreement.csv.
Run:  py -3 tsp_validate.py
"""
import csv
import os
import random
import time

import tsp_held_karp as hk

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")


def route_text(route, names):
    return " -> ".join(names[v] for v in route)


def main():
    names, cost = hk.load_cost_matrix(os.path.join(HERE, "test_data", "validation_hub4.csv"))
    n = len(names) - 1
    print("TASK 6.4 - VALIDATION: HELD-KARP DP vs EXHAUSTIVE ENUMERATION")
    print("=" * 96)
    print("TEST INPUT  test_data/validation_hub4.csv (hub + 4 locations, minutes)")
    print("    from\\to " + "".join(f"{nm:>6}" for nm in names))
    for nm, row in zip(names, cost):
        print(f"    {nm:<8}" + "".join(f"{c:>6}" for c in row))
    print("PREDICTION (recorded before running): 4! = 24 routes; because the costs are symmetric every tour "
          "appears twice\n    (once per direction), so the minimum must occur at least twice and DP must "
          "return one of those routes.")

    print(f"\nPart 1 - all {n}! routes, each cost re-added leg by leg")
    print(f"    {'#':>3}  {'route':<38} {'legs':<22} {'cost':>5}")
    rows, best = [], min(c for _, c in hk.all_routes(cost))
    for i, (route, c) in enumerate(hk.all_routes(cost), 1):
        legs = "+".join(str(cost[a][b]) for a, b in zip(route, route[1:]))
        mark = "  <-- minimum" if c == best else ""
        print(f"    {i:>3}  {route_text(route, names):<38} {legs:<22} {c:>5}{mark}")
        rows.append([i, route_text(route, names), legs, c, c == best])
    with open(os.path.join(RESULTS, "t6_validation_hub4_routes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["route_no", "route", "legs", "cost", "is_minimum"])
        w.writerows(rows)
    dp = hk.held_karp(cost)
    ex_best, ex_routes, tried = hk.exhaustive_tsp(cost)
    print(f"\n    Exhaustive reference : minimum {ex_best} over {tried} routes, reached by {len(ex_routes)} routes")
    print(f"    Held-Karp DP         : cost {dp.cost}, route {route_text(dp.route, names)}  "
          f"({dp.states} states, {dp.transitions} transitions)")
    print(f"    Comparison           : costs equal = {dp.cost == ex_best};  DP route among the optimal routes = "
          f"{dp.route in ex_routes};  DP route cost re-added = {hk.tour_cost(cost, dp.route)}")

    print("\nPart 2 - random instances (seed 2026): DP cost must equal the exhaustive optimum every time")
    print(f"    {'n':>2} {'costs':<10} {'instances':>9} {'DP = exhaustive':>16} {'DP transitions':>15} "
          f"{'routes n!':>10} {'DP ms (avg)':>12} {'exh. ms (avg)':>14}")
    rng, agree_rows, all_ok = random.Random(2026), [], True
    for n_loc in range(1, 9):
        for symmetric in (True, False):
            trials = 30 if n_loc <= 6 else (8 if n_loc == 7 else 3)
            ok, t_dp, t_ex, trans = 0, 0.0, 0.0, 0
            for _ in range(trials):
                m = hk.random_cost_matrix(n_loc, rng, symmetric)
                t0 = time.perf_counter()
                r = hk.held_karp(m)
                t1 = time.perf_counter()
                e, routes, _ = hk.exhaustive_tsp(m)
                t2 = time.perf_counter()
                ok += (r.cost == e and r.route in routes and hk.tour_cost(m, r.route) == r.cost)
                t_dp, t_ex, trans = t_dp + t1 - t0, t_ex + t2 - t1, r.transitions
            all_ok &= ok == trials
            kind = "symmetric" if symmetric else "asymmetric"
            fact = 1
            for k in range(2, n_loc + 1):
                fact *= k
            print(f"    {n_loc:>2} {kind:<10} {trials:>9} {f'{ok}/{trials}':>16} {trans:>15} {fact:>10} "
                  f"{1000 * t_dp / trials:>12.3f} {1000 * t_ex / trials:>14.3f}")
            agree_rows.append([n_loc, kind, trials, ok, trans, fact, round(1000 * t_dp / trials, 4),
                               round(1000 * t_ex / trials, 4)])
    with open(os.path.join(RESULTS, "t6_random_agreement.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n_locations", "costs", "instances", "dp_equals_exhaustive", "dp_transitions", "routes_n_fact",
                    "dp_ms_avg", "exhaustive_ms_avg"])
        w.writerows(agree_rows)
    print(f"\n    All random instances agree: {all_ok}")


if __name__ == "__main__":
    main()
