# CO1 – Assessment Tool 1: Scalability Audit of an E-Commerce Platform (ShopSphere)

**Course:** CSA06 – Design and Analysis of Algorithms · **Student:** V. Vasudevan (Reg. No. 192425324) · **Mode:** Individual

**CO assessed:** determine algorithm efficiency using asymptotic notations and mathematical techniques, including the Master Theorem and the substitution method.

ShopSphere's catalogue grows from n = 100,000 to n = 1,000,000 products. I audited five back-end modules (M1 duplicate detector, M2 rate limiter, M3 search S1/S2, M4 recommendation engine, M5 sales analytics, plus the nightly report generator). For each one I derived the exact basic-operation count and the asymptotic class, checked the result by counting operations in hand-written Python implementations, and estimated the running time at 10⁸ operations per second against a 10-minute nightly window.

## Folder structure

```
CO1_AT1/
├── README.md
└── Question_1/
    ├── Source_Code/         programs + their output logs (<program>_output.txt)
    ├── Report/              CO1_AT1_Report.md / .docx / .pdf
    │   ├── screenshots/     source-code and execution-output screenshots
    │   └── graphs/          fig1 … fig7 (PNG, 150 dpi)
    └── Supporting_Files/    raw CSV data behind every table and graph
```

## Programs (`Question_1/Source_Code`)

| Program | Part | What it does |
|---|---|---|
| `audit_common.py` | all | constants of the paper (10⁸ ops/s, 600 s window, n = 10⁵ and 10⁶) and table/CSV helpers |
| `m1_duplicate_detector.py` | (a), (b), (g) | nested-loop detector with comparison counters; checks n(n − 1)/2; finds planted duplicates; hash-set and sort-and-scan redesigns |
| `m2_rate_limiter.py` | (b) | counts Audit calls; trace for n = 1,024 (1,023 audits); closed form 2^⌈log₂ n⌉ − 1 for many n; compares with n log₂ n |
| `m3_product_search.py` | (c), (e) | S1 sequential and S2 binary search (iterative + recursive); backward-substitution check; best/average/worst counts; S1 average with probability p |
| `m4_m5_recurrences.py` | (d), (g) | Master-theorem parameters; exact T(2ᵏ) against closed forms; recursion-tree level sums; doubling ratios; M5 "gap" test |
| `m4_m5_simulation.py` | (d) | runs the recursive M4 (4 or 2 parts) and M5 (real merge sort per level) engines with operation counters and timings |
| `f_bound_proof_check.py` | (f) | checks 3n² ≤ f(n) ≤ 63n² (n ≥ 1) and ≤ 4n² (n ≥ 60) for every n ≤ 10⁶; shows f(n) is not O(n) |
| `scalability_estimates.py` | (g) | operations and time at n = 10⁵ and 10⁶, PASS/FAIL against 600 s, largest n that fits the window |
| `make_graphs.py` | all | draws the 7 figures from the CSV files |
| `run_tests.py` | all | 42 automated checks, prints `PASS …` lines and `RESULT: 42/42 tests passed` |
| `run_all.py` | all | runs every program in order (all exit with code 0) |

Run everything (Python 3.13 with matplotlib), from `Question_1/Source_Code`:

```
py -3 run_all.py
```

## Key results (n = 1,000,000, 10⁸ operations per second)

| Module | Exact count | Class | Time | 10-min window |
|---|---|---|---:|:---:|
| M1 Duplicate detector | n(n − 1)/2 = 499,999,500,000 | Θ(n²), Θ(1) extra space | 83.3 min | FAIL |
| M2 Rate limiter | 2^⌈log₂ n⌉ − 1 = 1,048,575 (1,023 for n = 1,024) | Θ(n) – the Θ(n log n) claim is wrong | 0.0105 s | PASS |
| S2 Binary search | ⌊log₂ n⌋ + 1 = 20 per search (log₂ n + 1 for n = 2ᵏ) | Θ(log n); space Θ(1) iterative, Θ(log n) recursive | 0.2 µs | PASS |
| S1 Sequential search | p(n + 1)/2 + n(1 − p) = 750,000.25 for p = 0.5 | Θ(n) | 7.5 ms per search | – |
| M4 current, 4T(n/2) + n | 2n² − n (Master Theorem Case 1) | Θ(n²); data doubles → time × 4 | 5.56 h | FAIL |
| M4 redesign, 2T(n/2) + n | n log₂ n + n (Case 2) | Θ(n log n); data doubles → time × ≈ 2.1 | 0.21 s | PASS |
| M5, 2T(n/2) + n log n | n log₂ n(log₂ n + 1)/2 + n (no standard case; extended Case 2 / recursion tree) | Θ(n log² n) | 2.10 s | PASS |
| Report generator | 3n² + 10n log₂ n + 50 (c₁ = 3, c₂ = 63, n₀ = 1; or c₂ = 4, n₀ = 60) | Θ(n²), not O(n) | 8.33 h | FAIL |

**Recommendation:** redesign M1 (hash set keyed on (title, seller), Θ(n) expected, or sort + scan, Θ(n log n)), adopt the M4 redesign, and replace the report generator's pairwise step with one-pass hash aggregation (made incremental). The three quadratic jobs already break the window at about 346,000 (M1), 173,000 (M4) and 141,000 (report generator) products.

## Report

`Question_1/Report/CO1_AT1_Report.md` (also `.docx` and `.pdf`) follows the department's sample report format: cover page and mark sheet, problem statement and test environment, parts (a)–(g) each with the question text, **Ans:**, derivations, tables, code and output screenshots and graphs, a summary of findings, appendices A–D (complete source code, graph script, raw CSV data, test results), references and the Code-of-Conduct declaration (signature left blank).

## Notes

- The question paper gives no marks per part, so the mark sheet on the cover lists the paper's rubric (Understanding 20, Application 30, Problem-Solving 20, Accuracy 20, Clarity 10 = 100).
- The paper gives only the report generator's cost function f(n); the redesign suggested for it (one-pass aggregation instead of the pairwise step implied by the 3n² term) is a recommendation, not an analysis of real code.
- Wall-clock times were measured while other programs shared the CPU, so they are secondary evidence; all conclusions rest on the counted operations and the derived closed forms, which agree exactly.
