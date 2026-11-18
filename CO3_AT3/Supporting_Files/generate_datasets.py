"""SwiftLogix CO3 case study - generate the larger datasets and the test-case files (seed 42).

Writes
    datasets/generated/m1_shipment_events_5000.csv   5,000 events as delivered: 16 hub feeds, each in time order
    datasets/generated/m2_priority_scores_5000.csv   5,000 open orders with integer priority scores 0..100
    datasets/generated/m3_tracking_index_20000.csv   20,000 sorted tracking IDs with record offsets
    datasets/generated/m3_lookup_queries_2000.csv    1,000 present + 1,000 absent tracking IDs
    datasets/generated/m4_demand_64x64.csv, m4_cost_64x64.csv   64 x 64 route matrices (integers 0..9)
    test_cases/m1_merge_sort_cases.json ... m4_strassen_cases.json   edge cases with EXPECTED outputs computed
        by independent references (sorted(), bisect, numpy) - never by the algorithms under test.

Run:  py -3 generate_datasets.py
"""
import bisect
import csv
import json
import random
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
GEN = HERE / "datasets" / "generated"
CASES = HERE / "test_cases"
HUBS = ["BLR", "MAA", "HYD", "DEL", "BOM", "CCU", "PNQ", "AMD", "JAI", "LKO", "COK", "IXC", "NAG", "IDR", "VTZ", "GAU"]
STATUSES = ["PICKED_UP", "ARRIVED_AT_HUB", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"]
DATES = ["2026-11-17", "2026-11-18", "2026-11-19"]


def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {path.relative_to(HERE)}  ({len(rows):,} rows)")


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1)
    print(f"  wrote {path.relative_to(HERE)}  ({len(obj['cases'])} cases)")


def gen_events(rng, n=5000):
    rows, eid = [], 1
    for h, hub in enumerate(HUBS):                      # each hub feed is chronological; feeds are concatenated
        feed = []
        for _ in range(n // len(HUBS) + (1 if h < n % len(HUBS) else 0)):
            date = rng.choice(DATES)
            t = f"{rng.randrange(6, 22):02d}:{rng.randrange(60):02d}:{rng.choice([0, 0, 15, 30, 45]):02d}"
            feed.append((date, t))
        for date, t in sorted(feed):
            rows.append([f"E{eid:05d}", f"SLX{rng.randrange(10 ** 9, 10 ** 10)}", date, t, hub,
                         rng.choice(STATUSES)])
            eid += 1
    return rows


def main():
    rng = random.Random(42)
    print("Generating datasets (seed 42)")
    write_csv(GEN / "m1_shipment_events_5000.csv",
              ["event_id", "tracking_id", "delivery_date", "event_time", "hub", "status"], gen_events(rng))
    write_csv(GEN / "m2_priority_scores_5000.csv", ["order_id", "priority_score"],
              [[f"O{100000 + i}", rng.randint(0, 100)] for i in range(5000)])
    ids = sorted(rng.sample(range(10 ** 9, 10 ** 10), 20000))
    offsets = list(range(20000))
    rng.shuffle(offsets)
    write_csv(GEN / "m3_tracking_index_20000.csv", ["position", "tracking_id", "record_offset"],
              [[p, f"SLX{k}", o] for p, (k, o) in enumerate(zip(ids, offsets))])
    id_set = set(ids)
    present = rng.sample(ids, 1000)
    absent = []
    while len(absent) < 1000:
        k = rng.randrange(10 ** 9, 10 ** 10)
        if k not in id_set:
            absent.append(k)
    queries = [[f"Q{i + 1:04d}", f"SLX{k}", "present"] for i, k in enumerate(present)] + \
              [[f"Q{i + 1001:04d}", f"SLX{k}", "absent"] for i, k in enumerate(absent)]
    write_csv(GEN / "m3_lookup_queries_2000.csv", ["query_id", "tracking_id", "expected"], queries)
    for name, seed in (("m4_demand_64x64.csv", 1), ("m4_cost_64x64.csv", 2)):
        r = random.Random(seed)
        write_csv(GEN / name, [f"c{j}" for j in range(64)], [[r.randint(0, 9) for _ in range(64)] for _ in range(64)])

    print("Generating test cases (expected outputs from sorted(), bisect and numpy)")
    sort_inputs = {
        "empty list": [], "single element": [42], "two elements reversed": [9, 3],
        "duplicates": [5, 1, 5, 3, 1, 5, 2], "already sorted": list(range(1, 21)),
        "reverse sorted": list(range(20, 0, -1)), "all equal": [7] * 15, "negative and zero": [0, -4, 8, -4, 3, 0, -9],
        "sample priority scores": [72, 35, 91, 50, 18, 64, 91, 27, 83, 50, 9, 50],
        "random 200 (0..100)": [rng.randint(0, 100) for _ in range(200)],
        "organ pipe": list(range(1, 26)) + list(range(25, 0, -1)),
    }
    cases = [{"name": k, "input": v, "expected": sorted(v)} for k, v in sort_inputs.items()]
    stab = [[rng.randint(0, 4), f"r{i:02d}"] for i in range(30)]     # (key, arrival tag): many ties
    m1_cases = cases + [{"name": "stability: 30 records, 5 keys", "input": stab,
                         "expected": sorted(stab, key=lambda r: r[0]), "key": 0}]
    write_json(CASES / "m1_merge_sort_cases.json", {"module": "M1 merge sort", "cases": m1_cases})
    write_json(CASES / "m2_quick_sort_cases.json", {"module": "M2 quick sort", "cases": cases})

    sample = [1046629381, 1198804562, 1873305540, 2290017745, 2675530981, 3105569820, 3359087714, 4410926638,
              4827301956, 5561290347, 6043378120, 6918845023, 7720418833, 8837152209, 9064471315, 9580032217]
    big = sorted(rng.sample(range(10 ** 9, 10 ** 10), 1000))
    search_sets = [
        ("empty index", [], [5]), ("single ID - hit", [500], [500]), ("single ID - below/above", [500], [100, 900]),
        ("two IDs", [10, 20], [10, 20, 5, 15, 25]),
        ("given sample: 8 queries", sample, [4410926638, 1046629381, 9580032217, 6918845023, 3000000000,
                                             999999999, 9999999999, 7720418833]),
        ("1,000 IDs: first, last, middle, gaps", big, [big[0], big[-1], big[500], big[0] - 1, big[-1] + 1,
                                                      big[250] + 1, big[999] - 1]),
    ]
    m3_cases = []
    for name, keys, qs in search_sets:
        exp = []
        for q in qs:
            p = bisect.bisect_left(keys, q)
            exp.append(p if p < len(keys) and keys[p] == q else -1)
        m3_cases.append({"name": name, "keys": keys, "queries": qs, "expected": exp})
    write_json(CASES / "m3_binary_search_cases.json", {"module": "M3 binary search", "cases": m3_cases})

    sample_d = [[4, 2, 0, 3], [1, 5, 2, 0], [3, 0, 6, 1], [2, 4, 1, 5]]
    sample_c = [[2, 1, 3, 0], [1, 4, 0, 2], [0, 3, 2, 1], [5, 0, 1, 3]]
    mats = [("1 x 1", [[3]], [[4]]), ("2 x 2", [[1, 2], [3, 4]], [[5, 6], [7, 8]]),
            ("given sample 4 x 4 (D x C)", sample_d, sample_c)]
    for n in (3, 5, 6, 7, 12):
        mats.append((f"{n} x {n} (padding needed)", [[rng.randint(-5, 9) for _ in range(n)] for _ in range(n)],
                     [[rng.randint(-5, 9) for _ in range(n)] for _ in range(n)]))
    ident = [[int(i == j) for j in range(8)] for i in range(8)]
    rnd8 = [[rng.randint(0, 9) for _ in range(8)] for _ in range(8)]
    mats += [("8 x 8 identity x random", ident, rnd8), ("8 x 8 zero x random", [[0] * 8 for _ in range(8)], rnd8),
             ("16 x 16 random", [[rng.randint(0, 9) for _ in range(16)] for _ in range(16)],
              [[rng.randint(0, 9) for _ in range(16)] for _ in range(16)])]
    m4_cases = [{"name": nm, "A": A, "B": B, "expected": (np.array(A) @ np.array(B)).tolist()} for nm, A, B in mats]
    write_json(CASES / "m4_strassen_cases.json", {"module": "M4 Strassen", "cases": m4_cases})


if __name__ == "__main__":
    main()
