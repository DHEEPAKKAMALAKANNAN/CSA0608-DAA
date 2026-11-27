# CO1 â€“ Assessment Tool 1: Scalability Audit of an E-Commerce Platform (ShopSphere)

**Course:** CSA06 â€“ Design and Analysis of Algorithms Â· **Student:** K DHEEPAK (Reg. No. 192411108) Â· **Mode:** Individual

**CO assessed:** determine algorithm efficiency using asymptotic notations and mathematical techniques, including the Master Theorem and the substitution method.

ShopSphere's catalogue grows from n = 100,000 to n = 1,000,000 products. I audited five back-end modules (M1 duplicate detector, M2 rate limiter, M3 search S1/S2, M4 recommendation engine, M5 sales analytics, plus the nightly report generator). For each one I derived the exact basic-operation count and the asymptotic class, checked the result by counting operations in hand-written Python implementations, and estimated the running time at 10â¸ operations per second against a 10-minute nightly window.

## Folder structure

```
CO1_AT1/
â”œâ”€â”€ README.md
â””â”€â”€ Question_1/
    â”œâ”€â”€ Source_Code/         programs (Python, standard library + matplotlib)
    â”œâ”€â”€ Report/              CO1_AT1_Report.docx / .pdf
    â”‚   â”œâ”€â”€ screenshots/     source-code and execution-output screenshots
    â”‚   â””â”€â”€ graphs/          fig1 â€¦ fig7 (PNG, 150 dpi)
    â””â”€â”€ Supporting_Files/    raw CSV data behind every table and graph
```

## Programs (`Question_1/Source_Code`)

| Program | Part | What it does |
|---|---|---|
| `audit_common.py` | all | constants of the paper (10â¸ ops/s, 600 s window, n = 10âµ and 10â¶) and table/CSV helpers |
| `m1_duplicate_detector.py` | (a), (b), (g) | nested-loop detector with comparison counters; checks n(n âˆ’ 1)/2; finds planted duplicates; hash-set and sort-and-scan redesigns |
| `m2_rate_limiter.py` | (b) | counts Audit calls; trace for n = 1,024 (1,023 audits); closed form 2^âŒˆlogâ‚‚ nâŒ‰ âˆ’ 1 for many n; compares with n logâ‚‚ n |
| `m3_product_search.py` | (c), (e) | S1 sequential and S2 binary search (iterative + recursive); backward-substitution check; best/average/worst counts; S1 average with probability p |
| `m4_m5_recurrences.py` | (d), (g) | Master-theorem parameters; exact T(2áµ) against closed forms; recursion-tree level sums; doubling ratios; M5 "gap" test |
| `m4_m5_simulation.py` | (d) | runs the recursive M4 (4 or 2 parts) and M5 (real merge sort per level) engines with operation counters and timings |
| `f_bound_proof_check.py` | (f) | checks 3nÂ² â‰¤ f(n) â‰¤ 63nÂ² (n â‰¥ 1) and â‰¤ 4nÂ² (n â‰¥ 60) for every n â‰¤ 10â¶; shows f(n) is not O(n) |
| `scalability_estimates.py` | (g) | operations and time at n = 10âµ and 10â¶, PASS/FAIL against 600 s, largest n that fits the window |
| `make_graphs.py` | all | draws the 7 figures from the CSV files |
| `diagrams.py` | (b)â€“(e), (g) | draws the flowcharts (M1, M1 hash redesign, M2, S1, S2) and the recursion-tree / substitution diagrams into `Report/diagrams/` |
| `run_tests.py` | all | 42 automated checks, prints `PASS â€¦` lines and `RESULT: 42/42 tests passed` |
| `run_all.py` | all | runs every program in order (all exit with code 0) |

Run everything (Python 3.13 with matplotlib), from `Question_1/Source_Code`:

```
py -3 run_all.py
```

## Key results (n = 1,000,000, 10â¸ operations per second)

| Module | Exact count | Class | Time | 10-min window |
|---|---|---|---:|:---:|
| M1 Duplicate detector | n(n âˆ’ 1)/2 = 499,999,500,000 | Î˜(nÂ²), Î˜(1) extra space | 83.3 min | FAIL |
| M2 Rate limiter | 2^âŒˆlogâ‚‚ nâŒ‰ âˆ’ 1 = 1,048,575 (1,023 for n = 1,024) | Î˜(n) â€“ the Î˜(n log n) claim is wrong | 0.0105 s | PASS |
| S2 Binary search | âŒŠlogâ‚‚ nâŒ‹ + 1 = 20 per search (logâ‚‚ n + 1 for n = 2áµ) | Î˜(log n); space Î˜(1) iterative, Î˜(log n) recursive | 0.2 Âµs | PASS |
| S1 Sequential search | p(n + 1)/2 + n(1 âˆ’ p) = 750,000.25 for p = 0.5 | Î˜(n) | 7.5 ms per search | â€“ |
| M4 current, 4T(n/2) + n | 2nÂ² âˆ’ n (Master Theorem Case 1) | Î˜(nÂ²); data doubles â†’ time Ã— 4 | 5.56 h | FAIL |
| M4 redesign, 2T(n/2) + n | n logâ‚‚ n + n (Case 2) | Î˜(n log n); data doubles â†’ time Ã— â‰ˆ 2.1 | 0.21 s | PASS |
| M5, 2T(n/2) + n log n | n logâ‚‚ n(logâ‚‚ n + 1)/2 + n (no standard case; extended Case 2 / recursion tree) | Î˜(n logÂ² n) | 2.10 s | PASS |
| Report generator | 3nÂ² + 10n logâ‚‚ n + 50 (câ‚ = 3, câ‚‚ = 63, nâ‚€ = 1; or câ‚‚ = 4, nâ‚€ = 60) | Î˜(nÂ²), not O(n) | 8.33 h | FAIL |

**Recommendation:** redesign M1 (hash set keyed on (title, seller), Î˜(n) expected, or sort + scan, Î˜(n log n)), adopt the M4 redesign, and replace the report generator's pairwise step with one-pass hash aggregation (made incremental). The three quadratic jobs already break the window at about 346,000 (M1), 173,000 (M4) and 141,000 (report generator) products.

## Report

`Question_1/Report/CO1_AT1_Report.docx` (also `.pdf`) follows the department's sample report format: cover page and mark sheet, problem statement and test environment, parts (a)â€“(g) each with the question text, **Ans:**, derivations, tables, code and output screenshots and graphs, a summary of findings, appendices Aâ€“D (complete source code, graph script, raw CSV data, test results), references and the Code-of-Conduct declaration (signature left blank).

## Notes

- The question paper gives no marks per part, so the mark sheet on the cover lists the paper's rubric (Understanding 20, Application 30, Problem-Solving 20, Accuracy 20, Clarity 10 = 100).
- The paper gives only the report generator's cost function f(n); the redesign suggested for it (one-pass aggregation instead of the pairwise step implied by the 3nÂ² term) is a recommendation, not an analysis of real code.
- Wall-clock times were measured while other programs shared the CPU, so they are secondary evidence; all conclusions rest on the counted operations and the derived closed forms, which agree exactly.

