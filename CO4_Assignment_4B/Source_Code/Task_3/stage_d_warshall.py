"""
Task 3, Stage D (part 2) - Reachability between every pair of depots with Warshall's algorithm.

Input : the Stage A network. It is deliberately NOT strongly connected: the hub H only sends, the Retail Park
        R only receives, and the Port P can only reach R.
Output: R(0) (adjacency), the entries that become 1 in every iteration k, the final transitive closure R(10),
        a reachability summary per depot, and cross-checks against breadth-first search and against Floyd
        (R[i][j] = 1 exactly when D[i][j] < inf for i != j).
Writes results/t3_warshall_R0.csv, t3_warshall_final.csv.  Run:  py -3 stage_d_warshall.py
"""
from collections import Counter

from routing_engine import INF, bfs_reachable, floyd, warshall
from routing_io import base_network, matrix_rows, print_header, print_matrix, print_wrapped, write_csv


def main():
    g, full = base_network()
    print_header("TASK 3 / STAGE D - WARSHALL'S ALGORITHM: IS DEPOT j REACHABLE FROM DEPOT i?")
    ops = Counter()
    reach, snaps, changes = warshall(g, ops)
    print("R(0) = adjacency matrix (1 = direct one-way road)")
    print_matrix(g, snaps[0], "R(0)", cell=str, width=4)
    print("\nIteration k: new 1-entries R[i][j] created by passing through depot k")
    for k, changed in enumerate(changes):
        items = [f"{g.names[i]}{g.names[j]}" for i, j in changed]
        print_wrapped(f"  k={k + 1:<2} via {g.names[k]} ({len(changed):>2} new): ", items or ["none"], indent=22)
    print("\nR(10) - FINAL reachability matrix (transitive closure)")
    print_matrix(g, reach, "R(10)", cell=str, width=4)
    write_csv("t3_warshall_R0.csv", ["from"] + g.names, matrix_rows(g, snaps[0], cell=str))
    write_csv("t3_warshall_final.csv", ["from"] + g.names, matrix_rows(g, reach, cell=str))

    print("\nReachability summary")
    for i in range(g.n):
        out = [g.names[j] for j in range(g.n) if reach[i][j] and j != i]
        into = [g.names[j] for j in range(g.n) if reach[j][i] and j != i]
        cyc = "yes" if reach[i][i] else "no"
        print(f"  {g.names[i]} {full[g.names[i]]:<14} reaches {len(out)}: {''.join(out) or '-':<9} "
              f"reached from {len(into)}: {''.join(into) or '-':<9} on a cycle: {cyc}")
    bfs_ok = all({j for j in range(g.n) if reach[i][j]} == bfs_reachable(g, i) for i in range(g.n))
    fl = floyd(g, keep_snapshots=False)
    floyd_ok = all(bool(reach[i][j]) == (fl.dist[i][j] < INF) for i in range(g.n) for j in range(g.n) if i != j)
    print(f"\nCross-check vs breadth-first search from every depot: {'identical' if bfs_ok else 'DIFFERENT'}")
    print(f"Cross-check vs Floyd (R[i][j] = 1 <=> D[i][j] < inf, i != j): {'identical' if floyd_ok else 'DIFFERENT'}")
    ones = sum(map(sum, reach))
    print(f"Work: {ops['warshall_cells']} cell examinations = n^3; {ones} of {g.n * g.n} pairs reachable")


if __name__ == "__main__":
    main()
