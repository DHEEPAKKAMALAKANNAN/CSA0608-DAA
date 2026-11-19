"""Q6(b) - Meet-in-the-Middle for drone payload packing (CSA06 DAA, Assignment 3 - CO3).

Problem: a drone with payload capacity W grams must carry a subset of n waiting parcels (weights w_i in grams) whose
total weight is as large as possible without exceeding W (an exact fill, total = W, is ideal).  n is up to 40.

Methods (pure Python, operations counted):
  best_fill_brute_force  enumerate all 2^n subsets in Gray-code order: each subset differs from the previous one by
                         one parcel, so it costs exactly ONE addition/subtraction + one feasibility check. Theta(2^n).
  best_fill_mitm         Meet-in-the-Middle (Divide-and-Conquer on the item set):
      DIVIDE   the parcels into two halves of n/2;
      CONQUER  list all 2^(n/2) subset sums of each half IN SORTED ORDER (built by merging L and L + w, no sort);
      COMBINE  for every sum a of half 1 (a <= W), binary-search the largest sum b <= W - a of half 2;
               best = max(a + b).  Time Theta(n * 2^(n/2)), memory Theta(2^(n/2)).
      matcher="two_pointer" replaces the binary searches by one linear scan (A ascending, B descending): the
      combine step becomes Theta(2^(n/2)) - an improvement that the sorted lists make possible.
  best_fill_mitm_split   time-memory trade-off variant: store the sorted sums of only the first k parcels (2^k sums)
                         and enumerate the other n - k parcels (Gray code), binary-searching each of their 2^(n-k)
                         totals in the stored list: memory Theta(2^k), time Theta(2^k + k * 2^(n-k)).
                         k = 0 is brute force, k = n/2 is the balanced split.
  best_fill_dp           reference: dynamic programming over the capacity (bitset of reachable totals).

Run:  py -3 q6_meet_in_the_middle.py    (demo + experiments; writes ../Meet_in_the_Middle/results/*.csv)
"""
import csv
import math
import os
import random
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "Meet_in_the_Middle", "results")


class PackCounter:
    """Operation counters of one packing run."""

    def __init__(self):
        self.subsets = 0             # brute force: subsets examined
        self.additions = 0           # additions / subtractions of weights
        self.merge_comparisons = 0   # MITM: comparisons while merging sorted sum lists
        self.probes = 0              # MITM binary search: probes B[mid] <= target
        self.scan_steps = 0          # MITM two-pointer: steps of the linear scan
        self.stored_sums = 0         # MITM: number of subset sums held in memory

    def total_ops(self):
        return self.subsets + self.additions + self.merge_comparisons + self.probes + self.scan_steps


# ----------------------------------------------------------------------------------------------- brute force
def best_fill_brute_force(weights, W, counter):
    """Best total <= W over all 2^n subsets (Gray-code order). Returns (best total, bit mask of chosen parcels)."""
    n = len(weights)
    best, best_mask, total, mask = 0, 0, 0, 0          # the empty subset (total 0) is always feasible
    for i in range(1, 1 << n):
        bit = (i & -i).bit_length() - 1                # parcel whose status changes (Gray code)
        if mask >> bit & 1:
            total -= weights[bit]
        else:
            total += weights[bit]
        mask ^= 1 << bit
        if best < total <= W:                          # feasibility check + keep the best
            best, best_mask = total, mask
    counter.subsets += 1 << n
    counter.additions += (1 << n) - 1
    return best, best_mask


# ----------------------------------------------------------------------------------------------- meet in the middle
def sorted_subset_sums(weights, counter):
    """All 2^m subset sums of `weights` in ascending order (with bit masks), built by repeated merging."""
    sums, masks = [0], [0]
    for idx, w in enumerate(weights):
        bit = 1 << idx
        plus_s = [s + w for s in sums]                 # still sorted: every sum shifted by w
        plus_m = [m | bit for m in masks]
        counter.additions += len(sums)
        out_s, out_m = [], []
        i = j = comps = 0
        size = len(sums)
        while i < size and j < size:
            comps += 1
            if sums[i] <= plus_s[j]:
                out_s.append(sums[i])
                out_m.append(masks[i])
                i += 1
            else:
                out_s.append(plus_s[j])
                out_m.append(plus_m[j])
                j += 1
        out_s.extend(sums[i:])
        out_m.extend(masks[i:])
        out_s.extend(plus_s[j:])
        out_m.extend(plus_m[j:])
        counter.merge_comparisons += comps
        sums, masks = out_s, out_m
    counter.stored_sums += len(sums)
    return sums, masks


def best_fill_mitm(weights, W, counter, matcher="binary"):
    """Best total <= W by Meet-in-the-Middle. Returns (best total, bit mask over all n parcels)."""
    m = len(weights) // 2
    A, MA = sorted_subset_sums(weights[:m], counter)       # half 1: 2^m sums
    B, MB = sorted_subset_sums(weights[m:], counter)       # half 2: 2^(n-m) sums
    best, ma, mb = -1, 0, 0
    if matcher == "binary":
        probes, nb = 0, len(B)
        for idx in range(len(A)):
            a = A[idx]
            if a > W:                                      # A is ascending: no later a can fit either
                break
            target = W - a
            lo, hi, pos = 0, nb - 1, -1                    # largest pos with B[pos] <= target
            while lo <= hi:
                mid = (lo + hi) >> 1
                probes += 1
                if B[mid] <= target:
                    pos, lo = mid, mid + 1
                else:
                    hi = mid - 1
            if a + B[pos] > best:                          # B[0] = 0, so pos >= 0 whenever a <= W
                best, ma, mb = a + B[pos], MA[idx], MB[pos]
        counter.probes += probes
    else:                                                  # two-pointer scan
        i, j, steps = 0, len(B) - 1, 0
        while i < len(A) and j >= 0:
            steps += 1
            s = A[i] + B[j]
            if s <= W:
                if s > best:
                    best, ma, mb = s, MA[i], MB[j]
                i += 1
            else:
                j -= 1
        counter.scan_steps += steps
    return best, ma | (mb << m)


def best_fill_mitm_split(weights, W, k, counter):
    """Best total <= W storing only the 2^k sorted subset sums of weights[:k] (time-memory trade-off).

    The remaining n - k parcels are enumerated one subset at a time in Gray-code order (one addition each); for every
    feasible total t the largest stored sum <= W - t is found by binary search. Returns the best total."""
    A, _ = sorted_subset_sums(weights[:k], counter)       # the only list kept in memory: 2^k sums
    rest = weights[k:]
    pos, probes = bisect_right_count(A, W, None)           # the empty subset of the rest: best stored sum <= W
    best, total, mask, na = A[pos], 0, 0, len(A)           # A[0] = 0 <= W, so pos >= 0
    for i in range(1, 1 << len(rest)):
        bit = (i & -i).bit_length() - 1
        if mask >> bit & 1:
            total -= rest[bit]
        else:
            total += rest[bit]
        mask ^= 1 << bit
        if total <= W:
            lo, hi, pos = 0, na - 1, -1                   # largest stored sum <= W - total
            target = W - total
            while lo <= hi:
                mid = (lo + hi) >> 1
                probes += 1
                if A[mid] <= target:
                    pos, lo = mid, mid + 1
                else:
                    hi = mid - 1
            if total + A[pos] > best:
                best = total + A[pos]
    counter.subsets += 1 << len(rest)
    counter.additions += (1 << len(rest)) - 1
    counter.probes += probes
    return best


def bisect_right_count(A, target, counter):
    """(largest index j with A[j] <= target, probes used) by binary search on the ascending list A."""
    lo, hi, pos, probes = 0, len(A) - 1, -1, 0
    while lo <= hi:
        mid = (lo + hi) >> 1
        probes += 1
        if A[mid] <= target:
            pos, lo = mid, mid + 1
        else:
            hi = mid - 1
    if counter is not None:
        counter.probes += probes
    return pos, probes


def best_fill_dp(weights, W):
    """Reference answer: dynamic programming over capacities 0..W, the bitset `reach` marks reachable totals."""
    reach, full = 1, (1 << (W + 1)) - 1
    for w in weights:
        reach = (reach | (reach << w)) & full
    return reach.bit_length() - 1


def mask_total(weights, mask):
    """Total weight of the parcels selected by a bit mask."""
    return sum(w for i, w in enumerate(weights) if mask >> i & 1)


# ----------------------------------------------------------------------------------------------- experiments
def make_instance(n):
    """n parcels of 200-5,000 g (seeded per n) and a capacity W = 40 % of their total weight."""
    rng = random.Random(1000 + n)
    weights = [rng.randint(200, 5000) for _ in range(n)]
    return weights, int(0.4 * sum(weights))


BF_SIZES = [12, 16, 20, 22, 24]
MITM_SIZES = [12, 16, 20, 24, 28, 32, 36, 40]
LIMIT_S = 2.0


def timed(fn, weights, W, repeats=1):
    """Run fn(weights, W, counter) `repeats` times; return (result, counter of the last run, minimum seconds)."""
    best_t, res, c = math.inf, None, None
    for _ in range(repeats):
        c = PackCounter()
        t0 = time.perf_counter()
        res = fn(weights, W, c)
        best_t = min(best_t, time.perf_counter() - t0)
    return res, c, best_t


def run_mitm(weights, W, matcher, repeats):
    """Run Meet-in-the-Middle with the given matcher `repeats` times; return (result, counter, minimum seconds)."""
    best_t, res, c = math.inf, None, None
    for _ in range(repeats):
        c = PackCounter()
        t0 = time.perf_counter()
        res = best_fill_mitm(weights, W, c, matcher)
        best_t = min(best_t, time.perf_counter() - t0)
    return res, c, best_t


def predicted_mitm_ops(n, matcher):
    """Operation model used for extrapolation: generation (additions + merges) + combine step."""
    m = n // 2
    gen = 3 * ((1 << m) + (1 << (n - m)))
    return gen + ((1 << m) * (n - m + 1) if matcher == "binary" else (1 << m) + (1 << (n - m)))


def main():
    os.makedirs(RESULTS, exist_ok=True)
    print("=" * 112)
    print("Q6(b)  Payload packing by Meet-in-the-Middle - demo: 10 parcels, capacity W = 9,000 g")
    print("=" * 112)
    demo_w = [2300, 1700, 4100, 900, 3600, 2800, 1250, 600, 3350, 1900]
    W = 9000
    best_b, mask_b = best_fill_brute_force(demo_w, W, PackCounter())
    c = PackCounter()
    best_m, mask_m = best_fill_mitm(demo_w, W, c)
    chosen = [f"P{i + 1}:{w}" for i, w in enumerate(demo_w) if mask_m >> i & 1]
    print(f"  weights (g): {demo_w}")
    print(f"  half 1 = {demo_w[:5]} -> 32 sums;  half 2 = {demo_w[5:]} -> 32 sums")
    print(f"  brute force best = {best_b} g  |  MITM best = {best_m} g  |  DP reference = {best_fill_dp(demo_w, W)} g")
    print(f"  MITM load: {', '.join(chosen)}  (total {mask_total(demo_w, mask_m)} g, exact fill = {best_m == W})")
    print(f"  MITM operations: {c.additions} additions, {c.merge_comparisons} merge comparisons, {c.probes} probes"
          f"  vs brute force 2^10 = 1,024 subsets")

    rows = []
    print("\nBrute force (Gray-code enumeration of all 2^n subsets)")
    print(f"{'n':>4}{'subsets = 2^n':>16}{'additions':>14}{'time s':>10}{'ns/subset':>11}{'best g':>9}{'W g':>8}{'= DP':>6}")
    print("-" * 78)
    for n in BF_SIZES:
        weights, W = make_instance(n)
        (best, mask), c, t = timed(best_fill_brute_force, weights, W, repeats=3 if n <= 20 else 1)
        ok = best == best_fill_dp(weights, W) == mask_total(weights, mask)
        rows.append({"method": "brute_force", "n": n, "W": W, "best": best, "subsets": c.subsets,
                     "additions": c.additions, "merge_comparisons": 0, "probes": 0, "scan_steps": 0,
                     "stored_sums": 0, "total_ops": c.total_ops(), "theory": 1 << n, "time_s": round(t, 5),
                     "correct": ok})
        print(f"{n:>4}{c.subsets:>16,}{c.additions:>14,}{t:>10.3f}{t / c.subsets * 1e9:>11.0f}{best:>9,}{W:>8,}"
              f"{'yes' if ok else 'NO':>6}")

    print("\nMeet-in-the-Middle (sorted half-sum lists by merging; binary search or two-pointer combine)")
    print(f"{'n':>4}{'stored sums':>13}{'gen adds':>11}{'merge cmp':>12}{'probes':>13}{'(n/2)2^(n/2)':>14}"
          f"{'binary s':>10}{'2-ptr steps':>13}{'2-ptr s':>9}{'best g':>9}{'W g':>8}{'= DP':>6}")
    print("-" * 122)
    for n in MITM_SIZES:
        weights, W = make_instance(n)
        reps = 3 if n <= 28 else 1
        (best, mask), c, t = run_mitm(weights, W, "binary", reps)
        (best2, mask2), c2, t2 = run_mitm(weights, W, "two_pointer", reps)
        ok = best == best2 == best_fill_dp(weights, W) == mask_total(weights, mask) == mask_total(weights, mask2)
        theory = (n // 2) * (1 << (n // 2))
        for name, cc, tt in (("mitm_binary", c, t), ("mitm_two_pointer", c2, t2)):
            rows.append({"method": name, "n": n, "W": W, "best": best, "subsets": 0, "additions": cc.additions,
                         "merge_comparisons": cc.merge_comparisons, "probes": cc.probes, "scan_steps": cc.scan_steps,
                         "stored_sums": cc.stored_sums, "total_ops": cc.total_ops(),
                         "theory": theory if name == "mitm_binary" else 1 << (n // 2), "time_s": round(tt, 5),
                         "correct": ok})
        print(f"{n:>4}{c.stored_sums:>13,}{c.additions:>11,}{c.merge_comparisons:>12,}{c.probes:>13,}{theory:>14,}"
              f"{t:>10.3f}{c2.scan_steps:>13,}{t2:>9.3f}{best:>9,}{W:>8,}{'yes' if ok else 'NO':>6}")
    with open(os.path.join(RESULTS, "q6_mitm_growth.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ------------------------------------------------------------------ the 2-second decision
    lim_rows = []
    bf_last = [r for r in rows if r["method"] == "brute_force"][-1]
    c_bf = bf_last["time_s"] / bf_last["subsets"]
    n_bf = int(math.floor(math.log2(LIMIT_S / c_bf)))
    lim_rows.append({"method": "brute_force", "cost_per_op_ns": round(c_bf * 1e9, 1),
                     "largest_measured_n_within_2s": max(r["n"] for r in rows if r["method"] == "brute_force"
                                                         and r["time_s"] <= LIMIT_S),
                     "predicted_largest_n_within_2s": n_bf, "predicted_time_at_that_n_s": round(c_bf * 2 ** n_bf, 2),
                     "predicted_time_next_n_s": round(c_bf * 2 ** (n_bf + 1), 2)})
    for name, matcher in (("mitm_binary", "binary"), ("mitm_two_pointer", "two_pointer")):
        last = [r for r in rows if r["method"] == name][-1]
        c_op = last["time_s"] / predicted_mitm_ops(last["n"], matcher)
        n_lim = max(n for n in range(2, 80) if c_op * predicted_mitm_ops(n, matcher) <= LIMIT_S)
        lim_rows.append({"method": name, "cost_per_op_ns": round(c_op * 1e9, 1),
                         "largest_measured_n_within_2s": max(r["n"] for r in rows if r["method"] == name
                                                             and r["time_s"] <= LIMIT_S),
                         "predicted_largest_n_within_2s": n_lim,
                         "predicted_time_at_that_n_s": round(c_op * predicted_mitm_ops(n_lim, matcher), 2),
                         "predicted_time_next_n_s": round(c_op * predicted_mitm_ops(n_lim + 1, matcher), 2)})
    with open(os.path.join(RESULTS, "q6_mitm_limits.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lim_rows[0].keys()))
        w.writeheader()
        w.writerows(lim_rows)
    print(f"\nLargest number of parcels decided within {LIMIT_S:.0f} s (cost per operation from the largest run):")
    for r in lim_rows:
        print(f"  {r['method']:<17} {r['cost_per_op_ns']:>7.1f} ns/op   largest measured n within 2 s = "
              f"{r['largest_measured_n_within_2s']:>2}   predicted limit n = {r['predicted_largest_n_within_2s']:>2} "
              f"({r['predicted_time_at_that_n_s']} s; n + 1: {r['predicted_time_next_n_s']} s)")
    print(f"All {len(rows)} runs agree with the DP reference: {all(r['correct'] for r in rows)}")
    print("CSV written: Meet_in_the_Middle/results/q6_mitm_growth.csv, q6_mitm_limits.csv")


if __name__ == "__main__":
    main()
