"""
SentinelOps SOC Alert-Triage Module - version 1.0 (CORRECTED)
=============================================================
The Security Operations Centre (SOC) receives a stream of alerts from the SIEM.  Before an
analyst picks up a shift's batch of alerts, this module runs four brute-force triage steps:

  1. sort_alerts(alerts)            -> NEW list ordered by severity (5 = critical first), ties
                                       by timestamp (oldest first); the input list is not changed
  2. find_alert(alerts, alert_id)   -> index of the first alert with that id, or -1 if absent
  3. match_signature(text, pattern) -> list of ALL start positions of a threat signature in a
                                       message (case-sensitive, overlapping matches included);
                                       an empty signature is invalid and matches nothing
  4. closest_alert_pair(alerts)     -> (distance, i, j) with i < j: the two alerts whose feature
                                       points (x = risk score, y = time of day) are nearest, used to
                                       correlate near-duplicate alerts; (inf, -1, -1) if n < 2

Every function updates COUNTERS so the SOC dashboard can show how much work each step costs.
CORRECTED version: the original program debugged with 14 minimal line-level fixes, each marked
'# FIX Dn' (n = defect number in the report).  The structure and algorithms are unchanged.
"""
import math

# operation counters shown on the SOC performance dashboard
COUNTERS = {"sort_comparisons": 0, "sort_swaps": 0, "search_comparisons": 0,
            "char_comparisons": 0, "distance_computations": 0}


def reset_counters():
    """Set every operation counter back to zero."""
    for key in COUNTERS:
        COUNTERS[key] = 0


class Alert:
    """One SOC alert produced by the SIEM correlation layer."""

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


# ------------------------------------------------------------------ 1. sorting (bubble sort)
def _comes_before(a, b):
    """True if alert a must be triaged before alert b."""
    if a.severity != b.severity:
        return a.severity > b.severity            # higher severity first
    return a.timestamp < b.timestamp              # FIX D3: '<' puts the older alert first


def sort_alerts(alerts):
    """Return the alerts ordered by severity (desc) then timestamp (asc) using bubble sort."""
    ordered = list(alerts)                        # FIX D1: sort a copy, not the caller's list
    n = len(ordered)
    for i in range(n - 1):
        swapped = False                           # FIX D4: reset the flag at every pass
        for j in range(n - i - 1):                # FIX D2: bound was n-i-2 (last pair skipped)
            COUNTERS["sort_comparisons"] += 1
            if _comes_before(ordered[j + 1], ordered[j]):
                ordered[j], ordered[j + 1] = ordered[j + 1], ordered[j]
                COUNTERS["sort_swaps"] += 1
                swapped = True
        if not swapped:                           # a pass without swaps -> already sorted
            break
    return ordered


# ------------------------------------------------------------------ 2. sequential search
def find_alert(alerts, alert_id):
    """Return the index of the first alert whose id equals alert_id, or -1 if there is none."""
    for i in range(len(alerts)):                  # FIX D5: start at index 0, not 1
        COUNTERS["search_comparisons"] += 1
        if alerts[i].alert_id == alert_id:        # FIX D6: compare values (==), not identity
            return i
    return -1                                     # FIX D7: 'absent' only after the full scan


# ------------------------------------------------------------------ 3. brute-force string matching
def match_signature(text, pattern):
    """Return every position where pattern occurs in text (brute force, overlaps included)."""
    n = len(text)
    m = len(pattern)
    if m == 0 or m > n:                           # FIX D10: an empty signature matches nothing
        return []
    positions = []
    for i in range(n - m + 1):                    # FIX D8: include the last alignment n-m
        matched = True
        for j in range(m):
            COUNTERS["char_comparisons"] += 1
            if text[i + j] != pattern[j]:
                matched = False
                break                             # FIX D9: stop at the first mismatch
        if matched:
            positions.append(i)
    return positions


# ------------------------------------------------------------------ 4. brute-force closest pair
def closest_alert_pair(alerts):
    """Return (distance, i, j), i < j, for the two alerts whose feature points are closest."""
    n = len(alerts)
    best, best_i, best_j = math.inf, -1, -1       # FIX D11: start with 'no pair found'
    for i in range(n):
        for j in range(i + 1, n):                 # FIX D12: pairs i < j only (no self-pair)
            COUNTERS["distance_computations"] += 1
            dx = alerts[i].x - alerts[j].x
            dy = alerts[i].y - alerts[j].y        # FIX D13: index typo, was alerts[i].y twice
            d = math.sqrt(dx ** 2 + dy ** 2)
            if d < best:
                best = d
                best_i = i
                best_j = j                        # FIX D14: update both indices together
    return best, best_i, best_j


# ------------------------------------------------------------------ triage demo
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
    """Run the four triage steps on the demo shift and print the analyst's view."""
    reset_counters()
    shift = demo_alerts()
    print("SentinelOps SOC alert triage - demo shift of", len(shift), "alerts")
    print("=" * 78)
    print("1) Triage queue (severity high -> low, oldest first)")
    queue = sort_alerts(shift)
    for pos, a in enumerate(queue, 1):
        print(f"   {pos:>2}. {a.alert_id}  sev {a.severity}  t={a.timestamp:>3}s  {a.message[:46]}")
    print("   arrival order after sorting:", " ".join(a.alert_id[-3:] for a in shift))
    print("2) Analyst look-ups (position in the arrival list)")
    for query in ["ALR-000101", "ALR-000110", "ALR-000999"]:
        print(f"   {query} -> index {find_alert(shift, query)}")
    print("3) Signature scan of alert messages (rules.txt)")
    for sig in RULES.split("\n"):
        hits = [f"{a.alert_id[-3:]}@{p}" for a in shift for p in match_signature(a.message, sig)]
        more = f" ... (+{len(hits) - 4} more)" if len(hits) > 4 else ""
        print(f"   {repr(sig):<18} {len(hits):>3} hit(s): {' '.join(hits[:4])}{more}")
    print("4) Near-duplicate correlation (closest pair of feature points)")
    d, i, j = closest_alert_pair(shift)
    print(f"   {shift[i].alert_id} <-> {shift[j].alert_id}   distance {d:.4f}")
    print("5) Work done:", ", ".join(f"{k}={v}" for k, v in COUNTERS.items()))


if __name__ == "__main__":
    main()
