# CO2 â€“ Debugging and Optimisation Task: SentinelOps SOC Alert-Triage Module

**Student:** K DHEEPAK Â· **Reg. No.:** 192411108 Â· **Course:** CSA06 â€“ Design and Analysis of Algorithms (CO2: brute-force
techniques â€“ sorting, sequential search, brute-force string matching, closest pair) Â· SIMATS Engineering Â· 19 November 2026

## Assumed question / scope (please read first)

- **The faulty program was reconstructed.** The faculty-issued faulty program and the task paper were not available, so
  `Source_Code/original_alert_triage.py` is a reconstruction: a realistic SOC alert-triage module, as a teammate might
  have written it, seeded with **14 plausible defects** (3â€“4 per function) in the four required brute-force functions
  `sort_alerts` (bubble sort), `find_alert` (sequential search), `match_signature` (brute-force string matching) and
  `closest_alert_pair` (brute-force closest pair). If the official program differs, the method, harness and report
  structure carry over unchanged.
- **The five-part breakdown is assumed** from the submission instructions: Part A Problem Identification (20 %),
  Part B Pseudocode (prepared before implementation), Part C Systematic Debugging (25 %), Part D Optimisation and
  Implementation (20 %), Part E Complexity Analysis and Experimental Comparison (20 %); Code Quality (15 %) is assessed
  throughout and summarised in its own section.
- **The batch-size range was blank in the brief** ("at least three batch sizes between [ â€¦ ]"). I used **five** batch
  sizes: **100, 500, 1,000, 2,000 and 5,000 alerts**.
- The corrected program is the original with **minimal line-level fixes** (each marked `# FIX Dn`), not a rewrite;
  `debug_session.py` proves this by replaying the 14 patches on the original text and checking the result is identical to
  `corrected_alert_triage.py`.

## Folder structure

```
CO2_Debugging_Optimisation/
â”œâ”€â”€ Pseudocode/            8 files: corrected + optimised pseudocode for each of the four functions
â”œâ”€â”€ Source_Code/
â”‚   â”œâ”€â”€ original_alert_triage.py    the given (faulty) program - reconstructed, 14 seeded defects
â”‚   â”œâ”€â”€ corrected_alert_triage.py   original + 14 line-level fixes (# FIX D1 ... # FIX D14)
â”‚   â”œâ”€â”€ optimised_alert_triage.py   merge sort, sentinel search + hash index, Horspool (+KMP), divide & conquer (+sweep)
â”‚   â”œâ”€â”€ test_harness.py             18 defect tests + 13 general tests (+6 for the optimised module), PASS/FAIL per test
â”‚   â”œâ”€â”€ debug_session.py            reproduce -> isolate (sys.settrace) -> fix one defect at a time -> re-test -> verify
â”‚   â”œâ”€â”€ experiments.py              operation counts + timings for n = 100 ... 5,000, CSV + graphs
â”‚   â”œâ”€â”€ diagrams.py                 flowcharts of the 4 corrected + 4 optimised functions and the debugging process
â”‚   â””â”€â”€ alert_data.py               seeded SOC alert datasets (also writes them as CSV)
â”œâ”€â”€ Report/
â”‚   â”œâ”€â”€ CO2_Debugging_Optimisation_Report.docx / .pdf
â”‚   â”œâ”€â”€ screenshots/        code_*.png (source code), out_*.png and experiments_output_*.png (real execution output)
â”‚   â”œâ”€â”€ diagrams/           flow_*.png flowcharts (Part B) and flow_debugging_process.png (Part C)
â”‚   â”œâ”€â”€ graphs/             fig_sort, fig_search, fig_matching, fig_closest_pair, fig_speedup (.png + plotted data .csv)
â”‚   â””â”€â”€ tables/             defect_tests.csv, diff_original_vs_corrected.csv, comparison_summary.csv
â”œâ”€â”€ Supporting_Files/
â”‚   â”œâ”€â”€ test_datasets/      alerts_random_<n>.csv, alerts_nearly_sorted_<n>.csv, alerts_same_x_1000.csv
â”‚   â”œâ”€â”€ execution_logs/     captured output of every program run + original_vs_corrected.diff
â”‚   â””â”€â”€ experimental_results/  sort, search, matching (+ worst case) and closest-pair results (CSV)
â””â”€â”€ README.md
```

## How to run (Python 3.13, `py -3`; only matplotlib is needed beyond the standard library)

```
cd Source_Code
py -3 original_alert_triage.py      # faulty demo shift: wrong queue, failed look-ups, false matches, distance 0
py -3 corrected_alert_triage.py     # corrected demo output
py -3 optimised_alert_triage.py     # same results with the optimised algorithms
py -3 test_harness.py               # original 6/31 (defects reproduced), corrected 31/31, optimised 37/37
py -3 debug_session.py              # systematic debugging replay, RESULT: 31/31 tests passed
py -3 experiments.py                # ~70 s; writes CSV files and graphs (--graphs-only redraws the graphs)
py -3 alert_data.py                 # rewrites the CSV test datasets
```

## The 14 defects (line numbers refer to `original_alert_triage.py`)

| ID | Function | Line(s) | Faulty code | Type |
|---|---|---|---|---|
| D1 | sort_alerts | 59 | `ordered = alerts` | side effect â€“ sorts the caller's list |
| D2 | sort_alerts | 63 | `range(n - i - 2)` | off-by-one â€“ last pair never compared |
| D3 | _comes_before | 54 | `a.timestamp > b.timestamp` | wrong tie-break â€“ newest first |
| D4 | sort_alerts | 61 | `swapped = False` before the outer loop | initialisation â€“ early exit lost |
| D5 | find_alert | 77 | `range(1, len(alerts))` | off-by-one â€“ index 0 skipped |
| D6 | find_alert | 79 | `alert_id is alert_id` | identity instead of equality |
| D7 | find_alert | 81â€“82 | `else: return -1` inside the loop | premature exit; `None` for empty list |
| D8 | match_signature | 93 | `range(n - m)` | off-by-one â€“ last alignment skipped |
| D9 | match_signature | 98 | no `break` after a mismatch | efficiency â€“ m comparisons per alignment |
| D10 | match_signature | 90 | `if m > n:` | empty signature matches everywhere |
| D11 | closest_alert_pair | 108 | `best = 0.0` | initialisation â€“ never updated |
| D12 | closest_alert_pair | 110 | `for j in range(n)` | self-pairs, every pair twice (nÂ² distances) |
| D13 | closest_alert_pair | 113 | `alerts[i].y - alerts[i].y` | index typo â€“ y ignored |
| D14 | closest_alert_pair | 118 | `best_j = j` outside the `if` | indices not updated together |

## Key results (n = 5,000 alerts; full tables in the report and `Report/tables/comparison_summary.csv`)

| Function | Corrected (brute force) | Optimised | Operation reduction | Time speed-up |
|---|---|---|---|---|
| sort_alerts | 12,461,989 comparisons (bubble) | 51,674 (merge sort) | 241Ã— | 265Ã— |
| find_alert Ã— 1,000 look-ups | 2,989,277 comparisons | 6,000 index operations | 498Ã— | 519Ã— |
| match_signature Ã— 5 signatures | 1,506,694 char comparisons | 171,309 (Horspool) | 8.8Ã— | 18.5Ã— |
| closest_alert_pair | **12,497,500 distance computations** = n(nâˆ’1)/2 | **6,393** (divide & conquer) | 1,955Ã— | 288Ã— |

Every experiment checks that the corrected and optimised versions return identical results (all `yes`).

