"""
Task 6 checker for run_all_tests.py - Held-Karp TSP (../Source_Code/Task_6/tsp_held_karp.py).

run_case(case) -> (expected, actual, ok).  Every optimum is confirmed independently: by the exhaustive
enumeration of all n! routes, by re-adding the legs of the returned route, or by a closed-form state count.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(HERE, "..", "Source_Code", "Task_6")
sys.path.insert(0, TASK_DIR)

import tsp_held_karp as hk  # noqa: E402


def load(name):
    return hk.load_cost_matrix(os.path.join(TASK_DIR, "test_data", name))


def fmt(c):
    return "inf" if c == hk.INF else c


def check_dp(cost):
    """DP result, exhaustive result and whether they agree (cost, route optimal, legs re-added)."""
    dp = hk.held_karp(cost)
    best, routes, tried = hk.exhaustive_tsp(cost)
    if dp.route is None:
        return dp, best, tried, best == hk.INF
    ok = (dp.cost == best and dp.route in routes and hk.tour_cost(cost, dp.route) == dp.cost
          and hk.is_valid_tour(dp.route, len(cost) - 1))
    return dp, best, tried, ok


def run_case(case):
    ty, ex = case["type"], case["expect"]
    if ty == "invalid":
        try:
            hk.held_karp(case["matrix"])
            return ex["error"], "accepted (no error)", False
        except hk.InvalidCostMatrix as exc:
            return ex["error"], f"InvalidCostMatrix: {exc}", True
    if ty == "file_cost":
        _, cost = load(case["file"])
        dp, best, _, ok = check_dp(cost)
        return ex["cost"], f"DP {fmt(dp.cost)}, exhaustive {fmt(best)}", ok and str(fmt(dp.cost)) == str(ex["cost"])
    if ty == "file_route":
        names, cost = load(case["file"])
        dp = hk.held_karp(cost)
        route = [names[v] for v in dp.route]
        ok = (route in ex["route_one_of"] and hk.is_valid_tour(dp.route, len(names) - 1)
              and hk.tour_cost(cost, dp.route) == dp.cost)
        return ex["route_one_of"][0], "-".join(route) + f" = {hk.tour_cost(cost, dp.route)}", ok
    if ty == "file_vs_exhaustive":
        _, cost = load(case["file"])
        dp, best, tried, ok = check_dp(cost)
        return ex, f"DP {dp.cost} = exh. {best} ({tried} routes)", ok and dp.cost == ex["cost"] and tried == ex["routes"]
    if ty == "random_vs_exhaustive":
        rng, good, total = random.Random(case["seed"]), 0, 0
        for n in case["n_values"]:
            for _ in range(case["trials"]):
                good += check_dp(hk.random_cost_matrix(n, rng, case["symmetric"]))[3]
                total += 1
        return ex, f"{good}/{total} instances agree", good == total
    if ty == "state_count":
        rng, bad = random.Random(0), []
        for n in case["n_values"]:
            r = hk.held_karp(hk.random_cost_matrix(n, rng))
            if (r.states, r.transitions) != (hk.predicted_states(n), hk.predicted_transitions(n)):
                bad.append(n)
        return ex, f"formula holds for n={case['n_values']}" if not bad else f"mismatch at {bad}", not bad
    if ty == "relabel":
        names, cost = load(case["file"])
        perm = [0] + case["permutation"]                  # new index i <- old location perm[i]
        relabelled = [[cost[perm[i]][perm[j]] for j in range(len(perm))] for i in range(len(perm))]
        dp, best, _, ok = check_dp(relabelled)
        return ex["cost"], f"relabelled DP {dp.cost}, exhaustive {best}", ok and dp.cost == ex["cost"]
    if ty == "matrix":
        dp, best, _, ok = check_dp(case["matrix"])
        ok = ok and dp.cost == ex["cost"] and ("route" not in ex or dp.route == ex["route"])
        return ex, f"cost {dp.cost}, route {dp.route}", ok
    if ty == "add_location":
        _, cost = load(case["file"])
        new = case["new_costs"]                           # symmetric costs of G to Hub, A..F
        grown = [row + [new[i]] for i, row in enumerate(cost)] + [new + [0]]
        dp, best, tried, ok = check_dp(grown)
        return ex, f"{dp.states} states, DP {dp.cost} = exh. {best} ({tried})", ok and dp.states == ex["states"]
    raise ValueError(f"unknown case type {ty}")
