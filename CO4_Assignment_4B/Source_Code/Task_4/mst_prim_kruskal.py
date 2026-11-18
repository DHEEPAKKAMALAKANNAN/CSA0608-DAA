"""
Task 4 - Minimum spanning tree for the city fibre backbone: Prim and Kruskal.

Sites are vertices 0..n-1, candidate fibre routes are undirected weighted edges (u, v, w) with w = trench
length in units of 100 m. A minimum spanning tree (MST) connects all sites with minimum total trench length.

  prim_heap     Prim with an INDEXED binary min-heap (insert / decrease-key / extract-min), O(E log V)
  prim_array    Prim with a plain key array and a linear minimum scan, O(V^2 + E) - best for dense graphs
  kruskal       merge sort of the edges + union-find; mode 'rank+compress' (union by rank and path
                compression, O(E log E)), 'rank' or 'naive' (no rank, no compression) for the comparison
  mst_bruteforce  exact reference for small graphs: tries every (V-1)-edge subset
Disconnected input: Prim reaches only the root's component (reported); Kruskal returns a minimum spanning
FOREST with n - c edges; spanning_tree() raises ValueError because no spanning tree exists.
Run:  py -3 mst_prim_kruskal.py      (given test case with every Prim and Kruskal step, then edge cases)
"""
import csv
import itertools
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
INF = float("inf")


# ----------------------------------------------------------------------------- graph helpers
def load_graph(path):
    """CSV columns u, v, w (site codes). Returns (names, edges as (u_index, v_index, w))."""
    names, index, edges = [], {}, []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for s in (r["u"], r["v"]):
                if s not in index:
                    index[s] = len(names)
                    names.append(s)
            edges.append((index[r["u"]], index[r["v"]], int(r["w"])))
    return names, edges


def adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        if u != v:                                   # a self-loop can never be in a spanning tree
            adj[u].append((v, w))
            adj[v].append((u, w))
    return adj


def validate_graph(n, edges):
    if n < 1:
        raise ValueError("a network needs at least one site")
    for u, v, w in edges:
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError(f"edge ({u}, {v}) refers to an unknown site")


# ----------------------------------------------------------------------------- indexed heap for Prim
class IndexedMinHeap:
    """Binary min-heap over vertex ids with a position index, so decrease_key is O(log V)."""

    def __init__(self, n, ops):
        self.h, self.pos, self.key, self.ops = [], [-1] * n, [INF] * n, ops

    def __len__(self):
        return len(self.h)

    def __contains__(self, v):
        return self.pos[v] != -1

    def _swap(self, i, j):
        h = self.h
        h[i], h[j] = h[j], h[i]
        self.pos[h[i]], self.pos[h[j]] = i, j

    def _up(self, i):
        while i > 0:
            p = (i - 1) // 2
            self.ops["heap_comparisons"] += 1
            if self.key[self.h[i]] < self.key[self.h[p]]:
                self._swap(i, p)
                i = p
            else:
                break

    def _down(self, i):
        n = len(self.h)
        while True:
            s, l, r = i, 2 * i + 1, 2 * i + 2
            if l < n:
                self.ops["heap_comparisons"] += 1
                if self.key[self.h[l]] < self.key[self.h[s]]:
                    s = l
            if r < n:
                self.ops["heap_comparisons"] += 1
                if self.key[self.h[r]] < self.key[self.h[s]]:
                    s = r
            if s == i:
                return
            self._swap(i, s)
            i = s

    def insert(self, v, k):
        self.key[v] = k
        self.h.append(v)
        self.pos[v] = len(self.h) - 1
        self._up(len(self.h) - 1)

    def decrease_key(self, v, k):
        self.ops["decrease_keys"] += 1
        self.key[v] = k
        self._up(self.pos[v])

    def pop_min(self):
        top = self.h[0]
        self._swap(0, len(self.h) - 1)
        self.h.pop()
        self.pos[top] = -1
        if self.h:
            self._down(0)
        return top


# ----------------------------------------------------------------------------- Prim
def prim_heap(n, edges, root=0, ops=None, trace=None):
    """Returns (tree edges [(parent, v, w)], total weight, number of sites reached)."""
    ops = Counter() if ops is None else ops
    validate_graph(n, edges)
    adj = adjacency(n, edges)
    key, parent, in_tree = [INF] * n, [-1] * n, [False] * n
    heap = IndexedMinHeap(n, ops)
    key[root] = 0
    heap.insert(root, 0)
    tree, total, reached = [], 0, 0
    while heap:
        u = heap.pop_min()                          # greedy choice: lightest edge crossing the cut
        in_tree[u] = True
        reached += 1
        if parent[u] != -1:
            tree.append((parent[u], u, key[u]))
            total += key[u]
        updated = []
        for v, w in adj[u]:
            ops["edge_checks"] += 1
            if not in_tree[v] and w < key[v]:
                key[v], parent[v] = w, u
                if v in heap:
                    heap.decrease_key(v, w)
                else:
                    heap.insert(v, w)
                updated.append((v, w))
        if trace is not None:
            trace.append((u, parent[u], key[u], total, updated))
    return tree, total, reached


def prim_array(n, edges, root=0, ops=None):
    """Prim with an unsorted key array: n linear scans for the minimum, O(V^2 + E)."""
    ops = Counter() if ops is None else ops
    validate_graph(n, edges)
    adj = adjacency(n, edges)
    key, parent, in_tree = [INF] * n, [-1] * n, [False] * n
    key[root] = 0
    tree, total, reached = [], 0, 0
    for _ in range(n):
        u, best = -1, INF
        for v in range(n):
            ops["scan_comparisons"] += 1
            if not in_tree[v] and key[v] < best:
                u, best = v, key[v]
        if u == -1:                                  # the rest is unreachable: graph disconnected
            break
        in_tree[u] = True
        reached += 1
        if parent[u] != -1:
            tree.append((parent[u], u, key[u]))
            total += key[u]
        for v, w in adj[u]:
            ops["edge_checks"] += 1
            if not in_tree[v] and w < key[v]:
                key[v], parent[v] = w, u
    return tree, total, reached


# ----------------------------------------------------------------------------- Kruskal
class UnionFind:
    """Disjoint sets. mode: 'rank+compress' (default), 'rank' (union by rank only) or 'naive'."""

    def __init__(self, n, mode="rank+compress", ops=None):
        self.parent, self.rank, self.mode = list(range(n)), [0] * n, mode
        self.ops = Counter() if ops is None else ops
        self.sets = n

    def find(self, x):
        self.ops["find_calls"] += 1
        root = x
        while self.parent[root] != root:
            self.ops["pointer_hops"] += 1
            root = self.parent[root]
        if self.mode == "rank+compress":             # path compression: point every node at the root
            while self.parent[x] != root:
                self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        """Link the roots of a and b. Returns False if they are already in the same set (cycle)."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.ops["unions"] += 1
        if self.mode == "naive":
            self.parent[ra] = rb
        else:                                        # union by rank: shorter tree under taller tree
            if self.rank[ra] < self.rank[rb]:
                ra, rb = rb, ra
            self.parent[rb] = ra
            if self.rank[ra] == self.rank[rb]:
                self.rank[ra] += 1
        self.sets -= 1
        return True


def merge_sort_edges(edges, ops):
    """Stable merge sort by weight; counts weight comparisons in ops['sort_comparisons']."""
    if len(edges) <= 1:
        return list(edges)
    mid = len(edges) // 2
    left, right = merge_sort_edges(edges[:mid], ops), merge_sort_edges(edges[mid:], ops)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        ops["sort_comparisons"] += 1
        if right[j][2] < left[i][2]:
            out.append(right[j]); j += 1
        else:
            out.append(left[i]); i += 1
    return out + left[i:] + right[j:]


def kruskal(n, edges, mode="rank+compress", ops=None, trace=None):
    """Returns (forest edges, total weight, number of components). Stops after n-1 accepted edges."""
    ops = Counter() if ops is None else ops
    validate_graph(n, edges)
    uf = UnionFind(n, mode, ops)
    tree, total = [], 0
    for u, v, w in merge_sort_edges(list(edges), ops):
        if len(tree) == n - 1:                       # early stop: the tree is complete
            break
        ru, rv = uf.find(u), uf.find(v)
        if ru != rv:                                 # greedy choice: lightest edge joining two components
            uf.union(ru, rv)
            tree.append((u, v, w))
            total += w
            if trace is not None:
                trace.append((u, v, w, ru, rv, "ACCEPT", uf.sets))
        else:
            ops["cycle_rejections"] += 1
            if trace is not None:
                trace.append((u, v, w, ru, rv, "REJECT (cycle)", uf.sets))
    return tree, total, uf.sets


def spanning_tree(n, edges):
    """Kruskal that refuses disconnected networks (no spanning tree exists)."""
    tree, total, comps = kruskal(n, edges)
    if comps > 1:
        raise ValueError(f"network is disconnected ({comps} components): no spanning tree exists")
    return tree, total


def mst_bruteforce(n, edges):
    """Exact minimum by trying every subset of n-1 edges (small graphs only).
    Returns (minimum weight, number of distinct minimum spanning trees, number of spanning trees)."""
    best, count_best, count_trees = INF, 0, 0
    for combo in itertools.combinations(range(len(edges)), n - 1):
        uf = UnionFind(n)
        if all(uf.union(edges[i][0], edges[i][1]) for i in combo):
            count_trees += 1
            w = sum(edges[i][2] for i in combo)
            if w < best:
                best, count_best = w, 1
            elif w == best:
                count_best += 1
    return best, count_best, count_trees


def cut_property_holds(n, edges, tree):
    """Check: every tree edge is a lightest edge across the cut formed by removing it from the tree."""
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


# ----------------------------------------------------------------------------- demo
def main():
    names, edges = load_graph(os.path.join(HERE, "test_data", "given_G1_fibre_network.csv"))
    n = len(names)
    nm = lambda i: names[i]                          # noqa: E731
    print("TASK 4 - MINIMUM SPANNING TREE: city fibre backbone (weights = trench length x 100 m)")
    print("=" * 104)
    print(f"Given test case G1: {n} sites, {len(edges)} candidate routes")
    for k in range(0, len(edges), 7):
        print("  " + "  ".join(f"{nm(u)}-{nm(v)}:{w}" for u, v, w in edges[k:k + 7]))

    print("\nPrim (indexed binary heap, root EOC) - one row per site added to the tree")
    print(f"  {'step':>4} {'add site':<9} {'via edge':<13} {'w':>3} {'total':>5}  keys lowered (decrease-key / insert)")
    ops, trace = Counter(), []
    ptree, ptotal, _ = prim_heap(n, edges, 0, ops, trace)
    for k, (u, p, w, tot, upd) in enumerate(trace, 1):
        via = "(root)" if p == -1 else f"{nm(p)}-{nm(u)}"
        print(f"  {k:>4} {nm(u):<9} {via:<13} {w if p != -1 else 0:>3} {tot:>5}  "
              f"{', '.join(f'{nm(v)}={x}' for v, x in upd) or '-'}")
    print(f"  Prim total = {ptotal}; {ops['heap_comparisons']} heap comparisons, {ops['decrease_keys']} decrease-keys, "
          f"{ops['edge_checks']} edge checks")

    print("\nKruskal (edges in weight order, union-find with union by rank + path compression)")
    print(f"  {'step':>4} {'edge':<13} {'w':>3} {'find(u)':<9} {'find(v)':<9} {'decision':<15} {'components':>10}")
    kops, ktrace = Counter(), []
    ktree, ktotal, comps = kruskal(n, edges, ops=kops, trace=ktrace)
    for k, (u, v, w, ru, rv, dec, sets) in enumerate(ktrace, 1):
        print(f"  {k:>4} {nm(u) + '-' + nm(v):<13} {w:>3} {nm(ru):<9} {nm(rv):<9} {dec:<15} {sets:>10}")
    print(f"  Kruskal total = {ktotal}; stopped after {len(ktrace)} of {len(edges)} edges "
          f"({kops['sort_comparisons']} sort comparisons, {kops['pointer_hops']} pointer hops)")
    best, nbest, ntrees = mst_bruteforce(n, edges)
    print(f"\nVerification: Prim {ptotal} = Kruskal {ktotal} = brute force {best} over {ntrees:,} spanning trees "
          f"({nbest} distinct MSTs);")
    same = sorted(tuple(sorted(e[:2])) for e in ptree) == sorted(tuple(sorted(e[:2])) for e in ktree)
    print(f"  edge sets equal: {same}; cut property holds for Prim tree: {cut_property_holds(n, edges, ptree)}, "
          f"Kruskal tree: {cut_property_holds(n, edges, ktree)}")

    print("\nBoundary and failure cases")
    dn, de = load_graph(os.path.join(HERE, "test_data", "failure_F1_disconnected.csv"))
    t, w, reached = prim_heap(len(dn), de, 0)
    print(f"  F1 disconnected ({len(dn)} sites): Prim from {dn[0]} reaches only {reached} sites (weight {w}) -> "
          f"NOT spanning")
    ft, fw, fc = kruskal(len(dn), de)
    print(f"     Kruskal -> minimum spanning FOREST: {len(ft)} edges = n - c = {len(dn)} - {fc}, weight {fw}")
    print("        forest edges: " + ", ".join(f"{dn[u]}-{dn[v]}" for u, v, _ in ft))
    try:
        spanning_tree(len(dn), de)
    except ValueError as e:
        print(f"     spanning_tree() -> ValueError: {e}")
    cases = [("B1 one site", 1, []),
             ("B2 two sites, one route", 2, [(0, 1, 7)]),
             ("B3 parallel routes 0-1 (9 and 4) + self-loop", 3, [(0, 1, 9), (0, 1, 4), (1, 1, 1), (1, 2, 5)]),
             ("B4 all weights equal (K4, w = 3)", 4, [(a, b, 3) for a in range(4) for b in range(a + 1, 4)]),
             ("B5 negative weight (subsidised route)", 4, [(0, 1, 4), (1, 2, -2), (2, 3, 6), (0, 3, 5), (0, 2, 3)])]
    for name, cn, ce in cases:
        _, pw, pr = prim_heap(cn, ce)
        _, kw, kc = kruskal(cn, ce)
        ref = mst_bruteforce(cn, [e for e in ce if e[0] != e[1]])[0] if cn > 1 else 0
        print(f"  {name:<46} Prim {pw:>3}  Kruskal {kw:>3}  brute force {ref:>3}  (reached {pr}/{cn})")


if __name__ == "__main__":
    main()
