# CSA06 â€“ Design and Analysis of Algorithms Â· Assignment 2 (CO2)

**Brute-Force and Exhaustive-Search Engineering** â€” Selection, Bubble and Insertion Sort, Sequential Search,
Brute-Force String Matching, Closest Pair, Convex Hull and Exhaustive Search.

Student: **K DHEEPAK** Â· Reg. No. **192411108** Â· SIMATS Engineering Â· 19 November 2026

The final report is [`Final_Report/CO2_Assignment_Report.docx`](Final_Report/CO2_Assignment_Report.docx)
(also as [PDF](Final_Report/CO2_Assignment_Report.pdf)).

## How the work is organised

Every question follows the cycle **Predict â†’ Design â†’ Implement â†’ Measure â†’ Analyse â†’ Evaluate** (Q7 adds
**Diagnose â†’ Redesign â†’ Validate**):

* `Pseudocode/` â€“ the design notes, predictions and pseudocode, written **before** the code, plus the
  **flowchart** of every algorithm (`q*_flowchart_*.png`, standard symbols) and explanatory diagrams (Q3 alignment
  diagram, Q4 pair plot / comparison triangle, Q5 orientation test, Q6 subset tree, Q7 sweep window),;
* `Implementation_Code/` â€“ the programs; `results/` holds the raw experimental data (CSV) and the datasets used (`results/datasets/`);
* `Output_Screenshots/` â€“ screenshots of the real program runs (`*_output*.png`), graphs and visualisations
  (the source-code screenshots are inside the report).

Operation counts (comparisons, swaps, shifts, character comparisons, distance calculations, orientation tests,
candidate subsets) are the **primary evidence**; wall-clock times are secondary (other programs were running on the
same PC, so times vary by about Â±30 % between runs).

```
CO2_Assignment/
â”œâ”€â”€ Q1_Sorting_Algorithms/              Pseudocode/  Implementation_Code/ (+ results/)  Output_Screenshots/
â”œâ”€â”€ Q2_Sequential_Search/               â€¦
â”œâ”€â”€ Q3_Brute_Force_String_Matching/     â€¦
â”œâ”€â”€ Q4_Brute_Force_Closest_Pair/        â€¦
â”œâ”€â”€ Q5_Brute_Force_Convex_Hull/         â€¦
â”œâ”€â”€ Q6_Exhaustive_Search/               â€¦
â”œâ”€â”€ Q7_Day4_Design_Challenge/           â€¦
â”œâ”€â”€ Final_Report/                       CO2_Assignment_Report.docx / .pdf
â””â”€â”€ README.md
```

## Questions, programs and evidence

| Q | Topic (application context) | Programs (`Implementation_Code/`) | Main evidence |
|---|---|---|---|
| Q1 | Selection / Bubble / Insertion Sort (e-commerce order dispatch) | `sorting_algorithms.py` (algorithms, tests, demo) Â· `q1_experiments.py` (6 datasets Ã— 3 sizes) Â· `q1_scenario_95.py` (95 %-sorted design decision) | `results/q1_results.csv`, `q1_scenario_95.csv`, `q1_counts_by_dataset_n5000.png`, `q1_comparisons_growth.png`, `q1_scenario_95.png` |
| Q2 | Sequential Search (aircraft-maintenance tool tracking) | `sequential_search.py` (algorithm, list store, hash-index store, tests, "Who has T-184?" demo) Â· `q2_experiments.py` (positions, sizes 50 â†’ 1 000 000, timing, boundary) Â· `q2_facility_simulation.py` (1 hangar vs 20 facilities) | `results/q2_positions.csv`, `q2_average.csv`, `q2_boundary.csv`, `q2_facility_simulation.csv`, `q2_comparisons.png`, `q2_operating_boundary.png` |
| Q3 | Brute-force string matching (SOC log screening) | `brute_force_string_match.py` (algorithm, tests, 3 designed conditions with printed predictions) Â· `q3_experiments.py` (size and pattern-length sweeps) | `results/q3_conditions.csv`, `q3_size_sweep.csv`, `q3_pattern_sweep.csv`, `q3_conditions_bar.png`, `q3_growth.png` |
| Q4 | Brute-force closest pair (drone collision risk) | `closest_pair_bruteforce.py` (algorithm, tests, 6-drone demo, fleet generator) Â· `q4_experiments.py` (n = 100 â†’ 10 000, fit, 100 ms boundary) | `results/q4_growth.csv`, `q4_fit.csv`, `q4_growth.png` |
| Q5 | Brute-force convex hull (wildlife-reserve boundary) | `convex_hull_bruteforce.py` (decision rule, tests, configurations A and B, hull plots) Â· `q5_growth_experiment.py` (n = 10 â†’ 1 280) | `results/q5_configs.csv`, `q5_growth.csv`, `q5_hull_configs.png`, `q5_growth.png` |
| Q6 | Exhaustive search, 0/1 knapsack (humanitarian airlift) | `knapsack_exhaustive.py` (bitmask enumeration, DP cross-check, full 32-row table) Â· `q6_growth_experiment.py` (n = 10 â†’ 22, 1 s deployment boundary) | `results/q6_growth.csv`, `q6_deployment.csv`, `q6_growth.png` |
| Q7 | Day-4 Design Challenge: diagnose, redesign and validate Q4 | `closest_pair_redesign.py` (sort + sweep redesign, tests vs the Q4 original) Â· `q7_diagnosis.py` (part A) Â· `q7_validation.py` (part E, same datasets as Q4) | `results/q7_diagnosis.csv`, `q7_validation.csv`, `q7_scaling.csv`, `q7_diagnosis.png`, `q7_original_vs_redesign.png`, `q7_layouts_n2000.png` |

## Running the programs

Requirements: Python 3.10+ (developed with 3.13) and matplotlib (graphs only); all algorithm cores are
hand-written pure Python with explicit operation counters. All random data is seeded, so every count is
reproducible exactly.

```
cd Q1_Sorting_Algorithms/Implementation_Code
py -3 sorting_algorithms.py          # PASS/FAIL tests + demo   (each "main" program prints RESULT: k/k tests passed)
py -3 q1_experiments.py              # writes results/*.csv and ../Output_Screenshots/*.png
```

Run the scripts of each question from its `Implementation_Code/` folder in the order listed in the table.
Dependencies between questions: `q2_facility_simulation.py` reads `results/q2_timing.csv` written by
`q2_experiments.py`; the Q7 scripts import the unchanged Q4 brute force and read the Q4 datasets and fit
(`Q4_Brute_Force_Closest_Pair/Implementation_Code/results/`), so run Q4 before Q7. Typical run times on the test PC:
each test/demo program < 2 s, each experiment script 5â€“60 s.

## Correctness verification (summary)

All seven algorithm programs print `PASS â€¦` lines and `RESULT: k/k tests passed`; together **77/77 tests pass**
(see the output screenshots and Appendix D of the report).

| Q | Reference used |
|---|---|
| Q1 | Python `sorted()`; every counter equals an exact prediction from the input's inversion profile |
| Q2 | independent dictionary index; list store and hash-index store agree on 3 000 mixed events and on every simulated lookup |
| Q3 | `str.startswith` at every shift; hand-counted comparisons; 200 random binary texts |
| Q4 | hand-checked fleets; `math.dist` over `itertools.combinations` on 150 random fleets |
| Q5 | hand results; Andrew's monotone chain used only as a test oracle (150 collinear/duplicate-heavy sets) |
| Q6 | 0/1-knapsack dynamic programming; `itertools.combinations` feasibility counts |
| Q7 | the original Q4 brute force on identical fleets (uniform, clustered, corridor, cross, tie-heavy grids) |

