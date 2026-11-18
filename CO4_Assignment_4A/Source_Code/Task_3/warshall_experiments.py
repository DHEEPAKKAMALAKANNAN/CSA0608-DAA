"""
Task 3 - experiments: growth of Warshall's algorithm with the number of vertices n.

Random digraphs (seed 42) with n = 40, 80, 160, 320 and edge probability 1.5/n (sparse, partly reachable) and
3/n (denser): inner steps of the plain triple loop (always n^3), inner steps of the row-skip version, row ORs of the
bitset version, times of all three (median of 3) and of the BFS reference; every closure is cross-checked.
Outputs: results/warshall_growth.csv, ../../Report/Screenshots/task3_warshall_growth.png
Run:  py -3 warshall_experiments.py
"""
import csv
import os
import random
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from warshall_closure import closure_bfs, warshall, warshall_bitset, warshall_row_skip  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.normpath(os.path.join(HERE, "..", "..", "Report", "Screenshots"))


def random_digraph(n, p, rng):
    return [[1 if (i != j and rng.random() < p) else 0 for j in range(n)] for i in range(n)]


def median_time(fn, A, repeats=3):
    times, res = [], None
    for _ in range(repeats):
        t0 = time.perf_counter()
        res = fn(A)
        times.append(time.perf_counter() - t0)
    return statistics.median(times), res


def main():
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    rng = random.Random(42)
    rows = []
    print("=" * 112)
    print(" TASK 3 - EXPERIMENTS: WARSHALL'S ALGORITHM, n = 40 ... 320 (random digraphs, seed 42, median of 3 runs)")
    print("=" * 112)
    hdr = (f"  {'n':>4}{'p*n':>5}{'edges':>7}{'closure 1s':>11}{'plain steps':>13}{'= n^3?':>8}{'skip steps':>12}"
           f"{'row ORs':>9}{'plain s':>9}{'skip s':>9}{'bitset s':>10}{'BFS s':>9}{'agree?':>8}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for c in (1.5, 3.0):
        for n in (40, 80, 160, 320):
            A = random_digraph(n, c / n, rng)
            edges = sum(map(sum, A))
            tp, (R, op) = median_time(warshall, A)
            ts, (Rs, osk) = median_time(warshall_row_skip, A)
            tb, (Rb, ob) = median_time(warshall_bitset, A)
            tq, Rq = median_time(closure_bfs, A)
            agree = R == Rs == Rb == Rq
            ones = sum(map(sum, R))
            rows.append({"n": n, "edge_factor": c, "edges": edges, "closure_ones": ones,
                         "plain_steps": op["inner_steps"], "skip_steps": osk["inner_steps"], "row_ors": ob["row_ors"],
                         "plain_s": tp, "skip_s": ts, "bitset_s": tb, "bfs_s": tq})
            print(f"  {n:>4}{c:>5}{edges:>7}{ones:>11}{op['inner_steps']:>13}"
                  f"{'yes' if op['inner_steps'] == n ** 3 else 'NO':>8}{osk['inner_steps']:>12}{ob['row_ors']:>9}"
                  f"{tp:>9.3f}{ts:>9.4f}{tb:>10.4f}{tq:>9.4f}{'yes' if agree else 'NO':>8}")
    dense = [r for r in rows if r["edge_factor"] == 3.0]
    g = [dense[i + 1]["plain_s"] / dense[i]["plain_s"] for i in range(len(dense) - 1)]
    print(f"\n  plain Warshall time ratio per doubling of n (p*n = 3): {', '.join(f'x{x:.1f}' for x in g)}"
          "  (Theta(n^3) predicts x8)")
    path = os.path.join(RESULTS, "warshall_growth.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    ns = [r["n"] for r in dense]
    ax1.loglog(ns, [r["plain_steps"] for r in dense], "o-", label="plain: inner steps (= n^3)")
    ax1.loglog(ns, [r["skip_steps"] for r in dense], "s-", label="row-skip: inner steps")
    ax1.loglog(ns, [r["row_ors"] for r in dense], "^-", label="bitset: row ORs")
    ax1.loglog(ns, [n ** 2 for n in ns], "k:", label="n^2 reference")
    ax1.set_title("Warshall: counted operations (p*n = 3)")
    ax1.set_xlabel("vertices n (log scale)")
    ax1.set_ylabel("operations (log scale)")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.loglog(ns, [r["plain_s"] for r in dense], "o-", label="plain triple loop")
    ax2.loglog(ns, [r["skip_s"] for r in dense], "s-", label="row-skip")
    ax2.loglog(ns, [r["bitset_s"] for r in dense], "^-", label="bitset rows")
    ax2.loglog(ns, [r["bfs_s"] for r in dense], "v-", label="BFS from every vertex")
    c3 = dense[-1]["plain_s"] / ns[-1] ** 3
    ax2.loglog(ns, [c3 * n ** 3 for n in ns], "k:", label="theory c * n^3 (scaled)")
    ax2.set_title("Warshall: running time (p*n = 3)")
    ax2.set_xlabel("vertices n (log scale)")
    ax2.set_ylabel("time in seconds (log scale)")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    gpath = os.path.join(SHOTS, "task3_warshall_growth.png")
    fig.savefig(gpath, dpi=150)
    plt.close(fig)
    print("Saved:", os.path.relpath(path, HERE), "  Graph:", os.path.relpath(gpath, HERE))


if __name__ == "__main__":
    main()
