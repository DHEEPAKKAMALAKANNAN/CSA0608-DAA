"""
CO4 Assignment 4B - test harness for all six tasks (greedy technique).

Loads the test catalogues task1..task6_test_cases.json from this folder (given, student-designed, boundary,
failure and large-scale cases), runs every case against the implementations in ../Source_Code/Task_N, compares
expected with actual, prints one PASS/FAIL line per case and finally  RESULT: k/k tests passed.
Task 6 additionally checks that every documented defect is still reproduced by the version just before its
fix and is absent from the final design (regression record of the debugging session).
Writes test_results.csv (id, category, description, expected, actual, status) next to this file.
Run:  py -3 run_all_tests.py
"""
import csv
import json
import os
import random
import sys
import time
from collections import Counter
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "Source_Code")
for t in range(1, 7):
    sys.path.insert(0, os.path.join(SRC, f"Task_{t}"))

import activity_selection as t1  # noqa: E402
import dijkstra_routing as t5  # noqa: E402
import huffman_coding as t3  # noqa: E402
import knapsack_coin_change as t2  # noqa: E402
import mst_prim_kruskal as t4  # noqa: E402
import task6_debugging as t6  # noqa: E402

INF = float("inf")
RESULTS = []


def data(task, name):
    return os.path.join(SRC, f"Task_{task}", "test_data", name)


def record(case, expected, actual, ok):
    status = "PASS" if ok else "FAIL"
    RESULTS.append(dict(id=case["id"], category=case["category"], description=case["description"],
                        expected=str(expected), actual=str(actual), status=status))
    print(f"{status}  {case['id']:<6} {case['category']:<8} {case['description'][:50]:<50} -> {str(actual)[:30]}")


def expect_error(case, fn):
    """Run fn; PASS if it raises the expected exception type."""
    try:
        res = fn()
        record(case, case["expect"]["error"], f"no error: {res}", False)
    except Exception as e:                                         # noqa: BLE001
        record(case, case["expect"]["error"], type(e).__name__, type(e).__name__ == case["expect"]["error"])


# ----------------------------------------------------------------------------- Task 1
def task1(case):
    ex, ty = case["expect"], case["type"]
    if "error" in ex:
        return expect_error(case, lambda: t1.select_eft(t1.make_requests(case["requests"])))
    if ty in ("eft_file", "eft"):
        reqs = t1.load_requests(data(1, case["file"])) if ty == "eft_file" else t1.make_requests(case["requests"])
        got = t1.select_eft(reqs)
        ids = [r.rid for r in got]
        ok = len(got) == ex["count"] and ("selected" not in ex or ids == ex["selected"])
        ok &= len(reqs) > 20 or t1.optimum_bruteforce(reqs) == len(got)
        return record(case, ex, f"{len(got)} {ids}", ok)
    if ty == "rule_fails":
        reqs = t1.make_requests(case["requests"])
        rc, ec, opt = len(t1.RULES[case["rule"]](reqs)), len(t1.select_eft(reqs)), t1.optimum_bruteforce(reqs)
        return record(case, ex, f"rule {rc}, EFT {ec}, opt {opt}",
                      (rc, ec, opt) == (ex["rule_count"], ex["eft_count"], ex["optimum"]))
    if ty == "rule_equals_eft":
        reqs = t1.load_requests(data(1, case["file"]))
        n = len(t1.RULES[case["rule"]](reqs))
        return record(case, ex, n, n == ex["count"] == len(t1.select_eft(reqs)))
    rng = random.Random(case.get("seed", 0))
    if ty == "random_vs_bruteforce":
        bad = sum(len(t1.select_eft(d)) != t1.optimum_bruteforce(d)
                  for d in (random_day(rng, case["n"]) for _ in range(case["trials"])))
        return record(case, ex, f"{case['trials'] - bad}/{case['trials']} equal", bad == 0)
    if ty == "random_naive_equal":
        bad = 0
        for _ in range(case["trials"]):
            d = random_day(rng, case["n"])
            bad += not (len(t1.select_eft(d)) == len(t1.select_naive_rescan(d)) == t1.optimum_dp(d))
        return record(case, ex, f"{case['trials'] - bad}/{case['trials']} equal", bad == 0)
    if ty == "large_vs_dp":
        reqs = [t1.Request(i, "", s, s + rng.randrange(30, 241, 15))
                for i, s in enumerate(rng.randrange(0, 30 * case["n"], 15) for _ in range(case["n"]))]
        k, opt = len(t1.select_eft(reqs)), t1.optimum_dp(reqs)
        return record(case, ex, f"EFT {k:,} = DP {opt:,}", k == opt)
    raise ValueError(ty)


def random_day(rng, n):
    reqs = []
    for i in range(n):
        s = 480 + rng.randrange(0, 570, 15)
        reqs.append(t1.Request(f"Q{i}", "", s, min(s + rng.randrange(30, 241, 15), 1080)))
    return reqs


# ----------------------------------------------------------------------------- Task 2
def items_of(spec):
    return [t2.Item(n, w, v) for n, w, v in spec]


def task2(case):
    ex, ty = case["expect"], case["type"]
    if ty == "coins" and "error" in ex:
        return expect_error(case, lambda: t2.greedy_change(case["coins"], case["amount"]))
    if "error" in ex:
        return expect_error(case, lambda: t2.fractional_sort(items_of(case["items"]), case["capacity"]))
    if ty in ("fractional", "fractional_file"):
        its = t2.load_items(data(2, case["file"])) if ty == "fractional_file" else items_of(case["items"])
        vs, _ = t2.fractional_sort(its, case["capacity"])
        vh, _ = t2.fractional_heap(its, case["capacity"])
        return record(case, ex["value"], f"sort {float(vs):g}, heap {float(vh):g}", vs == vh == Fraction(ex["value"]))
    if ty in ("zero_one", "zero_one_file"):
        its = t2.load_items(data(2, case["file"])) if ty == "zero_one_file" else items_of(case["items"])
        W = case["capacity"]
        got = {"greedy_density": t2.greedy_01(its, W, "density")[0], "greedy_value": t2.greedy_01(its, W, "value")[0],
               "optimum": t2.knapsack_01_dp(its, W)[0], "fractional": float(t2.fractional_sort(its, W)[0])}
        ok = all(got[k] == v for k, v in ex.items()) and t2.knapsack_01_bruteforce(its, W) == got["optimum"]
        return record(case, ex, {k: got[k] for k in ex}, ok)
    if ty == "coins":
        g, d = t2.greedy_change(case["coins"], case["amount"]), t2.dp_change(case["coins"], case["amount"])
        gl, dl = (None if g is None else len(g)), (None if d is None else len(d))
        ok = gl == ex["greedy"] and dl == ex["optimum"] and (g is None or sum(g) == case["amount"])
        return record(case, ex, f"greedy {gl}, optimum {dl}", ok)
    rng = random.Random(case.get("seed", 0))
    rand_items = lambda n: [t2.Item(i, rng.randint(1, 60), rng.randint(1, 100)) for i in range(n)]  # noqa: E731
    if ty == "random_fractional":
        bad = 0
        for _ in range(case["trials"]):
            its = rand_items(case["n"])
            W = rng.randint(1, sum(i.weight for i in its))
            vs, vh = t2.fractional_sort(its, W)[0], t2.fractional_heap(its, W)[0]
            bad += not (vs == vh and vs >= t2.knapsack_01_dp(its, W)[0])
        return record(case, ex, f"{case['trials'] - bad}/{case['trials']} ok", bad == 0)
    if ty == "random_dp_vs_bruteforce":
        bad = 0
        for _ in range(case["trials"]):
            its = rand_items(case["n"])
            W = rng.randint(1, sum(i.weight for i in its))
            bad += t2.knapsack_01_dp(its, W)[0] != t2.knapsack_01_bruteforce(its, W)
        return record(case, ex, f"{case['trials'] - bad}/{case['trials']} equal", bad == 0)
    if ty == "half_approx":
        bad = 0
        for _ in range(case["trials"]):
            its = rand_items(case["n"])
            W = rng.randint(1, sum(i.weight for i in its))
            bad += 2 * t2.greedy_01_half_approx(its, W)[0] < t2.knapsack_01_dp(its, W)[0]
        patho = t2.greedy_01_half_approx(items_of(case["items"]), case["capacity"])[0]
        return record(case, ex, f"pathological {patho}, {case['trials'] - bad}/{case['trials']} >= OPT/2",
                      bad == 0 and patho == ex["pathological"])
    if ty == "canonical":
        got = {k: t2.smallest_counterexample([int(x) for x in k.split()])[0] for k in case["systems"]}
        return record(case, case["systems"], got, got == case["systems"])
    raise ValueError(ty)


# ----------------------------------------------------------------------------- Task 3
def task3(case):
    ex, ty = case["expect"], case["type"]
    if ty == "huffman" and "error" in ex:
        return expect_error(case, lambda: t3.build_huffman(case["freqs"]))
    if ty == "decode":
        root = t3.build_huffman(case["freqs"])
        return expect_error(case, lambda: t3.decode(case["bits"], root))
    if ty == "encode":
        codes = t3.make_codes(t3.build_huffman(case["freqs"]))
        return expect_error(case, lambda: t3.encode(list(case["message"]), codes))
    if ty == "huffman":
        codes = t3.make_codes(t3.build_huffman(case["freqs"]))
        lens = {s: len(c) for s, c in codes.items()}
        ok = ("total_bits" not in ex or t3.total_bits(case["freqs"], codes) == ex["total_bits"])
        ok &= "lengths" not in ex or lens == ex["lengths"]
        ok &= "max_length" not in ex or max(lens.values()) == ex["max_length"]
        return record(case, ex, f"bits {t3.total_bits(case['freqs'], codes)}, lengths {lens}", ok)
    if ty == "ties":
        res = {}
        for pol in ("fifo", "lifo"):
            c = t3.make_codes(t3.build_huffman(case["freqs"], pol))
            res[f"{pol}_cost"], res[f"{pol}_max_len"] = t3.total_bits(case["freqs"], c), max(map(len, c.values()))
        return record(case, ex, res, res == ex)
    if ty == "round_trip":
        root = t3.build_huffman(case["freqs"])
        bits = t3.encode(list(case["message"]), t3.make_codes(root))
        back = "".join(t3.decode(bits, root))
        return record(case, ex, f"{len(bits)} bits, decoded {back}", len(bits) == ex["bits"] and back == case["message"])
    rng = random.Random(case.get("seed", 0))
    if ty in ("random_equal_cost", "random_bounds"):
        bad = 0
        for _ in range(case["trials"]):
            freqs = {i: rng.randint(1, 1000) for i in range(rng.randint(2, case["m"]))}
            root = t3.build_huffman(freqs)
            codes = t3.make_codes(root)
            cost = t3.total_bits(freqs, codes)
            if ty == "random_equal_cost":
                cw = sorted(codes.values())
                prefix_free = all(not b.startswith(a) for a, b in zip(cw, cw[1:]))
                msg = rng.choices(list(freqs), k=50)
                ok = cost == t3.huffman_naive(freqs) == t3.huffman_two_queue(sorted(freqs.values())) and prefix_free
                ok &= t3.decode(t3.encode(msg, codes), root) == msg
            else:
                H, L = t3.entropy(freqs), t3.average_length(freqs, codes)
                ok = abs(sum(2 ** -len(c) for c in codes.values()) - 1) < 1e-12 and H - 1e-9 <= L < H + 1
            bad += not ok
        return record(case, ex, f"{case['trials'] - bad}/{case['trials']} ok", bad == 0)
    if ty == "soc_stream":
        weights = [1 / (k ** 1.1) for k in range(1, 13)]
        msg = rng.choices("LDWFHSVPMXUB", weights=weights, k=case["n"])
        freqs = Counter(msg)
        root = t3.build_huffman(freqs)
        bits = t3.encode(msg, t3.make_codes(root))
        ok = len(bits) < 4 * len(msg) and t3.decode(bits, root) == msg
        return record(case, ex, f"{len(bits) / len(msg):.3f} bits/event < 4, round trip ok", ok)
    raise ValueError(ty)


# ----------------------------------------------------------------------------- Task 4
def rand_graph(rng, n, m):
    edges = [(v, rng.randrange(v), rng.randint(1, 20)) for v in range(1, n)]
    while len(edges) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            edges.append((u, v, rng.randint(1, 20)))
    return edges


def task4(case):
    ex, ty = case["expect"], case["type"]
    if ty == "mst" and "error" in ex:
        return expect_error(case, lambda: t4.kruskal(case["n"], [tuple(e) for e in case["edges"]]))
    if ty in ("mst", "mst_file"):
        if ty == "mst_file":
            names, edges = t4.load_graph(data(4, case["file"]))
            n = len(names)
        else:
            n, edges = case["n"], [tuple(e) for e in case["edges"]]
        pt, pw, _ = t4.prim_heap(n, edges)
        _, aw, _ = t4.prim_array(n, edges)
        kt, kw, _ = t4.kruskal(n, edges)
        ok = pw == aw == kw == ex["weight"] and len(pt) == len(kt) == ex["edges"]
        if "distinct_msts" in ex:
            best, cnt, _ = t4.mst_bruteforce(n, edges)
            ok &= best == ex["weight"] and cnt == ex["distinct_msts"]
        return record(case, ex, f"Prim {pw}/{aw}, Kruskal {kw}, {len(kt)} edges", ok)
    if ty == "cut_property":
        names, edges = t4.load_graph(data(4, case["file"]))
        n = len(names)
        ok = t4.cut_property_holds(n, edges, t4.prim_heap(n, edges)[0]) and \
            t4.cut_property_holds(n, edges, t4.kruskal(n, edges)[0])
        return record(case, ex, ok, ok)
    if ty == "disconnected_file":
        names, edges = t4.load_graph(data(4, case["file"]))
        n = len(names)
        _, _, reached = t4.prim_heap(n, edges)
        ft, fw, comps = t4.kruskal(n, edges)
        try:
            t4.spanning_tree(n, edges)
            err = None
        except ValueError:
            err = "ValueError"
        got = dict(prim_reached=reached, forest_edges=len(ft), components=comps, forest_weight=fw, error=err)
        return record(case, ex, got, got == ex)
    rng = random.Random(case.get("seed", 0))
    if ty == "random_vs_bruteforce":
        bad = 0
        for _ in range(case["trials"]):
            edges = rand_graph(rng, case["n"], case["m"])
            ws = {t4.prim_heap(case["n"], edges)[1], t4.prim_array(case["n"], edges)[1], t4.kruskal(case["n"], edges)[1],
                  t4.mst_bruteforce(case["n"], edges)[0]}
            bad += len(ws) != 1
        return record(case, ex, f"{case['trials'] - bad}/{case['trials']} equal", bad == 0)
    if ty == "uf_modes":
        bad = 0
        for _ in range(case["trials"]):
            edges = rand_graph(rng, case["n"], case["m"])
            bad += len({t4.kruskal(case["n"], edges, mode)[1] for mode in ("naive", "rank", "rank+compress")}) != 1
        return record(case, ex, f"{case['trials'] - bad}/{case['trials']} equal", bad == 0)
    if ty == "random_large":
        edges = rand_graph(rng, case["n"], case["m"])
        ws = (t4.prim_heap(case["n"], edges)[1], t4.prim_array(case["n"], edges)[1], t4.kruskal(case["n"], edges)[1])
        return record(case, ex, f"weights {ws}", len(set(ws)) == 1)
    raise ValueError(ty)


# ----------------------------------------------------------------------------- Task 5
def task5(case):
    ex, ty = case["expect"], case["type"]
    if ty == "dijkstra" and "error" in ex:
        return expect_error(case, lambda: t5.dijkstra_heap(case["n"], [tuple(e) for e in case["edges"]], case["source"]))
    if ty in ("network_file", "route_file", "heap_accounting"):
        names, edges = t5.load_network(data(5, case["file"]))
        s = names.index(case["source"])
        da, _ = t5.dijkstra_array(len(names), edges, s)
        ops = Counter()
        dh, ph = t5.dijkstra_heap(len(names), edges, s, ops)
        if ty == "network_file":
            got = {names[i]: d for i, d in enumerate(dh)}
            return record(case, ex["dist"], got, got == ex["dist"] and da == dh)
        if ty == "route_file":
            t = names.index(case["target"])
            path = [names[i] for i in t5.path_to(ph, s, t, dh)]
            return record(case, ex, f"{dh[t]} {'-'.join(path)}", dh[t] == ex["time"] and path == ex["path"])
        ok = ops["pops"] == ops["pushes"] == ops["settled"] + ops["stale_pops"] and ops["settled"] == len(names)
        return record(case, ex, f"pushes {ops['pushes']}, settled {ops['settled']}, stale {ops['stale_pops']}", ok)
    if ty == "dijkstra":
        edges = [tuple(e) for e in case["edges"]]
        da, _ = t5.dijkstra_array(case["n"], edges, case["source"])
        dh, ph = t5.dijkstra_heap(case["n"], edges, case["source"])
        exp = [INF if x == "inf" else x for x in ex["dist"]]
        ok = da == dh == exp
        if "path" in ex:
            ok &= t5.path_to(ph, case["source"], case["target"], dh) == ex["path"]
        return record(case, ex, f"dist {dh}", ok)
    if ty == "negative_edge":
        names, edges = t5.load_network(data(5, case["file"]))
        try:
            t5.dijkstra_heap(len(names), edges, 0)
            err = None
        except ValueError:
            err = "ValueError"
        du, _ = t5.dijkstra_heap(len(names), edges, 0, allow_negative=True)
        db, _, _ = t5.bellman_ford(len(names), edges, 0)
        got = {"error": err, "unsafe": {k: du[names.index(k)] for k in ex["unsafe"]},
               "bellman_ford": {k: db[names.index(k)] for k in ex["bellman_ford"]}}
        return record(case, ex, got, got == ex)
    if ty == "negative_cycle":
        names, edges = t5.load_network(data(5, case["file"]))
        neg = t5.bellman_ford(len(names), edges, 0)[2]
        return record(case, ex, f"negative cycle {neg}", neg == ex["negative_cycle"])
    rng = random.Random(case.get("seed", 0))
    n, m = case.get("n"), case.get("m")
    if ty == "random_vs_bellman_ford":
        bad = 0
        for _ in range(case["trials"]):
            edges = [(rng.randrange(n), rng.randrange(n), rng.randint(0, 20)) for _ in range(m)]
            s = rng.randrange(n)
            dh, ph = t5.dijkstra_heap(n, edges, s)
            ok = t5.dijkstra_array(n, edges, s)[0] == dh == t5.bellman_ford(n, edges, s)[0]
            wmin = {}
            for u, v, w in edges:
                wmin[(u, v)] = min(w, wmin.get((u, v), INF))
            for t in range(n):
                p = t5.path_to(ph, s, t, dh)
                ok &= (p is None) == (dh[t] == INF)
                if p:
                    ok &= sum(wmin[e] for e in zip(p, p[1:])) == dh[t]
            bad += not ok
        return record(case, ex, f"{case['trials'] - bad}/{case['trials']} equal", bad == 0)
    if ty == "early_exit":
        bad = 0
        for _ in range(case["trials"]):
            edges = [(rng.randrange(n), rng.randrange(n), rng.randint(1, 50)) for _ in range(m)]
            s, t = rng.randrange(n), rng.randrange(n)
            bad += t5.dijkstra_heap(n, edges, s, target=t)[0][t] != t5.dijkstra_heap(n, edges, s)[0][t]
        return record(case, ex, f"{case['trials'] - bad}/{case['trials']} equal", bad == 0)
    raise ValueError(ty)


# ----------------------------------------------------------------------------- Task 6
def task6(case, cat):
    st, e, a, _ = t6.run_case(t6.Final, case, cat)
    record(case, e, a, st == "PASS")


DEFECTS = [("D1", "V1", "T6-G2"), ("D2", "V3", "T6-S1"), ("D3", "V0 given", "T6-G1"), ("D4", "V4", "T6-S5"),
           ("D5", "V2", "T6-G3")]


def task6_defects(cat):
    """Each defect: the version just before its fix fails the documented case, FINAL passes it."""
    versions = {name: cls for name, cls, _ in t6.VERSIONS}
    by_id = {c["id"]: c for c in cat["cases"]}
    for d, before, cid in DEFECTS:
        c = by_id[cid]
        st_before = t6.run_case(versions[before], c, cat)[0]
        st_final = t6.run_case(t6.Final, c, cat)[0]
        case = {"id": f"T6-{d}", "category": "debug",
                "description": f"defect {d}: {before} fails {cid[3:]}, FINAL passes"}
        record(case, "FAIL before fix, PASS after", f"{before}: {st_before}, FINAL: {st_final}",
               st_before == "FAIL" and st_final == "PASS")


def main():
    t0 = time.perf_counter()
    print("CO4 ASSIGNMENT 4B - TEST HARNESS (given, student-designed, boundary, failure, scale and debug cases)")
    print("=" * 106)
    runners = {1: task1, 2: task2, 3: task3, 4: task4, 5: task5}
    for task in range(1, 7):
        with open(os.path.join(HERE, f"task{task}_test_cases.json"), encoding="utf-8") as f:
            cat = json.load(f)
        print(f"-- {cat['task']}")
        for case in cat["cases"]:
            try:
                if task == 6:
                    task6(case, cat)
                else:
                    runners[task](case)
            except Exception as e:                                 # noqa: BLE001  a crash is a FAIL
                record(case, case.get("expect"), f"CRASH {type(e).__name__}: {e}", False)
        if task == 6:
            task6_defects(cat)
    with open(os.path.join(HERE, "test_results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(RESULTS[0]))
        w.writeheader()
        w.writerows(RESULTS)
    passed = sum(r["status"] == "PASS" for r in RESULTS)
    by_cat = Counter(r["category"] for r in RESULTS)
    print("=" * 106)
    print("Cases by category: " + ", ".join(f"{k} {v}" for k, v in by_cat.items()))
    print(f"Run time {time.perf_counter() - t0:.1f} s; every case with expected and actual values is in test_results.csv")
    print(f"RESULT: {passed}/{len(RESULTS)} tests passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
