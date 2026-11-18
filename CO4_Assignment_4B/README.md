# CO4 Assignment 4B – Greedy Technique: Testing, Debugging, Optimisation and Validation

**Course:** CSA06 – Design and Analysis of Algorithms · **Student:** V. Vasudevan (192425324) · SIMATS Engineering

## Assumed question / scope

The six task statements of Assignment 4B were **not provided**. CO4 is *Dynamic Programming and Greedy
technique*; Assignment 4A covers dynamic programming and this assignment (4B) covers the **greedy technique**.
The six tasks below are therefore **reconstructed** in the department's style (application context → design,
implement, test, debug, optimise → evidence expected), including the "given" test cases that each statement
supplies. Marks are assumed (total 50). If the official paper differs, the task statements in the report can be
replaced and the programs, test catalogues and evidence reused.

| Task | Title (reconstructed) | Greedy algorithm(s) | Marks |
|---|---|---|---|
| 1 | Briefing-room booking – activity selection | earliest-finish-time greedy (+ counter-examples for other rules) | 7 |
| 2 | Relief-truck loading and relief cash counters | fractional knapsack (sort / heap), greedy 0/1 knapsack (failure vs DP), coin change | 8 |
| 3 | Compressing SOC event logs | Huffman coding (heap, naive, two-queue), encode/decode | 8 |
| 4 | City fibre backbone | Prim (indexed heap, array) and Kruskal (union–find with rank + path compression) | 9 |
| 5 | Ambulance routing | Dijkstra (array O(V²) and heap O((V+E) log V)), Bellman–Ford reference | 8 |
| 6 | Day-4 Design Challenge – debug, optimise and validate a teammate's route service | Dijkstra / A* for 100,000 junctions with nightly weight updates | 10 |

All tasks share one scenario: the **city Emergency Operations Centre (EOC)**.

## Folder structure

```
CO4_Assignment_4B/
├── Source_Code/
│   ├── Task_1/  activity_selection.py, task1_experiments.py, pseudocode.md, test_data/, results/, logs/
│   ├── Task_2/  knapsack_coin_change.py, task2_experiments.py, pseudocode.md, test_data/, results/, logs/
│   ├── Task_3/  huffman_coding.py, task3_experiments.py, pseudocode.md, test_data/, results/, logs/
│   ├── Task_4/  mst_prim_kruskal.py, task4_experiments.py, pseudocode.md, test_data/, results/, logs/
│   ├── Task_5/  dijkstra_routing.py, task5_experiments.py, pseudocode.md, test_data/, results/, logs/
│   └── Task_6/  given_faulty_route_service.py (GIVEN, unchanged), fixed_route_service.py (final design),
│                task6_debugging.py, task6_scale_validation.py, city_network.py, pseudocode.md,
│                test_data/ (sample nightly feed of the 30 x 30 grid), results/, logs/
├── Test_Cases/  task1..task6_test_cases.json, run_all_tests.py, run_all_tests_log.txt, test_results.csv
├── Report/      CO4_Assignment_4B_Report.pdf / .docx / .md, Screenshots/ (code, outputs, graphs)
└── README.md
```

* `test_data/` – the input data of each task (given cases as CSV, failure inputs, a sample SOC log).
* `results/` – raw CSV behind every table and graph, and the PNG graphs.
* `logs/` – the captured console output of every program (the same text as the output screenshots).
* Test case IDs: **G** = given in the task statement, **S** = student-designed, **B** = boundary,
  **F** = failure / invalid input, **L** = large-scale, **D** = defect regression (Task 6).

## How to run (Python 3.13, `py -3`; standard library + matplotlib)

```
cd Source_Code/Task_1 && py -3 activity_selection.py && py -3 task1_experiments.py
cd Source_Code/Task_2 && py -3 knapsack_coin_change.py && py -3 task2_experiments.py
cd Source_Code/Task_3 && py -3 huffman_coding.py && py -3 task3_experiments.py
cd Source_Code/Task_4 && py -3 mst_prim_kruskal.py && py -3 task4_experiments.py
cd Source_Code/Task_5 && py -3 dijkstra_routing.py && py -3 task5_experiments.py
cd Source_Code/Task_6 && py -3 task6_debugging.py && py -3 task6_scale_validation.py
cd Test_Cases && py -3 run_all_tests.py          # -> RESULT: 101/101 tests passed
```

Every program is deterministic (seed 42 unless a test case states its own seed) and finishes in under about
one minute. The algorithm cores are hand-written pure Python with operation counters (comparisons, heap
operations, relaxations, pointer hops, road scans); counted operations are the primary evidence, wall-clock
times (`time.perf_counter`) are secondary because other jobs ran on the machine at the same time.

## Key results

| Task | Result |
|---|---|
| 1 | EFT optimal on all 2,000 random days and 500 brute-force checks; earliest-start, shortest-duration and fewest-conflicts rules defeated by designed counter-examples; sort-once EFT ≈ n log₂ n comparisons vs naive Θ(n·k) re-scan (8.1 M vs 0.10 M comparisons at n = 8,000). |
| 2 | Fractional greedy optimal (5,670 points on the given truck); greedy 0/1 loads 1,975 vs DP optimum 3,475; heap version halves comparisons when only 5 % of items fit; coin greedy optimal for the rupee system, fails for {1, 3, 4}, {1, 10, 25}, {1, 7, 10}. |
| 3 | Huffman: 2.24 bits/event vs 3 fixed (−25.3 %) on the given frequencies; 24 % smaller on a 100,000-event SOC stream; two-queue O(m) and heap O(m log m) vs naive O(m²). |
| 4 | Prim = Kruskal = brute force (37) on the given network (2 distinct MSTs); Prim-heap fastest on sparse graphs, union-by-rank + compression avoids the naive union–find's Θ(V²) pointer hops; disconnected network → spanning forest. |
| 5 | Step table and routes for the given network; array vs heap: heap 127× faster on sparse graphs (V = 8,000), array 10× faster on worst-case dense graphs; negative edge → wrong Dijkstra answer, Bellman–Ford correct. |
| 6 | Five defects found in the given code (wrong route, stale-entry re-expansion, broken path, O(V·E) road scans, unvalidated feed); fixed one at a time (0 → 18 of 18 catalogue cases); final design answers a query on 100,000 junctions in ≈ 0.5 s (A* ≈ 0.2 s) vs ≈ 1.2 h estimated for the teammate's data structure. |

See `Report/CO4_Assignment_4B_Report.pdf` for the full analysis.
