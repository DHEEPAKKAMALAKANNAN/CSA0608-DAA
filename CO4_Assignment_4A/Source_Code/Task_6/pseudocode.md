# Task 6 – Pseudocode: Day-4 Design Challenge (large-capacity knapsack with item recovery, 32 MB budget)

Written before the implementation (`large_knapsack.py`). Changed requirement: n = 200 consignments,
W = 100,000 kg (1 kg resolution), the chosen consignments must be reported, the solver may use at most 32 MB.
The DP formulation is that of Task 2 (F[i][j] = best value of the first i items with capacity j); only the
**storage** of the table and the **recovery** of the items change.

## R1 – One value row + one decision bit per cell
Key idea: backtracking (Task 2) only asks "is F[i][j] ≠ F[i−1][j]?" — a yes/no question. Store that bit instead of
the whole value table; keep only one row of values.
```
Algorithm KnapsackBitPacked(w[1..n], v[1..n], W)
1. for j = 0 to W do best[j] = 0                           // one value row, Theta(W)
2. for i = 1 to n do
3.     keep[i] = all-zero bit string of length W + 1
4.     for j = W downto w[i] do                            // downward: best[j - w[i]] is still row i-1 (count)
5.         if v[i] + best[j - w[i]] > best[j] then
6.             best[j] = v[i] + best[j - w[i]]
7.             keep[i][j] = 1                              // "item i improves capacity j" = F[i][j] != F[i-1][j]
8. S = empty set;  j = W
9. for i = n downto 1 do                                   // the Task 2 backtracking, reading bits
10.    if keep[i][j] = 1 then S = S + {i};  j = j - w[i]
11. return best[W], S
```
Time Θ(nW); memory Θ(W) values + n(W + 1) bits = 0.8 MB + 2.5 MB (8-byte values) for n = 200, W = 100,000.

## R2 – Hirschberg-style divide and conquer (memory independent of n)
Key idea: an optimal load of items lo..hi−1 with capacity cap uses some capacity c* for the left half and at most
cap − c* for the right half, so c* maximises L[c] + R[cap − c] where L and R are the value rows of the two halves;
each row needs only Θ(cap) memory, and the item sets are found by recursing on (left half, c*) and
(right half, cap − c*).
```
Algorithm ValueRow(items lo..hi-1, cap)
1. for j = 0 to cap do best[j] = 0
2. for each item (w, v) in lo..hi-1 with w <= cap do
3.     for j = cap downto w do best[j] = max(best[j], v + best[j - w])     // count
4. return best                                             // best[c] = optimum with capacity c

Algorithm SolveDC(lo, hi, cap)
1. if lo >= hi or cap = 0 then return
2. if hi - lo = 1 then
3.     if w[lo] <= cap and v[lo] > 0 then add item lo to S
4.     return
5. mid = floor((lo + hi) / 2)
6. L = ValueRow(lo..mid-1, cap);  R = ValueRow(mid..hi-1, cap)
7. c* = argmax over c = 0..cap of L[c] + R[cap - c]        // best capacity split
8. free L and R                                            // only Theta(cap) memory at any time
9. SolveDC(lo, mid, c*);  SolveDC(mid, hi, cap - c*)

Algorithm KnapsackDivideConquer(w, v, W)
1. S = empty set;  SolveDC(0, n, W)
2. return sum of v over S, S
```
Cost: level ℓ of the recursion has subproblems with n/2^ℓ items whose capacities add up to ≤ W, so it evaluates
≤ nW/2^ℓ cells; summed over all levels ≤ 2nW cells → Θ(nW) time, Θ(W) memory, recursion depth ⌈log₂ n⌉ + 1.

## Planner (decision rule)
```
Algorithm PlanLoad(w, v, W, budget)
1. if predicted memory of R1 (one row + n(W+1) bits) <= budget then return KnapsackBitPacked(w, v, W)
2. else if predicted memory of R2 (two rows) <= budget then return KnapsackDivideConquer(w, v, W)
3. else refuse: "use a coarser weight unit" (e.g. 10 kg -> W / 10)
```
