"""
Task 1 - Activity selection: booking the single briefing room of the city Emergency Operations Centre (EOC).

Problem: n booking requests R_i = [start_i, finish_i) (half-open: a session ending at 10:00 is compatible
with one starting at 10:00). Accept the MAXIMUM number of mutually compatible requests.

Greedy (earliest finish time, EFT): sort by finish time, scan once, accept every request whose start is
>= the finish of the last accepted request.  Theta(n log n) (sort) + Theta(n) (scan).

The module also contains
  * the "wrong" greedy rules (earliest start, shortest duration, fewest conflicts) and the symmetric
    correct rule (latest start), to demonstrate counter-examples,
  * a naive O(n*k) re-scanning version of EFT (the un-optimised design),
  * two exact references: brute force over all subsets (n <= 20) and an O(n log n) DP,
  * operation counters (collections.Counter) - the primary evidence of cost.
Run:  py -3 activity_selection.py      (demo on the given test cases, prints every greedy step)
"""
import bisect
import csv
import os
from collections import Counter, namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
Request = namedtuple("Request", "rid agency start finish")      # start/finish in minutes after midnight


# ----------------------------------------------------------------------------- input helpers
def to_min(hhmm):
    """'09:30' -> 570 minutes after midnight."""
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def hhmm(minutes):
    """570 -> '09:30'."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def load_requests(path):
    """Read a CSV with columns rid, agency, start, finish (HH:MM) into Request tuples."""
    with open(path, newline="", encoding="utf-8") as f:
        return [Request(r["rid"], r["agency"], to_min(r["start"]), to_min(r["finish"]))
                for r in csv.DictReader(f)]


def make_requests(spec):
    """Build requests from [(rid, 'HH:MM', 'HH:MM'), ...] (agency left blank)."""
    return [Request(rid, "", to_min(s), to_min(f)) for rid, s, f in spec]


def validate(requests):
    """Reject impossible bookings: finish must be strictly after start and ids must be unique."""
    seen = set()
    for r in requests:
        if r.finish <= r.start:
            raise ValueError(f"request {r.rid}: finish {hhmm(r.finish)} is not after start {hhmm(r.start)}")
        if r.rid in seen:
            raise ValueError(f"duplicate request id {r.rid}")
        seen.add(r.rid)


def compatible(a, b):
    """Half-open intervals [s, f) are compatible when one ends no later than the other starts."""
    return a.finish <= b.start or b.finish <= a.start


# ----------------------------------------------------------------------------- sorting (counted)
def merge_sort(seq, key, ops, name="sort_comparisons"):
    """Stable top-down merge sort; every key comparison is counted in ops[name]."""
    def sort(a):
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left, right = sort(a[:mid]), sort(a[mid:])
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            ops[name] += 1
            if right[j][0] < left[i][0]:
                out.append(right[j]); j += 1
            else:
                out.append(left[i]); i += 1
        out.extend(left[i:]); out.extend(right[j:])
        return out
    return [x for _, x in sort([(key(x), x) for x in seq])]


# ----------------------------------------------------------------------------- the greedy algorithm
def select_eft(requests, ops=None, trace=None):
    """Earliest-finish-time greedy. Returns the accepted requests in time order.
    trace (optional list) receives one row per examined request: (request, last_finish, decision)."""
    ops = Counter() if ops is None else ops
    validate(requests)
    ordered = merge_sort(requests, key=lambda r: (r.finish, r.start), ops=ops)
    chosen, last_finish = [], float("-inf")
    for r in ordered:
        ops["compatibility_checks"] += 1
        if r.start >= last_finish:                       # greedy choice: first compatible finisher
            if trace is not None:
                trace.append((r, last_finish, "ACCEPT"))
            chosen.append(r)
            last_finish = r.finish
        elif trace is not None:
            blocker = chosen[-1].rid
            trace.append((r, last_finish, f"REJECT (overlaps {blocker})"))
    return chosen


def select_naive_rescan(requests, ops=None):
    """Un-optimised EFT: in every round scan ALL remaining requests for the compatible one that finishes
    first. Same answer, but Theta(n*k) comparisons (k = number accepted) instead of Theta(n log n)."""
    ops = Counter() if ops is None else ops
    validate(requests)
    remaining, chosen, last_finish = list(requests), [], float("-inf")
    while True:
        best = None
        for r in remaining:
            ops["scan_comparisons"] += 1
            if r.start >= last_finish and (best is None or (r.finish, r.start) < (best.finish, best.start)):
                best = r
        if best is None:
            return chosen
        chosen.append(best)
        last_finish = best.finish
        remaining = [r for r in remaining if r.start >= last_finish]   # discard what can never fit


# ----------------------------------------------------------------------------- other greedy rules
def select_by_key(requests, key, ops=None):
    """Generic greedy: consider requests in increasing `key` order, accept if compatible with all accepted."""
    ops = Counter() if ops is None else ops
    validate(requests)
    chosen = []
    for r in merge_sort(requests, key=key, ops=ops):
        ops["compatibility_checks"] += len(chosen)
        if all(compatible(r, c) for c in chosen):
            chosen.append(r)
    return sorted(chosen, key=lambda r: r.start)


def select_earliest_start(requests, ops=None):
    return select_by_key(requests, lambda r: (r.start, r.finish), ops)


def select_shortest(requests, ops=None):
    return select_by_key(requests, lambda r: (r.finish - r.start, r.start), ops)


def select_latest_start(requests, ops=None):
    """Mirror image of EFT (scan by latest start). Also optimal - used as a control in the experiments."""
    return select_by_key(requests, lambda r: (-r.start, -r.finish), ops)


def select_fewest_conflicts(requests, ops=None):
    """Repeatedly accept the remaining request that overlaps the fewest other remaining requests
    (ties: earliest finish), then delete it and everything that overlaps it."""
    ops = Counter() if ops is None else ops
    validate(requests)
    remaining, chosen = list(requests), []
    while remaining:
        def conflicts(r):
            ops["compatibility_checks"] += len(remaining) - 1
            return sum(1 for o in remaining if o is not r and not compatible(r, o))
        best = min(remaining, key=lambda r: (conflicts(r), r.finish, r.start))
        chosen.append(best)
        remaining = [o for o in remaining if o is not best and compatible(best, o)]
    return sorted(chosen, key=lambda r: r.start)


RULES = {"earliest finish (EFT)": select_eft, "latest start": select_latest_start,
         "earliest start": select_earliest_start, "shortest duration": select_shortest,
         "fewest conflicts": select_fewest_conflicts}


# ----------------------------------------------------------------------------- exact references
def optimum_bruteforce(requests, ops=None):
    """Exact maximum by checking all 2^n subsets (n <= 20). Used to certify small instances."""
    ops = Counter() if ops is None else ops
    n = len(requests)
    if n > 20:
        raise ValueError("brute force limited to n <= 20")
    clash = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and not compatible(requests[i], requests[j]):
                clash[i] |= 1 << j
    best = 0
    for mask in range(1 << n):
        ops["subsets"] += 1
        m, ok, size = mask, True, 0
        while m:
            low = m & -m
            i = low.bit_length() - 1
            if clash[i] & mask:
                ok = False
                break
            size += 1
            m ^= low
        if ok and size > best:
            best = size
    return best


def optimum_dp(requests):
    """Exact maximum by dynamic programming (weighted interval scheduling with unit weights):
    OPT(j) = max(OPT(j-1), 1 + OPT(p(j))), p(j) = number of requests finishing <= start_j."""
    ordered = sorted(requests, key=lambda r: r.finish)
    finishes = [r.finish for r in ordered]
    opt = [0] * (len(ordered) + 1)
    for j, r in enumerate(ordered, start=1):
        p = bisect.bisect_right(finishes, r.start, 0, j - 1)
        opt[j] = max(opt[j - 1], 1 + opt[p])
    return opt[-1]


# ----------------------------------------------------------------------------- the designed instances
COUNTER_EXAMPLES = {
    "earliest start": [("C1", "08:00", "17:00"), ("C2", "09:00", "10:00"), ("C3", "11:00", "12:00"),
                       ("C4", "13:00", "14:00")],
    "shortest duration": [("S1", "09:00", "12:00"), ("S2", "12:00", "15:00"), ("S3", "11:30", "12:30")],
    "fewest conflicts": [("T1", "08:00", "10:00"), ("T2", "10:00", "12:00"), ("T3", "12:00", "14:00"),
                         ("T4", "14:00", "16:00"), ("M1", "09:30", "10:30"), ("M2", "11:30", "12:30"),
                         ("M3", "13:30", "14:30"), ("X1", "09:00", "10:15"), ("X2", "09:15", "10:30"),
                         ("X3", "09:45", "10:30"), ("Y1", "13:45", "15:00"), ("Y2", "13:30", "14:45"),
                         ("Y3", "13:30", "14:15")],
}


def ids(reqs):
    return ",".join(r.rid for r in reqs)


def main():
    given = load_requests(os.path.join(HERE, "test_data", "given_G1_bookings.csv"))
    print("TASK 1 - ACTIVITY SELECTION: EOC briefing-room bookings (half-open intervals [start, finish))")
    print("=" * 100)
    print("Given test case G1 - 11 booking requests for one day")
    print(f"  {'id':<4} {'agency':<26} {'start':>5}  {'finish':>6}")
    for r in given:
        print(f"  {r.rid:<4} {r.agency:<26} {hhmm(r.start):>5}  {hhmm(r.finish):>6}")

    print("\nStep 1-2: sort by finish time, then scan once (greedy choice = earliest compatible finish)")
    print(f"  {'step':>4} {'req':<4} {'interval':<13} {'last finish':>11}  decision")
    ops, trace = Counter(), []
    chosen = select_eft(given, ops, trace)
    for k, (r, last, dec) in enumerate(trace, 1):
        lf = "-" if last == float("-inf") else hhmm(last)
        print(f"  {k:>4} {r.rid:<4} {hhmm(r.start)}-{hhmm(r.finish):<7} {lf:>11}  {dec}")
    print(f"\n  Accepted {len(chosen)} requests: {ids(chosen)}")
    print(f"  Operation counts: {ops['sort_comparisons']} sort comparisons + {ops['compatibility_checks']} "
          f"compatibility checks")
    bf = Counter()
    best = optimum_bruteforce(given, bf)
    print(f"  Brute-force optimum over {bf['subsets']:,} subsets = {best}  -> greedy is "
          f"{'OPTIMAL' if best == len(chosen) else 'NOT optimal'};  DP optimum = {optimum_dp(given)}")

    g2 = load_requests(os.path.join(HERE, "test_data", "given_G2_back_to_back.csv"))
    c2 = select_eft(g2)
    print(f"\nGiven test case G2 (back-to-back sessions): accepted {len(c2)} -> {ids(c2)} "
          f"(touching endpoints are compatible); optimum {optimum_bruteforce(g2)}")

    print("\nCounter-examples: other 'natural' greedy rules are NOT optimal")
    print(f"  {'rule under test':<18} {'n':>3} {'rule picks':<28} {'EFT picks':<20} {'optimum':>7}")
    for rule, spec in COUNTER_EXAMPLES.items():
        reqs = make_requests(spec)
        got, eft = RULES[rule](reqs), select_eft(reqs)
        print(f"  {rule:<18} {len(reqs):>3} {str(len(got)) + ' = ' + ids(got):<28} "
              f"{str(len(eft)) + ' = ' + ids(eft):<20} {optimum_bruteforce(reqs):>7}")

    print("\nBoundary and invalid-input cases")
    cases = [("empty request list", []),
             ("single request", [("B1", "09:00", "10:00")]),
             ("three identical requests", [("I1", "14:00", "15:00"), ("I2", "14:00", "15:00"),
                                           ("I3", "14:00", "15:00")]),
             ("all-day request + 4 inside", [("L", "08:00", "18:00"), ("a", "09:00", "10:00"),
                                             ("b", "10:00", "11:00"), ("c", "13:00", "14:00"),
                                             ("d", "15:00", "16:00")])]
    for name, spec in cases:
        reqs = make_requests(spec)
        got = select_eft(reqs)
        print(f"  {name:<28} -> accepted {len(got)} [{ids(got)}]   optimum {optimum_bruteforce(reqs)}")
    for name, spec in [("finish before start", [("E1", "11:00", "10:00")]),
                       ("zero-length request", [("E2", "10:00", "10:00")])]:
        try:
            select_eft(make_requests(spec))
            print(f"  {name:<28} -> accepted (UNEXPECTED)")
        except ValueError as e:
            print(f"  {name:<28} -> rejected: ValueError: {e}")


if __name__ == "__main__":
    main()
