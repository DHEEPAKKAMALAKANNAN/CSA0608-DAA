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
