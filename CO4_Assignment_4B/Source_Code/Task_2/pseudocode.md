# Task 2 – Greedy (fractional) vs DP (0/1) knapsack: pseudocode

```
Algorithm FractionalKnapsack(items, W)            // Solution A - greedy
1.  sort items by v/w in decreasing order          // merge sort, ~ n log₂ n comparisons
2.  room = W;  total = 0
3.  for each item k in that order while room > 0 do
4.      if w_k <= room then take k whole:  room = room - w_k;  total = total + v_k
5.      else take fraction f = room / w_k:  total = total + f·v_k;  room = 0
6.      record (k, decision, fraction, room, total)
7.  return total and the items / fractions taken
```

```
Algorithm Knapsack01DP(items, W)                   // Solution B - dynamic programming
1.  for c = 0 to W do best[0][c] = 0
2.  for i = 1 to n do
3.      for c = 0 to W do
4.          best[i][c] = best[i-1][c]                          // leave item i
5.          if w_i <= c and best[i-1][c-w_i] + v_i > best[i][c] then
6.              best[i][c] = best[i-1][c-w_i] + v_i            // take item i
7.  c = W;  chosen = {}                                        // trace back
8.  for i = n downto 1 do
9.      if best[i][c] ≠ best[i-1][c] then chosen = chosen ∪ {i};  c = c - w_i
10. return best[n][W], chosen
```

```
Algorithm FirstBlockingCommitment(items, W)        // diagnosis used in 2.2
1.  OPT = Knapsack01DP(items, W);  order = items sorted by v/w;  room = W;  committed = 0
2.  for step = 1 to n do
3.      k = order[step]
4.      if w_k <= room then commit k: room = room - w_k; committed = committed + v_k
5.      reachable = committed + Knapsack01DP(order[step+1..n], room)
6.      if k was committed and reachable < OPT then return step   // optimum no longer reachable
7.  return none                                     // greedy was optimal
```
