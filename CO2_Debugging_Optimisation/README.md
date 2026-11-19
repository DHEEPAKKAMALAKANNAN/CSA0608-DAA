# CO2 – Debugging and Optimisation Task: SentinelOps SOC Alert-Triage Module

**Student:** V. Vasudevan · **Reg. No.:** 192425324 · **Course:** CSA06 – Design and Analysis of Algorithms (CO2: brute-force
techniques – sorting, sequential search, brute-force string matching, closest pair) · SIMATS Engineering · 19 November 2026

## Assumed question / scope (please read first)

- **The faulty program was reconstructed.** The faculty-issued faulty program and the task paper were not available, so
  `Source_Code/original_alert_triage.py` is a reconstruction: a realistic SOC alert-triage module, as a teammate might
  have written it, seeded with **14 plausible defects** (3–4 per function) in the four required brute-force functions
  `sort_alerts` (bubble sort), `find_alert` (sequential search), `match_signature` (brute-force string matching) and
  `closest_alert_pair` (brute-force closest pair). If the official program differs, the method, harness and report
  structure carry over unchanged.
- **The five-part breakdown is assumed** from the submission instructions: Part A Problem Identification (20 %),
  Part B Pseudocode (prepared before implementation), Part C Systematic Debugging (25 %), Part D Optimisation and
  Implementation (20 %), Part E Complexity Analysis and Experimental Comparison (20 %); Code Quality (15 %) is assessed
  throughout and summarised in its own section.
- **The batch-size range was blank in the brief** ("at least three batch sizes between [ … ]"). I used **five** batch
  sizes: **100, 500, 1,000, 2,000 and 5,000 alerts**.
- The corrected program is the original with **minimal line-level fixes** (each marked `# FIX Dn`), not a rewrite;
  `debug_session.py` proves this by replaying the 14 patches on the original text and checking the result is identical to
  `corrected_alert_triage.py`.

## Folder structure

```
CO2_Debugging_Optimisation/
├── Pseudocode/            8 files: corrected + optimised pseudocode for each of the four functions
├── Source_Code/
│   ├── original_alert_triage.py    the given (faulty) program - reconstructed, 14 seeded defects
│   ├── corrected_alert_triage.py   original + 14 line-level fixes (# FIX D1 ... # FIX D14)
│   ├── optimised_alert_triage.py   merge sort, sentinel search + hash index, Horspool (+KMP), divide & conquer (+sweep)
│   ├── test_harness.py             18 defect tests + 13 general tests (+6 for the optimised module), PASS/FAIL per test
│   ├── debug_session.py            reproduce -> isolate (sys.settrace) -> fix one defect at a time -> re-test -> verify
│   ├── experiments.py              operation counts + timings for n = 100 ... 5,000, CSV + graphs
│   ├── diagrams.py                 flowcharts of the 4 corrected + 4 optimised functions and the debugging process
│   └── alert_data.py               seeded SOC alert datasets (also writes them as CSV)
├── Report/
│   ├── CO2_Debugging_Optimisation_Report.docx / .pdf
│   ├── screenshots/        code_*.png (source code), out_*.png and experiments_output_*.png (real execution output)
│   ├── diagrams/           flow_*.png flowcharts (Part B) and flow_debugging_process.png (Part C)
│   ├── graphs/             fig_sort, fig_search, fig_matching, fig_closest_pair, fig_speedup (.png + plotted data .csv)
│   └── tables/             defect_tests.csv, diff_original_vs_corrected.csv, comparison_summary.csv
├── Supporting_Files/
│   ├── test_datasets/      alerts_random_<n>.csv, alerts_nearly_sorted_<n>.csv, alerts_same_x_1000.csv
│   ├── execution_logs/     captured output of every program run + original_vs_corrected.diff
│   └── experimental_results/  sort, search, matching (+ worst case) and closest-pair results (CSV)
└── README.md
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
| D1 | sort_alerts | 59 | `ordered = alerts` | side effect – sorts the caller's list |
| D2 | sort_alerts | 63 | `range(n - i - 2)` | off-by-one – last pair never compared |
| D3 | _comes_before | 54 | `a.timestamp > b.timestamp` | wrong tie-break – newest first |
| D4 | sort_alerts | 61 | `swapped = False` before the outer loop | initialisation – early exit lost |
| D5 | find_alert | 77 | `range(1, len(alerts))` | off-by-one – index 0 skipped |
| D6 | find_alert | 79 | `alert_id is alert_id` | identity instead of equality |
| D7 | find_alert | 81–82 | `else: return -1` inside the loop | premature exit; `None` for empty list |
| D8 | match_signature | 93 | `range(n - m)` | off-by-one – last alignment skipped |
| D9 | match_signature | 98 | no `break` after a mismatch | efficiency – m comparisons per alignment |
| D10 | match_signature | 90 | `if m > n:` | empty signature matches everywhere |
| D11 | closest_alert_pair | 108 | `best = 0.0` | initialisation – never updated |
| D12 | closest_alert_pair | 110 | `for j in range(n)` | self-pairs, every pair twice (n² distances) |
| D13 | closest_alert_pair | 113 | `alerts[i].y - alerts[i].y` | index typo – y ignored |
| D14 | closest_alert_pair | 118 | `best_j = j` outside the `if` | indices not updated together |

## Key results (n = 5,000 alerts; full tables in the report and `Report/tables/comparison_summary.csv`)

| Function | Corrected (brute force) | Optimised | Operation reduction | Time speed-up |
|---|---|---|---|---|
| sort_alerts | 12,461,989 comparisons (bubble) | 51,674 (merge sort) | 241× | 265× |
| find_alert × 1,000 look-ups | 2,989,277 comparisons | 6,000 index operations | 498× | 519× |
| match_signature × 5 signatures | 1,506,694 char comparisons | 171,309 (Horspool) | 8.8× | 18.5× |
| closest_alert_pair | **12,497,500 distance computations** = n(n−1)/2 | **6,393** (divide & conquer) | 1,955× | 288× |

Every experiment checks that the corrected and optimised versions return identical results (all `yes`).
