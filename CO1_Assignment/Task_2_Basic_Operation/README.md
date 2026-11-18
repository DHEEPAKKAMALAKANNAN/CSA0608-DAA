# Task 2 – Identify the Basic Operation [2 Marks]

> Part of **CSA06 Assignment 1 (CO1)** – V. Vasudevan (192425324). Full report: [`Report/Documentation/CO1_Assignment_Report.md`](../Report/Documentation/CO1_Assignment_Report.md) · [project README](../README.md)

> For each of the proposed algorithms, identify the basic operation that predominantly determines its execution time. Discuss:
> - what the basic operation is;
> - where it occurs in the algorithm;
> - why it is appropriate to use this operation for efficiency analysis;
> - how the number of times it executes may change as the input size (n) increases.
> Do not simply name an operation. You are expected to relate the selected operation to the behaviour of the algorithm.

**Ans:**

## 1. Approach A – the key comparison A[i].reg_no = key

**What and where.** Line 2 of `SequentialSearch`, inside the only loop (`comparisons += 1` in `sequential_search`). Everything else in one loop iteration (advancing `i`, fetching `A[i]`) is done exactly once per comparison.

**Why it is appropriate.** The loop body is the innermost, most frequently executed statement, and the loop runs once per comparison, so the running time is T(n) ≈ c·C(n) + c₀ with c the cost of one iteration. Counting comparisons is machine-independent and captures the behaviour that matters: *how many records the search must look at before it can stop*.

**How the count changes with n.** It depends on where the student is: i + 1 comparisons for the record at position i, n for an absent number. Both the average and the worst case grow **linearly**: ten times more students means ten times more comparisons (measured 496 → 4,967 → 51,226 → 480,558 for successful searches, Task 9).

## 2. Approach B – the three-way comparison key : A[mid].reg_no

**What and where.** Line 3 of `BinSearch` (one comparison of the key with the middle record; equal / smaller / larger decides the next step). In `binary_search_recursive` it is the single `counter.comparisons += 1` executed in every call that has a non-empty range. I count a three-way comparison as one operation (as Levitin does); a two-way implementation would perform at most two `<`/`==` tests per step, which changes only the constant.

**Why it is appropriate.** Each recursive call performs exactly one such comparison plus constant work (computing `mid`, one call). The number of calls equals the number of comparisons (+1 for the final empty call of an unsuccessful search), so the comparison count determines the running time.

**Preprocessing.** For merge sort the basic operation is the key comparison `B[i].reg_no <= B[j].reg_no` inside `Merge` (line 4); every comparison places exactly one record, and record moves are proportional to it.

**How the count changes with n.** Every comparison halves the remaining range, so the count grows with the **number of halvings**, at most ⌊log₂ n⌋ + 1: multiplying n by 10 adds only log₂ 10 ≈ 3.3 comparisons (measured 8.98 → 12.31 → 15.64 → 18.87). The merge-sort count grows as n log₂ n.

## 3. Approach C – the key comparison along one chain (plus one hash computation)

**What and where.** Line 3 of `HashSearch` (`p.reg_no = key`, `counter.comparisons += 1` in `StudentHashTable.search`). Every search also performs exactly **one** hash computation `key mod m` (line 1), counted separately as `hash_computations`.

**Why it is appropriate.** The hash computation is a constant cost paid once per search; the only part whose count can vary is the scan of the chain, so the chain comparisons are what distinguish a good table (short chains) from a bad one (long chains). The total work of a search is 1 hash + (chain comparisons).

**Preprocessing.** Building the table costs one hash computation per record plus the duplicate-check comparisons along its chain; both are counted.

**How the count changes with n.** Because m grows with n (m ≥ n/0.75), the expected chain length α = n/m stays ≤ 0.75 for every n, so the count stays **constant** (measured 1.34, 1.39, 1.33, 1.32 comparisons per successful search). Only an adversarial key set that puts many keys into one chain would make it grow (Task 4).

## 4. Summary

Table 4: The basic operation of each algorithm and how its count grows

| Algorithm | Basic operation | Where | Count as n grows |
|---|---|---|---|
| A: sequential search | `A[i].reg_no = key` | loop body | linear: ≈ n/2 (hit), n (miss) |
| B: merge sort (preprocessing) | `B[i].reg_no <= B[j].reg_no` | `Merge` loop | n log₂ n − Θ(n) |
| B: recursive binary search | three-way `key : A[mid].reg_no` | once per recursive call | logarithmic: ≤ ⌊log₂ n⌋ + 1 |
| C: hash build (preprocessing) | `k mod m` + chain comparison | once per inserted record | linear: ≈ n(1 + α/2) |
| C: hash search | chain comparison `p.reg_no = key` (+1 hash) | chain loop | constant: ≈ 1 + α/2 (hit), α (miss) |

I deliberately do not use wall-clock time as the measure of efficiency: it depends on the processor, the Python interpreter and the other jobs running at the same moment, while the operation counts depend only on the algorithm and the input.
