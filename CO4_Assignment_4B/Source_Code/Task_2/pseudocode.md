# Task 2 – Pseudocode: Greedy Knapsack and Coin Change

Written before the implementation (`knapsack_coin_change.py`).

## (a) Fractional knapsack – divisible relief supplies

```
Algorithm FractionalKnapsack(I, n, W)             // I[i] = (w_i, v_i), capacity W
1. sort I by density v_i / w_i, largest first                // Theta(n log n)
2. room = W;  value = 0
3. for i = 1 to n while room > 0 do
4.     x = min(1, room / I[i].w)                              // greedy choice: densest item first
5.     value = value + x * I[i].v;  room = room - x * I[i].w
6. return value                                               // at most one item is taken fractionally

Algorithm FractionalKnapsackHeap(I, n, W)         // optimisation when only k << n items fit
1. build a max-heap H of I keyed by density (bottom-up)       // <= 2n comparisons
2. room = W;  value = 0
3. while room > 0 and H not empty do
4.     it = ExtractMax(H)                                     // O(log n) each, only k times
5.     x = min(1, room / it.w);  value = value + x * it.v;  room = room - x * it.w
6. return value                                               // Theta(n + k log n)
```

## (b) 0/1 knapsack – indivisible equipment

```
Algorithm Greedy01(I, n, W, rule)                 // rule = density | value | lightest
1. sort I by the rule
2. room = W;  value = 0
3. for i = 1 to n do
4.     if I[i].w <= room then take I[i];  room = room - I[i].w;  value = value + I[i].v
5. return value                                               // NOT optimal in general

Algorithm Knapsack01DP(I, n, W)                   // exact reference, Theta(nW)
1. B[0][c] = 0 for c = 0..W
2. for i = 1 to n do
3.     for c = 0 to W do
4.         B[i][c] = B[i-1][c]
5.         if I[i].w <= c then B[i][c] = max(B[i][c], B[i-1][c - I[i].w] + I[i].v)
6. return B[n][W]
```

## (c) Coin change

```
Algorithm GreedyChange(C, m, A)                   // coins C[1..m], amount A
1. sort C in decreasing order;  used = empty
2. for j = 1 to m do
3.     k = floor(A / C[j]);  add k coins C[j] to used;  A = A - k * C[j]
4. if A > 0 then return FAILURE                                // greedy got stuck
5. return used

Algorithm DPChange(C, m, A)                       // exact minimum, Theta(A m)
1. best[0] = 0;  best[a] = infinity for a = 1..A
2. for a = 1 to A do
3.     for each coin c in C with c <= a do
4.         best[a] = min(best[a], best[a - c] + 1)
5. return best[A]

Algorithm SmallestCounterExample(C, m)            // C sorted increasing
1. for a = 1 to C[m-1] + C[m] do                              // bound of Kozen & Zaks (1994)
2.     if |GreedyChange(C, m, a)| > DPChange(C, m, a) then return a
3. return none                                                // the system is canonical
```
