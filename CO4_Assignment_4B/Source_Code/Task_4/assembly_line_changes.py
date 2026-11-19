"""
Task 4.3 + 4.4 - predict before you execute, production disruption, and boundary / invalid-input tests.

4.3  One transfer time is raised substantially (line 1 -> line 2 after station 2: 2 -> 12 min).
4.4  A machine slows down (line 2, station 4: 3 -> 12 min).
For both, the prediction recorded in test_data/change_predictions.json (written before this program was first
run) is printed FIRST; then the modified DP runs, its decision table is shown with the decisions that flipped
marked, the new route is compared with the baseline and each prediction is checked.
Run:  py -3 assembly_line_changes.py
"""
import csv
import json
import os
import sys
import textwrap

import assembly_line_dp as al
from assembly_line_demo import load_instance

HERE = os.path.dirname(os.path.abspath(__file__))


def write_csv(name, rows):
    """Save the raw numbers behind a report table in results/ (no console output)."""
    with open(os.path.join(HERE, "results", name), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def compact_route(sched):
    parts, prev = ["Entry"], None
    for station, line in sched.route:
        parts.append(("=T=> " if prev is not None and line != prev else "-> ") + f"L{line}-S{station}")
        prev = line
    return " ".join(parts) + " -> Exit"


def decision_table(base, new):
    print(f"    {'Station':>7} | {'L1 stay':>7} {'L1 transf':>9} {'sel':>8} {'f1':>4} | {'L2 stay':>7} "
          f"{'L2 transf':>9} {'sel':>8} {'f2':>4} | flipped vs baseline")
    for b, d in zip(base.trace, new.trace):
        flips = [f"L{k}: {old} -> {cur}" for k, old, cur in ((1, b.choice1, d.choice1), (2, b.choice2, d.choice2))
                 if old != cur]
        t1 = "-" if d.transfer1 is None else d.transfer1
        t2 = "-" if d.transfer2 is None else d.transfer2
        print(f"    {d.station:>7} | {d.stay1:>7} {t1:>9} {d.choice1:>8} {d.f1:>4} | {d.stay2:>7} {t2:>9} "
              f"{d.choice2:>8} {d.f2:>4} | {', '.join(flips) if flips else '-'}")
    print(f"    {'Exit':>7} | f1 + x1 = {new.exit_costs[0]}, f2 + x2 = {new.exit_costs[1]} -> line {new.final_line}")


def first_route_change(base, new):
    for (s, l_old), (_, l_new) in zip(base.route, new.route):
        if l_old != l_new:
            return s
    return None


def run_change(title, inst, base, spec, keys):
    print("\n" + "=" * 112)
    print(title)
    print(textwrap.fill(spec["description"], 110, initial_indent="  Change: ", subsequent_indent=" " * 10))
    print("  PREDICTION (recorded before execution):")
    for key in keys:
        print(textwrap.fill(spec[key], 112, initial_indent=f"    {key:<20} ", subsequent_indent=" " * 25))
    change = {k: {int(s): v for s, v in edits.items()} for k, edits in spec["change"].items()}
    new = al.schedule(inst.copy_with(**change))
    write_csv(f"t4_{title.split()[1].replace('.', '_')}_decision_table.csv",
              [dict(d._asdict(), route_lines=" ".join(str(line) for _, line in new.route), min_time=new.min_time)
               for d in new.trace])
    print("  ACTUAL RESULT:")
    decision_table(base, new)
    print(f"    baseline route: {compact_route(base)}   time {base.min_time}")
    print(f"    new route:      {compact_route(new)}   time {new.min_time}")
    old_route_now = al.route_time(inst.copy_with(**change), [l for _, l in base.route])
    print(f"    the old route under the new times would cost {old_route_now}")
    best, _ = al.exhaustive_min_time(inst.copy_with(**change))
    print(f"    exhaustive check of the modified instance: {best} -> {'MATCH' if best == new.min_time else 'MISMATCH'}")
    return new


def boundary_tests(inst):
    print("\n" + "=" * 112)
    print("BOUNDARY AND INVALID-INPUT TESTS")
    cases = [
        ("single station (n = 1): min(e1+a1+x1, e2+a2+x2)", lambda: al.ProblemInstance([5], [3], [], [], 2, 4, 1, 3)),
        ("zero transfer times: free switching", lambda: inst.copy_with(t1={j: 0 for j in range(1, 6)},
                                                                      t2={j: 0 for j in range(1, 6)})),
        ("huge transfer times (1000): never transfer", lambda: inst.copy_with(t1={j: 1000 for j in range(1, 6)},
                                                                              t2={j: 1000 for j in range(1, 6)})),
        ("identical lines: tie -> stays, no transfer", lambda: al.ProblemInstance([3, 3, 3], [3, 3, 3], [1, 1], [1, 1],
                                                                                  1, 1, 1, 1)),
        ("lines of different length", lambda: al.ProblemInstance([1, 2, 3], [1, 2], [1, 1], [1], 1, 1, 1, 1)),
        ("wrong number of transfer times", lambda: al.ProblemInstance([1, 2], [1, 2], [1, 1], [1], 1, 1, 1, 1)),
        ("negative processing time", lambda: al.ProblemInstance([1, -2], [1, 2], [1], [1], 1, 1, 1, 1)),
        ("no stations", lambda: al.ProblemInstance([], [], [], [], 1, 1, 1, 1)),
    ]
    for name, build in cases:
        try:
            case = build()
            sched = al.schedule(case)
            best, _ = al.exhaustive_min_time(case)
            outcome = (f"time {sched.min_time} (exhaustive {best}), {len(sched.transfers)} transfer(s), "
                       f"lines {[l for _, l in sched.route]}")
        except ValueError as exc:
            outcome = f"rejected: ValueError: {exc}"
        print(f"  {name:<50} {outcome[:72]}")


def main():
    with open(os.path.join(HERE, "test_data", "change_predictions.json"), encoding="utf-8") as f:
        predictions = json.load(f)
    inst = load_instance()
    base = al.schedule(inst)
    print("TASK 4.3 / 4.4 - REQUIREMENT CHANGES WITH PREDICTIONS RECORDED FIRST")
    print("=" * 112)
    print(f"Baseline: {compact_route(base)}   minimum time {base.min_time}")
    spec = predictions["task_4_3"]
    new = run_change("TASK 4.3 - TRANSFER TIME INCREASED", inst, base, spec,
                     ("route_changes", "affected_decision", "total_increases"))
    print("  COMPARISON: route changed " + ("YES" if new.route != base.route else "NO")
          + f";  station-3 'reach line 2' decision: {base.trace[2].choice2} -> {new.trace[2].choice2}"
          + f";  time {base.min_time} -> {new.min_time} ({new.min_time - base.min_time:+d})")
    spec = predictions["task_4_4"]
    new = run_change("TASK 4.4 - PRODUCTION DISRUPTION", inst, base, spec,
                     ("route_changes", "moves_to_other_line", "change_station", "time_effect"))
    station = first_route_change(base, new)
    moved = dict(new.route).get(station) if station else None
    print(f"  COMPARISON: route changed {'YES' if new.route != base.route else 'NO'};  first station on a different "
          f"line: {('S' + str(station)) if station else 'none'}" + (f" (now line {moved})" if moved else "")
          + f";  time {base.min_time} -> {new.min_time} ({new.min_time - base.min_time:+d})")
    boundary_tests(inst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
