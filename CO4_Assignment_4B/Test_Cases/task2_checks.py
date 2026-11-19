"""Checker for Task 2 (greedy vs DP knapsack): run_case(case) -> (expected, actual, ok)."""
import json
import os
import random
import sys
from fractions import Fraction

TASK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Source_Code", "Task_2")
sys.path.insert(0, TASK)
import knapsack_engines as ks  # noqa: E402


def load(name):
    with open(os.path.join(TASK, "test_data", name), encoding="utf-8") as f:
        spec = json.load(f)
    return [ks.Item(*r) for r in spec["items"]], spec["capacity"]


def items_of(rows):
    return [ks.Item(*r) for r in rows]


def random_items(rng, n):
    return [ks.Item(f"I{k}", rng.randint(1, 30), rng.randint(1, 60)) for k in range(n)]


def run_case(case):
    ex, kind = case["expect"], case["type"]
    if kind == "error":
        try:
            ks.knapsack_01_dp(items_of(case["items"]), case["capacity"])
            return ex["error"], "no error", False
        except ValueError as exc:
            return ex["error"], type(exc).__name__, type(exc).__name__ == ex["error"]
    if kind == "fractional_file":
        items, cap = load(case["file"])
        value, plan, _ = ks.fractional_greedy(items, cap)
        units = [ks.Item(f"{it.item_id}.{u}", 1, Fraction(it.value, it.weight)) for it in items for u in range(it.weight)]
        ref = ks.knapsack_01_dp(units, cap)[0]
        load_kg = sum(f * it.weight for it, f in plan)
        return ex, f"greedy {value}, reference {ref}", value == ref == ex["value"] and load_kg <= cap
    if kind == "dp_file":
        items, cap = load(case["file"])
        value, chosen, _ = ks.knapsack_01_dp(items, cap)
        ids = [i.item_id for i in chosen]
        ok = value == ex["value"] == ks.knapsack_01_bruteforce(items, cap) and ids == ex["items"]
        return ex, f"{value} {ids}", ok
    if kind == "counterexample":
        items, cap = load(case["file"])
        g = ks.greedy_01_ratio(items, cap)[0]
        d = ks.knapsack_01_dp(items, cap)[0]
        return ex, f"greedy {g}, DP {d}", (g, d) == (ex["greedy"], ex["dp"]) and g != d
    if kind == "blocking":
        items, cap = load(case["file"])
        _, rows, step = ks.first_blocking_commitment(items, cap)
        return ex, f"step {step} = {rows[step - 1][1].item_id}", step == ex["step"] and rows[step - 1][1].item_id == ex["item"]
    rng = random.Random(case.get("seed", 0))
    if kind == "random_dp_vs_brute":
        bad = 0
        for _ in range(case["trials"]):
            items = random_items(rng, case["n"])
            cap = rng.randint(0, 120)
            value, chosen, _ = ks.knapsack_01_dp(items, cap)
            bad += not (value == ks.knapsack_01_bruteforce(items, cap) == sum(i.value for i in chosen)
                        and sum(i.weight for i in chosen) <= cap)
        return ex, f"{case['trials'] - bad}/{case['trials']} ok", bad == 0
    if kind == "random_fractional_bound":
        bad = 0
        for _ in range(case["trials"]):
            items = random_items(rng, case["n"])
            cap = rng.randint(1, 120)
            frac = ks.fractional_greedy(items, cap)[0]
            opt = ks.knapsack_01_dp(items, cap)[0]
            g = ks.greedy_01_ratio(items, cap)[0]
            b = ks.greedy_01_best_of_two(items, cap)[0]
            bad += not (frac >= opt >= b >= g and 2 * b >= opt)
        return ex, f"{case['trials'] - bad}/{case['trials']} ok", bad == 0
    if kind == "random_1d":
        bad = 0
        for _ in range(case["trials"]):
            items = random_items(rng, case["n"])
            cap = rng.randint(0, 150)
            bad += ks.knapsack_01_value_1d(items, cap) != ks.knapsack_01_dp(items, cap)[0]
        return ex, f"{case['trials'] - bad}/{case['trials']} ok", bad == 0
    if kind == "adversarial":
        items = [ks.Item("tiny", 1, 2), ks.Item("big", 1000, 1000)]
        g, b = ks.greedy_01_ratio(items, 1000)[0], ks.greedy_01_best_of_two(items, 1000)[0]
        return ex, f"greedy {g}, best-of-two {b}", (g, b) == (ex["greedy"], ex["best_of_two"])
    if kind == "values":
        items, cap = items_of(case["items"]), case["capacity"]
        frac = ks.fractional_greedy(items, cap)[0]
        dp = ks.knapsack_01_dp(items, cap)[0]
        return ex, f"fractional {frac}, DP {dp}", frac == ex["fractional"] and dp == ex["dp"]
    raise ValueError(kind)
