"""
Task 3, Stage A - Normal routing with Dijkstra's algorithm.

Input : test_data/depots.csv + base_network.csv (10 depots, 19 one-way roads, all costs >= 0), source H.
Output: the finalisation order step by step (vertex extracted, its final distance, relaxations performed),
        then for every depot the shortest distance, the actual path and the predecessor, with an independent
        check of each path cost and a Bellman-Ford cross-check. Writes results/t3_stage_a_dijkstra.csv.
Run:  py -3 stage_a_dijkstra.py
"""
from collections import Counter

from routing_engine import bellman_ford, dijkstra, path_cost, path_to
from routing_io import base_network, fmt, print_edges, print_header, route_text, write_csv

SOURCE = "H"


def main():
    g, full = base_network()
    print_header("TASK 3 / STAGE A - NORMAL ROUTING WITH DIJKSTRA (binary heap)")
    print(f"Network: {g.n} depots, {len(g.edges)} one-way roads (u->v cost in minutes); source = {SOURCE} "
          f"({full[SOURCE]})")
    print_edges(g)
    print(f"Negative edge present? {g.has_negative_edge()}  -> Dijkstra's greedy invariant is valid\n")

    ops, trace = Counter(), []
    dist, pred, order = dijkstra(g, SOURCE, ops, trace)
    print("Finalisation order (each step: extract-min = closest unfinalised depot, then relax its out-edges)")
    print(f"  {'step':>4}  {'finalised':<9} {'dist':>4}   relaxations  v: old -> new")
    for k, step in enumerate(trace, 1):
        rel = ", ".join(f"{g.names[v]}: {fmt(old)}->{fmt(new)}" for v, old, new in step["relaxed"]) or "-"
        print(f"  {k:>4}  {g.names[step['vertex']]:<9} {fmt(step['dist']):>4}   {rel}")
    print("  order: " + "  ->  ".join(f"{g.names[v]}({fmt(dist[v])})" for v in order))

    s = g.vertex(SOURCE)
    bf = bellman_ford(g, SOURCE)
    print(f"\nShortest routes from {SOURCE}")
    print(f"  {'depot':<16} {'dist':>4} {'pred':>4}  {'actual path':<41} {'path cost':>9} {'Bellman-Ford':>12}")
    rows = []
    for v in range(g.n):
        route = path_to(pred, s, v)
        cost = path_cost(g, route) if route else None
        name = f"{g.names[v]} {full[g.names[v]]}"
        p = g.names[pred[v]] if pred[v] != -1 else "-"
        ok = "agree" if bf.dist[v] == dist[v] and (cost is None or cost == dist[v]) else "DIFFER"
        print(f"  {name:<16} {fmt(dist[v]):>4} {p:>4}  {route_text(g, route):<41} {fmt(cost) if route else '-':>9}"
              f" {fmt(bf.dist[v]) + ' ' + ok:>12}")
        rows.append([g.names[v], full[g.names[v]], fmt(dist[v]), p, route_text(g, route),
                     order.index(v) + 1 if v in order else "-"])
    write_csv("t3_stage_a_dijkstra.csv", ["depot", "name", "distance", "predecessor", "path", "finalised_step"],
              rows)
    print(f"\nPredecessor array pred[]: " + "  ".join(
        f"{g.names[v]}:{g.names[pred[v]] if pred[v] != -1 else '-'}" for v in range(g.n)))
    print(f"Operation counts: {ops['heap_pops']} heap pops ({ops['stale_pops']} stale), {ops['heap_pushes']} pushes, "
          f"{ops['edge_relaxations']} edge relaxations, {ops['heap_comparisons']} heap comparisons")
    print("Interpretation: depots are finalised in non-decreasing distance order ("
          + ", ".join(fmt(dist[v]) for v in order) + ");")
    print("because no edge is negative, no later route can undercut a finalised distance.")


if __name__ == "__main__":
    main()
