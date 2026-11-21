# Task 6: Compulsory Day-4 Design Challenge – Energy-Aware Job Scheduling in a Cloud Data Centre

## 1. Problem Overview
- **Scenario:** A cloud data centre operates a specialized, high-performance, energy-efficient computing server. During an off-peak maintenance window, multiple computational batch jobs are awaiting execution.
- **Job Attributes:** Each job $j$ has a start time $s_j$, a finish time $f_j$ ($s_j < f_j$), and an energy-saving value $v_j \ge 0$.
- **Mutual Exclusivity Constraint:** The server processes at most one job at any instant. Two jobs whose execution intervals overlap cannot both be scheduled.
- **Assumption:** Touching intervals ($f_i \le s_k$ or $f_k \le s_i$) are non-overlapping and mutually compatible.
- **Objective:** Select an optimal subset of mutually non-overlapping jobs that **maximizes total cumulative energy savings**.
- **Challenge Requirement:** The algorithmic strategy is not given. It must be derived, defended, implemented, traced, and attacked through a 6-stage engineering design progression.

---

## 2. Stage 1: Interpret the Problem

| Dimension | Formal Mathematical / Computational Formulation |
|:---|:---|
| **Input** | A collection of $n$ jobs $\{J_1, J_2, \dots, J_n\}$. Each job $j$ is characterized by a half-open interval $[s_j, f_j)$ and a weight $v_j \in \mathbb{R}_{\ge 0}$. (Official dataset: $n = 8$). |
| **Output** | An ordered sequence of selected job identifiers $\text{Selected}$ and the scalar maximum total energy-saving $\text{BestValue}$. |
| **Objective** | $\text{Maximize } \sum_{j \in \text{Selected}} v_j$. |
| **Constraints** | 1. Compatibility: $\forall \; i, k \in \text{Selected} \; (i \neq k)$, either $f_i \le s_k$ or $f_k \le s_i$.<br>2. Non-preemption: jobs must run continuously in their designated time windows without preemption, stretching, or splitting.<br>3. Unit capacity: server executes at most one job at a time. |
| **Decision Variables** | $x_j \in \{0, 1\}$ for each job $j \in \{1, \dots, n\}$. |
| **Search Space** | $2^n$ combinations ($2^8 = 256$ subsets for the official instance). Problem is isomorphic to the classic **Weighted Interval Scheduling** problem. |

---

## 3. Stage 2: Propose and Justify the Algorithmic Strategy

### Exhaustive Evaluation of Candidate Strategies:
To select the correct design principle, six candidate strategies were evaluated against adversarial counter-examples:

| Strategy | Decision Principle | Official Data Result (Optimum = 200) | Failure Counter-Example $[s, f) = v$ | Algorithmic Verdict |
|:---|:---|:---:|:---|:---|
| **Earliest Finish Time** | Greedily pick compatible job finishing earliest | 160 (J1, J3, J4, J6, J8) | $X_1 [0, 2)=1, \; X_2 [1, 10)=100$<br>Yields $1$, optimum is $100$. | **Fails:** Ignores energy value completely. |
| **Highest Value First** | Greedily pick available job with largest $v_j$ | **200** (Coincidence) | $X_1 [0, 10)=50, \; X_2 [0, 5)=30, \; X_3 [5, 10)=30$<br>Yields $50$, optimum is $60$. | **Fails:** Commits to long high-value job, ignoring opportunity cost. |
| **Shortest Duration First** | Greedily pick compatible job with minimum $f_j - s_j$ | 160 (J1, J3, J4, J6, J8) | $X_1 [4, 6)=10, \; X_2 [0, 5)=40, \; X_3 [5, 10)=40$<br>Yields $10$, optimum is $80$. | **Fails:** Short jobs can block multiple high-value jobs. |
| **Value per Unit Time** | Greedily pick highest density $\frac{v_j}{f_j - s_j}$ | 180 (J7, J4, J8, J2) | $X_1 [0, 1)=10 \; (\text{density } 10), \; X_2 [0, 10)=50 \; (\text{density } 5)$<br>Yields $10$, optimum is $50$. | **Fails:** Fails to consider cumulative value over span. |
| **Brute Force Power Set** | Enumerate all $2^n$ subsets | **200** | None (always finds optimal) | **Fails:** Complexity $\Theta(n \cdot 2^n)$; completely intractable for large $n$. |
| **Dynamic Programming (Chosen)** | Sort by finish time; decide Include vs. Exclude via stored subproblems | **200** | None (Provably optimal; 500 random verification runs) | **SELECTED:** Provably optimal, $O(n \log n)$ time complexity. |

### Justification of Chosen Strategy (Dynamic Programming):
1. **Optimal Substructure:** Sorting jobs by non-decreasing finish time ensures that for any job $j$, the earlier compatible jobs form a contiguous prefix $\{1, \dots, p(j)\}$. The optimal solution for jobs $1..j$ is either the optimal solution for $1..j-1$ (Exclude $j$) or $v_j$ plus the optimal solution for $1..p(j)$ (Include $j$).
2. **Elimination of Premature Commitments:** Unlike greedy heuristics, DP maintains both possibilities until the entire schedule is evaluated, perfectly capturing the **opportunity cost** of overlapping jobs.
3. **Efficiency:** Sorting and binary search for $p(j)$ require $O(n \log n)$; DP state filling requires $\Theta(n)$. Total time: $O(n \log n)$.

---

## 4. Stage 3: Identification of Critical State Information

### Formulation:
- **Canonical Ordering:** Jobs are sorted by finish time: $f_1 \le f_2 \le \dots \le f_n$.
- **Compatibility Pointer $p(j)$:** Defined as the largest index $i < j$ such that $f_i \le s_j$ (or $0$ if no such earlier job exists). Because jobs are sorted by finish time, jobs $1..p(j)$ are compatible with $j$, while jobs $p(j)+1..j-1$ strictly overlap $j$.
- **State Representation $\text{OPT}[j]$:** The maximum total energy-saving value achievable by selecting a mutually compatible subset from the prefix of jobs $\{1, \dots, j\}$.
- **Recurrence Relation:**
  $$\text{OPT}[j] = \max\Big(\text{OPT}[j-1], \; v_j + \text{OPT}[p(j)]\Big)$$
- **Base Condition:** $\text{OPT}[0] = 0$.
- **Reconstruction Tracking:** $\text{Take}[j] = \text{TRUE} \iff v_j + \text{OPT}[p(j)] > \text{OPT}[j-1]$ (breaking ties in favor of excluding $j$ to minimize job count).

---

## 5. Stage 4: SIMATS Standard Pseudocode

```text
ALGORITHM EnergyAwareSchedule(Job, n)
INPUT:
    Job – array Job[1..n] of waiting computational jobs, where each job j has:
        Job[j].id     – identifier
        Job[j].start  – start time (s_j)
        Job[j].finish – finish time (f_j > s_j)
        Job[j].value  – energy-saving benefit (v_j >= 0)
    n – total number of waiting jobs (n >= 0)
OUTPUT:
    Selected  – list of IDs of selected mutually non-overlapping jobs (in time order)
    BestValue – maximum cumulative energy-saving value achievable (= OPT[n])
BEGIN
    // Step 1: Preprocessing - Order jobs by ascending finish time
    SORT Job in ascending order of finish time (break ties by ascending start time)
    
    // Step 2: Preprocessing - Compute compatibility pointers p[j] via binary search
    FOR j ← 1 TO n DO
        p[j] ← 0
        Low ← 1
        High ← j - 1
        WHILE Low <= High DO
            Mid ← ⌊(Low + High) / 2⌋
            IF Job[Mid].finish <= Job[j].start THEN
                p[j] ← Mid
                Low ← Mid + 1
            ELSE
                High ← Mid - 1
            END IF
        END WHILE
    END FOR
    
    // Step 3: Base Condition
    OPT[0] ← 0
    
    // Step 4: Dynamic Programming State Transitions
    FOR j ← 1 TO n DO
        Include ← Job[j].value + OPT[p[j]]
        Exclude ← OPT[j - 1]
        
        IF Include > Exclude THEN
            OPT[j] ← Include
            Take[j] ← TRUE
        ELSE
            OPT[j] ← Exclude
            Take[j] ← FALSE
        END IF
    END FOR
    
    BestValue ← OPT[n]
    
    // Step 5: Retrospective Solution Reconstruction
    Selected ← empty list
    j ← n
    WHILE j > 0 DO
        IF Take[j] = TRUE THEN
            INSERT Job[j].id at front of Selected
            j ← p[j]
        ELSE
            j ← j - 1
        END IF
    END WHILE
    
    RETURN Selected, BestValue
END
```

---

## 6. Stage 5: Manual Desk-Check on Official 8-Job Dataset

### Official Job Dataset:
| Job | Start ($s$) | Finish ($f$) | Value ($v$) |
|:---:|:---:|:---:|:---:|
| **J1** | 1 | 3 | 20 |
| **J2** | 2 | 5 | 50 |
| **J3** | 4 | 6 | 30 |
| **J4** | 6 | 8 | 40 |
| **J5** | 5 | 9 | 60 |
| **J6** | 8 | 10 | 30 |
| **J7** | 9 | 11 | 50 |
| **J8** | 11 | 13 | 40 |

### Derivation of Compatibility Pointers $p(j)$:
- $j=1$ (J1): No prior jobs $\implies p(1) = 0$.
- $j=2$ (J2): $s_2 = 2 < f_1 (3) \implies p(2) = 0$.
- $j=3$ (J3): $s_3 = 4 \ge f_1 (3) \implies p(3) = 1$.
- $j=4$ (J4): $s_4 = 6 \ge f_3 (6) \implies p(4) = 3$.
- $j=5$ (J5): $s_5 = 5 \ge f_2 (5) \implies p(5) = 2$.
- $j=6$ (J6): $s_6 = 8 \ge f_4 (8) \implies p(6) = 4$.
- $j=7$ (J7): $s_7 = 9 \ge f_5 (9) \implies p(7) = 5$.
- $j=8$ (J8): $s_8 = 11 \ge f_7 (11) \implies p(8) = 7$.

### Step-by-Step DP State Transitions:
| $j$ (Job) | Include Value ($v_j + \text{OPT}[p(j)]$) | Exclude Value ($\text{OPT}[j-1]$) | Decision | $\text{OPT}[j]$ | $\text{Take}[j]$ |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **0** | – | – | Base | 0 | – |
| **1 (J1)** | $20 + \text{OPT}[0] = 20$ | 0 | Include | 20 | TRUE |
| **2 (J2)** | $50 + \text{OPT}[0] = 50$ | 20 | Include | 50 | TRUE |
| **3 (J3)** | $30 + \text{OPT}[1] = 50$ | 50 | Exclude (Tie) | 50 | FALSE |
| **4 (J4)** | $40 + \text{OPT}[3] = 90$ | 50 | Include | 90 | TRUE |
| **5 (J5)** | $60 + \text{OPT}[2] = 110$ | 90 | Include | 110 | TRUE |
| **6 (J6)** | $30 + \text{OPT}[4] = 120$ | 110 | Include | 120 | TRUE |
| **7 (J7)** | $50 + \text{OPT}[5] = 160$ | 120 | Include | 160 | TRUE |
| **8 (J8)** | $40 + \text{OPT}[7] = \mathbf{200}$ | 160 | Include | **200** | TRUE |

### Backtracking Reconstruction Trace:
- Start at $j=8$: $\text{Take}[8] = \text{TRUE} \implies \text{Select } \mathbf{J8}$; jump to $p(8) = 7$.
- At $j=7$: $\text{Take}[7] = \text{TRUE} \implies \text{Select } \mathbf{J7}$; jump to $p(7) = 5$.
- At $j=5$: $\text{Take}[5] = \text{TRUE} \implies \text{Select } \mathbf{J5}$; jump to $p(5) = 2$.
- At $j=2$: $\text{Take}[2] = \text{TRUE} \implies \text{Select } \mathbf{J2}$; jump to $p(2) = 0$.
- At $j=0$: Terminate.

**Optimal Schedule:** **{J2, J5, J7, J8}**.  
**Execution Windows:** J2 [2, 5), J5 [5, 9), J7 [9, 11), J8 [11, 13).  
*(Note: Adjacent jobs touch precisely at $t = 5, 9, 11$, which is fully valid under the problem assumption).*  
**Total Energy Saving Value:** $50 + 60 + 50 + 40 = \mathbf{200}$.

---

## 7. Stage 6: Attack Your Own Design (Adversarial Stress Test)

### Adversarial Dataset Design:
Designed with deliberate traps to expose myopic greedy vulnerabilities:
- **K1 [0, 10), v = 100:** High-value single job blocking the entire active timeline.
- **K2 [0, 3), v = 40:** First segment of a 3-job chain.
- **K3 [3, 6), v = 40:** Middle segment touching K2 and K4.
- **K4 [6, 10), v = 40:** Final segment sharing finish time with K1. (Chain $K2+K3+K4 = 120 > 100$).
- **K5 [1, 2), v = 5:** Earliest finish / shortest duration bait; conflicts with K2.
- **K6 [10, 12), v = 30:** Compatible with both K1 and K4.

### Pre-Trace Hypothesis & Prediction:
1. **Greedy Traps:** Highest-value-first will lock into K1 ($v=100$) and miss the chain ($120$). Earliest-finish-first will lock into K5 ($v=5$), forfeiting K2 ($v=40$).
2. **DP Resilience:** The DP will compute:
   - At state 3 (K3): $\text{OPT}[3] = 80$ ($K2 + K3$).
   - At state 4 (K1): $\text{Include } = 100 + 0 = 100 > 80 \implies \text{OPT}[4] = 100$ (Tentative preference for K1).
   - At state 5 (K4): $\text{Include } = 40 + \text{OPT}[3] = 40 + 80 = \mathbf{120} > 100 \implies \text{OPT}[5] = 120$. **The tentative preference for K1 is cleanly overturned!**
3. **Predicted Optimal Result:** $\text{Selected} = \{K2, K3, K4, K6\}$, $\text{Total Value} = 40 + 40 + 40 + 30 = \mathbf{150}$.

### Execution Trace on Adversarial Dataset:
| $j$ (Sorted Job) | $p(j)$ | Include ($v_j + \text{OPT}[p(j)]$) | Exclude ($\text{OPT}[j-1]$) | Decision | $\text{OPT}[j]$ |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **1 (K5 [1, 2))** | 0 | $5 + 0 = 5$ | 0 | Include | 5 |
| **2 (K2 [0, 3))** | 0 | $40 + 0 = 40$ | 5 | Include | 40 |
| **3 (K3 [3, 6))** | 2 | $40 + \text{OPT}[2] = 80$ | 40 | Include | 80 |
| **4 (K1 [0, 10))** | 0 | $100 + 0 = 100$ | 80 | Include (Tentative) | 100 |
| **5 (K4 [6, 10))** | 3 | $40 + \text{OPT}[3] = \mathbf{120}$ | 100 | **Include (Overturns K1)** | 120 |
| **6 (K6 [10, 12))** | 5 | $30 + \text{OPT}[5] = \mathbf{150}$ | 120 | Include | **150** |

**Backtracking:** $6 \to 5 \to 3 \to 2 \to 0 \implies \mathbf{\{K2, K3, K4, K6\}}$, achieving **150**.  
- Earliest Finish heuristic scored: $115$.  
- Highest Value heuristic scored: $130$.  
- Shortest Duration heuristic scored: $115$.  
**Conclusion:** The DP design successfully resisted all adversarial traps, demonstrating complete theoretical correctness and algorithmic robustness.

---

## 8. Implementation & Verification Details

### File Manifest:
- `energy_scheduling.py`: Primary implementation with full trace printer and $2^n$ brute force verification.
- `compare_strategies.py`: Evaluator comparing DP against the 4 greedy heuristics.
- `jobs.csv`: Official 8-job dataset.
- `adversarial_jobs.csv`: 6-job adversarial dataset.
- `test_energy_scheduling.py`: Automated test suite testing against brute force across 500 random instances.

### How to Run:
```bash
python energy_scheduling.py
python energy_scheduling.py adversarial_jobs.csv
python compare_strategies.py
python test_energy_scheduling.py
```

### Verification Result:
```text
=== TASK 6: TEST SUITE ===
PASS test_official_dataset_schedule: optimal 200 with {J2, J5, J7, J8}
PASS test_adversarial_dataset_schedule: optimal 150 with {K2, K3, K4, K6}
PASS test_touching_intervals_feasibility
PASS test_overlapping_chains
PASS test_all_jobs_compatible: selects all
PASS test_all_jobs_mutually_conflicting: selects highest single job
PASS test_equal_finish_times_tie_breaking
PASS test_empty_job_set: returns 0
PASS test_single_job_selection
PASS test_exhaustive_brute_force (500 randomized instances)
PASS test_binary_search_p_correctness
RESULT: 11/11 tests passed
```
