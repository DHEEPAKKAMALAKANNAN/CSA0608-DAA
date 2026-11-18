"""
Task 3 - experiments for Huffman coding of SOC logs.

E1  Compression of a synthetic SOC event stream (100,000 events, 12 event types, Zipf-like frequencies):
    event-level Huffman vs 4-bit fixed codes vs entropy, plus character-level Huffman of the text log vs
    8-bit ASCII; every encoding is decoded again and compared (round-trip validation).
E2  Code quality on four frequency shapes (m = 16): H <= average length < H + 1.
E3  Construction cost: naive linear-scan Theta(m^2) vs binary heap Theta(m log m) vs two-queue Theta(m)
    (after sorting), all three must give the same total cost.
Writes results/task3_*.csv and results/task3_experiments.png;
also writes test_data/soc_events_sample.log (first 40 log lines).
Run:  py -3 task3_experiments.py
"""
import csv
import math
import os
import random
import time
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from huffman_coding import (average_length, build_huffman, decode, encode, entropy, fixed_length,  # noqa: E402
                            huffman_naive, huffman_two_queue, make_codes, total_bits)

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
SEED = 42
EVENTS = ["AUTH_OK", "DNS_QUERY", "FW_DROP", "AUTH_FAIL", "HTTP_4XX", "PORT_SCAN", "VPN_LOGIN", "PRIV_ESC",
          "MALWARE", "DLP_ALERT", "USB_INSERT", "BRUTE_FORCE"]
SYMBOL = dict(zip(EVENTS, "LDWFHSVPMXUB"))


def write_csv(name, rows):
    with open(os.path.join(RES, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def soc_stream(n, rng):
    """n events; event k (k = 1..12) has probability proportional to 1 / k^1.1 (Zipf-like)."""
    weights = [1 / (k ** 1.1) for k in range(1, len(EVENTS) + 1)]
    return rng.choices(EVENTS, weights=weights, k=n)


def log_lines(events, rng):
    lines = []
    for i, ev in enumerate(events):
        t = 8 * 3600 + i // 4
        lines.append(f"2026-11-19T{t // 3600 % 24:02d}:{t // 60 % 60:02d}:{t % 60:02d} {ev:<11} "
                     f"10.{rng.randint(0, 3)}.{rng.randint(0, 9)}.{rng.randint(1, 254)} sev={rng.randint(1, 5)}")
    return lines


def e1_soc(n=100_000):
    rng = random.Random(SEED)
    events = soc_stream(n, rng)
    symbols = [SYMBOL[e] for e in events]
    lines = log_lines(events, rng)
    with open(os.path.join(HERE, "test_data", "soc_events_sample.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines[:40]) + "\n")
    rows = []
    print(f"E1  SOC stream of {n:,} events, {len(EVENTS)} event types (Zipf-like); round trip checked")
    print(f"    {'encoding':<34} {'alphabet':>8} {'bits/symbol':>11} {'total bits':>12} {'saving':>9} "
          f"{'entropy':>8} {'encode+decode ms':>16} {'round trip':>10}")
    text = "\n".join(lines)
    for name, seq, fixed in (("event symbols (one per record)", symbols, fixed_length(len(EVENTS))),
                             ("characters of the text log", list(text), 8)):
        freqs = Counter(seq)
        t0 = time.perf_counter()
        root = build_huffman(freqs)
        codes = make_codes(root)
        bits = encode(seq, codes)
        ok = decode(bits, root) == seq
        ms = (time.perf_counter() - t0) * 1e3
        abl = len(bits) / len(seq)
        assert len(bits) == total_bits(freqs, codes)
        rows.append(dict(encoding=name, symbols=len(seq), alphabet=len(freqs), huffman_bits=len(bits),
                         fixed_bits_per_symbol=fixed, fixed_bits=fixed * len(seq), avg_bits=round(abl, 4),
                         entropy=round(entropy(freqs), 4), saving_pct=round(100 * (1 - abl / fixed), 2),
                         ms=round(ms, 1), round_trip_ok=ok))
        print(f"    {name:<34} {len(freqs):>8} {abl:>11.4f} {len(bits):>12,} {100 * (1 - abl / fixed):>8.1f}% "
              f"{entropy(freqs):>8.4f} {ms:>16.1f} {str(ok):>10}")
    freqs = Counter(symbols)
    codes = make_codes(build_huffman(freqs))
    print("    event code table: " + "  ".join(f"{s}={codes[s]}" for s in sorted(codes, key=lambda s: -freqs[s])))
    write_csv("task3_01_soc_compression.csv", rows)
    return rows


def e2_shapes(m=16):
    shapes = {"uniform": [100] * m,
              "Zipf (1/k)": [round(10000 / k) for k in range(1, m + 1)],
              "geometric (1/2^k)": [2 ** (m - k) for k in range(1, m + 1)],
              "Fibonacci": [1, 1]}
    while len(shapes["Fibonacci"]) < m:
        shapes["Fibonacci"].append(shapes["Fibonacci"][-1] + shapes["Fibonacci"][-2])
    rows = []
    print(f"\nE2  Code quality for four frequency shapes (m = {m} symbols): H <= L < H + 1")
    print(f"    {'shape':<18} {'entropy H':>9} {'Huffman L':>9} {'fixed':>5} {'L - H':>6} {'max length':>10} "
          f"{'within bound':>12}")
    for name, fs in shapes.items():
        freqs = {f"s{i}": f for i, f in enumerate(fs)}
        codes = make_codes(build_huffman(freqs))
        H, L = entropy(freqs), average_length(freqs, codes)
        ok = H - 1e-12 <= L < H + 1
        rows.append(dict(shape=name, m=m, entropy=round(H, 4), huffman_avg=round(L, 4), fixed=fixed_length(m),
                         redundancy=round(L - H, 4), max_length=max(map(len, codes.values())), bound_ok=ok))
        print(f"    {name:<18} {H:>9.4f} {L:>9.4f} {fixed_length(m):>5} {L - H:>6.3f} "
              f"{max(map(len, codes.values())):>10} {str(ok):>12}")
    write_csv("task3_02_frequency_shapes.csv", rows)
    return rows


def e3_construction(sizes=(64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384), naive_max=4096):
    rng = random.Random(SEED)
    rows = []
    print("\nE3  Construction cost for alphabet size m (random frequencies 1..10^6)")
    print(f"    {'m':>6} {'naive scans':>12} {'m^2':>11} {'heap cmp':>10} {'m log2 m':>9} {'2-queue cmp':>11} "
          f"{'naive ms':>9} {'heap ms':>8} {'2q ms*':>7} {'same cost':>9}")
    for m in sizes:
        freqs = {i: rng.randint(1, 10 ** 6) for i in range(m)}
        h_ops = Counter()
        t0 = time.perf_counter(); root = build_huffman(freqs, ops=h_ops); th = time.perf_counter() - t0
        h_cost = total_bits(freqs, make_codes(root))
        q_ops = Counter()
        srt = sorted(freqs.values())
        t0 = time.perf_counter(); q_cost = huffman_two_queue(srt, q_ops); tq = time.perf_counter() - t0
        n_cmp, tn, n_cost = "", "", None
        if m <= naive_max:
            n_ops = Counter()
            t0 = time.perf_counter(); n_cost = huffman_naive(freqs, n_ops); tn = (time.perf_counter() - t0) * 1e3
            n_cmp = n_ops["scan_comparisons"]
        same = h_cost == q_cost and (n_cost is None or n_cost == h_cost)
        rows.append(dict(m=m, naive_scan_comparisons=n_cmp, m_squared=m * m, heap_comparisons=h_ops["heap_comparisons"],
                         m_log2_m=round(m * math.log2(m)), two_queue_comparisons=q_ops["queue_comparisons"],
                         naive_ms=round(tn, 1) if tn != "" else "", heap_ms=round(th * 1e3, 1),
                         two_queue_ms=round(tq * 1e3, 2), same_cost=same))
        print(f"    {m:>6,} {n_cmp if n_cmp == '' else f'{n_cmp:,}':>12} {m * m:>11,} {h_ops['heap_comparisons']:>10,} "
              f"{round(m * math.log2(m)):>9,} {q_ops['queue_comparisons']:>11,} "
              f"{'' if tn == '' else f'{tn:.1f}':>9} {th * 1e3:>8.1f} {tq * 1e3:>7.2f} {str(same):>9}")
    print("    * two-queue time excludes the initial sort of the frequencies")
    write_csv("task3_03_construction_cost.csv", rows)
    return rows


def plot(shape_rows, cost_rows):
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
    names = [r["shape"] for r in shape_rows]
    x = range(len(names))
    ax[0].bar([i - 0.27 for i in x], [r["fixed"] for r in shape_rows], 0.27, label="fixed length", color="#9E9E9E")
    ax[0].bar(list(x), [r["huffman_avg"] for r in shape_rows], 0.27, label="Huffman average", color="#1565C0")
    ax[0].bar([i + 0.27 for i in x], [r["entropy"] for r in shape_rows], 0.27, label="entropy H", color="#2E7D32")
    ax[0].set_xticks(list(x)); ax[0].set_xticklabels(names, fontsize=8)
    ax[0].set_ylabel("bits per symbol"); ax[0].set_title("E2: code length vs entropy (m = 16)")
    ax[0].legend(fontsize=8); ax[0].grid(axis="y", alpha=0.3)
    m = [r["m"] for r in cost_rows]
    nv = [(r["m"], r["naive_scan_comparisons"]) for r in cost_rows if r["naive_scan_comparisons"] != ""]
    ax[1].loglog([a for a, _ in nv], [b for _, b in nv], "s-", label="naive linear scan (measured)")
    ax[1].loglog(m, [r["heap_comparisons"] for r in cost_rows], "o-", label="binary heap (measured)")
    ax[1].loglog(m, [r["two_queue_comparisons"] for r in cost_rows], "^-", label="two queues (measured)")
    ax[1].loglog(m, [x * x for x in m], "k:", lw=1, label="m²")
    ax[1].loglog(m, [x * math.log2(x) for x in m], "k--", lw=1, label="m log₂ m")
    ax[1].set_xlabel("alphabet size m"); ax[1].set_ylabel("comparisons (count)")
    ax[1].set_title("E3: cost of building the Huffman tree"); ax[1].legend(fontsize=7)
    ax[1].grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "task3_experiments.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(RES, exist_ok=True)
    print("TASK 3 - EXPERIMENTS (seed 42)")
    print("=" * 112)
    e1_soc()
    shapes = e2_shapes()
    cost = e3_construction()
    plot(shapes, cost)
    print("\nWrote results/task3_01..03_*.csv and results/task3_experiments.png")


if __name__ == "__main__":
    main()
