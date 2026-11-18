"""
Task 4 - experiments for the fibre-backbone MST.

E1  Sparse vs dense networks: Prim (indexed heap), Prim (array) and Kruskal (sort + union-find) on random
    connected graphs - sparse E = 4V (V = 1,000..16,000; the V^2 array version only up to 8,000) and
    dense = complete graphs E = V(V-1)/2 (V = 100..800).
    Every run must give the same total weight (validation); counted operations are the primary evidence.
E2  Union-find optimisation inside Kruskal: naive vs union by rank vs rank + path compression on two
    adversarial networks (a chain, and a binomial merge pattern).
Writes results/task4_*.csv and results/task4_experiments.png.
Run:  py -3 task4_experiments.py
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

from mst_prim_kruskal import kruskal, prim_array, prim_heap  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
SEED = 42


def write_csv(name, rows):
    with open(os.path.join(RES, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def random_connected(n, m, rng):
    """Random spanning tree (guarantees connectivity) plus random extra edges up to m distinct edges."""
    if m == n * (n - 1) // 2:                        # complete graph: every pair once
        return [(u, v, rng.randint(1, 1000)) for u in range(n) for v in range(u + 1, n)]
    seen, edges = set(), []
    for v in range(1, n):
        u = rng.randrange(v)
        seen.add((u, v))
        edges.append((u, v, rng.randint(1, 1000)))
    while len(edges) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v:
            continue
        a, b = min(u, v), max(u, v)
        if (a, b) not in seen:
            seen.add((a, b))
            edges.append((a, b, rng.randint(1, 1000)))
    return edges


def timed(fn, *args, **kw):
    ops = Counter()
    t0 = time.perf_counter()
    res = fn(*args, ops=ops, **kw)
    return res, ops, (time.perf_counter() - t0) * 1e3


def e1_sparse_dense():
    rng = random.Random(SEED)
    configs = [("sparse", v, 4 * v) for v in (1000, 2000, 4000, 8000, 16000)] + \
              [("dense", v, v * (v - 1) // 2) for v in (100, 200, 400, 800)]
    rows = []
    print("E1  Prim (heap), Prim (array) and Kruskal on sparse (E = 4V) and dense (complete) networks")
    print(f"    {'type':<6} {'V':>6} {'E':>7} | {'Prim-heap ops':>13} {'ms':>7} | {'Prim-array ops':>14} {'ms':>7} | "
          f"{'Kruskal ops':>11} {'ms':>7} | {'MST weight':>10} {'same':>4}")
    for kind, n, m in configs:
        edges = random_connected(n, m, rng)
        (_, wh, rh), oh, th = timed(prim_heap, n, edges)
        if n <= 8000:
            (_, wa, ra), oa, ta = timed(prim_array, n, edges)
        else:                                        # V^2 = 256 million scans: skipped (about 1 minute)
            (wa, ra), oa, ta = (wh, rh), None, None
        (_, wk, ck), ok, tk = timed(kruskal, n, edges)
        same = wh == wa == wk and rh == ra == n and ck == 1
        heap_ops = oh["heap_comparisons"] + oh["edge_checks"]
        arr_ops = oa["scan_comparisons"] + oa["edge_checks"] if oa else ""
        kr_ops = ok["sort_comparisons"] + ok["pointer_hops"] + ok["find_calls"]
        rows.append(dict(type=kind, V=n, E=len(edges), prim_heap_comparisons=oh["heap_comparisons"],
                         prim_heap_decrease_keys=oh["decrease_keys"], prim_heap_edge_checks=oh["edge_checks"],
                         prim_heap_ops=heap_ops, prim_heap_ms=round(th, 1),
                         prim_array_scans=oa["scan_comparisons"] if oa else "", prim_array_ops=arr_ops,
                         prim_array_ms=round(ta, 1) if oa else "",
                         kruskal_sort_comparisons=ok["sort_comparisons"], kruskal_finds=ok["find_calls"],
                         kruskal_hops=ok["pointer_hops"], kruskal_ops=kr_ops, kruskal_ms=round(tk, 1),
                         E_log2_V=round(len(edges) * math.log2(n)), V_squared=n * n, mst_weight=wh, same_weight=same))
        print(f"    {kind:<6} {n:>6,} {len(edges):>7,} | {heap_ops:>13,} {th:>7.1f} | {arr_ops if not oa else f'{arr_ops:,}':>14} {'' if not oa else f'{ta:.1f}':>7} | "
              f"{kr_ops:>11,} {tk:>7.1f} | {wh:>10,} {str(same):>4}")
    write_csv("task4_01_sparse_vs_dense.csv", rows)
    return rows


def adversarial(family, n):
    """Networks that stress union-find. The last site n is reachable only through the most expensive
    route, so Kruskal cannot stop early and must examine every edge.
    chain:    0-1-2-..-(n-1) cheap routes (a naive union builds one long path), then n routes (0, j)
              whose finds walk that path.
    binomial: routes (i, i + s) for s = 1, 2, 4, ... (union of equal-size trees: depth log2 n even with
              union by rank), then n routes between random sites (finds on deep nodes)."""
    rng = random.Random(SEED)
    if family == "chain":
        edges = [(i, i + 1, 1) for i in range(n - 1)] + [(0, rng.randrange(1, n), 2) for _ in range(n)]
    else:
        edges, step, w = [], 1, 1
        while step < n:
            edges += [(i, i + step, w) for i in range(0, n - step, 2 * step)]
            step, w = 2 * step, w + 1
        edges += [(rng.randrange(n), rng.randrange(n), w) for _ in range(n)]
    return edges + [(0, n, 10 ** 6)]


def e2_union_find(sizes=(1024, 2048, 4096, 8192)):
    rows = []
    print("\nE2  Union-find variants inside Kruskal on two adversarial networks (hops = parent links followed)")
    print(f"    {'network':<9} {'V':>6} {'finds':>7} | {'naive hops':>11} {'ms':>8} | {'rank hops':>10} {'ms':>7} | "
          f"{'rank+compress hops':>18} {'ms':>7} | {'same':>4}")
    for family in ("chain", "binomial"):
        for n in sizes:
            edges = adversarial(family, n)
            res = {}
            for mode in ("naive", "rank", "rank+compress"):
                (_, w, c), ops, t = timed(kruskal, n + 1, edges, mode=mode)
                res[mode] = (w, ops, t)
            same = len({r[0] for r in res.values()}) == 1
            rows.append(dict(network=family, V=n + 1, edges=len(edges), finds=res["naive"][1]["find_calls"],
                             naive_hops=res["naive"][1]["pointer_hops"], naive_ms=round(res["naive"][2], 1),
                             rank_hops=res["rank"][1]["pointer_hops"], rank_ms=round(res["rank"][2], 1),
                             rank_compress_hops=res["rank+compress"][1]["pointer_hops"],
                             rank_compress_ms=round(res["rank+compress"][2], 1), same_weight=same))
            print(f"    {family:<9} {n + 1:>6,} {res['naive'][1]['find_calls']:>7,} | "
                  f"{res['naive'][1]['pointer_hops']:>11,} {res['naive'][2]:>8.1f} | "
                  f"{res['rank'][1]['pointer_hops']:>10,} {res['rank'][2]:>7.1f} | "
                  f"{res['rank+compress'][1]['pointer_hops']:>18,} {res['rank+compress'][2]:>7.1f} | {str(same):>4}")
    write_csv("task4_02_union_find_variants.csv", rows)
    return rows


def plot(rows, uf_rows):
    fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.4))
    for i, kind in enumerate(("sparse", "dense")):
        rr = [r for r in rows if r["type"] == kind]
        v = [r["V"] for r in rr]
        ax[i].loglog(v, [r["prim_heap_ms"] for r in rr], "o-", label="Prim, binary heap")
        va = [r for r in rr if r["prim_array_ms"] != ""]
        ax[i].loglog([r["V"] for r in va], [r["prim_array_ms"] for r in va], "s-", label="Prim, array (V²)")
        ax[i].loglog(v, [r["kruskal_ms"] for r in rr], "^-", label="Kruskal, sort + union-find")
        ax[i].set_xlabel("number of sites V"); ax[i].set_ylabel("time (ms)")
        ax[i].set_title(f"E1: {kind} networks " + ("(E = 4V)" if kind == "sparse" else "(complete graphs)"))
        ax[i].legend(fontsize=8); ax[i].grid(True, which="both", alpha=0.3)
    for fam, mk in (("chain", "-"), ("binomial", "--")):
        rr = [r for r in uf_rows if r["network"] == fam]
        v = [r["V"] for r in rr]
        ax[2].loglog(v, [r["naive_hops"] for r in rr], "s" + mk, color="#C62828", label=f"naive, {fam}")
        ax[2].loglog(v, [r["rank_hops"] for r in rr], "o" + mk, color="#1565C0", label=f"rank, {fam}")
        ax[2].loglog(v, [r["rank_compress_hops"] for r in rr], "^" + mk, color="#2E7D32",
                     label=f"rank + compression, {fam}")
    v = sorted({r["V"] for r in uf_rows})
    ax[2].loglog(v, [x * x / 2 for x in v], "k:", lw=1, label="V²/2")
    ax[2].set_xlabel("number of sites V"); ax[2].set_ylabel("parent-pointer hops (count)")
    ax[2].set_title("E2: union-find variants (adversarial)"); ax[2].legend(fontsize=6.5)
    ax[2].grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "task4_experiments.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(RES, exist_ok=True)
    print("TASK 4 - EXPERIMENTS (seed 42)")
    print("=" * 118)
    rows = e1_sparse_dense()
    uf = e2_union_find()
    plot(rows, uf)
    print("\nWrote results/task4_01_sparse_vs_dense.csv, results/task4_02_union_find_variants.csv, "
          "results/task4_experiments.png")


if __name__ == "__main__":
    main()
