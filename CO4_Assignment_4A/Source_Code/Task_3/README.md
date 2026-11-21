# Task 3: From Recurrence to Executable Logic – Dynamic Programming: 0/1 Knapsack

## 1. Problem Overview
- **Scenario:** A cargo-planning system selects cargo items for a transport vehicle with limited carrying capacity $W = 7\text{ kg}$.
- **Item Attributes:** Indivisible packages (cannot be fractionated). Each item has an ID, integer weight $w_i > 0$, and value $v_i \ge 0$.
- **Problem Classification:** 0/1 Knapsack Problem (NP-Complete; solvable via Dynamic Programming in pseudo-polynomial time).
- **Core Principle:** Overlapping subproblems and optimal substructure; greedy heuristic fails due to item indivisibility.

---

## 2. Task 3.1: State Definition

### Formal Definition:
$$\text{DP}[i][w]$$
represents the **maximum cumulative value** achievable by selecting an optimal subset from the first $i$ candidate items ($\{Item_1, Item_2, \dots, Item_i\}$) such that their total combined weight does not exceed capacity limit $w$, where:
- $i \in \{0, 1, \dots, n\}$ denotes the item prefix index.
- $w \in \{0, 1, \dots, W\}$ denotes the allowable residual weight capacity.

### Semantic Meaning:
1. **Prefix Invariant:** Restricting selection to items $1..i$ ensures that items are considered sequentially and chosen at most once.
2. **Value Representation:** The table stores strictly optimal numerical values. The explicit subset of chosen items is recovered via retrospective backtracking.
3. **Global Optimum:** The solution to the overall problem corresponds to entry $\text{DP}[n][W]$.

---

## 3. Task 3.2: Recurrence Relation Formulation

### Recurrence Equations:
$$\text{DP}[i][w] = \begin{cases} 
\text{DP}[i-1][w] & \text{if } wt_i > w \quad (\text{Item } i \text{ exceeds current capacity}) \\
\max\Big(\text{DP}[i-1][w], \; val_i + \text{DP}[i-1][w - wt_i]\Big) & \text{if } wt_i \le w \quad (\text{Include vs. Exclude decision})
\end{cases}$$

### Boundary Conditions:
- $\text{DP}[0][w] = 0 \quad \forall \; 0 \le w \le W$ (Zero value available when zero items are considered).
- $\text{DP}[i][0] = 0 \quad \forall \; 0 \le i \le n$ (Zero value fit when carrying capacity is zero).

### Term Explanation & Optimal Substructure:
- **Exclude Choice ($\text{DP}[i-1][w]$):** If item $i$ is omitted, the maximum value with capacity $w$ is identical to the best subset obtainable from the remaining $i-1$ items.
- **Include Choice ($val_i + \text{DP}[i-1][w - wt_i]$):** If item $i$ is admitted, it consumes $wt_i$ capacity and yields $val_i$. By optimal substructure, the remaining items $1..i-1$ must constitute an optimal configuration for the remaining capacity $w - wt_i$.
- **Subproblem Overlap:** Many $(i, w)$ queries share identical $(i-1, w')$ subproblems. Memoizing in a 2D table prevents exponential re-computation.

---

## 4. Task 3.3: SIMATS Standard Pseudocode

```text
ALGORITHM Knapsack01(Item, n, W)
INPUT:
    Item – array Item[1..n] where each item i has:
        Item[i].id     – identifier
        Item[i].weight – positive integer weight (wt_i > 0)
        Item[i].value  – non-negative value (val_i >= 0)
    n    – number of available items (n >= 0)
    W    – vehicle capacity limit (integer W >= 0)
OUTPUT:
    BestValue – maximum attainable profit (= DP[n][W])
    Selected  – list of IDs of items achieving BestValue
BEGIN
    // Step 1: Initialize DP structure
    FOR w ← 0 TO W DO
        DP[0][w] ← 0
    END FOR
    FOR i ← 0 TO n DO
        DP[i][0] ← 0
    END FOR
    
    // Step 2: Compute DP states in dependency order
    FOR i ← 1 TO n DO
        FOR w ← 1 TO W DO
            Exclude ← DP[i - 1][w]
            IF Item[i].weight <= w THEN
                Include ← Item[i].value + DP[i - 1][w - Item[i].weight]
                IF Include > Exclude THEN
                    DP[i][w] ← Include
                ELSE
                    DP[i][w] ← Exclude
                END IF
            ELSE
                DP[i][w] ← Exclude
            END IF
        END FOR
    END FOR
    
    BestValue ← DP[n][W]
    
    // Step 3: Backtrack to reconstruct selected items
    Selected ← empty list
    w ← W
    FOR i ← n DOWNTO 1 DO
        IF DP[i][w] ≠ DP[i - 1][w] THEN
            INSERT Item[i].id at front of Selected
            w ← w - Item[i].weight
        END IF
    END FOR
    
    RETURN BestValue, Selected
END
```

### Complexity Analysis:
- **Time Complexity:** The nested loops execute $(n) \times (W)$ iterations, each taking $O(1)$ arithmetic operations. Reconstruction executes $n$ steps. Total Time: $\Theta(n \cdot W)$ (pseudo-polynomial).
- **Space Complexity:** $\Theta(n \cdot W)$ to maintain the full 2D table for reconstruction.

---

## 5. Task 3.4: Manual Desk-Check Trace

### Given Problem Instance ($W = 7$):
| Item ID | Weight ($wt$) | Value ($val$) | Ratio ($val/wt$) |
|:---:|:---:|:---:|:---:|
| **P** | 2 | 12 | 6.0 |
| **Q** | 3 | 20 | 6.67 |
| **R** | 4 | 25 | 6.25 |
| **S** | 5 | 30 | 6.0 |

### Complete DP Table $\text{DP}[i][w]$:
| $i$ (Item, $wt, val$) | $w=0$ | $w=1$ | $w=2$ | $w=3$ | $w=4$ | $w=5$ | $w=6$ | $w=7$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0 (None)** | **0** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **1 (P, 2, 12)** | **0** | 0 | 12 | 12 | 12 | 12 | 12 | 12 |
| **2 (Q, 3, 20)** | 0 | 0 | 12 | **20** | 20 | 32 | 32 | 32 |
| **3 (R, 4, 25)** | 0 | 0 | 12 | 20 | 25 | 32 | 37 | **45** |
| **4 (S, 5, 30)** | 0 | 0 | 12 | 20 | 25 | 32 | 37 | **45** |

*(Bold entries mark states on the optimal solution reconstruction trajectory).*

### Key Include/Exclude State Calculations:
- $\text{DP}[1][2]: \max(0, 12 + \text{DP}[0][0]) = 12$ (Include P)
- $\text{DP}[2][3]: \max(12, 20 + \text{DP}[1][0]) = 20$ (Include Q)
- $\text{DP}[2][5]: \max(12, 20 + \text{DP}[1][3]) = \max(12, 20 + 12) = 32$ (Include Q with P)
- $\text{DP}[3][7]: \max(\text{DP}[2][7], 25 + \text{DP}[2][7-4]) = \max(32, 25 + 20) = \mathbf{45}$ (Include R with Q)
- $\text{DP}[4][7]: \max(\text{DP}[3][7], 30 + \text{DP}[3][7-5]) = \max(45, 30 + \text{DP}[3][2]) = \max(45, 30 + 12) = 45$ (Exclude S, as $42 < 45$)

### Reconstruction Walk:
| Step $i$ | Residual $w$ | $\text{DP}[i][w]$ | $\text{DP}[i-1][w]$ | Comparison | Decision | Updated $w$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **4 (S)** | 7 | 45 | 45 | Equal | Exclude S | 7 |
| **3 (R)** | 7 | 45 | 32 | Differ | **Include R** | $7 - 4 = 3$ |
| **2 (Q)** | 3 | 20 | 12 | Differ | **Include Q** | $3 - 3 = 0$ |
| **1 (P)** | 0 | 0 | 0 | Equal | Exclude P | 0 |

**Final Solution:** Selected Items = **{Q, R}**, Total Weight = $3 + 4 = 7 \le 7$, **Optimal Value = 45**.

---

## 6. Task 3.5: State Dependency Analysis

### Architectural Dependency:
- Every cell $\text{DP}[i][w]$ depends **strictly on two cells from row $i-1$**:
  1. The directly vertical cell: $\text{DP}[i-1][w]$ (Exclude path).
  2. The left-offset cell: $\text{DP}[i-1][w - wt_i]$ (Include path).
- Under no circumstance does a state depend on cells in its own row $i$ or any subsequent row $k > i$.

### Processing Order Justification:
- Outer loop index $i$ must iterate strictly sequentially ($i = 1 \to n$). This guarantees row $i-1$ is finalized and immutable before computing row $i$.
- Inner loop index $w$ can proceed in either direction when maintaining a full 2D array.
- **Space Optimization Note:** If using a 1D state array $\text{DP}[w]$, the inner loop **must decrement** ($w = W \text{ downto } wt_i$) to prevent an item from being included multiple times in the same iteration (which would erroneously model the Unbounded Knapsack problem).

---

## 7. Implementation & Verification Details

### File Manifest:
- `knapsack_dp.py`: Python 3.13 implementation containing table generator, reconstruction logic, and $2^n$ brute-force verification.
- `items.csv`: Official input dataset.
- `test_knapsack_dp.py`: Automated test suite comparing DP against exhaustive power set enumeration across 400 randomized instances.

### How to Run:
```bash
python knapsack_dp.py
python test_knapsack_dp.py
```

### Verification Result:
```text
=== TASK 3: TEST SUITE ===
PASS test_official_knapsack_value: optimal value 45
PASS test_reconstruction_integrity: items {Q, R} match weight 7
PASS test_zero_capacity: W=0 returns 0
PASS test_items_heavier_than_capacity: returns 0
PASS test_all_items_fit: sums all values
PASS test_exhaustive_brute_force (400 randomized instances)
PASS test_deterministic_output
PASS test_optimal_substructure_invariant
RESULT: 8/8 tests passed
```
