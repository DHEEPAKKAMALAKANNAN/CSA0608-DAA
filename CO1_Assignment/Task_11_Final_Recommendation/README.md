# Task 11 – Recommend and Defend the Final Design [4 Marks]

> Part of **CSA06 Assignment 1 (CO1)** – V. Vasudevan (192425324). Full report: [`Report/Documentation/CO1_Assignment_Report.md`](../Report/Documentation/CO1_Assignment_Report.md) · [project README](../README.md)

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

## 1. Recommendation

I recommend **Approach C: a hash table with separate chaining, keyed by registration number** (h(k) = k mod m with m prime, m ≥ n/0.75 so that α ≤ 0.75, growing to the next prime ≥ 2m when needed), built once from the records and then used for every lookup. If the university later needs ordered reports or range queries (for example "all students with numbers 1924xxxxx"), a sorted array with binary search (Approach B) should be kept *next to it* as a secondary index, not instead of it.

## 2. Why it is better than the alternatives

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

## 3. Theoretical efficiency

Search: Θ(1) expected (1 + α/2 ≤ 1.375 comparisons for a hit, α ≤ 0.75 for a miss, plus one hash computation), independent of n. Preprocessing: Θ(n) expected (n hash computations + n(n − 1)/2m ≤ 0.375n comparisons). Cost of q searches: Θ(n + q), compared with Θ(n log n + q log n) for B and Θ(q·n) for A (Task 3). Space Θ(n + m) = Θ(n). The only weaker point is the theoretical worst case Θ(n) when all keys collide.

## 4. Experimentally observed performance

The measured counts confirmed the theory at every size (1.32–1.39 comparisons per hit, 0.67–0.76 per miss, exactly one hash computation per search; Tables 16 and 21). The time per search was 0.26–0.88 µs at all four sizes, the lowest of the three approaches at every size, including the smallest (at n = 1,000: 0.26 µs against 1.52 µs for B and 15.05 µs for A). Every one of the 4,000 test queries returned the correct record or `None` (Table 14).

## 5. Preprocessing cost

Building the table for 1,000,000 records took 1,326,797 basic operations and 0.74 s, compared with 18,674,803 comparisons and 5.85 s for merge sort. Because the build is linear, it also stays proportionate for small databases (0.4 ms at n = 1,000). In basic operations the build is recovered after **two** searches and in time after about **20** (Table 24), so the preprocessing is cheap relative to any realistic number of lookups.

## 6. Trade-offs and limitations

- **Memory:** about 70 bytes per record (69.8 MB at 10⁶), about 9 times the sorted array of B. This is the price of the space–time trade-off; it is still smaller than the records themselves (100 MB).
- **No order:** the table cannot list students in registration-number order or answer range queries without sorting first.
- **Worst case:** a key set concentrated in one residue class modulo m would make a search Θ(n) (test P5). Prime m and the university's own numbering make this unlikely (the longest chain was 5–8), and a randomly chosen (universal) hash function would remove the dependence on the key set.
- **Growth pauses:** when α would exceed 0.75 the table rehashes all records (Θ(n), about 0.8 s at 10⁶); the cost is amortised O(1) per insertion but happens at one moment (Task 12 addresses this).
- **Implementation constants:** in Python a hash search costs ≈ 0.9 µs, about 2.8 times slower than CPython's built-in `dict`; a production system would use the built-in hash map, which is the same algorithm.

## 7. Does it remain practical as the database grows?

Yes. Because m grows with n, the expected cost of a search stays constant: the measured comparisons did not change between 1,000 and 1,000,000 records, and the time grew only from 0.26 to 0.88 µs (memory caching, Task 10). The build and the memory grow linearly, so a database ten times larger (10 million records) would need about 7 s to build and about 0.7 GB for the table, while each search would still examine about one record. Sequential search would need ten times more comparisons per search and binary search about 3.3 more. Hashing is therefore the design that remains practical from 1,000 to 1,000,000+ records, with B as the complementary structure if ordered access is ever required.
