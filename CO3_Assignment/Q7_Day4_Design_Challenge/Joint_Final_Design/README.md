# Q7 – Joint final design (Student A + Student B)

**Implementation:** `../Implementation_Code/q7_introsort_hybrid.py` (`hybrid_sort`) · **Experiments:**
`../Implementation_Code/q7_experiments.py` · **Tests:** `../Implementation_Code/q7_tests.py` (20/20 passed) ·
**Pseudocode:** `../Pseudocode/Q7_Design_Challenge_Pseudocode.md` · **Diagram:** `../Implementation_Code/results/q7_design_diagram.png`

## 1. Comparison of the two independent proposals on identical datasets (n = 8,000)

| Dataset | Original (Q2) | Proposal A | Proposal B |
|---|---|---|---|
| random | 123,356 | 155,096 | 186,917 |
| sorted | 31,996,000 | 136,505 | 183,340 |
| reverse | 29,767,464 | 136,506 | 179,391 |
| slots (64 values) | 557,308 | 148,989 | 82,165 |
| all-equal | 31,996,000 | 142,907 | **16,000** |
| adversarial against A | 9,232,814 | **16,047,992** | 177,518 |
| adversarial against B (seed 42) | 130,998 | 153,533 | **32,004,690** |

(comparisons; full tables incl. moves, depth and time in `../Output_Screenshots/q7_experiments_output.txt`)

## 2. What was kept, combined or rejected

| Element | From | Decision | Evidence |
|---|---|---|---|
| Median-of-three pivot | A | **kept** | balanced splits on ordered exports; deterministic (same batch → same cost) |
| Two-pointer (Hoare) scan | A | **kept, combined** | A made 1,084 moves on sorted data vs 142,126 for B's partition |
| Smaller part recursively, loop on the larger | A | **kept** | A's depth ≤ 12 on every dataset, even under attack |
| Equal keys finished in the partition (3-way idea) | B | **kept, combined** | B: 16,000 comparisons on all-equal vs 142,907 for A |
| Insertion sort for ≤ 16 orders | B | **kept** | removes most calls on tiny parts |
| Dijkstra's partition itself | B | **rejected** (joint v1) | with A's pivot it reversed the upper part of sorted lists: v1 needed 484,346 comparisons and 10 heapsort fallbacks on sorted data |
| Random pivot | B | **rejected** | needs a secret seed; with a reproducible seed killer-B made it quadratic |
| Depth budget 2⌊log₂ n⌋ + heapsort fallback | joint | **added** | the only way to guarantee O(n log n) against adversarial input |

The two kept partition ideas are combined in the **fat partition** of Bentley & McIlroy: A's two pointers scan from
both ends (no moves on sorted data), while keys equal to the pivot are parked at both ends and swapped into the
middle at the end, where they are finished (B's idea).

## 3. Design objective (stated before validating the final version)

O1 ≤ 1.5 n log₂ n comparisons on every natural input; O2 ≤ 6 n log₂ n on adversarial inputs (derived worst-case
bound: ≤ 2⌊log₂ n⌋ levels of ≤ 2n comparisons plus heapsort ≤ 2n log₂ n); O3 recursion depth ≤ log₂ n; O4 all-equal
in 2n + 3 comparisons and the slot list no costlier than random; O5 always correct and deterministic.

## 4. Result (n = 8,000; identical datasets)

| Dataset | Comparisons | / n log₂ n | Moves | Depth | Heapsort fallbacks | Time (ms) |
|---|---|---|---|---|---|---|
| random | 150,258 | 1.45 | 62,526 | 7 | 0 | 12.4 |
| sorted | 81,491 | 0.79 | 2,296 | 9 | 0 | 5.7 |
| reverse | 89,473 | 0.86 | 10,324 | 9 | 0 | 9.4 |
| slots | 70,071 | 0.68 | 34,986 | 4 | 0 | 6.1 |
| all-equal | 16,003 | 0.15 | 0 | 1 | 0 | 0.8 |
| killer-A | 368,708 | 3.55 | 185,970 | 1 | 1 | 52.6 |
| killer-B | 143,878 | 1.39 | 62,267 | 6 | 0 | 11.9 |
| killer-J (against the joint design without guard) | 379,797 | 3.66 | 201,406 | 1 | 1 | 50.8 |

All five objectives were met at every size (1,000–8,000) and at n = 100,000 (0.12–1.41 n log₂ n, 10–195 ms).
Without the guard, killer-J costs 16,027,895 comparisons (n²/4) — the guard reduced it 42×.

## 5. Defence

- **Costs introduced:** a 157-line function instead of the 66-line original (four cooperating parts to test and maintain); on random distinct keys it makes 22% more comparisons
  than the original (1.45 vs 1.19 n log₂ n), although it is still faster (12.4 vs 16.3 ms) because it makes half
  the moves; it is not stable (equal deadlines may change order) – merge sort remains the choice when FIFO order
  among equal deadlines must be preserved.
- **When the original is still preferable:** small batches of distinct, randomly ordered keys, where its simplicity
  and fewer comparisons win and the quadratic inputs cannot occur.
- **Verdict:** the joint design removes the diagnosed limitation (Θ(n²) on ordered and duplicate-heavy batches), is
  never worse than O(n log n) even against a deliberate adversary, and is the fastest variant on the scheduler's
  typical slot-booked data.
