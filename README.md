# Design and Analysis of Algorithms (CSA06) - Lab Exercises and Assignments

**Student:** V. Vasudevan  ·  **Reg. No.:** 192425324  ·  SIMATS Engineering

## Lab Exercises

Python solutions for all 102 DAA lab exercises. Every exercise shows the **program** with the **screenshot of its output directly below it**.

| Topic | Exercises | Page |
|---|---|---|
| Topic 1 - Introduction | 1-17 | [Topic1_Introduction.md](Topic1_Introduction.md) |
| Topic 2 - Brute Force | 18-30 | [Topic2_BruteForce.md](Topic2_BruteForce.md) |
| Topic 3 - Divide and Conquer | 31-46 | [Topic3_DivideAndConquer.md](Topic3_DivideAndConquer.md) |
| Topic 4 - Dynamic Programming | 47-68 | [Topic4_DynamicProgramming.md](Topic4_DynamicProgramming.md) |
| Topic 5 - Greedy | 69-80 | [Topic5_Greedy.md](Topic5_Greedy.md) |
| Topic 6 - Backtracking | 81-96 | [Topic6_Backtracking.md](Topic6_Backtracking.md) |
| Topic 7 - Tractability and Approximation Algorithms | 97-102 | [Topic7_TractabilityAndApproximation.md](Topic7_TractabilityAndApproximation.md) |

### How the screenshots were made

Each `solutions/exNNN.py` was run with `py -3 -X utf8 exNNN.py`; the captured text output was then rendered as a terminal-style image (`screenshots/exNNN.png`). Run any program yourself with `python solutions/exNNN.py` (Python 3, standard library only).

### Notes on the exercise sheet

Some expected outputs printed in the exercise sheet are arithmetically wrong or inconsistent (for example the Karatsuba product, the assignment-problem costs, the Hamiltonian-cycle example). The programs print the *correct computed* result and add a `Note` line in the output wherever it differs from the sheet.

## Assignments (CO1 – CO4)

Each assignment folder follows the structure prescribed in its submission instructions and contains the source code, real execution outputs (screenshots + logs), experimental data, graphs and a report in the department's sample report format (`.docx` / `.pdf`, with the Markdown source).

| Folder | Assessment | Topic | Report |
|---|---|---|---|
| [CO1_AT1](CO1_AT1/) | CO1 – Assessment Tool 1 | Scalability audit of the "ShopSphere" e-commerce platform (asymptotic analysis, substitution, Master Theorem) | [Question_1/Report](CO1_AT1/Question_1/Report/) |
| [CO1_Assignment](CO1_Assignment/) | Assignment 1 – CO1 | Efficient search strategy for a large-scale student record system (Tasks 1–12) | [Report/Documentation](CO1_Assignment/Report/Documentation/) |
| [CO2_Assignment](CO2_Assignment/) | Assignment 2 – CO2 | Brute force & exhaustive search: sorting, sequential search, string matching, closest pair, convex hull, knapsack, Day-4 redesign (Q1–Q7) | [Final_Report](CO2_Assignment/Final_Report/) |
| [CO2_Debugging_Optimisation](CO2_Debugging_Optimisation/) | CO2 – Debugging & Optimisation | SentinelOps SOC alert-triage module: defects, debugging, optimisation, analysis | [Report](CO2_Debugging_Optimisation/Report/) |
| [CO3_AT3](CO3_AT3/) | CO3 – Assessment Tool 3 | Divide-and-conquer case study: Merge Sort, Quick Sort, Binary Search, Strassen | [Final_Design_and_Analysis](CO3_AT3/Final_Design_and_Analysis/) |
| [CO3_Assignment](CO3_Assignment/) | Assignment 3 – CO3 | Divide & conquer (Q1–Q7): Max–Min, Binary Search, Merge/Quick Sort, Karatsuba, Strassen, Closest Pair, Median of Medians, Meet-in-the-Middle, Day-4 challenge | [Final_Report](CO3_Assignment/Final_Report/) |
| [CO4_Assignment_4A](CO4_Assignment_4A/) | Assignment 4A – CO4 | Dynamic programming (Tasks 1–6) | [Report](CO4_Assignment_4A/Report/) |
| [CO4_Assignment_4B](CO4_Assignment_4B/) | Assignment 4B – CO4 | Greedy technique (Tasks 1–6) | [Report](CO4_Assignment_4B/Report/) |

### Running the assignment code

Python 3.10+ (developed with Python 3.13 on Windows). The algorithms use only the standard library; `matplotlib` is needed only for the graph scripts (`pip install matplotlib`). Every program is deterministic (fixed random seeds) and takes no input — see each folder's `README.md` for the exact commands, e.g.

```bash
cd CO1_AT1/Question_1/Source_Code
python run_all.py
```

### Notes

- Operation counts (comparisons, distance computations, probes …) are the primary experimental evidence; execution times are secondary and machine-dependent.
- For some assessments only the submission instructions were available when this work was prepared; those folders state their **assumed question / scope** at the top of their README and report.
