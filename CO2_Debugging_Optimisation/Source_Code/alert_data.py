"""
Deterministic SOC alert datasets for the SentinelOps alert-triage debugging/optimisation task.

All three versions of the module (original, corrected, optimised) define their own Alert class with
the same constructor, so datasets are produced as plain tuples
    (alert_id, severity, timestamp, source_ip, message, x, y)
and turned into objects with build(module, rows).  Every generator is seeded, so a run is repeatable.

Run this file to (re)write the CSV test datasets into ../Supporting_Files/test_datasets/.
"""
import csv
import os
import random

SHIFT_START = 8 / 24                     # shifts start at 08:00 -> y = time of day as a fraction of 24 h
SIGNATURES = ["Failed password", "mimikatz", "/etc/shadow", "powershell -enc", "cmd.exe /c whoami"]
BATCH_SIZES = [100, 500, 1000, 2000, 5000]
HEADER = ["alert_id", "severity", "timestamp", "source_ip", "message", "x_risk", "y_time"]
SEVERITY_WEIGHTS = {1: 30, 2: 25, 3: 25, 4: 15, 5: 5}          # % of alerts per severity level

TEMPLATES = [
    "Failed password for {user} from {ip} port {port} ssh2",
    "Accepted publickey for {user} from {ip} port {port} ssh2",
    "Outbound DNS query volume above baseline for host {host}",
    "Process mimikatz.exe accessed lsass memory on {host}",
    "powershell -enc {b64} spawned by winword.exe on {host}",
    "User {user} read /etc/shadow on {host}",
    "TLS certificate for {host} expires in {num} days",
    "Port scan detected from {ip}: {num} ports in 60 s",
    "Firewall denied {ip} -> 10.0.0.5:{port} (policy DMZ-IN)",
    "Antivirus quarantined Trojan.GenericKD.{num} on {host}",
    "Multiple 404 responses for /wp-login.php from {ip}",
    "New local administrator {user} created on {host}",
    "cmd.exe /c whoami executed by {user} on {host}",
    "Impossible travel: {user} signed in from two countries within {num} min",
]
USERS = ["admin", "root", "svc_backup", "j.smith", "a.kumar", "guest", "deploy", "oracle"]
B64 = "JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBt"


def _message(rng):
    """One realistic SIEM alert message."""
    return rng.choice(TEMPLATES).format(
        user=rng.choice(USERS), ip=f"10.{rng.randint(0, 9)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}",
        port=rng.randint(1024, 65535), host=f"WS-{rng.randint(1, 9999):04d}", num=rng.randint(2, 999),
        b64=B64[:rng.randint(16, len(B64))])


def make_alert_rows(n, seed=42, dup_rate=0.05):
    """n alerts in arrival (timestamp) order; ~dup_rate of them are re-fired near-duplicates."""
    rng = random.Random(seed)
    levels, weights = list(SEVERITY_WEIGHTS), list(SEVERITY_WEIGHTS.values())
    rows, t = [], 0
    for k in range(n):
        t += rng.randint(0, 20)                       # gap 0 gives equal timestamps (tie-break test)
        alert_id = f"ALR-{k + 1:06d}"
        y = round(SHIFT_START + t / 86400, 6)
        if rows and rng.random() < dup_rate:          # the same detection fires again
            _, sev, _, ip, msg, x, _ = rng.choice(rows[-50:])
            x = round(min(1.0, max(0.0, x + rng.uniform(-0.002, 0.002))), 6)
        else:
            sev = rng.choices(levels, weights)[0]
            ip = f"10.{rng.randint(0, 9)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
            msg = _message(rng)
            x = round(min(1.0, (sev - 1) / 5 + rng.uniform(0.0, 0.2)), 6)   # risk grows with severity
        rows.append((alert_id, sev, t, ip, msg, x, y))
    return rows


def make_nearly_sorted_rows(n, seed=42, fresh_rate=0.01):
    """An already triaged queue (priority order) with ~1 % fresh alerts appended at the end."""
    rows = make_alert_rows(n, seed)
    fresh = max(1, int(n * fresh_rate))
    queue = sorted(rows[:n - fresh], key=lambda r: (-r[1], r[2]))
    return queue + rows[n - fresh:]


def make_same_x_rows(n, seed=42):
    """Adversarial batch for the x-sweep: a mis-configured enrichment gives every alert risk x = 0.5;
    y uses sub-second arrival times, so all points are distinct and the closest pair is unique."""
    rng = random.Random(seed + 1)
    return [r[:5] + (0.5, SHIFT_START + (r[2] + rng.random()) / 86400) for r in make_alert_rows(n, seed)]


def log_text(rows):
    """The shift's log: all alert messages joined, one per line (text for signature scanning)."""
    return "\n".join(r[4] for r in rows)


def build(module, rows):
    """Turn tuples into module.Alert objects (each version has its own Alert class)."""
    return [module.Alert(*r) for r in rows]


def write_csv(rows, path):
    """Write alert tuples to a CSV file with a header row."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(HEADER)
        writer.writerows(rows)


def main():
    """Write every dataset used by the harness and the experiments as CSV."""
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Supporting_Files", "test_datasets")
    os.makedirs(out, exist_ok=True)
    for n in BATCH_SIZES:
        write_csv(make_alert_rows(n), os.path.join(out, f"alerts_random_{n}.csv"))
        write_csv(make_nearly_sorted_rows(n), os.path.join(out, f"alerts_nearly_sorted_{n}.csv"))
    write_csv(make_same_x_rows(1000), os.path.join(out, "alerts_same_x_1000.csv"))
    print("datasets written to", os.path.normpath(out))


if __name__ == "__main__":
    main()
