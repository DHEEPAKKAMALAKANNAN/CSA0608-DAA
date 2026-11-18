"""Q2 - Sequential Search for aircraft-maintenance tool tracking.

Problem
    A maintenance facility keeps a temporary list of specialised tools currently issued to technicians.
    Each record is (Tool ID, Technician ID, Issue Time, Work Bay).  Records are appended when a tool is issued
    and removed when it is returned, so the list is in issue order (unsorted by Tool ID).  The question
    "Who currently has Tool T-184?" is answered with Sequential Search.

This module provides
    * make_tool_records(n)       - a reproducible list of n issued-tool records (seeded RNG)
    * sequential_search(L, id)   - the instrumented algorithm: returns (index or -1, key comparisons)
    * ListToolStore / IndexedToolStore - the two record stores compared in the 20-facility re-evaluation
Run this file for the correctness tests and the "Who has T-184?" demonstration.
"""

import random

TECHNICIANS = [f"TECH-{i:03d}" for i in range(1, 401)]           # shared string pools keep 1M records small
TIMES = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(60)]
BAYS = [f"BAY-{b:02d}" for b in range(1, 41)]


def make_tool_records(n, seed=42, must_include=("T-184",)):
    """Return n records (tool_id, technician_id, issue_time, work_bay) in random issue order.

    Tool IDs are unique ("T-<number>"); `must_include` IDs are guaranteed to be present."""
    rng = random.Random(seed + n)
    numbers = rng.sample(range(1, 10 * n + 10), n)
    ids = [f"T-{k}" for k in numbers]
    present = set(ids)
    for tool in must_include:
        if n and tool not in present:
            ids[rng.randrange(n)] = tool                         # plant the queried tool at a random position
    times = sorted(rng.choice(TIMES) for _ in range(n))           # list is in issue order -> times ascend
    return [(tid, rng.choice(TECHNICIANS), tm, rng.choice(BAYS)) for tid, tm in zip(ids, times)]


def sequential_search(records, target_tool_id):
    """Scan records from the first to the last; stop at the first record whose Tool ID equals the target.

    Returns (index, comparisons); index = -1 when the tool is not currently issued (unsuccessful search).
    One comparison = one test `record.tool_id == target_tool_id`."""
    comparisons = 0
    for index, record in enumerate(records):
        comparisons += 1
        if record[0] == target_tool_id:
            return index, comparisons
    return -1, comparisons


class ListToolStore:
    """Original design: an unsorted list, searched sequentially for lookups and returns."""

    def __init__(self, records):
        self.records = list(records)
        self.comparisons = 0

    def issue(self, record):
        self.records.append(record)                      # O(1), no search needed

    def lookup(self, tool_id):
        idx, c = sequential_search(self.records, tool_id)
        self.comparisons += c
        return self.records[idx] if idx >= 0 else None

    def return_tool(self, tool_id):
        idx, c = sequential_search(self.records, tool_id)  # O(n) search to find the record ...
        self.comparisons += c
        if idx >= 0:                                       # ... then O(1) swap-with-last removal
            self.records[idx] = self.records[-1]
            self.records.pop()


class IndexedToolStore:
    """Redesigned store for many facilities: hash map Tool ID -> record, updated on every issue/return."""

    def __init__(self, records):
        self.index = {r[0]: r for r in records}
        self.probes = 0                                   # one hash-table access per operation

    def issue(self, record):
        self.index[record[0]] = record
        self.probes += 1

    def lookup(self, tool_id):
        self.probes += 1
        return self.index.get(tool_id)

    def return_tool(self, tool_id):
        self.probes += 1
        self.index.pop(tool_id, None)


# ------------------------------------------------------------------------------------------------- tests
def run_tests():
    """Expected index comes from an independent dictionary built over the list (first occurrence)."""
    recs = make_tool_records(1000)
    reference = {}
    for i, r in enumerate(recs):
        reference.setdefault(r[0], i)
    first, middle, last = recs[0][0], recs[499][0], recs[-1][0]
    cases = [
        ("empty list", [], "T-184", -1, 0),
        ("single, present", recs[:1], first, 0, 1),
        ("single, absent", recs[:1], "T-0", -1, 1),
        ("first record", recs, first, reference[first], 1),
        ("middle record (500th)", recs, middle, reference[middle], 500),
        ("last record", recs, last, reference[last], 1000),
        ("T-184 (planted)", recs, "T-184", reference["T-184"], reference["T-184"] + 1),
        ("absent tool", recs, "T-0", -1, 1000),
        ("duplicate ID -> first", [("T-5", "A", "", ""), ("T-5", "B", "", "")], "T-5", 0, 1),
    ]
    print("CORRECTNESS TESTS  (expected/actual; expected index from an independent dict, comparisons = position)")
    passed = 0
    for name, lst, target, exp_i, exp_c in cases:
        i, c = sequential_search(lst, target)
        ok = (i, c) == (exp_i, exp_c)
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  Q2 {name:<23} n={len(lst):<5} {target:<7} index {exp_i:>4}/{i:>4}"
              f"   comparisons {exp_c:>5}/{c:>5}")
    # the two stores used in the 20-facility study must give identical answers on the same event sequence
    rng = random.Random(5)
    lst_store, idx_store = ListToolStore(recs), IndexedToolStore(recs)
    agree = True
    for step in range(3000):
        tool = rng.choice(recs)[0] if rng.random() < 0.8 else f"T-{rng.randint(1, 20000)}"
        op = step % 3
        if op == 0:
            agree &= lst_store.lookup(tool) == idx_store.lookup(tool)
        elif op == 1:
            lst_store.return_tool(tool)
            idx_store.return_tool(tool)
        else:
            rec = (tool, "TECH-001", "08:00", "BAY-01")
            if idx_store.lookup(tool) is None:
                lst_store.issue(rec)
                idx_store.issue(rec)
    agree &= sorted(lst_store.records) == sorted(idx_store.index.values())
    passed += agree
    print(f"{'PASS' if agree else 'FAIL'}  Q2 list store == hash-index store on 3,000 mixed issue/return/lookup events")
    total = len(cases) + 1
    print(f"RESULT: {passed}/{total} tests passed")
    return passed == total


def demo():
    """Answer the technician's question on a small hangar list."""
    recs = make_tool_records(12, seed=2026)
    print("\nDEMO - currently issued tools in Hangar 1 (issue order):")
    print(f"   {'#':>3}  {'Tool ID':<9}{'Technician':<11}{'Issued':<8}Work bay")
    for i, (t, tech, tm, bay) in enumerate(recs, start=1):
        print(f"   {i:>3}  {t:<9}{tech:<11}{tm:<8}{bay}")
    for query in ("T-184", "T-999"):
        idx, comp = sequential_search(recs, query)
        if idx >= 0:
            t, tech, tm, bay = recs[idx]
            print(f"Q: Who currently has Tool {query}?  A: {tech}, issued {tm}, at {bay}"
                  f"  [record {idx + 1} of {len(recs)}, {comp} comparisons]")
        else:
            print(f"Q: Who currently has Tool {query}?  A: nobody - tool is not issued"
                  f"  [unsuccessful: all {comp} records compared]")


def main():
    ok = run_tests()
    demo()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
