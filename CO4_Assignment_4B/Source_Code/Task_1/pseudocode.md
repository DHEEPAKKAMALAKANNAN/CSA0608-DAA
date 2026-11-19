# Task 1 – Word Wrap DP: pseudocode

```
Algorithm WordWrap(w[0..n-1], W)
// best[i] = minimum penalty for laying out the suffix w[i..n-1]; next[i] = first word of the next line
1.  if W < 1 or some len(w[k]) > W then reject the input (no valid layout)
2.  best[n] = 0
3.  for i = n-1 downto 0 do
4.      best[i] = ∞;  used = -1
5.      for j = i+1 to n do                       // first line holds w[i..j-1]
6.          used = used + len(w[j-1]) + 1
7.          s = W - used                          // unused spaces on that line
8.          if s < 0 then break                   // longer lines cannot fit either
9.          cost = (0 if j = n else s²) + best[j]  // final line carries no penalty
10.         if cost < best[i] then best[i] = cost;  next[i] = j
11. i = 0                                         // reconstruct the layout
12. while i < n do
13.     output line w[i..next[i]-1], its s and penalty;  i = next[i]
14. return best[0]
```

Work: Θ(n·L) candidate lines (L = maximum words per line ≤ n); memory: Θ(n).
