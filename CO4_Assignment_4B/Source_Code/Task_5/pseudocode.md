# Task 5 – Pseudocode: Kruskal, Prim and Borůvka

All three algorithms add only **safe edges**: a lightest edge crossing a cut that no chosen edge crosses
(cut property). They differ in which cut they look at and in the data structure that finds the edge.
Flowcharts: `Report/Screenshots/t5_flowchart_kruskal.png`, `t5_flowchart_prim.png`, `t5_flowchart_boruvka.png`.

```
Algorithm Kruskal(V, E)
1.  sort E by cost (stable: equal costs keep input order)
2.  for each v in V do MakeSet(v)                       // union-find: parent[v] = v, rank[v] = 0
3.  T = {}
4.  for each (u, v, w) in sorted E do
5.      if |T| = |V| - 1 then break                      // tree complete: stop early
6.      ru = Find(u);  rv = Find(v)                      // path compression
7.      if ru != rv then                                 // ends in different components -> safe edge
8.          T = T ∪ {(u, v, w)};  Union(ru, rv)          // union by rank: forest merges
9.      else reject (u, v, w)                            // would close a cycle
10. if |T| < |V| - 1 then report "disconnected: T is a minimum spanning forest"
11. return T, Σ w(T)
```

```
Algorithm Prim(V, E, r)
1.  for each v in V do key[v] = ∞;  via[v] = none;  inTree[v] = false
2.  key[r] = 0;  H = indexed min-heap containing r
3.  T = {}
4.  while H is not empty do
5.      u = ExtractMin(H);  inTree[u] = true             // lightest edge leaving the tree
6.      if via[u] != none then T = T ∪ {via[u]}
7.      for each link (u, v, w) do
8.          if not inTree[v] and w < key[v] then         // strict <: first-found edge kept on a tie
9.              key[v] = w;  via[v] = (u, v, w)
10.             if v in H then DecreaseKey(H, v, w) else Insert(H, v, w)
11. if |T| < |V| - 1 then report "disconnected: only r's component was reached"
12. return T, Σ w(T)
```

```
Algorithm Boruvka(V, E)
1.  for each v in V do MakeSet(v)                        // |V| components
2.  T = {}
3.  while number of components > 1 do
4.      cheapest[c] = none for every component c
5.      for each (u, v, w) in E do                       // one pass over all links per round
6.          cu = Find(u);  cv = Find(v)
7.          if cu != cv then
8.              for c in {cu, cv} do
9.                  if cheapest[c] = none or (w, u, v) < key(cheapest[c]) then
10.                     cheapest[c] = (u, v, w)           // total order (cost, u, v) breaks ties
11.     if no cheapest edge exists then
12.         report "disconnected: T is a minimum spanning forest";  break
13.     for each component c with cheapest[c] = (u, v, w) do
14.         if Union(u, v) then T = T ∪ {(u, v, w)}       // edge chosen by both ends is added once
15. return T, Σ w(T)                                     // ≤ ⌈log₂ |V|⌉ rounds (components at least halve)
```

Complexities (V facilities, E links): Kruskal O(E log E) for the sort + O(E α(V)) union-find;
Prim O((V + E) log V) with a binary heap (O(V² + E) with a plain key array); Borůvka O(E log V)
(≤ ⌈log₂ V⌉ rounds × one O(E) scan), with the per-component searches of a round independent of each other.
