# Task 1 – Pseudocode: Binomial Coefficient C(n, k) (and Fibonacci warm-up)

Written before the implementation (`binomial_dp.py`). Counters used as evidence are marked `// count`.

## DP formulation
- **State:** C[i][j] = number of j-element subsets of an i-element set = C(i, j), 0 ≤ j ≤ min(i, k), 0 ≤ i ≤ n.
- **Recurrence:** C[i][j] = C[i−1][j−1] + C[i−1][j] for 0 < j < i (subsets that contain item i + those that do not).
- **Base cases:** C[i][0] = 1 and C[i][i] = 1.
- **Order of computation:** row by row (i = 0 … n), left to right inside a row (j = 0 … min(i, k)); every cell
  needs only cells of the previous row, which are already final.
- **Answer:** C[n][k].

## 1. Naive recursion (exposes the overlapping sub-problems)
```
Algorithm BinomNaive(n, k)
// Input: integers 0 <= k <= n      Output: C(n, k)
1. calls = calls + 1                                   // count
2. if k = 0 or k = n then return 1
3. additions = additions + 1                           // count
4. return BinomNaive(n-1, k-1) + BinomNaive(n-1, k)
```

## 2. Memoised recursion (top-down DP / memory function)
```
Algorithm BinomMemo(i, j)
// memo[] is an initially empty dictionary shared by all calls
1. calls = calls + 1                                   // count
2. if j = 0 or j = i then return 1
3. if (i, j) is in memo then return memo[(i, j)]       // overlapping sub-problem re-used
4. additions = additions + 1                           // count
5. memo[(i, j)] = BinomMemo(i-1, j-1) + BinomMemo(i-1, j)
6. return memo[(i, j)]
```

## 3. Bottom-up Pascal table (Levitin, Binomial(n, k))
```
Algorithm Binomial(n, k)
// Input: integers n >= k >= 0      Output: C(n, k)
1. for i = 0 to n do
2.     for j = 0 to min(i, k) do
3.         if j = 0 or j = i then C[i][j] = 1
4.         else
5.             C[i][j] = C[i-1][j-1] + C[i-1][j]
6.             additions = additions + 1               // count
7. return C[n][k]
```
Additions A(n, k) = Σ<sub>i=1..k</sub> (i − 1) + Σ<sub>i=k+1..n</sub> k = (k − 1)k/2 + k(n − k) ∈ Θ(nk).

## 4. Space-optimised single row (Θ(k) memory)
```
Algorithm BinomialOneRow(n, k)
1. row[0] = 1;  row[1..k] = 0                          // row 0 of Pascal's triangle
2. for i = 1 to n do
3.     for j = min(i, k) downto 1 do                    // downward: row[j-1] still holds C(i-1, j-1)
4.         if j = i then row[j] = 1
5.         else row[j] = row[j] + row[j-1]              // C(i,j) = C(i-1,j) + C(i-1,j-1); count
6. return row[k]
```

## 5. Fibonacci warm-up
```
Algorithm FibBottomUp(n)
1. if n < 2 then return n
2. prev = 0;  cur = 1
3. for i = 2 to n do
4.     (prev, cur) = (cur, prev + cur)                  // one addition per i
5. return cur
```
Naive recursion F(n) = F(n−1) + F(n−2) makes 2F(n+1) − 1 calls; the bottom-up loop makes n − 1 additions.
