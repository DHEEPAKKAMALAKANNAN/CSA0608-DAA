# Task 5 – Pseudocode: Optimal Binary Search Tree (chatbot intent-keyword lookup)

Written before the implementation (`optimal_bst.py`). Keys a₁ < a₂ < … < aₙ with access probabilities
P[1..n] (stored as integer counts per 100 lookups so that all arithmetic is exact).

## DP formulation
- **State:** C[i][j] = smallest average number of comparisons for a BST containing keys aᵢ … aⱼ;
  R[i][j] = root of that optimal subtree.
- **Recurrence:** C[i][j] = min<sub>i ≤ k ≤ j</sub> { C[i][k−1] + C[k+1][j] } + Σ<sub>s=i..j</sub> P[s]
  (choosing aₖ as root puts every key of the range one level deeper, which adds the whole probability mass once).
- **Base cases:** C[i][i−1] = 0 (empty tree), C[i][i] = P[i], R[i][i] = i.
- **Order of computation:** by diagonals d = j − i = 1, 2, …, n − 1 (every C needed on the right-hand side
  belongs to a shorter range, i.e. an earlier diagonal).
- **Answer:** C[1][n]; the tree is rebuilt from R starting with R[1][n].

## 1. Optimal BST (Levitin)
```
Algorithm OptimalBST(P[1..n])
// Output: average cost C[1][n] and root table R
1. for i = 1 to n do
2.     C[i][i-1] = 0;  C[i][i] = P[i];  R[i][i] = i
3. C[n+1][n] = 0
4. for d = 1 to n-1 do                                     // diagonal count
5.     for i = 1 to n-d do
6.         j = i + d;  minval = inf
7.         for k = i to j do                               // root candidate (count)
8.             if C[i][k-1] + C[k+1][j] < minval then
9.                 minval = C[i][k-1] + C[k+1][j];  kmin = k
10.        R[i][j] = kmin
11.        C[i][j] = minval + (prefix[j] - prefix[i-1])    // sum P[i..j] in O(1) with prefix sums
12. return C[1][n], R
```
Candidates examined = Σ<sub>d=1..n−1</sub> (n − d)(d + 1) = n(n − 1)(n + 4)/6 ∈ Θ(n³); space Θ(n²).

## 2. Building the tree from R
```
Algorithm BuildTree(R, i, j)
1. if i > j then return NIL
2. k = R[i][j]
3. return node(key a_k, left = BuildTree(R, i, k-1), right = BuildTree(R, k+1, j))
```

## 3. Knuth's improvement (Θ(n²))
```
Algorithm OptimalBSTKnuth(P[1..n])
// identical to OptimalBST except line 7:
7'.        for k = R[i][j-1] to R[i+1][j] do               // optimal roots are monotone
```
For a fixed diagonal the ranges telescope: Σᵢ (R[i+1][j] − R[i][j−1] + 1) ≤ n + (n − d), so each diagonal costs
O(n) and the whole table Θ(n²).

## 4. Comparison trees and exhaustive check
```
Algorithm BalancedBST(i, j)            // median key as root, ignores probabilities
1. if i > j then return NIL
2. k = floor((i + j) / 2);  return node(a_k, BalancedBST(i, k-1), BalancedBST(k+1, j))

Algorithm TreeCost(T)                   // average comparisons of any BST T
1. return sum over keys a_k of P[k] * depth(a_k)          // root has depth 1

Algorithm AllBSTs(i, j)                 // verification: every one of the Catalan(n) shapes
1. if i > j then yield NIL
2. for k = i to j do
3.     for each L in AllBSTs(i, k-1) do for each Rt in AllBSTs(k+1, j) do yield node(a_k, L, Rt)
```
