# Task 6 – Pseudocode: Final Design of the Ambulance Route Service

Written after the defects of the given code were isolated and before `fixed_route_service.py` was written.
The comments name the defect (D1–D5) that each line removes.

## Nightly rebuild and validated feed

```
Algorithm Build(n, R)                             // R = roads (u, v, t), t >= 0
1. adj[v] = empty list for v = 0..n-1;  index = empty map
2. for each (u, v, t) in R do
3.     if u or v not in 0..n-1 or t < 0 then error             // D5: validate input
4.     e = [v, t];  append e to adj[u];  index[(u, v)] = e      // D4: O(1) access, no list scans
5. calibrate()                                                 // s/km lower bound for A*

Algorithm ApplyFeed(U)                            // U = [(u, v, t)], t = -1 means "closed"
1. for each (u, v, t) in U do                                 // D5: validate the whole feed first (atomic)
2.     if (u, v) not in index or (t < 0 and t != -1) then error
3. for each (u, v, t) in U do
4.     if t = -1 then index[(u, v)].t = infinity              // closed: never relaxed, can be reopened
5.     else index[(u, v)].t = t                                // D4: O(1) per record
6. calibrate()
```

## Route query (Dijkstra, or A* when coordinates are known)

```
Algorithm Route(src, dst, method)
1. if src or dst unknown then error                           // D5
2. h(v) = 0 for Dijkstra;  h(v) = straightKm(v, dst) * minSecPerKm for A*   // never overestimates
3. dist = {src: 0};  prev = {};  H = min-heap {(h(src), 0, src)}
4. while H not empty do
5.     (f, g, u) = ExtractMin(H)
6.     if g > dist[u] then continue                           // D2: skip stale heap entries
7.     if u = dst then return g, Path(prev, src, dst)          // D1: stop when dst is SETTLED
8.     for each [v, t] in adj[u] do                           // D4: only u's own roads
9.         if g + t < dist.get(v, infinity) then
10.            dist[v] = g + t;  prev[v] = u;  Insert(H, (g + t + h(v), g + t, v))
11. return infinity, none                                      // D3: unreachable is an answer, not a crash

Algorithm Path(prev, src, dst)
1. P = [dst];  while last(P) != src do append prev[last(P)] to P   // D3: include src
2. return reverse(P)                                           // D3: travel order
```
Cost per day: Build + ApplyFeed = O(V + E + |U|); each query O((V' + E') log V') where V', E' are the
junctions and roads actually reached before dst is settled (A* reduces V').
