"""Checker for Task 4 (assembly line scheduling DP): run_case(case) -> (expected, actual, ok)."""
import os
import random
import sys

TASK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Source_Code", "Task_4")
sys.path.insert(0, TASK)
import assembly_line_dp as al  # noqa: E402
from assembly_line_demo import load_instance  # noqa: E402


def build(case):
    return al.ProblemInstance(case["a1"], case["a2"], case["t1"], case["t2"], *case["e"], *case["x"])


def lines_of(sched):
    return [line for _, line in sched.route]


def random_instance(rng, n):
    r = lambda k: [rng.randint(0, 12) for _ in range(k)]  # noqa: E731
    return al.ProblemInstance(r(n), r(n), r(n - 1), r(n - 1), rng.randint(0, 5), rng.randint(0, 5),
                              rng.randint(0, 5), rng.randint(0, 5))


def run_case(case):
    ex, kind = case["expect"], case["type"]
    if kind == "error":
        try:
            al.schedule(build(case))
            return ex["error"], "no error", False
        except ValueError as exc:
            return ex["error"], type(exc).__name__, type(exc).__name__ == ex["error"]
    if kind in ("factory", "instance", "change", "clrs"):
        if kind == "factory":
            inst = load_instance()
        elif kind == "change":
            inst = load_instance().copy_with(**{k: {int(s): v for s, v in e.items()} for k, e in case["change"].items()})
        elif kind == "clrs":
            inst = al.ProblemInstance([7, 9, 3, 4, 8, 4], [8, 5, 6, 4, 5, 7], [2, 3, 1, 3, 4], [2, 1, 2, 2, 1],
                                      2, 4, 3, 2)
        else:
            inst = build(case)
        sched = al.schedule(inst)
        ok = (sched.min_time == ex["time"] == al.exhaustive_min_time(inst)[0] and lines_of(sched) == ex["lines"]
              and al.route_time(inst, lines_of(sched)) == sched.min_time)
        return ex, f"time {sched.min_time}, lines {lines_of(sched)}", ok
    if kind == "transfers":
        sched = al.schedule(load_instance())
        got = [list(t) for t in sched.transfers]
        return ex, got, got == ex
    if kind == "trace":
        sched = al.schedule(load_instance())
        ok = True
        for d in sched.trace[1:]:
            ok &= d.f1 == min(d.stay1, d.transfer1) and d.f2 == min(d.stay2, d.transfer2)
            ok &= d.choice1 == ("stay" if d.stay1 <= d.transfer1 else "transfer")
            ok &= d.choice2 == ("stay" if d.stay2 <= d.transfer2 else "transfer")
        return ex, f"{len(sched.trace)} rows consistent" if ok else "inconsistent", ok
    rng = random.Random(case.get("seed", 0))
    if kind == "random_vs_exhaustive":
        bad = 0
        for _ in range(case["trials"]):
            inst = random_instance(rng, rng.randint(1, case["n_max"]))
            sched = al.schedule(inst)
            bad += not (sched.min_time == al.exhaustive_min_time(inst)[0] == al.route_time(inst, lines_of(sched)))
        return ex, f"{case['trials'] - bad}/{case['trials']} ok", bad == 0
    if kind == "monotone":
        bad = 0
        for _ in range(case["trials"]):
            n = rng.randint(2, 8)
            inst = random_instance(rng, n)
            key = rng.choice(["a1", "a2", "t1", "t2"])
            station = rng.randint(1, n if key in ("a1", "a2") else n - 1)
            base = al.schedule(inst).min_time
            target = {"a1": inst.a[0], "a2": inst.a[1], "t1": inst.t[0], "t2": inst.t[1]}[key]
            new = al.schedule(inst.copy_with(**{key: {station: target[station - 1] + rng.randint(1, 20)}})).min_time
            bad += new < base
        return ex, f"{case['trials'] - bad}/{case['trials']} ok", bad == 0
    raise ValueError(kind)
