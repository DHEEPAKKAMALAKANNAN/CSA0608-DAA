"""
single_source.py - Task 5.1 / 5.2 (CO4 Assignment 4A): Dijkstra (greedy) and Bellman-Ford (repeated
relaxation) on the given directed graph, plus the two negative-weight scenarios of Task 5.2.

Implements the report's pseudocode GreedyShortestPaths(G, s) - EXTRACT_MIN realised as a linear scan
over unsettled vertices (ties broken alphabetically) - and BellmanFord(G, s).  Prints the same
state -> decision -> update tables as the manual traces, which were done by hand first.
"""
from graph_common import INF, fmt, read_graph


def dijkstra(vertices, edges, s, trace=None):
    dist = {v: INF for v in vertices}
    pred = {v: None for v in vertices}
    dist[s] = 0
    settled = set()
    adj = {v: [] for v in vertices}
    for u, v, w in edges:
        adj[u].append((v, w))
    while len(settled) < len(vertices):
        candidates = [v for v in vertices if v not in settled and dist[v] < INF]
        if not candidates:                                    # remaining vertices unreachable
            break
        u = min(candidates, key=lambda v: (dist[v], v))       # EXTRACT_MIN
        settled.add(u)                                        # greedy commitment: dist[u] is final
        notes = []
        for v, w in adj[u]:
            if v in settled:
                notes.append(f"{u}{v}: {v} settled, skip")
            elif dist[u] + w < dist[v]:
                notes.append(f"{u}{v}: {fmt(dist[v])}->{dist[u] + w}")
                dist[v], pred[v] = dist[u] + w, u             # distance + predecessor update
            else:
                notes.append(f"{u}{v}: {dist[u] + w}>={fmt(dist[v])} keep")
        if trace is not None:
            trace.append((u, dict(dist), dict(pred), "; ".join(notes) or "no outgoing edges"))
    return dist, pred


def bellman_ford(vertices, edges, s, trace=None):
    dist = {v: INF for v in vertices}
    pred = {v: None for v in vertices}
    dist[s] = 0
    for k in range(1, len(vertices)):                         # at most |V| - 1 passes
        changed = []
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v], pred[v] = dist[u] + w, u
                changed.append(f"{u}{v}->{dist[v]}")
        if trace is not None:
            trace.append((k, dict(dist), ", ".join(changed) or "no change"))
        if not changed:                                       # early termination: converged
            break
    cycle_edge = None
    for u, v, w in edges:                                     # extra pass: negative-cycle detection
        if dist[u] != INF and dist[u] + w < dist[v]:
            cycle_edge = (u, v, w)
            break
    return dist, pred, cycle_edge


def path(pred, v):
    out = []
    while v is not None:
        out.append(v)
        v = pred[v]
    return "->".join(reversed(out))


def main():
    V, E = read_graph()
    print("=" * 112)
    print("TASK 5.1 - Greedy single-source shortest paths (Dijkstra) from A   - verification of the manual trace")
    print("=" * 112)
    print("edges:", ", ".join(f"{u}->{v}({w})" for u, v, w in E))
    tr = []
    dist, pred = dijkstra(V, E, "A", tr)
    print(f"{'step':>4} | {'extract':<7} | " + " ".join(f"{v:>4}" for v in V) + " | relaxations (u v: old -> new)")
    print("-" * 112)
    print(f"{0:>4} | {'init':<7} | " + " ".join(f"{fmt(0 if v == 'A' else INF):>4}" for v in V) + " | dist[A]=0")
    for k, (u, d, p, notes) in enumerate(tr, 1):
        print(f"{k:>4} | {u:<7} | " + " ".join(f"{fmt(d[v]):>4}" for v in V) + f" | {notes}")
    print("-" * 112)
    print("final: " + "   ".join(f"{v}: dist {fmt(dist[v])}, pred {pred[v] or '-'}, path {path(pred, v)}" for v in V[1:3]))
    print("       " + "   ".join(f"{v}: dist {fmt(dist[v])}, pred {pred[v] or '-'}, path {path(pred, v)}" for v in V[3:]))

    print("\n" + "=" * 112)
    print("TASK 5.2 - Bellman-Ford (edges relaxed in the order listed above), same graph")
    print("=" * 112)
    tr = []
    dist2, _, cyc = bellman_ford(V, E, "A", tr)
    for k, d, ch in tr:
        print(f"pass {k}: " + " ".join(f"{v}={fmt(d[v])}" for v in V) + f"   updates: {ch}")
    print(f"negative-cycle check (pass |V|): {'cycle via ' + str(cyc) if cyc else 'no edge can still relax -> none'}"
          f";  same distances as Dijkstra: {dist2 == dist}")

    print("\nScenario N1 - negative edge, no cycle: A->B 2, A->C 4, C->B -3  (true dist B = 1 via A->C->B)")
    V1, E1 = ["A", "B", "C"], [("A", "B", 2), ("A", "C", 4), ("C", "B", -3)]
    tr = []
    d1, _ = dijkstra(V1, E1, "A", tr)
    for u, d, _, notes in tr:
        print(f"   Dijkstra extract {u}: " + " ".join(f"{v}={fmt(d[v])}" for v in V1) + f"   {notes}")
    d2, _, _ = bellman_ford(V1, E1, "A")
    print(f"   Dijkstra result B = {d1['B']} (WRONG, B was committed too early);  Bellman-Ford B = {d2['B']} (correct)")

    print("\nScenario N2 - original graph plus edge C->B -4  (cycle B->C->B has weight 2 + (-4) = -2)")
    E2 = E + [("C", "B", -4)]
    tr = []
    d3, _, cyc = bellman_ford(V, E2, "A", tr)
    for k, d, ch in tr:
        print(f"   pass {k}: " + " ".join(f"{v}={fmt(d[v])}" for v in V) + f"   updates: {ch}")
    print(f"   extra pass |V| = 5: edge {cyc[0]}->{cyc[1]} ({cyc[2]}) can still relax -> "
          "REACHABLE NEGATIVE CYCLE DETECTED" if cyc else "   no cycle detected")


if __name__ == "__main__":
    main()
