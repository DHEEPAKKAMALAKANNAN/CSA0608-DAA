# CSA06 – Assignment 4A (CO4), Part I: Algorithmic Design through Pseudocode

**Student:** V. Vasudevan · **Reg. No.:** 192425324 · CSA06 – Design and Analysis of Algorithms · SIMATS Engineering · 19 November 2026

**Course outcome:** CO4 – Solve optimization problems using Dynamic Programming and Greedy strategies ·
Individual · One Week · 50 marks.

This assignment answers the official Assignment 4A question paper. The answers themselves are **precise,
language-independent pseudocode** (SIMATS handbook style), **flowcharts**, diagrams and **manual desk-check traces**
– see the report. As required by the department's submission instructions, every pseudocode was afterwards
implemented as a small Python program that prints the same trace; these programs only **verify** the manual
desk-checks (they are not offered as pseudocode).

| Task | Title (official paper) | Answer in short | Marks |
|---|---|---|---|
| 1 | Algorithm Design Review – Diagnose and Repair Poor Pseudocode (fractional loading) | 8 deficiencies; repaired `LoadVehicle` (greedy by value/weight, fractional last package) | 6 |
| 2 | From Business Requirement to Greedy Pseudocode – Job Sequencing with Deadlines | max profit first, latest free slot: C, A, D = **180**; B → 90 displaces C → 210 | 8 |
| 3 | From Recurrence to Executable Logic – 0/1 Knapsack DP | DP[i][w] table, reconstruction: **Q + R = 45** (W = 7) | 9 |
| 4 | Pseudocode Forensics – WordBreak | missing `DP[j] = TRUE` in the inner IF; failing input "catsdog"; one-line repair | 7 |
| 5 | Same Graph, Different Reasoning – Dijkstra, Bellman-Ford, Floyd | from A: B 4, C 6, D 7, E 10; negative-edge analysis; D(k)[i][j] | 7 |
| 6 | Design Challenge – Energy-Aware Job Scheduling (weighted interval scheduling) | DP over jobs sorted by finish time: **J2, J5, J7, J8 = 200**; adversarial set → 150 | 13 |

## Folder structure

```
CO4_Assignment_4A/
├── Source_Code/
│   ├── Task_1/   load_vehicle.py, test_load_vehicle.py, packages.csv
│   ├── Task_2/   job_sequencing.py, test_job_sequencing.py, jobs.csv
│   ├── Task_3/   knapsack_dp.py, test_knapsack_dp.py, items.csv
│   ├── Task_4/   word_break.py, test_word_break.py, word_break_cases.csv
│   ├── Task_5/   single_source.py (Dijkstra + Bellman-Ford), floyd_all_pairs.py, graph_common.py,
│   │             test_shortest_paths.py, graph.csv
│   └── Task_6/   energy_scheduling.py, compare_strategies.py, test_energy_scheduling.py,
│                 jobs.csv, adversarial_jobs.csv
├── Report/
│   ├── CO4_Assignment_4A_Report.pdf      (the deliverable)
│   ├── CO4_Assignment_4A_Report.docx
│   ├── Diagrams/      flowcharts (fc_*.png) and diagrams (dg_*.png)
│   └── Screenshots/   execution-output screenshots (also embedded in the report)
└── README.md
```

## How to run

Python 3.13 (`py -3`), standard library only (matplotlib only for the diagrams). All programs are deterministic
(seed 42) and finish in a few seconds.

```
cd Source_Code/Task_6
py -3 energy_scheduling.py                       # desk-check on the official 8 jobs (+ brute force over 256 subsets)
py -3 energy_scheduling.py adversarial_jobs.csv  # Stage 6 adversarial set
py -3 compare_strategies.py                      # Stage 2: greedy rules vs DP, counter-examples
py -3 test_energy_scheduling.py                  # PASS/FAIL lines + RESULT
```

The other task folders work the same way (`py -3 <program>.py`, then `py -3 test_<program>.py`).

## Verification

| Task | Reference used by the test program | Result |
|---|---|---|
| 1 | exhaustive optimum over all n! loading orders (300 random instances) + boundary cases | 9/9 PASS |
| 2 | exhaustive search over all 2ⁿ job subsets (given, modified and 400 random instances) | 9/9 PASS |
| 3 | brute force over all subsets (given and 400 random instances); reconstructed set feasible and optimal | 8/8 PASS |
| 4 | memoised recursive segmentation on 2000 random texts (faulty version wrong on 480 of them) | 10/10 PASS |
| 5 | Dijkstra = Bellman-Ford = Floyd = simple-path brute force (400 random graphs, incl. negative-edge DAGs) | 11/11 PASS |
| 6 | brute force over all 2ⁿ subsets (official, adversarial and 500 random instances) | 11/11 PASS |

All 58 tests pass. In every task the manual trace in the report was done first; the program output reproduces it
exactly.
