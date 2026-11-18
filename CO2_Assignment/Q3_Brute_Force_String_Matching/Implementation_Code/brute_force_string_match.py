"""Q3 - Brute-force string matching for cybersecurity log screening.

Problem
    A security operations centre searches large system logs for known event signatures (character patterns).
    The screener must report EVERY occurrence, so the brute-force matcher tries all n-m+1 alignments of the
    pattern under the text and compares characters left to right until the first mismatch.

    Basic operation counted: one character comparison text[s+j] vs pattern[j] (successful or not).

This program
    1. runs correctness tests (PASS/FAIL lines + RESULT),
    2. executes the three designed test conditions (same n = 100 000 and m = 38), printing the PREDICTION
       before each test is executed and the OBSERVED count after it,
    3. saves results/q3_conditions.csv and the datasets (log text, patterns) in results/datasets/.
"""

import csv
import os
import random
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
N_TEXT = 100_000
SIG_IOC = "#IOC:RANSOMWARE-SHADOWCOPY-DELETE-0x7F"      # C1: '#' never occurs in the logs
SIG_ADMIN = "Failed password for invalid user admin"     # C3: shares a 20-33 char prefix with benign lines
M = len(SIG_IOC)


def brute_force_match(text, pattern, profile=None):
    """Return (list of all match positions, number of character comparisons).

    For every shift s = 0 .. n-m compare pattern[0..m-1] with text[s..s+m-1] left to right, stopping at the
    first mismatch.  An empty pattern or a pattern longer than the text gives no alignments (0 comparisons).
    If a Counter is passed as `profile`, profile[k] counts the shifts that cost exactly k comparisons."""
    n, m = len(text), len(pattern)
    matches, comparisons = [], 0
    if m == 0 or m > n:
        return matches, comparisons
    for s in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[s + j] != pattern[j]:
                break
            j += 1
        if j == m:
            matches.append(s)
        if profile is not None:
            profile[min(j + 1, m)] += 1          # work done at this shift
    return matches, comparisons


def profile_summary(profile, m):
    """Group the per-shift work into bands: 1 comparison, 2-9, 10-19, 20-m-1, m (full length)."""
    bands = [("1", 1, 1), ("2-9", 2, 9), ("10-19", 10, 19), (f"20-{m - 1}", 20, m - 1), (f"{m}", m, m)]
    return {label: sum(c for k, c in profile.items() if lo <= k <= hi) for label, lo, hi in bands}


def make_auth_log(n_chars, seed=42):
    """Synthetic but realistic SSH/auth log (exactly n_chars characters, contains no '#')."""
    rng = random.Random(seed)
    users = ["test", "oracle", "guest", "ubuntu", "pi", "support", "postgres", "admin"]
    lines, size, sec = [], 0, 0
    while size < n_chars:
        sec += rng.randint(0, 3)
        stamp = f"Nov 19 {7 + sec // 3600 % 12:02d}:{sec // 60 % 60:02d}:{sec % 60:02d} gw01"
        ip = f"{rng.choice((203, 198, 192, 45))}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
        pid, port, r = rng.randint(1000, 9999), rng.randint(1024, 65535), rng.random()
        if r < 0.25:
            msg = f"sshd[{pid}]: Failed password for root from {ip} port {port} ssh2"
        elif r < 0.45:
            user = users[-1] if rng.random() < 0.03 else rng.choice(users[:-1])   # 'admin' is rare: real hits
            msg = f"sshd[{pid}]: Failed password for invalid user {user} from {ip} port {port} ssh2"
        elif r < 0.60:
            msg = f"sshd[{pid}]: Accepted publickey for deploy from {ip} port {port} ssh2"
        elif r < 0.75:
            msg = f"CRON[{pid}]: pam_unix(cron:session): session opened for user root(uid=0) by (uid=0)"
        elif r < 0.90:
            msg = f"kernel: [UFW BLOCK] IN=eth0 OUT= SRC={ip} DST=10.0.0.5 PROTO=TCP SPT={port} DPT=23"
        else:
            msg = "sudo:    alice : TTY=pts/0 ; PWD=/home/alice ; USER=root ; COMMAND=/usr/bin/apt update"
        line = f"{stamp} {msg}\n"
        lines.append(line)
        size += len(line)
    return "".join(lines)[:n_chars]


def independence_estimate(text, pattern):
    """Predicted comparisons if text characters were independent with the text's own character frequencies:
    (n-m+1) * sum_{k=0}^{m-1} prod_{i<k} f(pattern[i])."""
    freq = Counter(text)
    n, total, prob = len(text), 0.0, 1.0
    for ch in pattern:
        total += prob
        prob *= freq[ch] / n
    return (n - len(pattern) + 1) * total


def conditions(n=N_TEXT, m=M):
    """The three designed text-pattern pairs, with a prediction function evaluated BEFORE each run."""
    log = make_auth_log(n)
    return [
        ("C1 little work", "auth log", log, SIG_IOC[:m],
         lambda t, p: (len(t) - len(p) + 1, "exactly n-m+1: '#' never occurs, every shift fails at once")),
        ("C2 engineered worst case", "'A' * n", "A" * n, "A" * (m - 1) + "B",
         lambda t, p: (len(p) * (len(t) - len(p) + 1), "exactly m(n-m+1): every shift matches m-1 chars, fails last")),
        ("C3 own: shared prefix", "auth log", log, SIG_ADMIN,
         lambda t, p: (round(independence_estimate(t, p)),
                       "independence model; my own range: 1.0-1.3 x (n-m+1)")),
    ]


# ------------------------------------------------------------------------------------------------- tests
def run_tests():
    def reference(t, p):                                   # independent reference: str.startswith at every shift
        return [i for i in range(len(t) - len(p) + 1) if p and t.startswith(p, i)]

    cases = [
        ("hand example ABCABD/ABD", "ABCABD", "ABD", [3], 8),
        ("overlapping AAAAA/AA", "AAAAA", "AA", [0, 1, 2, 3], 8),
        ("pattern longer than text", "AB", "ABC", [], 0),
        ("empty pattern", "ABC", "", [], 0),
        ("worst case m(n-m+1)", "A" * 20, "AAAB", [], 4 * 17),
        ("best case n-m+1", "B" * 20, "AXYZ", [], 17),
        ("match at end only", "xxxxxxxxxxSIG", "SIG", [10], 13),
        ("signature in a log line", "sshd: Failed password for invalid user admin from 1.2.3.4", SIG_ADMIN, [6], None),
    ]
    print("CORRECTNESS TESTS  (expected matches: str.startswith reference; comparisons: counted by hand)")
    passed = 0
    for name, t, p, exp_matches, exp_comp in cases:
        got, comp = brute_force_match(t, p)
        ok = got == exp_matches == reference(t, p) and (exp_comp is None or comp == exp_comp)
        passed += ok
        mt = f"matches {got} " + ("= expected" if got == exp_matches else f"!= expected {exp_matches}")
        ct = f"comparisons {comp}" + ("" if exp_comp is None else
                                      " = expected" if comp == exp_comp else f" != expected {exp_comp}")
        print(f"{'PASS' if ok else 'FAIL'}  Q3 {name:<24} {mt:<34} {ct}")
    rng = random.Random(3)
    rand_ok = True
    for _ in range(200):                                    # random small-alphabet texts: many partial matches
        t = "".join(rng.choice("ab") for _ in range(rng.randint(0, 60)))
        p = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        rand_ok &= brute_force_match(t, p)[0] == reference(t, p)
    passed += rand_ok
    print(f"{'PASS' if rand_ok else 'FAIL'}  Q3 200 random binary texts/patterns: matches equal the reference")
    total = len(cases) + 1
    print(f"RESULT: {passed}/{total} tests passed")
    return passed == total


def run_conditions():
    os.makedirs(os.path.join(RESULTS, "datasets"), exist_ok=True)
    rows = []
    print(f"\nDESIGNED TEST CONDITIONS  (n = {N_TEXT:,} characters, m = {M} for all three; n-m+1 = {N_TEXT - M + 1:,}"
          f" shifts; m(n-m+1) = {M * (N_TEXT - M + 1):,})")
    for name, text_kind, text, pattern, predict in conditions():
        pred, reason = predict(text, pattern)
        print(f"\n[{name}]  text = {text_kind}, pattern = '{pattern}'")
        print(f"  PREDICTION (before running): {pred:>10,} comparisons - {reason}")
        t0 = time.perf_counter()
        matches, comp = brute_force_match(text, pattern)
        ms = (time.perf_counter() - t0) * 1000
        shifts = len(text) - len(pattern) + 1
        print(f"  OBSERVED                   : {comp:>10,} comparisons = {comp / shifts:.3f} per shift,"
              f" {len(matches)} match(es), {ms:.1f} ms;  observed/predicted = {comp / pred:.3f}")
        prof = Counter()
        brute_force_match(text, pattern, prof)            # second (untimed) run that records work per shift
        bands = profile_summary(prof, len(pattern))
        extra = sum((k - 1) * c for k, c in prof.items() if k >= 20)
        print("  shifts by cost (comparisons: #shifts)  " + "  ".join(f"{b}: {c:,}" for b, c in bands.items())
              + (f" | cost>=20 adds {extra:,}" if extra and pattern != "A" * (M - 1) + "B"
                 else ""))
        rows.append({"condition": name, "text": text_kind, "pattern": pattern, "n": len(text), "m": len(pattern),
                     "shifts": shifts, "predicted": pred, "observed": comp, "per_shift": round(comp / shifts, 4),
                     "observed_over_predicted": round(comp / pred, 4), "matches": len(matches),
                     "first_match": matches[0] if matches else -1, "time_ms": round(ms, 2),
                     **{f"shifts_cost_{b}": c for b, c in bands.items()}})
    with open(os.path.join(RESULTS, "q3_conditions.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(RESULTS, "datasets", "q3_auth_log_100k.txt"), "w", newline="\n") as fh:
        fh.write(make_auth_log(N_TEXT))
    with open(os.path.join(RESULTS, "datasets", "q3_patterns.txt"), "w") as fh:
        fh.write(f"C1\t{SIG_IOC}\nC2\t{'A' * (M - 1) + 'B'}\t(text: 'A' * {N_TEXT})\nC3\t{SIG_ADMIN}\n")

    c1, c2, c3 = (r["observed"] for r in rows)
    print(f"\nSUMMARY  same n and m:  C2 needs {c2 / c1:.1f}x the work of C1;  C3 needs {c3 / c1:.3f}x the work of C1")
    print("CSV  : results/q3_conditions.csv   datasets: results/datasets/q3_auth_log_100k.txt, q3_patterns.txt")


def main():
    ok = run_tests()
    run_conditions()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
