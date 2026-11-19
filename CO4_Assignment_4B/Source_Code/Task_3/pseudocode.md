# Task 3 – Pseudocode of the routing engine

Notation: G = (V, E, w) directed, n = |V|, m = |E|; `inf` = unreachable. Implemented in `routing_engine.py`.

```
Algorithm Dijkstra(G, s)                         // requires w(u, v) >= 0 for every edge
1. for each v in V do dist[v] = inf;  pred[v] = nil;  final[v] = false
2. dist[s] = 0;  H = min-heap;  push(H, (0, s));  order = []
3. while H is not empty do
4.     (d, u) = extract-min(H)
5.     if final[u] or d > dist[u] then continue          // stale heap entry
6.     final[u] = true;  append u to order               // greedy commitment
7.     for each edge (u, v, w) do
8.         if not final[v] and dist[u] + w < dist[v] then
9.             dist[v] = dist[u] + w;  pred[v] = u;  push(H, (dist[v], v))
10. return dist, pred, order
```

```
Algorithm BellmanFord(G, s)
1. for each v in V do dist[v] = inf;  pred[v] = nil
2. dist[s] = 0
3. for k = 1 to n - 1 do
4.     updated = false
5.     for each edge (u, v, w) in E do
6.         if dist[u] != inf and dist[u] + w < dist[v] then
7.             dist[v] = dist[u] + w;  pred[v] = u;  updated = true
8.     if not updated then break                        // early exit
9. for each edge (u, v, w) in E do                      // detection pass |V|
10.    if dist[u] != inf and dist[u] + w < dist[v] then
11.        pred[v] = u;  x = v
12.        repeat n times: x = pred[x]                  // now x lies on the cycle
13.        cycle = vertices met following pred from x until x repeats
14.        affected = all vertices reachable from cycle;  dist[a] = -inf for a in affected
15.        return NEGATIVE-CYCLE(cycle, weight(cycle), affected)
16. return dist, pred
```

```
Algorithm Floyd(W[1..n, 1..n])                    // W[i][i] = 0, W[i][j] = inf if no road
1. D = W
2. for i = 1 to n do for j = 1 to n do nxt[i][j] = j if W[i][j] < inf else nil
3. for k = 1 to n do
4.     for i = 1 to n do
5.         for j = 1 to n do
6.             if D[i][k] + D[k][j] < D[i][j] then
7.                 D[i][j] = D[i][k] + D[k][j];  nxt[i][j] = nxt[i][k]
8. if D[i][i] < 0 for some i then report NEGATIVE CYCLE through i
9. return D, nxt                     // route i -> j: i, nxt[i][j], nxt[nxt[i][j]][j], ..., j
```

```
Algorithm Warshall(A[1..n, 1..n])                 // A[i][j] = 1 iff road i -> j
1. R = A
2. for k = 1 to n do
3.     for i = 1 to n do
4.         for j = 1 to n do
5.             R[i][j] = R[i][j] or (R[i][k] and R[k][j])
6. return R                          // R[i][j] = 1 iff j is reachable from i
```

```
Algorithm ShortestPaths(G, s)                     // production facade
1. if every w(u, v) >= 0 then return Dijkstra(G, s)
2. result = BellmanFord(G, s)
3. if result is NEGATIVE-CYCLE then raise NegativeCycleError(cycle, weight)
4. return result
```
