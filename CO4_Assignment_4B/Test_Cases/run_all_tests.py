"""
CO4 Assignment 4B (Part II - Algorithm Engineering) - reproducible test harness for all six tasks.

For every task N it loads the catalogue  taskN_test_cases.json  (normal, student-designed counter-example,
boundary, failure / invalid-input, reference-validation and requirement-change cases) and the checker module
taskN_checks.py  (which imports the implementation from ../Source_Code/Task_N and compares the actual result
with the expected one, usually against an independent reference such as brute force).
Prints one PASS/FAIL line per case, a per-task summary and finally  RESULT: k/k tests passed.
Writes test_results.csv (task, id, category, description, expected, actual, status) next to this file.
Run:  py -3 run_all_tests.py
"""
import csv
import importlib
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CATEGORY = {"N": "normal", "S": "student", "B": "boundary", "F": "failure", "V": "validate", "R": "change"}


def short(x, width):
    s = str(x).replace("\n", " ")
    return s if len(s) <= width else s[:width - 3] + "..."


def run_task(task_no, rows):
    """Run every case of one task; returns (passed, total)."""
    with open(os.path.join(HERE, f"task{task_no}_test_cases.json"), encoding="utf-8") as f:
        catalogue = json.load(f)
    checks = importlib.import_module(f"task{task_no}_checks")
    print(f"\nTask {task_no} - {catalogue['task']}")
    passed = 0
    for case in catalogue["cases"]:
        category = CATEGORY.get(case["id"].split("-")[1][0], "other")
        try:
            expected, actual, ok = checks.run_case(case)
        except Exception as exc:                                    # noqa: BLE001 - a crash is a FAIL
            expected, actual, ok = case.get("expect", "?"), f"CRASH {type(exc).__name__}: {exc}", False
            traceback.print_exc()
        status = "PASS" if ok else "FAIL"
        passed += ok
        rows.append(dict(task=task_no, id=case["id"], category=category, description=case["description"],
                         expected=str(expected), actual=str(actual), status=status))
        print(f"{status}  {case['id']:<7} {category:<9} {short(case['description'], 58):<58} -> "
              f"{short(actual, 38)}")
    print(f"      Task {task_no}: {passed}/{len(catalogue['cases'])} passed")
    return passed, len(catalogue["cases"])


def main():
    print("CO4 ASSIGNMENT 4B - TEST HARNESS (all six tasks)")
    print("=" * 118)
    start, rows, total_pass, total = time.perf_counter(), [], 0, 0
    for task_no in range(1, 7):
        p, t = run_task(task_no, rows)
        total_pass, total = total_pass + p, total + t
    with open(os.path.join(HERE, "test_results.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("=" * 118)
    print(f"elapsed {time.perf_counter() - start:.1f} s;  details in test_results.csv")
    print(f"RESULT: {total_pass}/{total} tests passed")
    return 0 if total_pass == total else 1


if __name__ == "__main__":
    sys.exit(main())
