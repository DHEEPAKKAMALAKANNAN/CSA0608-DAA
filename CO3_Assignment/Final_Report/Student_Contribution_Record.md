# Student Contribution Record – CSA06 Assignment 3 (CO3): Divide-and-Conquer Algorithm Engineering

**Course:** CSA06 – Design and Analysis of Algorithms · SIMATS Engineering · **Nature of assignment:** Pair

Table 1: Pair details

| Role | Name | Register number |
|---|---|---|
| Student A | V. Vasudevan | 192425324 |
| Student B | [Student B Name] | [Reg. No.] |

**Status: proposed record.** This record was prepared together with the assignment and lists a proposed division of
the individual responsibilities. Both students must check it, correct it where it differs from what they actually
did, fill in Student B's details and sign it before submission. Both students took part in every question and are
prepared to explain and defend the complete assignment in the individual verification or viva.

## Contributions per question

Table 2: Student A, Student B and shared contributions for Q1–Q7

| Q | Student A – V. Vasudevan | Student B – [Student B Name] | Shared |
|---|---|---|---|
| Q1 – Max–Min and Binary Search (6) | Divide/conquer/combine design; `q1_maxmin_binsearch.py` (four Max–Min methods, recursive binary search, counters) and `q1_tests.py`; derivation of (3n + L₁)/2 − 2 and the even-split rule | Recursion trees; recurrences (Master Theorem, backward substitution, exact binary-search averages); `q1_experiments.py`, `q1_graphs.py` | Predictions; prediction vs observation; design decision (pairwise loop, ≤ 20 probes) |
| Q2 – Merge Sort vs Quick Sort (7) | Recurrences (best, worst, average with full derivation); the five datasets; decomposition diagrams | `q2_sorting.py` (Merge Sort, Quick Sort with three pivot rules, counters), `q2_tests.py`, `q2_experiments.py`; experiments | `q2_graphs.py`; analysis; recommendation; choice of the Q7 limitation |
| Q3 – Karatsuba (6) | Digit-array representation; schoolbook and subtractive Karatsuba in `q3_karatsuba.py`; `q3_tests.py`; worked example | Recurrence by Master Theorem and recursion tree; addition-count formula; `q3_experiments.py`, `q3_graphs.py`; size, crossover and threshold experiments | Divide/conquer/combine description; threshold decision (t = 16) |
| Q4 – Strassen (7) | Closed forms (n³, n²(n − 1), 7ᵏ, 6(7ᵏ − 4ᵏ)); analytical optimal cutoff (c = 8); recurrence solutions; operation-count crossover; `q4_experiments.py`, `q4_graphs.py` | Block decomposition (7 products); static vs dynamic padding design; `q4_strassen.py` (conventional, Strassen, padding, cutoff, counters), `q4_tests.py`; verification against numpy | Prediction vs observation; recommendation (dynamic padding, c = 32) |
| Q5 – Closest Pair (7) | D&C closest pair (presort by x, merge-by-y, strip scan) and counters in `q5_closest_pair.py`; recurrence and Master-Theorem solution | Brute-force reference and the four drone distributions; proof of the 7-neighbour strip bound; recursion-tree solution; `q5_experiments.py`, `q5_graphs.py` | Predictions; `q5_tests.py`; verification of all comparable runs; 1-second-cycle decision |
| Q6 – Median of Medians and Meet-in-the-Middle (7) | Lead on (a) Median of Medians: design, `q6_median_of_medians.py`, recurrence and linear-time proof, group-size study, `Median_of_Medians/README.md` | Lead on (b) Meet-in-the-Middle: design, `q6_meet_in_the_middle.py`, time/space derivation, 2-second limits, `Meet_in_the_Middle/README.md` | Cross-checking each other's derivations and tests (`q6_tests.py`); `q6_graphs.py`; design decisions |
| Q7 – Day-4 Design Challenge (10) | Diagnosis evidence; **independent proposal A** (median-of-three + Hoare partition + smaller-part recursion) with pseudocode, prediction and prototype `proposal_a_median3_hoare.py`; adversary `q7_adversary.py` | **Independent proposal B** (random pivot + 3-way partition + insertion-sort cutoff) with pseudocode, prediction and prototype `proposal_b_threeway_cutoff.py`; `q7_experiments.py`, `q7_graphs.py` | Comparison on identical datasets; rejection of joint v1; joint final design (fat partition + depth budget/heapsort) in `q7_introsort_hybrid.py`; `q7_tests.py`; objectives and defence |
| Report and repository | Report sections Q1, Q3, Q5, Q7-B; README | Report sections Q2, Q4, Q6, Q7-C | Problem statement, summary, appendices, final review |

## Day-4 Design Challenge: independent proposals

- **Student A (folder `Q7_Day4_Design_Challenge/Student_A_Initial_Design/`):** pick a representative pivot and split
  equal keys evenly — median-of-three pivot, Hoare partition whose pointers stop on equal keys, recursion into the
  smaller part (depth ≤ log₂ n). Strength: all natural inputs at 1.32–1.50 n log₂ n with the fewest moves. Weakness
  found: all-equal batches still cost n log₂ n comparisons; quadratic on an adversarial input.
- **Student B (folder `Q7_Day4_Design_Challenge/Student_B_Initial_Design/`):** finish equal keys in one pass — random
  pivot, Dijkstra 3-way partition, insertion sort for ≤ 16 orders. Strength: all-equal batch in 2n comparisons,
  slot data 0.79 n log₂ n. Weakness found: most comparisons and moves on distinct keys; quadratic on an adversarial
  input when the seed is known.
- **Joint final design (folder `Q7_Day4_Design_Challenge/Joint_Final_Design/`):** median-of-three and two-pointer
  scanning from A, equal-key elimination and insertion cutoff from B, combined in a fat partition, plus a joint depth
  budget with heapsort fallback that guarantees O(n log n).

## Confirmation

Table 3: Confirmation by both students

| Student | Signature | Date |
|---|---|---|
| Student A – V. Vasudevan (192425324) | | |
| Student B – [Student B Name] ([Reg. No.]) | | |
