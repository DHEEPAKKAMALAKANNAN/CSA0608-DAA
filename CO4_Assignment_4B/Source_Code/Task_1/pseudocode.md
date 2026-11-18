# Task 1 – Pseudocode: Activity Selection (EOC briefing-room bookings)

Written before the implementation (`activity_selection.py`). Requests are half-open intervals
[s<sub>i</sub>, f<sub>i</sub>): a session that ends at 10:00 is compatible with one that starts at 10:00.

## Greedy algorithm – earliest finish time (EFT)

```
Algorithm SelectEFT(R, n)                         // R[1..n] = requests (id, s, f)
1. for each request r in R do
2.     if r.f <= r.s then error "finish must be after start"
3. sort R by finish time (ties: earlier start first)          // Theta(n log n) comparisons
4. A = empty list;  last = -infinity
5. for i = 1 to n do                                          // one scan, n compatibility checks
6.     if R[i].s >= last then                                 // greedy choice: first compatible finisher
7.         append R[i] to A;  last = R[i].f
8. return A
```

## Un-optimised version used for comparison (naive re-scan)

```
Algorithm SelectNaive(R, n)
1. A = empty list;  last = -infinity;  P = R
2. repeat
3.     best = none
4.     for each r in P do                                     // full scan every round
5.         if r.s >= last and (best = none or r.f < best.f) then best = r
6.     if best = none then return A
7.     append best to A;  last = best.f
8.     P = { r in P : r.s >= last }                            // drop requests that can never fit
```
Cost: one scan of the remaining requests per accepted request, Theta(n·k) comparisons (k = |A|), i.e.
Theta(n²) when k grows with n.

## Rules that look reasonable but are not optimal (tested as counter-examples)

```
Algorithm SelectByKey(R, n, key)                  // key = start, duration, or "fewest conflicts"
1. sort R by key
2. A = empty list
3. for i = 1 to n do
4.     if R[i] overlaps no request in A then append R[i] to A
5. return A
```

## Exact references used only for verification

```
Algorithm OptimumDP(R, n)                         // weighted interval scheduling with weight 1
1. sort R by finish time;  OPT[0] = 0
2. for j = 1 to n do
3.     p = number of requests i < j with R[i].f <= R[j].s     // binary search
4.     OPT[j] = max(OPT[j-1], 1 + OPT[p])
5. return OPT[n]

Algorithm OptimumBruteForce(R, n)                 // n <= 20
1. best = 0
2. for every subset S of R do                                // 2^n subsets
3.     if no two requests of S overlap then best = max(best, |S|)
4. return best
```
