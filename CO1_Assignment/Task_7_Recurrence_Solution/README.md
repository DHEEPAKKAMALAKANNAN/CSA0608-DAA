# Task 7 â€“ Solve the Recurrence Relation [4 Marks]

> Part of **CSA06 Assignment 1 (CO1)** â€“ K DHEEPAK (192411108). Full report: [`Report/Documentation/CO1_Assignment_Report.md`](../Report/Documentation/CO1_Assignment_Report.md) Â· [project README](../README.md)

> Solve it using an appropriate method (substitution, iteration, Master Theorem, or another technique). Discuss:
> - why the selected method is applicable;
> - the steps;
> - the resulting complexity;
> - what the result indicates about the behaviour of the recursive algorithm as n increases.
> Show the analytical process. (Showing two methods, e.g. backward substitution AND Master Theorem, is a plus.)

**Ans:**

I solve C(n) = C(âŒŠn/2âŒ‹) + 1, C(0) = 0 (so C(1) = 1) with three methods: backward substitution (exact closed form for powers of two), the Master Theorem (growth class), and the substitution method by induction (exact closed form for **every** n). Then I solve the merge-sort recurrence and check all closed forms against the counted comparisons.

## 1. Method 1 â€“ Backward substitution (iteration)

**Why it applies.** The recurrence has a single recursive term whose argument halves, so repeatedly substituting the recurrence into itself produces a simple pattern. For n = 2áµ the floors disappear (âŒŠ2áµ/2âŒ‹ = 2<sup>kâˆ’1</sup>).

**Steps.** Let n = 2áµ:

C(2áµ) = C(2<sup>kâˆ’1</sup>) + 1

= [C(2<sup>kâˆ’2</sup>) + 1] + 1 = C(2<sup>kâˆ’2</sup>) + 2

= [C(2<sup>kâˆ’3</sup>) + 1] + 2 = C(2<sup>kâˆ’3</sup>) + 3

= â€¦

= C(2<sup>kâˆ’i</sup>) + i  (general pattern after i substitutions)

Choose i = k to reach the known value C(2â°) = C(1) = 1:

C(2áµ) = C(1) + k = 1 + k, and since k = logâ‚‚ n: **C(n) = logâ‚‚ n + 1** for n = 2áµ.

By the smoothness rule (log n is a smooth function and C is non-decreasing), the result extends to all n: C(n) âˆˆ Î˜(log n).

## 2. Method 2 â€“ Master Theorem

**Why it applies.** The recurrence has the form T(n) = aÂ·T(n/b) + f(n) with a = 1 â‰¥ 1 recursive call, b = 2 > 1, and f(n) = 1 asymptotically positive; floors in the argument do not change the result.

**Steps.**

- a = 1, b = 2, f(n) = 1 = Î˜(nâ°), so d = 0.
- n<sup>log<sub>b</sub> a</sup> = n<sup>logâ‚‚ 1</sup> = nâ° = 1.
- Compare f(n) with n<sup>log<sub>b</sub> a</sup>: f(n) = Î˜(1) = Î˜(n<sup>log<sub>b</sub> a</sup>), i.e. a = b<sup>d</sup> (1 = 2â°). This is **Case 2**.
- Case 2 gives T(n) = Î˜(n<sup>log<sub>b</sub> a</sup> Â· log n) = Î˜(nâ° log n) = **Î˜(log n)**.
- The regularity condition aÂ·f(n/b) â‰¤ cÂ·f(n) is only required in Case 3, so no check is needed here.

## 3. Method 3 â€“ Substitution method (proof by induction for every n)

**Claim:** C(n) = âŒŠlogâ‚‚ nâŒ‹ + 1 for all n â‰¥ 1.

**Basis:** n = 1: C(1) = C(0) + 1 = 1 = âŒŠlogâ‚‚ 1âŒ‹ + 1. âœ“

**Inductive step:** let n â‰¥ 2 and assume the claim for all 1 â‰¤ m < n. Choose j with 2Ê² â‰¤ n < 2<sup>j+1</sup>, so âŒŠlogâ‚‚ nâŒ‹ = j â‰¥ 1. Then 2<sup>jâˆ’1</sup> â‰¤ âŒŠn/2âŒ‹ < 2Ê², so âŒŠlogâ‚‚ âŒŠn/2âŒ‹âŒ‹ = j âˆ’ 1. Because 1 â‰¤ âŒŠn/2âŒ‹ < n the hypothesis applies:

C(n) = C(âŒŠn/2âŒ‹) + 1 = (âŒŠlogâ‚‚ âŒŠn/2âŒ‹âŒ‹ + 1) + 1 = (j âˆ’ 1) + 2 = j + 1 = **âŒŠlogâ‚‚ nâŒ‹ + 1**. âœ“

This is the exact worst-case number of three-way comparisons for every database size, and it agrees with the backward substitution for n = 2áµ.

## 4. Recursion tree, and the merge-sort recurrence

**Binary search.** The recursion tree is a single path (one recursive call per level): sizes n, âŒŠn/2âŒ‹, âŒŠn/4âŒ‹, â€¦, 1, with cost 1 on each of the âŒŠlogâ‚‚ nâŒ‹ + 1 levels and 0 at the empty base case. Summing the levels gives âŒŠlogâ‚‚ nâŒ‹ + 1 again (Figure 5a, n = 16: 5 levels â†’ 5 comparisons).

**Merge sort, backward substitution** (n = 2áµ, C(n) = 2C(n/2) + n âˆ’ 1, C(1) = 0):

C(2áµ) = 2C(2<sup>kâˆ’1</sup>) + 2áµ âˆ’ 1

= 2[2C(2<sup>kâˆ’2</sup>) + 2<sup>kâˆ’1</sup> âˆ’ 1] + 2áµ âˆ’ 1 = 4C(2<sup>kâˆ’2</sup>) + 2Â·2áµ âˆ’ (1 + 2)

= 8C(2<sup>kâˆ’3</sup>) + 3Â·2áµ âˆ’ (1 + 2 + 4)

= â€¦

= 2â± C(2<sup>kâˆ’i</sup>) + iÂ·2áµ âˆ’ (2â± âˆ’ 1)

With i = k: C(2áµ) = 2áµÂ·C(1) + kÂ·2áµ âˆ’ 2áµ + 1 = **n logâ‚‚ n âˆ’ n + 1**.

**Merge sort, Master Theorem:** a = 2, b = 2, f(n) = n âˆ’ 1 = Î˜(nÂ¹), n<sup>logâ‚‚ 2</sup> = nÂ¹ â†’ f(n) = Î˜(n<sup>log<sub>b</sub> a</sup>), Case 2 â†’ **Î˜(n log n)**.

**Merge sort, recursion tree:** level i has 2â± merges of size n/2â±, each costing n/2â± âˆ’ 1, so the level costs n âˆ’ 2â±; summing over the logâ‚‚ n merging levels gives n logâ‚‚ n âˆ’ (2<sup>logâ‚‚ n</sup> âˆ’ 1) = n logâ‚‚ n âˆ’ n + 1 (Figure 5b, n = 16: 15 + 14 + 12 + 8 = 49 = 16Â·4 âˆ’ 16 + 1).

![Figure 5: Recursion trees for n = 16 â€“ (a) recursive binary search, (b) merge-sort preprocessing](../Task_7_Recurrence_Solution/recursion_trees.png)

## 5. Verification against the counted comparisons

I checked the solutions against the counters in the real code. Test P3 searched every key and every gap for each n from 1 to 200: the maximum count equalled âŒŠlogâ‚‚ nâŒ‹ + 1 for all 200 sizes, and the total over all successful searches equalled the recurrence S(n) exactly (P3b). Test P4 confirmed that merge sort never exceeded nâŒˆlogâ‚‚ nâŒ‰ âˆ’ 2<sup>âŒˆlogâ‚‚ nâŒ‰</sup> + 1. For the four experimental sizes I searched **every stored key once**:

Table 10: Closed forms against the counted comparisons (exhaustive search of every stored key; exhaustive_verification.csv)

| Number of records (n) | Max counted | âŒŠlogâ‚‚ nâŒ‹ + 1 | Average counted | S(n)/n (recurrence) | Merge sort counted | Merge sort worst bound |
|---|---|---|---|---|---|---|
| 1,000 | 10 | 10 | 8.9870 | 8.9870 | 8,744 | 8,977 |
| 10,000 | 14 | 14 | 12.3631 | 12.3631 | 120,491 | 123,617 |
| 100,000 | 17 | 17 | 15.6895 | 15.6895 | 1,536,197 | 1,568,929 |
| 1,000,000 | 20 | 20 | 18.9514 | 18.9514 | 18,674,803 | 18,951,425 |

The agreement is exact for binary search, as it must be for a deterministic algorithm.

## 6. What the result means

C(n) = âŒŠlogâ‚‚ nâŒ‹ + 1 = Î˜(log n) means that **each doubling of the database adds exactly one comparison** and one stack frame. Going from 1,000 to 1,000,000 students (Ã—1,000 â‰ˆ 2Â¹â°) adds only 10 comparisons (10 â†’ 20). The recursion is also safe in Python: at n = 10â¶ the depth is at most 21 frames, far below the default limit of 1,000 frames, which would only be reached for n â‰ˆ 2â¹â¹â¹. The merge-sort result Î˜(n log n) says the preprocessing grows slightly faster than linearly; it is paid once and then shared by all later searches (Task 10, Â§5).

## Files in this folder

- `recursion_trees.png` â€“ Figure 5
- `draw_recursion_trees.py` â€“ draws it and prints the level sums for n = 16

