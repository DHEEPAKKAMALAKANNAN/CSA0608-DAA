# Task 2 – Pseudocode: 0/1 Knapsack by Dynamic Programming (drone cargo loading)

Written before the implementation (`knapsack_dp.py`). w[1..n] = parcel weights (kg), v[1..n] = values, W = payload.

## DP formulation
- **State:** F[i][j] = maximum value obtainable from the first i parcels with a payload limit of j kg.
- **Recurrence:** F[i][j] = F[i−1][j] if j < w[i]; otherwise F[i][j] = max(F[i−1][j], v[i] + F[i−1][j − w[i]])
  (either parcel i is left behind, or it is loaded and the remaining j − w[i] kg are used optimally).
- **Base cases:** F[0][j] = 0 for all j ≥ 0 (no parcels) and F[i][0] = 0 for all i ≥ 0 (no payload).
- **Order of computation:** rows i = 1 … n, inside a row j = 1 … W; each cell needs only row i − 1.
- **Answer:** F[n][W]; the parcels are recovered by walking back from F[n][W].

## 1. Bottom-up table
```
Algorithm KnapsackBottomUp(w[1..n], v[1..n], W)
1. for j = 0 to W do F[0][j] = 0
2. for i = 0 to n do F[i][0] = 0
3. for i = 1 to n do
4.     for j = 1 to W do                                    // one cell = one basic step (count)
5.         if j < w[i] then F[i][j] = F[i-1][j]
6.         else F[i][j] = max(F[i-1][j], v[i] + F[i-1][j - w[i]])
7. return F[n][W]
```

## 2. Backtracking (recover the chosen parcels)
```
Algorithm Backtrack(F, w[1..n], W)
1. j = W;  S = empty set
2. for i = n downto 1 do
3.     if F[i][j] != F[i-1][j] then                        // the optimum for (i, j) uses parcel i
4.         S = S + {i};  j = j - w[i]
5. return S
```

## 3. Memory function (top-down, Levitin's MFKnapsack)
```
Algorithm MFKnapsack(i, j)
// F[0][*] = F[*][0] = 0, every other cell initialised to -1 ("not computed")
1. if F[i][j] < 0 then
2.     if j < w[i] then value = MFKnapsack(i-1, j)
3.     else value = max(MFKnapsack(i-1, j), v[i] + MFKnapsack(i-1, j - w[i]))
4.     F[i][j] = value                                      // count computed cells
5. return F[i][j]
```

## 4. Θ(W)-space single row (value only)
```
Algorithm KnapsackOneRow(w[1..n], v[1..n], W)
1. for j = 0 to W do best[j] = 0
2. for i = 1 to n do
3.     for j = W downto w[i] do                             // downward: best[j - w[i]] is still row i-1
4.         best[j] = max(best[j], v[i] + best[j - w[i]])
5. return best[W]
```

## 5. Brute force (verification reference)
```
Algorithm KnapsackBrute(i, weight, value)
1. if i = n then
2.     if weight <= W and value > best then best = value   // one subset examined (count)
3.     return
4. KnapsackBrute(i+1, weight, value)                       // parcel i+1 left behind
5. KnapsackBrute(i+1, weight + w[i+1], value + v[i+1])     // parcel i+1 loaded
```
Costs: bottom-up Θ(nW) time and space; backtracking Θ(n); single row Θ(nW) time, Θ(W) space;
brute force Θ(2ⁿ).
