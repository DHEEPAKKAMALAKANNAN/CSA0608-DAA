"""
test_word_break.py - checks the corrected WordBreak (Task 4) against an independent recursive reference
and confirms the faulty version's defect.  Prints PASS/FAIL lines and a RESULT line.
"""
import random

from word_break import reference, word_break_corrected, word_break_faulty


def main():
    random.seed(42)
    passed = total = 0

    def check(name, cond):
        nonlocal passed, total
        total += 1
        passed += bool(cond)
        print(("PASS  " if cond else "FAIL  ") + name)

    d = {"cat", "dog"}
    check("failing input 'catsdog': faulty returns TRUE (wrong)", word_break_faulty("catsdog", d)[-1] is True)
    check("failing input 'catsdog': corrected returns FALSE = reference",
          word_break_corrected("catsdog", d)[-1] is False and reference("catsdog", frozenset(d)) is False)
    check("regression 'catdog': faulty and corrected both TRUE",
          word_break_faulty("catdog", d)[-1] and word_break_corrected("catdog", d)[-1])
    check("regression 'dogcatx': faulty and corrected both FALSE",
          not word_break_faulty("dogcatx", d)[-1] and not word_break_corrected("dogcatx", d)[-1])
    check("empty text -> TRUE (DP[0] base case)", word_break_corrected("", d)[-1] is True)
    check("overlapping words 'catsanddog' with {cat,cats,and,sand,dog} -> TRUE",
          word_break_corrected("catsanddog", {"cat", "cats", "and", "sand", "dog"})[-1])
    check("'catsandog' with {cat,cats,and,sand,dog} -> FALSE (faulty says TRUE)",
          not word_break_corrected("catsandog", {"cat", "cats", "and", "sand", "dog"})[-1]
          and word_break_faulty("catsandog", {"cat", "cats", "and", "sand", "dog"})[-1])
    bad_c = differ = 0
    for _ in range(2000):
        words = {"".join(random.choice("ab") for _ in range(random.randint(1, 3)))
                 for _ in range(random.randint(1, 4))}
        text = "".join(random.choice("ab") for _ in range(random.randint(0, 10)))
        ref = reference(text, frozenset(words))
        if word_break_corrected(text, words)[-1] != ref:
            bad_c += 1
        if word_break_faulty(text, words)[-1] != ref:
            differ += 1
    check("2000 random texts over {a,b}: corrected DP[n] = recursive reference in every case", bad_c == 0)
    check(f"same 2000 texts: faulty version is wrong on {differ} of them (defect is real)", differ > 0)
    bad_prefix = 0
    for _ in range(300):
        words = {"".join(random.choice("ab") for _ in range(random.randint(1, 3))) for _ in range(3)}
        text = "".join(random.choice("ab") for _ in range(8))
        dp = word_break_corrected(text, words)
        if any(dp[i] != reference(text[:i], frozenset(words)) for i in range(len(text) + 1)):
            bad_prefix += 1
    check("300 random texts: EVERY corrected state DP[i] equals reference(prefix of length i)", bad_prefix == 0)
    print(f"RESULT: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
