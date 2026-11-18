<!-- cover
institution: SIMATS ENGINEERING
department: Department of Computer Science and Engineering
course: CSA06 – Design and Analysis of Algorithms
assignment: ASSIGNMENT 1 – CO1
subtitle: Design, Analyse and Validate an Efficient Search Strategy for a Large-Scale Student Record System
coverage: CO1: Algorithm Fundamentals, Efficiency Analysis, Asymptotic Notations, Mathematical and Recurrence Analysis, Master Theorem and Substitution Method
student_name: V. Vasudevan
register_number: 192425324
nature: Individual
duration: 1 Week
total_marks: 50
marks: T1 | Algorithm Design | 5
marks: T2 | Basic Operation | 2
marks: T3 | Mathematical Complexity Analysis | 6
marks: T4 | Best/Average/Worst-Case Analysis | 4
marks: T5 | Asymptotic Analysis | 3
marks: T6 | Recurrence Formulation | 3
marks: T7 | Recurrence Solution | 4
marks: T8 | Implementation & Testing | 4
marks: T9 | Experimental Performance | 3
marks: T10 | Theory vs Experiment | 4
marks: T11 | Final Design Recommendation | 4
marks: T12 | Day-4 Design Challenge | 8
details: CO1 Coverage | Algorithm fundamentals, efficiency analysis, asymptotic analysis, mathematical analysis, recurrence analysis, Master Theorem, substitution, etc.
details: Course Outcome | CO1 – Determine algorithm efficiency using asymptotic notations and mathematical techniques including Master Theorem and substitution method.
details: Nature of Assignment | Individual
details: Duration | 1 Week
details: Total Marks | 50
details: Submission Date |
-->

# CSA06 – Assignment 1 (CO1): Design, Analyse and Validate an Efficient Search Strategy for a Large-Scale Student Record System

### Problem Statement: University Student Record Retrieval

A university maintains a large academic database containing student records, each identified by a unique **Registration Number**. Faculty and administrative staff frequently need to determine whether a particular student record exists and retrieve the corresponding information. The database may contain 1,000 → 10,000 → 100,000 → 1,000,000+ records. I have to investigate, design and compare efficient algorithmic approaches for locating a given registration number as the database grows. The solution must remain practical for both small and very large datasets, and any preprocessing performed on the records must be included in the efficiency analysis.

**How the twelve tasks are set in this scenario.** Every task is answered on the same student database. Each record is a `StudentRecord(reg_no, name, department, cgpa)`; `reg_no` is a unique 9-digit number of the form 19xxxxxxx (190,000,000 – 199,999,999, i.e. a key universe of U = 10,000,000 numbers). The records are stored in **arrival order**, so they are *not* sorted. Tasks 1–7 design and analyse three search strategies, Tasks 8–10 implement, measure and compare them on 1,000, 10,000, 100,000 and 1,000,000 records, Task 11 recommends one, and Task 12 re-evaluates it for 50,000 searches per hour with a daily batch of new records.

**Problem types identified.** Locating a registration number is the **searching** problem (find a search key in a set). Two of my strategies first **restructure** the data: sorting (Approach B) and hashing (Approach C), so the analysis always has two parts: the one-time preprocessing cost and the per-search cost. Task 12 adds a dynamic **dictionary** problem (search plus a daily batch of insertions).

**Evidence and reproducibility.** Every number in this report comes from the programs in `Task_8_Implementation_Testing/Source_Code/` (Appendix A): `student_records.py` generates the seeded datasets, `search_algorithms.py` holds the three algorithms with operation counters, `test_search_algorithms.py` runs the test cases (Appendix D), `run_experiments.py` produces the Task 9/10 measurements and graphs, and `design_challenge_simulation.py` simulates the Task 12 workload on 1,000,000 records. The diagram scripts are in Appendix B and every CSV file behind a table or graph is listed in Appendix C. Operation counts are the primary evidence; times are supporting evidence because other jobs were running on the same machine.

Table 1: Test environment

| Item | Value |
|---|---|
| Processor | 13th Gen Intel Core i5-13420H (8 cores, 12 threads) |
| Memory | 16 GB RAM |
| Operating system | Windows 11 Home (10.0.26200), 64-bit |
| Language | Python 3.13.11 (CPython, 64-bit); standard library only for the algorithms |
| Libraries | `random`, `math`, `time`, `gc`, `sys`, `csv`, `bisect`, `statistics`; matplotlib 3.10.8 for graphs only |
| Random seeds | 42 (datasets), n (query batch of each size), 2026 (daily batch), 1000 + hour (Task 12 queries) |
| Timer | `time.perf_counter`, garbage collector off while timing, minimum of R repeated runs |
| Datasets | nested: the first 1,000 records of the 1,000,000-record dataset are the 1,000-record dataset, etc. |

## Task 1 – Design the Algorithm [5 Marks]

> Design and propose at least three meaningfully different algorithmic strategies for locating a given registration number. The three approaches must represent distinct algorithmic strategies. Iterative and recursive implementations of the same underlying algorithm will not be considered as two different approaches.
> Your proposed approaches must include:
> - at least one iterative approach;
> - at least one recursive approach;
> - a clear explanation of the basic idea behind each approach;
> - pseudocode or an appropriate flowchart for each approach;
> - a brief justification for selecting each approach for investigation;
> - any preprocessing required by the approach, such as sorting or restructuring the data.
> You are expected to design and select the approaches independently. The appropriateness and diversity of the selected algorithmic strategies form part of the assessment.

**Evidence Expected**

> Three meaningfully different algorithmic strategies, supported by pseudocode/flowcharts, identification of the design strategy, preprocessing requirements, and justification for selecting each approach.

**Ans:**

### 1. The three strategies at a glance

I chose three strategies that use **increasing amounts of knowledge about the keys**: Approach A uses none (it only tests equality), Approach B uses the **order** of the keys, and Approach C uses the **arithmetic value** of the key to compute where the record is.

Table 2: The three proposed approaches

| | A – Sequential search | B – Binary search | C – Hash table |
|---|---|---|---|
| Design strategy | Brute force | Divide and conquer (decrease-by-half) | Space–time trade-off (transform and conquer) |
| Control structure | Iterative | Recursive | Iterative (hash, then one chain) |
| Structure searched | Unsorted array (as stored) | Sorted array of records | m chains, h(k) = k mod m |
| One-time setup | None | Own merge sort by `reg_no` | Insert every record once |
| Basic operation | `A[i].reg_no = key` | 3-way `key : A[mid].reg_no` | Chain comparison (+1 hash) |
| Expected search cost | (n + 1)/2 hit, n miss | ≈ log₂ n | ≈ 1 + α/2 hit, α miss (α ≤ 0.75) |

### 2. Approach A – Iterative sequential search (brute force)

**Basic idea.** Compare the key with the registration number of every record in the stored order, `A[0]`, `A[1]`, …, and stop at the first match. If the end of the list is reached, the student does not exist.

```
Algorithm SequentialSearch(A, n, key)
// A[0..n-1]: records in arrival order (unsorted); returns the record or NOT FOUND
1. for i = 0 to n-1 do
2.     if A[i].reg_no = key then             // basic operation: one key comparison
3.         return A[i]                       // successful search
4. return NOT FOUND                          // all n records compared
```

![Figure 1: Flowchart of Approach A – iterative sequential search](../../Task_1_Algorithm_Design/flowchart_A_sequential_search.png)

**Preprocessing:** none. The records are searched exactly as they arrive, so a new record is usable immediately (append in Θ(1)).

**Justification.** Sequential search is the baseline every other design must beat: it works on any list, needs no extra memory and no preprocessing, and it is the correct choice when the list is tiny or when only a handful of searches will ever be made. Investigating it tells me *how many searches* are needed before preprocessing pays for itself (Task 10).

### 3. Approach B – Recursive binary search on a sorted array (divide and conquer)

**Basic idea.** If the records are sorted by registration number, one comparison with the middle record `A[mid]` tells me which half can still contain the key; the other half is discarded. The function calls itself on the remaining half until the key is found or the range is empty. The work is **one** subproblem of half the size per call (Levitin calls this *decrease-by-a-constant-factor*, a special case of divide and conquer).

**Preprocessing:** the arrival-order records must be sorted once by `reg_no`. I implemented my own **merge sort** (also divide and conquer: sort both halves recursively, then merge them) with a comparison counter, so the preprocessing cost is measured, not assumed. It costs Θ(n log n) comparisons and a Θ(n) buffer.

```
Algorithm MergeSort(A, low, high)            // preprocessing for B: sort by reg_no
1. if low >= high then return                // 0 or 1 record: already sorted
2. mid = floor((low + high) / 2)
3. MergeSort(A, low, mid)
4. MergeSort(A, mid+1, high)
5. Merge(A, low, mid, high)

Algorithm Merge(A, low, mid, high)
1. copy A[low..high] into buffer B[low..high]
2. i = low;  j = mid + 1;  k = low
3. while i <= mid and j <= high do
4.     if B[i].reg_no <= B[j].reg_no then    // basic operation of the preprocessing
5.         A[k] = B[i];  i = i + 1
6.     else A[k] = B[j];  j = j + 1
7.     k = k + 1
8. copy the rest of B[i..mid] to A[k..]      // the rest of the right run is already in place
```

```
Algorithm BinSearch(A, key, low, high)       // A[low..high] sorted by reg_no
1. if low > high then return NOT FOUND       // base case: empty range
2. mid = floor((low + high) / 2)
3. if key = A[mid].reg_no then return A[mid] // one three-way comparison key : A[mid]
4. else if key < A[mid].reg_no then
5.     return BinSearch(A, key, low, mid-1)  // recurse on the left half only
6. else
7.     return BinSearch(A, key, mid+1, high) // recurse on the right half only
// first call: BinSearch(A, key, 0, n-1)
```

![Figure 2: Flowchart of Approach B – merge-sort preprocessing and recursive binary search](../../Task_1_Algorithm_Design/flowchart_B_recursive_binary_search.png)

**Justification.** Binary search is the classical way to exploit order, it is naturally recursive (the required recursive approach, analysed with recurrences in Tasks 6–7), and its guaranteed worst case of ⌊log₂ n⌋ + 1 comparisons is the strongest *worst-case* guarantee of the three. A sorted array also supports ordered reports (all students in a range of numbers), which the other two designs do not. Its weakness, the Θ(n log n) sorting cost, is exactly what the assignment asks me to include in the analysis.

### 4. Approach C – Hash table with separate chaining (space–time trade-off)

**Basic idea.** Instead of searching *for* the record, compute *where* it is: h(k) = k mod m maps a registration number to one of m buckets (m prime). Each bucket holds a short chain (list) of the records whose keys hash there. A search computes h(key) once and compares the key only with the records of that one chain. Choosing m ≥ n/0.75 keeps the **load factor** α = n/m ≤ 0.75, so a chain holds less than one record on average.

**Preprocessing:** build the table once: allocate m empty chains and insert every record (one hash computation each, plus a duplicate check along its chain). This costs Θ(n) expected time and Θ(n + m) extra memory. The table grows to the next prime ≥ 2m if more records arrive than it was sized for.

```
Algorithm BuildHashTable(R, n)               // preprocessing for C
1. m = smallest prime >= n / 0.75            // keeps alpha = n/m <= 0.75
2. T[0..m-1] = empty chains
3. for each record r in R do
4.     j = r.reg_no mod m                    // one hash computation
5.     if no record of chain T[j] has key r.reg_no then append r to T[j]
6. return T

Algorithm HashSearch(T, m, key)
1. j = key mod m                             // one hash computation
2. for each record p in chain T[j] do
3.     if p.reg_no = key then return p       // basic operation: one key comparison
4. return NOT FOUND
```

![Figure 3: Flowchart of Approach C – building the hash table and searching it](../../Task_1_Algorithm_Design/flowchart_C_hash_table.png)

**Justification.** Exact-match lookup by a unique numeric key is the textbook use of hashing; it is the only strategy whose expected cost does **not** grow with n. It also represents a different design philosophy (spend memory and a one-time build to buy speed), which lets me study a real trade-off. I wrote the table myself (division method with a prime m, separate chaining, resize when α > 0.75) instead of using Python's `dict`, so that every probe can be counted.

### 5. Why the three approaches are meaningfully different

Table 3: Diversity of the three strategies

| Question | A | B | C |
|---|---|---|---|
| What property of the key is used? | equality only | total order | arithmetic value (k mod m) |
| How much of the data is examined per search? | up to all n records | one path of ≈ log₂ n records | one chain of ≈ 1 record |
| Iterative or recursive | iterative loop | recursive (one call per level) | iterative |
| One-time preprocessing | none | Θ(n log n) merge sort | Θ(n) table build |
| Extra memory | none | sorted copy Θ(n) (+ Θ(n) buffer while sorting) | Θ(n + m) bucket array + chains |
| Supports ordered/range queries | no (needs a full scan) | yes | no |

They are not variants of one algorithm: A is brute force, B is divide and conquer on an ordered structure, and C replaces searching by address calculation. The pair "iterative vs recursive binary search" would not count as two approaches, so my only recursive approach (B) is matched with two *different* iterative strategies.

## Task 2 – Identify the Basic Operation [2 Marks]

> For each of the proposed algorithms, identify the basic operation that predominantly determines its execution time. Discuss:
> - what the basic operation is;
> - where it occurs in the algorithm;
> - why it is appropriate to use this operation for efficiency analysis;
> - how the number of times it executes may change as the input size (n) increases.
> Do not simply name an operation. You are expected to relate the selected operation to the behaviour of the algorithm.

**Ans:**

### 1. Approach A – the key comparison A[i].reg_no = key

**What and where.** Line 2 of `SequentialSearch`, inside the only loop (`comparisons += 1` in `sequential_search`). Everything else in one loop iteration (advancing `i`, fetching `A[i]`) is done exactly once per comparison.

**Why it is appropriate.** The loop body is the innermost, most frequently executed statement, and the loop runs once per comparison, so the running time is T(n) ≈ c·C(n) + c₀ with c the cost of one iteration. Counting comparisons is machine-independent and captures the behaviour that matters: *how many records the search must look at before it can stop*.

**How the count changes with n.** It depends on where the student is: i + 1 comparisons for the record at position i, n for an absent number. Both the average and the worst case grow **linearly**: ten times more students means ten times more comparisons (measured 496 → 4,967 → 51,226 → 480,558 for successful searches, Task 9).

### 2. Approach B – the three-way comparison key : A[mid].reg_no

**What and where.** Line 3 of `BinSearch` (one comparison of the key with the middle record; equal / smaller / larger decides the next step). In `binary_search_recursive` it is the single `counter.comparisons += 1` executed in every call that has a non-empty range. I count a three-way comparison as one operation (as Levitin does); a two-way implementation would perform at most two `<`/`==` tests per step, which changes only the constant.

**Why it is appropriate.** Each recursive call performs exactly one such comparison plus constant work (computing `mid`, one call). The number of calls equals the number of comparisons (+1 for the final empty call of an unsuccessful search), so the comparison count determines the running time.

**Preprocessing.** For merge sort the basic operation is the key comparison `B[i].reg_no <= B[j].reg_no` inside `Merge` (line 4); every comparison places exactly one record, and record moves are proportional to it.

**How the count changes with n.** Every comparison halves the remaining range, so the count grows with the **number of halvings**, at most ⌊log₂ n⌋ + 1: multiplying n by 10 adds only log₂ 10 ≈ 3.3 comparisons (measured 8.98 → 12.31 → 15.64 → 18.87). The merge-sort count grows as n log₂ n.

### 3. Approach C – the key comparison along one chain (plus one hash computation)

**What and where.** Line 3 of `HashSearch` (`p.reg_no = key`, `counter.comparisons += 1` in `StudentHashTable.search`). Every search also performs exactly **one** hash computation `key mod m` (line 1), counted separately as `hash_computations`.

**Why it is appropriate.** The hash computation is a constant cost paid once per search; the only part whose count can vary is the scan of the chain, so the chain comparisons are what distinguish a good table (short chains) from a bad one (long chains). The total work of a search is 1 hash + (chain comparisons).

**Preprocessing.** Building the table costs one hash computation per record plus the duplicate-check comparisons along its chain; both are counted.

**How the count changes with n.** Because m grows with n (m ≥ n/0.75), the expected chain length α = n/m stays ≤ 0.75 for every n, so the count stays **constant** (measured 1.34, 1.39, 1.33, 1.32 comparisons per successful search). Only an adversarial key set that puts many keys into one chain would make it grow (Task 4).

### 4. Summary

Table 4: The basic operation of each algorithm and how its count grows

| Algorithm | Basic operation | Where | Count as n grows |
|---|---|---|---|
| A: sequential search | `A[i].reg_no = key` | loop body | linear: ≈ n/2 (hit), n (miss) |
| B: merge sort (preprocessing) | `B[i].reg_no <= B[j].reg_no` | `Merge` loop | n log₂ n − Θ(n) |
| B: recursive binary search | three-way `key : A[mid].reg_no` | once per recursive call | logarithmic: ≤ ⌊log₂ n⌋ + 1 |
| C: hash build (preprocessing) | `k mod m` + chain comparison | once per inserted record | linear: ≈ n(1 + α/2) |
| C: hash search | chain comparison `p.reg_no = key` (+1 hash) | chain loop | constant: ≈ 1 + α/2 (hit), α (miss) |

I deliberately do not use wall-clock time as the measure of efficiency: it depends on the processor, the Python interpreter and the other jobs running at the same moment, while the operation counts depend only on the algorithm and the input.

## Task 3 – Derive the Time-Complexity Function Mathematically [6 Marks]

> Derive the time-complexity function for each proposed approach using mathematical analysis. Discuss:
> - the input size (n);
> - the number of times the basic operation executes;
> - how the operation count changes with n;
> - the mathematical expression representing the running time;
> - any preprocessing cost involved;
> - the overall cost when preprocessing and searching are considered together.
> You must show the mathematical reasoning leading to the complexity result. Merely stating that an algorithm is O(n), O(log n), etc., will not receive full credit.

**Ans:**

### 1. Input size and cost model

- **Input size n** = number of student records in the database (the registration numbers are fixed-size 9-digit integers, so one comparison costs constant time).
- **q** = number of searches served by one preprocessing (q = 1,200,000 per day in Task 12).
- **p** = probability that a searched registration number exists (p = ½ in Task 9 and p = 0.8 in Task 12).
- Successful searches are for a uniformly random stored student, so positions in the arrival order are uniformly distributed.
- C(n) = number of basic operations; T(n) = c·C(n) + lower-order terms, where c is the machine cost of one basic operation with its loop overhead.

### 2. Approach A – sequential search

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

### 3. Approach B – merge-sort preprocessing + recursive binary search

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

### 4. Approach C – hash table with separate chaining

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

### 5. Preprocessing and searching together

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

## Task 4 – Analyse Best, Average and Worst-Case Behaviour [4 Marks]

> Discuss, wherever applicable:
> - what input condition produces the best case;
> - the average case;
> - the worst case;
> - how the number of operations changes in each case;
> - why these differences occur.
> Do not simply provide a table containing complexity values. Explain the conditions that lead to each case, supported by mathematical reasoning.

**Ans:**

### 1. Approach A – sequential search

**Best case.** The searched student is the *first record stored* (position 0). The loop stops after **one** comparison: C<sub>best</sub>(n) = 1, independent of n. Test TC05 confirms it: the first stored record (196394267) was found with 1 comparison.

**Worst case.** Two input conditions: the student is the *last record stored*, or the registration number *does not exist*. In both, every record must be compared: C<sub>worst</sub>(n) = n. Tests TC06 (last record, 15 comparisons for n = 15) and TC11–TC13 (absent keys below the minimum, above the maximum and in a gap, 15 comparisons each) confirm it; in the experiments every unsuccessful search cost exactly n (1,000; 10,000; 100,000; 1,000,000).

**Average case.** For a uniformly random stored student, C<sub>hit</sub>(n) = (n + 1)/2 (Task 3, §2); with success probability p, C<sub>avg</sub> = p(n + 1)/2 + (1 − p)n. Measured averages: 496.25, 4,966.63, 51,226.36 and 480,558.07 (theory 500.5, 5,000.5, 50,000.5, 500,000.5).

**Why.** The records are in arrival order, which has no relation to the registration numbers, so a comparison with A[i] gives no information about where else the key could be. The algorithm can only rule out one record per comparison; the position of the key alone decides the cost, and an absent key can only be confirmed after looking at everything.

### 2. Approach B – recursive binary search

**Best case.** The key is the record at the **first middle position** `A[⌊(n − 1)/2⌋]`; it is found by the first three-way comparison: C<sub>best</sub>(n) = 1 (test TC07: the middle of the sorted 15 records, 1 comparison).

**Worst case.** The key is stored at a **deepest node** of the decision tree, or it is **absent** (any gap). Every comparison discards half and the search continues until one record (or none) is left: C<sub>worst</sub>(n) = ⌊log₂ n⌋ + 1 (4 for n = 15: tests TC08, TC09, TC11–TC13; 10, 14, 17 and 20 for the four experimental sizes, Table 10).

**Average case.** Figure 4 shows why the average is close to the worst case: level d of the decision tree contains 2<sup>d−1</sup> keys, so about half of all keys sit on the deepest level. For n = 15: (1·1 + 2·2 + 3·4 + 4·8)/15 = 49/15 = 3.27 comparisons, against a worst case of 4. In general C<sub>hit</sub>(n) ≈ log₂ n − 1 and every unsuccessful search costs ⌊log₂ n⌋ or ⌊log₂ n⌋ + 1 (all 16 gaps of the n = 15 tree cost 4).

![Figure 4: Decision tree of the recursive binary search for n = 15 – depth = comparisons](../../Task_4_Case_Analysis/binary_search_decision_tree.png)

**Why.** The cost depends only on the *position of the key in sorted order*, never on the values themselves, and the halving bounds the depth of the tree by log₂ n. Best and worst differ by a factor of only about log₂ n, not n.

**Preprocessing (merge sort).** The input order only changes the constant: the best case is input that is already sorted (each merge stops after the left run, ≈ (n/2) log₂ n comparisons), the worst case is when every merge alternates between the runs (n log₂ n − n + 1), and random input averages ≈ n log₂ n − 1.25n. All three are Θ(n log n), because merge sort always splits into halves regardless of the data. My random datasets needed 8,744 / 120,491 / 1,536,197 / 18,674,803 comparisons, within 0.4% of n log₂ n − 1.25n and below the worst-case bound (Table 15).

### 3. Approach C – hash table

**Best case.** The key's bucket h(key) is empty (unsuccessful search: 1 hash, **0 comparisons**, test TC11 and TC13) or the key is the first record of its chain (successful: 1 hash + **1 comparison**, tests TC02–TC10).

**Average case.** Under uniform hashing a successful search costs 1 + α/2 − α/(2n) comparisons and an unsuccessful one α (Task 3, §4). Because the table is resized to keep α ≤ 0.75, both are **constants**: ≤ 1.375 and ≤ 0.75. Measured: 1.32–1.39 (hit) and 0.62–0.76 (miss) at all four sizes.

**Worst case.** All n keys fall into the **same bucket**, e.g. keys that are all congruent modulo m. The table degenerates into one linked list and a search costs n comparisons, Θ(n), exactly like sequential search; building such a table costs Θ(n²) because of the duplicate checks (0 + 1 + … + (n − 1)). Property test P5 builds this case on purpose with the 1,000 keys k = 190,000,000 + i·m: the chain length was 1,000 and both a hit on the last key and a miss cost 1,000 comparisons.

**Why the worst case does not occur here.** Registration numbers are assigned by the university, not chosen by an adversary, and the division method with a prime m spreads them evenly. The longest chain I observed was 5, 7, 8 and 6 records at the four sizes (Table 18), consistent with the expected maximum chain length Θ(log n / log log n). If adversarial keys were a concern, a randomly chosen (universal) hash function would make the expected cost Θ(1) for *every* key set.

### 4. Summary of the cases

Table 6: Operation counts in the three cases (search only; n records, α = n/m ≤ 0.75)

| Approach | Best case: condition → count | Average case | Worst case: condition → count |
|---|---|---|---|
| A sequential search | key at position 0 → 1 | hit (n + 1)/2; miss n | key last or absent → n |
| B binary search | key at first mid → 1 | hit ≈ log₂ n − 1; miss ≈ log₂ n | deepest or absent → ⌊log₂ n⌋+1 |
| C hash search | empty chain → 0; key first → 1 | hit 1 + α/2; miss α | one chain holds all → n |
| B merge sort | sorted input → ≈ (n/2) log₂ n | ≈ n log₂ n − 1.25n | n log₂ n − n + 1 |
| C table build | no collisions → n hashes | n(1 + α/2) | all collide → n + n(n−1)/2 |

The differences have one common cause: **how much each comparison can eliminate.** A comparison in A eliminates one record, so the cost depends linearly on the key's position. A comparison in B eliminates half of the remaining records, so the cost depends only on the depth of the key in a balanced tree. In C the hash computation eliminates all records except one chain; the remaining cost depends on how evenly the keys are spread, which is a property of the hash function and the key set, not of n.

## Task 5 – Perform Asymptotic Analysis [3 Marks]

> Express and compare the growth behaviour using appropriate asymptotic notation. Discuss:
> - appropriate use of O, Ω and/or Θ;
> - how each algorithm behaves as n becomes very large;
> - how the growth rates differ;
> - what the growth behaviour means when the dataset increases from 1,000 to 1,000,000+ records.
> Interpret in the context of the application.

**Ans:**

### 1. The notations I use

- t(n) ∈ **O**(g(n)) if there are constants c > 0 and n₀ with t(n) ≤ c·g(n) for all n ≥ n₀ (upper bound, used for "never worse than").
- t(n) ∈ **Ω**(g(n)) if t(n) ≥ c·g(n) for all n ≥ n₀ (lower bound, "never better than").
- t(n) ∈ **Θ**(g(n)) if both hold (tight bound, the exact growth class).

I use Θ for each *case* (best, average, worst) because each case is a single function of n, and O/Ω for statements about the algorithm over *all* inputs.

### 2. Asymptotic classes, with the constants

**A – sequential search.** Worst case C(n) = n ∈ Θ(n). Average (n + 1)/2 ∈ Θ(n): for all n ≥ 1, ½·n ≤ (n + 1)/2 ≤ 1·n (c₁ = ½, c₂ = 1, n₀ = 1). Best case 1 ∈ Θ(1). Over all inputs sequential search is therefore **O(n) and Ω(1)**; it is *not* Θ(n) for every input, only for the worst and average cases.

**B – binary search.** Worst case ⌊log₂ n⌋ + 1 ∈ Θ(log n): for n ≥ 2, log₂ n < ⌊log₂ n⌋ + 1 ≤ log₂ n + 1 ≤ 2 log₂ n (c₁ = 1, c₂ = 2, n₀ = 2). Average ≈ log₂ n − 1 ∈ Θ(log n). Best case Θ(1). Over all inputs: **O(log n) and Ω(1)**. Preprocessing n log₂ n − n + 1 ∈ Θ(n log n): it is ≤ n log₂ n, and for n ≥ 4 it is ≥ ½ n log₂ n because ½ n log₂ n ≥ n − 1 when log₂ n ≥ 2.

**C – hash table.** Expected search 1 + α/2 ≤ 1.375 and α ≤ 0.75, so both are **Θ(1) expected**; the worst case over adversarial key sets is Θ(n), so over all inputs the search is **O(n)** and only Θ(1) *in expectation*. Build: Θ(n) expected (n hash computations + ≤ 0.375n comparisons), O(n²) worst case.

Table 7: Asymptotic summary (search cost per query, plus preprocessing)

| Approach | Best case | Average case | Worst case | Preprocessing cost | Extra space |
|---|---|---|---|---|---|
| A sequential | Θ(1) | Θ(n) | Θ(n) | none | Θ(1) |
| B binary (recursive) | Θ(1) | Θ(log n) | Θ(log n) | Θ(n log n) | Θ(n) + Θ(log n) stack |
| C hash table | Θ(1) | Θ(1) expected | Θ(n) | Θ(n) expected | Θ(n + m) = Θ(n) |

### 3. How the growth rates differ as n becomes very large

The limits of the ratios order the three classes strictly:

- lim<sub>n→∞</sub> log₂ n / n = lim (1/(n ln 2)) / 1 = 0 (L'Hôpital), so log n ∈ o(n): binary search grows **strictly slower** than sequential search.
- lim<sub>n→∞</sub> 1 / log₂ n = 0, so Θ(1) ⊂ o(log n): hashing grows strictly slower than binary search.
- For preprocessing, lim n / (n log n) = lim 1/log n = 0: building a hash table grows strictly slower than sorting.

The practical meaning: **doubling the database** doubles the work of A, adds exactly **one** comparison to B, and changes nothing for C.

### 4. From 1,000 to 1,000,000 records (×1,000)

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

## Task 6 – Formulate the Recurrence Relation [3 Marks]

> For the recursive approach, formulate a recurrence relation directly from the behaviour of the algorithm. Clearly identify:
> - the input size of the original problem;
> - the size of the recursive subproblem;
> - the number of recursive calls;
> - the work performed outside the recursive call;
> - the base case;
> - how these components lead to the recurrence relation.
> The recurrence must be derived from your algorithm, rather than simply writing a known recurrence formula.

**Ans:**

### 1. The algorithm the recurrence is derived from

The recursive approach is `binary_search_recursive(sorted_records, key, low, high, counter)` in `search_algorithms.py` (pseudocode `BinSearch`, Task 1). One activation does the following:

```
1. counter.calls += 1
2. if low > high: return None                          # base case: empty range
3. mid = (low + high) // 2
4. mid_key = sorted_records[mid].reg_no
5. counter.comparisons += 1                            # ONE three-way comparison key : A[mid]
6. if key == mid_key: return sorted_records[mid]       # found: no further call
7. if key < mid_key: return binary_search_recursive(..., low, mid - 1, ...)
8. return binary_search_recursive(..., mid + 1, high, ...)
```

### 2. The components, read from the code

**Input size of the original problem.** The problem is described by the range A[low..high]; its size is **n = high − low + 1**. The first call has low = 0, high = n − 1, i.e. the whole database.

**Size of the recursive subproblem.** With mid = ⌊(low + high)/2⌋:

- left half A[low..mid − 1] has size mid − low = ⌊(low + high)/2⌋ − low = ⌊(high − low)/2⌋ = **⌊(n − 1)/2⌋**;
- right half A[mid + 1..high] has size high − mid = (n − 1) − ⌊(n − 1)/2⌋ = ⌈(n − 1)/2⌉ = **⌊n/2⌋**.

The larger subproblem therefore has size ⌊n/2⌋ (for n = 1,000,000 the halves are 499,999 and 500,000).

**Number of recursive calls.** Lines 7 and 8 are alternatives (`if … return`), so an activation makes **at most one** recursive call, and none when the key is found on line 6. This is the decisive difference from merge sort, which makes two calls.

**Work outside the recursive call.** Lines 1–6: computing mid, reading A[mid] and **one** three-way comparison, i.e. f(n) = 1 basic operation (Θ(1) time), independent of n.

**Base case.** n = 0 (low > high): the function returns NOT FOUND after **0** comparisons, so C(0) = 0. (A size-1 range is not a base case in my code: it makes one comparison and, if unsuccessful, one call on an empty range; this gives C(1) = C(0) + 1 = 1.)

### 3. The recurrences

Combining "comparisons of this activation (1)" + "comparisons of the one recursive call on the larger half (worst case)":

**C<sub>worst</sub>(n) = C<sub>worst</sub>(⌊n/2⌋) + 1 for n ≥ 1,  C<sub>worst</sub>(0) = 0**

Table 9: Components of the recurrence, taken from the code

| Component | Value in `binary_search_recursive` | Contribution to the recurrence |
|---|---|---|
| Input size | n = high − low + 1 | C(n) |
| Subproblem size | ⌊(n − 1)/2⌋ (left) or ⌊n/2⌋ (right) | worst case uses ⌊n/2⌋ |
| Number of recursive calls | at most 1 (left **or** right) | coefficient a = 1 |
| Work outside the call | one three-way comparison + Θ(1) arithmetic | + 1 |
| Base case | n = 0 (low > high): 0 comparisons | C(0) = 0 |

Related recurrences from the same reasoning:

- **Best case:** the key is A[mid] in the first activation: C<sub>best</sub>(n) = 1 for n ≥ 1 (no recursive call).
- **Running time:** T(n) = T(⌊n/2⌋) + c for n ≥ 1, T(0) = d, where c is the constant cost of lines 1–6.
- **Recursion depth / stack space:** D(n) = D(⌊n/2⌋) + 1, D(0) = 1 frame — the same form as C(n).
- **Total over all n successful searches** (used for the exact average in Task 3): every search makes the root comparison, then ⌊(n − 1)/2⌋ of them continue left and ⌈(n − 1)/2⌉ continue right, so S(n) = n + S(⌊(n − 1)/2⌋) + S(⌈(n − 1)/2⌉), S(0) = 0.

### 4. Recurrence of the recursive preprocessing (merge sort)

`_merge_sort(a, aux, low, high)` sorts A[low..mid] (size ⌈n/2⌉) and A[mid + 1..high] (size ⌊n/2⌋) with **two** recursive calls and then merges them with at most n − 1 comparisons; a range of 0 or 1 record is the base case with 0 comparisons:

**C<sub>sort</sub>(n) = C<sub>sort</sub>(⌈n/2⌉) + C<sub>sort</sub>(⌊n/2⌋) + (n − 1) for n ≥ 2,  C<sub>sort</sub>(1) = 0,** which for n = 2ᵏ is C<sub>sort</sub>(n) = 2C<sub>sort</sub>(n/2) + n − 1.

## Task 7 – Solve the Recurrence Relation [4 Marks]

> Solve it using an appropriate method (substitution, iteration, Master Theorem, or another technique). Discuss:
> - why the selected method is applicable;
> - the steps;
> - the resulting complexity;
> - what the result indicates about the behaviour of the recursive algorithm as n increases.
> Show the analytical process. (Showing two methods, e.g. backward substitution AND Master Theorem, is a plus.)

**Ans:**

I solve C(n) = C(⌊n/2⌋) + 1, C(0) = 0 (so C(1) = 1) with three methods: backward substitution (exact closed form for powers of two), the Master Theorem (growth class), and the substitution method by induction (exact closed form for **every** n). Then I solve the merge-sort recurrence and check all closed forms against the counted comparisons.

### 1. Method 1 – Backward substitution (iteration)

**Why it applies.** The recurrence has a single recursive term whose argument halves, so repeatedly substituting the recurrence into itself produces a simple pattern. For n = 2ᵏ the floors disappear (⌊2ᵏ/2⌋ = 2<sup>k−1</sup>).

**Steps.** Let n = 2ᵏ:

C(2ᵏ) = C(2<sup>k−1</sup>) + 1

= [C(2<sup>k−2</sup>) + 1] + 1 = C(2<sup>k−2</sup>) + 2

= [C(2<sup>k−3</sup>) + 1] + 2 = C(2<sup>k−3</sup>) + 3

= …

= C(2<sup>k−i</sup>) + i  (general pattern after i substitutions)

Choose i = k to reach the known value C(2⁰) = C(1) = 1:

C(2ᵏ) = C(1) + k = 1 + k, and since k = log₂ n: **C(n) = log₂ n + 1** for n = 2ᵏ.

By the smoothness rule (log n is a smooth function and C is non-decreasing), the result extends to all n: C(n) ∈ Θ(log n).

### 2. Method 2 – Master Theorem

**Why it applies.** The recurrence has the form T(n) = a·T(n/b) + f(n) with a = 1 ≥ 1 recursive call, b = 2 > 1, and f(n) = 1 asymptotically positive; floors in the argument do not change the result.

**Steps.**

- a = 1, b = 2, f(n) = 1 = Θ(n⁰), so d = 0.
- n<sup>log<sub>b</sub> a</sup> = n<sup>log₂ 1</sup> = n⁰ = 1.
- Compare f(n) with n<sup>log<sub>b</sub> a</sup>: f(n) = Θ(1) = Θ(n<sup>log<sub>b</sub> a</sup>), i.e. a = b<sup>d</sup> (1 = 2⁰). This is **Case 2**.
- Case 2 gives T(n) = Θ(n<sup>log<sub>b</sub> a</sup> · log n) = Θ(n⁰ log n) = **Θ(log n)**.
- The regularity condition a·f(n/b) ≤ c·f(n) is only required in Case 3, so no check is needed here.

### 3. Method 3 – Substitution method (proof by induction for every n)

**Claim:** C(n) = ⌊log₂ n⌋ + 1 for all n ≥ 1.

**Basis:** n = 1: C(1) = C(0) + 1 = 1 = ⌊log₂ 1⌋ + 1. ✓

**Inductive step:** let n ≥ 2 and assume the claim for all 1 ≤ m < n. Choose j with 2ʲ ≤ n < 2<sup>j+1</sup>, so ⌊log₂ n⌋ = j ≥ 1. Then 2<sup>j−1</sup> ≤ ⌊n/2⌋ < 2ʲ, so ⌊log₂ ⌊n/2⌋⌋ = j − 1. Because 1 ≤ ⌊n/2⌋ < n the hypothesis applies:

C(n) = C(⌊n/2⌋) + 1 = (⌊log₂ ⌊n/2⌋⌋ + 1) + 1 = (j − 1) + 2 = j + 1 = **⌊log₂ n⌋ + 1**. ✓

This is the exact worst-case number of three-way comparisons for every database size, and it agrees with the backward substitution for n = 2ᵏ.

### 4. Recursion tree, and the merge-sort recurrence

**Binary search.** The recursion tree is a single path (one recursive call per level): sizes n, ⌊n/2⌋, ⌊n/4⌋, …, 1, with cost 1 on each of the ⌊log₂ n⌋ + 1 levels and 0 at the empty base case. Summing the levels gives ⌊log₂ n⌋ + 1 again (Figure 5a, n = 16: 5 levels → 5 comparisons).

**Merge sort, backward substitution** (n = 2ᵏ, C(n) = 2C(n/2) + n − 1, C(1) = 0):

C(2ᵏ) = 2C(2<sup>k−1</sup>) + 2ᵏ − 1

= 2[2C(2<sup>k−2</sup>) + 2<sup>k−1</sup> − 1] + 2ᵏ − 1 = 4C(2<sup>k−2</sup>) + 2·2ᵏ − (1 + 2)

= 8C(2<sup>k−3</sup>) + 3·2ᵏ − (1 + 2 + 4)

= …

= 2ⁱ C(2<sup>k−i</sup>) + i·2ᵏ − (2ⁱ − 1)

With i = k: C(2ᵏ) = 2ᵏ·C(1) + k·2ᵏ − 2ᵏ + 1 = **n log₂ n − n + 1**.

**Merge sort, Master Theorem:** a = 2, b = 2, f(n) = n − 1 = Θ(n¹), n<sup>log₂ 2</sup> = n¹ → f(n) = Θ(n<sup>log<sub>b</sub> a</sup>), Case 2 → **Θ(n log n)**.

**Merge sort, recursion tree:** level i has 2ⁱ merges of size n/2ⁱ, each costing n/2ⁱ − 1, so the level costs n − 2ⁱ; summing over the log₂ n merging levels gives n log₂ n − (2<sup>log₂ n</sup> − 1) = n log₂ n − n + 1 (Figure 5b, n = 16: 15 + 14 + 12 + 8 = 49 = 16·4 − 16 + 1).

![Figure 5: Recursion trees for n = 16 – (a) recursive binary search, (b) merge-sort preprocessing](../../Task_7_Recurrence_Solution/recursion_trees.png)

### 5. Verification against the counted comparisons

I checked the solutions against the counters in the real code. Test P3 searched every key and every gap for each n from 1 to 200: the maximum count equalled ⌊log₂ n⌋ + 1 for all 200 sizes, and the total over all successful searches equalled the recurrence S(n) exactly (P3b). Test P4 confirmed that merge sort never exceeded n⌈log₂ n⌉ − 2<sup>⌈log₂ n⌉</sup> + 1. For the four experimental sizes I searched **every stored key once**:

Table 10: Closed forms against the counted comparisons (exhaustive search of every stored key; exhaustive_verification.csv)

| Number of records (n) | Max counted | ⌊log₂ n⌋ + 1 | Average counted | S(n)/n (recurrence) | Merge sort counted | Merge sort worst bound |
|---|---|---|---|---|---|---|
| 1,000 | 10 | 10 | 8.9870 | 8.9870 | 8,744 | 8,977 |
| 10,000 | 14 | 14 | 12.3631 | 12.3631 | 120,491 | 123,617 |
| 100,000 | 17 | 17 | 15.6895 | 15.6895 | 1,536,197 | 1,568,929 |
| 1,000,000 | 20 | 20 | 18.9514 | 18.9514 | 18,674,803 | 18,951,425 |

The agreement is exact for binary search, as it must be for a deterministic algorithm.

### 6. What the result means

C(n) = ⌊log₂ n⌋ + 1 = Θ(log n) means that **each doubling of the database adds exactly one comparison** and one stack frame. Going from 1,000 to 1,000,000 students (×1,000 ≈ 2¹⁰) adds only 10 comparisons (10 → 20). The recursion is also safe in Python: at n = 10⁶ the depth is at most 21 frames, far below the default limit of 1,000 frames, which would only be reached for n ≈ 2⁹⁹⁹. The merge-sort result Θ(n log n) says the preprocessing grows slightly faster than linearly; it is paid once and then shared by all later searches (Task 10, §5).

## Task 8 – Implement and Test the Algorithms [4 Marks]

> Implement all approaches and test their behaviour using datasets of approximately 1,000 → 10,000 → 100,000 → 1,000,000 records. Ensure that:
> - all algorithms produce the correct result;
> - the same or equivalent datasets are used for comparison;
> - testing conditions are kept reasonably consistent;
> - appropriate test cases are included;
> - the implementation corresponds to the algorithms analysed.

**Evidence Expected**

> Working implementations together with a clearly described and reproducible testing procedure.

**Ans:**

### 1. Implementation overview

All algorithm cores are hand-written pure Python (no library search, sort or dictionary inside them), so that every basic operation can be counted with an `OpCounter`.

Table 11: Programs (Task_8_Implementation_Testing/Source_Code; all ran with exit code 0)

| File | Purpose | Run time |
|---|---|---|
| `student_records.py` | `StudentRecord`, seeded dataset generator (unique 19xxxxxxx keys, arrival order), query batches | < 1 s |
| `search_algorithms.py` | A `sequential_search`; B `merge_sort_records` + `binary_search_recursive`; C `StudentHashTable` (build/insert/search/rehash); `merge_sorted_batch` for Task 12; demo trace | < 1 s |
| `test_search_algorithms.py` | 39 checks: functional cases, properties, bulk validation on all four sizes | 14.9 s |
| `run_experiments.py` | Task 9/10 measurements, 10 CSV tables, 6 graphs | 95.4 s |
| `design_challenge_simulation.py` | Task 12 simulation on 1,000,000 records, 4 CSV tables, 2 graphs | 90.9 s |

**How to run** (from `Task_8_Implementation_Testing/Source_Code`, Python 3.13 with matplotlib): `py -3 search_algorithms.py` (demo), `py -3 test_search_algorithms.py`, `py -3 run_experiments.py`, `py -3 design_challenge_simulation.py`. All randomness is seeded, so every run reproduces the same datasets, queries and operation counts.

### 2. The implementation corresponds to the analysed algorithms

Table 12: Pseudocode line → code (search_algorithms.py)

| Pseudocode (Task 1) | Code | Counted as |
|---|---|---|
| `SequentialSearch` line 2: `A[i].reg_no = key` | `sequential_search`: `comparisons += 1; if record.reg_no == key` | `comparisons` |
| `MergeSort` lines 1–5 (two recursive calls) | `_merge_sort(a, aux, low, high, counter)` | – |
| `Merge` line 4: `B[i].reg_no <= B[j].reg_no` | `_merge`: `comparisons += 1; if aux[i].reg_no <= aux[j].reg_no` | `comparisons`, `moves` |
| `BinSearch` line 1: base case `low > high` | `binary_search_recursive`: `if low > high: return None` | `calls` |
| `BinSearch` line 3: three-way comparison | `counter.comparisons += 1`, then `==` / `<` on `mid_key` | `comparisons` |
| `BuildHashTable` lines 1–5 | `StudentHashTable.__init__` (prime m ≥ n/0.75), `build`, `insert` | `hash_computations`, `comparisons` |
| `HashSearch` lines 1–3 | `StudentHashTable.search`: `_hash`, loop over one chain | `hash_computations`, `comparisons` |

The demo in `search_algorithms.py` prints a trace of each approach on 15 records (Figures 20–21): sequential search needs 1 comparison for the first stored record and 15 for the last; merge sort sorts the 15 records with 38 comparisons (worst-case bound 45); the recursive binary search trace shows the four calls (low, high, mid) for a present key and the final empty-range call for an absent one; the hash table with m = 23 shows its chains.

### 3. Datasets and the reproducible testing procedure

1. **Data.** `generate_records(n)` draws unique registration numbers uniformly from 190,000,000–199,999,999 (seed 42), re-drawing a number that was already issued, and attaches a name, department and CGPA. Because each record depends only on the random stream before it, the datasets are **nested**: the 1,000-record set is the first 1,000 records of the 10,000-record set, and so on. All three approaches always receive *the same list* for a given n.
2. **Queries.** For each n, `make_query_batch` draws one batch of 500 stored keys (uniform positions) and 500 absent keys (uniform numbers in 19xxxxxxx that are not stored), with seed n. All three approaches search the same batch; sequential search at n = 1,000,000 uses the first 100 + 100 keys of it, because one search takes 25–55 ms in Python.
3. **Correctness reference.** Every result is compared with a Python `dict` built from the same records (used only for checking). A successful search must return the *identical* record object; an unsuccessful one must return `None`.
4. **Consistent conditions.** One process, one machine (Table 1), the same Python version; the garbage collector is switched off while timing; each timing is the minimum of several runs; operation counts are taken in a separate counting pass and do not depend on timing.

### 4. Test cases

Table 13: Functional test cases (actual = result(comparisons) for A / B / C; all 13 PASS, Appendix D)

| Test case | Key searched (reg. no.) | Expected result | A: sequential search | B: binary search | C: hash table search |
|---|---|---|---|---|---|
| TC01 empty dataset (n = 0) | 192425324 | not found | none(0) | none(0) | none(0) |
| TC02 single record, present | 192425324 | found | found(1) | found(1) | found(1) |
| TC03 single, absent smaller | 192425323 | not found | none(1) | none(1) | none(0) |
| TC04 single, absent larger | 192425325 | not found | none(1) | none(1) | none(0) |
| TC05 first stored record | 196394267 | found | found(1) | found(4) | found(1) |
| TC06 last stored record | 191711386 | found | found(15) | found(4) | found(1) |
| TC07 middle of sorted order | 196356844 | found | found(13) | found(1) | found(1) |
| TC08 smallest reg. number | 190265359 | found | found(4) | found(4) | found(1) |
| TC09 largest reg. number | 199572130 | found | found(7) | found(4) | found(1) |
| TC10 random present (seed 1) | 194219218 | found | found(3) | found(3) | found(1) |
| TC11 absent, below minimum | 189999999 | not found | none(15) | none(4) | none(0) |
| TC12 absent, above maximum | 200000000 | not found | none(15) | none(4) | none(2) |
| TC13 absent, in a gap (A[6] + 1) | 195362281 | not found | none(15) | none(4) | none(0) |

TC05–TC13 use the first 15 records of the seed-42 dataset. Five further checks assert the *operation counts* of the cases: sequential best case = 1 (TC05), sequential worst successful = n = 15 (TC06), binary best case = 1 (TC07), sequential unsuccessful = n (TC11) and binary unsuccessful ≤ ⌊log₂ 15⌋ + 1 = 4 (TC11). Duplicate registration numbers are impossible by construction (the generator re-draws them) and the hash table refuses to store a key twice.

**Property tests:** P1 re-inserting an existing key replaces the record and keeps the count at 1,000 (no duplicates); P2 merge sort equals Python's `sorted()` for n = 15, 1,000 and 10,000 and leaves the input list untouched; P3 for every n from 1 to 200, searching every key and every gap never exceeds ⌊log₂ n⌋ + 1 comparisons and the maximum is reached; P3b the total successful comparisons equal the recurrence S(n); P4 merge sort never exceeds n⌈log₂ n⌉ − 2<sup>⌈log₂ n⌉</sup> + 1; P5 the adversarial hash case (1,000 keys congruent modulo m) produces one chain of 1,000 and 1,000 comparisons; P6 a table created for 10 records grows through 7 rehashes to 2,000 records and α never exceeds 0.75 (max 0.749).

Table 14: Bulk validation on the four required sizes (same queries for every approach)

| Number of records (n) | A: correct answers | B: correct answers | C: correct answers | A invariant | B: every search ≤ | C: load factor α |
|---|---|---|---|---|---|---|
| 1,000 | 1,000/1,000 | 1,000/1,000 | 1,000/1,000 | hit = pos+1, miss = n | 10 | 0.735 |
| 10,000 | 1,000/1,000 | 1,000/1,000 | 1,000/1,000 | hit = pos+1, miss = n | 14 | 0.750 |
| 100,000 | 1,000/1,000 | 1,000/1,000 | 1,000/1,000 | hit = pos+1, miss = n | 17 | 0.750 |
| 1,000,000 | 200/200 | 1,000/1,000 | 1,000/1,000 | hit = pos+1, miss = n | 20 | 0.750 |

Result: **39/39 tests passed** (Figure 22). Every approach returned the correct record for every present key and `None` for every absent key at every size.

### 5. Source code

The core algorithms, the data generator and the test program are shown below; the experiment and simulation programs are listed in full in Appendix A, and screenshots of all eight programs are in `Report/Source_Code_Screenshots/`.

![Figure 6: Source code – search_algorithms.py (part 1 of 6)](../Source_Code_Screenshots/search_algorithms_code_1.png)

![Figure 7: Source code – search_algorithms.py (part 2 of 6)](../Source_Code_Screenshots/search_algorithms_code_2.png)

![Figure 8: Source code – search_algorithms.py (part 3 of 6)](../Source_Code_Screenshots/search_algorithms_code_3.png)

![Figure 9: Source code – search_algorithms.py (part 4 of 6)](../Source_Code_Screenshots/search_algorithms_code_4.png)

![Figure 10: Source code – search_algorithms.py (part 5 of 6)](../Source_Code_Screenshots/search_algorithms_code_5.png)

![Figure 11: Source code – search_algorithms.py (part 6 of 6)](../Source_Code_Screenshots/search_algorithms_code_6.png)

![Figure 12: Source code – student_records.py (part 1 of 3)](../Source_Code_Screenshots/student_records_code_1.png)

![Figure 13: Source code – student_records.py (part 2 of 3)](../Source_Code_Screenshots/student_records_code_2.png)

![Figure 14: Source code – student_records.py (part 3 of 3)](../Source_Code_Screenshots/student_records_code_3.png)

![Figure 15: Source code – test_search_algorithms.py (part 1 of 4)](../Source_Code_Screenshots/test_search_algorithms_code_1.png)

![Figure 16: Source code – test_search_algorithms.py (part 2 of 4)](../Source_Code_Screenshots/test_search_algorithms_code_2.png)

![Figure 17: Source code – test_search_algorithms.py (part 3 of 4)](../Source_Code_Screenshots/test_search_algorithms_code_3.png)

![Figure 18: Source code – test_search_algorithms.py (part 4 of 4)](../Source_Code_Screenshots/test_search_algorithms_code_4.png)

### 6. Execution output

![Figure 19: Execution output of student_records.py – sample records, uniqueness and prefix property](../Output_Screenshots/student_records_output.png)

![Figure 20: Execution output of search_algorithms.py – traces of the three approaches (part 1 of 2)](../Output_Screenshots/search_algorithms_demo_output_1.png)

![Figure 21: Execution output of search_algorithms.py – traces of the three approaches (part 2 of 2)](../Output_Screenshots/search_algorithms_demo_output_2.png)

![Figure 22: Execution output of test_search_algorithms.py – 39/39 tests passed](../Output_Screenshots/test_search_algorithms_output.png)

## Task 9 – Record Experimental Performance [3 Marks]

> Collect and present data for each algorithm across the input sizes:
> - execution time;
> - number of comparisons;
> - number of key operations;
> - input size;
> - other relevant measures where justified (e.g. preprocessing time, memory).
> Present with tables, graphs, performance plots so approaches are easily compared.

**Ans:**

### 1. What I measured

`run_experiments.py` ran once for all four sizes (95.4 s in total). For every n and approach it records: the preprocessing comparisons, moves / hash computations and time; the average and maximum key comparisons of successful and unsuccessful searches; the other key operations per search (recursive calls for B, hash computations for C); the time per search; and the memory of the search structure. Times are the minimum of 2–7 runs with the garbage collector off; the raw numbers are in Appendix C.

### 2. Preprocessing cost

Table 15: One-time preprocessing (preprocessing_cost.csv)

| Number of records (n) | B: merge sort comparisons | Reference value n log₂ n | B: sort time (ms) | C: build hash computations | C: build chain comparisons | C: build time (ms) |
|---|---|---|---|---|---|
| 1,000 | 8,744 | 9,966 | 1.4 | 1,000 | 344 | 0.4 |
| 10,000 | 120,491 | 132,877 | 35.3 | 10,000 | 3,868 | 3.3 |
| 100,000 | 1,536,197 | 1,660,964 | 262.2 | 100,000 | 37,297 | 63.4 |
| 1,000,000 | 18,674,803 | 19,931,569 | 5,846.8 | 1,000,000 | 326,797 | 742.1 |

Sequential search needs no preprocessing (0 operations, 0 ms). Merge sort also moved 19,358 / 261,799 / 3,282,893 / 39,298,156 records. The hash build performed exactly n hash computations and no rehash (the table is sized for n in advance).

### 3. Key comparisons per search

Table 16: Average key comparisons per search (search_performance.csv; A at 10⁶: 100 + 100 queries, otherwise 500 + 500)

| n | A hit | A miss | B hit | B miss | C hit | C miss |
|---|---|---|---|---|---|---|
| 1,000 | 496.25 | 1,000 | 8.98 | 9.98 | 1.34 | 0.76 |
| 10,000 | 4,966.63 | 10,000 | 12.31 | 13.34 | 1.39 | 0.70 |
| 100,000 | 51,226.36 | 100,000 | 15.64 | 16.75 | 1.33 | 0.67 |
| 1,000,000 | 480,558.07 | 1,000,000 | 18.87 | 19.95 | 1.32 | 0.68 |

### 4. Execution time per search

Table 17: Time per search in microseconds (minimum of R runs; search_performance.csv)

| n | A hit | A miss | B hit | B miss | C hit | C miss |
|---|---|---|---|---|---|---|
| 1,000 | 15.05 | 31.91 | 1.52 | 1.71 | 0.26 | 0.25 |
| 10,000 | 170.74 | 355.57 | 2.38 | 2.73 | 0.50 | 0.37 |
| 100,000 | 2,081.58 | 4,420.73 | 4.12 | 4.58 | 0.66 | 0.47 |
| 1,000,000 | 22,536.82 | 51,240.99 | 6.24 | 7.06 | 0.88 | 0.62 |

### 5. Other key operations and the maximum cost per search

Table 18: Maximum key comparisons and other key operations per search

| Number of records (n) | A maximum per search | B maximum per search | B calls per search | C maximum (all keys) | C hashes per search |
|---|---|---|---|---|---|
| 1,000 | 1,000 | 10 | 9.98 | 5 | 1.00 |
| 10,000 | 10,000 | 14 | 13.32 | 7 | 1.00 |
| 100,000 | 100,000 | 17 | 16.69 | 8 | 1.00 |
| 1,000,000 | 1,000,000 | 20 | 19.91 | 6 | 1.00 |

For B the calls exceed the comparisons by one in an unsuccessful search (the final call on an empty range); for C every search computes exactly one hash. C's maximum equals the longest chain in the table.

### 6. Memory

Table 19: Extra memory of the search structure (memory_usage.csv; the records themselves are shared by all three)

| Records (n) | Records (MB) | A extra | B sorted copy (MB) | B peak (MB) | C table (MB) | C size m (α) |
|---|---|---|---|---|---|---|
| 1,000 | 0.10 | 0 | 0.01 | 0.02 | 0.07 | 1,361 (0.735) |
| 10,000 | 1.00 | 0 | 0.08 | 0.16 | 0.68 | 13,337 (0.750) |
| 100,000 | 10.00 | 0 | 0.80 | 1.60 | 6.87 | 133,337 (0.750) |
| 1,000,000 | 100.00 | 0 | 8.00 | 16.00 | 69.79 | 1,333,357 (0.750) |

All three grow linearly. The sorted copy is an array of n references (8 bytes each); the hash table needs about 70 bytes per record (10.7 MB bucket array + about 59 MB of chain lists at n = 10⁶), roughly 9 times the sorted array but still less than the records themselves.

### 7. Graphs

![Figure 23: Average key comparisons per search against n, with the theoretical curves (log–log)](../Tables_and_Graphs/fig1_comparisons_vs_n.png)

![Figure 24: Time per search against n with fitted c·n, c·log₂ n and c·1 curves (log–log)](../Tables_and_Graphs/fig2_time_per_search_vs_n.png)

![Figure 25: Preprocessing – operations (left) and time (right) of merge sort and hash-table build](../Tables_and_Graphs/fig3_preprocessing_cost.png)

![Figure 26: Extra memory of the search structures against n](../Tables_and_Graphs/fig5_memory_vs_n.png)

### 8. Experiment output

![Figure 27: Execution output of run_experiments.py (part 1 of 2)](../Output_Screenshots/run_experiments_output_1.png)

![Figure 28: Execution output of run_experiments.py (part 2 of 2)](../Output_Screenshots/run_experiments_output_2.png)

## Task 10 – Compare Theory with Experimental Behaviour [4 Marks]

> Discuss:
> - whether observed growth agrees with theoretical complexity;
> - which algorithm scales better as n increases;
> - differences between prediction and actual execution;
> - possible reasons.
> Interpret, don't just reproduce tables/graphs.

**Ans:**

### 1. The operation counts agree with the theory

Table 20: Measured ÷ predicted average comparisons (theory_vs_measured.csv; C predicted with the finite-key-space model of Task 3)

| n | A hit | A miss | B hit | B miss | C hit | C miss |
|---|---|---|---|---|---|---|
| 1,000 | 0.992 | 1.000 | 0.999 | 1.000 | 0.982 | 1.037 |
| 10,000 | 0.993 | 1.000 | 0.996 | 0.998 | 1.013 | 0.929 |
| 100,000 | 1.025 | 1.000 | 0.997 | 1.003 | 0.974 | 0.900 |
| 1,000,000 | 0.961 | 1.000 | 0.996 | 1.000 | 0.996 | 1.044 |

- **A:** unsuccessful searches cost *exactly* n, as derived. Successful averages scatter by a few per cent around (n + 1)/2 only because they are averages over a random sample of positions: with 100 searches at n = 10⁶ the standard error of the mean position is n/√(12·100) ≈ 28,900, and the observed difference (−19,442) is −0.67 standard errors. Every single successful search cost exactly position + 1 (Table 14).
- **B:** within 0.4% for the batches and **exact** for the exhaustive check (Table 10); the maximum was ⌊log₂ n⌋ + 1 at every size.
- **C:** the batches agree within about two standard errors of a 500-search sample (a chain-length standard deviation of about 0.87 gives ±0.04 per average). The exhaustive check is decisive. At n = 10⁶ the textbook formula 1 + (n − 1)/2m predicts 1.3750, but I measured **1.3268**. The refined model that accounts for the limited key universe (U = 10⁷ numbers, only 7–8 possible keys per bucket) predicts **1.3267**, a difference of 0.01%:

Table 21: Hash search – exhaustive average over all stored keys against both models (exhaustive_verification.csv)

| Number of records (n) | Measured average | Finite-universe model | Textbook 1 + (n − 1)/2m | Longest chain | Load factor α |
|---|---|---|---|---|---|
| 1,000 | 1.3440 | 1.3670 | 1.3670 | 5 | 0.735 |
| 10,000 | 1.3868 | 1.3744 | 1.3749 | 7 | 0.750 |
| 100,000 | 1.3730 | 1.3700 | 1.3750 | 8 | 0.750 |
| 1,000,000 | 1.3268 | 1.3267 | 1.3750 | 6 | 0.750 |

Figure 29 shows the same effect on the whole chain-length distribution at n = 10⁶: the observed numbers of buckets (605,954 empty, 502,931 with one record, …, 16 with six, none with seven) follow the finite-universe model (605,862; 503,105; …; 19.3; 0.55) and **not** the Poisson model of the textbook analysis (629,842; 472,373; …; 155.7; 16.7). Sampling 10% of all possible numbers spreads the keys *more evenly* than independent random hashing would, so the table performs slightly better than the standard prediction. At small n the two models coincide and the measurements scatter around both.

![Figure 29: Hash chain lengths at n = 1,000,000 – observed, finite-key-space model and Poisson](../Tables_and_Graphs/fig6_chain_length_distribution.png)

**Preprocessing.** Merge sort used 0.877–0.937 × n log₂ n comparisons; the ratio rises towards 1 because the lower-order term −1.25n matters less as n grows. Against n log₂ n − 1.25n the counts agree within 0.4% (8,744 vs 8,716; 18,674,803 vs 18,681,569), always below the worst case n⌈log₂ n⌉ − 2<sup>⌈log₂ n⌉</sup> + 1. The hash build made exactly n hash computations, and its comparisons (326,797 at 10⁶) were below the uniform-hashing estimate n(n − 1)/2m = 374,993, again because the keys are spread more evenly than at random.

### 2. Which algorithm scales better

Table 22: Measured growth factor when n grows ten-fold (cmp = key comparisons; 50/50 mix; growth_factors.csv)

| n step | A cmp ratio | A time ratio | B cmp ratio | B time ratio | C cmp ratio | C time ratio |
|---|---|---|---|---|---|---|
| 1,000 → 10,000 | ×10.00 | ×11.21 | ×1.35 | ×1.58 | ×0.99 | ×1.69 |
| 10,000 → 100,000 | ×10.10 | ×12.35 | ×1.26 | ×1.70 | ×0.96 | ×1.29 |
| 100,000 → 1,000,000 | ×9.79 | ×11.35 | ×1.20 | ×1.53 | ×1.00 | ×1.33 |
| theory | ×10 | ×10 | ×1.33 / ×1.25 / ×1.20 | | ×1 | ×1 |

Fitting a straight line to log(time) against log(n) gives slopes of **1.068 (A), 0.207 (B) and 0.151 (C)**; the theoretical slopes are 1, about 0.10 (log₂ n over this range) and 0. The ranking predicted by the asymptotic analysis is exactly what I observed: **C scales best, then B, and A worst by orders of magnitude.** At n = 10⁶ a successful sequential search (22,537 µs) is 3,600 times slower than binary search (6.24 µs) and 25,600 times slower than hashing (0.88 µs). In operations: 480,558 vs 18.87 vs 1.32 comparisons.

### 3. Differences between prediction and actual execution

The counts follow the theory almost perfectly, but the times show three systematic differences:

1. **Time grows faster than the count at large n for all three approaches.** A's time per comparison rose from 30 ns (n = 1,000) to 34, 41 and 47 ns; B's time grew ×4.1 for ×2.1 more comparisons; C's time grew ×3.4 although its comparisons did not change.
2. **The constant per basic operation differs greatly between the approaches.** One sequential comparison costs 30–47 ns, one binary-search level ≈ 330 ns (6.24 µs / 18.87 comparisons), one hash search ≈ 0.25–0.9 µs, and one merge-sort comparison ≈ 313 ns (5,846.8 ms / 18.7 million, including the moves and calls).
3. **Some single timings are irregular**, e.g. merge sort at n = 10,000 took 35.3 ms, 25 times the 1,000-record time instead of the expected 13.3 times, while the comparison count grew by exactly the predicted factor.

### 4. Reasons

- **Memory hierarchy (difference 1).** At n = 1,000 the records (0.1 MB) and the table (0.07 MB) fit in the processor's caches; at n = 10⁶ the records alone take 100 MB, far more than the 12 MB L3 cache. Every comparison with a record in a random place (B touches about 20 such records per search, C about three objects: bucket array, chain list, record) becomes a main-memory access of the order of 100 ns. The RAM model behind the Θ-analysis charges the same cost for every access, so it cannot show this effect. A scans the records in their stored order, which is also roughly their allocation order, so it suffers least (+57% per comparison).
- **Interpreter constants (difference 2).** In CPython a recursive call, a method call or an attribute lookup costs tens to hundreds of nanoseconds, much more than a comparison inside a tight `for` loop. This is why the *time-based* break-even points are larger than the operation-based ones (Table 24). Table 23 shows the same algorithms implemented in C inside CPython: Timsort (`sorted()`, a merge-sort hybrid) is 9.6–23 times faster than my merge sort, `dict` (a hash table) builds 3.6–6.4 times faster than my table, `bisect` is 4.7–7.5 times faster than my recursive binary search and `dict.get` is 2.6–2.8 times faster than my hash search. Their growth with n is the same; only the constant differs. Asymptotic analysis predicts the growth, not the absolute time.
- **Measurement noise (difference 3).** Other experiment programs were running on the same machine at the same time. I reduced the effect by switching the garbage collector off while timing and keeping the minimum of repeated runs, but single timings can still be disturbed. This is why the operation counts are my primary evidence; they are identical in every run.
- **Counter overhead.** The counters add a constant per basic operation to all three approaches equally, so they change the constants but not the growth.

Table 23: My implementations against CPython's C implementations of the same ideas (builtin_reference.csv)

| Number of records (n) | Merge sort / sorted() (ms) | Hash build / dict (ms) | Binary search / bisect (µs) | Hash search / dict.get (µs) |
|---|---|---|---|---|
| 1,000 | 1.4 / 0.1 | 0.4 / 0.1 | 1.52 / 0.203 | 0.26 / 0.096 |
| 10,000 | 35.3 / 1.5 | 3.3 / 0.5 | 2.38 / 0.329 | 0.50 / 0.178 |
| 100,000 | 262.2 / 27.2 | 63.4 / 12.4 | 4.12 / 0.751 | 0.66 / 0.258 |
| 1,000,000 | 5,846.8 / 417.1 | 742.1 / 206.6 | 6.24 / 1.341 | 0.88 / 0.318 |

### 5. Is the preprocessing worth it? (amortised cost)

Table 24: Break-even number of searches q* after which preprocessing beats sequential search (break_even.csv)

| Records (n) | A → B (operations) | A → B (time) | A → C (operations) | A → C (time) |
|---|---|---|---|---|
| 1,000 | 11.84 | 63.23 | 1.80 | 15.24 |
| 10,000 | 16.13 | 135.63 | 1.85 | 12.71 |
| 100,000 | 20.32 | 80.75 | 1.82 | 19.51 |
| 1,000,000 | 25.23 | 158.53 | 1.79 | 20.12 |

The operation-based values match the formulas of Task 3 (≈ (log₂ n − 1.25)/0.75 for B, ≈ 1.8 for C). In time, preprocessing pays for itself after at most about 160 searches for merge sort + binary search and about 20 searches for hashing, even at one million records. Figure 30 shows the total cost of preprocessing + q searches: for 50,000 searches at n = 10⁶ (one hour of Task 12) the totals are 1,844 s for A, 6.18 s for B (5.85 s of it the sort) and 0.78 s for C (amortised_cost.csv). Only when the database is searched fewer than about 13–20 times between two rebuilds is sequential search the cheapest choice.

![Figure 30: Total cost of preprocessing + q searches for n = 1,000 and n = 1,000,000, with the break-even points](../Tables_and_Graphs/fig4_amortised_cost_vs_searches.png)

**Conclusion of the comparison.** The mathematical analysis predicted the *growth* of every count correctly: linear for A, logarithmic for B and constant for C, with exact agreement where the algorithm is deterministic. The experiments add what the analysis abstracts away: the constants of the Python interpreter, the cache effects at a million records, and a property of this key set (a small universe) that makes hashing slightly better than the textbook model.

## Task 11 – Recommend and Defend the Final Design [4 Marks]

> Recommend the most appropriate solution. Discuss:
> - which approach;
> - why better than alternatives;
> - theoretical efficiency;
> - experimentally observed performance;
> - preprocessing cost;
> - trade-offs or limitations;
> - whether it remains practical as the database grows.
> Simply identifying the lowest Big-O is not sufficient.

**Ans:**

### 1. Recommendation

I recommend **Approach C: a hash table with separate chaining, keyed by registration number** (h(k) = k mod m with m prime, m ≥ n/0.75 so that α ≤ 0.75, growing to the next prime ≥ 2m when needed), built once from the records and then used for every lookup. If the university later needs ordered reports or range queries (for example "all students with numbers 1924xxxxx"), a sorted array with binary search (Approach B) should be kept *next to it* as a secondary index, not instead of it.

### 2. Why it is better than the alternatives

Table 25: Decision matrix at n = 1,000,000 (measurements from Tables 15–19 and 24)

| Criterion | A – Sequential | B – Merge sort + binary search | C – Hash table |
|---|---|---|---|
| Comparisons per hit / miss | 480,558 / 1,000,000 | 18.87 / 19.95 | 1.32 / 0.68 |
| Time per hit | 22,537 µs | 6.24 µs | 0.88 µs |
| Guaranteed worst case | n = 1,000,000 | ⌊log₂ n⌋ + 1 = 20 | n in theory; 6 observed |
| One-time preprocessing | none | 18.7 M comparisons, 5.85 s | 1.33 M operations, 0.74 s |
| Break-even searches (time) | – | 159 | 20 |
| Extra memory | 0 | 8 MB (16 MB while sorting) | 70 MB |
| Adding one new record | Θ(1) append | Θ(n) shift or batch merge | Θ(1) expected |
| Ordered / range queries | full scan | yes | no |
| Growth from 10³ to 10⁶ records | ×1,000 comparisons | +10 comparisons | unchanged |

- **Against A:** A avoids preprocessing, but it is the slowest by four orders of magnitude at a million records, and its cost rises with every admitted batch. The table pays for its build after about 20 searches; a university system serves far more than 20 searches.
- **Against B:** C is better on *both* parts of the cost: its preprocessing is about 14 times fewer operations (Θ(n) vs Θ(n log n)) and 7.9 times less time, and every search is 14 times fewer comparisons and 7.1 times faster. B has a better *guaranteed* worst case and uses less memory, but these advantages do not show up in this workload (the observed hash worst case was 8 comparisons).

### 3. Theoretical efficiency

Search: Θ(1) expected (1 + α/2 ≤ 1.375 comparisons for a hit, α ≤ 0.75 for a miss, plus one hash computation), independent of n. Preprocessing: Θ(n) expected (n hash computations + n(n − 1)/2m ≤ 0.375n comparisons). Cost of q searches: Θ(n + q), compared with Θ(n log n + q log n) for B and Θ(q·n) for A (Task 3). Space Θ(n + m) = Θ(n). The only weaker point is the theoretical worst case Θ(n) when all keys collide.

### 4. Experimentally observed performance

The measured counts confirmed the theory at every size (1.32–1.39 comparisons per hit, 0.67–0.76 per miss, exactly one hash computation per search; Tables 16 and 21). The time per search was 0.26–0.88 µs at all four sizes, the lowest of the three approaches at every size, including the smallest (at n = 1,000: 0.26 µs against 1.52 µs for B and 15.05 µs for A). Every one of the 4,000 test queries returned the correct record or `None` (Table 14).

### 5. Preprocessing cost

Building the table for 1,000,000 records took 1,326,797 basic operations and 0.74 s, compared with 18,674,803 comparisons and 5.85 s for merge sort. Because the build is linear, it also stays proportionate for small databases (0.4 ms at n = 1,000). In basic operations the build is recovered after **two** searches and in time after about **20** (Table 24), so the preprocessing is cheap relative to any realistic number of lookups.

### 6. Trade-offs and limitations

- **Memory:** about 70 bytes per record (69.8 MB at 10⁶), about 9 times the sorted array of B. This is the price of the space–time trade-off; it is still smaller than the records themselves (100 MB).
- **No order:** the table cannot list students in registration-number order or answer range queries without sorting first.
- **Worst case:** a key set concentrated in one residue class modulo m would make a search Θ(n) (test P5). Prime m and the university's own numbering make this unlikely (the longest chain was 5–8), and a randomly chosen (universal) hash function would remove the dependence on the key set.
- **Growth pauses:** when α would exceed 0.75 the table rehashes all records (Θ(n), about 0.8 s at 10⁶); the cost is amortised O(1) per insertion but happens at one moment (Task 12 addresses this).
- **Implementation constants:** in Python a hash search costs ≈ 0.9 µs, about 2.8 times slower than CPython's built-in `dict`; a production system would use the built-in hash map, which is the same algorithm.

### 7. Does it remain practical as the database grows?

Yes. Because m grows with n, the expected cost of a search stays constant: the measured comparisons did not change between 1,000 and 1,000,000 records, and the time grew only from 0.26 to 0.88 µs (memory caching, Task 10). The build and the memory grow linearly, so a database ten times larger (10 million records) would need about 7 s to build and about 0.7 GB for the table, while each search would still examine about one record. Sequential search would need ten times more comparisons per search and binary search about 3.3 more. Hashing is therefore the design that remains practical from 1,000 to 1,000,000+ records, with B as the complementary structure if ordered access is ever required.

## Task 12 – Re-evaluate and Adapt the Design [8 Marks]

> **Day-4 Design Challenge.** The university now needs to process **50,000 search requests per hour** on a database containing **1,000,000 student records**. New student records are added **only once per day**. Re-evaluate your original design and determine whether it should be retained, modified or redesigned.
> You may RETAIN → MODIFY → or REDESIGN.

**Ans:**

The original design is the one recommended in Task 11: a hash table built once for the n records (m = smallest prime ≥ n/0.75 = 1,333,357 at n = 10⁶). To answer with evidence, I wrote `design_challenge_simulation.py`, which runs the new workload on the real 1,000,000-record dataset: one full day of 24 × 50,000 searches (80% for existing students, 20% for mistyped or non-existent numbers, seeded per hour) on every design, followed by a nightly batch of **b = 5,000** new records absorbed by six different update strategies, and a day-2 hour that also searches for the new records. The batch size and the 80/20 mix are my assumptions; the analysis shows that the decision does not depend on them.

### A. Impact Analysis [2 Marks]

> Explain what has changed in the problem, which original assumptions are affected, why search frequency is now important and why the low update frequency may influence the design.

**Ans:**

Table 26: The new requirement expressed in numbers

| Quantity | Value | Derivation |
|---|---|---|
| Search rate | 50,000 per hour | given |
| Average arrival rate | 13.9 searches per second | 50,000 / 3,600 |
| Searches per day | 1,200,000 | 24 × 50,000 |
| Searches between two updates | 1,200,000 | one batch per day |
| Database size | 1,000,000 records, growing by b per day | given; b = 5,000 assumed |
| Average time available per search | 72 ms | 3,600 s / 50,000 |

**What has changed.** (1) The workload is now *quantified and continuous*: the number of searches q, which in Tasks 3–11 was an unknown parameter, is now 1.2 million per day. (2) The database is now *dynamic*: records arrive in a daily batch, so the design must say how new records become searchable. (3) The size is fixed at the large end (10⁶) and keeps growing.

**Which original assumptions are affected.**

- *Static data.* Task 11 built the table once for exactly n records. With daily additions the table sized for n reaches α > 0.75 after only **18** new records (0.75 × 1,333,357 = 1,000,017.75), which triggers a full rehash; and the design did not say whether new records are inserted or the table is rebuilt.
- *Preprocessing amortised over "many" searches.* The break-even analysis (Table 24) assumed an unknown q; now q is known and enormous, so per-search cost dominates and preprocessing is amortised almost completely.
- *Occasional single searches.* The original analysis looked at the latency of one search. Now throughput, CPU utilisation and headroom for peak hours matter, because the cost of every search is multiplied by 1.2 million per day.

**Why search frequency is now important.** The cost of one day is D = U(n, b) + Q·S(n) with Q = 1,200,000. Any per-search cost is multiplied by 1.2 million: a difference of 1 µs per search is 1.2 s per day, and a Θ(n) search becomes 1.2 M × 600,000 = 7.2 × 10¹¹ comparisons per day. At the same time the one-time preprocessing is divided by 1.2 million: merge sort costs 18,674,803 / 1,200,000 = 15.6 comparisons per search of one day, and the hash build 1,326,797 / 1,200,000 = 1.1 operations per search. Frequent searching therefore favours whatever makes **each search cheapest**, even at a higher preprocessing cost.

**Why the low update frequency may influence the design.** Because records arrive once per day, the search structure is **read-only for 24 hours**: it can be optimised for reading, it needs no locking during the day, and expensive maintenance (sorting a batch, merging, rehashing) happens at most once per day in a quiet night-time window, where it is amortised over 1.2 million searches. It also means that a structure with expensive single insertions (the sorted array, Θ(n) per insertion) becomes acceptable if insertions are *batched*. If records arrived continuously, both the sorted array and a table that rehashes at unplanned moments would be much less attractive.

### B. Evaluation of the Original Design [2 Marks]

> Evaluate how your original design would behave under 50,000 searches per hour, whether its preprocessing cost is acceptable under the new conditions, and whether another approach could provide better overall performance.

**Ans:**

Table 27: Measured search load of one simulated day (design_challenge_hourly.csv, design_challenge_daily_cost.csv)

| Design | Comparisons per hour | CPU seconds per hour | Time per search | Share of one CPU core | Load headroom factor |
|---|---|---|---|---|---|
| A sequential (extrapolated) | 29,789,029,750 | 1,264 | 25,280 µs | 35.11% | 2.8× |
| B binary search | 957,484 | 0.438 | 8.75 µs | 0.0122% | 8,228× |
| C original, m = 1,333,357 | 59,610 (+ 50,000 hashes) | 0.056 | 1.12 µs | 0.0016% | 64,310× |
| C3 modified, m = 2,666,683 | 48,404 (+ 50,000 hashes) | 0.050 | 1.01 µs | 0.0014% | 71,441× |

**Behaviour of the original design under 50,000 searches per hour.** The prediction from Task 3 was 50,000 × (0.8 × 1.3267 + 0.2 × 0.6533) = 59,600 comparisons plus 50,000 hash computations per hour. The simulation measured between 59,309 and 59,896 comparisons in each of the 24 hours (59,610 on average), every one of the 40,000 existing students per hour was found and every absent number was rejected. The whole hour of searching took 0.047–0.075 s of CPU time, i.e. **0.0016% of one core**; one search takes about 1.1 µs against the 72 ms available on average. The original design easily meets the new requirement and could absorb about 64,000 times the load before one core is busy.

**Is its preprocessing cost acceptable?** The initial build (1,326,797 operations, 0.69 s in this run) is paid once at deployment and is negligible. The *daily* cost is where the original design is weak, because it was designed for a static database:

- **C1 – rebuild the table every night:** 1,332,916 operations and 0.714 s to add 5,000 records, Θ(n + b) work for Θ(b) new data, and the old and new tables (about 140 MB) must coexist during the rebuild.
- **C2 – insert into the table as built:** the 18th new record pushes α over 0.75 and the table rehashes all 1,000,018 records at that moment (1,005,018 hash computations, 0.792 s, m grows to 2,666,717). If records were inserted during service hours, all searches would stall for about 0.8 s at an unpredictable time.

Both are under one second per night, so the cost is *affordable*, but it is about **200 times more work than necessary** (1,332,916 vs 6,454 operations) and its timing is not controlled. That is a design flaw worth fixing, not a reason to abandon hashing.

**Could another approach give better overall performance?** No (Table 29). Binary search needs 16 times more comparisons per search (19.15 vs 1.19) and 7.8 times more CPU time, and its sorted array must be maintained by a full re-sort (4.18 s per night) or a batch merge (0.35 s); its total cost is 10.85–14.68 CPU-seconds per day against 2.06–2.14 s for the original hash design. Sequential search would need 30,335 CPU-seconds per day (8.4 hours), 35% of a core permanently, with a mean response time of about 39 ms by the M/M/1 formula R = S/(1 − ρ) = 25.3 ms / (1 − 0.351), and it would saturate the core if the load rose 2.8 times or, at the current load, once the database grows to about 2.85 million records (after about 369 days of 5,000 new records). The best approach remains hashing; what needs to change is the way it is sized and maintained.

### C. Adaptation or Redesign [2 Marks]

> Decide whether to retain, modify or redesign. If modified or redesigned, describe the revised strategy, what changed and its effect on the computational complexity; if retained, justify the decision technically.

**Ans:**

**Decision: MODIFY.** I retain the hash-table search (Approach C), because no other strategy is faster per search, and I modify how the table is sized and how the daily batch is absorbed.

**Revised strategy (design C3).**

1. **Capacity planning at deployment.** Create the table with m = smallest prime ≥ N<sub>plan</sub>/0.75 for a planned capacity N<sub>plan</sub> = 2,000,000 records (200 busy days of 5,000 new students, or several years at normal admission rates): m = 2,666,683, α = 0.375 at the start and 0.75 only when the planned capacity is reached. Initial build: 1,139,716 operations, 0.56 s.
2. **Nightly incremental batch insertion.** Once per day, in a maintenance window, insert only the b new records: b hash computations plus the duplicate checks (measured 5,000 + 1,454 operations, **0.0036 s**, no rehash). The simulation verified that all 5,000 new records, a sample of 1,000 old records and 1,000 absent numbers give the correct answers afterwards, and the day-2 hour found all 40,000 existing students including 180 searches for new ones.
3. **Read-only during the day.** Searches never run concurrently with an update, so no locking is needed. If the service must run 24 × 7, the batch can be inserted into a copy and the reference swapped; with incremental insertion this takes milliseconds.
4. **Planned growth and monitoring.** Each night the program records α and the longest chain. When the next batch would push α above 0.75, the table is rehashed to the next prime ≥ 2m in the maintenance window (about 0.8 s, measured as C2). Doubling keeps the total rehash work below two moves per inserted record (amortised O(1)).
5. **Optional secondary index.** Only if ordered or range queries are required, keep the sorted array of Approach B and merge the sorted daily batch into it (B2, Θ(n + b log b), 0.35 s per night). It is not needed for the stated requirement.

Table 28: The original design against the modified design (measurements from design_challenge_simulation.py)

| Aspect | Original (Task 11) | Modified (C3) |
|---|---|---|
| Table size m | 1,333,357, sized for n (α = 0.750) | 2,666,683, planned for 2,000,000 (α = 0.375 → 0.75) |
| How a daily batch is absorbed | rebuild Θ(n + b) or unplanned rehash Θ(n) | incremental insertion Θ(b) |
| Nightly update (operations / time) | 1,332,916 / 0.714 s (rebuild) | 6,454 / 0.0036 s |
| Comparisons per search (80/20 mix) | 1.19 | 0.97 |
| When a rehash can happen | after the 18th new record, at any time | only in a planned nightly window, after about 200 busy days |
| Bucket-array memory | 10.7 MB | 21.3 MB |
| CPU per day (update + 1.2 M searches) | 2.06 s | 1.21 s |

**Effect on the computational complexity.**

- **Search:** unchanged class, Θ(1) expected; the constant improves because 1 + α/2 is smaller while α < 0.75 (measured 0.97 instead of 1.19 comparisons per search, 19% fewer).
- **Daily maintenance:** from Θ(n + b) (rebuild) or an unplanned Θ(n) rehash to **Θ(b) expected**, 206 times fewer operations and about 200 times less time per night.
- **Cost of one day:** from Θ(n + b + Q) to Θ(b + Q) with Q = 1.2 M searches, i.e. it no longer depends on the size of the database at all.
- **Space:** still Θ(n + m) = Θ(n), but with a larger constant (the bucket array grows from 10.7 MB to 21.3 MB). This is the trade-off I accept for predictable, cheap updates.

### D. Evidence-Based Defence [2 Marks]

> Defend your decision using mathematical complexity analysis, experimental results, search frequency, preprocessing cost, dataset size and computational trade-offs. The decision must follow logically from the analysis.

**Ans:**

Table 29: Cost of one day for every design and update strategy (design_challenge_daily_cost.csv; n = 1,000,000, b = 5,000, 1,200,000 searches)

| Design | Nightly update (s) | Searching (s/day) | Total CPU (s/day) | Basic operations per day | Share of one core |
|---|---|---|---|---|---|
| A append to unsorted list | 0.0022 | 30,335.40 | 30,335.40 | 714,936,719,000 | 35.11% |
| B1 re-sort nightly | 4.1782 | 10.50 | 14.68 | 104,476,679 | 0.0122% |
| B2 sort batch + merge | 0.3476 | 10.50 | 10.85 | 48,385,118 | 0.0122% |
| C1 rebuild nightly | 0.7143 | 1.34 | 2.06 | 3,963,567 | 0.0016% |
| C2 insert, sized for n | 0.7921 | 1.34 | 2.14 | 3,637,066 | 0.0016% |
| **C3 reserved + batch insert** | **0.0036** | **1.21** | **1.21** | **2,368,157** | **0.0014%** |

![Figure 31: Cost of one day per design – nightly update and 24 hours of searching (log scale)](../Tables_and_Graphs/fig7_daily_cost_by_design.png)

**1. Mathematical complexity.** With D = U + Q·S and Q = 1.2 × 10⁶, the predicted daily operations are: A: Q × 0.6n = 7.2 × 10¹¹; B: U + Q × 19.15 = U + 2.3 × 10⁷ with U = 1.9 × 10⁷ (re-sort) or 1.1 × 10⁶ (merge); C: U + Q × (1 + 1.19) = U + 2.6 × 10⁶ with U = 1.3 × 10⁶ (rebuild) or 6.5 × 10³ (C3). The search term Q·S is the largest term of every design (for B1 and C1 the update term is of the same order), so the per-search class decides the ranking (Θ(1) < Θ(log n) < Θ(n)), and between variants with the same search cost the Θ(b) update beats the Θ(n) or Θ(n log n) one. The measured counts (Table 29) agree with each prediction: 7.1 × 10¹¹, 1.04 × 10⁸, 4.8 × 10⁷, 4.0 × 10⁶ and 2.4 × 10⁶.

**2. Experimental results.** One full simulated day on 1,000,000 records: C3 used 1.21 CPU-seconds, 9 times less than the best binary-search variant (10.85 s) and 25,000 times less than sequential search (30,335 s). Every one of the 960,000 successful searches of the day was answered correctly by B, C and C3, and all strategies passed the post-update verification.

**3. Search frequency.** Figure 32 varies the search rate using the measured unit costs. Every preprocessing design beats sequential search above 0.6–7 searches per hour (STEP 6 of the output); the merged sorted array B2 would be cheaper than the rebuilt hash table below about 2,000 searches per hour, because its nightly update is cheaper. At 50,000 searches per hour the search term decides, and C3 is the cheapest design at every rate above 0.002 searches per hour, because its update costs almost as little as A's append. The decision is therefore robust: it would hold for any rate above a few searches per hour.

![Figure 32: Daily CPU cost against the search rate, from the measured unit costs](../Tables_and_Graphs/fig8_daily_cost_vs_search_rate.png)

**4. Preprocessing cost.** Of C3's daily 1.21 s, 99.7% is searching and only 0.0036 s is the nightly update; the initial build (0.56 s) is paid once. A full nightly re-sort (B1, 4.18 s) would cost more than three times C3's entire day, and a rebuild (C1, 0.71 s) about 200 times C3's update, which is why incremental maintenance is the right modification when updates are rare and batched.

**5. Dataset size and growth.** At 5,000 new records per day the database doubles in 200 days. A's daily cost grows linearly with n and would saturate one core after about 369 days; B gains one comparison per search when n doubles; C3's cost per search stays constant, its update stays Θ(b), and its first rehash is planned for when the database reaches 2,000,000 records.

**6. Computational trade-offs.** C3 spends 10.7 MB more on its bucket array than the original table (21.3 MB instead of 10.7 MB), a hash table needs roughly 9 times the memory of B's sorted array (Table 19), and it gives up ordered queries. In return it has the lowest per-search cost, the cheapest and most predictable updates, and a load headroom of about 71,000×, so even a 100-fold peak in requests would use only about 0.14% of one core. The theoretical Θ(n) worst case is controlled by the prime table size, monitored longest chain (6 at 10⁶) and, if needed, a universal hash function.

**Conclusion.** Because searching dominates the daily cost, the approach with the cheapest search (hashing) must be **retained**; because updates are rare and batched, its static, sized-for-n preprocessing must be **modified** into planned capacity plus nightly incremental insertion. The decision MODIFY follows directly from D = U + Q·S with Q = 1.2 × 10⁶ and b ≪ n.

![Figure 33: Execution output of design_challenge_simulation.py (part 1 of 2)](../Output_Screenshots/design_challenge_simulation_output_1.png)

![Figure 34: Execution output of design_challenge_simulation.py (part 2 of 2)](../Output_Screenshots/design_challenge_simulation_output_2.png)

### Summary of Findings

Table 30: Summary of the twelve tasks

| Task | Finding |
|---|---|
| 1 Design | A: iterative brute-force sequential search; B: recursive divide-and-conquer binary search after my own merge sort; C: hash table with separate chaining (space–time trade-off). |
| 2 Basic operation | Key comparison (A), three-way comparison with A[mid] (B), chain comparison + one hash (C); merge-sort comparison and hash computation for preprocessing. |
| 3 Complexity functions | A: (n + 1)/2 hit, n miss; B: ⌊log₂ n⌋ + 1 worst, ≈ log₂ n − 1 hit, after n log₂ n − n + 1 sorting; C: 1 + α/2 hit, α miss after ≈ 1.375n build. |
| 4 Cases | Best case Θ(1) for all; worst A Θ(n), B Θ(log n), C Θ(n) only if all keys collide (demonstrated, longest chain observed 8). |
| 5 Asymptotics | Θ(1) ⊂ Θ(log n) ⊂ Θ(n); ×1,000 records → A ×1,000, B +10 comparisons, C unchanged. |
| 6–7 Recurrence | C(n) = C(⌊n/2⌋) + 1, C(0) = 0 → ⌊log₂ n⌋ + 1 = Θ(log n) by backward substitution, Master Theorem (a = 1, b = 2, case 2) and induction; merge sort n log₂ n − n + 1; exact agreement with counts. |
| 8 Testing | 39/39 checks passed on n = 0, 1, 15 and 1,000 – 1,000,000; same seeded data and queries for all. |
| 9 Measurements | At 10⁶: A 480,558 comparisons / 22.5 ms; B 18.87 / 6.24 µs after 5.85 s sorting; C 1.32 / 0.88 µs after 0.74 s build. |
| 10 Theory vs experiment | Counts match theory (exactly for B); time grows faster than counts at 10⁶ (cache misses); hashing beat the textbook model because of the small key universe. |
| 11 Recommendation | Hash table: fastest at every size, cheapest preprocessing, pays off after ≈ 20 searches; trade-off memory and no ordering. |
| 12 Design challenge | MODIFY: keep hashing, plan capacity (m = 2,666,683) and insert the daily batch incrementally: 1.21 CPU-s per day vs 10.85 s (best B) and 30,335 s (A). |

<!-- pagebreak -->

### Appendix A – Complete Source Code: Task_8_Implementation_Testing/Source_Code

The five programs below are complete and unedited. They need Python 3.13 and matplotlib (graphs only).

#### student_records.py

```python
"""
student_records.py - reproducible student-record datasets for the CO1 search assignment.

Problem
-------
A university database stores student records, each identified by a UNIQUE 9-digit Registration
Number in the format 19xxxxxxx (190,000,000 ... 199,999,999).  Staff must decide whether a given
registration number exists and, if so, retrieve that student's record.

This module provides
  * StudentRecord            - one record (reg_no, name, department, cgpa)
  * generate_records(n)      - n records with unique registration numbers, stored in ARRIVAL order
                               (i.e. NOT sorted), produced from a fixed seed (42)
  * make_query_batch(...)    - a batch of present keys (successful searches) and absent keys
                               (unsuccessful searches) drawn with a fixed seed

Every algorithm and every experiment uses these same datasets, so the comparison is fair.
Prefix property: generate_records(1_000) == generate_records(1_000_000)[:1_000], so the four
datasets (1,000 / 10,000 / 100,000 / 1,000,000 records) are nested and directly comparable.
"""
import random

SEED = 42
REG_MIN = 190_000_000          # smallest possible registration number
REG_MAX = 199_999_999          # largest possible registration number (10 million values in total)

DEPARTMENTS = ("CSE", "ECE", "EEE", "MECH", "CIVIL", "IT", "AIDS", "BME", "CHEM", "BIOTECH")
FIRST_NAMES = ("Aarav", "Aditi", "Akash", "Ananya", "Arjun", "Bhavana", "Charan", "Deepa", "Dhruv",
               "Divya", "Gokul", "Harini", "Ishaan", "Janani", "Karthik", "Kavya", "Lakshmi", "Manoj",
               "Meera", "Naveen", "Nisha", "Pranav", "Priya", "Rahul", "Ramya", "Rohan", "Sahana",
               "Sanjay", "Shreya", "Siddharth", "Sneha", "Surya", "Tanvi", "Varun", "Vidya", "Vikram",
               "Yamini", "Yash", "Zara", "Keerthi")
INITIALS = "ABCDEFGHIJKLMNOPRSTUVWY"

# Pools of shared, immutable objects: 1,000,000 records then cost ~100 bytes each instead of ~250.
NAME_POOL = tuple(f"{first} {initial}." for first in FIRST_NAMES for initial in INITIALS)
CGPA_POOL = tuple(round(5.0 + i / 100, 2) for i in range(501))          # 5.00 ... 10.00


class StudentRecord:
    """One student record. reg_no is the search key; the other fields are the retrieved data."""
    __slots__ = ("reg_no", "name", "department", "cgpa")

    def __init__(self, reg_no, name, department, cgpa):
        self.reg_no = reg_no
        self.name = name
        self.department = department
        self.cgpa = cgpa

    def __repr__(self):
        return f"StudentRecord({self.reg_no}, {self.name!r}, {self.department}, {self.cgpa:.2f})"


def generate_records(n, seed=SEED):
    """Return a list of n StudentRecord objects with unique registration numbers, in arrival order.

    Keys are drawn uniformly from 190,000,000..199,999,999; a key that was already issued is simply
    re-drawn, so the first n records never depend on how many records are requested in total.
    """
    rng = random.Random(seed)
    issued = set()
    records = []
    span = REG_MAX - REG_MIN + 1
    while len(records) < n:
        reg_no = REG_MIN + int(rng.random() * span)
        if reg_no in issued:                       # duplicates are impossible by construction
            continue
        issued.add(reg_no)
        records.append(StudentRecord(reg_no,
                                     NAME_POOL[int(rng.random() * len(NAME_POOL))],
                                     DEPARTMENTS[int(rng.random() * len(DEPARTMENTS))],
                                     CGPA_POOL[int(rng.random() * len(CGPA_POOL))]))
    return records


def generate_new_records(count, existing_keys, seed):
    """Return `count` NEW records whose registration numbers are not in `existing_keys` (a set)."""
    rng = random.Random(seed)
    span = REG_MAX - REG_MIN + 1
    new_records, new_keys = [], set()
    while len(new_records) < count:
        reg_no = REG_MIN + int(rng.random() * span)
        if reg_no in existing_keys or reg_no in new_keys:
            continue
        new_keys.add(reg_no)
        new_records.append(StudentRecord(reg_no,
                                         NAME_POOL[int(rng.random() * len(NAME_POOL))],
                                         DEPARTMENTS[int(rng.random() * len(DEPARTMENTS))],
                                         CGPA_POOL[int(rng.random() * len(CGPA_POOL))]))
    return new_records


def make_query_batch(records, n_present, n_absent, seed, key_set=None):
    """Return (present_keys, absent_keys).

    present_keys - n_present registration numbers chosen uniformly at random from `records`
                   (so every stored position is equally likely -> average-case conditions)
    absent_keys  - n_absent registration numbers inside 19xxxxxxx that are NOT stored (realistic
                   mistyped / non-existent numbers that fall into the gaps between stored keys)
    """
    rng = random.Random(seed)
    if key_set is None:
        key_set = {record.reg_no for record in records}
    present = [records[i].reg_no for i in rng.sample(range(len(records)), min(n_present, len(records)))]
    absent = []
    span = REG_MAX - REG_MIN + 1
    while len(absent) < n_absent:
        candidate = REG_MIN + int(rng.random() * span)
        if candidate not in key_set:
            absent.append(candidate)
    return present, absent


def main():
    """Print a small sample of the generated data and check the uniqueness / prefix properties."""
    print("=" * 78)
    print(" Student record generator (seed 42) - sample of the 1,000-record dataset")
    print("=" * 78)
    records = generate_records(1_000)
    print(f"{'pos':>4}  {'reg_no':>10}  {'name':<14} {'dept':<8} {'cgpa':>5}")
    for pos, rec in enumerate(records[:10]):
        print(f"{pos:>4}  {rec.reg_no:>10}  {rec.name:<14} {rec.department:<8} {rec.cgpa:>5.2f}")
    keys = [r.reg_no for r in records]
    print(f"\nunique keys      : {len(set(keys)) == len(keys)}  ({len(set(keys)):,} of {len(keys):,})")
    print(f"stored in order  : sorted = {keys == sorted(keys)}  (records are in arrival order)")
    bigger = generate_records(10_000)
    print(f"prefix property  : generate_records(10,000)[:1,000] == generate_records(1,000) -> "
          f"{[r.reg_no for r in bigger[:1_000]] == keys}")
    present, absent = make_query_batch(records, 5, 5, seed=7)
    print(f"sample present keys: {present}")
    print(f"sample absent keys : {absent}")


if __name__ == "__main__":
    main()
```

#### search_algorithms.py

```python
"""
search_algorithms.py - the three search strategies of the CO1 assignment and their preprocessing.

Problem: given the student records and a registration number `key`, decide whether a record with
that key exists and, if so, return (retrieve) it; otherwise return None.

  Approach A  sequential_search         ITERATIVE brute force on the unsorted records   no preprocessing
  Approach B  binary_search_recursive   RECURSIVE divide-and-conquer on a sorted array  merge_sort_records
  Approach C  StudentHashTable.search   HASHING with separate chaining (space-time      StudentHashTable.build
                                        trade-off / transform-and-conquer)

Every routine counts its basic operation in an OpCounter, so the analysis can be checked by measurement:
  comparisons        key comparisons (A: A[i].reg_no == key;  B: ONE three-way comparison of key with
                     A[mid];  C: key comparisons along one chain;  merge sort: aux[i].reg_no <= aux[j].reg_no)
  hash_computations  evaluations of h(k) = k mod m
  calls              recursive calls made by binary search (including a final empty-range call)
  moves              record moves made by merge sort (copy to the buffer + write back)
All algorithm cores are hand-written; no library search, sort or dict is used inside them.
"""
import math
import sys

from student_records import generate_records


class OpCounter:
    """Mutable bundle of operation counters that the algorithms increment."""
    __slots__ = ("comparisons", "hash_computations", "calls", "moves")

    def __init__(self):
        self.reset()

    def reset(self):
        self.comparisons = 0
        self.hash_computations = 0
        self.calls = 0
        self.moves = 0


# ===================================================================== Approach A: sequential search
def sequential_search(records, key, counter):
    """Iterative brute force: scan records[0], records[1], ... until reg_no == key or the list ends.

    Works on the records in their stored (unsorted) order, so no preprocessing is needed.
    Returns the matching StudentRecord, or None if the key is absent.
    """
    comparisons = 0
    for record in records:
        comparisons += 1                          # BASIC OPERATION: one key comparison per record
        if record.reg_no == key:
            counter.comparisons += comparisons
            return record
    counter.comparisons += comparisons            # unsuccessful: all n records were compared
    return None


# ======================================================= Preprocessing for Approach B: merge sort
def merge_sort_records(records, counter):
    """Return a NEW list with the records sorted by reg_no (top-down merge sort, divide and conquer).

    The arrival-order list is not modified.  One auxiliary buffer of n slots is reused by every merge.
    """
    result = list(records)
    aux = [None] * len(result)
    _merge_sort(result, aux, 0, len(result) - 1, counter)
    return result


def _merge_sort(a, aux, low, high, counter):
    """Sort a[low..high] in place: sort both halves recursively, then merge them."""
    if low >= high:                               # 0 or 1 record: already sorted (base case)
        return
    mid = (low + high) // 2
    _merge_sort(a, aux, low, mid, counter)
    _merge_sort(a, aux, mid + 1, high, counter)
    _merge(a, aux, low, mid, high, counter)


def _merge(a, aux, low, mid, high, counter):
    """Merge the sorted runs a[low..mid] and a[mid+1..high], counting key comparisons and moves."""
    aux[low:high + 1] = a[low:high + 1]           # copy both runs to the buffer
    i, j = low, mid + 1
    comparisons = 0
    writes = 0
    for k in range(low, high + 1):
        if i > mid:                               # left run used up: the rest of the right run
            break                                 # is already in its final place
        if j > high:                              # right run used up: copy the rest of the left run
            a[k:high + 1] = aux[i:mid + 1]
            writes += mid + 1 - i
            break
        comparisons += 1                          # BASIC OPERATION of the preprocessing step
        if aux[i].reg_no <= aux[j].reg_no:
            a[k] = aux[i]
            i += 1
        else:
            a[k] = aux[j]
            j += 1
        writes += 1
    counter.comparisons += comparisons
    counter.moves += (high - low + 1) + writes


# ================================================================ Approach B: recursive binary search
def binary_search_recursive(sorted_records, key, low, high, counter, trace=None):
    """Recursive binary search for key in sorted_records[low..high] (inclusive bounds).

    Divide: look at the middle record.  Conquer: recurse into ONE half only.  Combine: nothing.
    Returns the matching StudentRecord, or None.  `trace` (optional list) records (low, high, mid, A[mid]).
    """
    counter.calls += 1
    if low > high:                                # base case: empty range -> key is absent
        return None
    mid = (low + high) // 2
    mid_key = sorted_records[mid].reg_no
    counter.comparisons += 1                      # BASIC OPERATION: one three-way comparison key : A[mid]
    if trace is not None:
        trace.append((low, high, mid, mid_key))
    if key == mid_key:
        return sorted_records[mid]
    if key < mid_key:
        return binary_search_recursive(sorted_records, key, low, mid - 1, counter, trace)
    return binary_search_recursive(sorted_records, key, mid + 1, high, counter, trace)


def binary_search(sorted_records, key, counter, trace=None):
    """Convenience wrapper: binary search over the whole sorted array."""
    return binary_search_recursive(sorted_records, key, 0, len(sorted_records) - 1, counter, trace)


# ====================================================================== Approach C: hash table
def is_prime(x):
    """Trial-division primality test (only used to choose the table size)."""
    if x < 2:
        return False
    if x % 2 == 0:
        return x == 2
    divisor = 3
    while divisor * divisor <= x:
        if x % divisor == 0:
            return False
        divisor += 2
    return True


def next_prime(x):
    """Smallest prime >= x."""
    while not is_prime(x):
        x += 1
    return x


class StudentHashTable:
    """Hash table with separate chaining, h(k) = k mod m, m prime, load factor alpha = n/m <= 0.75.

    Preprocessing (build) inserts every record once: Theta(n) expected.  A search computes h(key) once
    and compares key only with the records in that one chain: Theta(1 + alpha) expected.
    """
    MAX_LOAD_FACTOR = 0.75

    def __init__(self, expected_records=0):
        self.size = next_prime(max(11, math.ceil(expected_records / self.MAX_LOAD_FACTOR)))
        self.buckets = [None] * self.size         # None = empty chain (saves memory)
        self.count = 0
        self.resizes = 0

    @classmethod
    def build(cls, records, counter):
        """Preprocessing for Approach C: create a table sized for len(records) and insert them all."""
        table = cls(len(records))
        for record in records:
            table.insert(record, counter)
        return table

    @property
    def load_factor(self):
        return self.count / self.size

    def _hash(self, key, counter):
        counter.hash_computations += 1
        return key % self.size                    # division method with a prime table size

    def insert(self, record, counter):
        """Insert a record (or replace the record with the same key). Returns True if the key was new."""
        index = self._hash(record.reg_no, counter)
        chain = self.buckets[index]
        if chain is None:
            self.buckets[index] = [record]
        else:
            for pos, existing in enumerate(chain):
                counter.comparisons += 1
                if existing.reg_no == record.reg_no:   # duplicates are never stored twice
                    chain[pos] = record
                    return False
            chain.append(record)
        self.count += 1
        if self.count > self.MAX_LOAD_FACTOR * self.size:
            self._rehash(next_prime(2 * self.size), counter)
        return True

    def reserve(self, expected_records, counter):
        """Grow the table in advance so that `expected_records` fit with alpha <= 0.75 (capacity plan)."""
        needed = next_prime(math.ceil(expected_records / self.MAX_LOAD_FACTOR))
        if needed > self.size:
            self._rehash(needed, counter)

    def _rehash(self, new_size, counter):
        """Move every record into a new bucket array of `new_size` chains (keys are already unique)."""
        old_buckets = self.buckets
        self.size = new_size
        self.buckets = [None] * new_size
        self.resizes += 1
        for chain in old_buckets:
            if chain is not None:
                for record in chain:
                    index = self._hash(record.reg_no, counter)
                    if self.buckets[index] is None:
                        self.buckets[index] = [record]
                    else:
                        self.buckets[index].append(record)

    def search(self, key, counter):
        """Approach C search: one hash computation, then key comparisons along a single chain."""
        chain = self.buckets[self._hash(key, counter)]
        if chain is not None:
            comparisons = 0
            for record in chain:
                comparisons += 1                  # BASIC OPERATION: key comparison with a chain entry
                if record.reg_no == key:
                    counter.comparisons += comparisons
                    return record
            counter.comparisons += comparisons
        return None

    def chain_lengths(self):
        return [0 if chain is None else len(chain) for chain in self.buckets]

    def memory_bytes(self):
        """Bytes used by the index itself (bucket array + chain lists), excluding the shared records."""
        return sys.getsizeof(self.buckets) + sum(sys.getsizeof(c) for c in self.buckets if c is not None)


def hash_search(table, key, counter):
    """Uniform call signature used by the test and experiment programs."""
    return table.search(key, counter)


# =========================================================== Task 12 helper: daily batch for Approach B
def merge_sorted_batch(sorted_records, new_records, counter):
    """Modified preprocessing for B: sort only the daily batch (b log b), then merge linearly (n + b)."""
    batch = merge_sort_records(new_records, counter)
    merged = [None] * (len(sorted_records) + len(batch))
    i = j = k = 0
    comparisons = 0
    while i < len(sorted_records) and j < len(batch):
        comparisons += 1
        if sorted_records[i].reg_no <= batch[j].reg_no:
            merged[k] = sorted_records[i]
            i += 1
        else:
            merged[k] = batch[j]
            j += 1
        k += 1
    merged[k:] = sorted_records[i:] if i < len(sorted_records) else batch[j:]
    counter.comparisons += comparisons
    counter.moves += len(merged)
    return merged


# ------------------------------------------------------------------ uniform registry of the approaches
def prepare_sequential(records, counter):
    """Approach A needs no preprocessing: it searches the records as stored."""
    return records


APPROACHES = (
    ("Sequential (A)", prepare_sequential, sequential_search),
    ("Binary (B)", merge_sort_records, binary_search),
    ("Hash (C)", StudentHashTable.build, hash_search),
)


# ------------------------------------------------------------------------------------------- demo
def main():
    """Trace all three approaches on a small 15-record dataset."""
    records = generate_records(15)
    line = "-" * 96
    print("=" * 96)
    print(" Demo: the three search approaches on the first 15 records of the seed-42 dataset")
    print("=" * 96)
    print(f" {'pos':>3}  {'reg_no':>10}  {'name':<14} {'dept':<8} {'cgpa':>5}")
    for pos, rec in enumerate(records):
        print(f" {pos:>3}  {rec.reg_no:>10}  {rec.name:<14} {rec.department:<8} {rec.cgpa:>5.2f}")

    print(line)
    print(" Approach A - iterative sequential search (records in arrival order, no preprocessing)")
    for label, key in (("first stored record", records[0].reg_no), ("last stored record", records[-1].reg_no),
                       ("absent key", 189_999_999)):
        c = OpCounter()
        found = sequential_search(records, key, c)
        print(f"   key {key:>10} ({label:<19}): {('found ' + found.name) if found else 'not found':<20}"
              f" comparisons = {c.comparisons}")

    print(line)
    c = OpCounter()
    sorted_records = merge_sort_records(records, c)
    n = len(records)
    bound = n * math.ceil(math.log2(n)) - 2 ** math.ceil(math.log2(n)) + 1
    print(f" Preprocessing for B - merge sort: {c.comparisons} key comparisons, {c.moves} moves "
          f"(worst-case bound n*ceil(lg n) - 2^ceil(lg n) + 1 = {bound})")
    for start in range(0, n, 5):
        cells = "  ".join(f"[{p:>2}] {sorted_records[p].reg_no}" for p in range(start, min(start + 5, n)))
        print("   " + cells)
    for label, key in (("present", records[3].reg_no), ("absent ", 195_000_000)):
        c, trace = OpCounter(), []
        found = binary_search(sorted_records, key, c, trace)
        print(f"\n Approach B - recursive binary search, {label} key {key}  (trace of the recursive calls)")
        print(f"   {'call':>4} {'low':>4} {'high':>4} {'mid':>4}  {'A[mid]':>10}  decision")
        for step, (lo, hi, mid, mid_key) in enumerate(trace, 1):
            if key == mid_key:
                decision = "key == A[mid] -> FOUND"
            elif key < mid_key:
                decision = f"key <  A[mid] -> recurse on left half  [{lo}..{mid - 1}]"
            else:
                decision = f"key >  A[mid] -> recurse on right half [{mid + 1}..{hi}]"
            print(f"   {step:>4} {lo:>4} {hi:>4} {mid:>4}  {mid_key:>10}  {decision}")
        if found is None:
            print(f"   {len(trace) + 1:>4}  low > high -> empty range (base case) -> NOT FOUND")
        print(f"   three-way comparisons = {c.comparisons}, recursive calls = {c.calls}, "
              f"worst case floor(lg n)+1 = {math.floor(math.log2(n)) + 1}")

    print(line)
    c = OpCounter()
    table = StudentHashTable.build(records, c)
    print(f" Approach C - hash table with separate chaining: m = {table.size} (smallest prime >= 15/0.75), "
          f"alpha = {table.count}/{table.size} = {table.load_factor:.3f}")
    print(f"   build: {c.hash_computations} hash computations + {c.comparisons} duplicate-check comparisons; "
          f"h(k) = k mod {table.size}")
    for index, chain in enumerate(table.buckets):
        if chain:
            print(f"   bucket {index:>2}: " + " -> ".join(str(r.reg_no) for r in chain))
    for label, key in (("present", records[3].reg_no), ("absent ", 195_000_000)):
        c = OpCounter()
        found = table.search(key, c)
        chain = table.buckets[key % table.size]
        length = len(chain) if chain else 0
        print(f"   search {label} key {key}: h = {key % table.size:>2}, chain length {length}, "
              f"{c.comparisons} comparison(s) -> {('FOUND ' + found.name) if found else 'NOT FOUND'}")


if __name__ == "__main__":
    main()
```

#### test_search_algorithms.py

```python
"""
test_search_algorithms.py - test cases for the three search approaches (Task 8).

Problem: every approach must return the correct student record for a present registration number and
None for an absent one, on every dataset size, and must behave as the analysis predicts.

  Part 1  hand-checkable functional test cases (empty, single record, first/last/middle, min/max,
          absent below min / above max / in a gap) run on ALL three approaches
  Part 2  property tests: duplicate handling, merge-sort correctness, exhaustive binary-search worst
          case for n = 1..200, merge-sort comparison bound, hash-table worst case and resizing
  Part 3  bulk validation on the 1,000 / 10,000 / 100,000 / 1,000,000-record datasets with the SAME
          query batch for every approach, checked against a reference Python dict (used only here)
Every check prints a PASS/FAIL line with expected and actual values, and the last line is
"RESULT: k/k tests passed"; the program exits with status 1 if anything fails.
"""
import math
import random
import sys
import time

from search_algorithms import (APPROACHES, OpCounter, StudentHashTable, binary_search,
                               merge_sort_records, sequential_search)
from student_records import StudentRecord, generate_records, make_query_batch

RESULTS = []                                       # one bool per check


def record_result(passed):
    RESULTS.append(passed)
    return "PASS" if passed else "FAIL"


def prepare_all(records):
    """Build the structure each approach searches (A: the list itself, B: sorted copy, C: hash table)."""
    return [(name, prepare(records, OpCounter()), search) for name, prepare, search in APPROACHES]


def run_case(case_id, description, structures, key, expected):
    """Search `key` with all three approaches; `expected` is the reference record or None."""
    cells, ok, counts = [], True, []
    for _, structure, search in structures:
        counter = OpCounter()
        found = search(structure, key, counter)
        ok &= (found is expected) if expected is None else (found is not None and found.reg_no == key
                                                            and found.name == expected.name)
        cells.append(f"{'found' if found else 'none'}({counter.comparisons})")
        counts.append(counter.comparisons)
    exp_text = "found" if expected else "not found"
    print(f"{record_result(ok):<5} {case_id:<5} {description:<34} {key:>10}  {exp_text:<9}  {cells[0]:<10} "
          f"{cells[1]:<10} {cells[2]:<10}")
    return counts


def part1_functional():
    print("PART 1 - functional test cases (actual = result(comparisons) for A: sequential, B: binary, C: hash)")
    print(f"{'':<5} {'ID':<5} {'test case':<34} {'key':>10}  {'expected':<9}  {'A':<10} {'B':<10} {'C':<10}")
    rec = StudentRecord(192425324, "Test Student", "CSE", 9.10)
    run_case("TC01", "empty dataset (n = 0)", prepare_all([]), 192425324, None)
    single = prepare_all([rec])
    run_case("TC02", "single record, key present", single, 192425324, rec)
    run_case("TC03", "single record, absent smaller key", single, 192425323, None)
    run_case("TC04", "single record, absent larger key", single, 192425325, None)

    data = generate_records(15)
    srt = merge_sort_records(data, OpCounter())
    structures = prepare_all(data)
    c05 = run_case("TC05", "first record in stored order", structures, data[0].reg_no, data[0])
    c06 = run_case("TC06", "last record in stored order", structures, data[-1].reg_no, data[-1])
    c07 = run_case("TC07", "middle record of sorted order", structures, srt[7].reg_no, srt[7])
    run_case("TC08", "smallest registration number", structures, srt[0].reg_no, srt[0])
    run_case("TC09", "largest registration number", structures, srt[-1].reg_no, srt[-1])
    rnd = data[random.Random(1).randrange(15)]
    run_case("TC10", "random present key (seed 1)", structures, rnd.reg_no, rnd)
    c11 = run_case("TC11", "absent, below minimum (189999999)", structures, 189_999_999, None)
    run_case("TC12", "absent, above maximum (200000000)", structures, 200_000_000, None)
    run_case("TC13", "absent, in a gap (A[6] + 1)", structures, srt[6].reg_no + 1, None)
    count_checks = [("TC05 sequential best case (key at position 0)", "= 1", c05[0], c05[0] == 1),
                    ("TC06 sequential worst successful (last position)", "= 15", c06[0], c06[0] == 15),
                    ("TC07 binary best case (key at the middle)", "= 1", c07[1], c07[1] == 1),
                    ("TC11 sequential unsuccessful (all n compared)", "= 15", c11[0], c11[0] == 15),
                    ("TC11 binary unsuccessful, floor(lg 15)+1 = 4", "<= 4", c11[1], c11[1] <= 4)]
    for text, expected, actual, ok in count_checks:
        print(f"{record_result(ok):<5} count {text:<50} expected {expected:>4}  actual {actual:>3}")


def exact_binary_success_total(n, memo={0: 0}):
    """S(n) = n + S(floor((n-1)/2)) + S(ceil((n-1)/2)): total comparisons over all n successful searches."""
    if n not in memo:
        left = (n - 1) // 2
        memo[n] = n + exact_binary_success_total(left) + exact_binary_success_total(n - 1 - left)
    return memo[n]


def part2_properties():
    print("\nPART 2 - property tests")
    # P1 duplicates are impossible: re-inserting an existing key replaces the record, count unchanged
    data = generate_records(1_000)
    table = StudentHashTable.build(data, OpCounter())
    updated = StudentRecord(data[10].reg_no, data[10].name, data[10].department, 9.99)
    is_new = table.insert(updated, OpCounter())
    ok = (not is_new) and table.count == 1_000 and table.search(data[10].reg_no, OpCounter()).cgpa == 9.99
    print(f"{record_result(ok):<5} P1  duplicate key re-inserted into hash table: expected count 1000, replaced"
          f"  actual count {table.count}, new={is_new}")

    # P2 merge sort output equals Python's sorted() and the input list is left unchanged
    for n in (15, 1_000, 10_000):
        data = generate_records(n)
        before = [r.reg_no for r in data]
        result = [r.reg_no for r in merge_sort_records(data, OpCounter())]
        ok = result == sorted(before) and [r.reg_no for r in data] == before
        print(f"{record_result(ok):<5} P2  merge sort n = {n:>6,} equals sorted(), input untouched: "
              f"expected True  actual {ok}")

    # P3 exhaustive binary search: every key and every gap for n = 1..200
    worst_ok = avg_ok = bound_ok = True
    rng = random.Random(5)
    for n in range(1, 201):
        keys = [190_000_000 + 2 * i for i in range(n)]            # gaps at odd values
        srt = [StudentRecord(k, "x", "CSE", 8.0) for k in keys]
        worst, total_success = 0, 0
        for probe in range(190_000_000 - 1, 190_000_000 + 2 * n):
            c = OpCounter()
            binary_search(srt, probe, c)
            worst = max(worst, c.comparisons)
            if probe % 2 == 0:
                total_success += c.comparisons
        worst_ok &= worst == math.floor(math.log2(n)) + 1
        avg_ok &= total_success == exact_binary_success_total(n)
        shuffled = srt[:]
        rng.shuffle(shuffled)
        c = OpCounter()
        merge_sort_records(shuffled, c)
        k = math.ceil(math.log2(n)) if n > 1 else 0
        bound_ok &= c.comparisons <= n * k - 2 ** k + 1
    print(f"{record_result(worst_ok):<5} P3  binary search n = 1..200, all keys + gaps: "
          f"max comparisons = floor(lg n)+1: expected True  actual {worst_ok}")
    print(f"{record_result(avg_ok):<5} P3b binary search n = 1..200: "
          f"total successful comparisons = S(n) recurrence: expected True  actual {avg_ok}")
    print(f"{record_result(bound_ok):<5} P4  merge sort n = 1..200: "
          f"comparisons <= n*ceil(lg n) - 2^ceil(lg n) + 1: expected True  actual {bound_ok}")

    # P5 hash-table worst case: every key congruent modulo m -> one chain of length n
    n = 1_000
    table = StudentHashTable(n)
    for i in range(n):
        table.insert(StudentRecord(190_000_000 + i * table.size, "x", "CSE", 8.0), OpCounter())
    c_hit, c_miss = OpCounter(), OpCounter()
    table.search(190_000_000 + (n - 1) * table.size, c_hit)
    table.search(190_000_000 + n * table.size, c_miss)
    longest = max(table.chain_lengths())
    ok = longest == n and c_hit.comparisons == n and c_miss.comparisons == n
    print(f"{record_result(ok):<5} P5  hash worst case, 1,000 keys = 190000000 + i*m: "
          f"expected chain 1000, 1000 cmp  actual {longest}, {c_hit.comparisons}/{c_miss.comparisons}")

    # P6 growth: a table created for 10 records must resize and keep alpha <= 0.75
    table = StudentHashTable(10)
    data = generate_records(2_000)
    max_alpha = 0.0
    for r in data:
        table.insert(r, OpCounter())
        max_alpha = max(max_alpha, table.load_factor)
    ok = max_alpha <= 0.75 and all(table.search(r.reg_no, OpCounter()) is r for r in data)
    print(f"{record_result(ok):<5} P6  dynamic growth 10 -> 2,000 records: expected alpha <= 0.75, all found  "
          f"actual {table.resizes} resizes, max alpha {max_alpha:.3f}")


def part3_bulk(sizes=(1_000, 10_000, 100_000, 1_000_000)):
    print("\nPART 3 - bulk validation: same dataset + same query batch for every approach, "
          "checked against a dict")
    print(f"{'':<5} {'n':>10}  {'approach':<15} {'queries':>9}  {'correct':>11}  {'avg cmp hit':>11}  "
          f"{'avg cmp miss':>12}  invariant")
    master = generate_records(max(sizes))
    for n in sizes:
        records = master[:n]
        reference = {r.reg_no: (pos, r) for pos, r in enumerate(records)}
        present, absent = make_query_batch(records, 500, 500, seed=n, key_set=reference.keys())
        lg = math.floor(math.log2(n)) + 1
        for name, prepare, search in APPROACHES:
            structure = prepare(records, OpCounter())
            hits = present if (name[0] != "S" or n < 1_000_000) else present[:100]
            misses = absent if (name[0] != "S" or n < 1_000_000) else absent[:100]
            correct, cmp_hit, cmp_miss, invariant = 0, 0, 0, True
            for key in hits:
                c = OpCounter()
                found = search(structure, key, c)
                correct += found is reference[key][1]
                cmp_hit += c.comparisons
                if name[0] == "S":
                    invariant &= c.comparisons == reference[key][0] + 1
                elif name[0] == "B":
                    invariant &= c.comparisons <= lg
            for key in misses:
                c = OpCounter()
                correct += search(structure, key, c) is None
                cmp_miss += c.comparisons
                if name[0] == "S":
                    invariant &= c.comparisons == n
                elif name[0] == "B":
                    invariant &= c.comparisons <= lg
            if name[0] == "S":
                inv_text = "hit = pos+1, miss = n"
            elif name[0] == "B":
                inv_text = f"every search <= {lg} cmp"
            else:
                inv_text = f"alpha = {structure.load_factor:.3f} <= 0.75"
                invariant = structure.load_factor <= 0.75
            total = len(hits) + len(misses)
            ok = correct == total and invariant
            print(f"{record_result(ok):<5} {n:>10,}  {name:<15} {total:>9,}  {f'{correct:,}/{total:,}':>11}  "
                  f"{cmp_hit / len(hits):>11.2f}  {cmp_miss / len(misses):>12.2f}  {inv_text}")
            del structure


def main():
    start = time.perf_counter()
    print("=" * 112)
    print(" CO1 Assignment - test cases for sequential search (A), recursive binary search (B) and hashing (C)")
    print("=" * 112)
    part1_functional()
    part2_properties()
    part3_bulk()
    passed = sum(RESULTS)
    print("-" * 112)
    print(f"run time {time.perf_counter() - start:.1f} s")
    print(f"RESULT: {passed}/{len(RESULTS)} tests passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
```

#### run_experiments.py

```python
"""
run_experiments.py - experimental performance of the three search approaches (Tasks 9 and 10).

Problem: measure how sequential search (A), recursive binary search with merge-sort preprocessing (B)
and hashing with separate chaining (C) behave as the database grows from 1,000 to 1,000,000 records,
and compare every measured operation count with the value predicted by the mathematical analysis.

Procedure (identical for every approach):
  * datasets   : nested seed-42 datasets of n = 1,000 / 10,000 / 100,000 / 1,000,000 records
  * queries    : for each n ONE batch of 500 present + 500 absent keys (seed = n) used by all three
                 approaches; sequential search at n = 1,000,000 uses the first 100 + 100 keys of that
                 batch (one search takes 25-55 ms in Python), still at random positions
  * counts     : basic operations counted inside the algorithms (primary evidence)
  * time       : time.perf_counter, garbage collector off while timing, MINIMUM of R repetitions
                 (other processes can only add time, so the minimum is the least disturbed run)
  * memory     : bytes of the search structure (sys.getsizeof accounting; shared records excluded)
  * exhaustive : every stored key searched once with B and C -> exact average vs the closed form
Outputs: CSV tables (Task_9 folder + Report/Tables_and_Graphs) and PNG graphs (Report/Tables_and_Graphs).
"""
import bisect
import csv
import gc
import math
import os
import platform
import statistics
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from search_algorithms import (OpCounter, StudentHashTable, binary_search, hash_search,  # noqa: E402
                               merge_sort_records, next_prime, sequential_search)
from student_records import REG_MAX, REG_MIN, generate_records, make_query_batch  # noqa: E402

SIZES = (1_000, 10_000, 100_000, 1_000_000)
HITS, MISSES = 500, 500
SEQ_QUERIES_AT_1M = 100                  # per type (successful / unsuccessful)
KEY_UNIVERSE = REG_MAX - REG_MIN + 1     # U = 10,000,000 possible registration numbers
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SOURCE_DIR, "..", ".."))
TASK9_DIR = os.path.join(ROOT, "Task_9_Experimental_Performance")
GRAPH_DIR = os.path.join(ROOT, "Report", "Tables_and_Graphs")
COLORS = {"A": "#d62728", "B": "#1f77b4", "C": "#2ca02c"}
NAMES = {"A": "A: sequential search", "B": "B: recursive binary search", "C": "C: hash table (chaining)"}


# ----------------------------------------------------------------------------------------- helpers
def timed(function, repeats):
    """Run function() `repeats` times with the GC disabled; return (minimum seconds, last result)."""
    times, result = [], None
    for _ in range(repeats):
        gc.collect()
        gc.disable()
        try:
            start = time.perf_counter()
            result = function()
            times.append(time.perf_counter() - start)
        finally:
            gc.enable()
    return min(times), result


def search_all(search, structure, keys):
    """The timed loop: search every key of the batch once."""
    counter = OpCounter()
    for key in keys:
        search(structure, key, counter)


def write_csv(name, header, rows):
    """Save a table as CSV in the Task 9 folder and in Report/Tables_and_Graphs."""
    for folder in (TASK9_DIR, GRAPH_DIR):
        with open(os.path.join(folder, name), "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            writer.writerows(rows)


def exact_binary_success_total(n, memo={0: 0}):
    """S(n) = n + S(floor((n-1)/2)) + S(ceil((n-1)/2)) = total three-way comparisons of all n hits."""
    if n not in memo:
        left = (n - 1) // 2
        memo[n] = n + exact_binary_success_total(left) + exact_binary_success_total(n - 1 - left)
    return memo[n]


def hash_pair_sum(m, universe=KEY_UNIVERSE):
    """Sum over buckets of c_j(c_j - 1), where c_j = number of possible keys with h(k) = j."""
    q, r = divmod(universe, m)
    return r * (q + 1) * q + (m - r) * q * (q - 1)


def theory(n, m):
    """Closed-form predictions from Tasks 3-7 (m = hash-table size)."""
    s = exact_binary_success_total(n)
    k = math.ceil(math.log2(n))
    u = KEY_UNIVERSE
    pairs = hash_pair_sum(m)
    return {"A_hit": (n + 1) / 2, "A_miss": n,
            "B_hit": s / n, "B_miss": (s + n) / (n + 1), "B_worst": math.floor(math.log2(n)) + 1,
            # uniform hashing of n keys drawn without replacement from the U = 10^7 possible numbers
            "C_hit": 1 + (n - 1) * pairs / (2 * u * (u - 1)), "C_miss": n * pairs / (u * (u - 1)),
            "C_hit_clrs": 1 + (n - 1) / (2 * m), "C_miss_clrs": n / m,       # textbook limit U -> infinity
            "sort_worst": n * k - 2 ** k + 1, "nlogn": n * math.log2(n),
            "build_cmp": n * (n - 1) / (2 * m), "alpha": n / m}


def measure_search(search, structure, hits, misses, reference, repeats):
    """Count operations per query (verification pass) and time the batch (timed passes)."""
    out = {}
    for label, keys in (("hit", hits), ("miss", misses)):
        counter, per_query, correct = OpCounter(), [], 0
        for key in keys:
            before = counter.comparisons
            found = search(structure, key, counter)
            per_query.append(counter.comparisons - before)
            correct += found is reference.get(key)
        seconds, _ = timed(lambda: search_all(search, structure, keys), repeats)
        out[label] = {"q": len(keys), "avg": sum(per_query) / len(keys), "max": max(per_query),
                      "extra": (counter.calls + counter.hash_computations) / len(keys),
                      "us": seconds / len(keys) * 1e6, "correct": correct}
    return out


def sort_with_counter(records):
    counter = OpCounter()
    return merge_sort_records(records, counter), counter


def build_with_counter(records):
    counter = OpCounter()
    return StudentHashTable.build(records, counter), counter


# ------------------------------------------------------------------------------------- experiment
def run(sizes):
    print("=" * 118)
    print(" CO1 experiments - sequential (A) vs recursive binary (B) vs hashing (C), "
          "1,000 ... 1,000,000 records")
    print(f" Python {platform.python_version()} on {platform.system()} {platform.release()} | perf_counter, "
          f"GC off while timing, minimum of R runs | {HITS}+{MISSES} queries per n "
          f"(A at 10^6: {SEQ_QUERIES_AT_1M}+{SEQ_QUERIES_AT_1M})")
    print("=" * 118)
    master = generate_records(max(sizes))
    res = {}
    for n in sizes:
        t_start = time.perf_counter()
        records = master[:n]
        reference = {r.reg_no: r for r in records}
        hits, misses = make_query_batch(records, HITS, MISSES, seed=n, key_set=reference.keys())
        reps_prep = 3 if n < 1_000_000 else 2
        r = {"n": n}
        # ---- preprocessing
        t_sort, (sorted_records, c_sort) = timed(lambda: sort_with_counter(records), reps_prep)
        t_build, (table, c_build) = timed(lambda: build_with_counter(records), reps_prep)
        r["prep"] = {"B": (c_sort.comparisons, c_sort.moves, t_sort),
                     "C": (c_build.comparisons, c_build.hash_computations, t_build)}
        r["m"], r["alpha"], r["max_chain"] = table.size, table.load_factor, max(table.chain_lengths())
        # ---- searching (same batch for all; A at 10^6 uses the first 100 + 100 keys of it)
        seq_hits = hits if n < 1_000_000 else hits[:SEQ_QUERIES_AT_1M]
        seq_misses = misses if n < 1_000_000 else misses[:SEQ_QUERIES_AT_1M]
        reps_seq = 5 if n <= 10_000 else (3 if n <= 100_000 else 1)
        r["A"] = measure_search(sequential_search, records, seq_hits, seq_misses, reference, reps_seq)
        r["B"] = measure_search(binary_search, sorted_records, hits, misses, reference, 7)
        r["C"] = measure_search(hash_search, table, hits, misses, reference, 7)
        # ---- exhaustive check: every stored key searched once with B and C
        for label, search, structure in (("B", binary_search, sorted_records), ("C", hash_search, table)):
            counter, worst = OpCounter(), 0
            for rec in records:
                before = counter.comparisons
                search(structure, rec.reg_no, counter)
                worst = max(worst, counter.comparisons - before)
            r["exh_" + label] = (counter.comparisons / n, worst)
        # ---- memory of the search structures (the records themselves are shared and excluded)
        per_record = sys.getsizeof(records[0]) + sys.getsizeof(records[0].reg_no)
        r["mem"] = {"records": sys.getsizeof(records) + n * per_record, "A": 0,
                    "B": sys.getsizeof(sorted_records), "B_peak": 2 * sys.getsizeof(sorted_records),
                    "C": table.memory_bytes()}
        # ---- reference: the same ideas implemented in C inside CPython (constant-factor comparison)
        keys_sorted = [rec.reg_no for rec in sorted_records]
        t_sorted, _ = timed(lambda: sorted(records, key=lambda x: x.reg_no), reps_prep)
        t_dict, d = timed(lambda: {rec.reg_no: rec for rec in records}, reps_prep)
        t_bisect, _ = timed(lambda: [bisect.bisect_left(keys_sorted, k) for k in hits], 7)
        t_dget, _ = timed(lambda: [d.get(k) for k in hits], 7)
        r["builtin"] = (t_sorted, t_dict, t_bisect / len(hits) * 1e6, t_dget / len(hits) * 1e6)
        if n == max(sizes):
            r["chains"] = table.chain_lengths()
        res[n] = r
        print(f" n = {n:>9,}: done in {time.perf_counter() - t_start:5.1f} s  (m = {table.size:,}, "
              f"alpha = {table.load_factor:.3f}, longest chain = {r['max_chain']})")
        del sorted_records, table, reference, d, keys_sorted
        gc.collect()
    return res


# ---------------------------------------------------------------------------------------- tables
def report_tables(res, sizes):
    th = {n: theory(n, res[n]["m"]) for n in sizes}
    print("\nTABLE 1 - preprocessing cost (once per dataset)")
    print(f"{'n':>10} | {'B: merge sort cmp':>17} {'n lg n':>12} {'worst bound':>12} {'moves':>11} "
          f"{'time ms':>9} | {'C: hash h(k)':>12} {'chain cmp':>9} {'theory':>9} {'time ms':>8}")
    prep_rows = []
    for n in sizes:
        cb, mv, tb = res[n]["prep"]["B"]
        cc, hc, tc = res[n]["prep"]["C"]
        t = th[n]
        print(f"{n:>10,} | {cb:>17,} {t['nlogn']:>12,.0f} {t['sort_worst']:>12,} {mv:>11,} {tb * 1e3:>9.1f} | "
              f"{hc:>12,} {cc:>9,} {t['build_cmp']:>9,.0f} {tc * 1e3:>8.1f}")
        prep_rows += [[n, "A", 0, 0, 0.0, 0, "no preprocessing"],
                      [n, "B", cb, mv, round(tb * 1e3, 3), t["sort_worst"],
                       "merge sort; other_ops = moves; theory = worst-case bound"],
                      [n, "C", cc, hc, round(tc * 1e3, 3), round(t["build_cmp"], 1),
                       "hash build; other_ops = hash computations; theory = n(n-1)/2m comparisons"]]
    write_csv("preprocessing_cost.csv", ["n", "approach", "comparisons", "other_ops", "time_ms",
                                         "theory_comparisons", "note"], prep_rows)

    print("\nTABLE 2 - search cost per query (average over the batch; time = minimum of R runs)")
    print(f"{'n':>10} {'approach':<4} {'queries':>8} {'avg cmp hit':>12} {'avg cmp miss':>13} {'max cmp':>9} "
          f"{'extra ops/q':>11} {'us/hit':>10} {'us/miss':>10} {'correct':>9}")
    rows = []
    for n in sizes:
        for a in "ABC":
            h, m = res[n][a]["hit"], res[n][a]["miss"]
            ok = h["correct"] + m["correct"] == h["q"] + m["q"]
            print(f"{n:>10,} {a:<4} {h['q'] + m['q']:>8,} {h['avg']:>12,.2f} {m['avg']:>13,.2f} "
                  f"{max(h['max'], m['max']):>9,} {(h['extra'] + m['extra']) / 2:>11.2f} {h['us']:>10,.2f} "
                  f"{m['us']:>10,.2f} {'all' if ok else 'ERROR':>9}")
            rows.append([n, a, h["q"], m["q"], round(h["avg"], 3), round(m["avg"], 3), h["max"], m["max"],
                         round(h["extra"], 3), round(m["extra"], 3), round(h["us"], 3), round(m["us"], 3),
                         round((h["us"] + m["us"]) / 2, 3), ok])
    write_csv("search_performance.csv", ["n", "approach", "hit_queries", "miss_queries", "avg_cmp_hit",
                                         "avg_cmp_miss", "max_cmp_hit", "max_cmp_miss", "extra_ops_hit",
                                         "extra_ops_miss", "time_us_hit", "time_us_miss", "time_us_mixed",
                                         "all_correct"], rows)

    print("\nTABLE 3 - theory vs measurement (average key comparisons per search)")
    print(f"{'n':>10} {'approach':<4} {'theory hit':>12} {'measured':>12} {'ratio':>7} | {'theory miss':>12} "
          f"{'measured':>12} {'ratio':>7}")
    rows = []
    for n in sizes:
        for a in "ABC":
            t_h, t_m = th[n][a + "_hit"], th[n][a + "_miss"]
            m_h, m_m = res[n][a]["hit"]["avg"], res[n][a]["miss"]["avg"]
            print(f"{n:>10,} {a:<4} {t_h:>12,.2f} {m_h:>12,.2f} {m_h / t_h:>7.3f} | {t_m:>12,.2f} "
                  f"{m_m:>12,.2f} {m_m / t_m:>7.3f}")
            rows += [[n, a, "successful", round(t_h, 4), round(m_h, 4), round(m_h / t_h, 4)],
                     [n, a, "unsuccessful", round(t_m, 4), round(m_m, 4), round(m_m / t_m, 4)]]
    write_csv("theory_vs_measured.csv", ["n", "approach", "case", "theory", "measured", "ratio"], rows)

    print("\nTABLE 4 - exhaustive check: every stored key searched once (exact averages)")
    print(f"{'n':>10} | {'B avg meas.':>11} {'S(n)/n':>9} {'B max':>6} {'lg bound':>8} | {'C avg meas.':>11} "
          f"{'model U=1e7':>11} {'1+(n-1)/2m':>11} {'C max':>6} {'alpha':>6}")
    rows = []
    for n in sizes:
        (b_avg, b_max), (c_avg, c_max) = res[n]["exh_B"], res[n]["exh_C"]
        t = th[n]
        print(f"{n:>10,} | {b_avg:>11.4f} {t['B_hit']:>9.4f} {b_max:>6} {t['B_worst']:>8} | {c_avg:>11.4f} "
              f"{t['C_hit']:>11.4f} {t['C_hit_clrs']:>11.4f} {c_max:>6} {t['alpha']:>6.3f}")
        rows.append([n, round(b_avg, 6), round(t["B_hit"], 6), b_max, t["B_worst"], round(c_avg, 6),
                     round(t["C_hit"], 6), round(t["C_hit_clrs"], 6), c_max, round(t["alpha"], 6), res[n]["m"]])
    write_csv("exhaustive_verification.csv", ["n", "B_avg_measured", "B_avg_theory_S(n)/n", "B_max_measured",
                                              "B_worst_theory", "C_avg_measured", "C_avg_theory_finite_U",
                                              "C_avg_theory_clrs", "C_max_comparisons", "alpha", "m"], rows)

    print("\nTABLE 5 - growth when n grows 10x (measured ratios) and log-log slope of time per search vs n")
    print(f"{'n step':>22} | {'A cmp':>7} {'A time':>7} | {'B cmp':>7} {'B time':>7} | {'C cmp':>7} "
          f"{'C time':>7} | {'theory A':>8} {'theory B':>8} {'theory C':>8}")
    rows = []
    for n1, n2 in zip(sizes, sizes[1:]):
        cells, out = [], [f"{n1:,}->{n2:,}"]
        for a in "ABC":
            c1, c2 = mixed(res[n1], a, "avg"), mixed(res[n2], a, "avg")
            t1, t2 = mixed(res[n1], a, "us"), mixed(res[n2], a, "us")
            cells.append(f"{c2 / c1:>7.2f} {t2 / t1:>7.2f}")
            out += [round(c2 / c1, 4), round(t2 / t1, 4)]
        theo = [n2 / n1, math.log2(n2) / math.log2(n1), 1.0]
        print(f"{out[0]:>22} | " + " | ".join(cells) + f" | {theo[0]:>8.2f} {theo[1]:>8.2f} {theo[2]:>8.2f}")
        rows.append(out + [round(x, 4) for x in theo])
    slopes = [loglog_slope(sizes, [mixed(res[n], a, "us") for n in sizes]) for a in "ABC"]
    print(f"{'log-log slope of time':>22} | {slopes[0]:>15.3f} | {slopes[1]:>15.3f} | {slopes[2]:>15.3f} | "
          f"(theory: A = 1, B -> 0 slowly (log n), C = 0)")
    rows.append(["loglog_time_slope", "", round(slopes[0], 4), "", round(slopes[1], 4), "", round(slopes[2], 4),
                 1.0, "", 0.0])
    write_csv("growth_factors.csv", ["n_step", "A_cmp_ratio", "A_time_ratio", "B_cmp_ratio", "B_time_ratio",
                                     "C_cmp_ratio", "C_time_ratio", "theory_A", "theory_B", "theory_C"], rows)

    print("\nTABLE 6 - extra memory of the search structure (records shared, not counted) "
          "and break-even searches")
    print(f"{'n':>10} | {'records MB':>10} {'A':>3} {'B sorted MB':>11} {'B peak MB':>9} {'C table MB':>10} | "
          f"{'A->B q* ops':>11} {'A->B q* time':>12} {'A->C q* ops':>11} {'A->C q* time':>12}")
    mem_rows, be_rows = [], []
    for n in sizes:
        mem = res[n]["mem"]
        be = break_even(res[n])
        print(f"{n:>10,} | {mem['records'] / 1e6:>10.2f} {0:>3} {mem['B'] / 1e6:>11.2f} "
              f"{mem['B_peak'] / 1e6:>9.2f} {mem['C'] / 1e6:>10.2f} | {be[0]:>11.2f} {be[1]:>12.2f} "
              f"{be[2]:>11.2f} {be[3]:>12.2f}")
        mem_rows.append([n, mem["records"], 0, mem["B"], mem["B_peak"], mem["C"], res[n]["m"],
                         round(res[n]["alpha"], 4)])
        be_rows.append([n] + [round(x, 3) for x in be])
    write_csv("memory_usage.csv", ["n", "records_bytes", "A_extra_bytes", "B_sorted_copy_bytes",
                                   "B_peak_extra_bytes_during_sort", "C_table_bytes", "hash_table_size_m",
                                   "alpha"], mem_rows)
    write_csv("break_even.csv", ["n", "A_to_B_by_operations", "A_to_B_by_time", "A_to_C_by_operations",
                                 "A_to_C_by_time"], be_rows)

    print("\nTABLE 7 - reference: the same ideas as C code inside CPython "
          "(shows the interpreter constant factor)")
    print(f"{'n':>10} | {'merge sort ms':>13} {'sorted() ms':>11} {'ratio':>6} | {'hash build ms':>13} "
          f"{'dict ms':>8} {'ratio':>6} | {'B us':>6} {'bisect us':>9} | {'C us':>6} {'dict.get us':>11}")
    rows = []
    for n in sizes:
        t_sorted, t_dict, us_bisect, us_dget = res[n]["builtin"]
        tb, tc = res[n]["prep"]["B"][2], res[n]["prep"]["C"][2]
        ub, uc = res[n]["B"]["hit"]["us"], res[n]["C"]["hit"]["us"]
        print(f"{n:>10,} | {tb * 1e3:>13.1f} {t_sorted * 1e3:>11.1f} {tb / t_sorted:>6.1f} | {tc * 1e3:>13.1f} "
              f"{t_dict * 1e3:>8.1f} {tc / t_dict:>6.1f} | {ub:>6.2f} {us_bisect:>9.3f} | {uc:>6.2f} "
              f"{us_dget:>11.3f}")
        rows.append([n, round(tb * 1e3, 3), round(t_sorted * 1e3, 3), round(tc * 1e3, 3),
                     round(t_dict * 1e3, 3), round(ub, 4), round(us_bisect, 4), round(uc, 4),
                     round(us_dget, 4)])
    write_csv("builtin_reference.csv", ["n", "merge_sort_ms", "builtin_sorted_ms", "hash_build_ms",
                                        "builtin_dict_ms", "binary_us_hit", "bisect_us_hit", "hash_us_hit",
                                        "dict_get_us_hit"], rows)
    return th


def mixed(r, a, key):
    """50/50 mix of successful and unsuccessful searches."""
    return (r[a]["hit"][key] + r[a]["miss"][key]) / 2


def loglog_slope(xs, ys):
    """Least-squares slope of log10(y) against log10(x)."""
    lx, ly = [math.log10(x) for x in xs], [math.log10(y) for y in ys]
    mx, my = statistics.mean(lx), statistics.mean(ly)
    return sum((x - mx) * (y - my) for x, y in zip(lx, ly)) / sum((x - mx) ** 2 for x in lx)


def break_even(r):
    """Number of searches after which preprocessing pays for itself compared with sequential search."""
    ops_a, ops_b = mixed(r, "A", "avg"), mixed(r, "B", "avg")
    ops_c = mixed(r, "C", "avg") + 1                       # + one hash computation per search
    prep_b_ops = r["prep"]["B"][0]
    prep_c_ops = r["prep"]["C"][0] + r["prep"]["C"][1]
    t_a, t_b, t_c = (mixed(r, x, "us") * 1e-6 for x in "ABC")
    return (prep_b_ops / (ops_a - ops_b), r["prep"]["B"][2] / (t_a - t_b),
            prep_c_ops / (ops_a - ops_c), r["prep"]["C"][2] / (t_a - t_c))


# ---------------------------------------------------------------------------------------- graphs
def style(ax, title, xlabel, ylabel, legend_loc="best"):
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8, loc=legend_loc)


def save(fig, name):
    path = os.path.join(GRAPH_DIR, name)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def make_graphs(res, sizes):
    ns = list(sizes)
    dense = sorted({int(round(10 ** (3 + i * 3 / 60))) for i in range(61)})
    dense_th = {n: theory(n, next_prime(math.ceil(n / 0.75))) for n in dense}
    paths = []

    # Figure 1 - comparisons vs n with the theoretical curves
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, case in zip(axes, ("hit", "miss")):
        for a in "ABC":
            ax.plot(ns, [res[n][a][case]["avg"] for n in ns], "o", color=COLORS[a], ms=7,
                    label=NAMES[a] + " (measured)")
        labels = {"hit": ("theory (n+1)/2", "theory S(n)/n ~ log2 n - 1", "theory 1 + alpha/2 (alpha <= 0.75)"),
                  "miss": ("theory n", "theory (S(n)+n)/(n+1) ~ log2 n", "theory alpha (alpha <= 0.75)")}[case]
        for a, label in zip("ABC", labels):
            ax.plot(dense, [dense_th[n][f"{a}_{case}"] for n in dense], "--", color=COLORS[a], label=label)
        ax.set_xscale("log")
        ax.set_yscale("log")
        style(ax, f"{'Successful' if case == 'hit' else 'Unsuccessful'} search: key comparisons vs n",
              "number of records n (log scale)", "average key comparisons per search (log scale)",
              "center right")
    fig.tight_layout()
    paths.append(save(fig, "fig1_comparisons_vs_n.png"))

    # Figure 2 - time per search vs n with fitted theory curves
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    models = {"A": (lambda n: n, "c*n"), "B": (lambda n: math.log2(n), "c*log2 n"), "C": (lambda n: 1.0, "c*1")}
    for a in "ABC":
        ys = [mixed(res[n], a, "us") for n in ns]
        f, label = models[a]
        c = math.exp(statistics.mean(math.log(y / f(n)) for y, n in zip(ys, ns)))
        ax.plot(ns, ys, "o-", color=COLORS[a], ms=7, label=NAMES[a] + " (measured)")
        ax.plot(dense, [c * f(n) for n in dense], "--", color=COLORS[a], alpha=0.7, label=f"fitted {label}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    style(ax, "Time per search vs n (50% successful / 50% unsuccessful)", "number of records n (log scale)",
          "time per search (microseconds, log scale)")
    paths.append(save(fig, "fig2_time_per_search_vs_n.png"))

    # Figure 3 - preprocessing cost
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    ax = axes[0]
    ax.plot(ns, [res[n]["prep"]["B"][0] for n in ns], "o", color=COLORS["B"], ms=7,
            label="B: merge sort comparisons (measured)")
    ax.plot(dense, [n * math.log2(n) for n in dense], "--", color=COLORS["B"], label="n log2 n")
    ax.plot(ns, [res[n]["prep"]["C"][0] + res[n]["prep"]["C"][1] for n in ns], "s", color=COLORS["C"], ms=7,
            label="C: hash computations + chain comparisons (measured)")
    ax.plot(dense, [n + dense_th[n]["build_cmp"] for n in dense], "--", color=COLORS["C"],
            label="n + n(n-1)/2m  (~1.37 n)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    style(ax, "Preprocessing: basic operations vs n", "number of records n (log scale)",
          "operations (log scale)")
    ax = axes[1]
    for a, f, label in (("B", lambda n: n * math.log2(n), "fitted c*n log2 n"),
                        ("C", lambda n: n, "fitted c*n")):
        ys = [res[n]["prep"][a][2] * 1e3 for n in ns]
        c = math.exp(statistics.mean(math.log(y / f(n)) for y, n in zip(ys, ns)))
        ax.plot(ns, ys, "o-", color=COLORS[a], ms=7, label=("B: merge sort" if a == "B" else "C: hash build")
                + " time (measured)")
        ax.plot(dense, [c * f(n) for n in dense], "--", color=COLORS[a], alpha=0.7, label=label)
    ax.set_xscale("log")
    ax.set_yscale("log")
    style(ax, "Preprocessing: time vs n", "number of records n (log scale)", "time (milliseconds, log scale)")
    fig.tight_layout()
    paths.append(save(fig, "fig3_preprocessing_cost.png"))

    # Figure 4 - amortised total cost vs number of searches q
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    rows = []
    qs = sorted({int(round(10 ** (i / 10))) for i in range(0, 71)})
    for ax, n in zip(axes, (ns[0], ns[-1])):
        r = res[n]
        prep = {"A": 0.0, "B": r["prep"]["B"][2], "C": r["prep"]["C"][2]}
        per = {a: mixed(r, a, "us") * 1e-6 for a in "ABC"}
        for a in "ABC":
            ax.plot(qs, [prep[a] + q * per[a] for q in qs], "-", color=COLORS[a], lw=2, label=NAMES[a])
        be = break_even(r)
        for q_star, a, label, offset, align in ((be[1], "B", "A = B", (-10, 10), "right"),
                                                (be[3], "C", "A = C", (10, -14), "left")):
            point = (q_star, prep[a] + q_star * per[a])
            ax.plot(*point, "k*", ms=11)
            ax.annotate(f"{label} at q = {q_star:.0f}", point, textcoords="offset points", xytext=offset,
                        fontsize=8, ha=align)
        ax.axvline(50_000, color="grey", ls=":", lw=1)
        ax.text(50_000, 0.03, " 50,000 searches", transform=ax.get_xaxis_transform(), fontsize=8, color="grey")
        ax.set_xscale("log")
        ax.set_yscale("log")
        style(ax, f"Total cost = preprocessing + q searches (n = {n:,})", "number of searches q (log scale)",
              "total time (seconds, log scale)", "upper left")
        for q in (1, 10, 100, 1_000, 10_000, 50_000, 100_000, 1_000_000):
            rows.append([n, q] + [round(prep[a] + q * per[a], 6) for a in "ABC"])
    fig.tight_layout()
    paths.append(save(fig, "fig4_amortised_cost_vs_searches.png"))
    write_csv("amortised_cost.csv", ["n", "searches_q", "A_total_s", "B_total_s", "C_total_s"], rows)

    # Figure 5 - memory
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.plot(ns, [res[n]["mem"]["records"] / 1e6 for n in ns], "k^-", label="the records themselves (shared)")
    ax.plot(ns, [res[n]["mem"]["B"] / 1e6 for n in ns], "o-", color=COLORS["B"],
            label="B: sorted copy (array of references)")
    ax.plot(ns, [res[n]["mem"]["B_peak"] / 1e6 for n in ns], "o--", color=COLORS["B"], alpha=0.6,
            label="B: peak during merge sort (+ buffer)")
    ax.plot(ns, [res[n]["mem"]["C"] / 1e6 for n in ns], "s-", color=COLORS["C"],
            label="C: bucket array + chains")
    ax.set_xscale("log")
    ax.set_yscale("log")
    style(ax, "Extra memory of the search structure (A needs none)", "number of records n (log scale)",
          "memory (MB, log scale)")
    paths.append(save(fig, "fig5_memory_vs_n.png"))

    # Figure 6 - chain-length distribution: observed vs Poisson vs finite-key-space model
    chains = res[ns[-1]]["chains"]
    m, n = len(chains), ns[-1]
    alpha, p = n / m, n / KEY_UNIVERSE
    q, r = divmod(KEY_UNIVERSE, m)
    xs = list(range(max(chains) + 2))
    observed = [chains.count(L) for L in xs]
    poisson = [m * math.exp(-alpha) * alpha ** L / math.factorial(L) for L in xs]
    finite = [r * binom(q + 1, L, p) + (m - r) * binom(q, L, p) for L in xs]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.bar([x - 0.27 for x in xs], observed, width=0.27, color=COLORS["C"], label="observed buckets")
    ax.bar(xs, finite, width=0.27, color="#9467bd",
           label=f"model: {q}-{q + 1} possible keys per bucket, p = {p}")
    ax.bar([x + 0.27 for x in xs], poisson, width=0.27, color="grey", label=f"Poisson(alpha = {alpha:.3f})")
    ax.set_yscale("log")
    ax.set_ylim(0.5, m)
    style(ax, f"Hash chain lengths at n = {n:,} (m = {m:,})", "chain length L", "number of buckets (log scale)")
    paths.append(save(fig, "fig6_chain_length_distribution.png"))
    write_csv("chain_length_distribution.csv", ["chain_length", "observed_buckets", "finite_key_space_model",
                                                "poisson_expected"],
              [[L, observed[L], round(finite[L], 2), round(poisson[L], 2)] for L in xs])
    return paths


def binom(trials, k, p):
    """Binomial probability P(X = k) for X ~ Bin(trials, p)."""
    return math.comb(trials, k) * p ** k * (1 - p) ** (trials - k) if k <= trials else 0.0


def main():
    start = time.perf_counter()
    res = run(SIZES)
    report_tables(res, SIZES)
    paths = make_graphs(res, SIZES)
    print("\nFiles written: 10 CSV tables (Task_9_Experimental_Performance + Report/Tables_and_Graphs) "
          "and graphs:")
    for i in range(0, len(paths), 3):
        print("  " + ", ".join(os.path.basename(p) for p in paths[i:i + 3]))
    print(f"Total experiment time: {time.perf_counter() - start:.1f} s")


if __name__ == "__main__":
    main()
```

#### design_challenge_simulation.py

```python
"""
design_challenge_simulation.py - Task 12, Day-4 Design Challenge.

Changed requirement: 50,000 search requests per hour on a database of 1,000,000 student records;
new records are added only once per day.  This program measures, on the real 1,000,000-record dataset,
what one day of operation costs for every design and every way of absorbing the daily batch:

  STEP 1  initial preprocessing (paid once at deployment)
  STEP 2  one simulated day: 24 hours x 50,000 searches (80% successful, 20% unsuccessful, seed = hour).
          B and both hash tables execute ALL 1,200,000 searches; sequential search (A) executes the
          first 200 searches of hour 1 and is extrapolated (a full hour would need ~25 min in Python)
  STEP 3  nightly update with a batch of b = 5,000 new records, six strategies:
            A   append to the unsorted list                                  Theta(b)
            B1  re-sort all n + b records with merge sort                     Theta((n+b) log(n+b))
            B2  merge sort the batch only, then merge it into the array       Theta(n + b log b)
            C1  rebuild the whole hash table                                   Theta(n + b)
            C2  insert the batch into the Task-11 table (sized for n)          Theta(b) + a rehash Theta(n)
            C3  insert the batch into a table built with reserved capacity     Theta(b), never rehashes
          every result is verified (new keys found, old keys still found, absent keys rejected)
  STEP 4  day 2: one hour of 50,000 searches that also asks for the new records
  STEP 5  cost per day = nightly update + 24 hours of searching, CPU utilisation, headroom
  STEP 6  sensitivity of the daily cost to the search rate (10 ... 10^7 searches per hour)
Outputs: CSV files (Task_12_Design_Challenge + Report/Tables_and_Graphs) and two graphs.
"""
import csv
import gc
import math
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from search_algorithms import (OpCounter, StudentHashTable, binary_search, hash_search,  # noqa: E402
                               merge_sort_records, merge_sorted_batch, sequential_search)
from student_records import REG_MAX, REG_MIN, generate_new_records, generate_records  # noqa: E402

N_RECORDS = 1_000_000
SEARCHES_PER_HOUR = 50_000
HIT_SHARE = 0.8
DAILY_BATCH = 5_000
RESERVED_CAPACITY = 2_000_000            # C3: room for 200 busy days of 5,000 new records at alpha <= 0.75
SEQ_SAMPLE = 200
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SOURCE_DIR, "..", ".."))
TASK12_DIR = os.path.join(ROOT, "Task_12_Design_Challenge")
GRAPH_DIR = os.path.join(ROOT, "Report", "Tables_and_Graphs")


def write_csv(name, header, rows):
    for folder in (TASK12_DIR, GRAPH_DIR):
        with open(os.path.join(folder, name), "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            writer.writerows(rows)


def hourly_queries(records, key_set, hour):
    """50,000 registration numbers for one hour: 80% stored (random record), 20% absent, shuffled."""
    rng = random.Random(1_000 + hour)
    n_hits = int(SEARCHES_PER_HOUR * HIT_SHARE)
    queries = [records[int(rng.random() * len(records))].reg_no for _ in range(n_hits)]
    while len(queries) < SEARCHES_PER_HOUR:
        key = REG_MIN + int(rng.random() * (REG_MAX - REG_MIN + 1))
        if key not in key_set:
            queries.append(key)
    rng.shuffle(queries)
    return queries, n_hits


def run_searches(search, structure, queries):
    """Execute a batch of searches (GC off); return (comparisons, other ops, seconds, records found)."""
    counter, found = OpCounter(), 0
    gc.collect()
    gc.disable()
    start = time.perf_counter()
    for key in queries:
        if search(structure, key, counter) is not None:
            found += 1
    seconds = time.perf_counter() - start
    gc.enable()
    return counter.comparisons, counter.hash_computations + counter.calls, seconds, found


def timed_update(function):
    """Run one update strategy (GC off) and return (result, counter, seconds)."""
    counter = OpCounter()
    gc.collect()
    gc.disable()
    start = time.perf_counter()
    result = function(counter)
    seconds = time.perf_counter() - start
    gc.enable()
    return result, counter, seconds


def build_reserved(records, counter):
    """C3: hash table created with capacity reserved for RESERVED_CAPACITY records."""
    table = StudentHashTable(RESERVED_CAPACITY)
    for record in records:
        table.insert(record, counter)
    return table


def insert_batch(table, batch, counter):
    for record in batch:
        table.insert(record, counter)
    return table


def verify(search, structure, batch, old_sample, absent_sample):
    """True if every new key and every sampled old key is found and every absent key is rejected."""
    c = OpCounter()
    return (all(search(structure, r.reg_no, c) is r for r in batch)
            and all(search(structure, r.reg_no, c) is r for r in old_sample)
            and all(search(structure, k, c) is None for k in absent_sample))


def main():
    start_all = time.perf_counter()
    print("=" * 112)
    print(f" Day-4 design challenge: {SEARCHES_PER_HOUR:,} searches/hour on {N_RECORDS:,} records, "
          f"{DAILY_BATCH:,} new records once per day")
    print("=" * 112)
    records = generate_records(N_RECORDS)
    key_set = {r.reg_no for r in records}

    # STEP 1 - initial preprocessing (once)
    sorted_records, c_sort, t_sort = timed_update(lambda c: merge_sort_records(records, c))
    table, c_tab, t_tab = timed_update(lambda c: StudentHashTable.build(records, c))
    table3, c_tab3, t_tab3 = timed_update(lambda c: build_reserved(records, c))
    print("STEP 1 - initial preprocessing, paid once at deployment")
    print(f"  B  merge sort of 1,000,000 records        : {c_sort.comparisons:>12,} comparisons "
          f"{t_sort:8.2f} s")
    print(f"  C  hash table sized for n (Task 11 design): {c_tab.hash_computations + c_tab.comparisons:>12,} "
          f"operations  {t_tab:8.2f} s   m = {table.size:,}, alpha = {table.load_factor:.3f}")
    ops3 = c_tab3.hash_computations + c_tab3.comparisons
    print(f"  C3 hash table, capacity for {RESERVED_CAPACITY:,}    : {ops3:>12,} operations  {t_tab3:8.2f} s   "
          f"m = {table3.size:,}, alpha = {table3.load_factor:.3f}")

    # STEP 2 - one simulated day of searching
    print(f"\nSTEP 2 - day 1: 24 hours x {SEARCHES_PER_HOUR:,} searches ({HIT_SHARE:.0%} successful), "
          f"every search executed for B, C and C3")
    print(f"  {'hour':>4} | {'B comparisons':>13} {'B s':>6} | {'C comparisons':>13} {'C s':>6} | "
          f"{'C3 comparisons':>14} {'C3 s':>6} | {'found (B/C/C3)':>20}")
    hourly_rows, day = [], {"B": [0, 0, 0.0], "C": [0, 0, 0.0], "C3": [0, 0, 0.0]}
    for hour in range(1, 25):
        queries, n_hits = hourly_queries(records, key_set, hour)
        out = {"B": run_searches(binary_search, sorted_records, queries),
               "C": run_searches(hash_search, table, queries),
               "C3": run_searches(hash_search, table3, queries)}
        for name, (cmp_, ops, sec, _) in out.items():
            day[name][0] += cmp_
            day[name][1] += ops
            day[name][2] += sec
        ok = all(v[3] == n_hits for v in out.values())
        found = "/".join(f"{v[3]:,}" for v in out.values())
        print(f"  {hour:>4} | {out['B'][0]:>13,} {out['B'][2]:>6.3f} | {out['C'][0]:>13,} "
              f"{out['C'][2]:>6.3f} | {out['C3'][0]:>14,} {out['C3'][2]:>6.3f} | {found:>20} "
              f"{'ok' if ok else 'ERROR'}")
        hourly_rows.append([hour, out["B"][0], round(out["B"][2], 4), out["C"][0], round(out["C"][2], 4),
                            out["C3"][0], round(out["C3"][2], 4), n_hits, ok])
        if hour == 1:
            sample = queries[:SEQ_SAMPLE]
    write_csv("design_challenge_hourly.csv",
              ["hour", "B_comparisons", "B_seconds", "C_comparisons", "C_seconds", "C3_comparisons",
               "C3_seconds", "successful_searches", "all_correct"], hourly_rows)
    a_cmp, _, a_sec, a_found = run_searches(sequential_search, records, sample)
    a_hits = sum(1 for k in sample if k in key_set)
    scale = SEARCHES_PER_HOUR / SEQ_SAMPLE
    print(f"  A sequential: {SEQ_SAMPLE} searches of hour 1 ({a_hits} successful, found {a_found}) -> "
          f"{a_cmp / SEQ_SAMPLE:,.0f} comparisons and {a_sec / SEQ_SAMPLE * 1e3:.1f} ms per search")
    print(f"  A extrapolated to one hour: {a_cmp * scale:,.0f} comparisons, {a_sec * scale:,.0f} s of CPU "
          f"({a_sec * scale / 36:.1f}% of one core)")
    day["A"] = [a_cmp * scale * 24, 0, a_sec * scale * 24]
    for name in ("B", "C", "C3"):
        print(f"  {name:<3} whole day: {day[name][0]:>13,} comparisons, {day[name][2]:7.2f} s "
              f"({day[name][2] / 1_200_000 * 1e6:.2f} us per search)")

    # STEP 3 - nightly update with the daily batch
    batch = generate_new_records(DAILY_BATCH, key_set, seed=2026)
    rng = random.Random(99)
    old_sample = rng.sample(records, 1_000)
    new_key_set = key_set | {r.reg_no for r in batch}
    absent_sample = []
    while len(absent_sample) < 1_000:
        k = REG_MIN + int(rng.random() * (REG_MAX - REG_MIN + 1))
        if k not in new_key_set:
            absent_sample.append(k)
    print(f"\nSTEP 3 - nightly update: b = {DAILY_BATCH:,} new records (seed 2026) added to n = {N_RECORDS:,}")
    print(f"  {'strategy':<52} {'comparisons':>12} {'other ops':>11} {'seconds':>9} {'rehash':>6}  verified")
    updates = {}
    list_a = list(records)
    _, c, sec = timed_update(lambda c: list_a.extend(batch))
    updates["A"] = (0, len(batch), sec, 0, verify(sequential_search, list_a, batch[-20:], old_sample[:20],
                                                   absent_sample[:5]))
    del list_a
    merged_b1, c, sec = timed_update(lambda c: merge_sort_records(records + batch, c))
    updates["B1"] = (c.comparisons, c.moves, sec, 0, verify(binary_search, merged_b1, batch, old_sample,
                                                            absent_sample))
    merged_b2, c, sec = timed_update(lambda c: merge_sorted_batch(sorted_records, batch, c))
    same = [r.reg_no for r in merged_b1] == [r.reg_no for r in merged_b2]
    updates["B2"] = (c.comparisons, c.moves, sec, 0,
                     same and verify(binary_search, merged_b2, batch, old_sample, absent_sample))
    del merged_b1
    rebuilt, c, sec = timed_update(lambda c: StudentHashTable.build(records + batch, c))
    updates["C1"] = (c.comparisons, c.hash_computations, sec, 0, verify(hash_search, rebuilt, batch, old_sample,
                                                                       absent_sample))
    del rebuilt
    _, c, sec = timed_update(lambda c: insert_batch(table, batch, c))
    updates["C2"] = (c.comparisons, c.hash_computations, sec, table.resizes,
                     verify(hash_search, table, batch, old_sample, absent_sample))
    _, c, sec = timed_update(lambda c: insert_batch(table3, batch, c))
    updates["C3"] = (c.comparisons, c.hash_computations, sec, table3.resizes,
                     verify(hash_search, table3, batch, old_sample, absent_sample))
    labels = {"A": "A  append batch to the unsorted list",
              "B1": "B1 re-sort all n + b records (merge sort)",
              "B2": "B2 sort batch, merge into sorted array",
              "C1": "C1 rebuild the whole hash table",
              "C2": "C2 insert batch, Task-11 table sized for n",
              "C3": "C3 insert batch, table with reserved capacity"}
    update_rows = []
    for key, (cmp_, other, sec, rehash, ok) in updates.items():
        print(f"  {labels[key]:<52} {cmp_:>12,} {other:>11,} {sec:>9.4f} {rehash:>6}  "
              f"{'PASS' if ok else 'FAIL'}")
        update_rows.append([key, labels[key][3:], cmp_, other, round(sec, 5), rehash, ok])
    print(f"  after the update: C2 m = {table.size:,} (alpha {table.load_factor:.3f}), C3 m = {table3.size:,} "
          f"(alpha {table3.load_factor:.3f}); B1 array == B2 array: {same}")
    write_csv("design_challenge_updates.csv", ["strategy", "description", "comparisons", "other_ops", "seconds",
                                               "rehashes", "verified"], update_rows)

    # STEP 4 - day 2: the new records are searchable
    all_records = records + batch
    queries, n_hits = hourly_queries(all_records, new_key_set, 25)
    new_asked = sum(1 for k in queries if k in {r.reg_no for r in batch})
    print(f"\nSTEP 4 - day 2, hour 1: {SEARCHES_PER_HOUR:,} searches over {len(all_records):,} records "
          f"({new_asked} of them for new records)")
    for name, search, structure in (("B2", binary_search, merged_b2), ("C3", hash_search, table3)):
        cmp_, _, sec, found = run_searches(search, structure, queries)
        print(f"  {name}: {cmp_:>10,} comparisons, {sec:6.3f} s, found {found:,} of {n_hits:,} "
              f"{'PASS' if found == n_hits else 'FAIL'}")

    # STEP 5 - cost per day
    print("\nSTEP 5 - cost per day = nightly update + 24 h x 50,000 searches (one CPU core, Python)")
    print(f"  {'design':<52} {'ops per day':>15} {'CPU s/day':>10} {'search % core':>13} {'headroom':>9}")
    designs = [("A", "A", "A"), ("B1", "B", "B1"), ("B2", "B", "B2"), ("C1", "C", "C1"), ("C2", "C", "C2"),
               ("C3", "C3", "C3")]
    daily_rows, unit = [], {}
    for name, search_key, update_key in designs:
        u_cmp, u_other, u_sec = updates[update_key][:3]
        ops = day[search_key][0] + day[search_key][1] + u_cmp + u_other
        total = day[search_key][2] + u_sec
        busy = day[search_key][2] / 24 / 3600
        unit[name] = (u_sec, day[search_key][2] / (24 * SEARCHES_PER_HOUR))
        print(f"  {labels[name]:<52} {ops:>15,.0f} {total:>10.2f} {busy * 100:>12.4f}% {1 / busy:>8,.0f}x")
        daily_rows.append([name, labels[name][3:], round(ops), round(u_sec, 5), round(day[search_key][2], 4),
                           round(total, 4), round(busy * 100, 6), round(1 / busy, 1),
                           round(unit[name][1] * 1e6, 4)])
    write_csv("design_challenge_daily_cost.csv", ["design", "description", "operations_per_day",
                                                  "update_seconds",
                                                  "search_seconds_per_day", "total_cpu_seconds_per_day",
                                                  "search_cpu_utilisation_percent", "load_headroom_factor",
                                                  "us_per_search"], daily_rows)

    # STEP 6 - sensitivity to the search rate
    rates = [10 ** (i / 4) for i in range(0, 29)]
    sens_rows = [[round(r, 2)] + [round(unit[d][0] + 24 * r * unit[d][1], 6) for d, _, _ in designs]
                 for r in rates]
    write_csv("design_challenge_sensitivity.csv",
              ["searches_per_hour"] + [f"{d}_cpu_s_per_day" for d, _, _ in designs], sens_rows)
    print("\nSTEP 6 - search rate at which each design's daily cost equals sequential search (A)")
    for d in ("B1", "B2", "C1", "C2", "C3"):
        rate = (unit[d][0] - unit["A"][0]) / (24 * (unit["A"][1] - unit[d][1]))
        if rate > 0:
            print(f"  {labels[d]:<52} pays off above {rate:10.3f} searches per hour")
        else:
            print(f"  {labels[d]:<52} pays off at every rate (its update is no dearer than A's append)")
    make_graphs(daily_rows, rates, unit, designs, labels)
    best = min(daily_rows, key=lambda row: row[5])
    print(f"\nLowest total daily cost: {best[0]} ({best[1]}) = {best[5]:.2f} CPU s/day "
          f"vs {daily_rows[0][5]:,.0f} s/day for sequential search")
    print(f"Total run time {time.perf_counter() - start_all:.1f} s; CSV + graphs written to Task_12 and "
          f"Report/Tables_and_Graphs")


def make_graphs(daily_rows, rates, unit, designs, labels):
    colors = {"A": "#d62728", "B1": "#1f77b4", "B2": "#17becf",
              "C1": "#98df8a", "C2": "#bcbd22", "C3": "#2ca02c"}
    fig, ax = plt.subplots(figsize=(10, 4.8))
    names = [row[0] for row in daily_rows]
    updates = [row[3] for row in daily_rows]
    searches = [row[4] for row in daily_rows]
    y = range(len(names))
    ax.barh([i + 0.2 for i in y], searches, height=0.4, color="#4c72b0", label="24 h of searching (CPU s/day)")
    ax.barh([i - 0.2 for i in y], updates, height=0.4, color="#dd8452", label="nightly update (CPU s/day)")
    for i, (s, u) in enumerate(zip(searches, updates)):
        ax.text(s * 1.15, i + 0.2, f"{s:,.2f} s", va="center", fontsize=8)
        ax.text(u * 1.15, i - 0.2, f"{u:,.4f} s", va="center", fontsize=8)
    ax.set_yticks(list(y))
    ax.set_yticklabels([labels[n] for n in names], fontsize=8)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(1e-4, 1e6)
    ax.set_xlabel("CPU seconds per day (log scale)")
    ax.set_title("Cost of one day: 1,200,000 searches + one batch of 5,000 new records (n = 1,000,000)",
                 fontsize=11)
    ax.grid(True, axis="x", which="both", alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(GRAPH_DIR, "fig7_daily_cost_by_design.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.2))
    for d, _, _ in designs:
        ax.plot(rates, [unit[d][0] + 24 * r * unit[d][1] for r in rates], color=colors[d], lw=2,
                label=labels[d])
    ax.axvline(SEARCHES_PER_HOUR, color="grey", ls=":", lw=1)
    ax.text(SEARCHES_PER_HOUR, 0.97, " 50,000 searches/hour", transform=ax.get_xaxis_transform(), fontsize=8,
            color="grey", va="top")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("search requests per hour (log scale)")
    ax.set_ylabel("CPU seconds per day (log scale)")
    ax.set_title("Daily cost vs search frequency (measured unit costs, n = 1,000,000, b = 5,000/day)",
                 fontsize=11)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(GRAPH_DIR, "fig8_daily_cost_vs_search_rate.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
```

### Appendix B – Graph Scripts: diagram programs

The performance graphs (Figures 23–26 and 29–32) are drawn by `run_experiments.py` and `design_challenge_simulation.py` (Appendix A). The three programs below draw the flowcharts (Figures 1–3), the decision tree (Figure 4) and the recursion trees (Figure 5).

#### Task_1_Algorithm_Design/draw_flowcharts.py

```python
"""
draw_flowcharts.py - draws the flowcharts of the three search approaches (Task 1).

Problem: Task 1 asks for pseudocode or a flowchart for every approach.  This script draws standard
flowchart symbols with matplotlib (terminal = rounded, process = rectangle, decision = diamond,
input/output = parallelogram, predefined process / recursive call = rectangle with side bars) and
writes flowchart_A_sequential_search.png, flowchart_B_recursive_binary_search.png and
flowchart_C_hash_table.png next to this file.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FILL = {"terminal": "#d9ead3", "process": "#dbe8f6", "decision": "#fff2cc", "io": "#e8dff5",
        "call": "#fde3cf"}


class Node:
    """A flowchart symbol centred at (x, y) with width w and height h."""

    def __init__(self, ax, x, y, text, kind="process", w=3.6, h=0.8, size=9):
        self.x, self.y, self.w, self.h = x, y, w, h
        style = dict(facecolor=FILL[kind], edgecolor="#333333", linewidth=1.2)
        if kind == "terminal":
            ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                        boxstyle=f"round,pad=0,rounding_size={h / 2}", **style))
        elif kind == "decision":
            ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)], **style))
        elif kind == "io":
            s = 0.25
            ax.add_patch(Polygon([(x - w / 2 + s, y + h / 2), (x + w / 2 + s, y + h / 2),
                                  (x + w / 2 - s, y - h / 2), (x - w / 2 - s, y - h / 2)], **style))
        else:
            ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, **style))
            if kind == "call":
                for dx in (0.18, w - 0.18):
                    ax.plot([x - w / 2 + dx] * 2, [y - h / 2, y + h / 2], color="#333333", lw=1.0)
        ax.text(x, y, text, ha="center", va="center", fontsize=size)

    def top(self):
        return (self.x, self.y + self.h / 2)

    def bottom(self):
        return (self.x, self.y - self.h / 2)

    def left(self):
        return (self.x - self.w / 2, self.y)

    def right(self):
        return (self.x + self.w / 2, self.y)


def arrow(ax, points, label=None, label_at=0, dx=0.12, dy=0.12, dashed=False):
    """Draw a polyline through `points` with an arrow head at the end; optional label near a vertex."""
    xs, ys = zip(*points)
    ax.plot(xs, ys, color="#333333", lw=1.2, ls="--" if dashed else "-")
    ax.annotate("", xy=points[-1], xytext=points[-2],
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2, shrinkA=0, shrinkB=0))
    if label:
        x, y = points[label_at]
        ax.text(x + dx, y + dy, label, fontsize=9, fontweight="bold", color="#7f3f00")


def new_canvas(width, y_low, y_high, title):
    fig, ax = plt.subplots(figsize=(width * 0.62, (y_high - y_low) * 0.62))
    ax.set_xlim(0, width)
    ax.set_ylim(y_low, y_high)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold")
    return fig, ax


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(path)


def flowchart_sequential():
    fig, ax = new_canvas(10, 2.6, 14.4, "Approach A - Iterative Sequential Search (no preprocessing)")
    start = Node(ax, 5, 13.6, "Start", "terminal", w=2.2)
    inp = Node(ax, 5, 12.4, "Input: records A[0..n-1] (unsorted), key", "io", w=6.2)
    init = Node(ax, 5, 11.1, "i <- 0", "process", w=2.4)
    d1 = Node(ax, 5, 9.6, "i < n ?", "decision", w=2.8, h=1.3)
    d2 = Node(ax, 5, 7.4, "A[i].reg_no = key ?\n(basic operation)", "decision", w=4.2, h=1.8)
    inc = Node(ax, 8.6, 7.4, "i <- i + 1", "process", w=2.0)
    found = Node(ax, 5.3, 5.3, "Output: return A[i]\n(record found)", "io", w=3.4, h=1.0)
    notf = Node(ax, 1.6, 5.3, "Output: return\nNOT FOUND", "io", w=2.6, h=1.0)
    end = Node(ax, 5.3, 3.9, "End", "terminal", w=2.2)
    arrow(ax, [start.bottom(), inp.top()])
    arrow(ax, [inp.bottom(), init.top()])
    arrow(ax, [init.bottom(), d1.top()])
    arrow(ax, [d1.bottom(), d2.top()], "Yes", 0)
    arrow(ax, [d2.right(), inc.left()], "No", 0, dy=0.15)
    arrow(ax, [inc.top(), (inc.x, d1.y), d1.right()])
    arrow(ax, [d1.left(), (notf.x, d1.y), notf.top()], "No", 0, dx=-0.6)
    arrow(ax, [d2.bottom(), (d2.x, 6.2), (found.x, 6.2), found.top()], "Yes", 0)
    arrow(ax, [found.bottom(), end.top()])
    arrow(ax, [notf.bottom(), (notf.x, end.y), end.left()])
    ax.text(5, 2.9, "Successful search at position i: i + 1 comparisons;  unsuccessful: n comparisons",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "flowchart_A_sequential_search.png")


def flowchart_binary():
    fig, ax = new_canvas(11, -0.1, 17.9, "Approach B - Recursive Binary Search (preprocessing: merge sort)")
    start = Node(ax, 5.5, 17.2, "Start", "terminal", w=2.2)
    inp = Node(ax, 5.5, 16.15, "Input: records (unsorted), key", "io", w=5.4)
    pre = Node(ax, 5.5, 15.0, "Preprocessing (once): A <- MergeSort(records by reg_no)\nTheta(n log n)",
               "call", w=7.4, h=1.0)
    call = Node(ax, 5.5, 13.8, "result <- BinSearch(A, key, 0, n-1)", "call", w=5.6)
    out = Node(ax, 5.5, 12.75, "Output: result (record or NOT FOUND)", "io", w=5.6)
    end = Node(ax, 5.5, 11.75, "End", "terminal", w=2.2)
    for a, b in ((start, inp), (inp, pre), (pre, call), (call, out), (out, end)):
        arrow(ax, [a.bottom(), b.top()])
    ax.add_patch(Rectangle((0.25, 0.2), 10.5, 10.85, fill=False, ls="--", lw=1.0, ec="#555555"))
    ax.text(0.45, 10.7, "function BinSearch(A, key, low, high)", fontsize=9, style="italic")
    entry = Node(ax, 5.5, 9.95, "BinSearch(A, key, low, high)", "terminal", w=4.6)
    arrow(ax, [call.right(), (9.6, call.y), (9.6, 10.6), (6.4, 10.6), (6.4, entry.y + entry.h / 2)],
          "first call", 1, dx=0.1, dy=-0.35, dashed=True)
    d1 = Node(ax, 5.5, 8.65, "low > high ?", "decision", w=3.0, h=1.3)
    base = Node(ax, 2.0, 8.65, "return NOT FOUND\n(base case)", "terminal", w=2.8, h=1.0, size=8.5)
    mid = Node(ax, 5.5, 7.25, "mid <- floor((low + high) / 2)", "process", w=3.9)
    d2 = Node(ax, 5.5, 5.65, "key = A[mid].reg_no ?\n(one 3-way comparison)", "decision", w=4.4, h=1.7)
    found = Node(ax, 9.25, 5.65, "return A[mid]\n(found)", "terminal", w=2.4, h=1.0, size=8.5)
    d3 = Node(ax, 5.5, 3.95, "key < A[mid].reg_no ?", "decision", w=4.2, h=1.3)
    left = Node(ax, 2.45, 2.3, "return BinSearch(A, key,\nlow, mid-1)", "call", w=3.6, h=1.0, size=8.5)
    right = Node(ax, 8.55, 2.3, "return BinSearch(A, key,\nmid+1, high)", "call", w=3.6, h=1.0, size=8.5)
    arrow(ax, [entry.bottom(), d1.top()])
    arrow(ax, [d1.left(), base.right()], "Yes", 0, dx=-0.55, dy=0.15)
    arrow(ax, [d1.bottom(), mid.top()], "No", 0)
    arrow(ax, [mid.bottom(), d2.top()])
    arrow(ax, [d2.right(), found.left()], "Yes", 0, dx=0.02, dy=0.15)
    arrow(ax, [d2.bottom(), d3.top()], "No", 0)
    arrow(ax, [d3.left(), (left.x, d3.y), left.top()], "Yes", 0, dx=-0.7)
    arrow(ax, [d3.right(), (right.x, d3.y), right.top()], "No", 0, dx=0.2)
    arrow(ax, [left.left(), (0.45, left.y), (0.45, entry.y), entry.left()], "recursive call", 1,
          dx=0.1, dy=1.2, dashed=True)
    arrow(ax, [right.right(), (10.55, right.y), (10.55, entry.y), entry.right()], dashed=True)
    ax.text(5.5, 0.75, "exactly ONE recursive call per activation, on a half of size <= floor(n/2)",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "flowchart_B_recursive_binary_search.png")


def flowchart_hash():
    fig, ax = new_canvas(16, 1.2, 14.5,
                         "Approach C - Hash Table with Separate Chaining (build once, then search)")
    ax.text(3.2, 13.9, "Preprocessing: Build(records)", ha="center", fontsize=10, fontweight="bold")
    ax.text(11.2, 13.9, "Search(T, key)", ha="center", fontsize=10, fontweight="bold")
    b0 = Node(ax, 3.2, 13.0, "Start", "terminal", w=2.2)
    b1 = Node(ax, 3.2, 11.7, "m <- smallest prime >= n / 0.75\nT[0..m-1] <- empty chains", "process",
              w=5.0, h=1.0)
    b2 = Node(ax, 3.2, 10.0, "another record r ?", "decision", w=3.8, h=1.4)
    b3 = Node(ax, 3.2, 8.3, "j <- r.reg_no mod m\n(one hash computation)", "process", w=4.4, h=1.0)
    b4 = Node(ax, 3.2, 6.8, "append r to chain T[j]\n(replace if the key is already there)", "process",
              w=5.0, h=1.0)
    b5 = Node(ax, 3.2, 4.9, "End: table T ready\n(alpha = n / m <= 0.75)", "terminal", w=4.4, h=1.0)
    arrow(ax, [b0.bottom(), b1.top()])
    arrow(ax, [b1.bottom(), b2.top()])
    arrow(ax, [b2.bottom(), b3.top()], "Yes", 0)
    arrow(ax, [b3.bottom(), b4.top()])
    arrow(ax, [b4.left(), (0.3, b4.y), (0.3, b2.y), b2.left()])
    arrow(ax, [b2.right(), (5.95, b2.y), (5.95, b5.y), b5.right()], "No", 0, dx=0.05)

    s0 = Node(ax, 11.2, 13.0, "Start", "terminal", w=2.2)
    s1 = Node(ax, 11.2, 11.7, "j <- key mod m\n(one hash computation)", "process", w=4.2, h=1.0)
    s2 = Node(ax, 11.2, 10.3, "p <- first record of chain T[j]", "process", w=4.6)
    s3 = Node(ax, 11.2, 8.9, "p = null ?", "decision", w=2.8, h=1.3)
    s4 = Node(ax, 11.2, 6.9, "p.reg_no = key ?\n(basic operation)", "decision", w=3.6, h=1.7)
    s5 = Node(ax, 7.4, 6.9, "p <- next record\nin the chain", "process", w=2.4, h=1.0, size=8.5)
    s6 = Node(ax, 11.2, 4.9, "Output: return p\n(found)", "io", w=3.0, h=1.0)
    s7 = Node(ax, 14.4, 4.9, "Output: return\nNOT FOUND", "io", w=2.5, h=1.0)
    s8 = Node(ax, 12.8, 3.2, "End", "terminal", w=2.2)
    arrow(ax, [s0.bottom(), s1.top()])
    arrow(ax, [s1.bottom(), s2.top()])
    arrow(ax, [s2.bottom(), s3.top()])
    arrow(ax, [s3.bottom(), s4.top()], "No", 0)
    arrow(ax, [s3.right(), (s7.x, s3.y), s7.top()], "Yes", 0)
    arrow(ax, [s4.left(), s5.right()], "No", 0, dx=-0.65, dy=0.15)
    arrow(ax, [s5.top(), (s5.x, s3.y), s3.left()])
    arrow(ax, [s4.bottom(), s6.top()], "Yes", 0)
    arrow(ax, [s6.bottom(), (s6.x, s8.y), s8.left()])
    arrow(ax, [s7.bottom(), (s7.x, s8.y), s8.right()])
    ax.text(8, 1.8, "Expected key comparisons: successful 1 + alpha/2, unsuccessful alpha  ->  Theta(1) when "
            "alpha <= 0.75;  worst case (all keys in one chain): n", ha="center", fontsize=8.5, style="italic")
    save(fig, "flowchart_C_hash_table.png")


def main():
    flowchart_sequential()
    flowchart_binary()
    flowchart_hash()


if __name__ == "__main__":
    main()
```

#### Task_4_Case_Analysis/draw_decision_tree.py

```python
"""
draw_decision_tree.py - binary-search decision tree for n = 15 (Task 4, best/average/worst case).

Problem: the cases of binary search are easiest to see on its decision tree: every internal node is
one three-way comparison key : A[mid]; a successful search for the key stored at a node at depth d
(root depth 1) costs d comparisons; an unsuccessful search ends in an external node (a gap) after
passing through every internal node on its path.  The script computes the tree with exactly the same
mid = (low + high) // 2 rule as search_algorithms.binary_search_recursive, draws it, prints the
level counts, and writes binary_search_decision_tree.png next to this file.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
N = 15


def build(low, high, depth, x_left, x_right, nodes, gaps):
    """Record (index, depth, x) of every mid chosen for the range [low..high] and every gap."""
    if low > high:
        gaps.append((depth, (x_left + x_right) / 2, low))
        return
    mid = (low + high) // 2
    x = (x_left + x_right) / 2
    nodes.append((mid, depth, x))
    build(low, mid - 1, depth + 1, x_left, x, nodes, gaps)
    build(mid + 1, high, depth + 1, x, x_right, nodes, gaps)


def main():
    nodes, gaps = [], []
    build(0, N - 1, 1, 0.0, 16.0, nodes, gaps)
    position = {mid: (x, depth) for mid, depth, x in nodes}
    fig, ax = plt.subplots(figsize=(12, 6.2))
    for mid, depth, x in nodes:                       # edges to the children
        for child in nodes:
            if child[1] == depth + 1 and abs(child[2] - x) < 16 / 2 ** depth:
                ax.plot([x, child[2]], [-depth, -child[1]], color="#555555", lw=1, zorder=1)
    for depth, x, low in gaps:
        parent = min((p for p in nodes if p[1] == depth - 1), key=lambda p: abs(p[2] - x))
        ax.plot([parent[2], x], [-parent[1], -depth + 0.25], color="#bbbbbb", lw=0.8, ls="--", zorder=1)
        ax.add_patch(plt.Rectangle((x - 0.18, -depth + 0.07), 0.36, 0.3, fc="#f4cccc", ec="#990000", zorder=2))
    colors = {1: "#b6d7a8", 2: "#cfe2f3", 3: "#fff2cc", 4: "#f9cb9c"}
    for mid, depth, x in nodes:
        ax.scatter([x], [-depth], s=1250, color=colors[depth], edgecolors="#333333", zorder=3)
        ax.text(x, -depth, f"A[{mid}]", ha="center", va="center", fontsize=8.5, zorder=4)
    levels = {}
    for _, depth, _ in nodes:
        levels[depth] = levels.get(depth, 0) + 1
    total = 0
    for depth in sorted(levels):
        total += depth * levels[depth]
        ax.text(16.6, -depth, f"level {depth}: {levels[depth]} key(s) x {depth} comparison(s) = "
                f"{depth * levels[depth]}", va="center", fontsize=9)
    gap_depth = "/".join(str(d) for d in sorted({d - 1 for d, _, _ in gaps}))
    ax.text(16.6, -4.75, f"{len(gaps)} gaps (unsuccessful searches): {gap_depth} comparisons each",
            va="center", fontsize=9, color="#990000")
    ax.text(16.6, -5.35, f"successful: best 1, worst {max(levels)}, average {total}/{N} = {total / N:.2f}",
            va="center", fontsize=9, fontweight="bold")
    ax.set_xlim(-0.5, 25.5)
    ax.set_ylim(-5.8, -0.4)
    ax.axis("off")
    ax.set_title(f"Decision tree of recursive binary search for n = {N} (mid = (low + high) // 2): "
                 "depth = number of three-way comparisons", fontsize=11)
    path = os.path.join(OUT_DIR, "binary_search_decision_tree.png")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"levels {levels}, total successful comparisons {total}, average {total / N:.4f}")
    print(path)


if __name__ == "__main__":
    main()
```

#### Task_7_Recurrence_Solution/draw_recursion_trees.py

```python
"""
draw_recursion_trees.py - recursion trees used to solve the recurrences in Task 7.

Problem: show the level-by-level cost of
  (a) recursive binary search   C(n) = C(floor(n/2)) + 1, C(0) = 0   -> one node per level, cost 1 each
  (b) merge sort preprocessing   C(n) = 2 C(n/2) + (n - 1), C(1) = 0
                                 -> 2^i nodes on level i, level cost n - 2^i
and print the level sums for n = 16 (so the drawing can be checked by hand).
Writes recursion_trees.png next to this file.
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
N = 16


def box(ax, x, y, text, color, w=1.5, h=0.6, size=11):
    ax.add_patch(plt.Rectangle((x - w / 2, y - h / 2), w, h, fc=color, ec="#333333", lw=1.1, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=size, zorder=3)


def binary_tree_panel(ax):
    sizes = []
    m = N
    while m >= 1:
        sizes.append(m)
        m //= 2
    for level, size in enumerate(sizes):
        y = -level * 1.15
        box(ax, 1.5, y, f"C({size})", "#cfe2f3")
        if level:
            ax.annotate("", xy=(1.5, y + 0.3), xytext=(1.5, y + 0.85),
                        arrowprops=dict(arrowstyle="-|>", color="#333333"))
        ax.text(2.6, y, f"level {level}: 1 subproblem of size {size} -> 1 comparison", va="center",
                fontsize=11)
    y = -len(sizes) * 1.15
    box(ax, 1.5, y, "C(0) = 0", "#f4cccc")
    ax.annotate("", xy=(1.5, y + 0.3), xytext=(1.5, y + 0.85),
                arrowprops=dict(arrowstyle="-|>", color="#333333"))
    ax.text(2.6, y, "empty range: base case, 0 comparisons", va="center", fontsize=11, color="#990000")
    ax.text(0.3, y - 1.2, f"Total = 1 per level x (floor(log2 {N}) + 1) levels = {len(sizes)} comparisons\n"
            f"In general C(n) = floor(log2 n) + 1  ->  Theta(log n)", fontsize=12, fontweight="bold")
    ax.set_xlim(0, 10)
    ax.set_ylim(y - 1.8, 0.8)
    ax.axis("off")
    ax.set_title("(a) Recursive binary search (worst case):  C(n) = C(floor(n/2)) + 1", fontsize=13)
    print(f"(a) binary search, n = {N}: levels {sizes} -> total {len(sizes)} = floor(log2 n) + 1 = "
          f"{math.floor(math.log2(N)) + 1}")


def merge_tree_panel(ax):
    levels = int(math.log2(N))
    total = 0
    width = 12.0
    for level in range(levels + 1):
        count, size = 2 ** level, N // 2 ** level
        y = -level * 1.3
        for i in range(count):
            x = width * (i + 0.5) / count
            w = min(1.5, width / count * 0.85)
            box(ax, x, y, f"{size}" if count > 4 else f"C({size})", "#d9ead3" if size > 1 else "#f4cccc", w=w,
                size=10 if count > 4 else 11)
            if level:
                parent_x = width * (i // 2 + 0.5) / (count // 2)
                ax.plot([parent_x, x], [y + 1.3 - 0.28, y + 0.28], color="#777777", lw=0.8, zorder=1)
        cost = count * (size - 1) if size > 1 else 0
        total += cost
        label = (f"level {level}: {count} x merge of size {size} -> {count} x ({size} - 1) = {cost}"
                 if size > 1 else f"level {level}: {count} single records, base case -> 0")
        ax.text(width + 0.4, y, label, va="center", fontsize=11)
    bound = N * levels - N + 1
    ax.text(0, -(levels + 1) * 1.3 - 0.3, f"Total (worst case) = sum over levels of (n - 2^i) = {total} = "
            f"n log2 n - n + 1 = {bound}\nIn general C(n) = n log2 n - n + 1  ->  Theta(n log n)",
            fontsize=12, fontweight="bold")
    ax.set_xlim(-0.2, 23)
    ax.set_ylim(-(levels + 1) * 1.3 - 1.0, 0.8)
    ax.axis("off")
    ax.set_title("(b) Merge-sort preprocessing (worst case):  C(n) = 2 C(n/2) + (n - 1)", fontsize=13)
    print(f"(b) merge sort, n = {N}: total worst-case comparisons {total} = n log2 n - n + 1 = {bound}")


def main():
    fig, axes = plt.subplots(2, 1, figsize=(11, 12.5), gridspec_kw={"height_ratios": [1, 1.05]})
    binary_tree_panel(axes[0])
    merge_tree_panel(axes[1])
    fig.suptitle(f"Recursion trees for n = {N}", fontsize=14, fontweight="bold")
    fig.tight_layout()
    path = os.path.join(OUT_DIR, "recursion_trees.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(path)


if __name__ == "__main__":
    main()
```

### Appendix C – Raw Experimental Data

Every CSV file written by the experiment programs, unedited (copies are also in `Report/Tables_and_Graphs/`).

#### Task_9_Experimental_Performance/preprocessing_cost.csv

```
n,approach,comparisons,other_ops,time_ms,theory_comparisons,note
1000,A,0,0,0.0,0,no preprocessing
1000,B,8744,19358,1.383,8977,merge sort; other_ops = moves; theory = worst-case bound
1000,C,344,1000,0.354,367.0,hash build; other_ops = hash computations; theory = n(n-1)/2m comparisons
10000,A,0,0,0.0,0,no preprocessing
10000,B,120491,261799,35.345,123617,merge sort; other_ops = moves; theory = worst-case bound
10000,C,3868,10000,3.34,3748.6,hash build; other_ops = hash computations; theory = n(n-1)/2m comparisons
100000,A,0,0,0.0,0,no preprocessing
100000,B,1536197,3282893,262.168,1568929,merge sort; other_ops = moves; theory = worst-case bound
100000,C,37297,100000,63.431,37498.6,hash build; other_ops = hash computations; theory = n(n-1)/2m comparisons
1000000,A,0,0,0.0,0,no preprocessing
1000000,B,18674803,39298156,5846.824,18951425,merge sort; other_ops = moves; theory = worst-case bound
1000000,C,326797,1000000,742.121,374993.0,hash build; other_ops = hash computations; theory = n(n-1)/2m comparisons
```

#### Task_9_Experimental_Performance/search_performance.csv

```
n,approach,hit_queries,miss_queries,avg_cmp_hit,avg_cmp_miss,max_cmp_hit,max_cmp_miss,extra_ops_hit,extra_ops_miss,time_us_hit,time_us_miss,time_us_mixed,all_correct
1000,A,500,500,496.246,1000.0,1000,1000,0.0,0.0,15.053,31.912,23.482,True
1000,B,500,500,8.976,9.978,10,10,8.976,10.978,1.523,1.708,1.616,True
1000,C,500,500,1.342,0.762,5,5,1.0,1.0,0.264,0.249,0.256,True
10000,A,500,500,4966.628,10000.0,9994,10000,0.0,0.0,170.742,355.567,263.155,True
10000,B,500,500,12.308,13.338,14,14,12.308,14.338,2.382,2.733,2.558,True
10000,C,500,500,1.392,0.696,6,4,1.0,1.0,0.5,0.369,0.434,True
100000,A,500,500,51226.358,100000.0,99913,100000,0.0,0.0,2081.58,4420.728,3251.154,True
100000,B,500,500,15.636,16.746,17,17,15.636,17.746,4.12,4.579,4.349,True
100000,C,500,500,1.334,0.666,4,5,1.0,1.0,0.656,0.468,0.562,True
1000000,A,100,100,480558.07,1000000.0,999764,1000000,0.0,0.0,22536.823,51240.99,36888.907,True
1000000,B,500,500,18.874,19.948,20,20,18.874,20.948,6.236,7.063,6.65,True
1000000,C,500,500,1.322,0.682,4,3,1.0,1.0,0.881,0.618,0.749,True
```

#### Task_9_Experimental_Performance/theory_vs_measured.csv

```
n,approach,case,theory,measured,ratio
1000,A,successful,500.5,496.246,0.9915
1000,A,unsuccessful,1000,1000.0,1.0
1000,B,successful,8.987,8.976,0.9988
1000,B,unsuccessful,9.977,9.978,1.0001
1000,C,successful,1.367,1.342,0.9817
1000,C,unsuccessful,0.7347,0.762,1.0372
10000,A,successful,5000.5,4966.628,0.9932
10000,A,unsuccessful,10000,10000.0,1.0
10000,B,successful,12.3631,12.308,0.9955
10000,B,unsuccessful,13.3618,13.338,0.9982
10000,C,successful,1.3744,1.392,1.0128
10000,C,unsuccessful,0.7488,0.696,0.9295
100000,A,successful,50000.5,51226.358,1.0245
100000,A,unsuccessful,100000,100000.0,1.0
100000,B,successful,15.6895,15.636,0.9966
100000,B,unsuccessful,16.6893,16.746,1.0034
100000,C,successful,1.37,1.334,0.9737
100000,C,unsuccessful,0.74,0.666,0.9
1000000,A,successful,500000.5,480558.07,0.9611
1000000,A,unsuccessful,1000000,1000000.0,1.0
1000000,B,successful,18.9514,18.874,0.9959
1000000,B,unsuccessful,19.9514,19.948,0.9998
1000000,C,successful,1.3267,1.322,0.9965
1000000,C,unsuccessful,0.6533,0.682,1.0439
```

#### Task_9_Experimental_Performance/exhaustive_verification.csv

```
n,B_avg_measured,B_avg_theory_S(n)/n,B_max_measured,B_worst_theory,C_avg_measured,C_avg_theory_finite_U,C_avg_theory_clrs,C_max_comparisons,alpha,m
1000,8.987,8.987,10,10,1.344,1.36696,1.36701,5,0.734754,1361
10000,12.3631,12.3631,14,14,1.3868,1.37436,1.374859,7,0.749794,13337
100000,15.68946,15.68946,17,17,1.37297,1.369986,1.374986,8,0.749979,133337
1000000,18.951445,18.951445,20,20,1.326797,1.32666,1.374993,6,0.749987,1333357
```

#### Task_9_Experimental_Performance/growth_factors.csv

```
n_step,A_cmp_ratio,A_time_ratio,B_cmp_ratio,B_time_ratio,C_cmp_ratio,C_time_ratio,theory_A,theory_B,theory_C
"1,000->10,000",10.0028,11.2065,1.3531,1.583,0.9924,1.6946,10.0,1.3333,1.0
"10,000->100,000",10.1042,12.3545,1.2627,1.7004,0.9579,1.2928,10.0,1.25,1.0
"100,000->1,000,000",9.7903,11.3464,1.1989,1.5289,1.002,1.3343,10.0,1.2,1.0
loglog_time_slope,,1.068,,0.2074,,0.1509,1.0,,0.0
```

#### Task_9_Experimental_Performance/memory_usage.csv

```
n,records_bytes,A_extra_bytes,B_sorted_copy_bytes,B_peak_extra_bytes_during_sort,C_table_bytes,hash_table_size_m,alpha
1000,100056,0,8056,16112,69712,1361,0.7348
10000,1000056,0,80056,160112,683720,13337,0.7498
100000,10000056,0,800056,1600112,6871256,133337,0.75
1000000,100000056,0,8000056,16000112,69791136,1333357,0.75
```

#### Task_9_Experimental_Performance/break_even.csv

```
n,A_to_B_by_operations,A_to_B_by_time,A_to_C_by_operations,A_to_C_by_time
1000,11.838,63.229,1.801,15.242
10000,16.129,135.633,1.854,12.714
100000,20.321,80.746,1.816,19.514
1000000,25.227,158.527,1.792,20.118
```

#### Task_9_Experimental_Performance/builtin_reference.csv

```
n,merge_sort_ms,builtin_sorted_ms,hash_build_ms,builtin_dict_ms,binary_us_hit,bisect_us_hit,hash_us_hit,dict_get_us_hit
1000,1.383,0.143,0.354,0.067,1.5234,0.2032,0.264,0.0964
10000,35.345,1.517,3.34,0.524,2.3822,0.329,0.5,0.1782
100000,262.168,27.17,63.431,12.443,4.1198,0.7514,0.6556,0.2578
1000000,5846.824,417.102,742.121,206.642,6.2358,1.3414,0.8812,0.3184
```

#### Task_9_Experimental_Performance/amortised_cost.csv

```
n,searches_q,A_total_s,B_total_s,C_total_s
1000,1,2.3e-05,0.001384,0.000354
1000,10,0.000235,0.001399,0.000357
1000,100,0.002348,0.001544,0.00038
1000,1000,0.023482,0.002998,0.00061
1000,10000,0.234824,0.017541,0.002918
1000,50000,1.17412,0.082173,0.013174
1000,100000,2.34824,0.162963,0.025994
1000,1000000,23.4824,1.617183,0.256754
1000000,1,0.036889,5.84683,0.742121
1000000,10,0.368889,5.84689,0.742128
1000000,100,3.688891,5.847488,0.742196
1000000,1000,36.888907,5.853473,0.74287
1000000,10000,368.889065,5.913319,0.749616
1000000,50000,1844.445325,6.179303,0.779596
1000000,100000,3688.89065,6.511783,0.817071
1000000,1000000,36888.9065,12.496423,1.491621
```

#### Task_9_Experimental_Performance/chain_length_distribution.csv

```
chain_length,observed_buckets,finite_key_space_model,poisson_expected
0,605954,605861.98,629841.63
1,502931,503104.52,472372.84
2,181977,181869.75,177136.67
3,37294,37352.83,44283.38
4,4788,4762.52,8302.99
5,397,385.52,1245.43
6,16,19.32,155.68
7,0,0.55,16.68
```

#### Task_12_Design_Challenge/design_challenge_hourly.csv

```
hour,B_comparisons,B_seconds,C_comparisons,C_seconds,C3_comparisons,C3_seconds,successful_searches,all_correct
1,957582,0.3807,59522,0.0514,48293,0.0464,40000,True
2,957592,0.3801,59309,0.0552,48454,0.0533,40000,True
3,957269,0.4119,59587,0.0523,48363,0.05,40000,True
4,957352,0.5183,59639,0.052,48431,0.0568,40000,True
5,957264,0.5263,59823,0.0534,48458,0.0419,40000,True
6,957634,0.4723,59518,0.0474,48370,0.051,40000,True
7,957797,0.4552,59676,0.0589,48193,0.0432,40000,True
8,957533,0.4386,59717,0.0605,48377,0.0511,40000,True
9,957778,0.4341,59480,0.0504,48532,0.0469,40000,True
10,957445,0.4875,59557,0.0654,48607,0.0741,40000,True
11,957791,0.5277,59479,0.0672,48560,0.0563,40000,True
12,957943,0.5133,59622,0.0537,48331,0.0567,40000,True
13,958002,0.58,59762,0.0544,48409,0.0565,40000,True
14,957455,0.4185,59474,0.0614,48228,0.0444,40000,True
15,957505,0.3845,59896,0.064,48508,0.0413,40000,True
16,957473,0.3865,59600,0.0542,48422,0.0563,40000,True
17,957357,0.412,59635,0.0749,48518,0.0469,40000,True
18,957128,0.4979,59717,0.0549,48394,0.053,40000,True
19,956905,0.4268,59562,0.058,48353,0.0409,40000,True
20,957594,0.3566,59559,0.0465,48441,0.0473,40000,True
21,957052,0.3787,59636,0.0582,48377,0.0473,40000,True
22,957208,0.4284,59611,0.0469,48440,0.0496,40000,True
23,957312,0.3472,59742,0.0512,48327,0.049,40000,True
24,957641,0.3374,59528,0.0509,48317,0.0494,40000,True
```

#### Task_12_Design_Challenge/design_challenge_updates.csv

```
strategy,description,comparisons,other_ops,seconds,rehashes,verified
A,append batch to the unsorted list,0,5000,0.00218,0,True
B1,re-sort all n + b records (merge sort),18774634,39502821,4.17819,0,True
B2,"sort batch, merge into sorted array",1060084,1125810,0.34755,0,True
C1,rebuild the whole hash table,327916,1005000,0.71426,0,True
C2,"insert batch, Task-11 table sized for n",1397,1005018,0.79205,1,True
C3,"insert batch, table with reserved capacity",1454,5000,0.00357,0,True
```

#### Task_12_Design_Challenge/design_challenge_daily_cost.csv

```
design,description,operations_per_day,update_seconds,search_seconds_per_day,total_cpu_seconds_per_day,search_cpu_utilisation_percent,load_headroom_factor,us_per_search
A,append batch to the unsorted list,714936719000,0.00218,30335.4006,30335.4028,35.110417,2.8,25279.5005
B1,re-sort all n + b records (merge sort),104476679,4.17819,10.5008,14.6789,0.012154,8228.0,8.7506
B2,"sort batch, merge into sorted array",48385118,0.34755,10.5008,10.8483,0.012154,8228.0,8.7506
C1,rebuild the whole hash table,3963567,0.71426,1.3435,2.0577,0.001555,64310.1,1.1196
C2,"insert batch, Task-11 table sized for n",3637066,0.79205,1.3435,2.1355,0.001555,64310.1,1.1196
C3,"insert batch, table with reserved capacity",2368157,0.00357,1.2094,1.213,0.0014,71440.8,1.0078
```

#### Task_12_Design_Challenge/design_challenge_sensitivity.csv

```
searches_per_hour,A_cpu_s_per_day,B1_cpu_s_per_day,B2_cpu_s_per_day,C1_cpu_s_per_day,C2_cpu_s_per_day,C3_cpu_s_per_day
1.0,0.608889,4.178396,0.347757,0.714283,0.792074,0.003594
1.78,1.081077,4.17856,0.34792,0.714304,0.792095,0.003613
3.16,1.92076,4.17885,0.348211,0.714341,0.792133,0.003646
5.62,3.41395,4.179367,0.348728,0.714407,0.792199,0.003706
10.0,6.069261,4.180286,0.349647,0.714525,0.792316,0.003812
17.78,10.791144,4.181921,0.351281,0.714734,0.792525,0.004
31.62,19.187972,4.184828,0.354188,0.715106,0.792897,0.004335
56.23,34.119879,4.189996,0.359357,0.715767,0.793559,0.00493
100.0,60.672982,4.199188,0.368548,0.716943,0.794735,0.005988
177.83,107.891817,4.215533,0.384893,0.719035,0.796826,0.007871
316.23,191.8601,4.244599,0.413959,0.722753,0.800545,0.011219
562.34,341.179168,4.296287,0.465647,0.729366,0.807158,0.017172
1000.0,606.710193,4.388201,0.557562,0.741126,0.818917,0.027758
1778.28,1078.898546,4.551652,0.721012,0.762038,0.83983,0.046582
3162.28,1918.581373,4.842313,1.011673,0.799226,0.877017,0.080058
5623.41,3411.772055,5.359188,1.528549,0.865356,0.943148,0.139588
10000.0,6067.082301,6.278338,2.447698,0.982954,1.060746,0.245448
17782.79,10788.965837,7.912843,4.082203,1.192077,1.269868,0.433698
31622.78,19185.794106,10.81945,6.98881,1.563955,1.641746,0.768457
56234.13,34117.700928,15.988208,12.157568,2.225257,2.303049,1.363754
100000.0,60670.803381,25.179705,21.349065,3.401238,3.479029,2.422357
177827.94,107889.638745,41.524754,37.694114,5.492461,5.570252,4.30485
316227.77,191857.92144,70.590819,66.760179,9.211239,9.28903,7.652447
562341.33,341176.989652,122.278403,118.447763,15.824265,15.902057,13.605411
1000000.0,606708.014181,214.19337,210.36273,27.584074,27.661866,24.191444
1778279.41,1078896.367826,377.643864,373.813224,48.4963,48.574092,43.016368
3162277.66,1918579.194773,668.304511,664.473871,85.684081,85.761873,76.492343
5623413.25,3411769.876897,1185.180355,1181.349715,151.814347,151.892138,136.021981
10000000.0,6067080.122181,2104.330026,2100.499386,269.412436,269.490228,241.88231
```

### Appendix D – Test Results

Captured output of `py -3 test_search_algorithms.py` (Task_8_Implementation_Testing/test_output.txt):

```
================================================================================================================
 CO1 Assignment - test cases for sequential search (A), recursive binary search (B) and hashing (C)
================================================================================================================
PART 1 - functional test cases (actual = result(comparisons) for A: sequential, B: binary, C: hash)
      ID    test case                                 key  expected   A          B          C         
PASS  TC01  empty dataset (n = 0)               192425324  not found  none(0)    none(0)    none(0)   
PASS  TC02  single record, key present          192425324  found      found(1)   found(1)   found(1)  
PASS  TC03  single record, absent smaller key   192425323  not found  none(1)    none(1)    none(0)   
PASS  TC04  single record, absent larger key    192425325  not found  none(1)    none(1)    none(0)   
PASS  TC05  first record in stored order        196394267  found      found(1)   found(4)   found(1)  
PASS  TC06  last record in stored order         191711386  found      found(15)  found(4)   found(1)  
PASS  TC07  middle record of sorted order       196356844  found      found(13)  found(1)   found(1)  
PASS  TC08  smallest registration number        190265359  found      found(4)   found(4)   found(1)  
PASS  TC09  largest registration number         199572130  found      found(7)   found(4)   found(1)  
PASS  TC10  random present key (seed 1)         194219218  found      found(3)   found(3)   found(1)  
PASS  TC11  absent, below minimum (189999999)   189999999  not found  none(15)   none(4)    none(0)   
PASS  TC12  absent, above maximum (200000000)   200000000  not found  none(15)   none(4)    none(2)   
PASS  TC13  absent, in a gap (A[6] + 1)         195362281  not found  none(15)   none(4)    none(0)   
PASS  count TC05 sequential best case (key at position 0)      expected  = 1  actual   1
PASS  count TC06 sequential worst successful (last position)   expected = 15  actual  15
PASS  count TC07 binary best case (key at the middle)          expected  = 1  actual   1
PASS  count TC11 sequential unsuccessful (all n compared)      expected = 15  actual  15
PASS  count TC11 binary unsuccessful, floor(lg 15)+1 = 4       expected <= 4  actual   4

PART 2 - property tests
PASS  P1  duplicate key re-inserted into hash table: expected count 1000, replaced  actual count 1000, new=False
PASS  P2  merge sort n =     15 equals sorted(), input untouched: expected True  actual True
PASS  P2  merge sort n =  1,000 equals sorted(), input untouched: expected True  actual True
PASS  P2  merge sort n = 10,000 equals sorted(), input untouched: expected True  actual True
PASS  P3  binary search n = 1..200, all keys + gaps: max comparisons = floor(lg n)+1: expected True  actual True
PASS  P3b binary search n = 1..200: total successful comparisons = S(n) recurrence: expected True  actual True
PASS  P4  merge sort n = 1..200: comparisons <= n*ceil(lg n) - 2^ceil(lg n) + 1: expected True  actual True
PASS  P5  hash worst case, 1,000 keys = 190000000 + i*m: expected chain 1000, 1000 cmp  actual 1000, 1000/1000
PASS  P6  dynamic growth 10 -> 2,000 records: expected alpha <= 0.75, all found  actual 7 resizes, max alpha 0.749

PART 3 - bulk validation: same dataset + same query batch for every approach, checked against a dict
               n  approach          queries      correct  avg cmp hit  avg cmp miss  invariant
PASS       1,000  Sequential (A)      1,000  1,000/1,000       496.25       1000.00  hit = pos+1, miss = n
PASS       1,000  Binary (B)          1,000  1,000/1,000         8.98          9.98  every search <= 10 cmp
PASS       1,000  Hash (C)            1,000  1,000/1,000         1.34          0.76  alpha = 0.735 <= 0.75
PASS      10,000  Sequential (A)      1,000  1,000/1,000      4966.63      10000.00  hit = pos+1, miss = n
PASS      10,000  Binary (B)          1,000  1,000/1,000        12.31         13.34  every search <= 14 cmp
PASS      10,000  Hash (C)            1,000  1,000/1,000         1.39          0.70  alpha = 0.750 <= 0.75
PASS     100,000  Sequential (A)      1,000  1,000/1,000     51226.36     100000.00  hit = pos+1, miss = n
PASS     100,000  Binary (B)          1,000  1,000/1,000        15.64         16.75  every search <= 17 cmp
PASS     100,000  Hash (C)            1,000  1,000/1,000         1.33          0.67  alpha = 0.750 <= 0.75
PASS   1,000,000  Sequential (A)        200      200/200    480558.07    1000000.00  hit = pos+1, miss = n
PASS   1,000,000  Binary (B)          1,000  1,000/1,000        18.87         19.95  every search <= 20 cmp
PASS   1,000,000  Hash (C)            1,000  1,000/1,000         1.32          0.68  alpha = 0.750 <= 0.75
----------------------------------------------------------------------------------------------------------------
run time 14.9 s
RESULT: 39/39 tests passed
```

### References

1. A. Levitin, *Introduction to the Design and Analysis of Algorithms*, 3rd ed., Pearson, 2012 – sequential search, binary search, merge sort, hashing, basic operation, smoothness rule and the Master Theorem.
2. T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., MIT Press, 2022 – recurrences, the Master Theorem, the substitution method and hash tables with chaining (expected search cost 1 + α/2 and α).
3. D. E. Knuth, *The Art of Computer Programming, Vol. 3: Sorting and Searching*, 2nd ed., Addison-Wesley, 1998 – average number of comparisons of merge sort and the analysis of binary search and hashing.
4. Python Software Foundation, *Python 3.13 Documentation* – `time.perf_counter`, `gc`, `sys.getsizeof`, `bisect` and the `dict` type.
