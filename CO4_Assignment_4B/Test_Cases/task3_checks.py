"""
Checker for Task 3 test cases (task3_test_cases.json): routing engine in ../Source_Code/Task_3.

run_case(case) -> (expected, actual, ok). Independent references: Bellman-Ford and Floyd cross-check Dijkstra,
exhaustive enumeration of simple paths checks Bellman-Ford/Floyd on graphs with negative edges, breadth-first
search checks Warshall, and Floyd's negative diagonal checks Bellman-Ford's negative-cycle detection.
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Source_Code", "Task_3"))

from routing_engine import (INF, Graph, NegativeCycleError, bellman_ford, bfs_reachable, dijkstra,  # noqa: E402
                            floyd, floyd_path, path_cost, path_to, shortest_paths, warshall)
from routing_io import base_network, modified_network  # noqa: E402


def names_of(g, vs):
    return "".join(g.names[v] for v in vs)


def route(g, pred, s, t):
    return "-".join(g.names[v] for v in path_to(pred, s, t))


def random_graph(rng, n, m, lo, hi, dag=False):
    names = [f"V{i}" for i in range(n)]
    edges = {}
    while len(edges) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v or (dag and u > v):
            continue
        edges[(u, v)] = rng.randint(lo, hi)
    return Graph(names, [(names[u], names[v], w) for (u, v), w in edges.items()])


def enumerate_best(g, s):
    """Reference: minimum over ALL simple paths from s (exhaustive DFS)."""
    best = [INF] * g.n
    best[s] = 0

    def dfs(u, cost, seen):
        for v, w in g.adj[u]:
            if v not in seen:
                best[v] = min(best[v], cost + w)
                seen.add(v)
                dfs(v, cost + w, seen)
                seen.remove(v)
    dfs(s, 0, {s})
    return best


def error_name(fn):
    try:
        fn()
        return "no error"
    except (ValueError, NegativeCycleError) as exc:
        return type(exc).__name__


def run_case(case):
    t, ex = case["type"], case["expect"]
    g, _ = base_network()
    h = g.vertex("H")
    if t == "stage_a_dist":
        dist = dijkstra(g, "H")[0]
        actual = {g.names[v]: dist[v] for v in range(g.n)}
        return ex, actual, actual == ex
    if t == "stage_a_order":
        actual = names_of(g, dijkstra(g, "H")[2])
        return ex, actual, actual == ex
    if t == "stage_a_path":
        dist, pred, _ = dijkstra(g, "H")
        tv = g.vertex(case["target"])
        actual = f"{route(g, pred, h, tv)} {dist[tv]}"
        return ex, actual, actual == ex and path_cost(g, path_to(pred, h, tv)) == dist[tv]
    if t.startswith("stage_b") or t == "facade_switch":
        gb, _ = modified_network("stage_b_negative_edge.csv")
        trace = []
        dd, _, _ = dijkstra(gb, "H", trace=trace)
        bf = bellman_ford(gb, "H")
        r = gb.vertex("R")
        if t == "stage_b_wrong":
            actual = names_of(gb, [v for v in range(gb.n) if dd[v] != bf.dist[v]])
        elif t == "stage_b_refused":
            k, step = next((k, st) for k, st in enumerate(trace, 1) if st["refused"])
            v, cand, final = step["refused"][0]
            actual = f"step {k}: {gb.names[v]} offered {cand} < final {final}"
        elif t == "stage_b_bf":
            actual = f"{route(gb, bf.pred, h, r)} {bf.dist[r]}"
        else:
            algo, dist, _ = shortest_paths(gb, "H")
            actual = f"{algo} {dist[r]}"
        return ex, actual, actual == ex
    if t == "stage_c_cycle":
        gc, _ = modified_network("stage_c_negative_cycle.csv")
        res = bellman_ford(gc, "H")
        actual = f"{''.join(sorted(gc.names[v] for v in res.negative_cycle))} {res.cycle_weight} {len(res.affected)}"
        no_finite_lie = all(res.dist[v] == -INF for v in res.affected)
        return ex, actual, actual == ex and no_finite_lie
    if t == "stage_c_facade":
        gc, _ = modified_network("stage_c_negative_cycle.csv")
        actual = error_name(lambda: shortest_paths(gc, "H"))
        return ex, actual, actual == ex
    if t == "error":
        fn = {"unknown_vertex": lambda: dijkstra(g, "Z"),
              "duplicate_edge": lambda: Graph(["A", "B"], [("A", "B", 1), ("A", "B", 2)]),
              "unknown_endpoint": lambda: Graph(["A"], [("A", "Q", 1)]),
              "empty": lambda: Graph([], [])}[case["error_case"]]
        actual = error_name(fn)
        return ex, actual, actual == ex
    if t == "unreachable":
        p = g.vertex("P")
        dist, pred, _ = dijkstra(g, "P")
        reach = [v for v in range(g.n) if dist[v] < INF and v != p]
        unreach = [v for v in range(g.n) if dist[v] == INF]
        actual = f"{names_of(g, reach)} reachable, {len(unreach)} unreachable"
        ok = actual == ex and all(path_to(pred, p, v) == [] for v in unreach)
        return ex, actual, ok
    if t == "single_vertex":
        one = Graph(["X"], [])
        bf = bellman_ford(one, "X")
        actual = (f"{dijkstra(one, 'X')[0][0]} {floyd(one).dist} {warshall(one)[0]} "
                  f"{'cycle' if bf.has_negative_cycle else 'no cycle'}")
        return ex, actual, actual == ex
    if t == "isolated_cycle":
        iso = Graph(["S", "T", "X", "Y"], [("S", "T", 1), ("X", "Y", -1), ("Y", "X", -1)])
        bf = bellman_ford(iso, "S")
        actual = (f"BF {'cycle' if bf.has_negative_cycle else 'no cycle'}, Floyd "
                  f"{names_of(iso, floyd(iso).negative_vertices)}")
        return ex, actual, actual == ex
    rng = random.Random(case.get("seed", 0))
    trials, good = case.get("trials", 0), 0
    if t == "random_nonneg":
        for _ in range(trials):
            n = rng.randint(2, 12)
            gr = random_graph(rng, n, rng.randint(0, n * (n - 1) // 2), 0, 25)
            fl = floyd(gr, keep_snapshots=False)
            good += all(dijkstra(gr, s)[0] == bellman_ford(gr, s).dist == fl.dist[s] for s in range(n))
    elif t == "random_negative_dag":
        for _ in range(trials):
            n = rng.randint(2, 8)
            gr = random_graph(rng, n, rng.randint(1, n * (n - 1) // 2), -10, 15, dag=True)
            fl = floyd(gr, keep_snapshots=False)
            good += all(bellman_ford(gr, s).dist == fl.dist[s] == enumerate_best(gr, s) for s in range(n))
    elif t == "random_cycle_detect":
        for _ in range(trials):
            n = rng.randint(2, 9)
            gr = random_graph(rng, n, rng.randint(1, n * (n - 1)), -6, 12)
            fl = floyd(gr, keep_snapshots=False)
            reach = bfs_reachable(gr, 0) | {0}
            truth = any(fl.dist[v][v] < 0 for v in reach)
            good += bellman_ford(gr, 0).has_negative_cycle == truth
    elif t == "random_warshall":
        for _ in range(trials):
            n = rng.randint(1, 12)
            gr = random_graph(rng, n, rng.randint(0, n * (n - 1)), 1, 9)
            closure = warshall(gr)[0]
            good += all({j for j in range(n) if closure[i][j]} == bfs_reachable(gr, i) for i in range(n))
    elif t == "floyd_paths":
        fl = floyd(g, keep_snapshots=False)
        for i in range(g.n):
            for j in range(g.n):
                rt = floyd_path(fl.nxt, i, j)
                good += (fl.dist[i][j] == INF and rt == []) or (rt and path_cost(g, rt) == fl.dist[i][j])
        actual = f"{good}/{g.n * g.n} pairs consistent"
        return ex, actual, actual == ex
    elif t == "stage_d":
        fl = floyd(g, keep_snapshots=False)
        actual = f"{','.join(str(x) for x in fl.dist[h])} | {sum(map(sum, warshall(g)[0]))}"
        return ex, actual, actual == ex
    else:
        raise ValueError(f"unknown case type {t}")
    actual = f"{good}/{trials} agree"
    return ex, actual, actual == ex
