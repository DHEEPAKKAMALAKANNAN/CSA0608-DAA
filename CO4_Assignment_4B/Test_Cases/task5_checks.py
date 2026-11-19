"""
Task 5 checker for run_all_tests.py: run_case(case) -> (expected, actual, ok).
Implementation under test: ../Source_Code/Task_5/mst_engines.py (Kruskal, Prim, Prim-array, Boruvka).
References: brute force over all spanning trees, enumeration of all MSTs, cut and cycle properties.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(HERE, "..", "Source_Code", "Task_5")
sys.path.insert(0, TASK_DIR)

import mst_engines as m  # noqa: E402


def load(name):
    return m.Network.from_csv(os.path.join(TASK_DIR, "test_data", name))


def three(net):
    return m.kruskal(net.n, net.edges), m.prim(net.n, net.edges, 0), m.boruvka(net.n, net.edges)


def random_graph(n, mcount, rng, wmax=1000):
    """Random connected graph: random spanning tree + random extra edges (duplicates of a pair avoided)."""
    if mcount >= n * (n - 1) // 2:
        return [(u, v, rng.randint(1, wmax)) for u in range(n) for v in range(u + 1, n)]
    seen, edges = set(), []
    for v in range(1, n):
        u = rng.randrange(v)
        seen.add((u, v))
        edges.append((u, v, rng.randint(1, wmax)))
    while len(edges) < mcount:
        a, b = sorted(rng.sample(range(n), 2))
        if (a, b) not in seen:
            seen.add((a, b))
            edges.append((a, b, rng.randint(1, wmax)))
    return edges


def expect_error(case, build):
    try:
        res = build()
        return case["expect"], f"no error: {res}", False
    except Exception as exc:                                       # noqa: BLE001
        return case["expect"], type(exc).__name__, type(exc).__name__ == case["expect"]["error"]


def run_case(case):
    ex, ty = case["expect"], case["type"]
    if ty == "file":
        net = load(case["file"])
        runs = three(net)
        same = len({m.canonical(r.edges) for r in runs}) == 1
        costs = [r.total for r in runs]
        ok = all(c == ex["cost"] for c in costs) and all(len(r.edges) == ex["edges"] for r in runs) \
            and same == ex["same_edges"]
        return ex, f"costs {costs}, same edges {same}", ok
    if ty == "construction_order":
        net = load(case["file"])
        kr, pr, br = three(net)
        got = (net.edge_label(kr.edges[0]), net.edge_label(pr.edges[0]), br.ops["rounds"])
        return ex, f"first {got[0]} / {got[1]}, {got[2]} rounds", \
            got == (ex["kruskal_first"], ex["prim_first"], ex["boruvka_rounds"])
    if ty == "bruteforce_file":
        net = load(case["file"])
        best, n_msts, n_trees = m.mst_bruteforce(net.n, net.edges)
        return ex, f"min {best}, {n_msts} MST of {n_trees} trees", (best, n_msts) == (ex["cost"], ex["msts"])
    if ty == "random_vs_bruteforce":
        rng, bad = random.Random(case["seed"]), 0
        for _ in range(case["trials"]):
            edges = random_graph(case["n"], case["m"], rng, wmax=6)       # small weights -> many ties
            best = m.mst_bruteforce(case["n"], edges)[0]
            bad += any(r.total != best for r in three(m.Network([str(i) for i in range(case["n"])], edges)))
        return ex, f"{case['trials'] - bad}/{case['trials']} agree", bad == 0
    if ty == "properties_random":
        rng, bad = random.Random(case["seed"]), 0
        for _ in range(case["trials"]):
            n = case["n"]
            edges = random_graph(n, case["m"], rng, wmax=20)
            for r in three(m.Network([str(i) for i in range(n)], edges)):
                bad += not (m.is_spanning_tree(n, r.edges) and m.cut_property_holds(n, edges, r.edges)
                            and m.cycle_property_holds(n, edges, r.edges))
        return ex, f"{3 * case['trials'] - bad}/{3 * case['trials']} trees valid", bad == 0
    if ty == "ties":
        net = load(case["file"])
        runs = three(net)
        best, msts = m.enumerate_msts(net.n, net.edges)
        distinct = len({m.canonical(r.edges) for r in runs})
        all_in = all(m.canonical(r.edges) in msts for r in runs)
        ok = best == ex["cost"] and len(msts) == ex["msts"] and distinct == ex["distinct_sets"] and all_in \
            and all(r.total == best for r in runs)
        return ex, f"{len(msts)} MSTs, {distinct} distinct returned, cost {best}", ok
    if ty == "prim_roots":
        net = load(case["file"])
        runs = [m.prim(net.n, net.edges, r) for r in range(net.n)]
        trees = {m.canonical(r.edges) for r in runs}
        ok = len(trees) == ex["distinct_trees"] and all(r.total == ex["cost"] for r in runs)
        return ex, f"{len(trees)} trees, costs {sorted({r.total for r in runs})}", ok
    if ty == "small":
        net = m.Network(case["names"], [tuple(e) for e in case["edges"]])
        runs = three(net)
        best = m.mst_bruteforce(net.n, net.edges)[0]
        ok = all(r.total == ex["cost"] == best and len(r.edges) == ex["edges"] for r in runs)
        return ex, f"costs {[r.total for r in runs]}, brute {best}", ok
    if ty == "disconnected":
        net = load(case["file"])
        kr, pr, br = three(net)
        ok = kr.components == br.components == ex["components"] and kr.total == br.total == ex["forest_cost"]
        try:
            m.require_spanning_tree(kr)
            err = "none"
        except ValueError:
            err = "ValueError"
        ok = ok and err == ex["error"] and pr.components > 1
        return ex, f"{kr.components} comps, forest {kr.total}, policy {err}", ok
    if ty == "invalid":
        edges = [tuple(float(x) if x == "NaN" else x for x in e) for e in case["edges"]]
        return expect_error(case, lambda: m.Network(case["names"], edges))
    if ty == "large":
        rng = random.Random(case["seed"])
        n = case["n"]
        edges = random_graph(n, case["m"], rng, wmax=10 ** 6)
        costs = [m.kruskal(n, edges).total, m.prim(n, edges).total, m.boruvka(n, edges).total]
        if n <= 1000:
            costs.append(m.prim_array(n, edges).total)
        return ex, f"all = {costs[0]:,}" if len(set(costs)) == 1 else str(costs), len(set(costs)) == 1
    raise ValueError(f"unknown case type {ty}")
