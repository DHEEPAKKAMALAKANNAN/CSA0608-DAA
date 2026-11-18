"""Shared helpers for the ShopSphere scalability-audit programs (CSA06 - CO1 - Assessment Tool 1).

This module holds the constants stated in the question paper (server speed, nightly window and the
two catalogue sizes), the folder that receives the CSV files, and a few small helpers so that every
program prints tidy, screenshot-friendly tables and the same "expected / actual / PASS|FAIL" lines.
"""
import csv
import gc
import time
from pathlib import Path

OPS_PER_SECOND = 10**8           # "the platform's servers execute 10^8 basic operations per second"
NIGHTLY_WINDOW_S = 10 * 60       # nightly processing window: 10 minutes = 600 seconds
N_CURRENT = 100_000              # catalogue size today
N_FUTURE = 1_000_000             # catalogue size expected within a year

SUPPORT_DIR = Path(__file__).resolve().parent.parent / "Supporting_Files"


def banner(title):
    """Print a program title framed by '=' lines."""
    line = "=" * max(70, len(title) + 4)
    print(f"{line}\n  {title}\n{line}")


def section(title):
    """Print a section heading."""
    print(f"\n--- {title} " + "-" * max(3, 96 - len(title)))


def print_table(headers, rows, right=None):
    """Print an aligned text table.

    headers : list of column titles
    rows    : list of rows (each a list of values; values are converted with str())
    right   : set of column indexes to right-align (default: every column except the first)
    """
    right = set(range(1, len(headers))) if right is None else set(right)
    cells = [[str(h) for h in headers]] + [[str(v) for v in r] for r in rows]
    widths = [max(len(row[c]) for row in cells) for c in range(len(headers))]

    def fmt(row):
        return "  ".join(v.rjust(w) if c in right else v.ljust(w)
                         for c, (v, w) in enumerate(zip(row, widths)))

    print(fmt(cells[0]))
    print("  ".join("-" * w for w in widths))
    for row in cells[1:]:
        print(fmt(row))


def write_csv(filename, headers, rows):
    """Write rows to Supporting_Files/<filename> and return the path."""
    SUPPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = SUPPORT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(rows)
    return path


def verdict(ok):
    """Return 'PASS' or 'FAIL'."""
    return "PASS" if ok else "FAIL"


def check(label, expected, actual):
    """Print one test line in the 'expected / actual / PASS|FAIL' format and return the result."""
    ok = expected == actual
    print(f"  {label:<52} expected = {expected!s:<16} actual = {actual!s:<16} {verdict(ok)}")
    return ok


def min_time(func, *args, repeats=5):
    """Wall-clock seconds of func(*args): one warm-up run, then the minimum of `repeats` runs.

    Timing is secondary evidence only (other programs share the CPU); operation counts are primary.
    Like the standard `timeit` module, the garbage collector is paused while timing.
    """
    func(*args)
    best = float("inf")
    gc.disable()
    try:
        for _ in range(repeats):
            t0 = time.perf_counter()
            func(*args)
            best = min(best, time.perf_counter() - t0)
    finally:
        gc.enable()
    return best


def fmt_int(x):
    """Format a number with thousands separators (rounded to an integer)."""
    return f"{round(x):,}"


def fmt_time(seconds):
    """Human-readable duration: s, min or h, whichever reads best."""
    if seconds < 1e-3:
        return f"{seconds * 1e6:.2f} us"
    if seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    if seconds < 120:
        return f"{seconds:.2f} s"
    if seconds < 2 * 3600:
        return f"{seconds / 60:.1f} min"
    return f"{seconds / 3600:.2f} h"
