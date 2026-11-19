"""
Task 2.1 + 2.2 - Build it and break it.

2.1  Normal case (test_data/normal_case.json): Solution A (fractional greedy) with its full decision sequence,
     verified against an independent reference (every item split into 1-kg units, then exact 0/1 DP);
     Solution B (0/1 DP) on the same data with the selected items.
2.2  Student-designed counter-example (test_data/counterexample.json): the PREDICTION is printed first, then
     the ratio greedy applied to the 0/1 problem, the DP optimum, the line "GreedyResult != DPOptimum", and the
     diagnosis of the first greedy commitment that makes the optimum unreachable.
Run:  py -3 knapsack_demo.py
"""
import csv
import json
import os
import sys
import textwrap
from collections import Counter
from fractions import Fraction

import knapsack_engines as ks

HERE = os.path.dirname(os.path.abspath(__file__))


def write_csv(name, rows):
    """Save the raw numbers behind a report table in results/ (no console output)."""
    with open(os.path.join(HERE, "results", name), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_case(name):
    with open(os.path.join(HERE, "test_data", name), encoding="utf-8") as f:
        spec = json.load(f)
    return spec, [ks.Item(*row) for row in spec["items"]], spec["capacity"]


def show_items(items, capacity):
    print(f"  capacity W = {capacity} kg;  items (Item ID, weight kg, value, value/weight):")
    print("   " + "  ".join(f"{it.item_id}({it.weight},{it.value},{float(ks.ratio(it)):.2f})" for it in items))


def show_trace(trace):
    print(f"  {'step':>4} {'item':<5} {'v/w':>5}  {'decision':<26} {'fraction':>8} {'room left':>9} {'value so far':>12}")
    for k, st in enumerate(trace, 1):
        print(f"  {k:>4} {st.item.item_id:<5} {float(st.ratio):>5.2f}  {st.decision:<26} {str(st.fraction):>8} "
              f"{float(st.room_after):>9.2f} {float(st.value_after):>12.2f}")


def unit_split_reference(items, capacity):
    """Independent check of Solution A: split every item into 1-kg units (value v/w each) and solve 0/1 by DP.
    Exact when all weights and W are integers (then some optimal fractional load uses whole kilograms)."""
    units = [ks.Item(f"{it.item_id}.{u}", 1, Fraction(it.value, it.weight))
             for it in items for u in range(it.weight)]
    return ks.knapsack_01_dp(units, capacity)[0]


def normal_case():
    spec, items, cap = load_case("normal_case.json")
    print(f"TASK 2.1 - NORMAL CASE: {spec['name']}")
    show_items(items, cap)
    print("  Expected behaviour: the fractional greedy is optimal for the fractional formulation (greedy-choice")
    print("  property: a kilogram of the densest item is never worse than a kilogram of any other).")
    print("\n  Solution A - fractional greedy, decision sequence:")
    ops = Counter()
    value, plan, trace = ks.fractional_greedy(items, cap, ops)
    show_trace(trace)
    write_csv("t2_normal_decisions.csv", [dict(step=k, item=st.item.item_id, ratio=round(float(st.ratio), 2),
                                               decision=st.decision, fraction=str(st.fraction),
                                               room_after=float(st.room_after), value_after=float(st.value_after))
                                          for k, st in enumerate(trace, 1)])
    print("  Selected: " + ", ".join(f"{it.item_id} x {f}" for it, f in plan) + f"  -> value {float(value):.2f}")
    ref = unit_split_reference(items, cap)
    print(f"  Reference (1-kg unit split + exact DP): {float(ref):.2f} -> {'MATCH' if ref == value else 'MISMATCH'}"
          f";  work: {ops['comparisons']} comparisons, {ops['items_examined']} items examined")
    dops = Counter()
    best, chosen, _ = ks.knapsack_01_dp(items, cap, dops)
    print(f"  Solution B - 0/1 DP on the same data (items indivisible): optimum {best} with "
          f"{'+'.join(i.item_id for i in chosen)} ({sum(i.weight for i in chosen)} kg), "
          f"{dops['dp_cells']} table cells")
    return ref == value


def counterexample():
    spec, items, cap = load_case("counterexample.json")
    print("\n" + "=" * 112)
    print(f"TASK 2.2 - BREAK THE GREEDY INTUITION: {spec['name']}")
    show_items(items, cap)
    print(textwrap.fill(spec["design"], 108, initial_indent="  Design idea: ", subsequent_indent=" " * 15))
    print("  PREDICTION (recorded before execution): the ratio greedy commits to C1 first (highest ratio 5.0);")
    print("  19 kg remain, so C2 and C3 (20 kg) are skipped and only C4 + C5 fit -> greedy 153; the optimum takes")
    print("  C2 + C3 = 40 kg -> 192. The first commitment that blocks the optimum should be C1 (step 1).")
    gops, dops = Counter(), Counter()
    g_value, g_chosen, g_trace = ks.greedy_01_ratio(items, cap, gops)
    print("\n  Greedy (value/weight) applied to the 0/1 problem - decision sequence:")
    show_trace(g_trace)
    best, chosen, table = ks.knapsack_01_dp(items, cap, dops, keep_table=True)
    print(f"  GreedyResult = {g_value} ({'+'.join(i.item_id for i in g_chosen)}, "
          f"{sum(i.weight for i in g_chosen)} kg)")
    print(f"  DPOptimum    = {best} ({'+'.join(i.item_id for i in chosen)}, {sum(i.weight for i in chosen)} kg)"
          f"   brute force over 2^{len(items)} subsets = {ks.knapsack_01_bruteforce(items, cap)}")
    print(f"  GreedyResult != DPOptimum: {g_value} != {best}  (greedy reaches {100 * g_value / best:.1f} % of "
          f"the optimum)" if g_value != best else "  GreedyResult == DPOptimum (counter-example FAILED)")
    print("\n  DP table rows best[i][c] for c = 0, 4, 9, 13, 19, 20, 21, 25, 29, 30, 34, 40:")
    cols = (0, 4, 9, 13, 19, 20, 21, 25, 29, 30, 34, 40)
    print("  " + f"{'i (item)':<10}" + "".join(f"{c:>5}" for c in cols))
    for i in range(len(items) + 1):
        label = "0 (none)" if i == 0 else f"{i} ({items[i - 1].item_id})"
        print("  " + f"{label:<10}" + "".join(f"{table[i][c]:>5}" for c in cols))
    optimum, rows, blocking = ks.first_blocking_commitment(items, cap)
    print("\n  Diagnosis - best value still reachable after each greedy decision (exact DP on undecided items):")
    print(f"  {'step':>4} {'item':<5} {'decision':<8} {'committed':>9} {'room':>5} {'best reachable':>14}  status")
    print(f"  {0:>4} {'-':<5} {'start':<8} {0:>9} {cap:>5} {optimum:>14}  optimum still reachable")
    for step, it, decision, committed, room, reachable in rows:
        status = "optimum still reachable" if reachable == optimum else f"optimum LOST ({reachable} < {optimum})"
        print(f"  {step:>4} {it.item_id:<5} {decision:<8} {committed:>9} {room:>5} {reachable:>14}  {status}")
    write_csv("t2_counterexample_diagnosis.csv",
              [dict(step=s, item=it.item_id, decision=d, committed=c, room=r, best_reachable=b)
               for s, it, d, c, r, b in rows])
    if blocking:
        print(f"  First greedy commitment that prevents the optimum: step {blocking} = "
              f"{rows[blocking - 1][1].item_id} (prediction {'CONFIRMED' if blocking == 1 else 'NOT CONFIRMED'})")
    return g_value != best


def main():
    print("TASK 2 - GREEDY (FRACTIONAL) vs DP (0/1) KNAPSACK: BUILD IT, BREAK IT")
    print("=" * 112)
    ok = normal_case() and counterexample()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
