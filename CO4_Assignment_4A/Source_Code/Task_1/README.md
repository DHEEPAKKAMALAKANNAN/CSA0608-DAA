# Task 1: Algorithm Design Review – Diagnose and Repair Poor Pseudocode

## 1. Problem Overview
- **Scenario:** A logistics company needs to load packages into a delivery vehicle to maximize the total value loaded without exceeding the vehicle's capacity.
- **Divisibility:** Packages may be divided if necessary (Fractional Knapsack problem).
- **Core Strategy:** Greedy approach sorting by value-to-weight ratio ($\frac{v_i}{w_i}$).
- **Target Outcome:** Identify and diagnose deficiencies in an engineer's flawed pseudocode, produce language-independent repaired pseudocode conforming to the *SIMATS Engineering Handbook for Algorithmic Pseudocode*, perform a rigorous manual desk-check trace, and defend the pseudocode design.

---

## 2. Task 1.1: Diagnosis of the Flawed Pseudocode

### Flawed Logic Proposed by Junior Engineer:
```text
ALGORITHM LoadVehicle
BEGIN
    Read packages
    Arrange packages
    Select the best package
    WHILE vehicle has space DO
        Add suitable package
    END WHILE
    Calculate value
    RETURN result
END
```

### Algorithmic Deficiencies & Implementation Impact:
1. **Missing Inputs and Outputs (Contract Incomplete):**
   - *Deficiency:* `ALGORITHM LoadVehicle` provides no parameter list, no input type/bounds specifications, and no definition of output variables.
   - *Impact:* An implementer cannot ascertain whether package weights and values are integers or floats, or whether the vehicle capacity $C$ is an argument or global constant.
2. **Ambiguous Selection Criterion ("Arrange packages"):**
   - *Deficiency:* "Arrange" gives neither the ordering key (value, weight, or density ratio) nor the sorting direction (ascending vs. descending).
   - *Impact:* Sorting purely by value ($220$), or lightest-first ($225$), produces sub-optimal solutions compared to value-per-unit-weight ratio ($240$).
3. **Undefined Meaning & Redundancy of "best" ("Select the best package"):**
   - *Deficiency:* Executed once *prior* to the loop, "best" is never defined (highest value? smallest weight? largest ratio?), and the selected item is never passed or referenced inside the loop.
   - *Impact:* Leads to dead code or arbitrary singleton operations outside the loading cycle.
4. **Omission of Feasibility Condition:**
   - *Deficiency:* "Add suitable package" lacks an explicit numerical feasibility predicate ($w_i \le \text{RemainingCapacity}$).
   - *Impact:* An implementer may attempt to add a package exceeding remaining capacity, resulting in vehicle overloading.
5. **Absence of Fractional Division Logic:**
   - *Deficiency:* Even though the scenario explicitly states packages can be divided, there is no logic handling a package that partially exceeds remaining capacity.
   - *Impact:* An engineer will likely implement 0/1 integer skipping (losing value) or overfill the vehicle. The exact fraction $\frac{\text{Remaining}}{w_i}$ is never computed.
6. **No State Tracking for Capacity:**
   - *Deficiency:* No variable tracks remaining capacity; no decrement occurs upon package loading; "vehicle has space" is unverifiable.
   - *Impact:* Loop condition cannot be evaluated programmatically, preventing termination when full.
7. **Flawed Termination Guard:**
   - *Deficiency:* The loop terminates solely when capacity reaches zero; it fails to guard against package list exhaustion ($i > n$).
   - *Impact:* If total package weight is less than vehicle capacity, the algorithm enters an infinite loop.
8. **Undefined Result Construction:**
   - *Deficiency:* "Calculate value" and "RETURN result" do not define how total value is accumulated or whether the loaded fractions are returned.
   - *Impact:* The logistics driver receives no loading manifest indicating which packages or fractions were chosen.

---

## 3. Task 1.2: Repaired Pseudocode & Design

### Greedy-Choice Rule:
> *At each step, select the unconsidered package with the highest value-to-weight ratio ($\frac{v_i}{w_i}$). Load the entire package if it fits; otherwise, load exactly the fractional portion that completely exhausts remaining capacity and terminate.*

### SIMATS Standard Pseudocode:
```text
ALGORITHM LoadVehicle(P, n, C)
INPUT:
    P – array P[1..n] of packages where each package k has:
        P[k].id     – package identifier
        P[k].weight – positive weight (w_k > 0)
        P[k].value  – non-negative value (v_k >= 0)
    n – total number of available packages (n >= 0)
    C – vehicle carrying capacity in kg (C >= 0)
OUTPUT:
    Load       – list of ordered pairs (P[k].id, fraction) with 0 < fraction <= 1
    TotalValue – maximum monetary value achievable within capacity C
BEGIN
    FOR k ← 1 TO n DO
        P[k].ratio ← P[k].value / P[k].weight
    END FOR
    
    SORT P in descending order of ratio
    
    Remaining ← C
    TotalValue ← 0
    Load ← empty list
    i ← 1
    
    WHILE Remaining > 0 AND i <= n DO
        IF P[i].weight <= Remaining THEN
            Fraction ← 1
        ELSE
            Fraction ← Remaining / P[i].weight
        END IF
        
        APPEND (P[i].id, Fraction) TO Load
        Remaining ← Remaining - Fraction * P[i].weight
        TotalValue ← TotalValue + Fraction * P[i].value
        i ← i + 1
    END WHILE
    
    RETURN Load, TotalValue
END
```

### Complexity Analysis:
- **Time Complexity:** 
  - Ratio computation: $\Theta(n)$
  - Sorting: $\Theta(n \log n)$
  - Greedy selection loop: At most $n$ iterations $\Rightarrow \Theta(n)$
  - Overall Time: $\Theta(n \log n)$
- **Space Complexity:** $\Theta(n)$ to store ratios and the loading manifest `Load`.

---

## 4. Manual Desk-Check Trace & Calculations

### Test Instance ($C = 50\text{ kg}$):
| Package ID | Weight ($w_k$) | Value ($v_k$) | Ratio ($v_k/w_k$) | Sorted Greedy Rank |
|:---:|:---:|:---:|:---:|:---:|
| **P1** | 10 kg | 60 | 6.0 | 1 |
| **P2** | 20 kg | 100 | 5.0 | 2 |
| **P3** | 30 kg | 120 | 4.0 | 3 |
| **P4** | 15 kg | 45 | 3.0 | 4 |

### Step-by-Step State Trace:
| Iteration | Package Considered | Remaining Before | Feasibility Condition | Fraction Loaded | Remaining After | Total Value Accumulated |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | P1 (10, 60, 6.0) | 50 kg | $10 \le 50$ (True) | 1.0 | $50 - 10 = 40\text{ kg}$ | $0 + 60 = 60$ |
| **2** | P2 (20, 100, 5.0) | 40 kg | $20 \le 40$ (True) | 1.0 | $40 - 20 = 20\text{ kg}$ | $60 + 100 = 160$ |
| **3** | P3 (30, 120, 4.0) | 20 kg | $30 \le 20$ (False) | $\frac{20}{30} = \frac{2}{3}$ | $20 - (\frac{2}{3} \times 30) = 0\text{ kg}$ | $160 + (\frac{2}{3} \times 120) = 240$ |
| **End** | P4 (15, 45, 3.0) | 0 kg | Loop guard `Remaining > 0` fails | – | 0 kg | **240.0** |

**Final Manifest:** `Load = {(P1, 1.0), (P2, 1.0), (P3, 0.667)}`, `TotalValue = 240.00`. Total Weight = 50 kg.

---

## 5. Task 1.3: Design Defence
> *Why this qualifies as algorithmic pseudocode rather than programming code or informal English:*
> 
> My rewritten `LoadVehicle` is pseudocode because it unambiguously specifies all algorithmic decisions (explicit inputs/outputs, the density-ratio greedy choice, feasibility testing, fractional handling, state decrements, and dual-termination conditions) while remaining strictly independent of any programming language. It utilizes standard handbook constructs (`ALGORITHM`, `INPUT`/`OUTPUT`, `BEGIN...END`, `←`, `WHILE`, and `IF...THEN...ELSE`) alongside accepted abstractions (`SORT`), completely omitting language-specific syntax, type signatures, or memory allocators. Unlike ambiguous prose, each statement maps directly to an executable algorithmic primitive with zero guesswork for implementers.

---

## 6. Implementation & Verification Details

### File Manifest:
- `load_vehicle.py`: Pure Python 3.13 implementation of the repaired algorithm, loading data from `packages.csv` and printing the full state trace.
- `packages.csv`: Package input dataset (`id,weight,value`).
- `test_load_vehicle.py`: Automated verification suite asserting:
  1. Exact agreement with the manual desk-check trace ($240.00$).
  2. Optimal fractional equivalence against an exhaustive permutation generator over $n!$ orders across 300 randomized inputs.
  3. Boundary scenarios ($C=0$, $n=0$, large capacity fitting all items).

### How to Run:
```bash
# Execute desk-check demonstration
python load_vehicle.py

# Execute automated test suite
python test_load_vehicle.py
```

### Verification Result:
```text
=== TASK 1: TEST SUITE ===
PASS test_official_desk_check: total value 240.00
PASS test_zero_capacity: C=0 loads nothing
PASS test_empty_packages: n=0 returns empty load
PASS test_all_fit: C=100 loads all packages
PASS test_exact_capacity: C=10 loads P1 completely
PASS test_fractional_split_precision
PASS test_exhaustive_random_instances (300 randomized instances)
PASS test_deterministic_behavior
PASS test_single_item_fits
RESULT: 9/9 tests passed
```
