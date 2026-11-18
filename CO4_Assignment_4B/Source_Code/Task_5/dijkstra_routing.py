"""
Task 5 - Dijkstra's single-source shortest paths for ambulance routing.

Junctions are vertices 0..n-1, roads are DIRECTED edges (u, v, w) with w = travel time in minutes
(a two-way street is two edges). From the hospital s we need the fastest time and route to every junction.

  dijkstra_array  O(V^2 + E): dist array, linear scan for the closest unsettled junction (greedy choice)
  dijkstra_heap   O((V + E) log V): binary heap with lazy deletion - stale entries are skipped on pop
  bellman_ford    O(VE) reference: correct with negative edges, detects negative cycles
  path_to         route reconstruction from the prev[] array
Dijkstra refuses negative weights (ValueError) unless allow_negative=True, which is used ONLY to
demonstrate the wrong answer it then produces.
Run:  py -3 dijkstra_routing.py   (given network: step table, routes, negative-edge failure, edge cases)
"""
import csv
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
INF = float("inf")


def load_network(path):
    """CSV columns u, v, w, two_way (yes/no). Returns (names, directed edges as (u, v, w))."""
    names, index, edges = [], {}, []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for s in (r["u"], r["v"]):
                if s not in index:
                    index[s] = len(names)
                    names.append(s)
            u, v, w = index[r["u"]], index[r["v"]], int(r["w"])
            edges.append((u, v, w))
            if r["two_way"].strip().lower() == "yes":
                edges.append((v, u, w))
    return names, edges


def adjacency(n, edges, allow_negative=False):
    if n < 1:
        raise ValueError("the road network needs at least one junction")
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"road ({u}, {v}) refers to an unknown junction")
        if w < 0 and not allow_negative:
            raise ValueError(f"negative travel time {w} on road ({u}, {v}): Dijkstra requires w >= 0")
        if u != v:                                   # a self-loop never shortens a route
            adj[u].append((v, w))
    return adj


# ----------------------------------------------------------------------------- O(V^2) array version
def dijkstra_array(n, edges, s, ops=None, trace=None, allow_negative=False):
    """Returns (dist, prev). trace receives (settled u, dist copy, settled copy, [updated v]) per round."""
    ops = Counter() if ops is None else ops
    adj = adjacency(n, edges, allow_negative)
    dist, prev, done = [INF] * n, [-1] * n, [False] * n
    dist[s] = 0
    for _ in range(n):
        u, best = -1, INF
        for v in range(n):                           # linear scan: closest unsettled junction
            ops["scan_comparisons"] += 1
            if not done[v] and dist[v] < best:
                u, best = v, dist[v]
        if u == -1:                                  # everything left is unreachable
            break
        done[u] = True
        updated = []
        for v, w in adj[u]:
            ops["relaxations"] += 1
            if not done[v] and dist[u] + w < dist[v]:
                dist[v], prev[v] = dist[u] + w, u
                updated.append(v)
        if trace is not None:
            trace.append((u, list(dist), list(done), updated))
    return dist, prev


# ----------------------------------------------------------------------------- O((V+E) log V) heap version
class BinaryHeap:
    """Min-heap of (dist, vertex) with counted comparisons (lazy deletion: duplicates allowed)."""

    def __init__(self, ops):
        self.a, self.ops = [], ops

    def __len__(self):
        return len(self.a)

    def push(self, d, v):
        a = self.a
        a.append((d, v))
        self.ops["pushes"] += 1
        i = len(a) - 1
        while i > 0:
            p = (i - 1) // 2
            self.ops["heap_comparisons"] += 1
            if a[i][0] < a[p][0]:
                a[i], a[p] = a[p], a[i]
                i = p
            else:
                break

    def pop(self):
        a = self.a
        self.ops["pops"] += 1
        top, last = a[0], a.pop()
        if a:
            a[0] = last
            i, n = 0, len(a)
            while True:
                s, l, r = i, 2 * i + 1, 2 * i + 2
                if l < n:
                    self.ops["heap_comparisons"] += 1
                    if a[l][0] < a[s][0]:
                        s = l
                if r < n:
                    self.ops["heap_comparisons"] += 1
                    if a[r][0] < a[s][0]:
                        s = r
                if s == i:
                    break
                a[i], a[s] = a[s], a[i]
                i = s
        return top


def dijkstra_heap(n, edges, s, ops=None, allow_negative=False, target=None):
    """Returns (dist, prev). With target given, stops as soon as the target is SETTLED (popped)."""
    ops = Counter() if ops is None else ops
    adj = adjacency(n, edges, allow_negative)
    dist, prev, done = [INF] * n, [-1] * n, [False] * n
    dist[s] = 0
    heap = BinaryHeap(ops)
    heap.push(0, s)
    while heap:
        d, u = heap.pop()
        if done[u] or d > dist[u]:                   # stale entry left behind by an earlier improvement
            ops["stale_pops"] += 1
            continue
        done[u] = True
        ops["settled"] += 1
        if u == target:
            break
        for v, w in adj[u]:
            ops["relaxations"] += 1
            if not done[v] and d + w < dist[v]:
                dist[v], prev[v] = d + w, u
                heap.push(dist[v], v)
    return dist, prev


# ----------------------------------------------------------------------------- reference + helpers
def bellman_ford(n, edges, s, ops=None):
    """Returns (dist, prev, negative_cycle_reachable). Handles negative weights; O(VE)."""
    ops = Counter() if ops is None else ops
    dist, prev = [INF] * n, [-1] * n
    dist[s] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            ops["bf_relaxations"] += 1
            if dist[u] + w < dist[v]:
                dist[v], prev[v], changed = dist[u] + w, u, True
        if not changed:                               # early exit: no change in a full pass
            break
    neg = any(dist[u] + w < dist[v] for u, v, w in edges)
    return dist, prev, neg


def path_to(prev, s, t, dist=None):
    """Junction list s -> t, or None when t is unreachable."""
    if dist is not None and dist[t] == INF:
        return None
    path = [t]
    while path[-1] != s:
        p = prev[path[-1]]
        if p == -1:
            return None
        path.append(p)
    return path[::-1]


def fmt(d):
    return "inf" if d == INF else str(d)


# ----------------------------------------------------------------------------- demo
def main():
    names, edges = load_network(os.path.join(HERE, "test_data", "given_G1_road_network.csv"))
    n, s = len(names), 0
    print("TASK 5 - DIJKSTRA: ambulance routing from the City Hospital (H), travel times in minutes")
    print("=" * 104)
    print(f"Given test case G1: {n} junctions, {len(edges)} directed road segments (two-way streets counted twice)")
    print("\nStep table (array version): * = settled; dist after the round; prev updated for the listed junctions")
    print(f"  {'round':>5} {'settle':<6} " + " ".join(f"{x:>5}" for x in names) + "  updated (new dist via settled)")
    ops, trace = Counter(), []
    dist, prev = dijkstra_array(n, edges, s, ops, trace)
    print(f"  {'init':>5} {'-':<6} " + " ".join(f"{fmt(0 if i == s else INF):>5}" for i in range(n)))
    for k, (u, dsnap, done, upd) in enumerate(trace, 1):
        cells = " ".join(f"{fmt(dsnap[i]) + ('*' if done[i] else ' '):>5}" for i in range(n))
        print(f"  {k:>5} {names[u]:<6} {cells}  {', '.join(f'{names[v]}={dsnap[v]}' for v in upd) or '-'}")
    print(f"  array version: {ops['scan_comparisons']} scan comparisons, {ops['relaxations']} relaxations")
    hops = Counter()
    hdist, _ = dijkstra_heap(n, edges, s, hops)
    bdist, _, _ = bellman_ford(n, edges, s)
    print(f"  heap version : {hops['heap_comparisons']} heap comparisons, {hops['pushes']} pushes, "
          f"{hops['stale_pops']} stale pops skipped; same distances: {hdist == dist}; Bellman-Ford agrees: {bdist == dist}")

    print("\nFastest ambulance routes from H (path reconstruction from prev[])")
    for t in range(1, n):
        p = path_to(prev, s, t, dist)
        print(f"  H -> {names[t]:<3} {fmt(dist[t]):>4} min   " + " -> ".join(names[x] for x in p))

    print("\nFailure case F1: a negative edge (B -> A = -4, a 'green-wave credit') - Dijkstra settles A too early")
    fn, fe = load_network(os.path.join(HERE, "test_data", "failure_F1_negative_edge.csv"))
    try:
        dijkstra_heap(len(fn), fe, 0)
    except ValueError as e:
        print(f"  safe mode  : ValueError: {e}")
    dd, dp = dijkstra_heap(len(fn), fe, 0, allow_negative=True)
    bd, bp, neg = bellman_ford(len(fn), fe, 0)
    print(f"  {'junction':<9} {'Dijkstra (unsafe)':>18} {'Bellman-Ford':>13}  correct route")
    for t in range(len(fn)):
        print(f"  {fn[t]:<9} {fmt(dd[t]):>18} {fmt(bd[t]):>13}  {' -> '.join(fn[x] for x in path_to(bp, 0, t))}"
              f"{'   <-- WRONG' if dd[t] != bd[t] else ''}")
    cn, ce = load_network(os.path.join(HERE, "test_data", "failure_F2_negative_cycle.csv"))
    print(f"  F2 negative cycle A->B->C->A (1 - 3 + 1 = -1): Bellman-Ford reports negative cycle = "
          f"{bellman_ford(len(cn), ce, 0)[2]} (no shortest route exists)")

    print("\nBoundary cases")
    d1, _ = dijkstra_heap(1, [], 0)
    print(f"  B1 single junction            -> dist {d1}")
    d2, p2 = dijkstra_heap(3, [(0, 1, 4)], 0)
    print(f"  B2 junction 2 unreachable     -> dist {[fmt(x) for x in d2]}, route to 2 = {path_to(p2, 0, 2, d2)}")
    d3, p3 = dijkstra_heap(3, [(0, 1, 0), (1, 2, 0), (0, 2, 1)], 0)
    print(f"  B3 zero-time roads            -> dist {d3}, route to 2 = {path_to(p3, 0, 2, d3)}")
    print(f"  B4 source = target            -> route H -> H = {[names[x] for x in path_to(prev, 0, 0, dist)]}, 0 min")
    d5, _ = dijkstra_heap(2, [(0, 1, 9), (0, 1, 4), (1, 1, 2)], 0)
    print(f"  B5 parallel roads + self-loop -> dist {d5} (cheaper parallel road used, loop ignored)")


if __name__ == "__main__":
    main()
