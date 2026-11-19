# Q7 – Pseudocode: most profitable contiguous run of delivery hours (Maximum Subarray Sum)

The paper leaves the Day-4 problem open, so the pair chose this problem because it is new relative to Q1–Q6.

## Baseline – brute force, Θ(n²)  (flowchart: `q7_flowchart_brute_force.png`)

```
Algorithm BruteForceRun(p, n)
1. best = p[0];  (bi, bj) = (0, 0)
2. for i = 0 to n-1 do
3.     run = 0
4.     for j = i to n-1 do
5.         run = run + p[j]                  // 1 addition
6.         if run > best then                // 1 comparison
7.             best = run;  (bi, bj) = (i, j)
8. return (best, bi, bj)                     // n(n+1)/2 additions and comparisons
```

## Comparison variant – repaired Student A proposal with a crossing scan, Θ(n log n)

```
Algorithm CrossingRun(p, lo, hi)
1. if lo = hi then return (p[lo], lo, lo)
2. mid = floor((lo + hi) / 2)
3. L = CrossingRun(p, lo, mid);  R = CrossingRun(p, mid + 1, hi)
4. scan k = mid downto lo keeping the best suffix sum ending at mid  -> (ls, i)
5. scan k = mid+1 to hi keeping the best prefix sum starting at mid+1 -> (rs, j)
6. return the largest of L, R, (ls + rs, i, j)          // T(n) = 2T(n/2) + Theta(n)
```

## Joint final design – 4-tuple summary with indices, Θ(n)  (flowchart: `q7_flowchart_joint_dc.png`)

```
Algorithm MaxRun(p, lo, hi)                    // returns Summary of p[lo..hi]
1. if lo = hi then
2.     return (total=p[lo], pre=p[lo], pre_end=lo, suf=p[lo], suf_start=lo, best=p[lo], bi=lo, bj=lo)
3. mid = floor((lo + hi) / 2)                  // DIVIDE
4. L = MaxRun(p, lo, mid)                      // CONQUER
5. R = MaxRun(p, mid + 1, hi)
6. total = L.total + R.total                   // COMBINE (4 additions, 4 comparisons)
7. if L.total + R.pre > L.pre then (pre, pre_end) = (L.total + R.pre, R.pre_end)
8.                             else (pre, pre_end) = (L.pre, L.pre_end)
9. if R.total + L.suf > R.suf then (suf, suf_start) = (R.total + L.suf, L.suf_start)
10.                            else (suf, suf_start) = (R.suf, R.suf_start)
11. cross = L.suf + R.pre
12. (best, bi, bj) = (L.best >= R.best) ? (L.best, L.bi, L.bj) : (R.best, R.bi, R.bj)
13. if cross > best then (best, bi, bj) = (cross, L.suf_start, R.pre_end)
14. return (total, pre, pre_end, suf, suf_start, best, bi, bj)

Algorithm MostProfitableRun(p, n)
1. if n = 0 then error "no hours"
2. S = MaxRun(p, 0, n - 1)
3. return (S.best, S.bi, S.bj)
```

Recurrence: T(1) = d, T(n) = 2T(n/2) + c → T(n) = dn + c(n − 1) = Θ(n) (Master Theorem case 1, a = b = 2,
f(n) = Θ(1)). Exactly 4(n − 1) additions, 4(n − 1) comparisons, 2n − 1 calls, depth ⌈log₂ n⌉.

Student proposals (Stage 1): `../Student_A_Initial_Design/README.md` and `../Student_B_Initial_Design/README.md`.
