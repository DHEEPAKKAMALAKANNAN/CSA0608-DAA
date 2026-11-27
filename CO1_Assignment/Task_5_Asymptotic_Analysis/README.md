# Task 5 â€“ Perform Asymptotic Analysis [3 Marks]

> Part of **CSA06 Assignment 1 (CO1)** â€“ K DHEEPAK (192411108). Full report: [`Report/Documentation/CO1_Assignment_Report.md`](../Report/Documentation/CO1_Assignment_Report.md) Â· [project README](../README.md)

> Express and compare the growth behaviour using appropriate asymptotic notation. Discuss:
> - appropriate use of O, Î© and/or Î˜;
> - how each algorithm behaves as n becomes very large;
> - how the growth rates differ;
> - what the growth behaviour means when the dataset increases from 1,000 to 1,000,000+ records.
> Interpret in the context of the application.

**Ans:**

## 1. The notations I use

- t(n) âˆˆ **O**(g(n)) if there are constants c > 0 and nâ‚€ with t(n) â‰¤ cÂ·g(n) for all n â‰¥ nâ‚€ (upper bound, used for "never worse than").
- t(n) âˆˆ **Î©**(g(n)) if t(n) â‰¥ cÂ·g(n) for all n â‰¥ nâ‚€ (lower bound, "never better than").
- t(n) âˆˆ **Î˜**(g(n)) if both hold (tight bound, the exact growth class).

I use Î˜ for each *case* (best, average, worst) because each case is a single function of n, and O/Î© for statements about the algorithm over *all* inputs.

## 2. Asymptotic classes, with the constants

**A â€“ sequential search.** Worst case C(n) = n âˆˆ Î˜(n). Average (n + 1)/2 âˆˆ Î˜(n): for all n â‰¥ 1, Â½Â·n â‰¤ (n + 1)/2 â‰¤ 1Â·n (câ‚ = Â½, câ‚‚ = 1, nâ‚€ = 1). Best case 1 âˆˆ Î˜(1). Over all inputs sequential search is therefore **O(n) and Î©(1)**; it is *not* Î˜(n) for every input, only for the worst and average cases.

**B â€“ binary search.** Worst case âŒŠlogâ‚‚ nâŒ‹ + 1 âˆˆ Î˜(log n): for n â‰¥ 2, logâ‚‚ n < âŒŠlogâ‚‚ nâŒ‹ + 1 â‰¤ logâ‚‚ n + 1 â‰¤ 2 logâ‚‚ n (câ‚ = 1, câ‚‚ = 2, nâ‚€ = 2). Average â‰ˆ logâ‚‚ n âˆ’ 1 âˆˆ Î˜(log n). Best case Î˜(1). Over all inputs: **O(log n) and Î©(1)**. Preprocessing n logâ‚‚ n âˆ’ n + 1 âˆˆ Î˜(n log n): it is â‰¤ n logâ‚‚ n, and for n â‰¥ 4 it is â‰¥ Â½ n logâ‚‚ n because Â½ n logâ‚‚ n â‰¥ n âˆ’ 1 when logâ‚‚ n â‰¥ 2.

**C â€“ hash table.** Expected search 1 + Î±/2 â‰¤ 1.375 and Î± â‰¤ 0.75, so both are **Î˜(1) expected**; the worst case over adversarial key sets is Î˜(n), so over all inputs the search is **O(n)** and only Î˜(1) *in expectation*. Build: Î˜(n) expected (n hash computations + â‰¤ 0.375n comparisons), O(nÂ²) worst case.

Table 7: Asymptotic summary (search cost per query, plus preprocessing)

| Approach | Best case | Average case | Worst case | Preprocessing cost | Extra space |
|---|---|---|---|---|---|
| A sequential | Î˜(1) | Î˜(n) | Î˜(n) | none | Î˜(1) |
| B binary (recursive) | Î˜(1) | Î˜(log n) | Î˜(log n) | Î˜(n log n) | Î˜(n) + Î˜(log n) stack |
| C hash table | Î˜(1) | Î˜(1) expected | Î˜(n) | Î˜(n) expected | Î˜(n + m) = Î˜(n) |

## 3. How the growth rates differ as n becomes very large

The limits of the ratios order the three classes strictly:

- lim<sub>nâ†’âˆž</sub> logâ‚‚ n / n = lim (1/(n ln 2)) / 1 = 0 (L'HÃ´pital), so log n âˆˆ o(n): binary search grows **strictly slower** than sequential search.
- lim<sub>nâ†’âˆž</sub> 1 / logâ‚‚ n = 0, so Î˜(1) âŠ‚ o(log n): hashing grows strictly slower than binary search.
- For preprocessing, lim n / (n log n) = lim 1/log n = 0: building a hash table grows strictly slower than sorting.

The practical meaning: **doubling the database** doubles the work of A, adds exactly **one** comparison to B, and changes nothing for C.

## 4. From 1,000 to 1,000,000 records (Ã—1,000)

Table 8: Growth from n = 1,000 to n = 1,000,000 (theory from Task 3, measurements from Task 9)

| Quantity | n = 1,000 | n = 1,000,000 | Change for Ã—1,000 records | Asymptotic prediction |
|---|---|---|---|---|
| A comparisons per hit (theory / measured) | 500.5 / 496.25 | 500,000.5 / 480,558 | Ã—999 / Ã—968 | Ã—1,000 (Î˜(n)) |
| B comparisons per hit (theory / measured) | 8.99 / 8.98 | 18.95 / 18.87 | +9.96 / +9.89 | + logâ‚‚ 1000 = +9.97 (Î˜(log n)) |
| C comparisons per hit (theory / measured) | 1.367 / 1.344 | 1.327 / 1.327 | unchanged | Ã—1 (Î˜(1)) |
| A time per hit (Âµs, measured) | 15.05 | 22,536.82 | Ã—1,497 | Ã—1,000 |
| B time per hit (Âµs, measured) | 1.52 | 6.24 | Ã—4.1 | Ã—2.0 |
| C time per hit (Âµs, measured) | 0.26 | 0.88 | Ã—3.4 | Ã—1 |

**Interpretation for the university.** With 1,000 students all three designs answer instantly (15 Âµs at most). At 1,000,000 students one sequential search takes 23 ms for an existing student and 51 ms for a mistyped number, and the cost keeps growing with every admitted batch; at the 50,000 searches per hour of Task 12 that becomes a substantial, permanently growing CPU load. Binary search stays at about 20 comparisons and hashing at about one comparison, so both remain effectively instantaneous for a database 1,000 times larger. (The times grew somewhat more than the counts for B and C; Task 10 explains this with memory caching.)

