"""
Task 1 (supporting experiment for 1.3) - how the optimum and the DP work depend on the line width W and on n.

E1  The same 20-word text for every W from 13 (the longest word) to 40: DP penalty, greedy first-fit penalty,
    number of lines and feasible candidate lines examined  ->  results/t1_width_sweep.csv
E2  Random texts (seed 42, word lengths 2..10) of n = 1,000 .. 16,000 words at W = 60: DP states and candidates
    vs the bound n * L (L = maximum words per line)  ->  results/t1_scaling.csv
Run:  py -3 word_wrap_width_sweep.py
"""
import csv
import os
import random
import time
from collections import Counter

import word_wrap_dp as ww

HERE = os.path.dirname(os.path.abspath(__file__))


def write_csv(name, rows):
    with open(os.path.join(HERE, "results", name), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def width_sweep(words):
    print("E1  Same text, W = 13 .. 40")
    print(f"    {'W':>3} {'DP penalty':>10} {'greedy':>7} {'lines':>5} {'candidates':>10}   DP line ends")
    rows = []
    for width in range(max(len(w) for w in words), 41):
        ops = Counter()
        total, lines, _ = ww.word_wrap_dp(words, width, ops)
        greedy, _ = ww.greedy_first_fit(words, width)
        rows.append(dict(width=width, dp_penalty=total, greedy_penalty=greedy, lines=len(lines),
                         candidates=ops["candidates"]))
        flag = " greedy worse" if greedy > total else ""
        print(f"    {width:>3} {total:>10} {greedy:>7} {len(lines):>5} {ops['candidates']:>10}   "
              f"{ww.layout_signature(lines)}{flag}")
    write_csv("t1_width_sweep.csv", rows)
    increases = sum(1 for a, b in zip(rows, rows[1:]) if b["dp_penalty"] > a["dp_penalty"])
    print(f"    W -> W+1 increased the optimum penalty in {increases} of {len(rows) - 1} steps (not monotone)")


def scaling():
    print("\nE2  Random texts at W = 60 (word lengths 2..10, seed 42)")
    print(f"    {'n words':>8} {'states':>8} {'candidates':>11} {'n * L bound':>11} {'cand / n':>8} {'time (ms)':>9}")
    rng, rows, width = random.Random(42), [], 60
    for n in (1000, 2000, 4000, 8000, 16000):
        words = ["x" * rng.randint(2, 10) for _ in range(n)]
        max_per_line = (width + 1) // 3              # shortest word 2 chars + 1 space
        ops = Counter()
        start = time.perf_counter()
        ww.word_wrap_dp(words, width, ops)
        ms = (time.perf_counter() - start) * 1000
        rows.append(dict(n=n, states=ops["states"], candidates=ops["candidates"], bound_nL=n * max_per_line,
                         candidates_per_word=round(ops["candidates"] / n, 2), time_ms=round(ms, 1)))
        print(f"    {n:>8,} {ops['states']:>8,} {ops['candidates']:>11,} {n * max_per_line:>11,} "
              f"{ops['candidates'] / n:>8.2f} {ms:>9.1f}")
    write_csv("t1_scaling.csv", rows)
    print("    candidates per word stay constant -> work grows linearly in n for a fixed W (Theta(n * L))")


def main():
    with open(os.path.join(HERE, "test_data", "layout_text.txt"), encoding="utf-8") as f:
        words = ww.tokenize(f.read())
    print("TASK 1 - WIDTH SWEEP AND SCALING OF THE WORD-WRAP DP")
    print("=" * 100)
    width_sweep(words)
    scaling()


if __name__ == "__main__":
    main()
