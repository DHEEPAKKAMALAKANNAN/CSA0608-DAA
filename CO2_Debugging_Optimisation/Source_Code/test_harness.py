"""
Test harness for the SentinelOps SOC alert-triage module (original, corrected and optimised versions).

* DEFECT_TESTS  - one or more test cases per seeded defect D1..D14.  Each is built so that it fails on
                  the original program because of that defect and passes once the defect is fixed.
* GENERAL_TESTS - edge cases and randomised cross-checks against independent reference answers
                  (sorted() with a key, list scan with ==, str.startswith, math.dist over all pairs).
* EXTRA_TESTS   - checks for the additional routines of the optimised module only.

Usage:  py -3 test_harness.py [original|corrected|optimised ...]      (default: all three)
Prints PASS/FAIL per test and "RESULT: k/n tests passed" per module.  When all three modules are run it
also writes ../Report/tables/defect_tests.csv (inputs, expected and actual outputs for the report).
Exit code 0 when the corrected and optimised modules pass every test (the original is EXPECTED to fail).
"""
import csv
import importlib
import itertools
import math
import os
import random
import sys

from alert_data import SIGNATURES, build, log_text, make_alert_rows, make_same_x_rows

MODULES = {"original": "original_alert_triage", "corrected": "corrected_alert_triage",
           "optimised": "optimised_alert_triage"}
HERE = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------------ helpers and reference answers
def alerts(mod, specs):
    """Alerts from (severity, timestamp, x, y) specs; ids ALR-000001, ALR-000002 ... built at run time."""
    return [mod.Alert(f"ALR-{k + 1:06d}", sev, t, "10.0.0.1", "test alert", x, y)
            for k, (sev, t, x, y) in enumerate(specs)]


def ids(seq):
    """Short id list for messages: ALR-000003 -> '003'."""
    return [a.alert_id[-3:] for a in seq]


def ref_sort(seq):
    return sorted(seq, key=lambda a: (-a.severity, a.timestamp))          # Python's sort is stable


def ref_find(seq, alert_id):
    return next((i for i, a in enumerate(seq) if a.alert_id == alert_id), -1)


def ref_match(text, pattern):
    if not pattern:
        return []
    return [i for i in range(len(text) - len(pattern) + 1) if text.startswith(pattern, i)]


def ref_closest(seq):
    if len(seq) < 2:
        return (math.inf, -1, -1)
    return min((math.dist((seq[i].x, seq[i].y), (seq[j].x, seq[j].y)), i, j)
               for i, j in itertools.combinations(range(len(seq)), 2))


def fmt_pair(res):
    d, i, j = res
    return f"({d:.4f}, {i}, {j})" if d != math.inf else f"(inf, {i}, {j})"


def same_pair(got, exp):
    """Closest-pair results agree: same indices and (numerically) the same distance."""
    return (tuple(got[1:]) == tuple(exp[1:]) and
            (got[0] == exp[0] or math.isclose(got[0], exp[0], rel_tol=1e-9, abs_tol=1e-12)))


def runtime_id(number):
    """An id string built at run time (equal to, but NOT the same object as, the stored id)."""
    return "-".join(["ALR", f"{number:06d}"])


# ------------------------------------------------------------------ test cases: one function per test
# each returns (passed, expected, actual) as short strings
def t01(mod):
    batch = alerts(mod, [(2, 10, 0, 0), (5, 20, 0, 0), (3, 30, 0, 0)])
    mod.sort_alerts(batch)
    return ids(batch) == ["001", "002", "003"], "input 001 002 003", "input " + " ".join(ids(batch))


def t02(mod):
    got = [a.severity for a in mod.sort_alerts(alerts(mod, [(3, 10, 0, 0), (2, 20, 0, 0), (5, 30, 0, 0)]))]
    return got == [5, 3, 2], "sev [5, 3, 2]", f"sev {got}"


def t03(mod):
    got = [a.timestamp for a in mod.sort_alerts(alerts(mod, [(4, 20, 0, 0), (4, 10, 0, 0), (4, 30, 0, 0)]))]
    return got == [10, 20, 30], "t [10, 20, 30]", f"t {got}"


def t04(mod):
    keys = [(5, 1), (4, 3), (5, 2), (4, 4), (3, 5), (3, 6), (2, 7), (2, 8), (1, 9), (1, 10)]
    batch = alerts(mod, [(s, t, 0, 0) for s, t in keys])
    mod.reset_counters()
    mod.sort_alerts(batch)
    c = mod.COUNTERS["sort_comparisons"]
    return c <= 17, "<= 2n-3 = 17 comparisons", f"{c} comparisons"


def t05(mod):
    batch = alerts(mod, [(1, 1, 0, 0), (2, 2, 0, 0), (3, 3, 0, 0)])
    got = mod.find_alert(batch, batch[0].alert_id)            # the stored object itself -> D6 cannot interfere
    return got == 0, "index 0", f"index {got}"


def t06(mod):
    batch = alerts(mod, [(1, 1, 0, 0), (2, 2, 0, 0), (3, 3, 0, 0)])
    got = mod.find_alert(batch, runtime_id(1))                # equal text, different string object
    return got == 0, "index 0", f"index {got}"


def t07(mod):
    batch = alerts(mod, [(1, 1, 0, 0), (2, 2, 0, 0), (3, 3, 0, 0)])
    got = mod.find_alert(batch, batch[2].alert_id)
    return got == 2, "index 2", f"index {got}"


def t07b(mod):
    got = mod.find_alert([], runtime_id(1))
    return got == -1, "-1", repr(got)


def t08(mod):
    got = mod.match_signature("User svc_backup read /etc/shadow", "/etc/shadow")
    return got == [21], "[21]", str(got)


def t08b(mod):
    got = mod.match_signature("mimikatz", "mimikatz")
    return got == [0], "[0]", str(got)


def t09(mod):
    mod.reset_counters()
    got = mod.match_signature("x" * 20, "abc")
    c = mod.COUNTERS["char_comparisons"]
    return got == [] and c <= 18, "[] in <= n-m+1 = 18 char cmp", f"{got} in {c} char cmp"


def t10(mod):
    got = mod.match_signature("Failed password for admin", "")
    shown = str(got) if len(got) < 4 else f"[{got[0]}, {got[1]}, ..., {got[-1]}] ({len(got)} hits)"
    return got == [], "[]", shown


def t11(mod):
    got = mod.closest_alert_pair([])
    return tuple(got) == (math.inf, -1, -1), "(inf, -1, -1)", fmt_pair(got)


def t12(mod):
    batch = alerts(mod, [(1, 1, 0.20, 0.50), (1, 2, 0.23, 0.50)])
    got, exp = mod.closest_alert_pair(batch), ref_closest(batch)
    return same_pair(got, exp), fmt_pair(exp), fmt_pair(got)


def t12b(mod):
    got = mod.closest_alert_pair(alerts(mod, [(1, 1, 0.20, 0.50)]))
    return tuple(got) == (math.inf, -1, -1), "(inf, -1, -1)", fmt_pair(got)


def t12c(mod):
    rng = random.Random(7)
    batch = alerts(mod, [(1, k, rng.random(), rng.random()) for k in range(10)])
    mod.reset_counters()
    mod.closest_alert_pair(batch)                             # efficiency only; results are checked elsewhere
    c = mod.COUNTERS["distance_computations"]
    return c <= 45, "<= n(n-1)/2 = 45 distances", f"{c} distances"


def t13(mod):
    batch = alerts(mod, [(1, 1, 0.10, 0.10), (1, 2, 0.12, 0.90), (1, 3, 0.30, 0.12)])
    got, exp = mod.closest_alert_pair(batch), ref_closest(batch)
    return same_pair(got, exp), fmt_pair(exp), fmt_pair(got)


def t14(mod):
    batch = alerts(mod, [(1, 1, 0.10, 0.10), (1, 2, 0.11, 0.10), (1, 3, 0.80, 0.80)])
    got, exp = mod.closest_alert_pair(batch), ref_closest(batch)
    return same_pair(got, exp), fmt_pair(exp), fmt_pair(got)


# ---- general tests
def g01(mod):
    batch = build(mod, make_alert_rows(300, seed=1))
    got, exp = mod.sort_alerts(batch), ref_sort(batch)
    wrong = sum(a.alert_id != b.alert_id for a, b in zip(got, exp))
    return wrong == 0, "== sorted(key)", f"{wrong}/300 positions differ"


def g02(mod):
    one = alerts(mod, [(3, 1, 0, 0)])
    ok = mod.sort_alerts([]) == [] and ids(mod.sort_alerts(one)) == ["001"]
    return ok, "[] and [001]", "ok" if ok else "wrong"


def g03(mod):
    batch = ref_sort(build(mod, make_alert_rows(200, seed=2)))
    before = [a.alert_id for a in batch]                       # snapshot: the call may alias/mutate batch
    ok = [a.alert_id for a in mod.sort_alerts(batch)] == before
    return ok, "order unchanged", "unchanged" if ok else "changed"


def g04(mod):
    batch = alerts(mod, [(1, 1, 0, 0), (2, 2, 0, 0), (3, 3, 0, 0), (4, 4, 0, 0)])
    batch[3].alert_id = runtime_id(2)                          # the same alert re-fired later
    got = mod.find_alert(batch, runtime_id(2))
    return got == 1, "index 1 (first)", f"index {got}"


def g05(mod):
    got = mod.find_alert(alerts(mod, [(1, 1, 0, 0), (2, 2, 0, 0), (3, 3, 0, 0)]), runtime_id(999))
    return got == -1, "-1", repr(got)


def g06(mod):
    batch = build(mod, make_alert_rows(300, seed=3))
    rng = random.Random(3)
    queries = [runtime_id(rng.randint(1, 360)) for _ in range(200)]     # ~1/6 of them are absent
    bad = sum(mod.find_alert(batch, q) != ref_find(batch, q) for q in queries)
    return bad == 0, "200/200 agree", f"{200 - bad}/200 agree"


def g07(mod):
    got = mod.match_signature("aaaa", "aa")
    return got == [0, 1, 2], "[0, 1, 2]", str(got)


def g08(mod):
    got = mod.match_signature("mimi", "mimikatz")
    return got == [], "[]", str(got)


def g09(mod):
    text = log_text(make_alert_rows(300, seed=4))
    bad = [s for s in SIGNATURES if mod.match_signature(text, s) != ref_match(text, s)]
    return not bad, "5/5 signatures agree", f"{5 - len(bad)}/5 agree"


def g10(mod):
    got = mod.match_signature("Process MIMIKATZ.EXE started", "mimikatz")
    return got == [], "[] (case-sensitive)", str(got)


def g11(mod):
    batch = build(mod, make_alert_rows(300, seed=5))
    got, exp = mod.closest_alert_pair(batch), ref_closest(batch)
    return same_pair(got, exp), fmt_pair(exp), fmt_pair(got)


def g12(mod):
    batch = alerts(mod, [(1, 1, 0.3, 0.4), (1, 2, 0.7, 0.1), (1, 3, 0.3, 0.4), (1, 4, 0.9, 0.9)])
    got = mod.closest_alert_pair(batch)
    ok = got[0] == 0.0 and got[1] < got[2] and {got[1], got[2]} == {0, 2}
    return ok, "(0.0000, 0, 2)", fmt_pair(got)


def g13(mod):
    batch = alerts(mod, [(3, 5, 0, 0), (3, 5, 0, 0), (5, 9, 0, 0), (3, 5, 0, 0)])   # equal keys
    got = ids(mod.sort_alerts(batch))
    return got == ["003", "001", "002", "004"], "003 001 002 004 (stable)", " ".join(got)


# ---- extra tests for the optimised module only
def o01(mod):
    batch = build(mod, make_alert_rows(300, seed=6))
    batch[250].alert_id = batch[20].alert_id                   # a duplicate id: first occurrence wins
    index, rng = mod.AlertIndex(batch), random.Random(6)
    queries = [runtime_id(rng.randint(1, 360)) for _ in range(200)] + [batch[20].alert_id]
    bad = sum(index.find(q) != ref_find(batch, q) for q in queries)
    return bad == 0, "201/201 agree", f"{201 - bad}/201 agree"


def o02(mod):
    batch = build(mod, make_alert_rows(50, seed=7))
    before = list(batch)
    mod.find_alert(batch, runtime_id(999))
    mod.find_alert(batch, runtime_id(17))
    ok = len(batch) == 50 and all(a is b for a, b in zip(batch, before))
    return ok, "list restored (50 items)", f"{len(batch)} items" + ("" if ok else ", changed")


def o03(mod):
    text = log_text(make_alert_rows(300, seed=8))
    cases = [(text, s) for s in SIGNATURES] + [("aaaa", "aa"), ("a" * 200, "a" * 9 + "b"),
                                               ("abababab", "abab"), ("x", ""), ("ab", "abc")]
    bad = sum(mod.match_signature_kmp(t, p) != ref_match(t, p) for t, p in cases)
    return bad == 0, "10/10 agree", f"{10 - bad}/10 agree"


def o04(mod):
    a = build(mod, make_alert_rows(300, seed=9))
    b = build(mod, make_same_x_rows(300, seed=9))
    ok = all(same_pair(mod.closest_alert_pair_sweep(s), ref_closest(s)) for s in (a, b))
    return ok, "random + same-x agree", "agree" if ok else "differ"


def o05(mod):
    cases = [("a" * 200, "a" * 9 + "b"), ("a" * 200, "b" + "a" * 9), ("a" * 50, "aaa")]
    bad = sum(mod.match_signature(t, p) != ref_match(t, p) for t, p in cases)
    return bad == 0, "3/3 agree", f"{3 - bad}/3 agree"


def o06(mod):
    batch = build(mod, make_same_x_rows(300, seed=10))
    ok = same_pair(mod.closest_alert_pair(batch), ref_closest(batch))
    return ok, "same-x batch agrees", "agree" if ok else "differ"


# (test id, defect, short description, input shown in the report, function)
DEFECT_TESTS = [
    ("T01", "D1", "sort leaves the caller's list in arrival order", "sev [2,5,3], t [10,20,30]", t01),
    ("T02", "D2", "sort: critical alert arriving last goes first", "sev [3,2,5], t [10,20,30]", t02),
    ("T03", "D3", "sort: equal severity -> oldest first", "sev [4,4,4], t [20,10,30]", t03),
    ("T04", "D4", "sort: early exit on a nearly sorted queue", "10 sorted alerts, items 2-3 swapped", t04),
    ("T05", "D5", "search finds the alert at index 0", "3 alerts, query = id of alert 0", t05),
    ("T06", "D6", "search with an equal but new id string", "3 alerts, query built at run time", t06),
    ("T07", "D7", "search continues past the first mismatch", "3 alerts, query = id of alert 2", t07),
    ("T07b", "D7", "search in an empty batch returns -1", "[] , 'ALR-000001'", t07b),
    ("T08", "D8", "signature at the very end of the message", "'User svc_backup read /etc/shadow'", t08),
    ("T08b", "D8", "message equal to the signature", "text = pattern = 'mimikatz'", t08b),
    ("T09", "D9", "early exit on mismatch (char comparisons)", "text 'x'*20, pattern 'abc'", t09),
    ("T10", "D10", "empty signature matches nothing", "'Failed password for admin', ''", t10),
    ("T11", "D11", "closest pair of an empty batch", "[]", t11),
    ("T12", "D12", "two alerts -> the pair (0, 1)", "(0.20,0.50), (0.23,0.50)", t12),
    ("T12b", "D12", "single alert -> no pair", "(0.20,0.50)", t12b),
    ("T12c", "D12", "n = 10 needs at most n(n-1)/2 distances", "10 random points (seed 7)", t12c),
    ("T13", "D13", "y difference is part of the distance", "(.10,.10), (.12,.90), (.30,.12)", t13),
    ("T14", "D14", "both pair indices updated together", "(.10,.10), (.11,.10), (.80,.80)", t14),
]
GENERAL_TESTS = [
    ("G01", "-", "sort 300 random alerts == reference", "make_alert_rows(300, seed=1)", g01),
    ("G02", "-", "sort an empty and a one-alert batch", "[], [ALR-000001]", g02),
    ("G03", "-", "sort an already triaged queue: unchanged", "200 alerts in priority order", g03),
    ("G04", "-", "search returns the FIRST duplicate", "ids 001 002 003 002, query 002", g04),
    ("G05", "-", "search for an absent id returns -1", "3 alerts, 'ALR-000999'", g05),
    ("G06", "-", "200 random look-ups == reference", "300 alerts, 200 queries (seed 3)", g06),
    ("G07", "-", "overlapping matches are all reported", "'aaaa', 'aa'", g07),
    ("G08", "-", "signature longer than the message", "'mimi', 'mimikatz'", g08),
    ("G09", "-", "5 signatures on a 300-alert log == ref", "log of 300 alerts (seed 4)", g09),
    ("G10", "-", "matching is case-sensitive", "'... MIMIKATZ.EXE ...', 'mimikatz'", g10),
    ("G11", "-", "closest pair of 300 alerts == reference", "make_alert_rows(300, seed=5)", g11),
    ("G12", "-", "exact duplicate alerts -> distance 0", "4 points, #0 and #2 identical", g12),
    ("G13", "-", "sort is stable for identical keys", "keys (3,5) (3,5) (5,9) (3,5)", g13),
]
EXTRA_TESTS = [
    ("O01", "-", "AlertIndex look-ups == reference", "300 alerts + duplicate id", o01),
    ("O02", "-", "sentinel search restores the caller's list", "50 alerts, hit + miss", o02),
    ("O03", "-", "KMP matcher == reference (10 cases)", "logs, overlaps, adversarial", o03),
    ("O04", "-", "x-sweep closest pair == reference", "random + same-x, 300 alerts", o04),
    ("O05", "-", "Horspool on adversarial texts", "'a'*200 with 'a'*9+'b' etc.", o05),
    ("O06", "-", "divide & conquer on a same-x batch", "300 alerts, all x = 0.5", o06),
]


def run_test(mod, test):
    """Run one test; an exception counts as a failure and is reported as the actual output."""
    try:
        return test[4](mod)
    except Exception as exc:                                     # noqa: BLE001 - report any crash
        return False, "-", f"{type(exc).__name__}: {exc}"[:40]


def tests_for(name):
    return DEFECT_TESTS + GENERAL_TESTS + (EXTRA_TESTS if name == "optimised" else [])


def run_module(name, quiet=False):
    """Run every applicable test on one module; return {test id: (passed, expected, actual)}."""
    mod = importlib.import_module(MODULES[name])
    results = {}
    if not quiet:
        print(f"=== {MODULES[name]}.py " + "=" * (80 - len(MODULES[name])))
    for test in tests_for(name):
        ok, exp, got = run_test(mod, test)
        results[test[0]] = (ok, exp, got)
        if not quiet:
            detail = "" if ok else f"  | expected {exp} | got {got}"
            print(f"{'PASS' if ok else 'FAIL'} {test[0]:<4} {test[1]:<3} {test[2]}{detail}"[:125])
    passed = sum(r[0] for r in results.values())
    if not quiet:
        print(f"RESULT: {passed}/{len(results)} tests passed ({MODULES[name]})\n")
    return results


def write_csv(all_results):
    """Defect-test table for the report: input, expected, actual output of every version."""
    path = os.path.join(HERE, "..", "Report", "tables", "defect_tests.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["test", "defect", "description", "input", "expected", "actual_original",
                    "original", "corrected", "optimised"])
        for tid, defect, desc, inp, _ in DEFECT_TESTS + GENERAL_TESTS + EXTRA_TESTS:
            row = [tid, defect, desc, inp]
            ref = all_results.get("corrected", {}).get(tid) or all_results["optimised"][tid]
            orig = all_results["original"].get(tid)
            row += [ref[1], orig[2] if orig else "n/a"]
            row += ["PASS" if all_results[m].get(tid, (None,))[0] else
                    ("n/a" if tid not in all_results[m] else "FAIL") for m in MODULES]
            w.writerow(row)
    return os.path.normpath(path)


def main():
    names = sys.argv[1:] or list(MODULES)
    all_results = {name: run_module(name) for name in names}
    print("SUMMARY")
    for name, res in all_results.items():
        note = "  <- defects reproduced (expected)" if name == "original" else ""
        print(f"  {MODULES[name]:<24} {sum(r[0] for r in res.values()):>2}/{len(res)} passed{note}")
    if set(all_results) == set(MODULES):
        print("  defect table written to", os.path.relpath(write_csv(all_results), HERE))
    good = all(all(r[0] for r in all_results[m].values()) for m in all_results if m != "original")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
