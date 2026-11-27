# Task 11 â€“ Recommend and Defend the Final Design [4 Marks]

> Part of **CSA06 Assignment 1 (CO1)** â€“ K DHEEPAK (192411108). Full report: [`Report/Documentation/CO1_Assignment_Report.md`](../Report/Documentation/CO1_Assignment_Report.md) Â· [project README](../README.md)

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

I recommend **Approach C: a hash table with separate chaining, keyed by registration number** (h(k) = k mod m with m prime, m â‰¥ n/0.75 so that Î± â‰¤ 0.75, growing to the next prime â‰¥ 2m when needed), built once from the records and then used for every lookup. If the university later needs ordered reports or range queries (for example "all students with numbers 1924xxxxx"), a sorted array with binary search (Approach B) should be kept *next to it* as a secondary index, not instead of it.

## 2. Why it is better than the alternatives

Table 25: Decision matrix at n = 1,000,000 (measurements from Tables 15â€“19 and 24)

| Criterion | A â€“ Sequential | B â€“ Merge sort + binary search | C â€“ Hash table |
|---|---|---|---|
| Comparisons per hit / miss | 480,558 / 1,000,000 | 18.87 / 19.95 | 1.32 / 0.68 |
| Time per hit | 22,537 Âµs | 6.24 Âµs | 0.88 Âµs |
| Guaranteed worst case | n = 1,000,000 | âŒŠlogâ‚‚ nâŒ‹ + 1 = 20 | n in theory; 6 observed |
| One-time preprocessing | none | 18.7 M comparisons, 5.85 s | 1.33 M operations, 0.74 s |
| Break-even searches (time) | â€“ | 159 | 20 |
| Extra memory | 0 | 8 MB (16 MB while sorting) | 70 MB |
| Adding one new record | Î˜(1) append | Î˜(n) shift or batch merge | Î˜(1) expected |
| Ordered / range queries | full scan | yes | no |
| Growth from 10Â³ to 10â¶ records | Ã—1,000 comparisons | +10 comparisons | unchanged |

- **Against A:** A avoids preprocessing, but it is the slowest by four orders of magnitude at a million records, and its cost rises with every admitted batch. The table pays for its build after about 20 searches; a university system serves far more than 20 searches.
- **Against B:** C is better on *both* parts of the cost: its preprocessing is about 14 times fewer operations (Î˜(n) vs Î˜(n log n)) and 7.9 times less time, and every search is 14 times fewer comparisons and 7.1 times faster. B has a better *guaranteed* worst case and uses less memory, but these advantages do not show up in this workload (the observed hash worst case was 8 comparisons).

## 3. Theoretical efficiency

Search: Î˜(1) expected (1 + Î±/2 â‰¤ 1.375 comparisons for a hit, Î± â‰¤ 0.75 for a miss, plus one hash computation), independent of n. Preprocessing: Î˜(n) expected (n hash computations + n(n âˆ’ 1)/2m â‰¤ 0.375n comparisons). Cost of q searches: Î˜(n + q), compared with Î˜(n log n + q log n) for B and Î˜(qÂ·n) for A (Task 3). Space Î˜(n + m) = Î˜(n). The only weaker point is the theoretical worst case Î˜(n) when all keys collide.

## 4. Experimentally observed performance

The measured counts confirmed the theory at every size (1.32â€“1.39 comparisons per hit, 0.67â€“0.76 per miss, exactly one hash computation per search; Tables 16 and 21). The time per search was 0.26â€“0.88 Âµs at all four sizes, the lowest of the three approaches at every size, including the smallest (at n = 1,000: 0.26 Âµs against 1.52 Âµs for B and 15.05 Âµs for A). Every one of the 4,000 test queries returned the correct record or `None` (Table 14).

## 5. Preprocessing cost

Building the table for 1,000,000 records took 1,326,797 basic operations and 0.74 s, compared with 18,674,803 comparisons and 5.85 s for merge sort. Because the build is linear, it also stays proportionate for small databases (0.4 ms at n = 1,000). In basic operations the build is recovered after **two** searches and in time after about **20** (Table 24), so the preprocessing is cheap relative to any realistic number of lookups.

## 6. Trade-offs and limitations

- **Memory:** about 70 bytes per record (69.8 MB at 10â¶), about 9 times the sorted array of B. This is the price of the spaceâ€“time trade-off; it is still smaller than the records themselves (100 MB).
- **No order:** the table cannot list students in registration-number order or answer range queries without sorting first.
- **Worst case:** a key set concentrated in one residue class modulo m would make a search Î˜(n) (test P5). Prime m and the university's own numbering make this unlikely (the longest chain was 5â€“8), and a randomly chosen (universal) hash function would remove the dependence on the key set.
- **Growth pauses:** when Î± would exceed 0.75 the table rehashes all records (Î˜(n), about 0.8 s at 10â¶); the cost is amortised O(1) per insertion but happens at one moment (Task 12 addresses this).
- **Implementation constants:** in Python a hash search costs â‰ˆ 0.9 Âµs, about 2.8 times slower than CPython's built-in `dict`; a production system would use the built-in hash map, which is the same algorithm.

## 7. Does it remain practical as the database grows?

Yes. Because m grows with n, the expected cost of a search stays constant: the measured comparisons did not change between 1,000 and 1,000,000 records, and the time grew only from 0.26 to 0.88 Âµs (memory caching, Task 10). The build and the memory grow linearly, so a database ten times larger (10 million records) would need about 7 s to build and about 0.7 GB for the table, while each search would still examine about one record. Sequential search would need ten times more comparisons per search and binary search about 3.3 more. Hashing is therefore the design that remains practical from 1,000 to 1,000,000+ records, with B as the complementary structure if ordered access is ever required.

