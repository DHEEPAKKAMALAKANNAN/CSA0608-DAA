# Task 2: From Business Requirement to Greedy Pseudocode – Job Sequencing with Deadlines

## 1. Problem Overview
- **Scenario:** A cloud service company processes independent batch computing jobs. Each job requires exactly one unit-time processing slot.
- **Attributes:** Each job has a `Job ID`, an integer `Deadline` ($d_k \ge 1$), and a `Profit` ($p_k \ge 0$).
- **Rule:** A job yields profit only if completed on or before its deadline. Each unit slot can host at most one job.
- **Objective:** Schedule a subset of jobs across available slots to **maximize total earned profit**.

---

## 2. Task 2.1: Formal Model of the Requirement

| Component | Formal Mathematical / Algorithmic Specification |
|:---|:---|
| **Input** | A set $J$ of $n$ independent jobs $\{J_1, J_2, \dots, J_n\}$. Each job $k$ has identifier $id_k$, deadline $d_k \in \mathbb{Z}^+$, and profit $p_k \in \mathbb{R}_{\ge 0}$. Discrete time slots are numbered $1, 2, 3, \dots, m$ where $m = \min(n, \max_{k} d_k)$. |
| **Output** | An assignment array $\text{Slot}[1..m]$ where $\text{Slot}[t]$ contains the assigned job ID or $\text{EMPTY}$, a list of $\text{Rejected}$ jobs, and the scalar $\text{TotalProfit}$. |
| **Objective** | $\text{Maximize } \sum_{t=1}^m p_{\text{Slot}[t]}$ subject to $\text{Slot}[t] \neq \text{EMPTY}$. |
| **Constraints** | 1. Unit execution: each job requires exactly 1 slot.<br>2. Exclusivity: at most one job per slot.<br>3. Deadline feasibility: if job $k$ is scheduled in slot $t$, then $1 \le t \le d_k$.<br>4. Non-duplication: each job runs at most once. |
| **Decisions** | For each job: whether to accept or reject it, and if accepted, the exact slot $t \in [1, d_k]$ assigned to it. |
| **Feasibility Condition** | A job $k$ can be feasibly added to partial schedule $S$ if there exists an unoccupied slot $t \le d_k$. By Hall's condition on matroids, a subset of jobs $S$ is feasible if and only if for all $t$, $|\{j \in S : d_j \le t\}| \le t$. |

---

## 3. Task 2.2: Greedy Hypothesis & Theoretical Justification

### Greedy-Choice Rule:
> *Process all jobs in descending order of profit. For each job, schedule it in the latest currently unoccupied slot $t$ such that $1 \le t \le d_k$; if no such slot exists, reject the job.*

### Theoretical Justification:
1. **Profit Maximization (Exchange Argument):** By considering highest-profit jobs first, whenever a lower-profit job is blocked, all blocking jobs earn at least as much profit. Swapping an admitted job for any displaced job cannot increase profit.
2. **Latest Slot Placement (Option Preservation):** Placing job $k$ as late as possible ($t = \min(d_k, \text{free slots})$) leaves earlier slots open for subsequent jobs that have more restrictive deadlines ($d_j < d_k$).
3. **Matroid Structure:** The system of feasible job subsets forms a graphic/hereditary matroid system satisfying the independent set exchange property. Consequently, the greedy priority rule provably converges to the global maximum.

---

## 4. Task 2.3: SIMATS Standard Pseudocode

```text
ALGORITHM JobSequencing(J, n)
INPUT:
    J – array J[1..n] of jobs, where each job k has:
        J[k].id       – unique job identifier
        J[k].deadline – integer deadline (d_k >= 1)
        J[k].profit   – non-negative profit (p_k >= 0)
    n – total number of submitted jobs (n >= 0)
OUTPUT:
    Slot        – array Slot[1..m] mapping slot t to job ID or EMPTY
    Rejected    – list of IDs of unassigned jobs
    TotalProfit – maximum cumulative profit earned
BEGIN
    SORT J in descending order of profit (break ties by earlier deadline)
    
    MaxD ← 0
    FOR k ← 1 TO n DO
        IF J[k].deadline > MaxD THEN
            MaxD ← J[k].deadline
        END IF
    END FOR
    
    m ← MIN(n, MaxD)
    
    FOR t ← 1 TO m DO
        Slot[t] ← EMPTY
    END FOR
    
    Rejected ← empty list
    TotalProfit ← 0
    
    FOR k ← 1 TO n DO
        t ← MIN(J[k].deadline, m)
        WHILE t >= 1 AND Slot[t] ≠ EMPTY DO
            t ← t - 1
        END WHILE
        
        IF t >= 1 THEN
            Slot[t] ← J[k].id
            TotalProfit ← TotalProfit + J[k].profit
        ELSE
            APPEND J[k].id TO Rejected
        END IF
    END FOR
    
    RETURN Slot, Rejected, TotalProfit
END
```

### Complexity:
- **Time Complexity:** Sorting requires $\Theta(n \log n)$. The placement loop inspects up to $m$ slots for each of $n$ jobs $\Rightarrow O(n \cdot m) \subseteq O(n^2)$. 
- **Refinement:** Using a Disjoint-Set Union-Find (DSU) structure to point directly to the latest available slot achieves near-linear $O(n \log n)$ or $O(n \cdot \alpha(m))$ time.
- **Space Complexity:** $\Theta(n)$ for schedule and rejection tracking.

---

## 5. Task 2.4: Manual Desk-Check Trace

### Given Problem Instance:
| Job ID | Deadline | Profit | Sorted Greedy Order |
|:---:|:---:|:---:|:---:|
| **A** | 2 | 80 | 1 |
| **B** | 1 | 35 | 4 |
| **C** | 2 | 60 | 2 |
| **D** | 3 | 40 | 3 |
| **E** | 1 | 25 | 5 |

- $n = 5, \text{MaxD} = 3 \Rightarrow m = \min(5, 3) = 3$.
- Initial state: $\text{Slot}[1..3] = [\text{EMPTY}, \text{EMPTY}, \text{EMPTY}]$, $\text{TotalProfit} = 0$.

### Step-by-Step Execution Trace:
| Step | Job ($d, p$) | Target $t$ | Search / Inspection | Decision | Resulting Slots `[1, 2, 3]` | Total Profit |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | A (2, 80) | 2 | Slot 2 is EMPTY | Accept $\to$ Slot 2 | `[EMPTY, A, EMPTY]` | 80 |
| **2** | C (2, 60) | 2 | Slot 2 busy $\to$ Slot 1 EMPTY | Accept $\to$ Slot 1 | `[C, A, EMPTY]` | $80 + 60 = 140$ |
| **3** | D (3, 40) | 3 | Slot 3 is EMPTY | Accept $\to$ Slot 3 | `[C, A, D]` | $140 + 40 = 180$ |
| **4** | B (1, 35) | 1 | Slot 1 busy $\to t=0$ | **Reject** | `[C, A, D]` | 180 |
| **5** | E (1, 25) | 1 | Slot 1 busy $\to t=0$ | **Reject** | `[C, A, D]` | 180 |

**Schedule Outcome:** Slot 1 = **C**, Slot 2 = **A**, Slot 3 = **D**. Rejected = `{B, E}`. **Total Profit = 180**.

---

## 6. Task 2.5: Challenge Your Design (Input Variation)

### Parameter Mutation:
- Change profit of job **B** from $35 \to \mathbf{90}$ (all deadlines and other profits remain identical).

### Pre-Trace Hypothesis & Prediction:
1. **Priority Inversion:** With $p_B = 90$, B becomes the top-ranked job in the sorted queue ($B(90) > A(80) > C(60) > D(40) > E(25)$).
2. **First Slot Preemption:** B has deadline 1 and will immediately occupy Slot 1.
3. **Displacement of C:** Job A will still occupy Slot 2. When Job C (deadline 2) is considered, it will inspect Slot 2 (busy with A) and Slot 1 (busy with B). Finding no slot $\le 2$ available, **C will be rejected**.
4. **Predicted Result:** Final schedule will be `[Slot 1: B, Slot 2: A, Slot 3: D]`, yielding $\text{Profit} = 90 + 80 + 40 = \mathbf{210}$.

### Verification Trace for Modified Instance:
| Step | Job ($d, p$) | Target $t$ | Search / Inspection | Decision | Resulting Slots `[1, 2, 3]` | Total Profit |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | B (1, 90) | 1 | Slot 1 EMPTY | Accept $\to$ Slot 1 | `[B, EMPTY, EMPTY]` | 90 |
| **2** | A (2, 80) | 2 | Slot 2 EMPTY | Accept $\to$ Slot 2 | `[B, A, EMPTY]` | $90 + 80 = 170$ |
| **3** | C (2, 60) | 2 | Slot 2 busy, Slot 1 busy $\to t=0$ | **Reject (Displaced)** | `[B, A, EMPTY]` | 170 |
| **4** | D (3, 40) | 3 | Slot 3 EMPTY | Accept $\to$ Slot 3 | `[B, A, D]` | $170 + 40 = 210$ |
| **5** | E (1, 25) | 1 | Slot 1 busy $\to t=0$ | **Reject** | `[B, A, D]` | 210 |

**Conclusion:** Prediction verified with exact fidelity. Total profit rises to **210**, matching global exhaustive search optimum.

---

## 7. Implementation & Verification Details

### File Manifest:
- `job_sequencing.py`: Pure Python 3.13 implementation with automated trace table generator.
- `jobs.csv`: Official input dataset.
- `test_job_sequencing.py`: Test suite testing base instance, modified instance, boundary conditions, and 400 random instances against $2^n$ exhaustive subset enumeration.

### How to Run:
```bash
python job_sequencing.py
python test_job_sequencing.py
```

### Verification Result:
```text
=== TASK 2: TEST SUITE ===
PASS test_official_instance_profit: 180 (C, A, D)
PASS test_modified_instance_profit: 210 (B, A, D)
PASS test_all_deadlines_equal: selects highest profit
PASS test_tight_deadlines_exhaustion
PASS test_empty_job_set
PASS test_single_job
PASS test_exhaustive_brute_force_random (400 randomized instances)
PASS test_deterministic_tie_breaking
PASS test_schedule_validity
RESULT: 9/9 tests passed
```
