"""
word_break.py - Task 4 (CO4 Assignment 4A): pseudocode forensics on WordBreak.

DP[i] should mean "the prefix Text[1..i] (first i characters) can be completely segmented into dictionary
words".  substring(Text, j, i) is the piece made of characters j+1 .. i (Python: text[j:i]).
  * word_break_faulty    - the given pseudocode: sets DP[i] TRUE as soon as ANY dictionary word ends at i.
  * word_break_corrected - the minimal repair: the word must also START at a segmentable prefix (DP[j]).
The program prints both DP arrays for the failing input (Task 4.2) and the regression input (Task 4.4)
and marks the first state where the faulty algorithm deviates.  The traces were done by hand first.
"""
import csv
import os
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))


def word_break_faulty(text, dictionary, witness=None):
    n = len(text)
    DP = [False] * (n + 1)
    DP[0] = True
    for i in range(1, n + 1):
        DP[i] = False
        for j in range(0, i):
            if text[j:i] in dictionary:                    # DEFECT: DP[j] is never consulted
                DP[i] = True
                if witness is not None:
                    witness[i] = j
                break
    return DP


def word_break_corrected(text, dictionary, witness=None):
    n = len(text)
    DP = [False] * (n + 1)
    DP[0] = True
    for i in range(1, n + 1):
        DP[i] = False
        for j in range(0, i):
            if DP[j] and text[j:i] in dictionary:          # REPAIR: prefix 1..j segmentable AND word j+1..i
                DP[i] = True
                if witness is not None:
                    witness[i] = j
                break
    return DP


def reference(text, dictionary):
    """Independent recursive check: can text[k:] be segmented?  (memoised top-down search)"""
    @lru_cache(maxsize=None)
    def ok(k):
        return k == len(text) or any(text[k:e] in dictionary and ok(e) for e in range(k + 1, len(text) + 1))
    return ok(0)


def show(title, text, dictionary):
    wf, wc = {}, {}
    f = word_break_faulty(text, dictionary, wf)
    c = word_break_corrected(text, dictionary, wc)
    print(f"{title}:  Text = \"{text}\" (n = {len(text)})   Dictionary = {sorted(dictionary)}")
    print(f"  {'i':>2} | {'prefix':<9} | {'faulty DP[i]':<12} {'(because)':<24} | {'corrected DP[i]':<15} "
          f"{'(because)':<24} | note")
    print("  " + "-" * 106)
    first = None
    for i in range(len(text) + 1):
        why_f = "base case" if i == 0 else (f"\"{text[wf[i]:i]}\" in Dict (j={wf[i]})" if f[i] else "no word ends here")
        why_c = "base case" if i == 0 else (f"DP[{wc[i]}] and \"{text[wc[i]:i]}\" (j={wc[i]})" if c[i]
                                             else "no valid split j")
        note = ""
        if f[i] != c[i] and first is None:
            first, note = i, "<-- FIRST WRONG"
        print(f"  {i:>2} | {text[:i] or '(empty)':<9} | {str(f[i]):<12} {why_f:<24} | {str(c[i]):<15} "
              f"{why_c:<24} | {note}")
    print(f"  returned: faulty DP[n] = {f[-1]}, corrected DP[n] = {c[-1]}, "
          f"independent reference = {reference(text, frozenset(dictionary))}\n")
    return f, c, first


def main():
    print("=" * 114)
    print("TASK 4 - WordBreak forensics: faulty vs minimally corrected pseudocode (verification of the manual trace)")
    print("=" * 114)
    with open(os.path.join(HERE, "word_break_cases.csv"), newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            show(row["case"], row["text"], set(row["dictionary"].split()))


if __name__ == "__main__":
    main()
