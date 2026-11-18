"""
Systematic debugging session: original_alert_triage.py -> corrected_alert_triage.py.

The original program is NOT rewritten.  This script replays the debugging process on its source text:
  STEP 1  Reproduce - run the defect test cases (test_harness.DEFECT_TESTS) on the untouched original.
  STEP 2  Isolate   - line-by-line traces of the faulty functions (sys.settrace, like stepping in pdb)
                      that show where the observed output diverges from the specification.
  STEP 3  Fix and re-test, ONE defect at a time - each entry of FIXES is a minimal line-level patch;
                      after every patch the module is re-loaded and all tests re-run (before -> after),
                      including a regression check on every test that already passed.
  STEP 4  Verify    - the fully patched source must be identical to corrected_alert_triage.py
                      (code after the module docstring) and the line diff is saved for the report.
"""
import csv
import difflib
import math
import os
import sys
import types

import test_harness as th

HERE = os.path.dirname(os.path.abspath(__file__))
COL = 50                                         # FIX comments start in this column, like the originals


def c(code, comment):
    """Code line with an aligned trailing comment."""
    return f"{code:<{COL}}# {comment}"


# (defect id, function, faulty lines in the original, replacement lines)
FIXES = [
    ("D1", "sort_alerts", ["    ordered = alerts"],
     [c("    ordered = list(alerts)", "FIX D1: sort a copy, not the caller's list")]),
    ("D2", "sort_alerts", ["        for j in range(n - i - 2):"],
     [c("        for j in range(n - i - 1):", "FIX D2: bound was n-i-2 (last pair skipped)")]),
    ("D3", "_comes_before", [c("    return a.timestamp > b.timestamp", "same severity: older alert first")],
     [c("    return a.timestamp < b.timestamp", "FIX D3: '<' puts the older alert first")]),
    ("D4", "sort_alerts", ["    swapped = False", "    for i in range(n - 1):"],
     ["    for i in range(n - 1):", c("        swapped = False", "FIX D4: reset the flag at every pass")]),
    ("D5", "find_alert", ["    for i in range(1, len(alerts)):"],
     [c("    for i in range(len(alerts)):", "FIX D5: start at index 0, not 1")]),
    ("D6", "find_alert", ["        if alerts[i].alert_id is alert_id:"],
     [c("        if alerts[i].alert_id == alert_id:", "FIX D6: compare values (==), not identity")]),
    ("D7", "find_alert", ["            return i", "        else:", "            return -1"],
     ["            return i", c("    return -1", "FIX D7: 'absent' only after the full scan")]),
    ("D8", "match_signature", ["    for i in range(n - m):"],
     [c("    for i in range(n - m + 1):", "FIX D8: include the last alignment n-m")]),
    ("D9", "match_signature", ["                matched = False"],
     ["                matched = False", c("                break", "FIX D9: stop at the first mismatch")]),
    ("D10", "match_signature", [c("    if m > n:", "signature longer than the message")],
     [c("    if m == 0 or m > n:", "FIX D10: an empty signature matches nothing")]),
    ("D11", "closest_alert_pair", ["    best, best_i, best_j = 0.0, 0, 0"],
     [c("    best, best_i, best_j = math.inf, -1, -1", "FIX D11: start with 'no pair found'")]),
    ("D12", "closest_alert_pair", ["        for j in range(n):"],
     [c("        for j in range(i + 1, n):", "FIX D12: pairs i < j only (no self-pair)")]),
    ("D13", "closest_alert_pair", ["            dy = alerts[i].y - alerts[i].y"],
     [c("            dy = alerts[i].y - alerts[j].y", "FIX D13: index typo, was alerts[i].y twice")]),
    ("D14", "closest_alert_pair", ["                best_i = i", "            best_j = j"],
     ["                best_i = i", c("                best_j = j", "FIX D14: update both indices together")]),
]


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return fh.read().split("\n")


def faulty_line(original, old, new):
    """Line number (in the original) of the first faulty line of a patch block."""
    _, start = apply_fix(original, old, old)
    k = next((k for k in range(len(old)) if k >= len(new) or old[k] != new[k]), 0)
    return start + k


def apply_fix(lines, old, new):
    """Replace the unique block `old` by `new` in a list of source lines (minimal line-level patch)."""
    starts = [k for k in range(len(lines)) if lines[k:k + len(old)] == old]
    assert len(starts) == 1, f"patch target not unique/found: {old[0]!r}"
    k = starts[0]
    return lines[:k] + new + lines[k + len(old):], k + 1


def load(lines, name="patched"):
    """Execute source lines as a fresh module object (re-load after every patch)."""
    mod = types.ModuleType(name)
    exec(compile("\n".join(lines), f"{name}.py", "exec"), mod.__dict__)
    return mod


def run_all(mod):
    return {t[0]: th.run_test(mod, t) for t in th.DEFECT_TESTS + th.GENERAL_TESTS}


def trace_call(func, args, watch):
    """Run func(*args) under sys.settrace; return (result, [(line no, {var: value})]) for its own frame."""
    events, code = [], func.__code__

    def local(frame, event, arg):
        if event == "line":
            events.append((frame.f_lineno, {v: frame.f_locals[v] for v in watch if v in frame.f_locals}))
        elif event == "return":
            events.append((frame.f_lineno, {"return": arg}))
        return local

    sys.settrace(lambda frame, event, arg: local if frame.f_code is code else None)
    try:
        result = func(*args)
    finally:
        sys.settrace(None)
    return result, events


def show(v):
    return f"{v:.4f}" if isinstance(v, float) and v != math.inf else repr(v)


def step_isolate(src):
    """Traces that localise each failure to specific lines of the original."""
    mod = load(src, "original")
    L = {d: faulty_line(src, old, new) for d, _, old, new in FIXES}
    print("STEP 2  Isolate the faulty lines with line traces of the original (sys.settrace)")
    # sort_alerts: which adjacent pairs are compared, and the swapped flag at the end of every pass
    batch = th.alerts(mod, [(3, 10, 0, 0), (2, 20, 0, 0), (5, 30, 0, 0)])
    _, ev = trace_call(mod.sort_alerts, (batch,), ["i", "j"])
    pairs = [(e["j"], e["j"] + 1) for ln, e in ev if src[ln - 1].strip().startswith("COUNTERS[")]
    print(f"  sort_alerts(sev [3,2,5]): adjacent pairs compared = {pairs}; pair (1, 2) is never compared"
          f"  -> D2 (line {L['D2']})")
    keys = [(5, 1), (4, 3), (5, 2), (4, 4), (3, 5), (3, 6), (2, 7), (2, 8), (1, 9), (1, 10)]
    _, ev = trace_call(mod.sort_alerts, (th.alerts(mod, [(s, t, 0, 0) for s, t in keys]),), ["i", "swapped"])
    flags = "".join("T" if e["swapped"] else "F" for ln, e in ev if "if not swapped" in src[ln - 1])
    print(f"  sort_alerts(nearly sorted, n=10): 'swapped' at the end of passes 0..{len(flags) - 1} = {flags},"
          f" but only pass 0 swaps  -> D4 (line {L['D4']})")
    older_first = mod._comes_before(*th.alerts(mod, [(4, 10, 0, 0), (4, 20, 0, 0)]))
    print(f"  _comes_before(sev 4 t=10, sev 4 t=20) = {older_first}; the older alert must come first"
          f"  -> D3 (line {L['D3']})")
    # find_alert: executed lines
    batch = th.alerts(mod, [(1, 1, 0, 0), (2, 2, 0, 0), (3, 3, 0, 0)])
    res, ev = trace_call(mod.find_alert, (batch, batch[0].alert_id), ["i"])
    path = " -> ".join(f"L{ln}" + (f"(i={e['i']})" if "i" in e else "") for ln, e in ev if "return" not in e)
    print(f"  find_alert(3 alerts, id of alert 0): {path} -> returns {res}")
    print(f"    i = 0 is never tried (D5, line {L['D5']}); 'return -1' fires after the FIRST mismatch"
          f" (D7, lines {L['D7']}-{L['D7'] + 1})")
    q = th.runtime_id(1)
    print(f"  query '{q}' == stored id: {q == batch[0].alert_id}, 'is' stored id: {q is batch[0].alert_id}"
          f"  -> identity test rejects equal ids (D6, line {L['D6']})")
    print(f"  find_alert([], ...) falls off the end of the function and returns {mod.find_alert([], q)!r}"
          " instead of -1 (D7)")
    # match_signature
    res, ev = trace_call(mod.match_signature, ("mimikatz", "mimikatz"), ["i"])
    body = sum(1 for ln, e in ev if "matched = True" in src[ln - 1])
    print(f"  match_signature('mimikatz', 'mimikatz'): range(n - m) = range(0), loop body ran {body} times"
          f" -> {res}  (D8, line {L['D8']})")
    mod.reset_counters()
    mod.match_signature("x" * 20, "abc")
    print(f"  match_signature('x'*20, 'abc'): {mod.COUNTERS['char_comparisons']} char comparisons = 17 alignments"
          f" x 3: no break after a mismatch (D9, line {L['D9']})")
    res = mod.match_signature("Failed password", "")
    print(f"  match_signature('Failed password', ''): guard 'if m > n' lets m = 0 through -> {len(res)} false"
          f" hits (D10, line {L['D10']})")
    # closest_alert_pair
    batch = th.alerts(mod, [(1, 1, 0.20, 0.50), (1, 2, 0.23, 0.70)])
    res, ev = trace_call(mod.closest_alert_pair, (batch,), ["i", "j", "dy", "d", "best", "best_j"])
    test_line = next(k + 1 for k, line in enumerate(src) if line.strip() == "if d < best:")
    rows = [e for ln, e in ev if ln == test_line]
    print(f"  closest_alert_pair((0.20,0.50), (0.23,0.70)), state at 'if d < best' (line {test_line}):")
    for e in rows:
        print("    " + "  ".join(f"{k}={show(e[k])}" for k in ["i", "j", "dy", "d", "best", "best_j"]))
    print(f"    -> returns {th.fmt_pair(res)} instead of {th.fmt_pair(th.ref_closest(batch))}:"
          f" best starts at 0.0, so 'd < best' is never true (D11, line {L['D11']});")
    print(f"       j starts at 0: self-pairs (d = 0) and every pair twice (D12, line {L['D12']});"
          f" dy is always 0 (D13, line {L['D13']});")
    print(f"       best_j changes on every iteration instead of together with best_i (D14, line {L['D14']})")
    print()


def diff_table(original, corrected):
    """One row per defect: faulty line(s) of the original and the fixed line(s) of the corrected file."""
    rows = []
    for defect, func, old, new in FIXES:
        _, start = apply_fix(original, old, old)
        faulty = [(start + k, line) for k, line in enumerate(old) if line not in new]
        if not faulty:                                    # D9: the defect is a MISSING line after `old`
            faulty = [(start + len(old) - 1, old[-1] + "  (no break)")]
        fixed = [(k + 1, line) for k, line in enumerate(corrected) if f"# FIX {defect}:" in line]
        code = lambda line: line.split("  #")[0].strip()  # without the trailing comment
        if len(faulty) == len(fixed) == 1 and code(faulty[0][1]) == code(fixed[0][1]):   # D4, D14: moved line
            indent = lambda line: len(line) - len(line.lstrip())
            faulty = [(faulty[0][0], f"{code(faulty[0][1])}  [indent {indent(faulty[0][1])}]")]
            fixed = [(fixed[0][0], f"{code(fixed[0][1])}  [indent {indent(fixed[0][1])}]")]
        faulty = [(n, code(c)) for n, c in faulty]
        fixed = [(n, code(c)) for n, c in fixed]
        rows.append([defect, func, "-".join(str(n) for n, _ in faulty[::max(1, len(faulty) - 1)]),
                     " / ".join(c for _, c in faulty), "-".join(str(n) for n, _ in fixed),
                     " / ".join(c for _, c in fixed)])
    return rows


def main():
    original = read("original_alert_triage.py")
    print("SentinelOps alert-triage: systematic debugging session (original -> corrected)")
    print("=" * 96)
    before = run_all(load(original, "original"))
    n_def, n_gen = len(th.DEFECT_TESTS), len(th.GENERAL_TESTS)
    passed = sum(before[t[0]][0] for t in th.DEFECT_TESTS)
    print(f"STEP 1  Reproduce: defect tests on the untouched original -> {passed}/{n_def} pass, general tests "
          f"{sum(before[t[0]][0] for t in th.GENERAL_TESTS)}/{n_gen} pass\n")
    step_isolate(original)

    print("STEP 3  Fix ONE defect at a time, re-load the module and re-run every test")
    print(f"  {'fix':<4} {'line':>4}  {'test':<5} {'before the fix':<34} {'after the fix':<30} result   defect/general")
    src, state, regressions = original, before, []
    for defect, func, old, new in FIXES:
        line_in_original = faulty_line(original, old, new)
        src, _ = apply_fix(src, old, new)
        after = run_all(load(src))
        regressions += [f"{t} after {defect}" for t in after if state[t][0] and not after[t][0]]
        mine = [t for t in th.DEFECT_TESTS if t[1] == defect]
        for k, t in enumerate(mine):
            tally = (f"{sum(after[x[0]][0] for x in th.DEFECT_TESTS):>2}/{n_def}  "
                     f"{sum(after[x[0]][0] for x in th.GENERAL_TESTS):>2}/{n_gen}") if k == 0 else ""
            head = f"{defect:<4} {line_in_original:>4}" if k == 0 else " " * 9
            print(f"  {head}  {t[0]:<5} {state[t[0]][2][:34]:<34} {after[t[0]][2][:30]:<30} "
                  f"{'PASS' if after[t[0]][0] else 'FAIL':<8} {tally}")
        state = after
    print("  regression check after every fix (every test that passed before must still pass):",
          ", ".join(regressions) if regressions else "no regressions", "\n")

    corrected = read("corrected_alert_triage.py")
    body = lambda lines: lines[lines.index("import math"):]           # code after the module docstring
    same = body(src) == body(corrected)
    print("STEP 4  Verify: original + 14 line-level fixes == corrected_alert_triage.py (code after docstring):",
          "IDENTICAL" if same else "DIFFERENT")
    rows = diff_table(original, corrected)
    print(f"  {'fix':<4} {'original line(s)':<46} corrected line(s)")
    for defect, _, ln_o, code_o, ln_c, code_c in rows:
        print(f"  {defect:<4} {ln_o:>5}: {code_o[:39]:<39} {ln_c:>5}: {code_c[:45]}")
    out = os.path.join(HERE, "..", "Report", "tables", "diff_original_vs_corrected.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows([["defect", "function", "original_lines", "original_code", "corrected_lines",
                                   "corrected_code"]] + rows)
    diff = difflib.unified_diff(original, corrected, "original_alert_triage.py", "corrected_alert_triage.py",
                                lineterm="")
    with open(os.path.join(HERE, "..", "Supporting_Files", "execution_logs", "original_vs_corrected.diff"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(diff) + "\n")
    print("  table -> Report/tables/diff_original_vs_corrected.csv, unified diff -> Supporting_Files/execution_logs")
    final = run_all(load(corrected, "corrected"))
    print(f"  corrected module: {sum(r[0] for r in final.values())}/{len(final)} defect + general tests pass")
    print(f"RESULT: {sum(r[0] for r in final.values())}/{len(final)} tests passed")
    return 0 if same and all(r[0] for r in final.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
