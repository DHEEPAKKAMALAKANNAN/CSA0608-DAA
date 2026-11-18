"""
Task 6 - Day-4 Design Challenge: large-capacity cargo knapsack WITH item recovery under a memory limit
                                                                                       (CO4, Assignment 4A)
Changed requirement: the drone planner of Task 2 becomes the loading planner of a cargo aircraft feeder truck:
n = 200 consignments, capacity W = 100,000 kg (1 kg resolution), and it must still report WHICH consignments to
load - but the planner runs in a container whose solver may use at most MEMORY_BUDGET_MB = 32 MB.

The original Task 2 design keeps the full (n+1) x (W+1) table -> 20,100,201 cells: about 80 MB even as packed
4-byte integers and about 430 MB as Python lists, so it violates the budget. Two redesigns:

  R1  knapsack_bitpacked        one value row best[0..W] (Theta(W)) + one BIT per decision keep[i][j] = 1 iff
                                loading item i improved capacity j (Theta(nW) bits = nW/8 bytes = 2.5 MB);
                                time Theta(nW) (one pass), items recovered exactly like Task 2's backtracking.
  R2  knapsack_divide_conquer   Hirschberg-style: split the items in halves, compute the value rows of both halves
                                with Theta(W) memory, pick the best capacity split c*, recurse on (left, c*) and
                                (right, W - c*). Memory Theta(W) independent of n; time <= 2nW cell updates.
  plan_load                     chooses R1 when its predicted memory fits the budget, otherwise R2.
Memory evidence: every design is run in a FRESH child process and its peak private memory (what a container
limit counts) is read from the operating system, minus the same process's baseline before solving.
Run:  py -3 large_knapsack.py     (generates test_data/large_instance_n200_W100000.csv and solves it)
"""
import csv
import json
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Task_2"))
from knapsack_dp import backtrack_items, knapsack_bottom_up  # noqa: E402  (the ORIGINAL design of Task 2)

MEMORY_BUDGET_MB = 32
N_ITEMS, CAPACITY = 200, 100_000
PY_BYTES_PER_CELL = 22.3       # Task 2 measurement: 17.12 MiB for the 201 x 4001 = 804,201-cell table
PY_BYTES_PER_VALUE = 36        # list slot (8 B) + int object (28 B) for one stored value in a Python row
INSTANCE_CSV = os.path.join(HERE, "test_data", "large_instance_n200_W100000.csv")
_BITS = bytes.maketrans(b"\x00\x01", b"01")


# --------------------------------------------------------------------------------------- instance
def generate_instance(n=N_ITEMS, seed=42):
    """Consignment weights 100..5000 kg; values weakly correlated with weight (hard for greedy rules)."""
    rng = random.Random(seed)
    weights = [rng.randint(100, 5000) for _ in range(n)]
    values = [w + rng.randint(-w // 4, w // 4) + rng.randint(0, 300) for w in weights]
    return weights, values


def save_instance(weights, values, path=INSTANCE_CSV):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["item", "weight_kg", "value"])
        for i, (w, v) in enumerate(zip(weights, values), 1):
            wr.writerow([i, w, v])


def load_instance(path=INSTANCE_CSV):
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [int(r["weight_kg"]) for r in rows], [int(r["value"]) for r in rows]


# ------------------------------------------------------------------------------ memory predictions
def predict_memory_mb(n, W):
    """Language-independent model (8-byte values, 1-bit decisions) and Python model for each design."""
    cells = (n + 1) * (W + 1)
    return {
        "cells": cells,
        "original_C_int32": 4 * cells / 2**20, "original_C_int64": 8 * cells / 2**20,
        "original_python": PY_BYTES_PER_CELL * cells / 2**20,
        "r1_model": (8 * (W + 1) + n * (W + 1) / 8) / 2**20,
        "r1_python": (PY_BYTES_PER_VALUE * (W + 1) + n * (W + 1) / 7.5) / 2**20,
        "r2_model": 2 * 8 * (W + 1) / 2**20,
        "r2_python": 2 * PY_BYTES_PER_VALUE * (W + 1) / 2**20,
    }


# ------------------------------------------------------------------ R1: value row + bit-packed decisions
def knapsack_bitpacked(weights, values, W):
    """One pass over the items with a single value row (j downward, as in Task 2's single-row version);
    the take/skip decision of every cell is stored as ONE bit. Returns (value, chosen 1-based items, ops)."""
    if W < 0 or len(weights) != len(values) or any(w <= 0 for w in weights) or any(v < 0 for v in values):
        raise ValueError("need W >= 0, equal lengths, positive weights and non-negative values")
    best = [0] * (W + 1)
    keep = []                                       # keep[i]: Python int, bit j = 1 iff item i+1 taken at j
    ops = {"cells": 0, "improvements": 0, "bit_bytes": 0}
    for w, v in zip(weights, values):
        if w > W:
            keep.append(0)
            continue
        flags = bytearray(W + 1)
        for j in range(W, w - 1, -1):               # downward: best[j - w] still belongs to the previous item
            t = best[j - w] + v
            if t > best[j]:
                best[j] = t
                flags[j] = 1
        ops["cells"] += W - w + 1
        ops["improvements"] += flags.count(1)
        row_bits = int(flags[::-1].translate(_BITS), 2)   # pack: bit j <- flags[j]
        keep.append(row_bits)
        ops["bit_bytes"] += (row_bits.bit_length() + 7) // 8
    chosen, j = [], W                               # backtracking, exactly as in Task 2
    for i in range(len(weights) - 1, -1, -1):
        if (keep[i] >> j) & 1:
            chosen.append(i + 1)
            j -= weights[i]
    return best[W], sorted(chosen), ops


# ------------------------------------------------------------- R2: Hirschberg-style divide and conquer
def _value_row(weights, values, lo, hi, cap, ops):
    """best[c] = optimum of items lo..hi-1 for every capacity c <= cap (Theta(cap) memory)."""
    best = [0] * (cap + 1)
    for idx in range(lo, hi):
        w, v = weights[idx], values[idx]
        if w > cap:
            continue
        for j in range(cap, w - 1, -1):
            t = best[j - w] + v
            if t > best[j]:
                best[j] = t
        ops["cells"] += cap - w + 1
    return best


def knapsack_divide_conquer(weights, values, W):
    """Split items into halves; F_left[c] + F_right[cap - c] is maximal at the capacity split c* used by an
    optimal solution; recurse on both halves. Returns (value, chosen 1-based items, ops)."""
    if W < 0 or len(weights) != len(values) or any(w <= 0 for w in weights) or any(v < 0 for v in values):
        raise ValueError("need W >= 0, equal lengths, positive weights and non-negative values")
    ops = {"cells": 0, "split_checks": 0, "max_depth": 0}
    chosen = []

    def solve(lo, hi, cap, depth):
        ops["max_depth"] = max(ops["max_depth"], depth)
        if lo >= hi or cap == 0:
            return
        if hi - lo == 1:                            # one item: load it if it fits and is worth something
            if weights[lo] <= cap and values[lo] > 0:
                chosen.append(lo + 1)
            return
        mid = (lo + hi) // 2
        left = _value_row(weights, values, lo, mid, cap, ops)
        right = _value_row(weights, values, mid, hi, cap, ops)
        best_c, best_v = 0, -1
        for c in range(cap + 1):                    # best way to share the capacity between the halves
            s = left[c] + right[cap - c]
            if s > best_v:
                best_c, best_v = c, s
        ops["split_checks"] += cap + 1
        del left, right                             # free Theta(cap) memory before recursing
        solve(lo, mid, best_c, depth + 1)
        solve(mid, hi, cap - best_c, depth + 1)

    solve(0, len(weights), W, 1)
    chosen.sort()
    return sum(values[i - 1] for i in chosen), chosen, ops


# ------------------------------------------------------------------------------------- the planner
def choose_design(n, W, budget_mb=MEMORY_BUDGET_MB):
    """Decision rule: R1 if its predicted Python memory fits the budget, else R2 if it fits, else None."""
    pred = predict_memory_mb(n, W)
    if pred["r1_python"] <= budget_mb:
        return "R1 bit-packed"
    if pred["r2_python"] <= budget_mb:
        return "R2 divide&conquer"
    return None


def plan_load(weights, values, W, budget_mb=MEMORY_BUDGET_MB):
    """Solve with the design chosen by choose_design(); raise MemoryError if nothing fits the budget."""
    design = choose_design(len(weights), W, budget_mb)
    if design is None:
        raise MemoryError(f"even Theta(W) value rows exceed the {budget_mb} MB budget")
    fn = knapsack_bitpacked if design.startswith("R1") else knapsack_divide_conquer
    value, items, ops = fn(weights, values, W)
    return design, value, items, ops


# ------------------------------------------------------------------------- measurement in a child process
def private_memory_mb():
    """(current, peak) private committed memory of THIS process in MB - Windows psapi; elsewhere ru_maxrss."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + \
                       [(f, ctypes.c_size_t) for f in ("PeakWorkingSetSize", "WorkingSetSize",
                        "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                        "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
        k32, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        pmc = PMC()
        pmc.cb = ctypes.sizeof(PMC)
        psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
        return pmc.PagefileUsage / 2**20, pmc.PeakPagefileUsage / 2**20
    import resource                                  # Linux reports KB, macOS bytes (peak only)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss = rss / 2**20 if sys.platform == "darwin" else rss / 1024
    return rss, rss


DESIGNS = {"R1": knapsack_bitpacked, "R2": knapsack_divide_conquer}


def child_run(design, n, W):
    """Executed inside the child process: build the instance, solve with one design, print a JSON line.
    Reported memory = peak private memory after solving - current private memory before solving. This is an
    upper bound of the solver's own peak (it can only be inflated by start-up transients, reported as slack)."""
    weights, values = load_instance() if n == N_ITEMS and os.path.exists(INSTANCE_CSV) else generate_instance(n)
    base, base_peak = private_memory_mb()
    t0 = time.perf_counter()
    if design == "original":                         # the Task 2 design: full table + backtracking
        F, ops = knapsack_bottom_up(weights, values, W)
        value, items = F[n][W], backtrack_items(F, weights, W)
    else:
        value, items, ops = DESIGNS[design](weights, values, W)
    t = time.perf_counter() - t0
    print(json.dumps({"design": design, "n": n, "W": W, "value": value, "items": items, "cells": ops["cells"],
                      "time_s": t, "peak_mb": private_memory_mb()[1] - base, "baseline_mb": base,
                      "slack_mb": base_peak - base}))


def measure_in_child(design, n, W):
    """Run one design in a fresh interpreter so that its peak memory is not mixed with other runs."""
    out = subprocess.run([sys.executable, os.path.abspath(__file__), "--child", design, str(n), str(W)],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


def main():
    weights, values = generate_instance()
    save_instance(weights, values)
    weights, values = load_instance()
    n, W = len(weights), CAPACITY
    print("=" * 108)
    print(f" TASK 6 - DESIGN CHALLENGE: n = {n} consignments, W = {W:,} kg, solver memory budget {MEMORY_BUDGET_MB} MB")
    print("=" * 108)
    print(f"[1] Instance test_data/{os.path.basename(INSTANCE_CSV)} (generated with seed 42)")
    print(f"    weights {min(weights)}..{max(weights)} kg (total {sum(weights):,} kg = {sum(weights) / W:.1f} x W), "
          f"values {min(values)}..{max(values)}")
    p = predict_memory_mb(n, W)
    print("\n[2] Predicted memory (before running anything)")
    print(f"    original 2-D table: {p['cells']:,} cells -> {p['original_C_int32']:.1f} MB as int32, "
          f"{p['original_C_int64']:.1f} MB as int64, ~{p['original_python']:.0f} MB in Python  -> VIOLATES")
    print(f"    R1 bit-packed     : model {p['r1_model']:.1f} MB (one 8-byte row + n*W bits), "
          f"Python ~{p['r1_python']:.1f} MB  -> fits")
    print(f"    R2 divide&conquer : model {p['r2_model']:.1f} MB (two 8-byte rows), "
          f"Python ~{p['r2_python']:.1f} MB  -> fits, independent of n")

    print("\n[3] Each design solves the full instance in a fresh process (time, peak private memory above baseline)")
    runs = {d: measure_in_child(d, n, W) for d in ("original", "R1", "R2")}
    for d, label in [("original", "original 2-D (Task 2)"), ("R1", "R1 bit-packed"), ("R2", "R2 divide&conquer")]:
        r = runs[d]
        wt = sum(weights[i - 1] for i in r["items"])
        print(f"    {label:<22}value {r['value']:>7,}  items {len(r['items']):>2}  load {wt:>7,} kg  cells "
              f"{r['cells']:>11,}  {r['time_s']:>5.2f} s  peak {r['peak_mb']:>6.1f} MB  "
              f"{'<= budget' if r['peak_mb'] <= MEMORY_BUDGET_MB else 'OVER BUDGET'}")
    print(f"    (child baseline before solving {runs['R1']['baseline_mb']:.1f} MB is not counted; start-up slack "
          f"{max(r['slack_mb'] for r in runs.values()):.1f} MB)")

    print("\n[4] Validation against the original design")
    v0, items0 = runs["original"]["value"], runs["original"]["items"]
    v1, items1 = runs["R1"]["value"], runs["R1"]["items"]
    v2, items2 = runs["R2"]["value"], runs["R2"]["items"]
    print(f"    same optimum: R1 {v1 == v0}, R2 {v2 == v0};  R1 recovers exactly the original item set: "
          f"{items1 == items0}")
    feasible = all(sum(weights[i - 1] for i in s) <= W for s in (items1, items2))
    adds_up = v1 == sum(values[i - 1] for i in items1) and v2 == sum(values[i - 1] for i in items2)
    print(f"    both recovered loads respect W = {W:,} kg: {feasible};  item values add up to the optimum: {adds_up}")
    print(f"    R2 evaluated {runs['R2']['cells'] / runs['R1']['cells']:.2f} x the cells of R1 (predicted bound: 2 x)")

    print("\n[5] plan_load() decisions from the predicted Python memory (R1 if it fits, else R2, else refuse)")
    for (nn, WW) in [(n, W), (3000, W), (n, 1_000_000)]:
        pr = predict_memory_mb(nn, WW)
        choice = choose_design(nn, WW)
        print(f"    n = {nn:>4}, W = {WW:>9,}, budget {MEMORY_BUDGET_MB} MB: R1 ~{pr['r1_python']:>5.1f} MB, "
              f"R2 ~{pr['r2_python']:>5.1f} MB -> {choice or 'REFUSE (use a coarser weight unit, e.g. 10 kg)'}")
    print(f"    given instance - chosen consignments (first 12 of {len(items1)}): {items1[:12]} ...")


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--child":
        child_run(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    else:
        main()
