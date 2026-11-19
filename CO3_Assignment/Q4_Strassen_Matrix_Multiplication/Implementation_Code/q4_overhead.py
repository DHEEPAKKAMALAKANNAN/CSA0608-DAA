"""Q4 - engineering analysis of Strassen (Student A): repeated timing, crossover, overhead breakdown and memory.

Scenario (drone-delivery operations centre): zone-demand forecasts multiply n x n zone-to-zone matrices. The counted
experiments in q4_experiments.py show that Strassen saves multiplications; this script asks what the saving is worth
in practice on this computer.

  E5  REPEATED TIMING - conventional vs hybrid Strassen (dynamic padding, cutoff 32 and 64) at n = 64 ... 512;
      median, minimum and maximum of 5 runs (3 runs for n >= 384) -> practical time crossover range, together with
      the operation-count ratio from the counters.
  E6  OVERHEAD BREAKDOWN - the helpers of q4_strassen are wrapped with timers (monkeypatching the module), so the
      time of one product is split into: block additions/subtractions, split/join copying, padding/unpadding,
      base-case (conventional) multiplications and the rest (recursion, call and bookkeeping overhead).
  E7  MEMORY - peak memory allocated during one product (tracemalloc) and the number of temporary matrices created.
  E8  LIBRARY REFERENCE - numpy's BLAS product (float64) at the same sizes, to show what an optimised conventional
      kernel achieves.
  E9  FLOATING-POINT ACCURACY - real-valued matrices (entries in [-1, 1]): largest error of the conventional product
      and of Strassen against a correctly rounded reference (math.fsum of every dot product).
Every Strassen product is checked against the conventional product.
Run:  py -3 q4_overhead.py      (about 3-4 minutes; timings are noisy because other programs share the processor)
"""
import csv
import math
import os
import random
import statistics
import time
import tracemalloc

import numpy as np

import q4_strassen as qs
from q4_strassen import OpCounter, conventional_multiply, random_matrix, strassen_multiply

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")


def write_csv(name, rows):
    """Write a list of dicts to results/<name>."""
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, name), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def time_runs(func, repeats):
    """Run func() `repeats` times; return (last result, list of seconds)."""
    times, result = [], None
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = func()
        times.append(time.perf_counter() - t0)
    return result, times


# ----------------------------------------------------------------------------- E5 repeated timing
def experiment_timing(rng):
    print("E5  REPEATED TIMING - conventional vs hybrid Strassen (dynamic padding); median / min / max in ms")
    print(f"   {'n':>4} {'method':<14} {'runs':>4} | {'median':>9} {'min':>9} {'max':>9} | "
          f"{'total ops':>12} {'ops gain':>8} {'time gain':>9} | ok")
    print("   " + "-" * 92)
    rows = []
    for n in (64, 128, 256, 384, 512):
        repeats = 5 if n <= 256 else 3
        A, B = random_matrix(n, rng), random_matrix(n, rng)
        conv_ops = OpCounter()
        C_ref, t_conv = time_runs(lambda: conventional_multiply(A, B, OpCounter()), repeats)
        conventional_multiply(A, B, conv_ops)
        med_conv = statistics.median(t_conv)
        configs = [("conventional", None, C_ref, t_conv, conv_ops)]
        for c in (32, 64):
            ops = OpCounter()
            C, t = time_runs(lambda: strassen_multiply(A, B, OpCounter(), c), repeats)
            strassen_multiply(A, B, ops, c)
            configs.append((f"Strassen c={c}", c, C, t, ops))
        for name, c, C, t, ops in configs:
            med = statistics.median(t)
            ops_gain = conv_ops.total / ops.total
            time_gain = med_conv / med
            ok = C == C_ref
            print(f"   {n:>4} {name:<14} {repeats:>4} | {med * 1e3:>9.1f} {min(t) * 1e3:>9.1f} {max(t) * 1e3:>9.1f} | "
                  f"{ops.total:>12,} {ops_gain:>7.2f}x {time_gain:>8.2f}x | {'yes' if ok else 'NO'}")
            rows.append({"n": n, "method": name, "cutoff": c or "", "runs": repeats,
                         "median_ms": round(med * 1e3, 2), "min_ms": round(min(t) * 1e3, 2),
                         "max_ms": round(max(t) * 1e3, 2), "mults": ops.mults, "adds": ops.adds,
                         "total_ops": ops.total, "ops_gain": round(ops_gain, 3), "time_gain": round(time_gain, 3),
                         "correct": ok})
    write_csv("q4_timing.csv", rows)
    return rows


# ----------------------------------------------------------------------------- E6 overhead breakdown
class Profiler:
    """Wraps selected functions of q4_strassen with timers (exclusive time per category)."""

    CATEGORIES = {"mat_add": "add/sub", "mat_sub": "add/sub", "split": "split/join", "join": "split/join",
                  "pad": "pad/unpad", "unpad": "pad/unpad", "conventional_multiply": "base case"}

    def __init__(self):
        self.seconds = {cat: 0.0 for cat in self.CATEGORIES.values()}
        self.calls = {name: 0 for name in self.CATEGORIES}
        self.originals = {}

    def __enter__(self):
        for name, cat in self.CATEGORIES.items():
            original = getattr(qs, name)
            self.originals[name] = original
            setattr(qs, name, self._wrap(name, cat, original))
        return self

    def _wrap(self, name, cat, original):
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            result = original(*args, **kwargs)
            self.seconds[cat] += time.perf_counter() - t0
            self.calls[name] += 1
            return result
        return wrapper

    def __exit__(self, *exc):
        for name, original in self.originals.items():
            setattr(qs, name, original)


def experiment_overhead(rng):
    print("\nE6  OVERHEAD BREAKDOWN - share of the time of one product (helpers wrapped with timers)")
    print(f"   {'n':>4} {'cut':>4} | {'total ms':>9} | {'add/sub':>8} {'split/join':>10} {'pad/unpad':>9} "
          f"{'base case':>9} {'recursion+rest':>14} | {'calls':>7} {'adds/mults':>10}")
    print("   " + "-" * 104)
    rows = []
    for n, c in ((128, 1), (128, 16), (256, 8), (256, 32), (129, 32), (200, 32)):
        A, B = random_matrix(n, rng), random_matrix(n, rng)
        ops = OpCounter()
        with Profiler() as prof:
            t0 = time.perf_counter()
            C = qs.strassen_multiply(A, B, ops, c)
            total = time.perf_counter() - t0
        assert C == conventional_multiply(A, B, OpCounter())
        parts = dict(prof.seconds)
        parts["recursion+rest"] = max(total - sum(parts.values()), 0.0)
        share = {k: 100 * v / total for k, v in parts.items()}
        print(f"   {n:>4} {c:>4} | {total * 1e3:>9.1f} | {share['add/sub']:>7.1f}% {share['split/join']:>9.1f}% "
              f"{share['pad/unpad']:>8.1f}% {share['base case']:>8.1f}% {share['recursion+rest']:>13.1f}% | "
              f"{ops.calls:>7,} {ops.adds / ops.mults:>10.2f}")
        rows.append({"n": n, "cutoff": c, "total_ms": round(total * 1e3, 1),
                     **{f"pct_{k.replace('/', '_').replace('+', '_')}": round(v, 1) for k, v in share.items()},
                     "strassen_calls": ops.calls, "pads": ops.pads, "mults": ops.mults, "adds": ops.adds,
                     "add_calls": prof.calls["mat_add"] + prof.calls["mat_sub"],
                     "base_calls": prof.calls["conventional_multiply"]})
    print("   (the wrappers add a little time of their own; 'recursion+rest' = total - all wrapped categories)")
    write_csv("q4_overhead.csv", rows)
    return rows


# ----------------------------------------------------------------------------- E7 memory
def temporaries(n, cutoff):
    """Matrices created by one Strassen product (dynamic padding): per splitting call 8 blocks (split), 10 operand
    sums, 8 combine results and 1 join; +2 padded copies and 1 unpadded result when the size is odd."""
    if n <= cutoff:
        return 1                                    # the conventional result matrix (+ B transposed, not counted)
    h = (n + 1) // 2
    own = 8 + 10 + 8 + 1 + (3 if 2 * h != n else 0)
    return own + 7 * temporaries(h, cutoff)


def experiment_memory(rng):
    print("\nE7  MEMORY - peak bytes allocated during one product (tracemalloc) and temporary matrices created")
    print(f"   {'n':>4} {'method':<14} | {'peak KiB':>9} {'peak / input':>12} {'vs conv':>8} | "
          f"{'temp matrices':>13} {'calls':>7}")
    print("   " + "-" * 80)
    rows = []
    for n in (32, 64):
        A, B = random_matrix(n, rng), random_matrix(n, rng)
        tracemalloc.start()
        tracemalloc.reset_peak()
        base = tracemalloc.get_traced_memory()[0]
        conventional_multiply(A, B, OpCounter())
        input_bytes = None
        configs = []
        peak_conv = tracemalloc.get_traced_memory()[1] - base
        configs.append(("conventional", None, peak_conv, 2, 1))
        for c in (1, 8, 16):
            if c >= n:
                continue
            tracemalloc.reset_peak()
            base = tracemalloc.get_traced_memory()[0]
            ops = OpCounter()
            strassen_multiply(A, B, ops, c)
            peak = tracemalloc.get_traced_memory()[1] - base
            configs.append((f"Strassen c={c}", c, peak, temporaries(n, c), ops.calls))
        tracemalloc.stop()
        # size of one n x n matrix of small ints as Python lists (pointer arrays; small ints are cached objects)
        tracemalloc.start()
        M = [[rng.randint(0, 9) for _ in range(n)] for _ in range(n)]
        input_bytes = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        del M
        for name, c, peak, temps, calls in configs:
            print(f"   {n:>4} {name:<14} | {peak / 1024:>9.1f} {peak / input_bytes:>11.1f}x {peak / peak_conv:>7.2f}x | "
                  f"{temps:>13,} {calls:>7,}")
            rows.append({"n": n, "method": name, "cutoff": c or "", "peak_bytes": peak,
                         "one_matrix_bytes": input_bytes, "peak_over_matrix": round(peak / input_bytes, 2),
                         "peak_over_conventional": round(peak / peak_conv, 2),
                         "temp_matrices": temps, "calls": calls})
    print("   peak / input = peak bytes divided by the bytes of ONE n x n input matrix stored as lists of lists;")
    print("   products > 256 are new int objects (28 bytes each), so even the conventional result costs > 1 matrix")
    write_csv("q4_memory.csv", rows)
    return rows


# ----------------------------------------------------------------------------- E8 library reference
def experiment_numpy(rng):
    print("\nE8  LIBRARY REFERENCE - numpy float64 product (optimised BLAS conventional kernel), median of 5 runs")
    rows = []
    line = []
    for n in (64, 128, 256, 512):
        A = np.array(random_matrix(n, rng), dtype=np.float64)
        B = np.array(random_matrix(n, rng), dtype=np.float64)
        _, t = time_runs(lambda: A @ B, 5)
        med = statistics.median(t)
        line.append(f"n = {n}: {med * 1e3:.3f} ms")
        rows.append({"n": n, "numpy_median_ms": round(med * 1e3, 4)})
    print("   " + ";  ".join(line))
    write_csv("q4_numpy.csv", rows)
    return rows


# ----------------------------------------------------------------------------- E9 floating-point accuracy
def experiment_accuracy(rng):
    print("\nE9  FLOATING-POINT ACCURACY - entries uniform in [-1, 1]; max |error| against math.fsum reference")
    print(f"   {'n':>4} | {'conventional':>12} | {'Strassen c=1':>12} {'ratio':>7} | {'Strassen c=16':>13} {'ratio':>7}")
    print("   " + "-" * 70)
    rows = []
    for n in (32, 64, 128):
        A = [[rng.uniform(-1, 1) for _ in range(n)] for _ in range(n)]
        B = [[rng.uniform(-1, 1) for _ in range(n)] for _ in range(n)]
        Bt = [list(col) for col in zip(*B)]
        ref = [[math.fsum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]

        def max_err(C):
            return max(abs(c - r) for rc, rr in zip(C, ref) for c, r in zip(rc, rr))
        e_conv = max_err(conventional_multiply(A, B, OpCounter()))
        e_s1 = max_err(strassen_multiply(A, B, OpCounter(), 1))
        e_s16 = max_err(strassen_multiply(A, B, OpCounter(), 16))
        print(f"   {n:>4} | {e_conv:>12.2e} | {e_s1:>12.2e} {e_s1 / e_conv:>6.1f}x | {e_s16:>13.2e} {e_s16 / e_conv:>6.1f}x")
        rows.append({"n": n, "err_conventional": e_conv, "err_strassen_c1": e_s1, "err_strassen_c16": e_s16})
    write_csv("q4_accuracy.csv", rows)
    return rows


def main():
    rng = random.Random(42)
    print("Q4 ENGINEERING ANALYSIS - repeated timing, crossover, overhead and memory (seed 42, entries 0..9)")
    print("=" * 108)
    timing = experiment_timing(rng)
    experiment_overhead(rng)
    experiment_memory(rng)
    numpy_rows = experiment_numpy(rng)
    experiment_accuracy(rng)

    print("\nPRACTICAL CROSSOVER (E5, median times)")
    for c in (32, 64):
        faster = [r["n"] for r in timing if r["cutoff"] == c and r["time_gain"] > 1.0]
        gains = ", ".join(f"{r['n']}: {r['time_gain']:.2f}x" for r in timing if r["cutoff"] == c)
        print(f"   Strassen c={c}: time gain {gains}  -> faster at n = {faster if faster else 'none'}")
    conv512 = next(r["median_ms"] for r in timing if r["n"] == 512 and r["cutoff"] == "")
    np512 = next(r["numpy_median_ms"] for r in numpy_rows if r["n"] == 512)
    print(f"   numpy (BLAS) at n = 512 is {conv512 / np512:,.0f}x faster than our pure-Python conventional product")
    print("CSV written: results/q4_timing.csv, q4_overhead.csv, q4_memory.csv, q4_numpy.csv, q4_accuracy.csv")


if __name__ == "__main__":
    main()
