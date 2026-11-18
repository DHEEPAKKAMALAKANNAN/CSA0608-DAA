"""
SentinelOps SOC Alert-Triage Module - version 2.0 (OPTIMISED)
=============================================================
Same interface and the same results as corrected_alert_triage.py (verified by test_harness.py and
experiments.py), but with faster algorithms and fewer basic operations:

  sort_alerts          stable top-down merge sort on precomputed priority keys; a merge is skipped when
                       the two halves are already in order          O(n log n) worst, n - 1 comparisons
                                                                      on an already triaged queue
  find_alert           sentinel sequential search: no bounds test inside the loop      O(n), 1 test/item
  AlertIndex           hash index alert_id -> first position for repeated look-ups:
                       O(n) to build once, O(1) expected per look-up
  match_signature      Boyer-Moore-Horspool: right-to-left window check + bad-character shift table,
                       about n/m .. n character comparisons on log text, O(nm) worst case
  match_signature_kmp  Knuth-Morris-Pratt alternative with a guaranteed O(n + m) worst case
  closest_alert_pair   divide and conquer on x-sorted points with a y-sorted strip and squared
                       distances (one sqrt at the very end)                       O(n log n) worst case
  closest_alert_pair_sweep  sort by x and stop as soon as the x-gap alone is >= the best distance
                       (very few distances on real data, O(n^2) worst case when all x are equal)

Counters are accumulated in local variables and added to COUNTERS once per call (cheaper than a
dictionary update inside the inner loops).
"""
import math

COUNTERS = {"sort_comparisons": 0, "sort_moves": 0, "search_comparisons": 0, "index_inserts": 0,
            "char_comparisons": 0, "distance_computations": 0}


def reset_counters():
    """Set every operation counter back to zero."""
    for key in COUNTERS:
        COUNTERS[key] = 0


class Alert:
    """One SOC alert (same fields as before; __slots__ makes attribute access faster and smaller)."""
    __slots__ = ("alert_id", "severity", "timestamp", "source_ip", "message", "x", "y")

    def __init__(self, alert_id, severity, timestamp, source_ip, message, x, y):
        self.alert_id = alert_id      # e.g. "ALR-000123"
        self.severity = severity      # 1 = informational ... 5 = critical
        self.timestamp = timestamp    # seconds since the start of the shift
        self.source_ip = source_ip
        self.message = message
        self.x = x                    # feature 1: normalised risk score (0..1)
        self.y = y                    # feature 2: time of day as a fraction of 24 h (0..1)

    def __repr__(self):
        return f"{self.alert_id}(sev={self.severity}, t={self.timestamp})"


# ------------------------------------------------------------------ 1. sorting: adaptive merge sort
def sort_alerts(alerts):
    """Return a NEW list ordered by severity (desc) then timestamp (asc); stable merge sort."""
    items = [((-a.severity, a.timestamp), a) for a in alerts]   # decorate once: one key per alert
    if len(items) > 1:
        _merge_sort(items, [None] * len(items), 0, len(items))
    return [a for _, a in items]


def _merge_sort(items, aux, lo, hi):
    """Sort items[lo:hi] (pairs (key, alert)) in place; aux is scratch space for the left half."""
    if hi - lo < 2:
        return
    mid = (lo + hi) // 2
    _merge_sort(items, aux, lo, mid)
    _merge_sort(items, aux, mid, hi)
    COUNTERS["sort_comparisons"] += 1
    if items[mid - 1][0] <= items[mid][0]:      # halves already in order -> nothing to merge
        return
    aux[lo:mid] = items[lo:mid]                 # copy only the left half
    i, j, k, comparisons = lo, mid, lo, 0
    while i < mid and j < hi:
        comparisons += 1
        if items[j][0] < aux[i][0]:             # strict '<': equal keys keep the earlier alert (stable)
            items[k] = items[j]
            j += 1
        else:
            items[k] = aux[i]
            i += 1
        k += 1
    items[k:k + mid - i] = aux[i:mid]           # left leftovers; right leftovers are already in place
    COUNTERS["sort_comparisons"] += comparisons
    COUNTERS["sort_moves"] += (k - lo) + (mid - i)


# ------------------------------------------------------------------ 2. searching
class _Probe:
    """Sentinel record appended after the last alert so the search loop needs no bounds test."""
    __slots__ = ("alert_id",)

    def __init__(self, alert_id):
        self.alert_id = alert_id


def find_alert(alerts, alert_id):
    """Sentinel sequential search: index of the first alert with this id, or -1.
    The caller's list is restored (sentinel removed) before returning, even on an exception."""
    n = len(alerts)
    alerts.append(_Probe(alert_id))             # the loop is now guaranteed to stop
    try:
        i = 0
        while alerts[i].alert_id != alert_id:   # ONE comparison per element, no 'i < n' test
            i += 1
    finally:
        alerts.pop()
    COUNTERS["search_comparisons"] += i + 1
    return i if i < n else -1


class AlertIndex:
    """Hash index alert_id -> position of its FIRST occurrence, for many look-ups on one batch."""

    def __init__(self, alerts):
        self._pos = {}
        for i, a in enumerate(alerts):
            self._pos.setdefault(a.alert_id, i)  # keep the first occurrence (same as sequential search)
        COUNTERS["index_inserts"] += len(alerts)

    def find(self, alert_id):
        """Index of the first alert with this id, or -1: one hash probe."""
        COUNTERS["search_comparisons"] += 1
        return self._pos.get(alert_id, -1)


# ------------------------------------------------------------------ 3. string matching
def _shift_table(pattern):
    """Horspool bad-character table: distance from the last occurrence of ch (in pattern[:-1]) to the end."""
    m = len(pattern)
    return {ch: m - 1 - k for k, ch in enumerate(pattern[:-1])}


def match_signature(text, pattern):
    """All (overlapping) start positions of pattern in text - Boyer-Moore-Horspool."""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:                         # empty or over-long signature: no match
        return []
    shift, last = _shift_table(pattern), m - 1
    positions, comparisons, i = [], 0, 0
    while i <= n - m:
        j = last
        while True:                             # compare the window right to left
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
            if j == 0:
                positions.append(i)
                break
            j -= 1
        i += shift.get(text[i + last], m)       # skip using the window's last character
    COUNTERS["char_comparisons"] += comparisons
    return positions


def match_signature_kmp(text, pattern):
    """All (overlapping) start positions of pattern in text - Knuth-Morris-Pratt, O(n + m)."""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []
    comparisons, fail, k = 0, [0] * m, 0        # fail[q] = longest proper border of pattern[:q + 1]
    for q in range(1, m):
        while True:
            comparisons += 1
            if pattern[q] == pattern[k]:
                k += 1
                break
            if k == 0:
                break
            k = fail[k - 1]
        fail[q] = k
    positions, q = [], 0
    for i in range(n):
        while True:
            comparisons += 1
            if text[i] == pattern[q]:
                q += 1
                break
            if q == 0:
                break
            q = fail[q - 1]
        if q == m:                              # full match ending at i
            positions.append(i - m + 1)
            q = fail[q - 1]
    COUNTERS["char_comparisons"] += comparisons
    return positions


# ------------------------------------------------------------------ 4. closest pair
def _better(best, p, q):
    """Compare the pair (p, q) with the best (d2, i, j) so far; squared distance, ties -> smaller (i, j)."""
    COUNTERS["distance_computations"] += 1
    dx, dy = p[0] - q[0], p[1] - q[1]
    cand = (dx * dx + dy * dy,) + ((p[2], q[2]) if p[2] < q[2] else (q[2], p[2]))
    return cand if cand < best else best


def _closest(px, lo, hi):
    """Closest pair in px[lo:hi] (points (x, y, index) sorted by x) -> ((d2, i, j), points sorted by y)."""
    if hi - lo <= 3:                            # base case: brute force on at most 3 points
        best = (math.inf, -1, -1)
        for a in range(lo, hi):
            for b in range(a + 1, hi):
                best = _better(best, px[a], px[b])
        return best, sorted(px[lo:hi], key=lambda p: p[1])
    mid = (lo + hi) // 2
    x_mid = px[mid][0]
    best_left, left = _closest(px, lo, mid)
    best_right, right = _closest(px, mid, hi)
    best = min(best_left, best_right)
    by_y, a, b = [], 0, 0                       # merge the two y-sorted halves
    while a < len(left) and b < len(right):
        if right[b][1] < left[a][1]:
            by_y.append(right[b])
            b += 1
        else:
            by_y.append(left[a])
            a += 1
    by_y += left[a:] + right[b:]
    strip = [p for p in by_y if (p[0] - x_mid) ** 2 < best[0]]
    for s in range(len(strip)):                 # each strip point meets at most 7 successors
        for t in range(s + 1, len(strip)):
            dy = strip[t][1] - strip[s][1]
            if dy * dy >= best[0]:
                break
            best = _better(best, strip[s], strip[t])
    return best, by_y


def closest_alert_pair(alerts):
    """(distance, i, j), i < j, of the two alerts with the closest feature points; (inf, -1, -1) if n < 2."""
    if len(alerts) < 2:
        return (math.inf, -1, -1)
    px = sorted((a.x, a.y, k) for k, a in enumerate(alerts))       # pre-sort by x once
    (d2, i, j), _ = _closest(px, 0, len(px))
    return (math.sqrt(d2), i, j)


def closest_alert_pair_sweep(alerts):
    """Same result by an x-sorted sweep that stops when the x-gap alone reaches the best distance."""
    n = len(alerts)
    if n < 2:
        return (math.inf, -1, -1)
    px = sorted((a.x, a.y, k) for k, a in enumerate(alerts))
    best, count = (math.inf, -1, -1), 0
    for a in range(n - 1):
        xa, ya, ka = px[a]
        for b in range(a + 1, n):
            xb, yb, kb = px[b]
            dx = xb - xa
            if dx * dx >= best[0]:              # every later point is even further away in x
                break
            count += 1
            dy = yb - ya
            cand = (dx * dx + dy * dy,) + ((ka, kb) if ka < kb else (kb, ka))
            if cand < best:
                best = cand
    COUNTERS["distance_computations"] += count
    return (math.sqrt(best[0]), best[1], best[2])


# ------------------------------------------------------------------ triage demo (same shift as before)
SHIFT_START = 8 / 24                              # the shift starts at 08:00
RULES = "Failed password\nmimikatz\n/etc/shadow\npowershell -enc\n"   # contents of rules.txt
DEMO_SHIFT = [   # (severity, timestamp s, source_ip, message, risk score)
    (3, 105, "10.0.4.17", "Failed password for admin from 10.0.4.17 port 22 ssh2", 0.41),
    (2, 230, "10.0.7.3", "Outbound DNS query volume above baseline for host WS-0233", 0.22),
    (5, 344, "10.0.9.41", "Process mimikatz.exe accessed lsass memory on DC-01", 0.97),
    (4, 402, "172.16.2.8", "powershell -enc JABzAD0ATgBlAHcA spawned by winword.exe", 0.83),
    (3, 518, "10.0.4.17", "Failed password for root from 10.0.4.17 port 22 ssh2", 0.43),
    (4, 640, "10.0.3.25", "User svc_backup read /etc/shadow", 0.79),
    (1, 711, "10.0.8.90", "TLS certificate for intranet portal expires in 14 days", 0.05),
    (3, 799, "10.0.4.17", "Failed password for admin from 10.0.4.17 port 22 ssh2", 0.41),
    (2, 861, "10.0.7.3", "Outbound DNS query volume above baseline for host WS-0233", 0.23),
    (5, 930, "10.0.9.44", "Credential dump: mimikatz sekurlsa::logonpasswords on DC-02", 0.95),
]


def demo_alerts():
    """Build the ten alerts of the demo shift (ids are generated, as the SIEM does)."""
    return [Alert(f"ALR-{101 + k:06d}", sev, t, ip, msg, risk, round(SHIFT_START + t / 86400, 4))
            for k, (sev, t, ip, msg, risk) in enumerate(DEMO_SHIFT)]


def main():
    """Run the four optimised triage steps on the demo shift and print the analyst's view."""
    reset_counters()
    shift = demo_alerts()
    print("SentinelOps SOC alert triage (optimised) - demo shift of", len(shift), "alerts")
    print("=" * 78)
    print("1) Triage queue (severity high -> low, oldest first) - merge sort")
    queue = sort_alerts(shift)
    for pos, a in enumerate(queue, 1):
        print(f"   {pos:>2}. {a.alert_id}  sev {a.severity}  t={a.timestamp:>3}s  {a.message[:46]}")
    print("   arrival order after sorting:", " ".join(a.alert_id[-3:] for a in shift))
    print("2) Analyst look-ups (position in the arrival list) - sentinel search | hash index")
    index = AlertIndex(shift)
    for query in ["ALR-000101", "ALR-000110", "ALR-000999"]:
        print(f"   {query} -> index {find_alert(shift, query)} | AlertIndex: {index.find(query)}")
    print("3) Signature scan of alert messages (rules.txt) - Horspool")
    for sig in RULES.split("\n"):
        hits = [f"{a.alert_id[-3:]}@{p}" for a in shift for p in match_signature(a.message, sig)]
        more = f" ... (+{len(hits) - 4} more)" if len(hits) > 4 else ""
        print(f"   {repr(sig):<18} {len(hits):>3} hit(s): {' '.join(hits[:4])}{more}")
    print("4) Near-duplicate correlation (closest pair of feature points) - divide and conquer")
    d, i, j = closest_alert_pair(shift)
    print(f"   {shift[i].alert_id} <-> {shift[j].alert_id}   distance {d:.4f}")
    work = [f"{k}={v}" for k, v in COUNTERS.items()]
    print("5) Work done:", ", ".join(work[:3]) + ",")
    print("              " + ", ".join(work[3:]))


if __name__ == "__main__":
    main()
