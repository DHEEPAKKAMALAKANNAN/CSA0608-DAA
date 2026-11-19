"""
Task 5 - Industry decision experiments: sparse vs dense networks and Boruvka's parallel structure.

E1  Random connected networks, SPARSE (E = 4V, V = 250..8,000) and DENSE (complete graphs, V = 25..400).
    Kruskal (merge sort + union-find), Prim (indexed binary heap), Prim (plain key array, the dense-graph variant;
    skipped on sparse graphs above V = 4,000) and Boruvka run on the same graph; all totals must agree. Evidence =
    counted elementary operations (comparisons, finds + pointer hops, heap operations, edge scans);
    secondary = median wall-clock time of 3 runs; plus the auxiliary memory (words) each data structure needs.
E2  Boruvka rounds: components before/after every round and edges scanned per round (each component's
    cheapest-edge search is independent = the work that can be done in parallel); rounds <= ceil(log2 V).
Writes results/t5_sparse_dense.csv, results/t5_boruvka_rounds.csv, results/t5_experiments.png
(+ a copy in ../../Report/Screenshots/t5_experiments.png).
Run:  py -3 mst_experiments.py
"""
import csv
import math
import os
import random
import shutil
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from mst_engines import boruvka, kruskal, prim, prim_array  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "..", "Report", "Screenshots")
SEED = 42
SPARSE_V = [250, 500, 1000, 2000, 4000, 8000]
DENSE_V = [25, 50, 100, 200, 400]
REPEATS = 3
ARRAY_LIMIT = 4000                                   # Prim-array skipped above this V on sparse graphs

ALGORITHMS = {                                           # name -> (function, counters that make up "work")
    "Kruskal": (kruskal, ("sort_comparisons", "finds", "pointer_hops")),
    "Prim-heap": (prim, ("heap_comparisons", "edge_scans")),
    "Prim-array": (prim_array, ("scan_comparisons", "edge_scans")),
    "Boruvka": (boruvka, ("edge_scans", "key_comparisons", "finds", "pointer_hops")),
}


def aux_memory_words(name, n, m):
    """Words of working storage beyond the input edge list (the data structure each algorithm maintains)."""
    return {"Kruskal": m + 2 * n,                        # sorted edge-index array + parent, rank
            "Prim-heap": 2 * (2 * m) + 5 * n,            # adjacency lists (v, w, id) + key, via, in_tree, heap, pos
            "Prim-array": 2 * (2 * m) + 3 * n,           # adjacency lists + key, via, in_tree (no heap)
            "Boruvka": 2 * n + n}[name]                  # parent, rank + cheapest[component] (edges scanned in place)


def random_connected(n, m, rng):
    """Random spanning tree (guarantees connectivity) + random extra distinct edges up to m."""
    if m >= n * (n - 1) // 2:
        return [(u, v, rng.randint(1, 10 ** 6)) for u in range(n) for v in range(u + 1, n)]
    seen, edges = set(), []
    for v in range(1, n):
        u = rng.randrange(v)
        seen.add((u, v))
        edges.append((u, v, rng.randint(1, 10 ** 6)))
    while len(edges) < m:
        a, b = sorted(rng.sample(range(n), 2))
        if (a, b) not in seen:
            seen.add((a, b))
            edges.append((a, b, rng.randint(1, 10 ** 6)))
    return edges


def measure(family, n, edges):
    rows, totals, rounds = [], set(), None
    for name, (fn, keys) in ALGORITHMS.items():
        if name == "Prim-array" and family == "sparse" and n > ARRAY_LIMIT:
            continue                                     # Theta(V^2) scans: 64 M operations at V = 8,000
        times = []
        for _ in range(REPEATS):
            t0 = time.perf_counter()
            res = fn(n, edges)
            times.append(time.perf_counter() - t0)
        totals.add(res.total)
        work = sum(res.ops[k] for k in keys)
        rows.append(dict(family=family, V=n, E=len(edges), algorithm=name, work=work,
                         median_ms=round(statistics.median(times) * 1000, 2),
                         aux_memory_words=aux_memory_words(name, n, len(edges)),
                         rounds=res.ops.get("rounds", ""), total=res.total))
        if name == "Boruvka":
            rounds = res.trace
    assert len(totals) == 1, f"algorithms disagree on {family} V={n}: {totals}"
    return rows, rounds


def write_csv(name, rows):
    with open(os.path.join(RES, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    rng = random.Random(SEED)
    print("TASK 5 - EXPERIMENTS: sparse vs dense networks, Boruvka rounds (seed 42, median of 3 runs)")
    print("=" * 112)
    all_rows, round_rows = [], []
    print(f"{'family':<7} {'V':>5} {'E':>7} | {'work: Kruskal':>13} {'Prim-heap':>10} {'Prim-array':>10} {'Boruvka':>10} | "
          f"{'ms: Kr':>7} {'P-heap':>7} {'P-arr':>7} {'Bor':>7} | rnd lg V")
    for family, sizes in (("sparse", SPARSE_V), ("dense", DENSE_V)):
        for n in sizes:
            m = 4 * n if family == "sparse" else n * (n - 1) // 2
            edges = random_connected(n, m, rng)
            rows, trace = measure(family, n, edges)
            all_rows += rows
            by = {r["algorithm"]: r for r in rows}
            print(f"{family:<7} {n:>5} {len(edges):>7} | " +
                  " ".join(f"{by[a]['work'] if a in by else '-':>{w}}" for a, w in zip(ALGORITHMS, (13, 10, 10, 10)))
                  + " | " + " ".join(f"{by[a]['median_ms']:>7.1f}" if a in by else f"{'-':>7}" for a in ALGORITHMS) +
                  f" | {by['Boruvka']['rounds']:>3} {math.ceil(math.log2(n)):>4}")
            if n in (SPARSE_V[-1], DENSE_V[-1]):
                for rnd, before, cheapest, added, after, scanned in trace:
                    round_rows.append(dict(family=family, V=n, round=rnd, components_before=before,
                                           independent_searches=len(cheapest), edges_added=len(added),
                                           components_after=after, edges_scanned=scanned,
                                           shrink_factor=round(before / after, 2)))
    print("(all algorithms returned the same total cost on every graph - checked by assertion; Prim-array is skipped")
    print(f" on sparse graphs with V > {ARRAY_LIMIT:,} because its V^2 minimum scans alone would be 64 M operations)")

    print("\nE2 Boruvka rounds - components shrink by a factor >= 2 per round; every component searches independently")
    print(f"{'family':<7} {'V':>5} {'round':>5} {'comp. before':>12} {'independent searches':>20} {'edges added':>11} "
          f"{'comp. after':>11} {'shrink':>6} {'edges scanned':>13}")
    for r in round_rows:
        print(f"{r['family']:<7} {r['V']:>5} {r['round']:>5} {r['components_before']:>12} "
              f"{r['independent_searches']:>20} {r['edges_added']:>11} {r['components_after']:>11} "
              f"{r['shrink_factor']:>6} {r['edges_scanned']:>13}")

    print("\nAuxiliary memory (words) at the largest sizes:")
    for family, n in (("sparse", SPARSE_V[-1]), ("dense", DENSE_V[-1])):
        sel = [r for r in all_rows if r["family"] == family and r["V"] == n]
        print(f"  {family:<6} V={n:<5} E={sel[0]['E']:<6} " +
              "  ".join(f"{r['algorithm']} {r['aux_memory_words']:,}" for r in sel))
    write_csv("t5_sparse_dense.csv", all_rows)
    write_csv("t5_boruvka_rounds.csv", round_rows)
    plot(all_rows, round_rows)


def plot(rows, round_rows):
    colors = {"Kruskal": "#1f77b4", "Prim-heap": "#d62728", "Prim-array": "#2ca02c", "Boruvka": "#9467bd"}
    fig, axes = plt.subplots(2, 2, figsize=(13, 9.5))
    for ax, family, title in ((axes[0][0], "sparse", "(a) Sparse networks, E = 4V"),
                              (axes[0][1], "dense", "(b) Dense networks, complete graph E = V(V-1)/2")):
        for a in ALGORITHMS:
            sel = [r for r in rows if r["family"] == family and r["algorithm"] == a]
            ax.loglog([r["V"] for r in sel], [r["work"] for r in sel], "o-", color=colors[a], label=a)
        sel = [r for r in rows if r["family"] == family and r["algorithm"] == "Kruskal"]
        ref = [r["E"] * math.log2(r["V"]) for r in sel]
        scale = sel[-1]["work"] / ref[-1]
        ax.loglog([r["V"] for r in sel], [x * scale for x in ref], "k--", lw=1, label="E log₂ V (scaled)")
        if family == "dense":
            ax.loglog([r["V"] for r in sel], [r["V"] ** 2 for r in sel], "k:", lw=1, label="V² (unscaled)")
        ax.set_title(title)
        ax.set_xlabel("number of facilities V")
        ax.set_ylabel("counted elementary operations")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
    ax = axes[1][0]
    for family, mk in (("sparse", "o-"), ("dense", "s-")):
        sel = [r for r in round_rows if r["family"] == family]
        xs = [0] + [r["round"] for r in sel]
        ys = [sel[0]["components_before"]] + [r["components_after"] for r in sel]
        ax.semilogy(xs, [max(y, 0.8) for y in ys], mk, label=f"Boruvka, {family} V={sel[0]['V']}")
        ax.semilogy(xs, [sel[0]["components_before"] / 2 ** x for x in xs], ":", color="grey")
    ax.set_title("(c) Boruvka: components after each round (dotted = V / 2^round bound)")
    ax.set_xlabel("round")
    ax.set_ylabel("number of components (log)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    ax = axes[1][1]
    for family, ls in (("sparse", "-"), ("dense", "--")):
        for a in ALGORITHMS:
            sel = [r for r in rows if r["family"] == family and r["algorithm"] == a]
            ax.loglog([r["E"] for r in sel], [r["median_ms"] for r in sel], ls, marker="o", ms=3,
                      color=colors[a], label=f"{a} ({family})")
    ax.set_title("(d) Median wall-clock time (secondary evidence)")
    ax.set_xlabel("number of links E")
    ax.set_ylabel("time (ms)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    fig.suptitle("Task 5 - Kruskal vs Prim vs Boruvka on sparse and dense networks", fontweight="bold")
    fig.tight_layout()
    path = os.path.join(RES, "t5_experiments.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    shutil.copy(path, os.path.join(SHOTS, "t5_experiments.png"))


if __name__ == "__main__":
    main()
