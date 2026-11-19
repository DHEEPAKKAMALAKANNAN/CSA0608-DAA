"""
Task 3 - Routing engine of a logistics platform under changing network conditions (algorithm core, no I/O).

The network is a DIRECTED weighted graph: vertices are depots (short codes such as H, A, B ...), an edge
(u, v, w) is a one-way road whose travel cost is w (minutes; in Stages B/C a contract may make w negative).

  dijkstra(g, s)         single source, binary heap, greedy "finalise the closest unfinalised vertex".
                         It is run EXACTLY as written even when a negative edge exists, so its failure can be
                         observed; the trace records every relaxation that was refused because the target was
                         already finalised (the moment the greedy invariant is broken).
  bellman_ford(g, s)     single source, |V|-1 passes over all edges (+ early exit), then one extra pass: any
                         edge that still relaxes proves a reachable negative cycle. The cycle is extracted by a
                         predecessor walk and every vertex reachable from it is reported as -inf (undefined)
                         instead of returning a misleading finite distance.
  floyd(g)               all pairs, D(k) matrices + successor matrix for route reconstruction, negative-cycle
                         check on the diagonal.
  warshall(g)            transitive closure R(k) (reachability matrix).
  shortest_paths(g, s)   production facade: Dijkstra when all weights are >= 0, otherwise Bellman-Ford;
                         raises NegativeCycleError when a reachable negative cycle exists.
Every algorithm counts its basic operations in a collections.Counter (primary evidence, not time).
"""
import csv
from collections import Counter, deque

INF = float("inf")


class NegativeCycleError(Exception):
    """Raised when shortest paths are undefined because a negative cycle is reachable from the source."""

    def __init__(self, cycle, weight):
        super().__init__(f"negative cycle {' -> '.join(cycle + cycle[:1])} with total weight {weight}")
        self.cycle, self.weight = cycle, weight


# ----------------------------------------------------------------------------- graph model
class Graph:
    """Directed weighted graph with named vertices (index = position in `names`)."""

    def __init__(self, names, edges):
        """names: list of distinct vertex codes; edges: iterable of (u_code, v_code, weight)."""
        if not names:
            raise ValueError("a network needs at least one vertex")
        if len(set(names)) != len(names):
            raise ValueError("vertex codes must be unique")
        self.names = list(names)
        self.index = {name: i for i, name in enumerate(self.names)}
        self.edges = []                                 # (u, v, w) with integer indices, in input order
        seen = set()
        for u, v, w in edges:
            if u not in self.index or v not in self.index:
                raise ValueError(f"edge {u}->{v} refers to an unknown vertex")
            if not isinstance(w, (int, float)) or w != w or w in (INF, -INF):
                raise ValueError(f"edge {u}->{v} has an invalid weight {w!r}")
            if (u, v) in seen:
                raise ValueError(f"duplicate edge {u}->{v}")
            seen.add((u, v))
            self.edges.append((self.index[u], self.index[v], w))
        self.adj = [[] for _ in self.names]
        for u, v, w in self.edges:
            self.adj[u].append((v, w))

    @property
    def n(self):
        return len(self.names)

    def vertex(self, code):
        """Index of a vertex code; ValueError for an unknown code (invalid query)."""
        if code not in self.index:
            raise ValueError(f"unknown vertex {code!r}")
        return self.index[code]

    def has_negative_edge(self):
        return any(w < 0 for _, _, w in self.edges)

    def with_extra_edges(self, extra):
        """New graph = this graph plus the edges in `extra` (an edge u->v already present is replaced)."""
        replaced = {(u, v) for u, v, _ in extra}
        kept = [(self.names[u], self.names[v], w) for u, v, w in self.edges
                if (self.names[u], self.names[v]) not in replaced]
        return Graph(self.names, kept + list(extra))


def load_edges(path):
    """CSV with columns u, v, w -> list of (u, v, int w)."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    try:
        return [(r["u"].strip(), r["v"].strip(), int(r["w"])) for r in rows]
    except (KeyError, ValueError) as exc:
        raise ValueError(f"{path}: malformed edge row ({exc})") from exc


def load_names(path):
    """CSV with columns code, name, ... -> (codes list, {code: full name})."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r["code"] for r in rows], {r["code"]: r["name"] for r in rows}


# ----------------------------------------------------------------------------- binary heap
class BinaryHeap:
    """Min-heap of (key, vertex) pairs with counted comparisons; ties broken by vertex index (deterministic)."""

    def __init__(self, ops):
        self.a, self.ops = [], ops

    def __len__(self):
        return len(self.a)

    def push(self, key, v):
        a = self.a
        a.append((key, v))
        self.ops["heap_pushes"] += 1
        i = len(a) - 1
        while i > 0:
            p = (i - 1) // 2
            self.ops["heap_comparisons"] += 1
            if a[i] < a[p]:
                a[i], a[p] = a[p], a[i]
                i = p
            else:
                break

    def pop(self):
        a = self.a
        self.ops["heap_pops"] += 1
        top, last = a[0], a.pop()
        if a:
            a[0] = last
            i, n = 0, len(a)
            while True:
                s, l, r = i, 2 * i + 1, 2 * i + 2
                if l < n:
                    self.ops["heap_comparisons"] += 1
                    if a[l] < a[s]:
                        s = l
                if r < n:
                    self.ops["heap_comparisons"] += 1
                    if a[r] < a[s]:
                        s = r
                if s == i:
                    break
                a[i], a[s] = a[s], a[i]
                i = s
        return top


# ----------------------------------------------------------------------------- Dijkstra
def dijkstra(g, source, ops=None, trace=None):
    """Dijkstra with a binary heap and lazy deletion.
    Returns (dist, pred, order): dist/pred lists by vertex index, order = vertices in finalisation order.
    trace (optional list) receives one dict per finalisation:
      {"vertex", "dist", "relaxed": [(v, old, new)], "refused": [(v, candidate, finalised_dist)]}
    'refused' lists cheaper routes to ALREADY finalised vertices - impossible when all w >= 0."""
    ops = Counter() if ops is None else ops
    s = g.vertex(source) if isinstance(source, str) else source
    dist, pred, done, order = [INF] * g.n, [-1] * g.n, [False] * g.n, []
    dist[s] = 0
    heap = BinaryHeap(ops)
    heap.push(0, s)
    while heap:
        d, u = heap.pop()
        if done[u] or d > dist[u]:                     # stale entry left by an earlier improvement
            ops["stale_pops"] += 1
            continue
        done[u] = True                                 # greedy commitment: dist[u] is declared final
        order.append(u)
        step = {"vertex": u, "dist": d, "relaxed": [], "refused": []}
        for v, w in g.adj[u]:
            ops["edge_relaxations"] += 1
            cand = d + w
            if done[v]:
                if cand < dist[v]:
                    step["refused"].append((v, cand, dist[v]))
                continue
            if cand < dist[v]:
                step["relaxed"].append((v, dist[v], cand))
                dist[v], pred[v] = cand, u
                heap.push(cand, v)
        if trace is not None:
            trace.append(step)
    return dist, pred, order


def path_to(pred, source, target):
    """Route source -> target as a list of vertex indices from the predecessor array ([] if unreachable)."""
    if source == target:
        return [source]
    if pred[target] == -1:
        return []
    route, v, guard = [target], target, 0
    while v != source:
        v = pred[v]
        guard += 1
        if v == -1 or guard > len(pred):               # broken chain (e.g. predecessor cycle): no valid route
            return []
        route.append(v)
    return route[::-1]


def path_cost(g, route):
    """Sum of edge weights along a route given as vertex indices (validates that every hop is an edge)."""
    weight = {(u, v): w for u, v, w in g.edges}
    total = 0
    for u, v in zip(route, route[1:]):
        if (u, v) not in weight:
            raise ValueError(f"{g.names[u]}->{g.names[v]} is not an edge")
        total += weight[(u, v)]
    return total


# ----------------------------------------------------------------------------- Bellman-Ford
class BellmanFordResult:
    """dist (with -inf for vertices whose distance is undefined), pred, pass_log, negative_cycle, affected."""

    def __init__(self, dist, pred, pass_log, negative_cycle, cycle_weight, affected):
        self.dist, self.pred, self.pass_log = dist, pred, pass_log
        self.negative_cycle, self.cycle_weight, self.affected = negative_cycle, cycle_weight, affected

    @property
    def has_negative_cycle(self):
        return self.negative_cycle is not None


def bellman_ford(g, source, ops=None):
    """Bellman-Ford with early exit and a V-th detection pass.
    pass_log: one dict per pass {"pass", "updates": [(v, old, new, via_u)], "dist": copy}.
    If a reachable negative cycle exists: negative_cycle = list of vertex indices in cycle order, its weight,
    and affected = every vertex reachable from the cycle; their dist is set to -inf (no shortest path)."""
    ops = Counter() if ops is None else ops
    s = g.vertex(source) if isinstance(source, str) else source
    dist, pred, pass_log = [INF] * g.n, [-1] * g.n, []
    dist[s] = 0
    for k in range(1, g.n):                            # at most |V|-1 passes are ever needed
        updates = []
        for u, v, w in g.edges:
            ops["edge_relaxations"] += 1
            if dist[u] != INF and dist[u] + w < dist[v]:
                updates.append((v, dist[v], dist[u] + w, u))
                dist[v], pred[v] = dist[u] + w, u
        pass_log.append({"pass": k, "updates": updates, "dist": list(dist)})
        if not updates:                                # early exit: distances are stable
            break
    # detection pass: after |V|-1 passes every simple shortest path is settled, so any further improvement
    # can only come from a walk that repeats a vertex with negative total weight = a negative cycle.
    witness = None
    for u, v, w in g.edges:
        ops["detection_checks"] += 1
        if dist[u] != INF and dist[u] + w < dist[v]:
            witness = (u, v, w)
            break
    if witness is None:
        return BellmanFordResult(dist, pred, pass_log, None, None, set())
    u, v, w = witness
    pred = list(pred)
    pred[v] = u
    x = v
    for _ in range(g.n):                               # walking back |V| steps lands inside the cycle
        x = pred[x]
    cycle, y = [x], pred[x]
    while y != x:
        cycle.append(y)
        y = pred[y]
    cycle.reverse()                                    # forward order along the edges
    weight = {(a, b): c for a, b, c in g.edges}
    cycle_weight = sum(weight[(cycle[i], cycle[(i + 1) % len(cycle)])] for i in range(len(cycle)))
    affected, queue = set(cycle), deque(cycle)        # everything reachable from the cycle is -inf
    while queue:
        a = queue.popleft()
        for b, _ in g.adj[a]:
            if b not in affected:
                affected.add(b)
                queue.append(b)
    safe = [(-INF if i in affected else d) for i, d in enumerate(dist)]
    return BellmanFordResult(safe, pred, pass_log, cycle, cycle_weight, affected)


# ----------------------------------------------------------------------------- Floyd
class FloydResult:
    """dist matrix, nxt successor matrix, snapshots [D(0), ..., D(n)], changes per k, negative-cycle vertices."""

    def __init__(self, dist, nxt, snapshots, changes, negative_vertices):
        self.dist, self.nxt, self.snapshots = dist, nxt, snapshots
        self.changes, self.negative_vertices = changes, negative_vertices


def floyd(g, ops=None, keep_snapshots=True):
    """Floyd's algorithm. D(k)[i][j] = shortest i->j cost using only intermediates among the first k vertices.
    changes[k-1] = list of (i, j, old, new) improved while allowing vertex k-1 as an intermediate."""
    ops = Counter() if ops is None else ops
    n = g.n
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[j if i == j else -1 for j in range(n)] for i in range(n)]
    for u, v, w in g.edges:
        if u == v:
            dist[u][u] = min(0, w)                     # a negative self-loop is a negative cycle
        elif w < dist[u][v]:
            dist[u][v], nxt[u][v] = w, v
    snapshots = [[row[:] for row in dist]] if keep_snapshots else []
    changes = []
    for k in range(n):
        changed = []
        dk = dist[k]
        for i in range(n):
            dik = dist[i][k]
            if dik == INF:
                ops["floyd_cells"] += n                # the whole row is skipped but counted as examined
                continue
            di = dist[i]
            for j in range(n):
                ops["floyd_cells"] += 1
                if dik + dk[j] < di[j]:
                    changed.append((i, j, di[j], dik + dk[j]))
                    di[j], nxt[i][j] = dik + dk[j], nxt[i][k]
        changes.append(changed)
        if keep_snapshots:
            snapshots.append([row[:] for row in dist])
    negative = [i for i in range(n) if dist[i][i] < 0]
    return FloydResult(dist, nxt, snapshots, changes, negative)


def floyd_path(nxt, i, j):
    """Route i -> j from the successor matrix ([] if j is unreachable from i)."""
    if nxt[i][j] == -1:
        return []
    route = [i]
    while i != j:
        i = nxt[i][j]
        route.append(i)
        if len(route) > len(nxt) + 1:                  # only possible with a negative cycle
            return []
    return route


# ----------------------------------------------------------------------------- Warshall
def warshall(g, ops=None):
    """Transitive closure. Returns (R, snapshots [R(0)..R(n)], changes per k as lists of (i, j)).
    R[i][j] = 1 iff j can be reached from i by a path of >= 1 edge (R[i][i] = 1 iff i lies on a cycle)."""
    ops = Counter() if ops is None else ops
    n = g.n
    reach = [[0] * n for _ in range(n)]
    for u, v, _ in g.edges:
        reach[u][v] = 1
    snapshots, changes = [[row[:] for row in reach]], []
    for k in range(n):
        changed, rk = [], reach[k]
        for i in range(n):
            ri = reach[i]
            for j in range(n):
                ops["warshall_cells"] += 1
                if not ri[j] and ri[k] and rk[j]:
                    ri[j] = 1
                    changed.append((i, j))
        changes.append(changed)
        snapshots.append([row[:] for row in reach])
    return reach, snapshots, changes


def bfs_reachable(g, s):
    """Reference for Warshall: set of vertices reachable from s by >= 1 edge (breadth-first search)."""
    seen, queue = set(), deque([s])
    while queue:
        u = queue.popleft()
        for v, _ in g.adj[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return seen


# ----------------------------------------------------------------------------- production facade
def shortest_paths(g, source, ops=None):
    """Choose the algorithm from the data: Dijkstra if every weight is >= 0, otherwise Bellman-Ford.
    Returns (algorithm name, dist, pred); raises NegativeCycleError instead of returning misleading distances."""
    if not g.has_negative_edge():
        dist, pred, _ = dijkstra(g, source, ops)
        return "Dijkstra", dist, pred
    res = bellman_ford(g, source, ops)
    if res.has_negative_cycle:
        raise NegativeCycleError([g.names[v] for v in res.negative_cycle], res.cycle_weight)
    return "Bellman-Ford", res.dist, res.pred
