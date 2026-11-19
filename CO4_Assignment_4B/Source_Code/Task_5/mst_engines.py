"""
Task 5 - Three greedy engineers, one network: Kruskal, Prim and Boruvka minimum spanning trees.

Problem: a company must connect all of its facilities (vertices) with cable/fibre links (undirected weighted
edges, weight = installation cost) so that every facility is reachable and the total cost is minimum.
That is the minimum spanning tree (MST) problem. All three algorithms add a SAFE edge (a lightest edge
crossing some cut that respects the current partial solution - the cut property), but they choose the cut
differently:
  kruskal  - global view: edges in increasing weight order; accept an edge iff it joins two different
             components (union-find with union by rank + path compression). Partial solution = forest.
  prim     - local view: one tree grown from a root; next edge = lightest edge leaving the tree
             (indexed binary min-heap with decrease-key). Partial solution = one connected tree.
  boruvka  - component view: in every round EACH component picks its cheapest outgoing edge, all of them are
             added at once and components merge (at least halving per round). Ties are broken by the total
             order (weight, min(u,v), max(u,v), edge index) so simultaneous choices never create a cycle.
Reference / validation helpers: mst_bruteforce (tries all (V-1)-edge subsets), enumerate_msts (lists every
MST of a small graph), is_spanning_tree, cut_property_holds, cycle_property_holds.
Algorithm logic only: no printing here (drivers: mst_construction_demo.py, mst_multiple_msts.py,
mst_experiments.py). Every core returns an MSTResult with the edges, total cost, number of components
(1 = spanning tree, >1 = minimum spanning FOREST of a disconnected network), operation counters and a trace.
"""
import csv
import itertools
import math
from collections import Counter, namedtuple

INF = float("inf")
MSTResult = namedtuple("MSTResult", "algorithm edges total components ops trace")


# ----------------------------------------------------------------------------- graph model
class Network:
    """Undirected weighted network of named facilities. edges: list of (u, v, w) with vertex indices."""

    def __init__(self, names, edges):
        self.names = list(names)
        self.index = {name: i for i, name in enumerate(self.names)}
        self.edges = [(u, v, w) for u, v, w in edges]
        validate_network(len(self.names), self.edges)

    @property
    def n(self):
        return len(self.names)

    @classmethod
    def from_named_edges(cls, named_edges, names=None):
        """Build from [(name_u, name_v, w)]; vertex order = `names` if given, else first appearance."""
        order = list(names) if names else []
        for a, b, _ in named_edges:
            for s in (a, b):
                if s not in order:
                    order.append(s)
        pos = {s: i for i, s in enumerate(order)}
        return cls(order, [(pos[a], pos[b], w) for a, b, w in named_edges])

    @classmethod
    def from_csv(cls, path):
        """CSV with columns u, v, w (facility codes, numeric cost)."""
        with open(path, newline="", encoding="utf-8") as f:
            rows = [(r["u"].strip(), r["v"].strip(), float(r["w"]) if "." in r["w"] else int(r["w"]))
                    for r in csv.DictReader(f)]
        return cls.from_named_edges(rows)

    def edge_label(self, e):
        return f"{self.names[e[0]]}-{self.names[e[1]]}"


def validate_network(n, edges):
    """Reject inputs no MST algorithm can interpret: no vertices, unknown endpoints, non-numeric/NaN/inf costs."""
    if n < 1:
        raise ValueError("a network needs at least one facility")
    for u, v, w in edges:
        if not (isinstance(u, int) and isinstance(v, int) and 0 <= u < n and 0 <= v < n):
            raise ValueError(f"edge ({u}, {v}) refers to an unknown facility")
        if isinstance(w, bool) or not isinstance(w, (int, float)) or math.isnan(w) or math.isinf(w):
            raise ValueError(f"edge ({u}, {v}) has an invalid cost {w!r}")


def edge_key(edges, i):
    """Total order used for every tie-break: (weight, smaller endpoint, larger endpoint, input index)."""
    u, v, w = edges[i]
    return (w, min(u, v), max(u, v), i)


def canonical(edge_list):
    """Edge set without orientation/weight noise - used to compare trees returned by different algorithms."""
    return frozenset((min(u, v), max(u, v), w) for u, v, w in edge_list)


# ----------------------------------------------------------------------------- union-find
class UnionFind:
    """Disjoint sets with union by rank and path compression; counts find calls and pointer hops."""

    def __init__(self, n, ops=None):
        self.parent, self.rank, self.sets = list(range(n)), [0] * n, n
        self.ops = Counter() if ops is None else ops

    def find(self, x):
        self.ops["finds"] += 1
        root = x
        while self.parent[root] != root:
            self.ops["pointer_hops"] += 1
            root = self.parent[root]
        while self.parent[x] != root:                  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.sets -= 1
        self.ops["unions"] += 1
        return True


# ----------------------------------------------------------------------------- Kruskal
def merge_sort_indices(edges, ops):
    """Stable merge sort of edge indices by weight (equal weights keep input order); counts comparisons."""
    def sort(idx):
        if len(idx) <= 1:
            return idx
        mid = len(idx) // 2
        left, right = sort(idx[:mid]), sort(idx[mid:])
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            ops["sort_comparisons"] += 1
            if edges[right[j]][2] < edges[left[i]][2]:
                out.append(right[j]); j += 1
            else:
                out.append(left[i]); i += 1
        return out + left[i:] + right[j:]
    return sort(list(range(len(edges))))


def kruskal(n, edges):
    """Kruskal. trace rows: (edge, find(u), find(v), 'ACCEPT'/'REJECT', components after).
    Equal-weight edges are processed in input order (stable sort) - this is what lets it pick a different
    (equally correct) tree from Prim or Boruvka when weights tie."""
    validate_network(n, edges)
    ops, trace = Counter(), []
    uf = UnionFind(n, ops)
    order = merge_sort_indices(edges, ops)
    tree, total = [], 0
    for i in order:
        if len(tree) == n - 1:                         # tree complete: remaining edges never examined
            break
        u, v, w = edges[i]
        ops["edges_examined"] += 1
        ru, rv = uf.find(u), uf.find(v)
        if ru != rv:
            uf.union(ru, rv)
            tree.append(edges[i])
            total += w
            trace.append((edges[i], ru, rv, "ACCEPT", uf.sets))
        else:
            ops["cycle_rejections"] += 1
            trace.append((edges[i], ru, rv, "REJECT", uf.sets))
    return MSTResult("Kruskal", tree, total, uf.sets, ops, trace)


# ----------------------------------------------------------------------------- Prim
class IndexedMinHeap:
    """Binary min-heap over vertex ids with a position index (decrease_key in O(log V))."""

    def __init__(self, n, ops):
        self.h, self.pos, self.key, self.ops = [], [-1] * n, [INF] * n, ops

    def __len__(self):
        return len(self.h)

    def __contains__(self, v):
        return self.pos[v] != -1

    def _less(self, a, b):
        self.ops["heap_comparisons"] += 1
        return (self.key[a], a) < (self.key[b], b)

    def _swap(self, i, j):
        h = self.h
        h[i], h[j] = h[j], h[i]
        self.pos[h[i]], self.pos[h[j]] = i, j

    def _up(self, i):
        while i > 0 and self._less(self.h[i], self.h[(i - 1) // 2]):
            self._swap(i, (i - 1) // 2)
            i = (i - 1) // 2

    def _down(self, i):
        n = len(self.h)
        while True:
            s, l, r = i, 2 * i + 1, 2 * i + 2
            if l < n and self._less(self.h[l], self.h[s]):
                s = l
            if r < n and self._less(self.h[r], self.h[s]):
                s = r
            if s == i:
                return
            self._swap(i, s)
            i = s

    def push_or_decrease(self, v, k):
        self.key[v] = k
        if v in self:
            self.ops["decrease_keys"] += 1
            self._up(self.pos[v])
        else:
            self.ops["heap_inserts"] += 1
            self.h.append(v)
            self.pos[v] = len(self.h) - 1
            self._up(len(self.h) - 1)

    def pop_min(self):
        self.ops["heap_extracts"] += 1
        top = self.h[0]
        self._swap(0, len(self.h) - 1)
        self.h.pop()
        self.pos[top] = -1
        if self.h:
            self._down(0)
        return top


def adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for i, (u, v, w) in enumerate(edges):
        if u != v:                                     # a self-loop can never be part of a tree
            adj[u].append((v, w, i))
            adj[v].append((u, w, i))
    return adj


def prim(n, edges, root=0):
    """Prim from `root`. trace rows: (vertex added, tree edge or None, cost so far, [(v, new key, via)], frontier
    size). Vertices outside root's component are never reached -> components > 1 is reported."""
    validate_network(n, edges)
    if not 0 <= root < n:
        raise ValueError(f"root {root} is not a facility")
    ops, trace = Counter(), []
    adj = adjacency(n, edges)
    key, via, in_tree = [INF] * n, [None] * n, [False] * n
    heap = IndexedMinHeap(n, ops)
    key[root] = 0
    heap.push_or_decrease(root, 0)
    tree, total, reached = [], 0, 0
    while heap:
        u = heap.pop_min()                             # safe edge: lightest edge leaving the tree
        in_tree[u] = True
        reached += 1
        if via[u] is not None:
            tree.append(edges[via[u]])
            total += edges[via[u]][2]
        updated = []
        for v, w, i in adj[u]:
            ops["edge_scans"] += 1
            if not in_tree[v] and w < key[v]:          # strict <: on a tie the first-found edge is kept
                key[v], via[v] = w, i
                heap.push_or_decrease(v, w)
                updated.append((v, w, u))
        trace.append((u, edges[via[u]] if via[u] is not None else None, total, updated, len(heap)))
    return MSTResult(f"Prim(root={root})", tree, total, n - reached + 1, ops, trace)


def prim_array(n, edges, root=0):
    """Prim with a plain key array and a linear minimum scan: O(V^2 + E) - the dense-graph variant."""
    validate_network(n, edges)
    ops = Counter()
    adj = adjacency(n, edges)
    key, via, in_tree = [INF] * n, [None] * n, [False] * n
    key[root] = 0
    tree, total, reached = [], 0, 0
    for _ in range(n):
        u, best = -1, INF
        for v in range(n):
            ops["scan_comparisons"] += 1
            if not in_tree[v] and key[v] < best:
                u, best = v, key[v]
        if u == -1:
            break
        in_tree[u] = True
        reached += 1
        if via[u] is not None:
            tree.append(edges[via[u]])
            total += edges[via[u]][2]
        for v, w, i in adj[u]:
            ops["edge_scans"] += 1
            if not in_tree[v] and w < key[v]:
                key[v], via[v] = w, i
    return MSTResult(f"Prim-array(root={root})", tree, total, n - reached + 1, ops, [])


# ----------------------------------------------------------------------------- Boruvka
def boruvka(n, edges):
    """Boruvka. trace rows per round: (round, components before, [(component members, cheapest edge)],
    edges added this round, components after, edges scanned this round)."""
    validate_network(n, edges)
    ops, trace = Counter(), []
    uf = UnionFind(n, ops)
    tree, total, rnd = [], 0, 0
    while uf.sets > 1:
        rnd += 1
        before = uf.sets
        cheapest = {}                                  # component root -> index of its cheapest outgoing edge
        members = {}                                   # component root -> its facilities (for the trace)
        for x in range(n):
            members.setdefault(uf.find(x), []).append(x)
        ops["finds"] -= n                              # trace bookkeeping is not algorithmic work
        for i, (u, v, w) in enumerate(edges):         # one independent scan per round
            ops["edge_scans"] += 1
            ru, rv = uf.find(u), uf.find(v)
            if ru == rv:
                continue
            k = edge_key(edges, i)
            for r in (ru, rv):
                ops["key_comparisons"] += 1
                if r not in cheapest or k < edge_key(edges, cheapest[r]):
                    cheapest[r] = i
        if not cheapest:                               # no component has an outgoing edge: disconnected
            break
        added = []
        for r in sorted(cheapest, key=lambda c: edge_key(edges, cheapest[c])):
            i = cheapest[r]
            if uf.union(edges[i][0], edges[i][1]):     # the same edge may be chosen by both components
                tree.append(edges[i])
                total += edges[i][2]
                added.append(edges[i])
        trace.append((rnd, before, [(members[r], edges[i]) for r, i in sorted(cheapest.items(),
                      key=lambda kv: members[kv[0]])], added, uf.sets, len(edges)))
    ops["rounds"] = rnd
    return MSTResult("Boruvka", tree, total, uf.sets, ops, trace)


# ----------------------------------------------------------------------------- policy + validation helpers
def require_spanning_tree(result, names=None):
    """Production policy: a disconnected network has no spanning tree -> raise instead of a misleading tree."""
    if result.components > 1:
        raise ValueError(f"{result.algorithm}: no spanning tree - {result.components} components "
                         f"(partial forest cost {result.total})")
    return result


def is_spanning_tree(n, tree):
    if len(tree) != n - 1:
        return False
    uf = UnionFind(n)
    return all(uf.union(u, v) for u, v, _ in tree)


def mst_bruteforce(n, edges):
    """Exact reference: every subset of n-1 edges. Returns (min cost, number of MSTs, number of spanning trees)."""
    loops_free = [e for e in edges if e[0] != e[1]]
    if n == 1:
        return 0, 1, 1
    best, count_best, count_trees = INF, 0, 0
    for combo in itertools.combinations(loops_free, n - 1):
        if is_spanning_tree(n, combo):
            count_trees += 1
            w = sum(e[2] for e in combo)
            if w < best:
                best, count_best = w, 1
            elif w == best:
                count_best += 1
    return best, count_best, count_trees


def enumerate_msts(n, edges):
    """All distinct minimum spanning trees (as canonical edge sets) of a small graph."""
    best, _, _ = mst_bruteforce(n, edges)
    found = set()
    for combo in itertools.combinations([e for e in edges if e[0] != e[1]], n - 1):
        if sum(e[2] for e in combo) == best and is_spanning_tree(n, combo):
            found.add(canonical(combo))
    return best, sorted(found, key=lambda s: sorted(s))


def cut_property_holds(n, edges, tree):
    """Every tree edge is a lightest edge across the cut obtained by deleting it from the tree."""
    for t in tree:
        uf = UnionFind(n)
        for e in tree:
            if e is not t:
                uf.union(e[0], e[1])
        side = uf.find(t[0])
        crossing = [w for u, v, w in edges if (uf.find(u) == side) != (uf.find(v) == side)]
        if t[2] > min(crossing):
            return False
    return True


def cycle_property_holds(n, edges, tree):
    """Every non-tree edge is a heaviest edge on the cycle it closes with the tree (no improving swap)."""
    tset = canonical(tree)
    adj = [[] for _ in range(n)]
    for u, v, w in tree:
        adj[u].append((v, w))
        adj[v].append((u, w))

    def max_on_path(s, t):                             # DFS in the tree, track the heaviest edge
        stack, seen = [(s, -INF)], {s}
        while stack:
            x, m = stack.pop()
            if x == t:
                return m
            for y, w in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append((y, max(m, w)))
        return INF
    return all(w >= max_on_path(u, v) for u, v, w in edges
               if u != v and (min(u, v), max(u, v), w) not in tset)
