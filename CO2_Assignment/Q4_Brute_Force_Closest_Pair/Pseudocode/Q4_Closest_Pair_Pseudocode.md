# Q4 – Brute-Force Closest Pair for Drone Collision-Risk Monitoring: Pseudocode and Pre-Implementation Notes

*Written before implementation.*

## 1. Which candidate pairs must be examined?

The closest two drones could be **any** two drones, and a brute-force method uses no geometric knowledge to rule a
pair out, so *every unordered pair {Dᵢ, Dⱼ} with i ≠ j* is a candidate. The distance is symmetric
(d(Dᵢ,Dⱼ) = d(Dⱼ,Dᵢ)) and d(Dᵢ,Dᵢ) = 0 is meaningless, so:

* **avoid duplicates** by examining only ordered index pairs with **i < j** (the inner loop starts at j = i+1);
* never pair a drone with itself.

## 2. How many unique pairs exist? (derivation)

Drone Dᵢ (i = 1..n−1) is paired with Dᵢ₊₁ … Dₙ, i.e. with n−i drones:

  P(n) = Σ<sub>i=1</sub><sup>n−1</sup> (n − i) = (n−1) + (n−2) + … + 1 = **n(n−1)/2 = C(n,2)**.

Check by counting ordered pairs: n choices for the first drone × (n−1) for the second = n(n−1) ordered pairs, each
unordered pair counted twice ⇒ n(n−1)/2. Hence P(n) ∈ Θ(n²): doubling n multiplies the work by
P(2n)/P(n) = 2(2n−1)/(n−1) → 4.

| n | 100 | 1 000 | 5 000 | 10 000 |
|---|---|---|---|---|
| n(n−1)/2 | 4 950 | 499 500 | 12 497 500 | 49 995 000 |

## 3. Pseudocode

```
BRUTE-FORCE-CLOSEST-PAIR(D[0..n−1])            // D[k] = (x_k, y_k) in metres, n ≥ 2
    best² ← +∞ ; bestPair ← none
    pairsExamined ← 0 ; distanceCalcs ← 0
    for i ← 0 to n−2 do
        for j ← i+1 to n−1 do                   // j > i: each unordered pair exactly once
            pairsExamined ← pairsExamined + 1
            dx ← x_i − x_j ; dy ← y_i − y_j
            d² ← dx·dx + dy·dy                   // squared distance: no square root inside the loop
            distanceCalcs ← distanceCalcs + 1
            if d² < best² then best² ← d² ; bestPair ← (i, j)
    return bestPair, √best², pairsExamined, distanceCalcs
```

Design notes: comparing squared distances preserves the order of distances (√ is monotone), so the single √ is
taken only once at the end. Duplicate positions give d = 0, which is reported immediately as the closest pair
(a real collision alert).

## 4. Predictions (before running)

* `pairsExamined = distanceCalcs = n(n−1)/2` **exactly**, for every input distribution (uniform or clustered)
  – the brute-force work does not depend on where the drones are.
* Time T(n) ≈ c · n(n−1)/2 with a constant c (cost of one distance evaluation in Python, expected ≈ 0.1–0.5 µs).
  Each doubling of n should multiply both the count and the time by ≈ 4.
* Experimental sizes: n = 100, 500, 1 000, 2 000, 5 000, 10 000 (uniform drones in a 10 km × 10 km area) plus a
  clustered (swarm) layout with n = 2 000 to confirm that the count is distribution-independent.

## 5. Acceptability criterion (defined before measuring)

Drone telemetry arrives about once per second (1 Hz). The collision check must leave the remainder of the cycle for
alerting, logging and networking, so I define **acceptable response = ≤ 100 ms per monitoring cycle** (10 % of the
cycle); 1 s is the hard limit (the check would no longer finish before the next update).
With T(n) ≈ c · n²/2, the largest acceptable fleet is n<sub>max</sub> ≈ √(2 · 0.1 s / c).
