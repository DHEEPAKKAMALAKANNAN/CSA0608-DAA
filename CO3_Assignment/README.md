# CSA06 – Assignment 3 (CO3): Divide-and-Conquer Algorithm Engineering

**Course:** CSA06 – Design and Analysis of Algorithms · SIMATS Engineering · **Nature:** pair assignment ·
**Student A:** V. Vasudevan (192425324) · **Student B:** [Student B Name] ([Reg. No.]) · **Date:** 19 November 2026

## Assumed question / scope

The official question texts were not available; only the folder structure and the submission instructions were
given. The question texts used here are **reconstructed** in the style of the CO2 assignment (problem context →
challenge → predict → design → implement → measure → analyse → decide) and are reproduced verbatim at the start of
every answer in the report. Assumed marks: Q1 6, Q2 7, Q3 6, Q4 7, Q5 7, Q6 7, Q7 10 (parts A–E, 2 each) = 50.
All questions are set in one scenario, **a city drone-delivery operations centre**. If the official paper differs,
the programs and evidence can be re-mapped to its wording. Student B's name and register number are placeholders.

## Contents

```
CO3_Assignment/
├── Q1_MaxMin_Binary_Search/            Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
├── Q2_MergeSort_QuickSort/             Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
├── Q3_Karatsuba_Multiplication/        Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
├── Q4_Strassen_Matrix_Multiplication/  Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
├── Q5_Divide_Conquer_Closest_Pair/     Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
├── Q6_Advanced_Divide_Conquer/
│   ├── Median_of_Medians/              README.md (design, analysis, results) + results/ (CSV, graphs)
│   ├── Meet_in_the_Middle/             README.md (design, analysis, results) + results/ (CSV, graphs)
│   └── Pseudocode/  Implementation_Code/  Output_Screenshots/
├── Q7_Day4_Design_Challenge/
│   ├── Student_A_Initial_Design/       README.md + proposal_a_median3_hoare.py (independent proposal A)
│   ├── Student_B_Initial_Design/       README.md + proposal_b_threeway_cutoff.py (independent proposal B)
│   ├── Joint_Final_Design/             README.md (comparison, kept/rejected elements, objectives, defence)
│   └── Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
├── Final_Report/
│   ├── CO3_Assignment_Report.docx / .pdf / .md   (report in the department's sample format)
│   └── Student_Contribution_Record.docx / .md     (Student A / Student B / shared, Q1–Q7)
└── README.md
```

Each question folder contains: `Pseudocode/` (written before implementation: divide / conquer / combine, numbered
pseudocode, recurrence), `Implementation_Code/` (algorithms with operation counters, an experiment program, a test
program and a graph script; CSV files and graphs in `results/`) and `Output_Screenshots/` (code screenshots and real
execution screenshots with the captured `.txt` output).

## Questions, programs and key results

| Q | Task in the scenario | Programs (`Implementation_Code/`) | Key result |
|---|---|---|---|
| Q1 | Max/min battery temperature per flight; parcel look-up in a sorted manifest | `q1_maxmin_binsearch.py`, `q1_experiments.py`, `q1_tests.py`, `q1_graphs.py` | D&C Max–Min ⌈3n/2⌉ − 2 vs 2n − 2 comparisons (25% fewer); middle split up to 11% worse for non-powers of 2; binary search exactly ⌊log₂ n⌋ + 1 = 20 probes at 10⁶ |
| Q2 | Sorting delivery orders by deadline | `q2_sorting.py`, `q2_experiments.py`, `q2_tests.py`, `q2_graphs.py` | Merge Sort ≤ n log₂ n − n + 1 on every input; Lomuto Quick Sort n(n − 1)/2 and depth n − 1 on sorted (last pivot) and all-equal (every pivot) data |
| Q3 | Signing commands: 617- / 1,234-digit products | `q3_karatsuba.py`, `q3_experiments.py`, `q3_tests.py`, `q3_graphs.py` | multiplications exactly n² vs 3^⌈log₂ n⌉; hybrid with threshold 16 digits 3.5–4.6× fewer operations |
| Q4 | Zone-demand matrix products | `q4_strassen.py`, `q4_experiments.py`, `q4_tests.py`, `q4_graphs.py` | 7^k vs 8^k multiplications, 6(7^k − 4^k) additions; hybrid with dynamic padding and cutoff 32 recommended |
| Q5 | Closest pair of airborne drones | `q5_closest_pair.py`, `q5_experiments.py`, `q5_tests.py`, `q5_graphs.py` | D&C 1.1–1.4n distance computations, ≤ 2 strip neighbours (bound 7); 20,000 drones in 0.11–0.15 s |
| Q6 | Median delivery time; payload packing | `q6_median_of_medians.py`, `q6_meet_in_the_middle.py`, `q6_tests.py`, `q6_graphs.py` | MoM ≈ 9–10n comparisons at every size; Meet-in-the-Middle packs 40 parcels in 2 s (brute force 22) |
| Q7 | Robust sorting for the dispatch scheduler | `q7_introsort_hybrid.py`, `q7_adversary.py`, `q7_experiments.py`, `q7_tests.py`, `q7_graphs.py` (+ the two prototypes) | joint hybrid: 0.15–1.45 n log₂ n on all natural inputs, ≤ 3.66 n log₂ n on adversarial inputs, depth ≤ log₂ n |

## How to run (Python 3.13, matplotlib; numpy only for the Q4 verification)

```
cd Q1_MaxMin_Binary_Search/Implementation_Code
py q1_maxmin_binsearch.py      # demonstration with recursion traces
py q1_experiments.py           # experiments -> results/*.csv
py q1_tests.py                 # PASS/FAIL lines + RESULT
py q1_graphs.py                # graphs and decomposition diagrams -> results/*.png
```

The other questions follow the same pattern (`qN_<algorithm>.py`, `qN_experiments.py`, `qN_tests.py`,
`qN_graphs.py`; Q6 has `q6_median_of_medians.py` and `q6_meet_in_the_middle.py`; Q7's experiment program imports
Q2's original Quick Sort and both student prototypes so that all variants run on identical datasets). Every random
generator is seeded (42), so all operation counts are exactly reproducible; times vary with machine load.

**Tests:** Q1 17/17, Q2 14/14, Q3 15/15, Q4 13/13, Q5 19/19, Q6 27/27, Q7 20/20 — **125/125 passed**.

## Contributions

Both students took part in every question. The per-question split (Student A / Student B / shared) is in the
*Contribution* sub-section of every answer in the report and in `Final_Report/Student_Contribution_Record.docx`; it is
a proposed record that both students must confirm. In Q7 each student first produced an independent design
(`Student_A_Initial_Design/`, `Student_B_Initial_Design/`) before the joint final design (`Joint_Final_Design/`).
