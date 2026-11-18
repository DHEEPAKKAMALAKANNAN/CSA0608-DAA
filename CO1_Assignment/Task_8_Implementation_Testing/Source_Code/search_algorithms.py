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
