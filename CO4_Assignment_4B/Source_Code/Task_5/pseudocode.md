# Task 5 – Pseudocode: Dijkstra's Algorithm for Ambulance Routing

Written before the implementation (`dijkstra_routing.py`). Directed roads, w(u, v) >= 0 = minutes.

## Array version, O(V² + E)

```
Algorithm DijkstraArray(G, s)
1. for each v in V do dist[v] = infinity;  prev[v] = nil;  done[v] = false
2. dist[s] = 0
3. repeat |V| times
4.     u = the vertex with done[u] = false and the smallest dist (linear scan)   // greedy choice
5.     if dist[u] = infinity then stop                         // the rest is unreachable
6.     done[u] = true                                          // dist[u] is now final
7.     for each road (u, v, w) do
8.         if not done[v] and dist[u] + w < dist[v] then dist[v] = dist[u] + w;  prev[v] = u   // relax
9. return dist, prev
```

## Binary-heap version with lazy deletion, O((V + E) log V)

```
Algorithm DijkstraHeap(G, s, target = none)
1. if some w(u, v) < 0 then error "Dijkstra requires non-negative weights"
2. dist[v] = infinity for all v;  dist[s] = 0;  H = min-heap {(0, s)}
3. while H not empty do
4.     (d, u) = ExtractMin(H)
5.     if done[u] or d > dist[u] then continue                 // stale entry: skip
6.     done[u] = true
7.     if u = target then stop                                 // early exit once the target is settled
8.     for each road (u, v, w) do
9.         if not done[v] and d + w < dist[v] then
10.            dist[v] = d + w;  prev[v] = u;  Insert(H, (dist[v], v))
11. return dist, prev
```

## Route reconstruction and the reference algorithm

```
Algorithm PathTo(prev, s, t)
1. if dist[t] = infinity then return none
2. P = [t];  while last(P) != s do append prev[last(P)] to P
3. return reverse(P)

Algorithm BellmanFord(G, s)                      // correct with negative weights, O(VE)
1. dist[v] = infinity for all v;  dist[s] = 0
2. repeat |V| - 1 times: for each road (u, v, w) do if dist[u] + w < dist[v] then dist[v] = dist[u] + w
3. if some road can still be relaxed then report "negative cycle"
4. return dist
```
