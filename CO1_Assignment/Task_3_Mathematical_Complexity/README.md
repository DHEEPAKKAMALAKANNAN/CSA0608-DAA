# Task 3 – Derive the Time-Complexity Function Mathematically [6 Marks]

> Part of **CSA06 Assignment 1 (CO1)** – V. Vasudevan (192425324). Full report: [`Report/Documentation/CO1_Assignment_Report.md`](../Report/Documentation/CO1_Assignment_Report.md) · [project README](../README.md)

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
- **p** = probability that a searched registration number exists (p = ½ in Task 9 and p = 0.8 in Task 12).
- Successful searches are for a uniformly random stored student, so positions in the arrival order are uniformly distributed.
- C(n) = number of basic operations; T(n) = c·C(n) + lower-order terms, where c is the machine cost of one basic operation with its loop overhead.

## 2. Approach A – sequential search

The loop compares the key with A[0], A[1], … and stops at the first match.

**Successful search for the record at position i (0-based):** the comparisons are with A[0], …, A[i], so C(i) = i + 1.

**Unsuccessful search:** every record is compared once: C<sub>miss</sub>(n) = Σ<sub>i=0</sub><sup>n−1</sup> 1 = n.

**Average successful search** (each of the n positions with probability 1/n):

C<sub>hit</sub>(n) = Σ<sub>i=0</sub><sup>n−1</sup> (1/n)(i + 1) = (1/n) · n(n + 1)/2 = **(n + 1)/2**

**Average over hits and misses** (success probability p):

C<sub>avg</sub>(n) = p·(n + 1)/2 + (1 − p)·n

For p = ½: C<sub>avg</sub>(n) = 0.75n + 0.25; for p = 0.8: C<sub>avg</sub>(n) = 0.6n + 0.4 (600,000 comparisons per search at n = 10⁶).

**Running time:** T<sub>A</sub>(n) = c<sub>A</sub>·C(n) + c₀ = Θ(n) on average and in the worst case. I measured c<sub>A</sub> ≈ 30 ns per comparison at n = 1,000 rising to ≈ 47 ns at n = 10⁶ (Task 10 explains why).

**Preprocessing:** P<sub>A</sub>(n) = 0. **Overall cost of q searches:** T<sub>A</sub>(n, q) = q·C<sub>avg</sub>(n) = Θ(q·n).

## 3. Approach B – merge-sort preprocessing + recursive binary search

**Preprocessing (merge sort).** Merging two sorted runs of total size s takes at most s − 1 comparisons (every comparison outputs one record and the last record needs no comparison) and at least ⌊s/2⌋. Sorting n records sorts two halves of sizes ⌈n/2⌉ and ⌊n/2⌋ and merges them, so in the worst case

C<sub>sort</sub>(n) = C<sub>sort</sub>(⌈n/2⌉) + C<sub>sort</sub>(⌊n/2⌋) + (n − 1),  C<sub>sort</sub>(1) = 0.

For n = 2ᵏ this solves (Task 7, §4) to **C<sub>sort</sub>(n) = n log₂ n − n + 1**, and for general n to n⌈log₂ n⌉ − 2<sup>⌈log₂ n⌉</sup> + 1. On random input the average is ≈ n log₂ n − 1.25n (Knuth). Each merge level also moves every record about twice (copy to the buffer and back), so the moves are ≈ 2n log₂ n. Hence **P<sub>B</sub>(n) = Θ(n log n)** time and Θ(n) extra memory (sorted copy + buffer).

**Search – worst case.** Each three-way comparison either finds the key or keeps one half of the current range. A range of size s leaves at most ⌊s/2⌋ records (Task 6 proves the exact sizes). After j unsuccessful comparisons at most ⌊n/2ʲ⌋ records remain. A comparison is made only while the range is non-empty, i.e. while ⌊n/2ʲ⌋ ≥ 1 ⇔ 2ʲ ≤ n ⇔ j ≤ log₂ n. So the largest number of comparisons is

C<sub>worst</sub>(n) = ⌊log₂ n⌋ + 1.

**Search – average successful case.** Arrange the sorted keys in the binary-search decision tree (Figure 4 in Task 4): the key at depth d needs exactly d comparisons and depth d holds 2<sup>d−1</sup> keys. For n = 2ᵏ − 1 (a full tree of k levels) the total over all keys is

S(n) = Σ<sub>d=1</sub><sup>k</sup> d·2<sup>d−1</sup> = (k − 1)·2ᵏ + 1

(proof: let F = Σ d·2<sup>d−1</sup>; then 2F − F = k·2ᵏ − Σ<sub>d=0</sub><sup>k−1</sup> 2ᵈ = k·2ᵏ − (2ᵏ − 1)), so

C<sub>hit</sub>(n) = S(n)/n = ((k − 1)(n + 1) + 1)/n ≈ **log₂(n + 1) − 1**.

For general n I use the exact recurrence of the program, S(n) = n + S(⌊(n − 1)/2⌋) + S(⌈(n − 1)/2⌉), S(0) = 0 (each of the n searches makes one comparison at the root and then continues in one half). It gives 8.987, 12.363, 15.690 and 18.951 comparisons for the four sizes.

**Search – average unsuccessful case.** An unsuccessful search ends in one of the n + 1 gaps (external nodes). The external path length equals the internal path length + 2n, which gives C<sub>miss</sub>(n) = (S(n) + n)/(n + 1) = 9.977, 13.362, 16.689 and 19.951; every unsuccessful search costs ⌊log₂ n⌋ or ⌊log₂ n⌋ + 1.

**Running time:** T<sub>B</sub>(n) = c<sub>B</sub>·(⌊log₂ n⌋ + 1) + c₀ = Θ(log n). **Overall cost of q searches:**

T<sub>B</sub>(n, q) ≈ (n log₂ n − 1.25n) + q·log₂ n = **Θ(n log n + q log n)**

## 4. Approach C – hash table with separate chaining

**Preprocessing (build).** The table size is m = smallest prime ≥ n/0.75, so α = n/m ≤ 0.75. Inserting the i-th record (i = 0, …, n − 1) costs one hash computation and a duplicate check along its chain, whose expected length under uniform hashing is i/m. Total expected operations:

P<sub>C</sub>(n) = n + Σ<sub>i=0</sub><sup>n−1</sup> i/m = n + n(n − 1)/(2m) ≈ n(1 + α/2) ≤ **1.375n**,

plus Θ(m) = Θ(n/0.75) to allocate the buckets. So the build is **Θ(n)** expected time and Θ(n + m) memory.

**Unsuccessful search.** One hash computation, then the key is compared with every record of chain h(key); with simple uniform hashing the expected chain length is n/m:

C<sub>miss</sub>(n) = **α** (≤ 0.75) comparisons + 1 hash.

**Successful search.** New records are appended at the end of a chain, so searching for the j-th inserted record compares the key with that record and with the records inserted earlier into the same chain. Each of the j − 1 earlier records is in the same chain with probability 1/m:

C<sub>hit</sub>(n) = (1/n) Σ<sub>j=1</sub><sup>n</sup> (1 + (j − 1)/m) = 1 + (n − 1)/(2m) = **1 + α/2 − α/(2n)** ≤ 1.375.

**Refinement for this key universe.** The registration numbers are drawn *without replacement* from only U = 10⁷ values. Bucket j can only ever receive the c<sub>j</sub> numbers with k mod m = j (at n = 10⁶, U/m ≈ 7.5, so c<sub>j</sub> is 7 or 8). The chain lengths are then hypergeometric instead of Poisson, and the same derivation gives C<sub>hit</sub> = 1 + (n − 1)·Σ c<sub>j</sub>(c<sub>j</sub> − 1) / (2U(U − 1)) = 1.3267 and C<sub>miss</sub> = n·Σ c<sub>j</sub>(c<sub>j</sub> − 1)/(U(U − 1)) = 0.6533 at n = 10⁶. For small n (U/m large) this equals the textbook value (1.3670 at n = 1,000). Task 10 shows that the measurements agree with the refined value.

**Running time:** T<sub>C</sub>(n) = c<sub>h</sub> + c<sub>C</sub>·(1 + α/2) = Θ(1) expected. **Overall cost of q searches:**

T<sub>C</sub>(n, q) ≈ n(1 + α/2) + q(1 + 1 + α/2) = **Θ(n + q)** expected

## 5. Preprocessing and searching together

Table 5: Derived operation counts at the four required sizes (A hit = (n + 1)/2, A miss = n, B hit = S(n)/n, B worst = ⌊log₂ n⌋ + 1, C hit = 1 + (n − 1)/2m with the m actually built, B sort ≈ n log₂ n)

| Records (n) | A hit | A miss | B hit | B worst | C hit | B sort n log₂ n |
|---|---|---|---|---|---|---|
| 1,000 | 500.5 | 1,000 | 8.987 | 10 | 1.367 | 9,966 |
| 10,000 | 5,000.5 | 10,000 | 12.363 | 14 | 1.375 | 132,877 |
| 100,000 | 50,000.5 | 100,000 | 15.690 | 17 | 1.375 | 1,660,964 |
| 1,000,000 | 500,000.5 | 1,000,000 | 18.951 | 20 | 1.375 | 19,931,569 |

With preprocessing included, the total cost of q searches (50/50 hit/miss mix) is A: q·0.75n, B: n log₂ n + q·log₂ n, C: 1.375n + 2q. Preprocessing pays off after the **break-even number of searches** q* at which the totals are equal:

- A → B: q* = (n log₂ n − 1.25n)/(0.75n − log₂ n) ≈ (log₂ n − 1.25)/0.75 = 24.9 at n = 10⁶ (measured 25.2, Table 24).
- A → C: q* ≈ 1.375n/(0.75n − 2) ≈ 1.8 for every n (measured 1.79–1.85).
- C needs fewer operations than B for **every** q ≥ 0 (smaller preprocessing *and* cheaper searches), so B can only win on criteria other than lookup cost (ordering, worst-case guarantee, memory).

Measured in basic operations, both preprocessing strategies are worth their cost after a few dozen searches, and hashing after about two.
