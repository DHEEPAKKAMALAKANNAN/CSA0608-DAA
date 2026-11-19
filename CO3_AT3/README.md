# CO3 – Assessment Tool 3: Divide-and-Conquer Case Study – SwiftLogix

**V. Vasudevan** · Reg. No. **192425324** · CSA06 – Design and Analysis of Algorithms · SIMATS Engineering · 19 November 2026

Coverage: **CO3 – Merge Sort, Quick Sort, Binary Search and Strassen's Matrix Multiplication**, applied to the four
back-end modules of one platform: *SwiftLogix – National Logistics and Delivery Analytics Platform*.

## Assumed question / scope

The original case-study paper (scenario, wording of the six parts, "given sample datasets", production workloads)
was not available, so it was **reconstructed**. Adapt the items below if the official paper differs.

- **Scenario:** SwiftLogix runs four back-end modules – M1 nightly *stable* sort of shipment events by
  (delivery date, event time) with **Merge Sort**; M2 in-memory ranking of order-priority scores (0–100, duplicate-heavy)
  for the dispatch queue with **Quick Sort**; M3 tracking-ID lookup in the sorted shipment index with **Binary Search**;
  M4 route-demand × cost matrix product for network forecasting with **Strassen's algorithm**.
- **Six parts (assumed marks, total 70):** Part 1 Case Analysis (10) · Part 2 Algorithm Design & Pseudocode (10) ·
  Part 3 Implementation & Execution Traces (15) · Part 4 Recurrences, Complexity & Production Workloads (15) ·
  Part 5 Comparative Performance, Limitations & Improvements (10) · Part 6 Final Design (10). Duration 1 week (assumed).
- **Given sample datasets (invented):** 12 shipment events with two pairs of equal keys; 12 priority scores with
  duplicates; a sorted index of 16 tracking IDs with 8 queries (5 present, 3 absent); two 4 × 4 route matrices
  (`Supporting_Files/datasets/`).
- **Production workloads (assumed):** 5,000,000 events/night (64-byte records, 64 time-ordered hub feeds);
  2,000,000 orders per dispatch cycle (scores 0–100, 1-second budget); 20,000,000 lookups/day on 10,000,000 IDs
  (16-byte entries, peak 2,000/s); 1,024 × 1,024 matrices (8-byte reals, 96 forecasts/day); server speed
  10⁸ basic operations/s; 1 MB = 10⁶ bytes.
- To use other numbers, change the sample files and the constants at the top of
  `Supporting_Files/production_workload.py`, then rerun the programs – every table and graph is regenerated.

## Folder structure

```
CO3_AT3/
├── Module_1_Merge_Sort/
│   ├── Pseudocode/merge_sort_pseudocode.txt          (written before implementation; baseline + Part 5 variants)
│   ├── Source_Code/merge_sort.py                      (algorithms + counters + trace demo on the sample)
│   │               merge_sort_experiments.py          (experiments, CSVs, graphs)
│   └── Report/Module_1_Merge_Sort_Report.docx/.pdf, screenshots/, traces/, graphs/ (+ CSV copies)
├── Module_2_Quick_Sort/                               (same layout: quick_sort.py, quick_sort_experiments.py)
├── Module_3_Binary_Search/                            (binary_search.py, binary_search_experiments.py)
├── Module_4_Strassen_Matrix_Multiplication/           (strassen.py, strassen_experiments.py)
├── Final_Design_and_Analysis/
│   ├── CO3_AT3_Case_Study_Report.docx/.pdf        (complete case study: all six parts, all four modules)
│   ├── Final_Algorithmic_Design.md                    (the final design at a glance)
│   ├── graphs/  final_production_time.png, final_memory.png, final_theory_vs_experiment.png, production_workload.csv
│   ├── diagrams/  flowcharts of the 4 modules + recursion/partition trees, search intervals, Strassen blocks
│   └── screenshots/  production calculator, dataset generator and full test-run outputs
├── Supporting_Files/
│   ├── datasets/            given samples (m1…m4) + generated/ (5,000 events, 5,000 scores, 20,000-ID index,
│   │                        2,000 queries, 64 × 64 matrices)
│   ├── test_cases/          JSON edge cases with expected outputs from sorted() / bisect / numpy
│   ├── results/             all experimental results (CSV)
│   ├── generate_datasets.py, run_all_tests.py, production_workload.py, diagrams.py (flowcharts/diagrams)
└── README.md
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
experiment scripts take 1–2 minutes each; `production_workload.py` needs the experiment CSVs;
`run_all_tests.py [--module N]` prints PASS/FAIL lines and **RESULT: 65/65 tests passed**. All runs are seeded
(seed 42) and deterministic in their operation counts; wall-clock times vary with machine load.

## Results at a glance

| Module | Part 2 design (production estimate) | Key finding (Part 5) | Final design (production estimate) |
|---|---|---|---|
| M1 Merge Sort | top-down stable merge sort: 106.6 M comparisons + 230 M moves → 3.37 s, 640 MB | 64 sorted hub feeds → natural merge sort needs 1.64× fewer comparisons, 2.3× less time | natural merge sort on (key, index) pairs: 0.95 s, 120 MB |
| M2 Quick Sort | Lomuto, last pivot: 5.56 h on a sorted queue, 198 s on duplicate scores | exactly n(n−1)/2 and depth n−1 on sorted input; n²/(2k) on duplicates; fixed median-of-3 defeated by 3-way partition | introsort-style 3-way hybrid: 0.20 s, 16 MB |
| M3 Binary Search | ≤ 24 comparisons/lookup → 4.8 s CPU/day, 160 MB | counts equal the exact decision-tree formulas; interpolation 4.3 probes but collapses on clustered IDs | guarded interpolation with binary-search guarantee, ≈ 416 k lookups/s/core |
| M4 Strassen | pure Strassen: 1.97 × 10⁹ operations → 19.7 s (naive 21.5 s) | op crossover n > 15 with a cutoff (pure only at n = 1,024); time-optimal n₀ = 64 in Python; minimal padding up to 6.35× cheaper | hybrid Strassen, tuned n₀: 1.10 × 10⁹ operations → 11.0 s, 65 MB |

## Reports

- `Final_Design_and_Analysis/CO3_AT3_Case_Study_Report.{md,docx,pdf}` – the complete case study (all six parts).
- `Module_N_…/Report/Module_N_…_Report.{md,docx,pdf}` – one report per module (same six-part rubric applied to that
  module), with its screenshots, traces and graphs.

All reports follow the department's sample report format (cover page with mark sheet, question boxes, "Ans:",
numbered tables and figures, appendices with source code, raw data and test results).
