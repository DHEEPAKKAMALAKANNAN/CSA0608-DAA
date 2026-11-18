"""
Task 6 - experiments: does the redesign keep its promises as W and n grow?

Every configuration runs in a FRESH child process (large_knapsack.measure_in_child) that reports the optimum,
the recovered items, the cells evaluated, the time and the peak private memory above its baseline.
E1  n = 200, W = 12,500 / 25,000 / 50,000 / 100,000 : original (Task 2 table), R1 (bit-packed), R2 (divide&conquer)
E2  W = 100,000, n = 50 / 100 / 200 / 400 / 800      : R1 and R2 (original only for n <= 200: n = 400 would need
                                                       ~0.8 GB and is reported from the measured bytes per cell)
Outputs: results/large_knapsack_E1.csv, results/large_knapsack_E2.csv,
         ../../Report/Screenshots/task6_large_knapsack.png
Run:  py -3 large_knapsack_experiments.py
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from large_knapsack import (CAPACITY, MEMORY_BUDGET_MB, N_ITEMS, PY_BYTES_PER_CELL, generate_instance,  # noqa: E402
                            measure_in_child, predict_memory_mb, save_instance)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.normpath(os.path.join(HERE, "..", "..", "Report", "Screenshots"))


def row_of(r, n, W):
    return {"design": r["design"], "n": n, "W": W, "value": r["value"], "items": len(r["items"]),
            "cells": r["cells"], "time_s": round(r["time_s"], 4), "peak_mb": round(r["peak_mb"], 2)}


def print_row(r, ok):
    print(f"  {r['design']:<9}{r['n']:>5}{r['W']:>9,}{r['value']:>10,}{r['items']:>7}{r['cells']:>13,}"
          f"{r['time_s']:>9.2f}{r['peak_mb']:>10.1f}{'yes' if r['peak_mb'] <= MEMORY_BUDGET_MB else 'NO':>10}"
          f"{ok:>11}")


HEADER = (f"  {'design':<9}{'n':>5}{'W':>9}{'optimum':>10}{'items':>7}{'cells':>13}{'time s':>9}{'peak MB':>10}"
          f"{'<= 32 MB':>10}{'same opt?':>11}")


def experiment_1():
    print(f"E1  n = {N_ITEMS}, growing capacity W (one fresh process per run)")
    print(HEADER)
    print("  " + "-" * (len(HEADER) - 2))
    rows = []
    for W in (12_500, 25_000, 50_000, 100_000):
        res = {d: measure_in_child(d, N_ITEMS, W) for d in ("original", "R1", "R2")}
        same = "yes" if res["original"]["value"] == res["R1"]["value"] == res["R2"]["value"] else "NO"
        for d in ("original", "R1", "R2"):
            r = row_of(res[d], N_ITEMS, W)
            rows.append(r)
            print_row(r, same)
    return rows


def experiment_2(e1):
    print(f"\nE2  W = {CAPACITY:,}, growing number of items n (original only where it is affordable)")
    print(HEADER)
    print("  " + "-" * (len(HEADER) - 2))
    rows = []
    for n in (50, 100, 200, 400, 800):
        designs = ("original", "R1", "R2") if n <= 200 else ("R1", "R2")
        if n == N_ITEMS:                               # identical runs already done in E1
            res = {r["design"]: r for r in e1 if r["W"] == CAPACITY}
            got = [res[d] for d in designs]
        else:
            got = [row_of(measure_in_child(d, n, CAPACITY), n, CAPACITY) for d in designs]
        same = "yes" if len({g["value"] for g in got}) == 1 else "NO"
        for r in got:
            rows.append(dict(r))
            print_row(r, same)
        if n > 200:
            pred = predict_memory_mb(n, CAPACITY)["original_python"]
            print(f"  {'original':<9}{n:>5}{CAPACITY:>9,}    not run - predicted {pred:,.0f} MB "
                  f"from {PY_BYTES_PER_CELL} bytes/cell")
    return rows


def save_csv(rows, name):
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


def plot(e1, e2):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    styles = {"original": ("o-", "original 2-D table (Task 2)"), "R1": ("s-", "R1 bit-packed decisions"),
              "R2": ("^-", "R2 divide & conquer")}
    ax = axes[0]
    for d, (st, lab) in styles.items():
        pts = [r for r in e1 if r["design"] == d]
        ax.loglog([r["W"] for r in pts], [r["peak_mb"] for r in pts], st, label=lab)
    ax.axhline(MEMORY_BUDGET_MB, color="red", ls="--", label=f"budget {MEMORY_BUDGET_MB} MB")
    ax.set_title(f"Peak memory vs capacity (n = {N_ITEMS})")
    ax.set_xlabel("capacity W in kg (log scale)")
    ax.set_ylabel("peak private memory in MB (log scale)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)

    ax = axes[1]
    for d, (st, lab) in styles.items():
        pts = [r for r in e2 if r["design"] == d]
        ax.plot([r["n"] for r in pts], [r["peak_mb"] for r in pts], st, label=lab + " (measured)")
    ns = sorted({r["n"] for r in e2})
    ax.plot(ns, [predict_memory_mb(n, CAPACITY)["original_python"] for n in ns], "k:",
            label=f"original, predicted {PY_BYTES_PER_CELL} B/cell")
    ax.axhline(MEMORY_BUDGET_MB, color="red", ls="--", label=f"budget {MEMORY_BUDGET_MB} MB")
    ax.set_yscale("log")
    ax.set_title(f"Peak memory vs number of items (W = {CAPACITY:,})")
    ax.set_xlabel("number of consignments n")
    ax.set_ylabel("peak private memory in MB (log scale)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=7)

    ax = axes[2]
    for d, (st, lab) in styles.items():
        pts = [r for r in e1 if r["design"] == d]
        ax.plot([r["W"] for r in pts], [r["cells"] / 1e6 for r in pts], st, label=lab)
    ax.plot([r["W"] for r in e1 if r["design"] == "R1"], [2 * N_ITEMS * r["W"] / 1e6 for r in e1
                                                           if r["design"] == "R1"], "k:", label="bound 2nW")
    ax.set_title(f"Cells evaluated vs capacity (n = {N_ITEMS})")
    ax.set_xlabel("capacity W in kg")
    ax.set_ylabel("cells evaluated (millions)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    path = os.path.join(SHOTS, "task6_large_knapsack.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def main():
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    save_instance(*generate_instance())
    print("=" * 112)
    print(" TASK 6 - EXPERIMENTS: ORIGINAL TABLE vs R1 (bit-packed) vs R2 (divide & conquer) UNDER A 32 MB BUDGET")
    print("=" * 112)
    e1 = experiment_1()
    e2 = experiment_2(e1)
    o = [r for r in e1 if r["design"] == "original"]
    per_cell = [r["peak_mb"] * 2**20 / ((N_ITEMS + 1) * (r["W"] + 1)) for r in o]
    print(f"\n  original table: {', '.join(f'{b:.1f}' for b in per_cell)} bytes per cell -> memory grows as Theta(nW)")
    r1 = [r for r in e2 if r["design"] == "R1"]
    r2 = [r for r in e2 if r["design"] == "R2"]
    print(f"  R1 memory n = {r1[0]['n']} -> {r1[-1]['n']}: {r1[0]['peak_mb']:.1f} -> {r1[-1]['peak_mb']:.1f} MB "
          f"(grows with the n*W bits);  R2: {r2[0]['peak_mb']:.1f} -> {r2[-1]['peak_mb']:.1f} MB (Theta(W) only)")
    ratio = [b["cells"] / a["cells"] for a, b in zip(r1, r2)]
    print(f"  R2 / R1 cells: {', '.join(f'{x:.2f}' for x in ratio)}  (bound 2)")
    print("Saved:", os.path.relpath(save_csv(e1, "large_knapsack_E1.csv"), HERE), ",",
          os.path.relpath(save_csv(e2, "large_knapsack_E2.csv"), HERE))
    print("Graph:", os.path.relpath(plot(e1, e2), HERE))


if __name__ == "__main__":
    main()
