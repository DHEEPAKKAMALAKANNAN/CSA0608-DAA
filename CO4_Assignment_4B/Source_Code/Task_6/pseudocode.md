# Task 6 – Pseudocode: TSP by Dynamic Programming (Held–Karp)

Vertex 0 is the distribution hub, vertices 1..n are the delivery locations, c(i, j) ≥ 0 is the travel cost
(∞ = no road). S ⊆ {1..n} is stored as a bitmask (bit j−1 ⇔ location j ∈ S).

```
Algorithm HeldKarp(c, n)
// DP[S][j] = cheapest path that starts at the hub, visits exactly the locations of S and ends at j (j ∈ S)
1.  ValidateCostMatrix(c)                         // square, n ≥ 1, c ≥ 0, diagonal 0, else reject
2.  for j = 1 to n do                             // base states: one location visited
3.      DP[{j}][j] = c(0, j);  PARENT[{j}][j] = 0
4.  for S = 1 to 2^n − 1 in increasing bitmask order with |S| ≥ 2 do
5.      for every j ∈ S do
6.          DP[S][j] = ∞
7.          for every k ∈ S − {j} do              // one transition
8.              if DP[S − {j}][k] + c(k, j) < DP[S][j] then
9.                  DP[S][j] = DP[S − {j}][k] + c(k, j);  PARENT[S][j] = k
10. OPT = min over j of DP[ALL][j] + c(j, 0);  last = the minimising j     // return to the hub
11. if OPT = ∞ then return "no feasible tour"
12. route = [0];  S = ALL;  j = last
13. while j ≠ 0 do                                // walk the PARENT pointers backwards
14.     append j to route;  (S, j) = (S − {j}, PARENT[S][j])
15. append 0 to route;  reverse(route)
16. return OPT, route
```

States evaluated: n·2ⁿ⁻¹. Transitions: Σₛ C(n, s)·s·(s − 1) = n(n − 1)·2ⁿ⁻² (+ n closing edges).
Time Θ(n²·2ⁿ), memory Θ(n·2ⁿ).

```
Algorithm ExhaustiveTSP(c, n)                    // independent reference for Task 6.4
1.  best = ∞;  bestRoutes = []
2.  for every permutation p of (1, 2, ..., n) do  // n! routes
3.      cost = c(0, p1) + c(p1, p2) + ... + c(pn, 0)
4.      if cost < best then best = cost;  bestRoutes = [p]
5.      else if cost = best then append p to bestRoutes
6.  return best, bestRoutes
```

Time Θ(n·n!), memory Θ(n).
