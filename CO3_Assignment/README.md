# CSA06 â€“ Assignment 3 (CO3): Divide and Conquer â€“ Design, Analysis and Experimental Validation

**Course:** CSA06 â€“ Design and Analysis of Algorithms Â· SIMATS Engineering Â· **Mode:** Pair Work â€“ 2 students per group Â·
**Student A:** K DHEEPAK (192411108) Â· **Student B:** [Student B Name] ([Reg. No.]) Â· **Date:** 19 November 2026 Â·
**Total marks:** 50

## Overview

This folder answers the official CO3 question paper (Assignment 3, "Pair Work"). All seven questions are set in one
scenario, a **city drone-delivery operations centre**. Every algorithm is hand-written in pure Python with explicit
operation counters, tested against an independent reference, measured, and analysed with its recurrence.

The report reproduces each official question verbatim. The answer follows the paper's structure: the
**Shared Group Work**, then the **Student A** and **Student B** parts with each bullet answered, then the joint question. Each
algorithm has a flowchart, decomposition or recursion-tree diagrams, code screenshots, execution-output screenshots
and graphs.

**Q7 problem.** The paper leaves the Day-4 problem to be announced on Day 4. To complete the challenge, the pair chose
a problem that is new relative to Q1â€“Q6: the **most profitable contiguous run of delivery hours (Maximum Subarray
Sum)**. If a different Day-4 problem is given, the same six-stage process applies.

## Questions and individual responsibilities (as prescribed by the paper)

| Q (marks) | Topic | Student A â€“ primary | Student B â€“ primary | Joint |
|---|---|---|---|---|
| Q1 (6) | Decomposition and Elimination in Ordered Data: Max/Min + Binary Search | Max/Min design & mathematical analysis; binary-search experimental investigation | Max/Min experimental validation; binary-search elimination logic | strategy, base case, returns, implementation, tests |
| Q2 (7) | The Quality of Decomposition in Sorting | Quick Sort investigation: designed balanced/unbalanced inputs, partition sizes, recursion depth | Comparative D&C analysis of Merge Sort vs Quick Sort, O(nÂ²) under imbalance | implementation, pivot strategy (last element), experiments, Joint Design Question |
| Q3 (7) | Breaking the Quadratic Barrier: Karatsuba | algorithmic derivation, recurrence, Î˜(n^1.585) | crossover investigation: repeated timing, counts, crossover, overhead | implementation, Joint Conclusion |
| Q4 (7) | The Reality of Strassen's Matrix Multiplication (roles reversed) | experimental & engineering analysis: counts, repeated times, crossover, overhead, memory | algebraic design & correctness: 8 â†’ 7 products, padding | implementation, verification, Joint Engineering Decision |
| Q5 (6) | Upgrading Closest Pair Using D&C | decomposition design, strip/boundary | comparative evidence: distances, growth, practical crossover | design, implementation, Cross-Understanding |
| Q6 (7) | Advanced D&C Mini-Investigations | Median of Medians (+ verification on MitM) | Meet-in-the-Middle subset sum (+ verification on pivot quality) | tests, graphs |
| Q7 (10) | Day-4 Design Challenge (Stages 1â€“6) | Stage 1 proposal A; Stage 4 mathematical validation; Stage 5 evidence defence | Stage 1 proposal B; Stage 4 experimental validation; Stage 5 recurrence defence | Stages 2, 3 and 6 |

The contribution record (`Final_Report/Student_Contribution_Record.docx`) must be confirmed by both students.

## How to run (Python 3.13 + matplotlib; numpy only for the Q4 verification)

```
cd Q1_MaxMin_Binary_Search/Implementation_Code
py -3 q1_maxmin_binsearch.py      # demonstration with traces
py -3 q1_experiments.py           # experiments -> results/*.csv
py -3 q1_tests.py                 # PASS/FAIL lines + RESULT
py -3 q1_graphs.py                # graphs and diagrams -> results/*.png
py -3 q1_flowcharts.py            # flowcharts -> ../Pseudocode/*.png
```

The other questions follow the same pattern.

| Q | Main program | Additional programs |
|---|---|---|
| Q2 | `q2_sorting.py` | `q2_partition_study.py` |
| Q3 | `q3_karatsuba.py` | `q3_crossover.py` |
| Q4 | `q4_strassen.py` | `q4_overhead.py` |
| Q5 | `q5_closest_pair.py` | `q5_crossover.py` |
| Q6 | `q6_median_of_medians.py`, `q6_meet_in_the_middle.py` | `q6_pivot_quality.py`, `q6_mitm_memory.py` |
| Q7 | `q7_max_subarray.py` | `q7_experiments.py`, and the two Stage-1 proposals in `Student_A_Initial_Design/` and `Student_B_Initial_Design/` |

Every random generator is seeded (42), so operation counts are exactly reproducible. Times vary with the load on the
machine.

**Tests:** Q1 18/18, Q2 20/20, Q3 17/17, Q4 17/17, Q5 22/22, Q6 32/32, Q7 20/20, a total of **146/146 passed**.

## Folder structure

```
CO3_Assignment/
â”œâ”€â”€ Q1_MaxMin_Binary_Search/            Pseudocode/ (md + flowcharts)  Implementation_Code/ (+ results/)  Output_Screenshots/
â”œâ”€â”€ Q2_MergeSort_QuickSort/             Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
â”œâ”€â”€ Q3_Karatsuba_Multiplication/        Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
â”œâ”€â”€ Q4_Strassen_Matrix_Multiplication/  Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
â”œâ”€â”€ Q5_Divide_Conquer_Closest_Pair/     Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
â”œâ”€â”€ Q6_Advanced_Divide_Conquer/
â”‚   â”œâ”€â”€ Median_of_Medians/              README.md (Student A investigation) + results/ (CSV, graphs)
â”‚   â”œâ”€â”€ Meet_in_the_Middle/             README.md (Student B investigation) + results/ (CSV, graphs)
â”‚   â””â”€â”€ Pseudocode/  Implementation_Code/  Output_Screenshots/
â”œâ”€â”€ Q7_Day4_Design_Challenge/
â”‚   â”œâ”€â”€ Student_A_Initial_Design/       README.md + proposal_a_midpoint_split.py + flowchart (Stage 1, kept unchanged)
â”‚   â”œâ”€â”€ Student_B_Initial_Design/       README.md + proposal_b_four_tuple.py + flowchart (Stage 1, kept unchanged)
â”‚   â”œâ”€â”€ Joint_Final_Design/             README.md (Stage 2 comparison record, Stage 3 joint design)
â”‚   â””â”€â”€ Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
â”œâ”€â”€ Final_Report/
â”‚   â”œâ”€â”€ CO3_Assignment_Report.docx / .pdf        (report in the department's sample format)
â”‚   â””â”€â”€ Student_Contribution_Record.docx           (Question | Student A | Student B | Joint Work)
â””â”€â”€ README.md
```

Each question folder contains three sub-folders:

- `Pseudocode/` holds the pseudocode, the divide/conquer/combine description, the recurrence and the flowchart PNGs.
- `Implementation_Code/` holds the algorithms with counters, the experiment programs, the tests, and the graph and
  flowchart scripts. CSV files and graphs go to `results/`.
- `Output_Screenshots/` holds screenshots of the main algorithm code, screenshots of every real execution, and the
  captured `.txt` output.

