"""
Task 5 - experiments for Dijkstra ambulance routing.

E1  Validation: 300 random road networks (V = 30, E = 120, weights 0..20) - array Dijkstra, heap Dijkstra and
    Bellman-Ford must give identical distances for every junction; reconstructed routes must have exactly
    the reported length.
E2  Optimisation: array O(V^2) vs binary heap O((V + E) log V) on sparse road-like networks (E = 4V) and on
    dense networks (complete directed graphs, random and worst-case weights), counted operations + time.
Writes results/task5_*.csv and results/task5_array_vs_heap.png.
Run:  py -3 task5_experiments.py
"""
import csv
import math
import os
import random
import time
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from dijkstra_routing import INF, bellman_ford, dijkstra_array, dijkstra_heap, path_to  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
SEED = 42


def write_csv(name, rows):
    with open(os.path.join(RES, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def random_network(n, m, rng, wmax=60):
    """Directed network: a random two-way 'ring road' (keeps most junctions reachable) + random one-way roads."""
    if m >= n * (n - 1):                                    # complete directed graph
        return [(u, v, rng.randint(1, wmax)) for u in range(n) for v in range(n) if u != v]
    order = list(range(n))
    rng.shuffle(order)
    edges = []
    for i in range(n):
        a, b = order[i], order[(i + 1) % n]
        w = rng.randint(1, wmax)
        edges += [(a, b, w), (b, a, w)]
    while len(edges) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            edges.append((u, v, rng.randint(1, wmax)))
    return edges


def worst_case_dense(n):
    """Complete directed graph on which EVERY forward relaxation improves a distance: w(u, v) = 2(v - u) - 1
    for u < v gives dist[u] = u and makes dist[u] + w(u, v) = 2v - u - 1 strictly decreasing in u, so the
    heap receives about V^2 / 2 pushes (the O(E log V) worst case). Backward roads are very slow (10^6)."""
    return [(u, v, 2 * (v - u) - 1 if u < v else 10 ** 6) for u in range(n) for v in range(n) if u != v]


def e1_validation(trials=300, n=30, m=120):
    rng = random.Random(SEED)
    agree = routes_ok = unreachable = 0
    for _ in range(trials):
        edges = [(rng.randrange(n), rng.randrange(n), rng.randint(0, 20)) for _ in range(m)]
        s = rng.randrange(n)
        da, pa = dijkstra_array(n, edges, s)
        dh, ph = dijkstra_heap(n, edges, s)
        db, _, _ = bellman_ford(n, edges, s)
        agree += da == dh == db
        wmin = {}
        for u, v, w in edges:
            wmin[(u, v)] = min(w, wmin.get((u, v), INF))
        ok = True
        for t in range(n):
            if dh[t] == INF:
                unreachable += 1
                ok &= path_to(ph, s, t, dh) is None
                continue
            p = path_to(ph, s, t, dh)
            ok &= p[0] == s and p[-1] == t and sum(wmin[(a, b)] for a, b in zip(p, p[1:])) == dh[t]
        routes_ok += ok
    row = dict(trials=trials, V=n, E=m, all_three_agree=agree, routes_consistent=routes_ok,
               unreachable_pairs=unreachable)
    print(f"E1  Validation on {trials} random networks (V = {n}, E = {m}, weights 0..20, incl. zero weights)")
    print(f"    array = heap = Bellman-Ford on {agree}/{trials} networks; reconstructed routes consistent on "
          f"{routes_ok}/{trials};")
    print(f"    unreachable (source, junction) pairs handled correctly (dist inf, no route): {unreachable}")
    write_csv("task5_01_validation.csv", [row])
    return row


def e2_array_vs_heap():
    rng = random.Random(SEED)
    configs = [("sparse", v, 4 * v) for v in (500, 1000, 2000, 4000, 8000, 16000, 32000)] + \
              [("dense", v, v * (v - 1)) for v in (100, 200, 400, 800)] + \
              [("worst", v, v * (v - 1)) for v in (100, 200, 400, 800)]
    rows = []
    print("\nE2  Array O(V^2 + E) vs binary heap O((V + E) log V)")
    print(f"    {'type':<6} {'V':>6} {'E':>7} | {'array scans':>12} {'relax':>7} {'ms':>8} | {'heap cmp':>10} "
          f"{'pushes':>7} {'stale':>7} {'(V+E)log2V':>11} {'ms':>7} | {'speed-up':>8} {'same':>4}")
    for kind, n, m in configs:
        edges = worst_case_dense(n) if kind == "worst" else random_network(n, m, rng)
        s = 0
        ao = Counter()
        if n <= 8000:
            t0 = time.perf_counter(); da, _ = dijkstra_array(n, edges, s, ao); ta = (time.perf_counter() - t0) * 1e3
        else:
            da, ta = None, None
        best, ho = INF, None
        for _ in range(3):
            o = Counter()
            t0 = time.perf_counter(); dh, _ = dijkstra_heap(n, edges, s, o); th = (time.perf_counter() - t0) * 1e3
            if th < best:
                best, ho = th, o
        same = da is None or da == dh
        bound = (n + len(edges)) * math.log2(n)
        rows.append(dict(type=kind, V=n, E=len(edges), array_scan_comparisons=ao["scan_comparisons"] if da else "",
                         array_relaxations=ao["relaxations"] if da else "", array_ms=round(ta, 1) if da else "",
                         heap_comparisons=ho["heap_comparisons"], heap_pushes=ho["pushes"],
                         heap_stale_pops=ho["stale_pops"], heap_relaxations=ho["relaxations"],
                         V_plus_E_log2_V=round(bound), heap_ms=round(best, 1),
                         speedup=round(ta / best, 1) if da else "", same_distances=same))
        if da:
            a_scan, a_rel, a_ms = f"{ao['scan_comparisons']:,}", f"{ao['relaxations']:,}", f"{ta:.1f}"
            speed = f"{ta / best:.1f}x"
        else:                                                # V^2 >= 256 million scans: not run
            a_scan = a_rel = a_ms = speed = ""
        print(f"    {kind:<6} {n:>6,} {len(edges):>7,} | {a_scan:>12} {a_rel:>7} {a_ms:>8} | "
              f"{ho['heap_comparisons']:>10,} {ho['pushes']:>7,} {ho['stale_pops']:>7,} {round(bound):>11,} "
              f"{best:>7.1f} | {speed:>8} {str(same):>4}")
    write_csv("task5_02_array_vs_heap.csv", rows)
    return rows


def plot(rows):
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.3))
    titles = {"sparse": "sparse networks (E = 4V)", "dense": "dense, random weights (E = V(V−1))",
              "worst": "dense, worst-case weights (E = V(V−1))"}
    for i, kind in enumerate(("sparse", "dense", "worst")):
        rr = [r for r in rows if r["type"] == kind]
        ra = [r for r in rr if r["array_ms"] != ""]
        ax[i].loglog([r["V"] for r in ra], [r["array_ms"] for r in ra], "s-", label="array O(V² + E)")
        ax[i].loglog([r["V"] for r in rr], [r["heap_ms"] for r in rr], "o-", label="binary heap O((V+E) log V)")
        c = ra[-1]["array_ms"] / ra[-1]["V"] ** 2
        ax[i].loglog([r["V"] for r in rr], [c * r["V"] ** 2 for r in rr], "k:", lw=1, label="c·V² (scaled)")
        c2 = rr[-1]["heap_ms"] / rr[-1]["V_plus_E_log2_V"]
        ax[i].loglog([r["V"] for r in rr], [c2 * r["V_plus_E_log2_V"] for r in rr], "k--", lw=1,
                     label="c·(V+E) log₂ V (scaled)")
        ax[i].set_xlabel("number of junctions V"); ax[i].set_ylabel("time (ms)")
        ax[i].set_title("E2: " + titles[kind], fontsize=10)
        ax[i].legend(fontsize=8); ax[i].grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "task5_array_vs_heap.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(RES, exist_ok=True)
    print("TASK 5 - EXPERIMENTS (seed 42)")
    print("=" * 125)
    e1_validation()
    rows = e2_array_vs_heap()
    plot(rows)
    print("\nWrote results/task5_01_validation.csv, task5_02_array_vs_heap.csv, task5_array_vs_heap.png")


if __name__ == "__main__":
    main()
