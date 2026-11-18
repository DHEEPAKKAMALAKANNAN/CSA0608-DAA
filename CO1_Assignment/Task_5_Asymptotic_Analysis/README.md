# Task 5 – Perform Asymptotic Analysis [3 Marks]

> Part of **CSA06 Assignment 1 (CO1)** – V. Vasudevan (192425324). Full report: [`Report/Documentation/CO1_Assignment_Report.md`](../Report/Documentation/CO1_Assignment_Report.md) · [project README](../README.md)

> Express and compare the growth behaviour using appropriate asymptotic notation. Discuss:
> - appropriate use of O, Ω and/or Θ;
> - how each algorithm behaves as n becomes very large;
> - how the growth rates differ;
> - what the growth behaviour means when the dataset increases from 1,000 to 1,000,000+ records.
> Interpret in the context of the application.

**Ans:**

## 1. The notations I use

- t(n) ∈ **O**(g(n)) if there are constants c > 0 and n₀ with t(n) ≤ c·g(n) for all n ≥ n₀ (upper bound, used for "never worse than").
- t(n) ∈ **Ω**(g(n)) if t(n) ≥ c·g(n) for all n ≥ n₀ (lower bound, "never better than").
- t(n) ∈ **Θ**(g(n)) if both hold (tight bound, the exact growth class).

I use Θ for each *case* (best, average, worst) because each case is a single function of n, and O/Ω for statements about the algorithm over *all* inputs.

## 2. Asymptotic classes, with the constants

**A – sequential search.** Worst case C(n) = n ∈ Θ(n). Average (n + 1)/2 ∈ Θ(n): for all n ≥ 1, ½·n ≤ (n + 1)/2 ≤ 1·n (c₁ = ½, c₂ = 1, n₀ = 1). Best case 1 ∈ Θ(1). Over all inputs sequential search is therefore **O(n) and Ω(1)**; it is *not* Θ(n) for every input, only for the worst and average cases.

**B – binary search.** Worst case ⌊log₂ n⌋ + 1 ∈ Θ(log n): for n ≥ 2, log₂ n < ⌊log₂ n⌋ + 1 ≤ log₂ n + 1 ≤ 2 log₂ n (c₁ = 1, c₂ = 2, n₀ = 2). Average ≈ log₂ n − 1 ∈ Θ(log n). Best case Θ(1). Over all inputs: **O(log n) and Ω(1)**. Preprocessing n log₂ n − n + 1 ∈ Θ(n log n): it is ≤ n log₂ n, and for n ≥ 4 it is ≥ ½ n log₂ n because ½ n log₂ n ≥ n − 1 when log₂ n ≥ 2.

**C – hash table.** Expected search 1 + α/2 ≤ 1.375 and α ≤ 0.75, so both are **Θ(1) expected**; the worst case over adversarial key sets is Θ(n), so over all inputs the search is **O(n)** and only Θ(1) *in expectation*. Build: Θ(n) expected (n hash computations + ≤ 0.375n comparisons), O(n²) worst case.

Table 7: Asymptotic summary (search cost per query, plus preprocessing)

| Approach | Best case | Average case | Worst case | Preprocessing cost | Extra space |
|---|---|---|---|---|---|
| A sequential | Θ(1) | Θ(n) | Θ(n) | none | Θ(1) |
| B binary (recursive) | Θ(1) | Θ(log n) | Θ(log n) | Θ(n log n) | Θ(n) + Θ(log n) stack |
| C hash table | Θ(1) | Θ(1) expected | Θ(n) | Θ(n) expected | Θ(n + m) = Θ(n) |

## 3. How the growth rates differ as n becomes very large

The limits of the ratios order the three classes strictly:

- lim<sub>n→∞</sub> log₂ n / n = lim (1/(n ln 2)) / 1 = 0 (L'Hôpital), so log n ∈ o(n): binary search grows **strictly slower** than sequential search.
- lim<sub>n→∞</sub> 1 / log₂ n = 0, so Θ(1) ⊂ o(log n): hashing grows strictly slower than binary search.
- For preprocessing, lim n / (n log n) = lim 1/log n = 0: building a hash table grows strictly slower than sorting.

The practical meaning: **doubling the database** doubles the work of A, adds exactly **one** comparison to B, and changes nothing for C.

## 4. From 1,000 to 1,000,000 records (×1,000)

Table 8: Growth from n = 1,000 to n = 1,000,000 (theory from Task 3, measurements from Task 9)

| Quantity | n = 1,000 | n = 1,000,000 | Change for ×1,000 records | Asymptotic prediction |
|---|---|---|---|---|
| A comparisons per hit (theory / measured) | 500.5 / 496.25 | 500,000.5 / 480,558 | ×999 / ×968 | ×1,000 (Θ(n)) |
| B comparisons per hit (theory / measured) | 8.99 / 8.98 | 18.95 / 18.87 | +9.96 / +9.89 | + log₂ 1000 = +9.97 (Θ(log n)) |
| C comparisons per hit (theory / measured) | 1.367 / 1.344 | 1.327 / 1.327 | unchanged | ×1 (Θ(1)) |
| A time per hit (µs, measured) | 15.05 | 22,536.82 | ×1,497 | ×1,000 |
| B time per hit (µs, measured) | 1.52 | 6.24 | ×4.1 | ×2.0 |
| C time per hit (µs, measured) | 0.26 | 0.88 | ×3.4 | ×1 |

**Interpretation for the university.** With 1,000 students all three designs answer instantly (15 µs at most). At 1,000,000 students one sequential search takes 23 ms for an existing student and 51 ms for a mistyped number, and the cost keeps growing with every admitted batch; at the 50,000 searches per hour of Task 12 that becomes a substantial, permanently growing CPU load. Binary search stays at about 20 comparisons and hashing at about one comparison, so both remain effectively instantaneous for a database 1,000 times larger. (The times grew somewhat more than the counts for B and C; Task 10 explains this with memory caching.)
