# Task 8 â€“ Implement and Test the Algorithms [4 Marks]

> Part of **CSA06 Assignment 1 (CO1)** â€“ K DHEEPAK (192411108). Full report: [`Report/Documentation/CO1_Assignment_Report.md`](../Report/Documentation/CO1_Assignment_Report.md) Â· [project README](../README.md)

> Implement all approaches and test their behaviour using datasets of approximately 1,000 â†’ 10,000 â†’ 100,000 â†’ 1,000,000 records. Ensure that:
> - all algorithms produce the correct result;
> - the same or equivalent datasets are used for comparison;
> - testing conditions are kept reasonably consistent;
> - appropriate test cases are included;
> - the implementation corresponds to the algorithms analysed.

**Evidence Expected**

> Working implementations together with a clearly described and reproducible testing procedure.

**Ans:**

## 1. Implementation overview

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

## 2. The implementation corresponds to the analysed algorithms

Table 12: Pseudocode line â†’ code (search_algorithms.py)

| Pseudocode (Task 1) | Code | Counted as |
|---|---|---|
| `SequentialSearch` line 2: `A[i].reg_no = key` | `sequential_search`: `comparisons += 1; if record.reg_no == key` | `comparisons` |
| `MergeSort` lines 1â€“5 (two recursive calls) | `_merge_sort(a, aux, low, high, counter)` | â€“ |
| `Merge` line 4: `B[i].reg_no <= B[j].reg_no` | `_merge`: `comparisons += 1; if aux[i].reg_no <= aux[j].reg_no` | `comparisons`, `moves` |
| `BinSearch` line 1: base case `low > high` | `binary_search_recursive`: `if low > high: return None` | `calls` |
| `BinSearch` line 3: three-way comparison | `counter.comparisons += 1`, then `==` / `<` on `mid_key` | `comparisons` |
| `BuildHashTable` lines 1â€“5 | `StudentHashTable.__init__` (prime m â‰¥ n/0.75), `build`, `insert` | `hash_computations`, `comparisons` |
| `HashSearch` lines 1â€“3 | `StudentHashTable.search`: `_hash`, loop over one chain | `hash_computations`, `comparisons` |

The demo in `search_algorithms.py` prints a trace of each approach on 15 records (Figures 20â€“21): sequential search needs 1 comparison for the first stored record and 15 for the last; merge sort sorts the 15 records with 38 comparisons (worst-case bound 45); the recursive binary search trace shows the four calls (low, high, mid) for a present key and the final empty-range call for an absent one; the hash table with m = 23 shows its chains.

## 3. Datasets and the reproducible testing procedure

1. **Data.** `generate_records(n)` draws unique registration numbers uniformly from 190,000,000â€“199,999,999 (seed 42), re-drawing a number that was already issued, and attaches a name, department and CGPA. Because each record depends only on the random stream before it, the datasets are **nested**: the 1,000-record set is the first 1,000 records of the 10,000-record set, and so on. All three approaches always receive *the same list* for a given n.
2. **Queries.** For each n, `make_query_batch` draws one batch of 500 stored keys (uniform positions) and 500 absent keys (uniform numbers in 19xxxxxxx that are not stored), with seed n. All three approaches search the same batch; sequential search at n = 1,000,000 uses the first 100 + 100 keys of it, because one search takes 25â€“55 ms in Python.
3. **Correctness reference.** Every result is compared with a Python `dict` built from the same records (used only for checking). A successful search must return the *identical* record object; an unsuccessful one must return `None`.
4. **Consistent conditions.** One process, one machine (Table 1), the same Python version; the garbage collector is switched off while timing; each timing is the minimum of several runs; operation counts are taken in a separate counting pass and do not depend on timing.

## 4. Test cases

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

TC05â€“TC13 use the first 15 records of the seed-42 dataset. Five further checks assert the *operation counts* of the cases: sequential best case = 1 (TC05), sequential worst successful = n = 15 (TC06), binary best case = 1 (TC07), sequential unsuccessful = n (TC11) and binary unsuccessful â‰¤ âŒŠlogâ‚‚ 15âŒ‹ + 1 = 4 (TC11). Duplicate registration numbers are impossible by construction (the generator re-draws them) and the hash table refuses to store a key twice.

**Property tests:** P1 re-inserting an existing key replaces the record and keeps the count at 1,000 (no duplicates); P2 merge sort equals Python's `sorted()` for n = 15, 1,000 and 10,000 and leaves the input list untouched; P3 for every n from 1 to 200, searching every key and every gap never exceeds âŒŠlogâ‚‚ nâŒ‹ + 1 comparisons and the maximum is reached; P3b the total successful comparisons equal the recurrence S(n); P4 merge sort never exceeds nâŒˆlogâ‚‚ nâŒ‰ âˆ’ 2<sup>âŒˆlogâ‚‚ nâŒ‰</sup> + 1; P5 the adversarial hash case (1,000 keys congruent modulo m) produces one chain of 1,000 and 1,000 comparisons; P6 a table created for 10 records grows through 7 rehashes to 2,000 records and Î± never exceeds 0.75 (max 0.749).

Table 14: Bulk validation on the four required sizes (same queries for every approach)

| Number of records (n) | A: correct answers | B: correct answers | C: correct answers | A invariant | B: every search â‰¤ | C: load factor Î± |
|---|---|---|---|---|---|---|
| 1,000 | 1,000/1,000 | 1,000/1,000 | 1,000/1,000 | hit = pos+1, miss = n | 10 | 0.735 |
| 10,000 | 1,000/1,000 | 1,000/1,000 | 1,000/1,000 | hit = pos+1, miss = n | 14 | 0.750 |
| 100,000 | 1,000/1,000 | 1,000/1,000 | 1,000/1,000 | hit = pos+1, miss = n | 17 | 0.750 |
| 1,000,000 | 200/200 | 1,000/1,000 | 1,000/1,000 | hit = pos+1, miss = n | 20 | 0.750 |

Result: **39/39 tests passed** (Figure 22). Every approach returned the correct record for every present key and `None` for every absent key at every size.

## 5. Source code

The core algorithms, the data generator and the test program are shown below; the experiment and simulation programs are listed in full in Appendix A, and screenshots of all eight programs are in `Report/Source_Code_Screenshots/`.

![Figure 6: Source code â€“ search_algorithms.py (part 1 of 6)](../Report/Source_Code_Screenshots/search_algorithms_code_1.png)

![Figure 7: Source code â€“ search_algorithms.py (part 2 of 6)](../Report/Source_Code_Screenshots/search_algorithms_code_2.png)

![Figure 8: Source code â€“ search_algorithms.py (part 3 of 6)](../Report/Source_Code_Screenshots/search_algorithms_code_3.png)

![Figure 9: Source code â€“ search_algorithms.py (part 4 of 6)](../Report/Source_Code_Screenshots/search_algorithms_code_4.png)

![Figure 10: Source code â€“ search_algorithms.py (part 5 of 6)](../Report/Source_Code_Screenshots/search_algorithms_code_5.png)

![Figure 11: Source code â€“ search_algorithms.py (part 6 of 6)](../Report/Source_Code_Screenshots/search_algorithms_code_6.png)

![Figure 12: Source code â€“ student_records.py (part 1 of 3)](../Report/Source_Code_Screenshots/student_records_code_1.png)

![Figure 13: Source code â€“ student_records.py (part 2 of 3)](../Report/Source_Code_Screenshots/student_records_code_2.png)

![Figure 14: Source code â€“ student_records.py (part 3 of 3)](../Report/Source_Code_Screenshots/student_records_code_3.png)

![Figure 15: Source code â€“ test_search_algorithms.py (part 1 of 4)](../Report/Source_Code_Screenshots/test_search_algorithms_code_1.png)

![Figure 16: Source code â€“ test_search_algorithms.py (part 2 of 4)](../Report/Source_Code_Screenshots/test_search_algorithms_code_2.png)

![Figure 17: Source code â€“ test_search_algorithms.py (part 3 of 4)](../Report/Source_Code_Screenshots/test_search_algorithms_code_3.png)

![Figure 18: Source code â€“ test_search_algorithms.py (part 4 of 4)](../Report/Source_Code_Screenshots/test_search_algorithms_code_4.png)

## 6. Execution output

![Figure 19: Execution output of student_records.py â€“ sample records, uniqueness and prefix property](../Report/Output_Screenshots/student_records_output.png)

![Figure 20: Execution output of search_algorithms.py â€“ traces of the three approaches (part 1 of 2)](../Report/Output_Screenshots/search_algorithms_demo_output_1.png)

![Figure 21: Execution output of search_algorithms.py â€“ traces of the three approaches (part 2 of 2)](../Report/Output_Screenshots/search_algorithms_demo_output_2.png)

![Figure 22: Execution output of test_search_algorithms.py â€“ 39/39 tests passed](../Report/Output_Screenshots/test_search_algorithms_output.png)

## Files in this folder

- `Source_Code/` â€“ the five programs (see the table above)
- `test_output.txt`, `search_algorithms_demo_output.txt`, `student_records_output.txt` â€“ captured program output

