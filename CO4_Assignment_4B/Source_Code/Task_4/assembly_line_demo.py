"""
Task 4.1 + 4.2 - build the optimisation engine and expose the decision process.

Loads the factory instance (test_data/factory_instance.json: station times, transfer times, entry and exit
times), runs the DP and prints
  * the input,
  * the decision table: for every station the cost of reaching each line by staying vs by transferring and the
    selected decision (the optimal substructure made visible),
  * the exit decision, the minimum production time, the line selected at each station, the transfer points and
    the final optimal route in the arrow format of the task statement,
  * a cross-check against exhaustive enumeration of all 2^n line sequences.
Run:  py -3 assembly_line_demo.py
"""
import csv
import json
import os
import sys

import assembly_line_dp as al

HERE = os.path.dirname(os.path.abspath(__file__))


def write_csv(name, rows):
    """Save the raw numbers behind a report table in results/ (no console output)."""
    with open(os.path.join(HERE, "results", name), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_instance(path=os.path.join(HERE, "test_data", "factory_instance.json")):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return al.ProblemInstance(d["a1"], d["a2"], d["t1"], d["t2"], d["e1"], d["e2"], d["x1"], d["x2"], d["name"])


def print_input(inst):
    n = inst.n
    print(f"Input: {inst.name}")
    print(f"  {'':<26}" + "".join(f"{'S' + str(j):>6}" for j in range(1, n + 1)))
    print(f"  {'Line 1 processing a1':<26}" + "".join(f"{v:>6}" for v in inst.a[0]))
    print(f"  {'Line 2 processing a2':<26}" + "".join(f"{v:>6}" for v in inst.a[1]))
    print(f"  {'Transfer L1->L2 after Sj':<26}" + "".join(f"{v:>6}" for v in inst.t[0]))
    print(f"  {'Transfer L2->L1 after Sj':<26}" + "".join(f"{v:>6}" for v in inst.t[1]))
    print(f"  Entry e1 = {inst.e[0]}, e2 = {inst.e[1]};  Exit x1 = {inst.x[0]}, x2 = {inst.x[1]}")


def print_decisions(sched):
    print("\nTASK 4.2 - DP DECISIONS AT EACH STATION  (f1/f2 = fastest time to leave the station on line 1/2)")
    print(f"  {'Station':>7} | {'L1 by stay':>10} {'L1 by transfer':>14} {'Selected':>9} {'f1':>4} | "
          f"{'L2 by stay':>10} {'L2 by transfer':>14} {'Selected':>9} {'f2':>4}")
    for d in sched.trace:
        t1 = "-" if d.transfer1 is None else d.transfer1
        t2 = "-" if d.transfer2 is None else d.transfer2
        print(f"  {d.station:>7} | {d.stay1:>10} {t1:>14} {d.choice1:>9} {d.f1:>4} | "
              f"{d.stay2:>10} {t2:>14} {d.choice2:>9} {d.f2:>4}")
    print(f"  {'Exit':>7} | f1 + x1 = {sched.exit_costs[0]:<4} f2 + x2 = {sched.exit_costs[1]:<4} -> "
          f"leave from line {sched.final_line}")


def route_arrows(sched):
    """The route in the arrow format of the task statement (one list of text lines)."""
    lines, prev = ["Entry"], None
    for station, line in sched.route:
        lines.append("  ↓ Transfer" if prev is not None and line != prev else "  ↓")
        lines.append(f"Line {line} – Station {station}")
        prev = line
    lines += ["  ↓", "Exit", f"Minimum Production Time = {sched.min_time}"]
    return lines


def print_result(inst, sched):
    print(f"\nTASK 4.1 - RESULT")
    print(f"  Minimum total production time = {sched.min_time}")
    print("  Line selected at each station:  " + ", ".join(f"S{s}: L{l}" for s, l in sched.route))
    if sched.transfers:
        print("  Transfer points:  " + "; ".join(f"after S{s}: L{a} -> L{b} (+{tt})" for s, a, b, tt in sched.transfers))
    else:
        print("  Transfer points:  none (the product stays on one line)")
    print("  Final optimal route:")
    for text in route_arrows(sched):
        print("      " + text)
    recomputed = al.route_time(inst, [line for _, line in sched.route])
    print(f"  Route time recomputed leg by leg = {recomputed}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")          # the route uses the arrow character
    inst = load_instance()
    print("TASK 4 - ASSEMBLY LINE SCHEDULING BY DYNAMIC PROGRAMMING")
    print("=" * 112)
    print_input(inst)
    print("Expected behaviour: minimum = min over all 2^n line sequences (exhaustive check below); the route")
    print("must re-sum to that minimum; transfers only where the saving exceeds the transfer time.")
    sched = al.schedule(inst)
    write_csv("t4_decision_table.csv", [d._asdict() for d in sched.trace])
    print_decisions(sched)
    print_result(inst, sched)
    best, lines = al.exhaustive_min_time(inst)
    print(f"\nCheck: exhaustive enumeration of 2^{inst.n} = {2 ** inst.n} line sequences -> minimum {best} via "
          f"{lines} -> {'MATCH' if best == sched.min_time else 'MISMATCH'}")
    print(f"DP work: {2 * (inst.n - 1)} stay/transfer comparisons + 1 exit comparison (exhaustive: "
          f"{2 ** inst.n} complete routes)")
    return 0 if best == sched.min_time else 1


if __name__ == "__main__":
    sys.exit(main())
