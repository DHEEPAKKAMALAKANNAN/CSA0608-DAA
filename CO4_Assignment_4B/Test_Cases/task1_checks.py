"""Checker for Task 1 (word wrap DP): run_case(case) -> (expected, actual, ok)."""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Source_Code", "Task_1"))
import word_wrap_dp as ww  # noqa: E402

TEXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Source_Code", "Task_1", "test_data",
                    "layout_text.txt")


def file_words():
    with open(TEXT, encoding="utf-8") as f:
        return ww.tokenize(f.read())


def run_case(case):
    ex, kind = case["expect"], case["type"]
    if kind == "error":
        try:
            ww.word_wrap_dp(ww.tokenize(case["text"]), case["width"])
            return ex["error"], "no error", False
        except ValueError as exc:
            return ex["error"], type(exc).__name__, type(exc).__name__ == ex["error"]
    if kind in ("file", "text"):
        words = file_words() if kind == "file" else ww.tokenize(case["text"])
        total, lines, _ = ww.word_wrap_dp(words, case["width"])
        ok = total == ex["penalty"] and len(lines) == ex["lines"] and total == ww.exhaustive_min_penalty(words, case["width"])
        return ex, f"penalty {total}, {len(lines)} lines", ok
    if kind == "report":
        words, width = file_words(), case["width"]
        total, lines, _ = ww.word_wrap_dp(words, width)
        flat = [w for line in lines for w in line.words]
        ok = flat == words and all(len(" ".join(l.words)) + l.unused == width and l.unused >= 0 for l in lines)
        ok &= lines[-1].penalty == 0 and sum(l.penalty for l in lines) == total
        ok &= all(l.penalty == l.unused ** 2 for l in lines[:-1])
        return ex, f"valid layout, total {total}", ok
    if kind == "greedy_gap":
        words = file_words()
        dp, _, _ = ww.word_wrap_dp(words, case["width"])
        greedy, _ = ww.greedy_first_fit(words, case["width"])
        return ex, f"DP {dp}, greedy {greedy}", dp == ex["dp"] and greedy == ex["greedy"]
    if kind == "random_vs_exhaustive":
        rng, bad = random.Random(case["seed"]), 0
        for _ in range(case["trials"]):
            words = ["x" * rng.randint(1, 8) for _ in range(rng.randint(1, case["n_max"]))]
            width = rng.randint(8, 20)
            bad += ww.word_wrap_dp(words, width)[0] != ww.exhaustive_min_penalty(words, width)
        return ex, f"{case['trials'] - bad}/{case['trials']} equal", bad == 0
    raise ValueError(kind)
