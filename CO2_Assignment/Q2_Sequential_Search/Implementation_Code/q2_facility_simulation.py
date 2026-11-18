"""Q2 changed condition - one hangar vs 20 maintenance facilities (peak hour simulation).

The SAME seeded event sequence (issues, returns, "who has tool X?" lookups and an end-of-shift reconciliation)
is applied to
    (a) ListToolStore    - the original unsorted list + Sequential Search (counts key comparisons), and
    (b) IndexedToolStore - a hash map Tool ID -> record kept up to date on every issue/return (counts probes).
Every lookup answer of (a) and (b) is compared, so the redesign is verified on the same workload.

Workload assumptions (stated in the report; scaled x20 for 20 facilities):
    one hangar : 500 active records, peak hour = 600 issues, 600 returns, 1 200 lookups (90 % successful),
                 then an end-of-shift reconciliation of 500 tool IDs (80 % already returned -> unsuccessful).
Writes results/q2_facility_simulation.csv and ../Output_Screenshots/q2_operating_boundary.png.
"""

import csv
import os
import random
import statistics
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from sequential_search import (BAYS, TECHNICIANS, TIMES, IndexedToolStore, ListToolStore,  # noqa: E402
                               make_tool_records)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")
BASE = {"active": 500, "issues": 600, "returns": 600, "lookups": 1200, "reconcile": 500}
SCENARIOS = {"1 hangar": 1, "20 facilities": 20}
L_MAX, U_MAX, RECONCILE_WINDOW_S = 0.050, 0.05, 60.0


def build_events(scale, seed=2026):
    """Return (initial records, list of (operation, payload)) for one peak hour at the given scale."""
    rng = random.Random(seed + scale)
    initial = make_tool_records(BASE["active"] * scale, seed=seed + scale)
    active = [r[0] for r in initial]
    pos = {t: i for i, t in enumerate(active)}           # generator bookkeeping only (not measured)
    issued_this_shift = list(active)
    next_id = 10 * len(active) + 100
    ops = (["issue"] * BASE["issues"] + ["return"] * BASE["returns"] + ["lookup"] * BASE["lookups"]) * scale
    rng.shuffle(ops)
    events = []
    for op in ops:
        if op == "issue":
            tool = f"T-{next_id}"
            next_id += 1
            events.append(("issue", (tool, rng.choice(TECHNICIANS), rng.choice(TIMES), rng.choice(BAYS))))
            pos[tool] = len(active)
            active.append(tool)
            issued_this_shift.append(tool)
        elif op == "return":
            tool = active[rng.randrange(len(active))]
            events.append(("return", tool))
            i = pos.pop(tool)
            last = active.pop()
            if last != tool:
                active[i] = last
                pos[last] = i
        else:
            hit = rng.random() < 0.9
            tool = active[rng.randrange(len(active))] if hit else f"T-{rng.randint(10 ** 7, 10 ** 8)}"
            events.append(("lookup", tool))
    for tool in rng.sample(issued_this_shift, BASE["reconcile"] * scale):
        events.append(("reconcile", tool))                # "is this tool still out?" - mostly returned
    return initial, events


def run_store(store, events):
    """Apply events; return (answers of lookups, seconds per phase, comparisons/probes per phase)."""
    answers, secs, work = [], {"hour": 0.0, "reconcile": 0.0}, {"lookup": 0, "return": 0, "issue": 0, "reconcile": 0}
    counter = "comparisons" if isinstance(store, ListToolStore) else "probes"
    for op, payload in events:
        before = getattr(store, counter)
        t0 = time.perf_counter()
        if op == "issue":
            store.issue(payload)
        elif op == "return":
            store.return_tool(payload)
        else:
            answers.append(store.lookup(payload))
        secs["reconcile" if op == "reconcile" else "hour"] += time.perf_counter() - t0
        work[op] += getattr(store, counter) - before
    return answers, secs, work


def read_tc():
    with open(os.path.join(RESULTS, "q2_timing.csv")) as fh:
        rows = [r for r in csv.DictReader(fh) if int(r["n"]) >= 50_000]
    return statistics.median(float(r["ns_per_comparison"]) for r in rows) * 1e-9


def main():
    t_c = read_tc()
    print(f"Q2 CHANGED CONDITION - same seeded peak-hour workload applied to both stores  (t_c = {t_c * 1e9:.1f} ns"
          " from q2_timing.csv)")
    rows = []
    for name, scale in SCENARIOS.items():
        initial, events = build_events(scale)
        list_store, hash_store = ListToolStore(initial), IndexedToolStore(initial)
        a1, s1, w1 = run_store(list_store, events)
        a2, s2, w2 = run_store(hash_store, events)
        same = a1 == a2
        searches = sum(1 for op, _ in events if op in ("lookup", "return", "reconcile"))
        rows.append({"scenario": name, "active_records": len(initial), "events": len(events), "searches": searches,
                     "seq_comparisons": sum(w1.values()), "seq_lookup": w1["lookup"], "seq_return": w1["return"],
                     "seq_reconcile": w1["reconcile"], "hash_probes": sum(w2.values()),
                     "seq_hour_s": round(s1["hour"], 4), "seq_reconcile_s": round(s1["reconcile"], 4),
                     "hash_hour_s": round(s2["hour"], 4), "hash_reconcile_s": round(s2["reconcile"], 4),
                     "dict_bytes": sys.getsizeof(hash_store.index), "answers_identical": same})
    print(f"\n{'':<34}{'1 hangar':>18}{'20 facilities':>18}{'growth':>10}")
    print("-" * 80)
    a, b = rows

    def line(label, key, fmt="{:,}"):
        ratio = b[key] / a[key] if a[key] else float("nan")
        print(f"{label:<34}{fmt.format(a[key]):>18}{fmt.format(b[key]):>18}{ratio:>9.0f}x")
    line("active records n", "active_records")
    line("events in the peak hour", "events")
    line("searches (lookups+returns+recon.)", "searches")
    line("SEQUENTIAL comparisons - lookups", "seq_lookup")
    line("SEQUENTIAL comparisons - returns", "seq_return")
    line("SEQUENTIAL comparisons - reconcile", "seq_reconcile")
    line("SEQUENTIAL comparisons - total", "seq_comparisons")
    line("HASH INDEX probes - total", "hash_probes")
    line("sequential time, hour traffic (s)", "seq_hour_s", "{:.3f}")
    line("sequential time, reconciliation (s)", "seq_reconcile_s", "{:.3f}")
    line("hash-index time, hour traffic (s)", "hash_hour_s", "{:.4f}")
    line("hash-index time, reconciliation (s)", "hash_reconcile_s", "{:.4f}")
    print(f"{'answers identical (list vs index)':<34}{str(a['answers_identical']):>18}{str(b['answers_identical']):>18}")
    print(f"{'hash index memory (dict, bytes)':<34}{a['dict_bytes']:>18,}{b['dict_bytes']:>18,}")

    print("\nRE-EVALUATION against the operating boundary (latency <= 50 ms, load <= 5 % of one core);"
          f" reconciliation window {RECONCILE_WINDOW_S:.0f} s")
    print(f"  {'scenario':<14}{'worst lookup':>14}{'hour load':>11}{'recon. lookups/s':>18}{'model load':>12}"
          f"{'measured load':>15}  verdict")
    for r in rows:
        n = r["active_records"]
        worst = n * t_c * 1000                                     # ms, unsuccessful search of n records
        lam_burst = BASE["reconcile"] * SCENARIOS[r["scenario"]] / RECONCILE_WINDOW_S
        model_burst = lam_burst * n * t_c                          # boundary model: lambda * n * t_c
        measured_burst = r["seq_reconcile_s"] / RECONCILE_WINDOW_S  # measured CPU seconds / window
        ok = worst <= L_MAX * 1000 and measured_burst <= U_MAX
        r.update({"worst_lookup_ms": round(worst, 3), "burst_lookups_per_s": round(lam_burst, 1),
                  "burst_cpu_share_model": round(model_burst, 5), "burst_cpu_share_measured": round(measured_burst, 5),
                  "hour_cpu_share": round(r["seq_hour_s"] / 3600, 6)})
        print(f"  {r['scenario']:<14}{worst:>11.3f} ms{r['hour_cpu_share']:>11.3%}{lam_burst:>18.1f}{model_burst:>12.3%}"
              f"{measured_burst:>15.3%}  {'within boundary' if ok else 'OUTSIDE boundary'}")
    print(f"  Sequential work grew {b['seq_comparisons'] / a['seq_comparisons']:.0f}x (prediction ~400x = 20x records"
          f" x 20x requests); the hash index grew {b['hash_probes'] / a['hash_probes']:.0f}x (prediction 20x).")

    with open(os.path.join(RESULTS, "q2_facility_simulation.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("CSV  : results/q2_facility_simulation.csv")

    # operating-boundary graph with the two scenarios
    lams = [10 ** (k / 20) for k in range(-40, 81)]
    nmax = [min(L_MAX / t_c, U_MAX / (lam * t_c)) for lam in lams]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.plot(lams, nmax, color="#4C72B0", lw=2.5, label="boundary n_max = min(L/t_c, U/(lambda t_c))")
    ax.fill_between(lams, 1, nmax, color="#4C72B0", alpha=0.12, label="sequential search acceptable")
    for r, col in zip(rows, ("#55A868", "#C44E52")):
        lam_hour = r["searches"] / 3600
        ax.scatter([lam_hour], [r["active_records"]], s=70, color=col, marker="o", zorder=3,
                   label=f"{r['scenario']}: peak-hour average")
        ax.scatter([r["burst_lookups_per_s"]], [r["active_records"]], s=90, color=col, marker="^", zorder=3,
                   label=f"{r['scenario']}: reconciliation burst")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.01, 1e4)
    ax.set_ylim(10, 1e7)
    ax.set_xlabel("search requests per second, lambda (log)")
    ax.set_ylabel("active records n (log)")
    ax.set_title(f"Q2 - Operating boundary of Sequential Search (t_c = {t_c * 1e9:.0f} ns, L = 50 ms, U = 5 %)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(SHOTS, "q2_operating_boundary.png"), dpi=150)
    plt.close(fig)
    print("Graph: ../Output_Screenshots/q2_operating_boundary.png")


if __name__ == "__main__":
    main()
