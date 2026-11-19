"""
load_vehicle.py - Task 1 (CO4 Assignment 4A): repaired LoadVehicle pseudocode (fractional knapsack).

Problem: packages have a weight and a value and may be divided; load the vehicle so that the total value
is maximised without exceeding the capacity.  This program implements, line by line, the repaired
pseudocode ALGORITHM LoadVehicle(P, n, C) of the report (greedy choice: highest value-per-kg first).
It is used ONLY to verify the manual desk-check that was done by hand first: it prints the same
state -> decision -> update table.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def read_packages(path):
    """Read (id, weight, value) rows from a CSV file and the capacity from its 'CAPACITY' row."""
    packages, capacity = [], None
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["id"] == "CAPACITY":
                capacity = float(row["weight"])
            else:
                packages.append((row["id"], float(row["weight"]), float(row["value"])))
    return packages, capacity


def load_vehicle(packages, capacity, trace=None):
    """Repaired LoadVehicle: returns (total_value, load list of (id, fraction, weight_taken, value_taken)).

    If `trace` is a list, one tuple per loop iteration is appended to it (for printing the desk-check).
    """
    # SORT P in descending order of value/weight (ties: smaller weight first, then id)
    order = sorted(packages, key=lambda p: (-(p[2] / p[1]), p[1], p[0]))
    remaining, total, load = capacity, 0.0, []
    i = 0
    while remaining > 0 and i < len(order):          # termination: vehicle full OR no package left
        pid, w, v = order[i]
        before = remaining
        if w <= remaining:                            # feasibility: the whole package fits
            fraction = 1.0
            decision = "whole package fits -> take all"
        else:                                         # package does not completely fit -> divide it
            fraction = remaining / w
            decision = f"only {remaining:g} of {w:g} kg fits -> take fraction {fraction:.4f}"
        load.append((pid, fraction, fraction * w, fraction * v))
        remaining -= fraction * w                     # update remaining capacity
        total += fraction * v                         # update total value
        if trace is not None:
            trace.append((i + 1, pid, w, v, v / w, before, decision, remaining, total))
        i += 1
    return total, load


def main():
    packages, capacity = read_packages(os.path.join(HERE, "packages.csv"))
    print("=" * 110)
    print("TASK 1 - Repaired LoadVehicle (fractional loading, greedy by value/weight)  - verification run")
    print("=" * 110)
    print(f"Capacity C = {capacity:g} kg      packages (id, weight kg, value):",
          ", ".join(f"{p}({w:g},{v:g})" for p, w, v in packages))
    print("\nStep 1 - SORT packages in descending order of value/weight:")
    for p, w, v in sorted(packages, key=lambda p: (-(p[2] / p[1]), p[1], p[0])):
        print(f"   {p:<3} weight {w:>5g}   value {v:>6g}   ratio {v / w:>6.2f}")
    trace = []
    total, load = load_vehicle(packages, capacity, trace)
    print("\nStep 2 - greedy loop (state -> decision -> update):")
    print(f"{'it':>2} | {'pkg':<3} | {'w':>4} | {'v':>5} | {'v/w':>5} | {'rem before':>10} | "
          f"{'decision':<46} | {'rem after':>9} | {'total':>7}")
    print("-" * 110)
    for it, p, w, v, r, before, dec, after, tot in trace:
        print(f"{it:>2} | {p:<3} | {w:>4g} | {v:>5g} | {r:>5.2f} | {before:>10g} | {dec:<46} | "
              f"{after:>9g} | {tot:>7.2f}")
    print("-" * 110)
    print("Loop ends because remaining capacity = 0." if trace and trace[-1][7] <= 0
          else "Loop ends because no package is left.")
    print("\nResult - load list (package, fraction, kg loaded, value):")
    for pid, fr, wt, val in load:
        print(f"   {pid:<3} fraction {fr:.4f}   {wt:>6.2f} kg   value {val:>7.2f}")
    print(f"TOTAL VALUE = {total:.2f}   (loaded {sum(x[2] for x in load):g} of {capacity:g} kg)")


if __name__ == "__main__":
    main()
