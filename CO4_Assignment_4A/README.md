# CSA06 – Assignment 4A (CO4): Dynamic Programming – Design, Traces and Analysis

**Student:** V. Vasudevan · **Reg. No.:** 192425324 · CSA06 – Design and Analysis of Algorithms · SIMATS Engineering · 19 November 2026

## Assumed question / scope

The six task statements of Assignment 4A were **not provided**, so this assignment is a **reconstruction**.
The course outcome was confirmed as CO4 = *Dynamic Programming and Greedy technique* (Levitin, chapters 8–9);
Assignment 4A covers **Dynamic Programming** (Levitin ch. 8) and Assignment 4B (built separately) covers the Greedy
technique. Each task statement was written in the department's style (application context → what to design, trace,
compute and test → evidence expected) and is reproduced in the report's question boxes. The marks below are assumed
(total 50). All instances are my own and live in the `test_data/` CSV files; if the official paper uses other data,
edit those files and rerun the programs – every table, trace, graph and screenshot is regenerated from them.

| Task | Topic (application context) | Marks |
|---|---|---|
| 1 | Overlapping sub-problems – binomial coefficient C(n, k) and Fibonacci (combinatorial test planning) | 7 |
| 2 | 0/1 knapsack by DP – bottom-up table, backtracking, memory function, single row (drone cargo loading) | 9 |
| 3 | Warshall's algorithm – transitive closure (data-centre replication reachability) | 7 |
| 4 | Floyd's algorithm – all-pairs shortest paths, predecessor matrix, negative edges and cycles (city courier) | 9 |
| 5 | Optimal binary search tree – C and R tables, Knuth's improvement (chatbot keyword lookup) | 8 |
| 6 | **Day-4 Design Challenge (compulsory)** – knapsack with W = 100,000 kg, n = 200, item recovery, 32 MB memory limit | 10 |

## Folder structure

```
CO4_Assignment_4A/
├── Source_Code/
│   ├── Task_1/   binomial_dp.py, binomial_experiments.py, test_binomial.py, pseudocode.md, test_data/, results/
│   ├── Task_2/   knapsack_dp.py, knapsack_experiments.py, test_knapsack.py, pseudocode.md, test_data/, results/
│   ├── Task_3/   warshall_closure.py, warshall_experiments.py, test_warshall.py, pseudocode.md, test_data/, results/
│   ├── Task_4/   floyd_shortest_paths.py, floyd_experiments.py, test_floyd.py, pseudocode.md, test_data/, results/
│   ├── Task_5/   optimal_bst.py, obst_experiments.py, test_optimal_bst.py, pseudocode.md, test_data/, results/
│   └── Task_6/   large_knapsack.py, large_knapsack_experiments.py, test_large_knapsack.py, pseudocode.md,
│                 test_data/, results/
├── Report/
│   ├── CO4_Assignment_4A_Report.pdf      (the deliverable)
│   ├── CO4_Assignment_4A_Report.docx
│   ├── CO4_Assignment_4A_Report.md       (source of the report)
│   └── Screenshots/                      (code and execution screenshots, graphs embedded in the report)
└── README.md
```

In every task folder: the **main module** implements the algorithms with operation counters and prints the manual
trace; the **experiment script** writes CSV files to `results/` and its graph to `Report/Screenshots/`; the **test
script** prints `PASS`/`FAIL` lines and `RESULT: k/k tests passed`; `pseudocode.md` holds the DP formulation and the
pseudocode written before the implementation; `test_data/` holds the input instances and table-driven test cases;
`results/` holds the captured console logs (`*_log.txt`) and the raw CSV data.

## How to run

Python 3.13 (`py -3`), standard library only; matplotlib for the graphs. Every program is deterministic (seed 42).

```
cd Source_Code/Task_1
py -3 binomial_dp.py            # manual trace of C(6, 3)
py -3 binomial_experiments.py   # growth experiment -> results/*.csv + Report/Screenshots/task1_binomial_growth.png
py -3 test_binomial.py          # 25 tests
```

The same three-step pattern applies to every task (Task 6: `large_knapsack.py` takes about 10 s and
`large_knapsack_experiments.py` about 1 minute because each design runs in a fresh process to measure its memory).

## Results at a glance

| Task | Main result | Verification |
|---|---|---|
| 1 | C(6, 3) = 20 with 12 additions = (k−1)k/2 + k(n−k); naive recursion makes 2C(n,k) − 1 calls (5,408,311 at n = 24: 1,048.53 ms vs 0.039 ms for the table) | 25/25 tests, `math.comb` |
| 2 | Drone load P1 + P3 + P4 = 10 kg, value 94 (greedy: 88); memory function computes 23 of 50 cells; 165 ns per table cell, Θ(nW) | 23/23 tests, brute force |
| 3 | Closure of the 5-centre network: {D, E} cannot reach {A, B, C}; n³ = 125 steps; time ×7.9–8.4 per doubling of n | 19/19 tests, BFS |
| 4 | All shortest travel times and routes (e.g. E → B → C → D → A, 17 min); negative energy streets handled, Dijkstra wrong; negative cycle detected | 18/18 tests, Bellman–Ford |
| 5 | Optimal BST root *refund*, cost 1.85 vs 2.20 for the balanced BST; Knuth's version examines 65× fewer candidates at n = 400 | 15/15 tests, all Catalan(n) trees |
| 6 | Original table needs 396.7 MB (> 32 MB); redesign R1 (value row + decision bits) needs 6.1 MB with the same optimum 128,890 and identical items; R2 (Hirschberg-style) needs 7.5 MB for any n | 24/24 tests, original design + brute force |

## Test environment

13th Gen Intel Core i5-13420H, 16 GB RAM, Windows 11 Home 10.0.26200, Python 3.13.11 (64-bit), matplotlib 3.10.8.
Times are medians of 3 runs (secondary evidence); counted operations are the primary evidence.
