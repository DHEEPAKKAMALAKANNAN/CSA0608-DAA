"""Q7 - Day-4 Design Challenge: Maximum Subarray Sum by Divide and Conquer (CSA06 DAA, Assignment 3 - CO3).

Problem (drone-delivery operations centre): the finance team has the net profit or loss of one delivery hub for
each operating hour, p[0..n-1] (rupees; negative = loss, e.g. bad weather, idle drones, re-deliveries). It wants
the MOST PROFITABLE CONTIGUOUS RUN OF HOURS: indices i <= j maximising p[i] + p[i+1] + ... + p[j]
(the run must contain at least one hour, so when every hour is a loss the answer is the smallest single loss).

Algorithms (pure Python, every basic operation counted):
  brute_force_max_subarray  baseline: every start i, running sum over every end j -> n(n+1)/2 additions and
                            n(n+1)/2 comparisons, Theta(n^2).
  dc_crossing               Student A's repaired proposal (textbook D&C): split at the middle, solve both halves,
                            and scan outwards from the middle for the best run CROSSING the split;
                            T(n) = 2T(n/2) + Theta(n) = Theta(n log n).
  dc_joint                  JOINT FINAL DESIGN: split at the middle; every call returns the 4-tuple summary
                            (total, best prefix, best suffix, best run) WITH the hour indices of each run, so the
                            crossing run is L.suffix + R.prefix and the combine is Theta(1);
                            T(n) = 2T(n/2) + Theta(1) = Theta(n).
  kadane                    linear scan used ONLY as an independent reference in the tests (not divide and conquer).

Counted operations: additions of profit values, comparisons of profit values, calls (recursion-tree nodes) and
maximum recursion depth (root = 0).
Run:  py -3 q7_max_subarray.py   (demo with a recursion trace; experiments: q7_experiments.py; tests: q7_tests.py)
"""
import random


class Counter:
    """Basic-operation counters of one run."""

    def __init__(self):
        self.additions = 0
        self.comparisons = 0
        self.calls = 0
        self.max_depth = 0

    @property
    def total(self):
        """Additions + comparisons."""
        return self.additions + self.comparisons


# ----------------------------------------------------------------------------- baseline O(n^2)
def brute_force_max_subarray(p, c=None):
    """Return (best_sum, i, j) by trying every start i and extending the run one hour at a time."""
    c = c or Counter()
    best, bi, bj = p[0], 0, 0
    for i in range(len(p)):
        run = 0
        for j in range(i, len(p)):
            run += p[j]                                   # one addition per (i, j) pair
            c.additions += 1
            c.comparisons += 1
            if run > best:                                # one comparison per (i, j) pair
                best, bi, bj = run, i, j
    return best, bi, bj


# ----------------------------------------------------------------------------- Student A repaired: Theta(n log n)
def dc_crossing(p, c=None):
    """Return (best_sum, i, j): D&C with an explicit O(n) scan for the best run crossing the middle."""
    c = c or Counter()

    def crossing(lo, mid, hi):
        """Best run that contains both p[mid] and p[mid + 1]: best suffix of the left + best prefix of the right."""
        s, left_best, li = 0, None, mid
        for k in range(mid, lo - 1, -1):                  # scan leftwards from the middle
            s += p[k]
            c.additions += 1
            if left_best is None or s > left_best:
                if left_best is not None:
                    c.comparisons += 1
                left_best, li = s, k
            else:
                c.comparisons += 1
        s, right_best, rj = 0, None, mid + 1
        for k in range(mid + 1, hi + 1):                  # scan rightwards from the middle
            s += p[k]
            c.additions += 1
            if right_best is None or s > right_best:
                if right_best is not None:
                    c.comparisons += 1
                right_best, rj = s, k
            else:
                c.comparisons += 1
        c.additions += 1
        return left_best + right_best, li, rj

    def solve(lo, hi, depth):
        c.calls += 1
        c.max_depth = max(c.max_depth, depth)
        if lo == hi:                                      # base case: one hour
            return p[lo], lo, hi
        mid = (lo + hi) // 2                              # DIVIDE
        left = solve(lo, mid, depth + 1)                  # CONQUER
        right = solve(mid + 1, hi, depth + 1)
        cross = crossing(lo, mid, hi)                     # COMBINE: Theta(n) scan
        c.comparisons += 2
        best = left if left[0] >= right[0] else right
        return best if best[0] >= cross[0] else cross

    return solve(0, len(p) - 1, 0)


# ----------------------------------------------------------------------------- JOINT FINAL DESIGN: Theta(n)
class Summary:
    """What one subproblem p[lo..hi] returns to its parent (the information needed by the combine step).

    total            sum of the whole segment
    pre, pre_end     best prefix sum p[lo..pre_end]
    suf, suf_start   best suffix sum p[suf_start..hi]
    best, bi, bj     best run anywhere inside the segment, p[bi..bj]
    """
    __slots__ = ("total", "pre", "pre_end", "suf", "suf_start", "best", "bi", "bj")

    def __init__(self, total, pre, pre_end, suf, suf_start, best, bi, bj):
        self.total, self.pre, self.pre_end = total, pre, pre_end
        self.suf, self.suf_start = suf, suf_start
        self.best, self.bi, self.bj = best, bi, bj

    def as_tuple(self):
        return (self.total, self.pre, self.suf, self.best)


def combine(L, R, c):
    """Theta(1) combine of two adjacent segment summaries: exactly 4 additions and 4 comparisons."""
    total = L.total + R.total                             # 1 addition
    through = L.total + R.pre                             # prefix that runs through the whole left half
    c.additions += 2
    c.comparisons += 1
    if through > L.pre:
        pre, pre_end = through, R.pre_end
    else:
        pre, pre_end = L.pre, L.pre_end
    through = R.total + L.suf                             # suffix that runs through the whole right half
    c.additions += 1
    c.comparisons += 1
    if through > R.suf:
        suf, suf_start = through, L.suf_start
    else:
        suf, suf_start = R.suf, R.suf_start
    cross = L.suf + R.pre                                 # the best run crossing the split
    c.additions += 1
    c.comparisons += 2
    if L.best >= R.best:
        best, bi, bj = L.best, L.bi, L.bj
    else:
        best, bi, bj = R.best, R.bi, R.bj
    if cross > best:
        best, bi, bj = cross, L.suf_start, R.pre_end
    return Summary(total, pre, pre_end, suf, suf_start, best, bi, bj)


def dc_joint(p, c=None, trace=None):
    """Return (best_sum, i, j) with the joint 4-tuple design; optional trace of every node (for the demo)."""
    if not p:
        raise ValueError("at least one hour of data is required")
    c = c or Counter()

    def solve(lo, hi, depth):
        c.calls += 1
        c.max_depth = max(c.max_depth, depth)
        if lo == hi:                                      # base case: one hour, everything equals p[lo]
            s = Summary(p[lo], p[lo], lo, p[lo], lo, p[lo], lo, lo)
        else:
            mid = (lo + hi) // 2                          # DIVIDE at the middle hour
            s = combine(solve(lo, mid, depth + 1), solve(mid + 1, hi, depth + 1), c)   # CONQUER + COMBINE
        if trace is not None:
            trace.append((depth, lo, hi, s))
        return s

    s = solve(0, len(p) - 1, 0)
    return s.best, s.bi, s.bj


# ----------------------------------------------------------------------------- independent reference
def kadane(p):
    """Linear-scan reference (Kadane): best sum only. Used in the tests to cross-check, not part of the design."""
    best = cur = p[0]
    for x in p[1:]:
        cur = x if cur < 0 else cur + x
        best = max(best, cur)
    return best


def hourly_profits(n, seed=42):
    """Synthetic hourly net profit (Rs) of a hub: daily demand cycle + noise, with occasional loss-making hours."""
    rng = random.Random(seed)
    out = []
    for h in range(n):
        hour = h % 24
        demand = 250 if 10 <= hour <= 13 or 17 <= hour <= 20 else (-220 if hour < 6 else -80)
        out.append(demand + rng.randint(-350, 350))
    return out


def main():
    print("=" * 100)
    print("Q7 DEMO - most profitable contiguous run of delivery hours (Maximum Subarray Sum)")
    print("=" * 100)
    p = [-120, 340, -60, 410, -380, 150, 220, -90]
    print("Hourly net profit, hours 0-7 (Rs):", p)
    trace = []
    c = Counter()
    best, i, j = dc_joint(p, c, trace)
    print("\nJoint D&C design - summary returned by every node (total, best prefix, best suffix, best run):")
    for depth, lo, hi, s in sorted(trace, key=lambda t: (t[0], t[1])):
        print(f"   depth {depth}  hours [{lo}..{hi}]{'':<{6 - len(str(lo)) - len(str(hi))}}"
              f"total {s.total:>5}  prefix {s.pre:>5} (to {s.pre_end})  suffix {s.suf:>5} (from {s.suf_start})"
              f"  best {s.best:>5} = hours {s.bi}..{s.bj}")
    print(f"Result: best run = hours {i}..{j}, profit Rs {best}  ({c.additions} additions, {c.comparisons} "
          f"comparisons = 4(n-1) each; {c.calls} calls = 2n-1, depth {c.max_depth})")

    cb = Counter()
    bb = brute_force_max_subarray(p, cb)
    cx = Counter()
    bx = dc_crossing(p, cx)
    print("\nSame 8 hours with the other methods:")
    print(f"   brute force O(n^2)      : {bb}  additions {cb.additions:>3}, comparisons {cb.comparisons:>3}"
          f"  (n(n+1)/2 = {len(p) * (len(p) + 1) // 2})")
    print(f"   D&C crossing scan       : {bx}  additions {cx.additions:>3}, comparisons {cx.comparisons:>3}")
    print(f"   joint D&C (4-tuple)     : {(best, i, j)}  additions {c.additions:>3}, comparisons {c.comparisons:>3}")
    print(f"   Kadane reference (sum)  : {kadane(p)}")

    week = hourly_profits(24 * 7)
    cj, cb = Counter(), Counter()
    rj = dc_joint(week, cj)
    rb = brute_force_max_subarray(week, cb)
    print(f"\nOne week of hourly data (n = {len(week)} hours, seed 42):")
    print(f"   joint D&C  : best run hours {rj[1]}..{rj[2]} (day {rj[1] // 24 + 1} {rj[1] % 24:02d}:00 to day "
          f"{rj[2] // 24 + 1} {rj[2] % 24 + 1:02d}:00), profit Rs {rj[0]:,};  {cj.total:,} operations")
    print(f"   brute force: {rb};  {cb.total:,} operations  -> same profit: {rj[0] == rb[0]}")


if __name__ == "__main__":
    main()
