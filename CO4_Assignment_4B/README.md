# CO4 Assignment 4B – Part II: Algorithm Engineering – Implement, Test, Debug & Optimise

**Course:** CSA06 – Design and Analysis of Algorithms · **Student:** V. Vasudevan (192425324) · SIMATS Engineering
**Course outcome:** CO4 – Solve optimization problems using Dynamic Programming and Greedy strategies ·
Individual · One week · 50 marks

The report answers the official question paper task by task (sub-sections numbered exactly as in the paper):
`Report/CO4_Assignment_4B_Report.pdf` (also `.docx`, and the Markdown source `.md`).

| Task | Paper title | Algorithms | Marks |
|---|---|---|---|
| 1 | Build and Validate a DP Solution – Word Wrap as a Document-Layout Engine (1.1–1.4) | suffix DP, Σ s² penalty, exhaustive reference | 8 |
| 2 | Greedy vs Dynamic Programming – Build It, Break It, Explain It (2.1–2.4) | fractional knapsack greedy, 0/1 knapsack DP | 9 |
| 3 | Routing Engine Under Changing Network Conditions (Stages A–D) | Dijkstra, Bellman-Ford, Floyd, Warshall | 10 |
| 4 | Smart Manufacturing Optimisation – Assembly Line Scheduling (4.1–4.5) | two-line DP with decision table and route | 7 |
| 5 | Three Greedy Engineers, One Network | Kruskal, Prim, Borůvka | 7 |
| 6 | Last-Mile Delivery Route Optimisation – TSP by DP (6.1–6.7) | Held–Karp DP, exhaustive validation | 9 |

## Folder structure

```
CO4_Assignment_4B/
├── Source_Code/
│   ├── Task_1/  word_wrap_dp.py (algorithm), word_wrap_demo.py, word_wrap_width_change.py,
│   │            word_wrap_width_sweep.py, draw_diagrams_t1.py, pseudocode.md, test_data/, results/
│   ├── Task_2/  knapsack_engines.py, knapsack_demo.py, knapsack_experiments.py, draw_diagrams_t2.py, ...
│   ├── Task_3/  routing_engine.py, routing_io.py, stage_a_dijkstra.py, stage_b_negative_edge.py,
│   │            stage_c_negative_cycle.py, stage_d_floyd.py, stage_d_warshall.py, boundary_tests.py,
│   │            task3_experiments.py, draw_diagrams_t3.py, ...
│   ├── Task_4/  assembly_line_dp.py, assembly_line_demo.py, assembly_line_changes.py, draw_diagrams_t4.py, ...
│   ├── Task_5/  mst_engines.py, mst_construction_demo.py, mst_multiple_msts.py, mst_boundary_failure.py,
│   │            mst_experiments.py, draw_diagrams_t5.py, ...
│   └── Task_6/  tsp_held_karp.py, make_delivery_data.py, tsp_route_engine.py, tsp_validate.py,
│                tsp_state_growth.py, draw_diagrams_t6.py, ...
├── Test_Cases/  run_all_tests.py, task1..task6_test_cases.json, task1..task6_checks.py,
│                run_all_tests_log.txt, test_results.csv
├── Report/      CO4_Assignment_4B_Report.pdf / .docx, Screenshots/ (outputs, flowcharts, diagrams, graphs)
└── README.md
```

* In every task folder the **algorithm module never prints** (it returns results plus a decision trace); the
  drivers do the input/output. `test_data/` holds the inputs (and, for Tasks 1 and 4, the predictions recorded
  before the modified cases were first run), `results/` the CSV behind every table and graph.
* `draw_diagrams_tN.py` draws the task's flowcharts (standard symbols) and diagrams from the programs' own results.
* Test-case IDs: **N** normal, **S** student-designed / counter-example, **V** validation against an independent
  reference (exhaustive enumeration, brute force, another algorithm), **R** requirement change, **B** boundary,
  **F** failure / invalid input.

## How to run (Python 3.13, `py -3`; standard library + matplotlib)

```
cd Source_Code/Task_1 && py -3 word_wrap_demo.py && py -3 word_wrap_width_change.py && py -3 word_wrap_width_sweep.py
cd Source_Code/Task_2 && py -3 knapsack_demo.py && py -3 knapsack_experiments.py        (experiments ≈ 1.5 min)
cd Source_Code/Task_3 && py -3 stage_a_dijkstra.py   (… stage_b/c/d_*.py, boundary_tests.py, task3_experiments.py)
cd Source_Code/Task_4 && py -3 assembly_line_demo.py && py -3 assembly_line_changes.py
cd Source_Code/Task_5 && py -3 mst_construction_demo.py   (… mst_multiple_msts.py, mst_boundary_failure.py, mst_experiments.py)
cd Source_Code/Task_6 && py -3 tsp_route_engine.py && py -3 tsp_validate.py && py -3 tsp_state_growth.py   (≈ 2 min)
cd Test_Cases && py -3 run_all_tests.py          →  RESULT: 101/101 tests passed
py -3 Source_Code/Task_N/draw_diagrams_tN.py     →  flowcharts and diagrams in Report/Screenshots/
```

All random data is seeded (42; the Task 6 data generator uses 45), so every run reproduces the numbers in the report.

## Key results

| Task | Result |
|---|---|
| 1 | W = 21: minimum penalty 66 (= exhaustive over 524,288 break patterns; greedy first-fit 78); W = 18 / 26 / 30 → 27 / 9 / 24 (8 of 9 recorded predictions confirmed); the exact-fit boundary case exposes an off-by-one fit test |
| 2 | Fractional greedy 273 (= unit-split DP); student counter-example GreedyResult 153 ≠ DPOptimum 192, first blocking commitment C1; greedy work independent of W, DP work n(W + 1) cells |
| 3 | Dijkstra correct on non-negative roads; a designed −5 edge makes it wrong for 5 depots while Bellman-Ford is right; a reachable negative cycle is reported (`NegativeCycleError`), not hidden; Floyd and Warshall matrices validated against Dijkstra and BFS |
| 4 | Minimum production time 32 with transfers after S2 and S4 (= exhaustive over 64 routes); transfer 2 → 12 ⇒ 35; slowdown at L2-S4 ⇒ production moves to line 1 at S4, 38 |
| 5 | Kruskal, Prim, Borůvka: same MST (cost 38) built in different orders; with ties 8 MSTs and 3 different correct edge sets; deployment choice backed by sparse/dense/round measurements |
| 6 | Held–Karp: Hub→E→D→B→F→A→C→Hub = 123 (= exhaustive over 720 routes); hub + 4 validated against all 24 routes; state space measured to n = 16 |
