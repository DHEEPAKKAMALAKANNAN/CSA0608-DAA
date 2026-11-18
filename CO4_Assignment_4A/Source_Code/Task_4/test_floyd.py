"""
Task 4 - test suite for floyd_shortest_paths.py.

* Table-driven networks from test_data/floyd_test_cases.csv (given + own + boundary) with hand-derived distance
  matrices or the expected negative-cycle verdict.
* Path reconstruction: every reconstructed path is a real street sequence whose cost equals D[i][j].
* 200 random networks with negative streets but no negative cycle vs Bellman-Ford from every source;
  200 random networks, negative cycles possible: Floyd's verdict = Bellman-Ford's verdict.
Prints PASS/FAIL lines and "RESULT: k/k tests passed".   Run:  py -3 test_floyd.py
"""
import csv
import os
import random

from floyd_shortest_paths import (INF, bellman_ford, floyd, load_graph, negative_cycle_report, path_cost,
                                  reconstruct_path)

HERE = os.path.dirname(os.path.abspath(__file__))
results = []


def check(name, condition, detail=""):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


def build(n, edges):
    W = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for e in filter(None, edges.split(";")):
        uv, w = e.split(":")
        u, v = map(int, uv.split("-"))
        W[u][v] = int(w)
    return W


def has_negative_cycle_bf(W):
    """Bellman-Ford from a virtual source joined to every vertex with weight 0."""
    n = len(W)
    dist = [0] * n
    edges = [(u, v, W[u][v]) for u in range(n) for v in range(n) if W[u][v] < INF and (u != v or W[u][v] < 0)]
    for _ in range(n):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return any(dist[u] + w < dist[v] for u, v, w in edges)


def paths_valid(W, D, P):
    n = len(W)
    for i in range(n):
        for j in range(n):
            path = reconstruct_path(P, i, j)
            if D[i][j] == INF:
                if path:
                    return False
            elif path[0] != i or path[-1] != j or path_cost(W, path) != D[i][j]:
                return False
    return True


def table_cases():
    with open(os.path.join(HERE, "test_data", "floyd_test_cases.csv"), encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            n = int(row["n"])
            W = build(n, row["edges"])
            D, P, ops = floyd(W)
            bad, _ = negative_cycle_report(D)
            if row["negative_cycle"] == "yes":
                ok = bool(bad) and has_negative_cycle_bf(W)
                detail = f"negative cycle detected through {len(bad)} vertices"
            else:
                exp = [[INF if x == "i" else int(x) for x in r.split()] for r in row["expected_distances"].split("/")] \
                    if n else []
                ok = D == exp and not bad and paths_valid(W, D, P) and ops["comparisons"] == n ** 3
                detail = "distances, paths and n^3 comparisons correct"
            check(f"{row['case_id']:<4}({row['category']:<8}) n={n} {row['description']}", ok, detail)


def potential_network(n, rng):
    W = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for _ in range(rng.randint(0, n * n)):
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            W[u][v] = rng.randint(0, 20)
    h = [rng.randint(0, 30) for _ in range(n)]
    return [[W[u][v] + h[u] - h[v] if (u != v and W[u][v] < INF) else W[u][v] for v in range(n)] for u in range(n)]


def property_tests():
    labels, W = load_graph("road_network.csv")
    D, P, ops = floyd(W)
    check("road network: route E -> A is E-B-C-D-A with 17 minutes",
          reconstruct_path(P, 4, 0) == [4, 1, 2, 3, 0] and D[4][0] == 17)
    check("road network: improvements per k = [2, 5, 5, 7, 3] and 125 comparisons",
          ops["updates_per_k"] == [2, 5, 5, 7, 3] and ops["comparisons"] == 125)
    rng = random.Random(42)
    ok_bf, ok_paths = True, True
    for _ in range(200):
        n = rng.randint(1, 9)
        Wr = potential_network(n, rng)
        Dr, Pr, _ = floyd(Wr)
        ok_bf &= all(bellman_ford(Wr, s) == (Dr[s], False) for s in range(n))
        ok_paths &= paths_valid(Wr, Dr, Pr)
    check("200 random networks with negative streets (no negative cycle): Floyd = Bellman-Ford, all sources", ok_bf)
    check("200 random networks: every reconstructed path is valid and costs exactly D[i][j]", ok_paths)
    agree, cycles = True, 0
    for _ in range(200):
        n = rng.randint(1, 7)
        Wr = [[0 if i == j else INF for j in range(n)] for i in range(n)]
        for _ in range(rng.randint(0, 2 * n)):
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v:
                Wr[u][v] = rng.randint(-10, 20)
        verdict = bool(negative_cycle_report(floyd(Wr)[0])[0])
        cycles += verdict
        agree &= verdict == has_negative_cycle_bf(Wr)
    check("200 random networks, negative cycles possible: Floyd's verdict = Bellman-Ford's", agree,
          f"{cycles} networks had a negative cycle")
    Wc = [[0, 3], [INF, 0]]
    floyd(Wc)
    check("input weight matrix is not modified", Wc == [[0, 3], [INF, 0]])
    try:
        floyd([[0, 1], [1]])
        ok = False
    except ValueError:
        ok = True
    check("non-square weight matrix rejected with ValueError", ok)


def main():
    print("Task 4 - Floyd's algorithm: test run")
    table_cases()
    property_tests()
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
