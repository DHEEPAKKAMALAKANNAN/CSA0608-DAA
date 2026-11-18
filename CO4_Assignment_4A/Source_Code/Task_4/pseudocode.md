# Task 4 – Pseudocode: Floyd's Algorithm (all-pairs shortest paths, path reconstruction, negative cycles)

Written before the implementation (`floyd_shortest_paths.py`). W[1..n, 1..n] = weight matrix
(W[i][i] = 0, W[i][j] = ∞ when there is no street i → j).

## DP formulation
- **State:** D(k)[i][j] = length of the shortest i → j path whose intermediate vertices are all numbered ≤ k.
- **Recurrence:** D(k)[i][j] = min( D(k−1)[i][j], D(k−1)[i][k] + D(k−1)[k][j] ).
- **Base case:** D(0) = W.
- **Order of computation:** k = 1 … n outer loop; all (i, j) inside. Row k and column k are unchanged in iteration k
  (D[k][k] = 0 when there is no negative cycle), so one matrix is updated in place.
- **Answer:** D(n). A value D(n)[i][i] < 0 proves a negative cycle through i — shortest paths are then undefined.

## 1. Floyd with predecessor matrix
```
Algorithm Floyd(W[1..n, 1..n])
// Output: distance matrix D and predecessor matrix P
1. D = W
2. for i = 1 to n do for j = 1 to n do
3.     P[i][j] = i if (i != j and W[i][j] < inf) else NIL
4. for k = 1 to n do
5.     for i = 1 to n do
6.         for j = 1 to n do                                   // one comparison (count): n^3 in total
7.             if D[i][k] + D[k][j] < D[i][j] then
8.                 D[i][j] = D[i][k] + D[k][j]                 // improvement (count)
9.                 P[i][j] = P[k][j]                           // last hop of the k -> j part
10. return D, P
```

## 2. Path reconstruction
```
Algorithm ReconstructPath(P, i, j)
1. if i = j then return [i]
2. if P[i][j] = NIL then return []                             // j unreachable from i
3. path = [j];  v = j
4. while v != i do
5.     v = P[i][v];  insert v at the front of path
6. return path
```

## 3. Negative-cycle check (failure case)
```
Algorithm NegativeCycleReport(D)
1. Bad = { v : D[v][v] < 0 }                                   // v lies on a negative cycle
2. Unbounded = { (i, j) : some v in Bad with D[i][v] < inf and D[v][j] < inf }
3. if Bad is not empty then report "negative cycle - distances undefined" and reject the data
4. return Bad, Unbounded
```

## 4. Reference for verification (Bellman–Ford from source s)
```
Algorithm BellmanFord(W, s)
1. dist[v] = inf for all v;  dist[s] = 0
2. repeat n - 1 times
3.     for each street (u, v) do dist[v] = min(dist[v], dist[u] + W[u][v])
4. if some street can still be relaxed then report a negative cycle
5. return dist
```
Costs: Floyd Θ(n³) time, Θ(n²) space (D and P); path reconstruction O(n) per pair; Bellman–Ford Θ(nm) per source.
