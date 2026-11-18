# Q5 – Divide-and-Conquer Closest Pair: Pseudocode (prepared before implementation)

**Problem (airspace deconfliction).** Given the positions Dᵢ = (xᵢ, yᵢ) in metres of n airborne drones, find the two
drones with the smallest Euclidean distance. Brute force examines all n(n − 1)/2 pairs; the Divide-and-Conquer
design below avoids almost all of them.

## Divide-and-Conquer logic

| Step | What it does | Cost |
|---|---|---|
| **Preprocess** | Sort the drones once by x (merge sort). | Θ(n log n), once |
| **Divide** | Split the x-sorted list at its middle: left half (x ≤ mid_x), right half (x ≥ mid_x). The vertical line x = mid_x separates them. | Θ(1) (+ list slicing Θ(n)) |
| **Conquer** | Solve each half recursively; each call returns its best distance δ and its points **sorted by y**. Base case: 2 or 3 drones → brute force. | 2T(n/2) |
| **Combine** | (1) Merge the two y-sorted halves (Θ(n)). (2) δ = min(δ_L, δ_R). Only a pair with one drone on each side and both within δ of the line can beat δ → keep the **strip** \|x − mid_x\| < δ (already in y-order). (3) Compare every strip drone with the following strip drones while their y-difference is < δ — **at most 7** of them. | Θ(n) |

**Why at most 7 neighbours.** Take a strip drone p and the δ × 2δ rectangle above it (y from p.y to p.y + δ, x from
mid_x − δ to mid_x + δ). Its left δ × δ square contains only left-half drones, which are pairwise at least δ apart
(δ ≤ δ_L); a δ × δ square can hold at most 4 such points (one per corner region — split the square into four
δ/2 × δ/2 cells, each cell has diameter δ/√2 < δ, so it holds at most one point). The same holds for the right square.
So the rectangle holds at most 8 drones including p: p has at most **7** neighbours to examine.

## Pseudocode

```
Algorithm ClosestPairDC(D, n)                     // D[0..n-1] = (x, y) positions, n >= 2
1. Px = MergeSortBy(D, x)                         // presort by x once: Theta(n log n)
2. (best2, pair, Py) = Closest(Px)
3. return sqrt(best2), pair

Algorithm Closest(Px)                             // Px sorted by x; returns (best squared distance, pair, Py)
1.  m = |Px|
2.  if m <= 3 then                                // base case
3.      (best2, pair) = BruteForce(Px)            // <= 3 distance computations
4.      Py = Px sorted by y                       // <= 3 comparisons
5.      return (best2, pair, Py)
6.  mid = floor(m / 2);  mid_x = Px[mid].x        // DIVIDE: vertical line x = mid_x
7.  (bL, pL, Ly) = Closest(Px[0 .. mid-1])        // CONQUER left half
8.  (bR, pR, Ry) = Closest(Px[mid .. m-1])        // CONQUER right half
9.  (best2, pair) = smaller of (bL, pL), (bR, pR)
10. Py = Merge(Ly, Ry) by y                       // COMBINE 1: Theta(m)
11. delta = sqrt(best2)
12. S = [p in Py with |p.x - mid_x| < delta]      // COMBINE 2: the strip, still in y order
13. for i = 0 to |S| - 1 do                       // COMBINE 3: <= 7 neighbours per strip point
14.     j = i + 1
15.     while j < |S| and S[j].y - S[i].y < delta do
16.         d2 = (S[i].x - S[j].x)^2 + (S[i].y - S[j].y)^2      // one distance computation
17.         if d2 < best2 then best2 = d2; pair = (S[i], S[j]); delta = sqrt(best2)
18.         j = j + 1
19. return (best2, pair, Py)

Algorithm BruteForce(D, n)                        // reference: all n(n-1)/2 pairs
1. best2 = +infinity
2. for i = 0 to n-2 do
3.     for j = i+1 to n-1 do
4.         d2 = (D[i].x - D[j].x)^2 + (D[i].y - D[j].y)^2
5.         if d2 < best2 then best2 = d2; pair = (D[i], D[j])
6. return (best2, pair)
```

Squared distances are compared (same order as the true distance); the square root is taken only for δ and the answer.

## Recurrence

T(n) = 2T(n/2) + Θ(n) for n > 3, T(n) = Θ(1) for n ≤ 3 (plus the one-off Θ(n log n) presort).
Master Theorem: a = 2, b = 2, f(n) = Θ(n), n^(log_b a) = n¹ → f(n) = Θ(n^(log_b a)) → **case 2** → T(n) = Θ(n log n).
Recursion tree: level i has 2ⁱ sub-problems of size n/2ⁱ, each with Θ(n/2ⁱ) combine work → Θ(n) per level × log₂ n levels.
(If the strip were re-sorted by y in every call, f(n) = Θ(n log n) and T(n) = Θ(n log² n) — the merge avoids this.)

Decomposition diagram: `../Implementation_Code/results/q5_decomposition.png`.
