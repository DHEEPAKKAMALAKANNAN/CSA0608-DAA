"""
Task 4 - experiments: growth of Floyd's algorithm with the number of vertices n.

Random street networks (seed 42), n = 40, 80, 160, 320, about 4n streets. Two weight models:
  "positive" : travel times 1..100
  "negative" : the same streets re-weighted with vertex potentials h, w'(u,v) = w(u,v) + h(u) - h(v); this creates
               many negative streets but provably no negative cycle (every cycle keeps its original, positive cost)
Measured: comparisons (always n^3), improvements (updates), time (median of 3), negative edges, and agreement
with Bellman-Ford from 3 random sources. Outputs: results/floyd_growth.csv, ../../Report/Screenshots/task4_floyd_growth.png
Run:  py -3 floyd_experiments.py
"""
import csv
import os
import random
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from floyd_shortest_paths import INF, bellman_ford, floyd, negative_cycle_report  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.normpath(os.path.join(HERE, "..", "..", "Report", "Screenshots"))


def random_network(n, rng, negative):
    W = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    order = list(range(n))
    rng.shuffle(order)
    for a, b in zip(order, order[1:] + order[:1]):          # a Hamiltonian cycle keeps it strongly connected
        W[a][b] = rng.randint(1, 100)
    for _ in range(3 * n):
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            W[u][v] = rng.randint(1, 100)
    if negative:
        h = [rng.randint(0, 150) for _ in range(n)]
        W = [[W[u][v] + h[u] - h[v] if (u != v and W[u][v] < INF) else W[u][v] for v in range(n)] for u in range(n)]
    return W


def main():
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(SHOTS, exist_ok=True)
    rng = random.Random(42)
    rows = []
    print("=" * 108)
    print(" TASK 4 - EXPERIMENTS: FLOYD'S ALGORITHM, n = 40 ... 320 (random street networks, seed 42, median of 3)")
    print("=" * 108)
    hdr = (f"  {'weights':<9}{'n':>5}{'streets':>9}{'neg. streets':>13}{'comparisons':>13}{'= n^3?':>8}"
           f"{'updates':>10}{'updates/n^3':>13}{'time s':>9}{'neg. cycle':>11}{'= Bellman-Ford?':>16}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for model in ("positive", "negative"):
        for n in (40, 80, 160, 320):
            W = random_network(n, rng, model == "negative")
            m = sum(1 for u in range(n) for v in range(n) if u != v and W[u][v] < INF)
            neg = sum(1 for u in range(n) for v in range(n) if u != v and W[u][v] < 0)
            times = []
            for _ in range(3):
                t0 = time.perf_counter()
                D, P, ops = floyd(W)
                times.append(time.perf_counter() - t0)
            t = statistics.median(times)
            bad, _ = negative_cycle_report(D)
            sources = rng.sample(range(n), 3)
            agree = all(bellman_ford(W, s) == (D[s], False) for s in sources)
            rows.append({"weights": model, "n": n, "streets": m, "negative_streets": neg,
                         "comparisons": ops["comparisons"], "updates": ops["updates"], "time_s": t,
                         "negative_cycle": bool(bad), "bellman_ford_agrees": agree})
            print(f"  {model:<9}{n:>5}{m:>9}{neg:>13}{ops['comparisons']:>13}"
                  f"{'yes' if ops['comparisons'] == n ** 3 else 'NO':>8}{ops['updates']:>10}"
                  f"{ops['updates'] / n ** 3:>13.4f}{t:>9.3f}{'yes' if bad else 'no':>11}{'yes' if agree else 'NO':>16}")
    pos = [r for r in rows if r["weights"] == "positive"]
    g = [pos[i + 1]["time_s"] / pos[i]["time_s"] for i in range(len(pos) - 1)]
    print(f"\n  time ratio per doubling of n (positive weights): {', '.join(f'x{x:.1f}' for x in g)}"
          "   (Theta(n^3) predicts x8)")
    print("  negative streets do not change the work: the same n^3 comparisons, only the values differ")
    path = os.path.join(RESULTS, "floyd_growth.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
    ns = [r["n"] for r in pos]
    negr = [r for r in rows if r["weights"] == "negative"]
    ax1.loglog(ns, [r["comparisons"] for r in pos], "o-", label="comparisons (= n^3)")
    ax1.loglog(ns, [r["updates"] for r in pos], "s-", label="improvements, positive weights")
    ax1.loglog(ns, [r["updates"] for r in negr], "^--", label="improvements, with negative streets")
    ax1.set_title("Floyd: counted operations")
    ax1.set_xlabel("vertices n (log scale)")
    ax1.set_ylabel("operations (log scale)")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.loglog(ns, [r["time_s"] for r in pos], "o-", label="positive weights")
    ax2.loglog(ns, [r["time_s"] for r in negr], "s--", label="with negative streets")
    c3 = pos[-1]["time_s"] / ns[-1] ** 3
    ax2.loglog(ns, [c3 * n ** 3 for n in ns], "k:", label="theory c * n^3 (scaled)")
    ax2.set_title("Floyd: running time")
    ax2.set_xlabel("vertices n (log scale)")
    ax2.set_ylabel("time in seconds (log scale)")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    gpath = os.path.join(SHOTS, "task4_floyd_growth.png")
    fig.savefig(gpath, dpi=150)
    plt.close(fig)
    print("Saved:", os.path.relpath(path, HERE), "  Graph:", os.path.relpath(gpath, HERE))


if __name__ == "__main__":
    main()
