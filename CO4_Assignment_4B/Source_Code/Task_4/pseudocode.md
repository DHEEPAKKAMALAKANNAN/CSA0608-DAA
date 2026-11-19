# Task 4 – Assembly Line Scheduling DP: pseudocode

```
Algorithm AssemblyLine(a1, a2, t1, t2, e1, e2, x1, x2, n)
// f_i[j] = fastest time to leave station j on line i;  pred_i[j] = line used at station j-1
1.  f1[1] = e1 + a1[1];  f2[1] = e2 + a2[1]
2.  for j = 2 to n do
3.      stay1 = f1[j-1] + a1[j];   trans1 = f2[j-1] + t2[j-1] + a1[j]
4.      if stay1 <= trans1 then f1[j] = stay1; pred1[j] = 1 else f1[j] = trans1; pred1[j] = 2
5.      stay2 = f2[j-1] + a2[j];   trans2 = f1[j-1] + t1[j-1] + a2[j]
6.      if stay2 <= trans2 then f2[j] = stay2; pred2[j] = 2 else f2[j] = trans2; pred2[j] = 1
7.      record (j, stay1, trans1, choice1, stay2, trans2, choice2)      // decision table
8.  if f1[n] + x1 <= f2[n] + x2 then f* = f1[n] + x1; line = 1 else f* = f2[n] + x2; line = 2
9.  for j = n downto 1 do                                            // route reconstruction
10.     route[j] = line
11.     if j > 1 then line = pred_line[j]
12. transfers = { j : route[j] ≠ route[j+1] }
13. return f*, route, transfers
```

Work: 2 comparisons per station + 1 at the exit → Θ(n); memory Θ(n) for pred (f needs only two variables).
