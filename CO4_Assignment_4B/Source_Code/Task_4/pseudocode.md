# Task 4 – Pseudocode: Minimum Spanning Tree (Prim and Kruskal)

Written before the implementation (`mst_prim_kruskal.py`). G = (V, E), w(u, v) = trench length.

## Prim with an indexed binary heap

```
Algorithm PrimHeap(G, r)
1. for each v in V do key[v] = infinity;  parent[v] = nil;  inTree[v] = false
2. key[r] = 0;  Q = indexed min-heap containing r
3. while Q not empty do
4.     u = ExtractMin(Q);  inTree[u] = true                   // greedy: lightest edge crossing the cut
5.     if parent[u] != nil then add edge (parent[u], u) to T
6.     for each (v, w) adjacent to u do
7.         if not inTree[v] and w < key[v] then
8.             key[v] = w;  parent[v] = u
9.             if v in Q then DecreaseKey(Q, v, w) else Insert(Q, v, w)
10. return T                                                  // |T| < |V| - 1  =>  graph disconnected
// O(E log V)
```

## Prim with a plain array (dense graphs)

```
Algorithm PrimArray(G, r)
1. key[v] = infinity for all v;  key[r] = 0
2. repeat |V| times
3.     u = vertex not in tree with the smallest key (linear scan)   // Theta(V) per round
4.     if key[u] = infinity then stop                          // disconnected
5.     add u (and edge parent[u]-u) to the tree
6.     for each (v, w) adjacent to u do if v not in tree and w < key[v] then key[v] = w;  parent[v] = u
// O(V^2 + E)
```

## Kruskal with union–find (union by rank + path compression)

```
Algorithm Kruskal(G)
1. sort E by weight                                           // Theta(E log E)
2. for each v in V do MakeSet(v)
3. T = empty
4. for each edge (u, v, w) in sorted order while |T| < |V| - 1 do
5.     ru = Find(u);  rv = Find(v)
6.     if ru != rv then add (u, v, w) to T;  Union(ru, rv)     // greedy: lightest edge, no cycle
7.     else reject (u, v, w)                                   // it would close a cycle
8. return T                                                   // spanning forest if disconnected

Algorithm Find(x)
1. root = x;  while parent[root] != root do root = parent[root]
2. while parent[x] != root do next = parent[x];  parent[x] = root;  x = next   // path compression
3. return root

Algorithm Union(a, b)                              // a, b are roots
1. if rank[a] < rank[b] then swap a, b
2. parent[b] = a;  if rank[a] = rank[b] then rank[a] = rank[a] + 1
```
