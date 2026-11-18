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
