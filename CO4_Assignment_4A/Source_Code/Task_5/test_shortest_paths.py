"""
test_shortest_paths.py - cross-checks Dijkstra, Bellman-Ford and Floyd (Task 5) on the given graph and on
random graphs.  Reference: Floyd vs Bellman-Ford vs Dijkstra agreement, and brute-force enumeration of all
simple paths on small graphs.  Prints PASS/FAIL lines and a RESULT line.
"""
import random

from floyd_all_pairs import floyd
from graph_common import INF, read_graph
from single_source import bellman_ford, dijkstra


def brute_simple_paths(vertices, edges, s):
    """Shortest simple-path length from s to every vertex by DFS over all simple paths."""
    adj = {v: [] for v in vertices}
    for u, v, w in edges:
        adj[u].append((v, w))
    best = {v: INF for v in vertices}

    def dfs(u, d, seen):
        best[u] = min(best[u], d)
        for v, w in adj[u]:
            if v not in seen:
                dfs(v, d + w, seen | {v})
    dfs(s, 0, {s})
    return best


def random_graph(n, m, lo, hi):
    V = [chr(65 + i) for i in range(n)]
    E = {}
    m = min(m, n * (n - 1))                      # cannot have more distinct directed edges than n(n-1)
    while len(E) < m:
        u, v = random.sample(V, 2)
        E[(u, v)] = random.randint(lo, hi)
    return V, [(u, v, w) for (u, v), w in E.items()]


def main():
    random.seed(42)
    passed = total = 0

    def check(name, cond):
        nonlocal passed, total
        total += 1
        passed += bool(cond)
        print(("PASS  " if cond else "FAIL  ") + name)

    V, E = read_graph()
    d, p = dijkstra(V, E, "A")
    check("Dijkstra from A: B 4, C 6, D 7, E 10", [d[v] for v in "BCDE"] == [4, 6, 7, 10])
    check("predecessors: B<-A, C<-B, D<-C, E<-D", [p[v] for v in "BCDE"] == ["A", "B", "C", "D"])
    bd, _, cyc = bellman_ford(V, E, "A")
    check("Bellman-Ford gives the same distances, no negative cycle", bd == d and cyc is None)
    D, _ = floyd(V, E)
    check("Floyd row A = Dijkstra distances", D[0] == [d[v] for v in V])
    check("Floyd B->E = 6, C->E = 4, E->A = inf", D[1][4] == 6 and D[2][4] == 4 and D[4][0] == INF)
    check("brute-force simple paths from A agree", brute_simple_paths(V, E, "A") == d)
    nd, _ = dijkstra(["A", "B", "C"], [("A", "B", 2), ("A", "C", 4), ("C", "B", -3)], "A")
    nb, _, _ = bellman_ford(["A", "B", "C"], [("A", "B", 2), ("A", "C", 4), ("C", "B", -3)], "A")
    check("negative edge: Dijkstra B = 2 (wrong), Bellman-Ford B = 1 (correct)", nd["B"] == 2 and nb["B"] == 1)
    _, _, cyc = bellman_ford(V, E + [("C", "B", -4)], "A")
    check("adding C->B = -4 creates cycle B->C->B of weight -2: detected", cyc is not None)
    _, _, cyc = bellman_ford(V, E + [("C", "B", -2)], "A")
    check("adding C->B = -2 (cycle weight 0): NOT reported as negative cycle", cyc is None)
    bad = 0
    for _ in range(200):
        Vr, Er = random_graph(random.randint(2, 7), random.randint(1, 15), 0, 20)
        s = Vr[0]
        dd, _ = dijkstra(Vr, Er, s)
        bb, _, _ = bellman_ford(Vr, Er, s)
        DD, _ = floyd(Vr, Er)
        if not (dd == bb == brute_simple_paths(Vr, Er, s) and DD[0] == [dd[v] for v in Vr]):
            bad += 1
    check("200 random non-negative graphs: Dijkstra = Bellman-Ford = Floyd row = brute force", bad == 0)
    bad = 0
    for _ in range(200):
        n = random.randint(2, 6)
        Vr = [chr(65 + i) for i in range(n)]
        Er = [(Vr[i], Vr[j], random.randint(-5, 10)) for i in range(n) for j in range(i + 1, n)
              if random.random() < 0.6]                            # DAG -> negative edges but no cycles
        bb, _, cyc = bellman_ford(Vr, Er, Vr[0])
        DD, _ = floyd(Vr, Er)
        if cyc is not None or bb != brute_simple_paths(Vr, Er, Vr[0]) or DD[0] != [bb[v] for v in Vr]:
            bad += 1
    check("200 random DAGs with negative edges: Bellman-Ford = Floyd = brute force, no false cycle", bad == 0)
    print(f"RESULT: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
