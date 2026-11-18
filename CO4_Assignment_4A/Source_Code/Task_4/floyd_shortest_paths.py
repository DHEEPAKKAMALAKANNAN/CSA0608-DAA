"""
Task 4 - Floyd's algorithm: all-pairs shortest paths in a city delivery network       (CO4, Assignment 4A)

Application context: a city courier plans routes between five sites linked by one-way streets:
A Depot, B Central Market, C General Hospital, D Tech Park, E Railway Station.
  * road_network.csv          weights = travel time in minutes (all positive)            -> main manual trace
  * ev_energy_network.csv     weights = net battery energy (Wh) of an electric van; downhill streets are
                              NEGATIVE (regenerative braking) but no cycle can gain energy -> negative edges
  * faulty_energy_network.csv one value mistyped (D->A = -135 instead of -35) creates a NEGATIVE CYCLE
                              -> the algorithm must detect it and refuse to report "shortest" paths

DP formulation (Levitin 8.4):  D(k)[i][j] = length of the shortest i -> j path whose intermediate vertices are
all among the first k vertices.  D(0) = weight matrix (0 on the diagonal, inf where no street),
    D(k)[i][j] = min( D(k-1)[i][j],  D(k-1)[i][k] + D(k-1)[k][j] ),           answer D(n).
Predecessor matrix P: P[i][j] = vertex just before j on the best i -> j path (P[i][j] = i for a direct street);
when the path through k wins, P[i][j] = P[k][j].  A negative D(n)[i][i] proves a negative cycle through i.
Instrumented functions: floyd (comparisons / updates), reconstruct_path, negative_cycle_report,
bellman_ford (reference), dijkstra (greedy, shown to fail with negative edges).
Run:  py -3 floyd_shortest_paths.py
"""
import csv
import heapq
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INF = float("inf")


def load_graph(name):
    """Read a weighted digraph CSV (from,to,weight); returns (labels, weight matrix W)."""
    with open(os.path.join(HERE, "test_data", name), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    labels = sorted({r["from"] for r in rows} | {r["to"] for r in rows})
    idx = {v: i for i, v in enumerate(labels)}
    n = len(labels)
    W = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for r in rows:
        W[idx[r["from"]]][idx[r["to"]]] = int(r["weight"])
    return labels, W


def floyd(W, snapshots=None):
    """Floyd's algorithm with a predecessor matrix. Returns (D, P, ops).
    If `snapshots` is a list, (D(k), set of cells updated in iteration k) is appended for k = 0..n."""
    n = len(W)
    if any(len(row) != n for row in W):
        raise ValueError("weight matrix must be square")
    D = [row[:] for row in W]
    P = [[i if (i != j and W[i][j] < INF) else None for j in range(n)] for i in range(n)]
    ops = {"comparisons": 0, "updates": 0, "updates_per_k": []}
    if snapshots is not None:
        snapshots.append(([row[:] for row in D], set()))
    for k in range(n):
        Dk, Pk, changed = D[k], P[k], set()
        for i in range(n):
            Di, Pi = D[i], P[i]
            dik = Di[k]
            for j in range(n):
                ops["comparisons"] += 1
                if dik + Dk[j] < Di[j]:           # path through k is shorter
                    Di[j] = dik + Dk[j]
                    Pi[j] = Pk[j]
                    changed.add((i, j))
        ops["updates"] += len(changed)
        ops["updates_per_k"].append(len(changed))
        if snapshots is not None:
            snapshots.append(([row[:] for row in D], changed))
    return D, P, ops


def reconstruct_path(P, i, j):
    """Vertices of the best i -> j path, following predecessors backwards from j; [] if unreachable."""
    if i == j:
        return [i]
    if P[i][j] is None:
        return []
    path, v, guard = [j], j, 0
    while v != i:
        v = P[i][v]
        path.append(v)
        guard += 1
        if v is None or guard > len(P):
            raise RuntimeError("predecessor chain broken (negative cycle?)")
    return path[::-1]


def path_cost(W, path):
    return sum(W[a][b] for a, b in zip(path, path[1:]))


def negative_cycle_report(D):
    """Vertices on a negative cycle (D[v][v] < 0) and all pairs whose distance is unbounded (-infinity)."""
    n = len(D)
    bad = [v for v in range(n) if D[v][v] < 0]
    unbounded = {(i, j) for v in bad for i in range(n) for j in range(n) if D[i][v] < INF and D[v][j] < INF}
    return bad, unbounded


def bellman_ford(W, s):
    """Reference single-source distances (negative edges allowed). Returns (dist, has_negative_cycle)."""
    n = len(W)
    dist = [INF] * n
    dist[s] = 0
    edges = [(u, v, W[u][v]) for u in range(n) for v in range(n) if u != v and W[u][v] < INF]
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    neg = any(dist[u] + w < dist[v] for u, v, w in edges)
    return dist, neg


def dijkstra(W, s):
    """Greedy single-source shortest paths (valid only for non-negative weights): each vertex finalised once."""
    n = len(W)
    dist, done = [INF] * n, [False] * n
    dist[s] = 0
    heap = [(0, s)]
    while heap:
        d, u = heapq.heappop(heap)
        if done[u]:
            continue
        done[u] = True
        for v in range(n):
            if not done[v] and u != v and W[u][v] < INF and d + W[u][v] < dist[v]:
                dist[v] = d + W[u][v]
                heapq.heappush(heap, (dist[v], v))
    return dist


# ---------------------------------------------------------------------------------------- printing
def fmt(x):
    return "inf" if x == INF else str(x)


def print_side_by_side(snaps, labels, ks, titles):
    n = len(labels)
    cw = 5
    block = 3 + cw * n + 3
    print(("    " + "".join(f"{titles[k]:<{block}}" for k in ks)).rstrip())
    print(("    " + "".join(("   " + "".join(f"{lab:>{cw}}" for lab in labels)).ljust(block) for _ in ks)).rstrip())
    for i in range(n):
        line = ""
        for k in ks:
            D, changed = snaps[k]
            cells = "".join(f"{fmt(D[i][j]) + ('*' if (i, j) in changed else ''):>{cw}}" for j in range(n))
            line += f" {labels[i]} {cells}".ljust(block)
        print(("    " + line).rstrip())


def main():
    labels, W = load_graph("road_network.csv")
    n = len(labels)
    L = labels
    print("=" * 112)
    print(" TASK 4 - FLOYD'S ALGORITHM: ALL-PAIRS SHORTEST TRAVEL TIMES (minutes) BETWEEN 5 SITES, ONE-WAY STREETS")
    print(" A Depot, B Central Market, C General Hospital, D Tech Park, E Railway Station (test_data/road_network.csv)")
    print("=" * 112)
    snaps = []
    D, P, ops = floyd(W, snaps)
    titles = ["D(0) = W"] + [f"D({k}) via {L[k - 1]}" for k in range(1, n + 1)]
    print("[1] Distance matrices D(0) ... D(5)   (* = improved in this iteration)")
    print_side_by_side(snaps, L, [0, 1, 2], titles)
    print()
    print_side_by_side(snaps, L, [3, 4, 5], titles)

    print("\n[2] Every improvement D[i][j] = D[i][k] + D[k][j] < old value")
    for k in range(1, n + 1):
        prev, (cur, changed) = snaps[k - 1][0], snaps[k]
        items = [f"{L[i]}{L[j]}: {fmt(prev[i][j])} -> {prev[i][k-1]}+{prev[k-1][j]}={cur[i][j]}"
                 for (i, j) in sorted(changed)]
        for c in range(0, len(items), 4):
            head = f"    k={k} ({L[k-1]}): " if c == 0 else " " * 16
            print(head + "   ".join(items[c:c + 4]))
    print(f"    comparisons = {ops['comparisons']} = n^3;  updates per k = {ops['updates_per_k']} "
          f"(total {ops['updates']})")

    print("\n[3] Final predecessor matrix P (P[i][j] = vertex before j on the best i -> j path)")
    print("       " + "".join(f"{lab:>4}" for lab in L))
    for i in range(n):
        print(f"    {L[i]}  " + "".join(f"{(L[P[i][j]] if P[i][j] is not None else '-'):>4}" for j in range(n)))
    print("    Reconstructed routes:")
    for (a, b) in [(4, 0), (0, 4), (1, 0), (2, 1)]:
        path = reconstruct_path(P, a, b)
        print(f"      {L[a]} -> {L[b]}: {' -> '.join(L[v] for v in path):<22} cost {path_cost(W, path):>3} "
              f"= D[{L[a]}][{L[b]}] = {D[a][b]}")

    print("\n[4] Negative edges: electric-van energy (Wh) per street, downhill < 0 (test_data/ev_energy_network.csv)")
    _, We = load_graph("ev_energy_network.csv")
    De, Pe, _ = floyd(We)
    bf_ok = all(bellman_ford(We, s) == (De[s], False) for s in range(n))
    print("       " + "".join(f"{lab:>6}" for lab in L))
    for i in range(n):
        print(f"    {L[i]}  " + "".join(f"{fmt(De[i][j]):>6}" for j in range(n)))
    bad, _ = negative_cycle_report(De)
    print(f"    negative cycle? {'YES' if bad else 'no'} (all D[i][i] = 0);  equals Bellman-Ford from every source:"
          f" {bf_ok}")
    for (a, b) in [(0, 4), (3, 1)]:
        path = reconstruct_path(Pe, a, b)
        print(f"      {L[a]} -> {L[b]}: {' -> '.join(L[v] for v in path)}  energy {path_cost(We, path)} Wh")
    dj = dijkstra(We, 0)
    wrong = [f"{L[j]} ({dj[j]} instead of {De[0][j]})" for j in range(n) if dj[j] != De[0][j]]
    print(f"    greedy Dijkstra from A: {'WRONG for ' + ', '.join(wrong) if wrong else 'happens to be correct'}")
    print("    (Dijkstra finalises C at 25 before the downhill street B->C (-20) is seen; Floyd has no such rule)")

    print("\n[5] Failure case: D->A mistyped as -135 Wh (test_data/faulty_energy_network.csv)")
    _, Wf = load_graph("faulty_energy_network.csv")
    Df, _, _ = floyd(Wf)
    bad, unbounded = negative_cycle_report(Df)
    print(f"    diagonal after Floyd: {[Df[v][v] for v in range(n)]}")
    print(f"    NEGATIVE CYCLE through {', '.join(L[v] for v in bad)} -> {len(unbounded)} of {n * n} pairs have no "
          f"shortest path (-inf)")
    print(f"    Bellman-Ford from A also reports a negative cycle: {bellman_ford(Wf, 0)[1]}")
    print("    -> the planner must reject this data instead of printing distances.")


if __name__ == "__main__":
    main()
