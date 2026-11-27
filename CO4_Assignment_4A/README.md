# CSA06 â€“ Assignment 4A (CO4), Part I: Algorithmic Design through Pseudocode

**Student:** K DHEEPAK Â· **Reg. No.:** 192411108 Â· **Course:** CSA06 â€“ Design and Analysis of Algorithms  
**Institution:** SIMATS Engineering Â· **Date:** 19 November 2026  
**Course Outcome:** CO4 â€“ Solve optimization problems using Dynamic Programming and Greedy strategies  
**Nature:** Individual Â· **Duration:** One Week Â· **Total Marks:** 50 Marks  

---

## Executive Summary & Official Syllabus Coverage

This repository contains the complete, rigorous solutions for **Assignment 4A (CO4 â€“ Part I: Algorithmic Design through Pseudocode)**, adhering strictly to the *SIMATS Engineering Handbook for Algorithmic Pseudocode* and the departmental submission instructions.

Every task exhibits the required engineering design progression:
$$\text{Interpret the Problem} \longrightarrow \text{Identify Decision/State} \longrightarrow \text{Design the Logic} \longrightarrow \text{Write Pseudocode} \longrightarrow \text{Desk-Check Trace} \longrightarrow \text{Challenge/Attack} \longrightarrow \text{Refine}$$

| Task | Title (Official Question Paper) | Core Strategy | Primary Manual Result | Verification Reference | Marks | Documentation |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **Task 1** | **Algorithm Design Review:** Diagnose and Repair Poor Pseudocode | Greedy (density ratio $\frac{v_i}{w_i}$) | 8 defects; repaired `LoadVehicle`; C=50 loads P1, P2, 2/3 of P3 $\to$ **240.0** | Exhaustive $n!$ orders (300 instances) | 6 | [Task 1 Docs](Source_Code/Task_1/README.md) |
| **Task 2** | **Business Requirement to Greedy Pseudocode:** Job Sequencing with Deadlines | Greedy (descending profit, latest free slot) | Base: [C, A, D] = **180**; Challenge ($p_B \to 90$ displaces C) = **210** | Power set $2^n$ brute force (400 instances) | 8 | [Task 2 Docs](Source_Code/Task_2/README.md) |
| **Task 3** | **Recurrence to Executable Logic:** Dynamic Programming â€“ 0/1 Knapsack | Dynamic Programming ($\text{DP}[i][w]$) | $\text{DP}[4][7] = \mathbf{45}$; Reconstructed subset = **{Q, R}** | Power set $2^n$ brute force (400 instances) | 9 | [Task 3 Docs](Source_Code/Task_3/README.md) |
| **Task 4** | **Pseudocode Forensics:** Find, Explain and Repair Algorithmic Defect | String DP ($\text{DP}[i]$) | Defect: missing $\text{DP}[j]$; Failing case `catsdog` caught at $\text{DP}[7]$ | Memoized recursive segmenter (2,000 texts) | 7 | [Task 4 Docs](Source_Code/Task_4/README.md) |
| **Task 5** | **Same Graph, Different Reasoning:** Dijkstra, Bellman-Ford, Floyd | Greedy vs. Edge DP vs. Vertex DP | Distances from A: B=4, C=6, D=7, E=10; Negative edge analysis; Full $D^{(5)}$ | Simple-path brute force (400 graphs) | 7 | [Task 5 Docs](Source_Code/Task_5/README.md) |
| **Task 6** | **Compulsory Design Challenge:** Energy-Aware Cloud Job Scheduling | DP over jobs sorted by finish time | Base: {J2, J5, J7, J8} = **200**; Adversarial 6-job stress test = **150** | Power set $2^n$ brute force (500 instances) | 13 | [Task 6 Docs](Source_Code/Task_6/README.md) |
| **Total** | | | | **58/58 Tests Passed (100%)** | **50** | |

---

## Prescribed Submission Directory Structure

```
CO4_Assignment_4A/
â”‚
â”œâ”€â”€ Source_Code/
â”‚   â”œâ”€â”€ Task_1/
â”‚   â”‚   â”œâ”€â”€ load_vehicle.py              # Fractional Knapsack solver & trace generator
â”‚   â”‚   â”œâ”€â”€ packages.csv                 # Official package input dataset
â”‚   â”‚   â”œâ”€â”€ test_load_vehicle.py         # 9/9 automated test suite
â”‚   â”‚   â””â”€â”€ README.md                    # Detailed Task 1 documentation & traces
â”‚   â”‚
â”‚   â”œâ”€â”€ Task_2/
â”‚   â”‚   â”œâ”€â”€ job_sequencing.py            # Unit-time job sequencing with deadlines
â”‚   â”‚   â”œâ”€â”€ jobs.csv                     # Official job input dataset
â”‚   â”‚   â”œâ”€â”€ test_job_sequencing.py       # 9/9 automated test suite
â”‚   â”‚   â””â”€â”€ README.md                    # Detailed Task 2 documentation & traces
â”‚   â”‚
â”‚   â”œâ”€â”€ Task_3/
â”‚   â”‚   â”œâ”€â”€ knapsack_dp.py               # 0/1 Knapsack DP table builder & reconstruction
â”‚   â”‚   â”œâ”€â”€ items.csv                    # Cargo items input dataset
â”‚   â”‚   â”œâ”€â”€ test_knapsack_dp.py          # 8/8 automated test suite
â”‚   â”‚   â””â”€â”€ README.md                    # Detailed Task 3 documentation & traces
â”‚   â”‚
â”‚   â”œâ”€â”€ Task_4/
â”‚   â”‚   â”œâ”€â”€ word_break.py                # Faulty vs. repaired WordBreak comparison
â”‚   â”‚   â”œâ”€â”€ word_break_cases.csv         # Vocabulary and test strings
â”‚   â”‚   â”œâ”€â”€ test_word_break.py           # 10/10 automated test suite
â”‚   â”‚   â””â”€â”€ README.md                    # Detailed Task 4 documentation & traces
â”‚   â”‚
â”‚   â”œâ”€â”€ Task_5/
â”‚   â”‚   â”œâ”€â”€ single_source.py             # Dijkstra & Bellman-Ford implementations
â”‚   â”‚   â”œâ”€â”€ floyd_all_pairs.py           # Floyd-Warshall all-pairs matrix DP
â”‚   â”‚   â”œâ”€â”€ graph_common.py              # Shared graph structures
â”‚   â”‚   â”œâ”€â”€ graph.csv                    # Directed weighted graph edge list
â”‚   â”‚   â”œâ”€â”€ test_shortest_paths.py       # 11/11 automated test suite
â”‚   â”‚   â””â”€â”€ README.md                    # Detailed Task 5 documentation & traces
â”‚   â”‚
â”‚   â””â”€â”€ Task_6/
â”‚       â”œâ”€â”€ energy_scheduling.py         # Day-4 Design Challenge DP implementation
â”‚       â”œâ”€â”€ compare_strategies.py        # Evaluation of 4 greedy heuristics vs DP
â”‚       â”œâ”€â”€ jobs.csv                     # Official 8-job dataset
â”‚       â”œâ”€â”€ adversarial_jobs.csv         # Student-designed 6-job adversarial dataset
â”‚       â”œâ”€â”€ test_energy_scheduling.py    # 11/11 automated test suite
â”‚       â””â”€â”€ README.md                    # Detailed Task 6 documentation & traces
â”‚
â”œâ”€â”€ Report/
â”‚   â”œâ”€â”€ CO4_Assignment_4A_Report.pdf     # Primary official deliverable (84 pages)
â”‚   â”œâ”€â”€ CO4_Assignment_4A_Report.docx    # Word master document with cover and signatures
â”‚   â”œâ”€â”€ CO4_Assignment_4A_Report.md      # Full Markdown source with all derivations
â”‚   â”œâ”€â”€ Diagrams/                        # 16 visual flowcharts and state diagrams
â”‚   â””â”€â”€ Screenshots/                     # Terminal execution and code screenshots
â”‚
â”œâ”€â”€ Test_Cases/
â”‚   â””â”€â”€ run_all_tests_log.txt            # Consolidated 58/58 test pass verification log
â”‚
â””â”€â”€ README.md                            # Main assignment documentation
```

---

## Detailed Task Summaries

### Task 1: Algorithm Design Review (Fractional Knapsack)
- **Diagnosis:** Identified 8 algorithmic deficiencies in junior engineer's draft: missing contract parameters, undefined "arrange" key, obsolete "best" call prior to loop, absent feasibility predicate, missing fractional cut logic, no remaining capacity state variable, unbounded termination loop guard, and undefined manifest return.
- **Repaired Design:** Language-independent `LoadVehicle` sorting by $\frac{v_i}{w_i}$ ratio in $O(n \log n)$ time and $O(n)$ space.
- **Trace:** Manual trace on instance $C = 50\text{ kg}$ loads P1 ($10\text{ kg}, 60$), P2 ($20\text{ kg}, 100$), and $\frac{2}{3}$ of P3 ($20\text{ kg}, 80$) $\Rightarrow$ **Total Value = 240.0**.
- **Defence:** Strictly algorithmic pseudocode omitting language syntax, libraries, and types while specifying all operational predicates.
- **Documentation:** See [Task 1 Detailed Documentation](Source_Code/Task_1/README.md).

### Task 2: Business Requirement to Greedy Pseudocode (Job Sequencing)
- **Model:** Matroid formulation of independent unit-time jobs maximizing profit over slots $1..\min(n, \max d_k)$.
- **Greedy Rule:** Sort descending by profit; greedily assign to latest free slot $t \le d_k$.
- **Trace:** Base instance A(2, 80), B(1, 35), C(2, 60), D(3, 40), E(1, 25) schedules Slot 1 = C, Slot 2 = A, Slot 3 = D $\Rightarrow$ **Profit = 180**.
- **Challenge:** Increasing profit of B to 90 shifts B to Slot 1, displacing C $\Rightarrow$ Schedule [B, A, D], **Profit = 210**.
- **Documentation:** See [Task 2 Detailed Documentation](Source_Code/Task_2/README.md).

### Task 3: Recurrence to Executable Logic (0/1 Knapsack DP)
- **State:** $\text{DP}[i][w]$ represents optimal cumulative value selecting from items $1..i$ within capacity limit $w$.
- **Recurrence:** $\text{DP}[i][w] = \max(\text{DP}[i-1][w], \; val_i + \text{DP}[i-1][w - wt_i])$ when $wt_i \le w$.
- **Trace:** Instance with capacity $W=7$ and items P(2, 12), Q(3, 20), R(4, 25), S(5, 30) computes $\text{DP}[4][7] = \mathbf{45}$.
- **Reconstruction:** Backtracking selects items **Q** and **R** (Weight $3+4=7 \le 7$).
- **Dependencies:** Strictly row $i-1$ dependent, justifying the outer loop ordering $i = 1 \to n$.
- **Documentation:** See [Task 3 Detailed Documentation](Source_Code/Task_3/README.md).

### Task 4: Pseudocode Forensics (WordBreak)
- **Defect:** Inner condition checks only $substring(Text, j, i) \in Dictionary$ without verifying whether prefix $\text{DP}[j]$ is segmentable.
- **Counter-Example:** Text `catsdog` with dict `{"cat", "dog"}` falsely returns `TRUE` because suffix `dog` matches, ignoring unsegmentable prefix `cats`. First faulty state is $\text{DP}[7]$.
- **Minimal Fix:** Conjunction `IF DP[j] = TRUE AND substring(...) THEN`.
- **Regression:** Text `catdog` preserves `TRUE`; `dogcatx` preserves `FALSE`. 480 flaws caught across 2,000 random strings.
- **Documentation:** See [Task 4 Detailed Documentation](Source_Code/Task_4/README.md).

### Task 5: Same Graph, Different Reasoning (Shortest Paths)
- **Dijkstra:** Greedy selection via `EXTRACT_MIN`. Distances from A: B=4, C=6, D=7, E=10.
- **Bellman-Ford:** Repeated relaxation over $|V|-1$ passes. Demonstrates failure of greedy choice under negative edge scenario N1 ($A \to C \to B = 1 < 2$) and detects negative cycle in scenario N2.
- **Floyd-Warshall:** All-pairs DP over intermediate vertices $v_1..v_k$. Transition $D^{(k)}[i][j] = \min(D^{(k-1)}[i][j], D^{(k-1)}[i][k] + D^{(k-1)}[k][j])$.
- **Documentation:** See [Task 5 Detailed Documentation](Source_Code/Task_5/README.md).

### Task 6: Compulsory Day-4 Design Challenge (Energy-Aware Cloud Scheduling)
- **Problem Abstraction:** Weighted Interval Scheduling over 8 batch jobs on an energy-efficient server.
- **Strategy Selection:** Evaluated 4 greedy heuristics (Earliest Finish, Highest Value, Shortest Duration, Value Density), proving failure counter-examples for each. Selected Dynamic Programming over jobs sorted by finish time.
- **DP Formulation:** $\text{OPT}[j] = \max(\text{OPT}[j-1], \; v_j + \text{OPT}[p(j)])$, where $p(j)$ is computed via binary search.
- **Trace:** Base 8-job dataset yields optimal schedule **{J2, J5, J7, J8}** with cumulative energy savings of **200**.
- **Adversarial Attack:** Constructed 6-job dataset with a high-value trap (K1 = 100) and an earliest-finish trap (K5 = 5). DP tentatively prefers K1 at state 4, then overturns it at critical state 5, achieving global optimum **150** ({K2, K3, K4, K6}).
- **Documentation:** See [Task 6 Detailed Documentation](Source_Code/Task_6/README.md).

---

## Automated Verification & Test Results

All verification test suites run deterministically in Python 3.13 without third-party runtime dependencies:

```bash
# Run all tests sequentially
python Source_Code/Task_1/test_load_vehicle.py
python Source_Code/Task_2/test_job_sequencing.py
python Source_Code/Task_3/test_knapsack_dp.py
python Source_Code/Task_4/test_word_break.py
python Source_Code/Task_5/test_shortest_paths.py
python Source_Code/Task_6/test_energy_scheduling.py
```

### Consolidated Verification Summary:
```text
========================================================================
CSA06 DAA - ASSIGNMENT 4A (CO4) COMPREHENSIVE AUTOMATED VERIFICATION LOG
========================================================================
Task 1 (load_vehicle.py)         : 9/9   PASSED (Exhaustive n! check across 300 instances)
Task 2 (job_sequencing.py)       : 9/9   PASSED (Exhaustive 2^n power set across 400 instances)
Task 3 (knapsack_dp.py)          : 8/8   PASSED (Exhaustive 2^n power set across 400 instances)
Task 4 (word_break.py)           : 10/10 PASSED (Memoized recursive reference across 2000 instances)
Task 5 (shortest_paths.py)       : 11/11 PASSED (Simple-path brute force across 400 graphs)
Task 6 (energy_scheduling.py)    : 11/11 PASSED (Exhaustive 2^n power set across 500 instances)
========================================================================
OVERALL SUITE RESULT: 58/58 tests passed (100% Pass Rate)
========================================================================
```
Full execution logs are archived in [`Test_Cases/run_all_tests_log.txt`](Test_Cases/run_all_tests_log.txt).

