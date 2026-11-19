"""
Task 1.3 + 1.4 - requirement change (three new line widths) and boundary testing of the word-wrap DP.

1.3  For W = 18, 26 and 30 the program FIRST prints the prediction recorded in
     test_data/width_change_predictions.json (written before this program was ever run), THEN runs the DP and
     compares the new layout with the W = 21 baseline: does the arrangement change, which line changes first,
     does the total penalty increase or decrease - and checks each prediction.
1.4  The selected boundary case (a word of exactly W characters, test_data/boundary_cases.json) is run through
     the real DP and through a deliberately defective variant (fit test 'unused > 0' instead of 'unused >= 0')
     to show that the case exposes that off-by-one defect; further boundary / invalid inputs follow.
Run:  py -3 word_wrap_width_change.py
"""
import csv
import json
import os
import re
import sys
import textwrap

import word_wrap_dp as ww

HERE = os.path.dirname(os.path.abspath(__file__))


def write_csv(name, rows):
    """Save the raw numbers behind a report table in results/ (no console output)."""
    with open(os.path.join(HERE, "results", name), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_json(name):
    with open(os.path.join(HERE, "test_data", name), encoding="utf-8") as f:
        return json.load(f)


def load_words():
    with open(os.path.join(HERE, "test_data", "layout_text.txt"), encoding="utf-8") as f:
        return ww.tokenize(f.read())


def line_texts(lines):
    return [" ".join(line.words) for line in lines]


def first_changed_line(old, new):
    """1-based number of the first line whose content differs (None if the layouts are identical)."""
    for k, (a, b) in enumerate(zip(old, new), 1):
        if a != b:
            return k
    return None if len(old) == len(new) else min(len(old), len(new)) + 1


def defective_dp_min_penalty(words, width):
    """DELIBERATELY WRONG copy of the DP used only for 1.4: a line 'fits' only if unused > 0 (off-by-one)."""
    n, lengths = len(words), [len(w) for w in words]
    best = [ww.INF] * (n + 1)
    best[n] = 0
    for i in range(n - 1, -1, -1):
        used = -1
        for j in range(i + 1, n + 1):
            used += lengths[j - 1] + 1
            unused = width - used
            if unused <= 0:                        # BUG: rejects a line that is exactly full
                break
            best[i] = min(best[i], (0 if j == n else unused * unused) + best[j])
    return best[0]


def requirement_change(words, base_width, predictions):
    _, base_lines, _ = ww.word_wrap_dp(words, base_width)
    base_text, base_total = line_texts(base_lines), sum(line.penalty for line in base_lines)
    print(f"Baseline W = {base_width}: {len(base_lines)} lines, total penalty {base_total}, line ends after words "
          f"{ww.layout_signature(base_lines)}")
    verdicts, layout_rows = [], []
    for case in predictions["cases"]:
        width = case["width"]
        print("\n" + "-" * 112)
        print(f"MODIFIED CASE W = {width}")
        print("  PREDICTION (recorded before execution):")
        for key in ("arrangement_changes", "first_change", "penalty"):
            print(textwrap.fill(case[key], 110, initial_indent=f"    {key:<20} ", subsequent_indent=" " * 25))
        total, lines, _ = ww.word_wrap_dp(words, width)
        new_text = line_texts(lines)
        print(f"  ACTUAL RESULT: {len(lines)} lines, total penalty {total}")
        rows = max(len(base_text), len(new_text))
        print(f"    {'line':>4}  {'W = ' + str(base_width) + ' (baseline)':<{base_width + 2}} {'s':>3}   "
              f"{'W = ' + str(width):<{width + 2}} {'s':>3} {'s^2':>4}")
        for k in range(rows):
            a = base_text[k] if k < len(base_text) else ""
            sa = str(base_lines[k].unused) if k < len(base_lines) else ""
            b = new_text[k] if k < len(new_text) else ""
            sb = str(lines[k].unused) if k < len(lines) else ""
            pb = str(lines[k].penalty) if k < len(lines) else ""
            mark = "  <- first change" if k + 1 == first_changed_line(base_text, new_text) else ""
            print(f"    {k + 1:>4}  {a:<{base_width + 2}} {sa:>3}   {b:<{width + 2}} {sb:>3} {pb:>4}{mark}")
        layout_rows += [dict(width=width, line=k, text=t, unused=lines[k - 1].unused, penalty=lines[k - 1].penalty)
                 for k, t in enumerate(new_text, 1)]
        write_csv("t1_width_change_layouts.csv", layout_rows)
        changed = new_text != base_text
        first = first_changed_line(base_text, new_text)
        direction = "INCREASE" if total > base_total else "DECREASE" if total < base_total else "UNCHANGED"
        predicted_line = int(re.search(r"line (\d+)", case["first_change"]).group(1))
        checks = [("arrangement changes", case["arrangement_changes"].startswith("YES") == changed,
                   "YES" if changed else "NO"),
                  ("first change", predicted_line == first, f"line {first}"),
                  ("penalty", case["penalty"].startswith(direction), f"{direction} ({base_total} -> {total})")]
        print("  COMPARISON WITH PREDICTION:")
        for name, ok, actual in checks:
            print(f"    {name:<20} actual {actual:<26} prediction {'CONFIRMED' if ok else 'NOT CONFIRMED'}")
            verdicts.append(ok)
    print(f"\nPredictions confirmed: {sum(verdicts)}/{len(verdicts)}")


def boundary_tests(spec):
    sel = spec["selected_boundary"]
    words, width = ww.tokenize(sel["text"]), sel["width"]
    print("\n" + "=" * 112)
    print(f"TASK 1.4 - SELECTED BOUNDARY CASE: {sel['text']!r} with W = {width}")
    print(textwrap.fill(sel["why"], 110, initial_indent="  Why: ", subsequent_indent="       "))
    total, lines, _ = ww.word_wrap_dp(words, width)
    for k, line in enumerate(lines, 1):
        print(f"    line {k}: {' '.join(line.words):<{width}} | s = {line.unused:>2}, penalty {line.penalty}")
    print(f"  Correct DP: total penalty {total} (exhaustive reference {ww.exhaustive_min_penalty(words, width)})")
    wrong = defective_dp_min_penalty(words, width)
    print(f"  Defective variant (fit test 'unused > 0'): {'no layout found (inf)' if wrong == ww.INF else wrong}"
          f"  -> the boundary case EXPOSES the off-by-one defect")
    print("\n  Further boundary / invalid inputs:")
    for case in spec["extra"]:
        try:
            total, lines, _ = ww.word_wrap_dp(ww.tokenize(case["text"]), case["width"])
            outcome = f"penalty {total}, {len(lines)} line(s) {line_texts(lines)}"
        except ValueError as exc:                          # LayoutError is a ValueError
            outcome = f"rejected: {type(exc).__name__}: {exc}"
        print(f"    {case['name']:<50} W={case['width']:<3} {outcome[:56]}")


def main():
    predictions = load_json("width_change_predictions.json")
    print("TASK 1.3 - REQUIREMENT CHANGE: SAME TEXT, THREE NEW LINE WIDTHS (prediction printed first)")
    print("=" * 112)
    requirement_change(load_words(), predictions["base_width"], predictions)
    boundary_tests(load_json("boundary_cases.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
