# Q6 – Exhaustive Search for Humanitarian Airlift Planning: Design and Pre-Implementation Notes

*Designed from the problem statement (not from supplied pseudocode) before implementation.*

## 1. Design decisions

| Question | Decision |
|---|---|
| **How is a candidate combination represented?** | an n-bit binary vector, stored as an integer `mask` ∈ [0, 2ⁿ−1]; bit i = 1 ⇔ package i is loaded. Example (n = 5): `mask = 0b00101` = packages P1 and P3. |
| **How are candidates generated?** | count `mask = 0, 1, 2, …, 2ⁿ−1`. Binary counting visits every subset exactly once (bijection between integers 0..2ⁿ−1 and subsets), with no duplicates and none missed. |
| **How is feasibility checked?** | total weight W(mask) = Σ<sub>i: bit i = 1</sub> wᵢ; feasible ⇔ W(mask) ≤ payload limit C. |
| **How are feasible candidates evaluated?** | total humanitarian value V(mask) = Σ<sub>i: bit i = 1</sub> vᵢ. |
| **How is the best retained?** | keep `(bestValue, bestWeight, bestMask)`; replace it when V is larger, or V is equal and W is smaller (tie-break: lighter load = more safety margin); the first such mask in counting order is kept. |

## 2. Pseudocode

```
EXHAUSTIVE-AIRLIFT(w[0..n−1], v[0..n−1], C)
    bestValue ← −1 ; bestWeight ← 0 ; bestMask ← 0
    generated ← 0 ; feasible ← 0 ; bitChecks ← 0
    for mask ← 0 to 2ⁿ − 1 do                  // every candidate loading plan
        generated ← generated + 1
        W ← 0 ; V ← 0
        for i ← 0 to n−1 do                      // decode the bit vector
            bitChecks ← bitChecks + 1
            if bit i of mask = 1 then W ← W + w[i] ; V ← V + v[i]
        if W ≤ C then                            // feasibility test
            feasible ← feasible + 1
            if V > bestValue or (V = bestValue and W < bestWeight) then
                bestValue ← V ; bestWeight ← W ; bestMask ← mask
    return bestMask, bestValue, bestWeight, generated, feasible, bitChecks
```

## 3. Correctness check plan

* Small instance, n = 5 packages, payload 15 kg: print the **full enumeration table** (all 32 rows: mask,
  packages, weight, value, feasible?, best-so-far) so every row can be verified by hand.
* The instance is designed so that the "highest value-per-kg first" greedy rule gives 101 but the true optimum is
  102 – exhaustive search must find 102.
* Independent cross-check for larger n: 0/1-knapsack dynamic programming (a different method) must give the same
  optimum value on random instances.

## 4. Growth prediction (before experimenting)

* Each package is either loaded or not ⇒ number of candidates = 2 × 2 × … × 2 = **2ⁿ** (product rule).
* Adding **one** package doubles the candidates: |S(n+1)| = 2·|S(n)|; adding k packages multiplies by 2ᵏ
  (10 packages more ⇒ 1 024× more work).
* Work per candidate = n bit checks ⇒ total basic operations = n·2ⁿ, so T(n) ≈ c·n·2ⁿ ∈ Θ(n·2ⁿ).
* Predicted ratio T(n+2)/T(n) = 4·(n+2)/n (≈ 4.4 at n = 20).
* Experimental sizes: n = 10, 12, 14, 16, 18, 20, 22 (pure Python; larger n would take minutes).

## 5. Deployment boundary (method)

Fixed response time chosen: **1 second** (an interactive loading planner must let the coordinator re-plan
instantly when packages or priorities change). Fit c from the measured runs, then find the largest n with
c·n·2ⁿ ≤ 1 s; also report the sensitivity for 10 s and 60 s.
