# CO3 â€“ Assessment Tool 3: Divide-and-Conquer Case Study â€“ SwiftLogix

**K DHEEPAK** Â· Reg. No. **192411108** Â· CSA06 â€“ Design and Analysis of Algorithms Â· SIMATS Engineering Â· 19 November 2026

Coverage: **CO3 â€“ Merge Sort, Quick Sort, Binary Search and Strassen's Matrix Multiplication**, applied to the four
back-end modules of one platform: *SwiftLogix â€“ National Logistics and Delivery Analytics Platform*.

## Assumed question / scope

The original case-study paper (scenario, wording of the six parts, "given sample datasets", production workloads)
was not available, so it was **reconstructed**. Adapt the items below if the official paper differs.

- **Scenario:** SwiftLogix runs four back-end modules â€“ M1 nightly *stable* sort of shipment events by
  (delivery date, event time) with **Merge Sort**; M2 in-memory ranking of order-priority scores (0â€“100, duplicate-heavy)
  for the dispatch queue with **Quick Sort**; M3 tracking-ID lookup in the sorted shipment index with **Binary Search**;
  M4 route-demand Ã— cost matrix product for network forecasting with **Strassen's algorithm**.
- **Six parts (assumed marks, total 70):** Part 1 Case Analysis (10) Â· Part 2 Algorithm Design & Pseudocode (10) Â·
  Part 3 Implementation & Execution Traces (15) Â· Part 4 Recurrences, Complexity & Production Workloads (15) Â·
  Part 5 Comparative Performance, Limitations & Improvements (10) Â· Part 6 Final Design (10). Duration 1 week (assumed).
- **Given sample datasets (invented):** 12 shipment events with two pairs of equal keys; 12 priority scores with
  duplicates; a sorted index of 16 tracking IDs with 8 queries (5 present, 3 absent); two 4 Ã— 4 route matrices
  (`Supporting_Files/datasets/`).
- **Production workloads (assumed):** 5,000,000 events/night (64-byte records, 64 time-ordered hub feeds);
  2,000,000 orders per dispatch cycle (scores 0â€“100, 1-second budget); 20,000,000 lookups/day on 10,000,000 IDs
  (16-byte entries, peak 2,000/s); 1,024 Ã— 1,024 matrices (8-byte reals, 96 forecasts/day); server speed
  10â¸ basic operations/s; 1 MB = 10â¶ bytes.
- To use other numbers, change the sample files and the constants at the top of
  `Supporting_Files/production_workload.py`, then rerun the programs â€“ every table and graph is regenerated.

## Folder structure

```
CO3_AT3/
â”œâ”€â”€ Module_1_Merge_Sort/
â”‚   â”œâ”€â”€ Pseudocode/merge_sort_pseudocode.txt          (written before implementation; baseline + Part 5 variants)
â”‚   â”œâ”€â”€ Source_Code/merge_sort.py                      (algorithms + counters + trace demo on the sample)
â”‚   â”‚               merge_sort_experiments.py          (experiments, CSVs, graphs)
â”‚   â””â”€â”€ Report/Module_1_Merge_Sort_Report.docx/.pdf, screenshots/, traces/, graphs/ (+ CSV copies)
â”œâ”€â”€ Module_2_Quick_Sort/                               (same layout: quick_sort.py, quick_sort_experiments.py)
â”œâ”€â”€ Module_3_Binary_Search/                            (binary_search.py, binary_search_experiments.py)
â”œâ”€â”€ Module_4_Strassen_Matrix_Multiplication/           (strassen.py, strassen_experiments.py)
â”œâ”€â”€ Final_Design_and_Analysis/
â”‚   â”œâ”€â”€ CO3_AT3_Case_Study_Report.docx/.pdf        (complete case study: all six parts, all four modules)
â”‚   â”œâ”€â”€ Final_Algorithmic_Design.md                    (the final design at a glance)
â”‚   â”œâ”€â”€ graphs/  final_production_time.png, final_memory.png, final_theory_vs_experiment.png, production_workload.csv
â”‚   â”œâ”€â”€ diagrams/  flowcharts of the 4 modules + recursion/partition trees, search intervals, Strassen blocks
â”‚   â””â”€â”€ screenshots/  production calculator, dataset generator and full test-run outputs
â”œâ”€â”€ Supporting_Files/
â”‚   â”œâ”€â”€ datasets/            given samples (m1â€¦m4) + generated/ (5,000 events, 5,000 scores, 20,000-ID index,
â”‚   â”‚                        2,000 queries, 64 Ã— 64 matrices)
â”‚   â”œâ”€â”€ test_cases/          JSON edge cases with expected outputs from sorted() / bisect / numpy
â”‚   â”œâ”€â”€ results/             all experimental results (CSV)
â”‚   â”œâ”€â”€ generate_datasets.py, run_all_tests.py, production_workload.py, diagrams.py (flowcharts/diagrams)
â””â”€â”€ README.md
```

## How to run (Python 3.13, `py -3`; matplotlib for graphs, numpy only for verification)

```
cd Module_1_Merge_Sort/Source_Code      &&  py -3 merge_sort.py             &&  py -3 merge_sort_experiments.py
cd Module_2_Quick_Sort/Source_Code      &&  py -3 quick_sort.py             &&  py -3 quick_sort_experiments.py
cd Module_3_Binary_Search/Source_Code   &&  py -3 binary_search.py          &&  py -3 binary_search_experiments.py
cd Module_4_Strassen_Matrix_Multiplication/Source_Code  &&  py -3 strassen.py  &&  py -3 strassen_experiments.py
cd Supporting_Files  &&  py -3 generate_datasets.py  &&  py -3 production_workload.py  &&  py -3 run_all_tests.py
```

The demo programs print the divide / conquer / combine trace on the given sample and verify the result; the
experiment scripts take 1â€“2 minutes each; `production_workload.py` needs the experiment CSVs;
`run_all_tests.py [--module N]` prints PASS/FAIL lines and **RESULT: 65/65 tests passed**. All runs are seeded
(seed 42) and deterministic in their operation counts; wall-clock times vary with machine load.

## Results at a glance

| Module | Part 2 design (production estimate) | Key finding (Part 5) | Final design (production estimate) |
|---|---|---|---|
| M1 Merge Sort | top-down stable merge sort: 106.6 M comparisons + 230 M moves â†’ 3.37 s, 640 MB | 64 sorted hub feeds â†’ natural merge sort needs 1.64Ã— fewer comparisons, 2.3Ã— less time | natural merge sort on (key, index) pairs: 0.95 s, 120 MB |
| M2 Quick Sort | Lomuto, last pivot: 5.56 h on a sorted queue, 198 s on duplicate scores | exactly n(nâˆ’1)/2 and depth nâˆ’1 on sorted input; nÂ²/(2k) on duplicates; fixed median-of-3 defeated by 3-way partition | introsort-style 3-way hybrid: 0.20 s, 16 MB |
| M3 Binary Search | â‰¤ 24 comparisons/lookup â†’ 4.8 s CPU/day, 160 MB | counts equal the exact decision-tree formulas; interpolation 4.3 probes but collapses on clustered IDs | guarded interpolation with binary-search guarantee, â‰ˆ 416 k lookups/s/core |
| M4 Strassen | pure Strassen: 1.97 Ã— 10â¹ operations â†’ 19.7 s (naive 21.5 s) | op crossover n > 15 with a cutoff (pure only at n = 1,024); time-optimal nâ‚€ = 64 in Python; minimal padding up to 6.35Ã— cheaper | hybrid Strassen, tuned nâ‚€: 1.10 Ã— 10â¹ operations â†’ 11.0 s, 65 MB |

## Reports

- `Final_Design_and_Analysis/CO3_AT3_Case_Study_Report.{md,docx,pdf}` â€“ the complete case study (all six parts).
- `Module_N_â€¦/Report/Module_N_â€¦_Report.{md,docx,pdf}` â€“ one report per module (same six-part rubric applied to that
  module), with its screenshots, traces and graphs.

All reports follow the department's sample report format (cover page with mark sheet, question boxes, "Ans:",
numbered tables and figures, appendices with source code, raw data and test results).

