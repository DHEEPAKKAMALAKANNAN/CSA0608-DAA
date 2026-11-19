"""
floyd_all_pairs.py - Task 5.3 (CO4 Assignment 4A): Floyd's all-pairs shortest paths on the given graph.

D(k)[i][j] = length of the shortest path from vertex i to vertex j whose INTERMEDIATE vertices all lie in
{v1, ..., vk} (here v1..v5 = A..E).  Transition: D(k)[i][j] = min(D(k-1)[i][j], D(k-1)[i][k] + D(k-1)[k][j]).
Prints every matrix D(0)..D(5) and marks the entries that improved in each phase (*).  The matrices
were first computed by hand; this run only confirms them.
"""
from graph_common import INF, fmt, read_graph


def floyd(vertices, edges, snapshots=None):
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}
    D = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    NXT = [[None] * n for _ in range(n)]
    for u, v, w in edges:
        D[idx[u]][idx[v]] = min(D[idx[u]][idx[v]], w)
        NXT[idx[u]][idx[v]] = idx[v]
    if snapshots is not None:
        snapshots.append(([row[:] for row in D], set()))
    for k in range(n):                                  # phase k: allow vertex k as an intermediate
        improved = set()
        for i in range(n):
            for j in range(n):
                if D[i][k] + D[k][j] < D[i][j]:
                    D[i][j] = D[i][k] + D[k][j]
                    NXT[i][j] = NXT[i][k]
                    improved.add((i, j))
        if snapshots is not None:
            snapshots.append(([row[:] for row in D], improved))
    return D, NXT


def route(NXT, vertices, i, j):
    if NXT[i][j] is None:
        return "-"
    out = [vertices[i]]
    while i != j:
        i = NXT[i][j]
        out.append(vertices[i])
    return "->".join(out)


def main():
    V, E = read_graph()
    snaps = []
    D, NXT = floyd(V, E, snaps)
    print("=" * 100)
    print("TASK 5.3 - Floyd's algorithm: D(k)[i][j] for k = 0..5 (intermediates restricted to the first k vertices)")
    print("=" * 100)
    blocks = []
    for k, (M, imp) in enumerate(snaps):
        title = "D(0) = edge weights" if k == 0 else f"D({k}) via {V[k - 1]}  ({len(imp)} improved)"
        lines = [f"{title:<30}", "     " + "".join(f"{v:>5}" for v in V)]
        for i, v in enumerate(V):
            lines.append(f"  {v}  " + "".join(f"{fmt(M[i][j]) + ('*' if (i, j) in imp else ''):>5}"
                                             for j in range(len(V))))
        blocks.append(lines)
    for a in range(0, len(blocks), 3):                  # print three matrices side by side
        group = blocks[a:a + 3]
        for r in range(len(group[0])):
            print("   ".join(g[r] + " " * (30 - len(g[r])) for g in group))
        print()
    print("* = entry improved in that phase.   Shortest routes from the final matrix D(5):")
    for i, u in enumerate(V):
        routes = [f"{u}->{V[j]}: {fmt(D[i][j])} {route(NXT, V, i, j)}" for j in range(len(V))
                  if j != i and D[i][j] < INF]
        print("  " + "   ".join(routes) if routes else f"  {u}: no outgoing paths")
    print("Row A of D(5) = " + " ".join(f"{V[j]}={fmt(D[0][j])}" for j in range(len(V)))
          + "  (identical to the Dijkstra / Bellman-Ford distances from A)")


if __name__ == "__main__":
    main()
