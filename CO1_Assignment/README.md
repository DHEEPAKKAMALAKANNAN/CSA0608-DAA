# CO1 Assignment – Design, Analyse and Validate an Efficient Search Strategy for a Large-Scale Student Record System

**Course:** CSA06 – Design and Analysis of Algorithms · **Assessment:** Assignment 1 – CO1 (50 marks, individual, 1 week)
**Student:** V. Vasudevan · **Reg. No.:** 192425324 · SIMATS Engineering · 19 November 2026

**Course outcome CO1:** determine algorithm efficiency using asymptotic notations and mathematical techniques
including the Master Theorem and the substitution method.

## The project

A university database stores student records, each identified by a unique 9-digit **registration number**
(19xxxxxxx). Staff must find out whether a registration number exists and retrieve the record. The database grows
from 1,000 to 1,000,000+ records. This project designs three different search strategies, derives their complexity
mathematically (including recurrences solved by backward substitution, the Master Theorem and induction),
implements them in pure Python with operation counters, measures them on 1,000 / 10,000 / 100,000 / 1,000,000
records, recommends one, and re-evaluates it for the **Day-4 Design Challenge** (50,000 searches per hour on
1,000,000 records with a daily batch of new records).

The complete answer to all 12 tasks is the report
[`Report/Documentation/CO1_Assignment_Report.docx`](Report/Documentation/CO1_Assignment_Report.docx)
(also as [PDF](Report/Documentation/CO1_Assignment_Report.pdf), in the department's sample-report format). Every `Task_N` folder
contains a `README.md` with that task's complete answer.

## Algorithms implemented

| Approach | Strategy | Preprocessing | Search cost | Measured at n = 1,000,000 |
|---|---|---|---|---|
| A – Sequential search (iterative) | Brute force | none | Θ(n): (n + 1)/2 hit, n miss | 480,558 comparisons, 22.5 ms per hit |
| B – Binary search (recursive) | Divide and conquer | own merge sort, Θ(n log n) | Θ(log n): ≤ ⌊log₂ n⌋ + 1 | 18.87 comparisons, 6.24 µs (after a 5.85 s sort) |
| C – Hash table, separate chaining | Space–time trade-off | build, Θ(n) expected | Θ(1) expected: 1 + α/2 hit, α miss | 1.32 comparisons, 0.88 µs (after a 0.74 s build) |

- **Recurrence (Tasks 6–7):** C(n) = C(⌊n/2⌋) + 1, C(0) = 0 ⇒ C(n) = ⌊log₂ n⌋ + 1 = Θ(log n); merge sort
  C(n) = 2C(n/2) + n − 1 ⇒ n log₂ n − n + 1 = Θ(n log n). Both checked exactly against counted comparisons.
- **Recommendation (Task 11):** the hash table – fastest at every size, cheapest preprocessing, pays off after about
  20 searches.
- **Design challenge (Task 12): MODIFY** – keep hashing, reserve capacity (m = 2,666,683 for 2,000,000 records) and
  insert each daily batch incrementally (Θ(b)): 1.21 CPU-seconds per simulated day against 10.85 s for the best
  binary-search variant and 30,335 s for sequential search.

## How to run

Requirements: Python 3.13 (`py -3` on Windows) and matplotlib (graphs only). Everything is seeded and reproducible.

```
cd Task_8_Implementation_Testing/Source_Code
py -3 student_records.py              # sample of the generated data            (< 1 s)
py -3 search_algorithms.py            # traces of the three approaches on 15 records (< 1 s)
py -3 test_search_algorithms.py       # 39 test checks, ends with "RESULT: 39/39 tests passed" (~15 s)
py -3 run_experiments.py              # Task 9/10 measurements -> CSV + graphs   (~1.5 min)
py -3 design_challenge_simulation.py  # Task 12 simulation on 1,000,000 records (~1.5 min)
```

The diagram scripts are `Task_1_Algorithm_Design/draw_flowcharts.py`, `Task_4_Case_Analysis/draw_decision_tree.py`
and `Task_7_Recurrence_Solution/draw_recursion_trees.py`. The experiment programs write their CSV files to
`Task_9_Experimental_Performance/` and `Task_12_Design_Challenge/` and copies plus all graphs to
`Report/Tables_and_Graphs/`.

## Repository structure

```
CO1_Assignment/
├── Task_1_Algorithm_Design/          README (3 approaches, pseudocode), flowchart PNGs + draw_flowcharts.py
├── Task_2_Basic_Operation/           README
├── Task_3_Mathematical_Complexity/   README (derivations, preprocessing + search, break-even)
├── Task_4_Case_Analysis/             README, binary-search decision tree PNG + script
├── Task_5_Asymptotic_Analysis/       README (O, Ω, Θ with constants, growth 10³ → 10⁶)
├── Task_6_Recurrence_Formulation/    README (recurrence read from the code)
├── Task_7_Recurrence_Solution/       README (substitution, Master Theorem, induction), recursion-tree PNG + script
├── Task_8_Implementation_Testing/    README (test procedure, 13 cases + properties), captured outputs
│   └── Source_Code/                  student_records.py, search_algorithms.py, test_search_algorithms.py,
│                                     run_experiments.py, design_challenge_simulation.py
├── Task_9_Experimental_Performance/  README (tables + graphs), 10 CSV files
├── Task_10_Theory_vs_Experiment/     README
├── Task_11_Final_Recommendation/     README
├── Task_12_Design_Challenge/         README (A–D), 4 CSV files
├── Report/
│   ├── Source_Code_Screenshots/      rendered source code of all 8 programs
│   ├── Output_Screenshots/           real execution output of the 5 programs
│   ├── Analysis/                     complexity_derivations.md, theory_vs_experiment.md, design_challenge_analysis.md
│   ├── Tables_and_Graphs/            8 graphs (fig1–fig8) + all 14 CSV tables
│   └── Documentation/                CO1_Assignment_Report.docx / .pdf (all 12 tasks + appendices)
└── README.md
```

## Test environment

13th Gen Intel Core i5-13420H, 16 GB RAM, Windows 11, Python 3.13.11 (CPython 64-bit). Operation counts are the
primary evidence; times are the minimum of repeated runs with the garbage collector off, measured while other jobs
were running on the same machine.
