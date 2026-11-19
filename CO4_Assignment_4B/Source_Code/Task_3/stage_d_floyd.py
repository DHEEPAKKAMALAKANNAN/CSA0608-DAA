"""
Task 3, Stage D (part 1) - All-pairs shortest-path costs with Floyd's algorithm.

Input : the Stage A network (10 depots, 19 one-way roads, costs >= 0).
Output: D(0) (direct costs), the entries improved in every iteration k (vertex k allowed as an intermediate),
        the intermediate matrix D(4) (intermediates H, A, B, C), the final D(10), route reconstruction from
        the successor matrix, and a cross-check of every row against Dijkstra run from that row's depot.
Writes results/t3_floyd_D0.csv, t3_floyd_final.csv, t3_floyd_changes.csv.  Run:  py -3 stage_d_floyd.py
"""
from collections import Counter

from routing_engine import dijkstra, floyd, floyd_path, path_cost
from routing_io import base_network, fmt, matrix_rows, print_header, print_matrix, print_wrapped, route_text, write_csv

QUERIES = [("H", "R"), ("B", "G"), ("E", "D"), ("G", "C"), ("R", "H")]


def main():
    g, _ = base_network()
    print_header("TASK 3 / STAGE D - FLOYD'S ALGORITHM: SHORTEST-PATH COST BETWEEN EVERY PAIR")
    ops = Counter()
    res = floyd(g, ops)
    print("D(0) = direct road costs (inf = no direct road)")
    print_matrix(g, res.snapshots[0], "D(0)")
    print("\nIteration k: entries D[i][j] improved by routing through depot k  (i->j: old -> new)")
    change_rows = []
    for k, changed in enumerate(res.changes):
        items = [f"{g.names[i]}{g.names[j]}:{fmt(o)}->{fmt(n)}" for i, j, o, n in changed]
        print_wrapped(f"  k={k + 1:<2} via {g.names[k]} ({len(changed):>2}): ", items or ["no improvement"],
                      indent=18)
        change_rows += [[k + 1, g.names[k], g.names[i], g.names[j], fmt(o), fmt(n)] for i, j, o, n in changed]
    write_csv("t3_floyd_changes.csv", ["k", "via", "from", "to", "old", "new"], change_rows)
    print("\nD(4) - intermediates restricted to {H, A, B, C}")
    print_matrix(g, res.snapshots[4], "D(4)")
    print("\nD(10) - FINAL all-pairs shortest-path costs")
    print_matrix(g, res.dist, "D(10)")
    write_csv("t3_floyd_D0.csv", ["from"] + g.names, matrix_rows(g, res.snapshots[0]))
    write_csv("t3_floyd_final.csv", ["from"] + g.names, matrix_rows(g, res.dist))

    print("\nRoute reconstruction from the successor matrix nxt[i][j]")
    for a, b in QUERIES:
        i, j = g.vertex(a), g.vertex(b)
        route = floyd_path(res.nxt, i, j)
        cost = fmt(path_cost(g, route)) if route else "-"
        print(f"  {a} -> {b}: cost {fmt(res.dist[i][j]):>3}   route {route_text(g, route):<41} (re-summed: {cost})")

    agree = sum(dijkstra(g, s)[0] == res.dist[s] for s in range(g.n))
    print(f"\nCross-check: Floyd row == Dijkstra from that depot for {agree}/{g.n} sources")
    print(f"Negative diagonal entries: {res.negative_vertices or 'none'} -> matrix valid")
    print(f"Work: {ops['floyd_cells']} cell examinations = n^3 = {g.n ** 3} (independent of the number of roads)")


if __name__ == "__main__":
    main()
