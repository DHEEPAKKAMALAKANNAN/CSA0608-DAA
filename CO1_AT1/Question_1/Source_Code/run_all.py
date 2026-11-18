"""ShopSphere audit - run every program of the assignment in order and report exit codes and run times.

Order: the five module programs (they write the CSV files), part (f), part (g), the graph script (reads the
CSV files) and finally the test suite. Each program's output is saved as <program>_output.txt here.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROGRAMS = ["m1_duplicate_detector.py", "m2_rate_limiter.py", "m3_product_search.py",
            "m4_m5_recurrences.py", "m4_m5_simulation.py", "f_bound_proof_check.py",
            "scalability_estimates.py", "make_graphs.py", "run_tests.py"]


def main():
    failures = 0
    for program in PROGRAMS:
        t0 = time.perf_counter()
        proc = subprocess.run([sys.executable, program], cwd=HERE, capture_output=True, text=True,
                              encoding="utf-8")
        seconds = time.perf_counter() - t0
        log = HERE / program.replace(".py", "_output.txt")
        log.write_text(proc.stdout + proc.stderr, encoding="utf-8", newline="\n")
        failures += proc.returncode != 0
        print(f"{program:<28} exit {proc.returncode}   {seconds:7.1f} s")
    print(f"\n{len(PROGRAMS) - failures}/{len(PROGRAMS)} programs finished with exit code 0")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
