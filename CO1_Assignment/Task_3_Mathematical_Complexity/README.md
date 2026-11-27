# Task 3 â€“ Derive the Time-Complexity Function Mathematically [6 Marks]

> Part of **CSA06 Assignment 1 (CO1)** â€“ K DHEEPAK (192411108). Full report: [`Report/Documentation/CO1_Assignment_Report.md`](../Report/Documentation/CO1_Assignment_Report.md) Â· [project README](../README.md)

> Derive the time-complexity function for each proposed approach using mathematical analysis. Discuss:
> - the input size (n);
> - the number of times the basic operation executes;
> - how the operation count changes with n;
> - the mathematical expression representing the running time;
> - any preprocessing cost involved;
> - the overall cost when preprocessing and searching are considered together.
> You must show the mathematical reasoning leading to the complexity result. Merely stating that an algorithm is O(n), O(log n), etc., will not receive full credit.

**Ans:**

## 1. Input size and cost model

- **Input size n** = number of student records in the database (the registration numbers are fixed-size 9-digit integers, so one comparison costs constant time).
- **q** = number of searches served by one preprocessing (q = 1,200,000 per day in Task 12).
- **p** = probability that a searched registration number exists (p = Â½ in Task 9 and p = 0.8 in Task 12).
- Successful searches are for a uniformly random stored student, so positions in the arrival order are uniformly distributed.
- C(n) = number of basic operations; T(n) = cÂ·C(n) + lower-order terms, where c is the machine cost of one basic operation with its loop overhead.

## 2. Approach A â€“ sequential search

The loop compares the key with A[0], A[1], â€¦ and stops at the first match.

**Successful search for the record at position i (0-based):** the comparisons are with A[0], â€¦, A[i], so C(i) = i + 1.

**Unsuccessful search:** every record is compared once: C<sub>miss</sub>(n) = Î£<sub>i=0</sub><sup>nâˆ’1</sup> 1 = n.

**Average successful search** (each of the n positions with probability 1/n):

C<sub>hit</sub>(n) = Î£<sub>i=0</sub><sup>nâˆ’1</sup> (1/n)(i + 1) = (1/n) Â· n(n + 1)/2 = **(n + 1)/2**

**Average over hits and misses** (success probability p):

C<sub>avg</sub>(n) = pÂ·(n + 1)/2 + (1 âˆ’ p)Â·n

For p = Â½: C<sub>avg</sub>(n) = 0.75n + 0.25; for p = 0.8: C<sub>avg</sub>(n) = 0.6n + 0.4 (600,000 comparisons per search at n = 10â¶).

**Running time:** T<sub>A</sub>(n) = c<sub>A</sub>Â·C(n) + câ‚€ = Î˜(n) on average and in the worst case. I measured c<sub>A</sub> â‰ˆ 30 ns per comparison at n = 1,000 rising to â‰ˆ 47 ns at n = 10â¶ (Task 10 explains why).

**Preprocessing:** P<sub>A</sub>(n) = 0. **Overall cost of q searches:** T<sub>A</sub>(n, q) = qÂ·C<sub>avg</sub>(n) = Î˜(qÂ·n).

## 3. Approach B â€“ merge-sort preprocessing + recursive binary search

**Preprocessing (merge sort).** Merging two sorted runs of total size s takes at most s âˆ’ 1 comparisons (every comparison outputs one record and the last record needs no comparison) and at least âŒŠs/2âŒ‹. Sorting n records sorts two halves of sizes âŒˆn/2âŒ‰ and âŒŠn/2âŒ‹ and merges them, so in the worst case

C<sub>sort</sub>(n) = C<sub>sort</sub>(âŒˆn/2âŒ‰) + C<sub>sort</sub>(âŒŠn/2âŒ‹) + (n âˆ’ 1),  C<sub>sort</sub>(1) = 0.

For n = 2áµ this solves (Task 7, Â§4) to **C<sub>sort</sub>(n) = n logâ‚‚ n âˆ’ n + 1**, and for general n to nâŒˆlogâ‚‚ nâŒ‰ âˆ’ 2<sup>âŒˆlogâ‚‚ nâŒ‰</sup> + 1. On random input the average is â‰ˆ n logâ‚‚ n âˆ’ 1.25n (Knuth). Each merge level also moves every record about twice (copy to the buffer and back), so the moves are â‰ˆ 2n logâ‚‚ n. Hence **P<sub>B</sub>(n) = Î˜(n log n)** time and Î˜(n) extra memory (sorted copy + buffer).

**Search â€“ worst case.** Each three-way comparison either finds the key or keeps one half of the current range. A range of size s leaves at most âŒŠs/2âŒ‹ records (Task 6 proves the exact sizes). After j unsuccessful comparisons at most âŒŠn/2Ê²âŒ‹ records remain. A comparison is made only while the range is non-empty, i.e. while âŒŠn/2Ê²âŒ‹ â‰¥ 1 â‡” 2Ê² â‰¤ n â‡” j â‰¤ logâ‚‚ n. So the largest number of comparisons is

C<sub>worst</sub>(n) = âŒŠlogâ‚‚ nâŒ‹ + 1.

**Search â€“ average successful case.** Arrange the sorted keys in the binary-search decision tree (Figure 4 in Task 4): the key at depth d needs exactly d comparisons and depth d holds 2<sup>dâˆ’1</sup> keys. For n = 2áµ âˆ’ 1 (a full tree of k levels) the total over all keys is

S(n) = Î£<sub>d=1</sub><sup>k</sup> dÂ·2<sup>dâˆ’1</sup> = (k âˆ’ 1)Â·2áµ + 1

(proof: let F = Î£ dÂ·2<sup>dâˆ’1</sup>; then 2F âˆ’ F = kÂ·2áµ âˆ’ Î£<sub>d=0</sub><sup>kâˆ’1</sup> 2áµˆ = kÂ·2áµ âˆ’ (2áµ âˆ’ 1)), so

C<sub>hit</sub>(n) = S(n)/n = ((k âˆ’ 1)(n + 1) + 1)/n â‰ˆ **logâ‚‚(n + 1) âˆ’ 1**.

For general n I use the exact recurrence of the program, S(n) = n + S(âŒŠ(n âˆ’ 1)/2âŒ‹) + S(âŒˆ(n âˆ’ 1)/2âŒ‰), S(0) = 0 (each of the n searches makes one comparison at the root and then continues in one half). It gives 8.987, 12.363, 15.690 and 18.951 comparisons for the four sizes.

**Search â€“ average unsuccessful case.** An unsuccessful search ends in one of the n + 1 gaps (external nodes). The external path length equals the internal path length + 2n, which gives C<sub>miss</sub>(n) = (S(n) + n)/(n + 1) = 9.977, 13.362, 16.689 and 19.951; every unsuccessful search costs âŒŠlogâ‚‚ nâŒ‹ or âŒŠlogâ‚‚ nâŒ‹ + 1.

**Running time:** T<sub>B</sub>(n) = c<sub>B</sub>Â·(âŒŠlogâ‚‚ nâŒ‹ + 1) + câ‚€ = Î˜(log n). **Overall cost of q searches:**

T<sub>B</sub>(n, q) â‰ˆ (n logâ‚‚ n âˆ’ 1.25n) + qÂ·logâ‚‚ n = **Î˜(n log n + q log n)**

## 4. Approach C â€“ hash table with separate chaining

**Preprocessing (build).** The table size is m = smallest prime â‰¥ n/0.75, so Î± = n/m â‰¤ 0.75. Inserting the i-th record (i = 0, â€¦, n âˆ’ 1) costs one hash computation and a duplicate check along its chain, whose expected length under uniform hashing is i/m. Total expected operations:

P<sub>C</sub>(n) = n + Î£<sub>i=0</sub><sup>nâˆ’1</sup> i/m = n + n(n âˆ’ 1)/(2m) â‰ˆ n(1 + Î±/2) â‰¤ **1.375n**,

plus Î˜(m) = Î˜(n/0.75) to allocate the buckets. So the build is **Î˜(n)** expected time and Î˜(n + m) memory.

**Unsuccessful search.** One hash computation, then the key is compared with every record of chain h(key); with simple uniform hashing the expected chain length is n/m:

C<sub>miss</sub>(n) = **Î±** (â‰¤ 0.75) comparisons + 1 hash.

**Successful search.** New records are appended at the end of a chain, so searching for the j-th inserted record compares the key with that record and with the records inserted earlier into the same chain. Each of the j âˆ’ 1 earlier records is in the same chain with probability 1/m:

C<sub>hit</sub>(n) = (1/n) Î£<sub>j=1</sub><sup>n</sup> (1 + (j âˆ’ 1)/m) = 1 + (n âˆ’ 1)/(2m) = **1 + Î±/2 âˆ’ Î±/(2n)** â‰¤ 1.375.

**Refinement for this key universe.** The registration numbers are drawn *without replacement* from only U = 10â· values. Bucket j can only ever receive the c<sub>j</sub> numbers with k mod m = j (at n = 10â¶, U/m â‰ˆ 7.5, so c<sub>j</sub> is 7 or 8). The chain lengths are then hypergeometric instead of Poisson, and the same derivation gives C<sub>hit</sub> = 1 + (n âˆ’ 1)Â·Î£ c<sub>j</sub>(c<sub>j</sub> âˆ’ 1) / (2U(U âˆ’ 1)) = 1.3267 and C<sub>miss</sub> = nÂ·Î£ c<sub>j</sub>(c<sub>j</sub> âˆ’ 1)/(U(U âˆ’ 1)) = 0.6533 at n = 10â¶. For small n (U/m large) this equals the textbook value (1.3670 at n = 1,000). Task 10 shows that the measurements agree with the refined value.

**Running time:** T<sub>C</sub>(n) = c<sub>h</sub> + c<sub>C</sub>Â·(1 + Î±/2) = Î˜(1) expected. **Overall cost of q searches:**

T<sub>C</sub>(n, q) â‰ˆ n(1 + Î±/2) + q(1 + 1 + Î±/2) = **Î˜(n + q)** expected

## 5. Preprocessing and searching together

Table 5: Derived operation counts at the four required sizes (A hit = (n + 1)/2, A miss = n, B hit = S(n)/n, B worst = âŒŠlogâ‚‚ nâŒ‹ + 1, C hit = 1 + (n âˆ’ 1)/2m with the m actually built, B sort â‰ˆ n logâ‚‚ n)

| Records (n) | A hit | A miss | B hit | B worst | C hit | B sort n logâ‚‚ n |
|---|---|---|---|---|---|---|
| 1,000 | 500.5 | 1,000 | 8.987 | 10 | 1.367 | 9,966 |
| 10,000 | 5,000.5 | 10,000 | 12.363 | 14 | 1.375 | 132,877 |
| 100,000 | 50,000.5 | 100,000 | 15.690 | 17 | 1.375 | 1,660,964 |
| 1,000,000 | 500,000.5 | 1,000,000 | 18.951 | 20 | 1.375 | 19,931,569 |

With preprocessing included, the total cost of q searches (50/50 hit/miss mix) is A: qÂ·0.75n, B: n logâ‚‚ n + qÂ·logâ‚‚ n, C: 1.375n + 2q. Preprocessing pays off after the **break-even number of searches** q* at which the totals are equal:

- A â†’ B: q* = (n logâ‚‚ n âˆ’ 1.25n)/(0.75n âˆ’ logâ‚‚ n) â‰ˆ (logâ‚‚ n âˆ’ 1.25)/0.75 = 24.9 at n = 10â¶ (measured 25.2, Table 24).
- A â†’ C: q* â‰ˆ 1.375n/(0.75n âˆ’ 2) â‰ˆ 1.8 for every n (measured 1.79â€“1.85).
- C needs fewer operations than B for **every** q â‰¥ 0 (smaller preprocessing *and* cheaper searches), so B can only win on criteria other than lookup cost (ordering, worst-case guarantee, memory).

Measured in basic operations, both preprocessing strategies are worth their cost after a few dozen searches, and hashing after about two.

