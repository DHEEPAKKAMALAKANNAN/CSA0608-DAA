"""
Task 3 - Boundary and failure tests of the routing engine (expected vs actual for each case).

Unreachable destinations, source = destination, a one-depot network, a zero-cost road, an unreachable
negative cycle (single-source vs all-pairs view), a negative self-loop, and invalid inputs that must be
rejected with a clear error instead of producing a route. Prints PASS/FAIL per case.
Run:  py -3 boundary_tests.py
"""
import os
import tempfile

from routing_engine import (Graph, NegativeCycleError, bellman_ford, dijkstra, floyd, load_edges, path_to,
                            shortest_paths, warshall)
from routing_io import base_network, fmt, print_header, route_text

RESULTS = []


def check(name, expected, actual):
    ok = expected == actual
    RESULTS.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name:<52} expected {str(expected):<26} actual {actual}")


def error_of(fn):
    try:
        fn()
        return "no error"
    except (ValueError, NegativeCycleError) as exc:
        return type(exc).__name__


def main():
    print_header("TASK 3 - BOUNDARY AND FAILURE TESTS")
    g, _ = base_network()
    p = g.vertex("P")
    dist, pred, order = dijkstra(g, "P")
    bf = bellman_ford(g, "P")
    unreachable = [g.names[v] for v in range(g.n) if dist[v] == float("inf")]
    check("B1 from Port P: unreachable depots", "HABCDEFG", "".join(unreachable))
    check("B1 P -> A path (no route, no crash)", "(no route)", route_text(g, path_to(pred, p, g.vertex("A"))))
    check("B1 Dijkstra = Bellman-Ford incl. inf entries", True, dist == bf.dist)
    h = g.vertex("H")
    d, pr, _ = dijkstra(g, "H")
    check("B2 source = destination H -> H", "0 H", f"{fmt(d[h])} {route_text(g, path_to(pr, h, h))}")

    one = Graph(["X"], [])
    check("B3 one-depot network: Dijkstra / Floyd / Warshall", "[0] [[0]] [[0]]",
          f"{dijkstra(one, 'X')[0]} {floyd(one).dist} {warshall(one)[0]}")
    zero = Graph(["S", "T", "U"], [("S", "T", 0), ("T", "U", 0), ("S", "U", 1)])
    zd, zp, _ = dijkstra(zero, "S")
    check("B4 zero-cost roads: S -> U", "0 S -> T -> U", f"{fmt(zd[2])} {route_text(zero, path_to(zp, 0, 2))}")

    iso = Graph(["S", "T", "X", "Y"], [("S", "T", 1), ("X", "Y", -1), ("Y", "X", -1)])
    check("B5 negative cycle X<->Y unreachable from S: BF", "no cycle, T=1",
          f"{'cycle' if bellman_ford(iso, 'S').has_negative_cycle else 'no cycle'}, T={fmt(bellman_ford(iso, 'S').dist[1])}")
    check("B5 ... but Floyd (all pairs) flags X and Y", "['X', 'Y']",
          str([iso.names[i] for i in floyd(iso).negative_vertices]))
    loop = Graph(["X"], [("X", "X", -1)])
    check("B6 negative self-loop detected by Bellman-Ford", "['X']",
          str([loop.names[v] for v in bellman_ford(loop, "X").negative_cycle]))

    check("F1 query for unknown depot 'Z'", "ValueError", error_of(lambda: dijkstra(g, "Z")))
    check("F2 road to an undeclared depot", "ValueError", error_of(lambda: Graph(["A"], [("A", "Q", 3)])))
    check("F3 duplicate road A->B", "ValueError", error_of(lambda: Graph(["A", "B"], [("A", "B", 1), ("A", "B", 2)])))
    check("F4 empty network", "ValueError", error_of(lambda: Graph([], [])))
    check("F5 non-numeric weight 'abc' in CSV", "ValueError", error_of(lambda: load_bad_csv("u,v,w\nA,B,abc\n")))
    check("F6 weight = infinity", "ValueError", error_of(lambda: Graph(["A", "B"], [("A", "B", float("inf"))])))
    cyc = g.with_extra_edges([("E", "C", -9)])
    check("F7 facade on negative-cycle network", "NegativeCycleError", error_of(lambda: shortest_paths(cyc, "H")))
    check("F8 facade on base network chooses", "Dijkstra", shortest_paths(g, "H")[0])
    print("=" * 112)
    print(f"RESULT: {sum(RESULTS)}/{len(RESULTS)} boundary/failure checks passed")


def load_bad_csv(text):
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    try:
        return load_edges(path)
    finally:
        os.remove(path)


if __name__ == "__main__":
    main()
