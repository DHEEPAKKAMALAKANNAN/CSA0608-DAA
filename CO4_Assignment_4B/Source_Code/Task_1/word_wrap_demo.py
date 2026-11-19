"""
Task 1.1 + 1.2 - run the word-wrap DP on the layout text (test_data/layout_text.txt) at W = 21 and show
  * the optimal layout: words on each line, unused spaces s, penalty s^2 (0 for the final line), total;
  * the DP states best[i] / next_break[i] for every suffix, with every feasible candidate line that was
    compared, so the construction of the optimum is visible;
  * a cross-check against the exhaustive reference and the greedy first-fit layout.
Run:  py -3 word_wrap_demo.py
"""
import csv
import os
import sys
from collections import Counter

import word_wrap_dp as ww

HERE = os.path.dirname(os.path.abspath(__file__))
WIDTH = 21


def write_csv(name, rows):
    """Save the raw numbers behind a report table in results/ (no console output)."""
    with open(os.path.join(HERE, "results", name), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_words():
    with open(os.path.join(HERE, "test_data", "layout_text.txt"), encoding="utf-8") as f:
        return ww.tokenize(f.read())


def print_layout(lines, width, title):
    print(title)
    print(f"  {'line':>4}  {'text (| = right margin at W = ' + str(width) + ')':<{width + 3}} {'words':>5} "
          f"{'unused s':>8} {'penalty':>8}")
    for k, line in enumerate(lines, 1):
        text = " ".join(line.words)
        note = "  (final line: no penalty)" if k == len(lines) else ""
        print(f"  {k:>4}  {text:<{width}} | {len(line.words):>5} {line.unused:>8} {line.penalty:>8}{note}")
    print(f"  {'':>4}  {'':<{width}}   {'':>5} {'TOTAL':>8} {sum(line.penalty for line in lines):>8}")


def print_states(words, states):
    print("\nTASK 1.2 - DP STATES (filled from the last word backwards)")
    print("  best[i]  = minimum penalty to lay out the suffix words[i..n-1];  best[n] = 0")
    print("  next[i]  = j: the first line of that suffix holds words i..j-1 (s = its unused spaces)")
    print("  candidates j:total with total = s^2 (0 if j = n, final line) + best[j];  * marks the minimum kept")
    print(f"  {'i':>2} {'word[i]':<14} {'best[i]':>7} {'next[i]':>7} {'s':>3} {'s^2':>4} {'+best[j]':>8}   "
          f"all feasible candidates j:total")
    for st in states:
        kept = next(c for c in st.candidates if c.j == st.next_break)
        cands = " ".join(f"{c.j}:{c.total}{'*' if c.j == st.next_break else ''}" for c in st.candidates)
        print(f"  {st.i:>2} {words[st.i]:<14} {st.best:>7} {st.next_break:>7} {kept.unused:>3} {kept.line_cost:>4} "
              f"{kept.suffix_cost:>8}   {cands}")


def main():
    words = load_words()
    print("TASK 1 - WORD WRAP DP (document-layout engine)")
    print("=" * 112)
    print(f"Input: {len(words)} words from test_data/layout_text.txt, maximum line width W = {WIDTH}")
    print(f"       word lengths: {[len(w) for w in words]}")
    print("Expected behaviour: every line <= W, words in order, penalty = sum of s^2 over non-final lines,")
    print("                    result equal to the exhaustive optimum over all 2^(n-1) break patterns.\n")
    ops = Counter()
    total, lines, states = ww.word_wrap_dp(words, WIDTH, ops, record_states=True)
    print_layout(lines, WIDTH, f"TASK 1.1 - OPTIMAL LAYOUT (minimum total penalty = {total})")
    print_states(words, states)
    write_csv("t1_layout_w21.csv", [dict(line=k, words=" ".join(l.words), word_count=len(l.words), unused=l.unused,
                                         penalty=l.penalty) for k, l in enumerate(lines, 1)])
    write_csv("t1_dp_states_w21.csv", [dict(i=st.i, word=words[st.i], best=st.best, next_break=st.next_break,
                                            candidates=" ".join(f"{c.j}:{c.total}" for c in st.candidates))
                                       for st in states])
    reference = ww.exhaustive_min_penalty(words, WIDTH)
    g_total, g_lines = ww.greedy_first_fit(words, WIDTH)
    print(f"\nDP work: {ops['states']} states, {ops['candidates']} feasible candidate lines examined "
          f"(exhaustive reference examined 2^{len(words) - 1} = {2 ** (len(words) - 1):,} break patterns)")
    print(f"Check:   DP minimum = {total}, exhaustive minimum = {reference} -> "
          f"{'MATCH' if total == reference else 'MISMATCH'}")
    print(f"Greedy first-fit (fill every line) for comparison: penalty {g_total}, line ends after words "
          f"{ww.layout_signature(g_lines)}")
    print(f"DP optimum line ends after words {ww.layout_signature(lines)}")
    return 0 if total == reference else 1


if __name__ == "__main__":
    sys.exit(main())
