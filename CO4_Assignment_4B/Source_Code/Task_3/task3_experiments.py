"""
Task 3 - Experiment: how much work does each routing algorithm do as the network grows?

Random directed networks (seed 42) with n depots and m = 4n roads, costs 1..20, a ring guarantees that every
depot is reachable. For each n the script counts basic operations (primary evidence) and times one run
(secondary evidence, noisy):
  Dijkstra (one source)         edge relaxations + heap comparisons      O((V + E) log V)
  Bellman-Ford (one source)     edge relaxations incl. detection pass    O(V E), early exit helps in practice
  n x Dijkstra (all pairs)      sum over all sources                     O(V (V + E) log V)
  Floyd (all pairs)             cell examinations = n^3                  Theta(V^3)
All single-source and all-pairs answers are checked to be identical.
Writes results/t3_operation_counts.csv and the graph ../../Report/Screenshots/t3_operation_counts.png.
Run:  py -3 task3_experiments.py
"""
import os
import random
import time
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from routing_engine import Graph, bellman_ford, dijkstra, floyd  # noqa: E402
from routing_io import RESULTS, write_csv  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "..", "Report", "Screenshots")
SIZES = [10, 20, 40, 80, 160, 320]


def random_network(n, rng):
    names = [f"V{i}" for i in range(n)]
    edges = {(i, (i + 1) % n): rng.randint(1, 20) for i in range(n)}
    while len(edges) < 4 * n:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v and (u, v) not in edges:
            edges[(u, v)] = rng.randint(1, 20)
    order = list(edges.items())
    rng.shuffle(order)                              # Bellman-Ford edge order is arbitrary, not topological
    return Graph(names, [(names[u], names[v], w) for (u, v), w in order])


def timed(fn):
    t = time.perf_counter()
    out = fn()
    return out, time.perf_counter() - t


def main():
    rng = random.Random(42)
    print("TASK 3 - OPERATION COUNTS OF THE FOUR ROUTING ALGORITHMS (m = 4n random roads, seed 42)")
    print("=" * 118)
    print(f"{'n':>5} {'m':>6} | {'Dijkstra ops':>12} {'BF ops':>10} {'BF passes':>9} | {'n x Dijkstra':>12} "
          f"{'Floyd ops':>11} | {'t_Dij ms':>8} {'t_BF ms':>8} {'t_nDij ms':>9} {'t_Floyd ms':>10} | agree")
    rows = []
    for n in SIZES:
        g = random_network(n, rng)
        do, bo, ao, fo = Counter(), Counter(), Counter(), Counter()
        (dd, _, _), t_d = timed(lambda: dijkstra(g, 0, do))
        bf, t_b = timed(lambda: bellman_ford(g, 0, bo))
        alld, t_a = timed(lambda: [dijkstra(g, s, ao)[0] for s in range(n)])
        fl, t_f = timed(lambda: floyd(g, fo, keep_snapshots=False))
        agree = dd == bf.dist and alld == fl.dist
        d_ops = do["edge_relaxations"] + do["heap_comparisons"]
        b_ops = bo["edge_relaxations"] + bo["detection_checks"]
        a_ops = ao["edge_relaxations"] + ao["heap_comparisons"]
        rows.append([n, len(g.edges), d_ops, b_ops, len(bf.pass_log), a_ops, fo["floyd_cells"],
                     round(t_d * 1e3, 3), round(t_b * 1e3, 3), round(t_a * 1e3, 2), round(t_f * 1e3, 2), agree])
        print(f"{n:>5} {len(g.edges):>6} | {d_ops:>12,} {b_ops:>10,} {len(bf.pass_log):>9} | {a_ops:>12,} "
              f"{fo['floyd_cells']:>11,} | {t_d * 1e3:>8.2f} {t_b * 1e3:>8.2f} {t_a * 1e3:>9.1f} {t_f * 1e3:>10.1f} | "
              f"{'yes' if agree else 'NO'}")
    path = write_csv("t3_operation_counts.csv", ["n", "m", "dijkstra_ops", "bellman_ford_ops", "bf_passes",
                                                 "n_dijkstra_ops", "floyd_ops", "t_dijkstra_ms", "t_bf_ms",
                                                 "t_n_dijkstra_ms", "t_floyd_ms", "all_agree"], rows)
    plot(rows)
    print(f"\nraw data: {os.path.relpath(path, HERE)}")
    print("Single source: Bellman-Ford needs several full passes over all m edges, Dijkstra touches each edge once.")
    print("All pairs on a sparse network: n x Dijkstra does less work than Floyd's n^3, but Floyd is simpler and")
    print("handles negative edges; on dense networks (m ~ n^2) the two converge.")


def plot(rows):
    ns = [r[0] for r in rows]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6))
    a1.loglog(ns, [r[2] for r in rows], "o-", label="Dijkstra (one source)")
    a1.loglog(ns, [r[3] for r in rows], "s-", label="Bellman-Ford (one source)")
    a1.loglog(ns, [r[5] for r in rows], "^-", label="n x Dijkstra (all pairs)")
    a1.loglog(ns, [r[6] for r in rows], "d-", label="Floyd (all pairs)")
    scale = rows[-1][6] / ns[-1] ** 3
    a1.loglog(ns, [scale * n ** 3 for n in ns], "k:", label="n³ (scaled)")
    a1.set_title("Basic operations vs network size (m = 4n)")
    a1.set_xlabel("number of depots n")
    a1.set_ylabel("basic operations (count)")
    a1.grid(True, which="both", alpha=0.3)
    a1.legend(fontsize=8)
    a2.loglog(ns, [r[7] for r in rows], "o-", label="Dijkstra")
    a2.loglog(ns, [r[8] for r in rows], "s-", label="Bellman-Ford")
    a2.loglog(ns, [r[9] for r in rows], "^-", label="n x Dijkstra")
    a2.loglog(ns, [r[10] for r in rows], "d-", label="Floyd")
    a2.set_title("Wall-clock time (secondary evidence)")
    a2.set_xlabel("number of depots n")
    a2.set_ylabel("time (ms)")
    a2.grid(True, which="both", alpha=0.3)
    a2.legend(fontsize=8)
    fig.tight_layout()
    os.makedirs(SHOTS, exist_ok=True)
    for path in (os.path.join(RESULTS, "t3_operation_counts.png"), os.path.join(SHOTS, "t3_operation_counts.png")):
        fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
