"""
Task 6 - systematic debugging session for the given route service: reproduce -> isolate -> fix -> re-test.

1. REPRODUCE  run the Task 6 test catalogue (Test_Cases/task6_test_cases.json: given, designed, boundary,
              failure and scale cases) against the GIVEN code and record expected vs actual.
2. ISOLATE    minimal reproductions with instrumentation (traces, counters, a step-budget watchdog that
              stops runaway loops) - one per defect, each with the line that causes it.
3. FIX        one defect at a time: V1 (+D3) -> V2 (+D1) -> V3 (+D5) -> V4 (+D2) -> FINAL (+D4, A*);
4. RE-TEST    the whole catalogue after every fix (regression), ending with the defect table.
The intermediate versions V1-V4 are small subclasses of the given class below, so each fix is visible
in isolation; FINAL is fixed_route_service.RouteService.
Run:  py -3 task6_debugging.py
"""
import heapq
import json
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Task_5"))
from city_network import apply_feed_to_list, city_grid, daily_feed  # noqa: E402
from dijkstra_routing import dijkstra_heap  # noqa: E402  (Task 5 reference implementation)
from fixed_route_service import RouteService as Final  # noqa: E402
from given_faulty_route_service import RouteService as Given  # noqa: E402

CATALOGUE = os.path.join(HERE, "..", "..", "Test_Cases", "task6_test_cases.json")
INF = float("inf")


# ----------------------------------------------------------------------------- instrumentation
class Watchdog(Counter):
    """Stats counter that aborts a route search after `limit` expansions (runaway loop detector)."""

    def __init__(self, limit):
        super().__init__()
        self.limit = limit

    def __setitem__(self, key, value):
        if key == "expansions" and value > self.limit:
            raise RuntimeError(f"watchdog: > {self.limit:,} expansions (runaway search)")
        super().__setitem__(key, value)


# ----------------------------------------------------------------------------- intermediate versions
class V1(Given):
    """Given + FIX D3: path in travel order, including the source; None for an unreachable target."""

    def _path(self, prev, src, dst):
        if dst != src and dst not in prev:                           # FIX D3: unreachable -> None
            return None
        path = [dst]
        while path[-1] != src:
            path.append(prev[path[-1]])
        return path[::-1]                                            # FIX D3: src first


class V2(V1):
    """V1 + FIX D1: the destination is final only when it is popped (settled), not when discovered."""

    def route(self, src, dst):
        dist, prev, heap = {src: 0}, {}, [(0, src)]
        while heap:
            d, u = heapq.heappop(heap)
            self.stats["expansions"] += 1
            if u == dst:                                             # FIX D1
                return d, self._path(prev, src, dst)
            for v, w in self.neighbours(u):
                self.stats["relaxations"] += 1
                nd = d + w
                if v not in dist or nd < dist[v]:
                    dist[v], prev[v] = nd, u
                    heapq.heappush(heap, (nd, v))
        return dist.get(dst, INF), self._path(prev, src, dst)


class V3(V2):
    """V2 + FIX D5: validate queries and the daily feed (-1 closes a road, other negatives rejected)."""

    def __init__(self, n, roads):
        for u, v, w in roads:
            if w < 0:
                raise ValueError(f"road ({u}, {v}) has negative travel time {w}")
        super().__init__(n, roads)
        self.closed = {}

    def _check(self, j):
        if not (0 <= j < self.n):
            raise ValueError(f"unknown junction {j}")

    def apply_daily_update(self, updates):
        known = {(a, b) for a, b, _ in self.roads} | set(self.closed)
        for u, v, w in updates:                                      # FIX D5: validate the whole feed first
            self._check(u); self._check(v)
            if (u, v) not in known:
                raise ValueError(f"update for unknown road ({u}, {v})")
            if w < 0 and w != -1:
                raise ValueError(f"invalid travel time {w} for road ({u}, {v})")
        for u, v, w in updates:
            self.stats["road_scans"] += len(self.roads)               # each record still rebuilds the list (D4)
            if w == -1:                                              # FIX D5: closed road leaves the list
                self.closed[(u, v)] = True
                self.roads = [r for r in self.roads if (r[0], r[1]) != (u, v)]
            else:
                self.closed.pop((u, v), None)
                self.roads = [r for r in self.roads if (r[0], r[1]) != (u, v)] + [(u, v, w)]

    def route(self, src, dst):
        self._check(src); self._check(dst)                           # FIX D5: reject unknown junctions
        return super().route(src, dst)


class V4(V3):
    """V3 + FIX D2: skip stale heap entries (a junction is expanded at most once)."""

    def route(self, src, dst):
        self._check(src); self._check(dst)
        dist, prev, heap = {src: 0}, {}, [(0, src)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:                                          # FIX D2: stale entry
                continue
            self.stats["expansions"] += 1
            if u == dst:
                return d, self._path(prev, src, dst)
            for v, w in self.neighbours(u):
                self.stats["relaxations"] += 1
                nd = d + w
                if v not in dist or nd < dist[v]:
                    dist[v], prev[v] = nd, u
                    heapq.heappush(heap, (nd, v))
        return INF, None


VERSIONS = [("V0 given", Given, "-"), ("V1", V1, "D3"), ("V2", V2, "D3 D1"), ("V3", V3, "D3 D1 D5"),
            ("V4", V4, "D3 D1 D5 D2"), ("FINAL", Final, "D3 D1 D5 D2 D4 + A*")]


# ----------------------------------------------------------------------------- running one catalogue case
def load_catalogue():
    with open(CATALOGUE, encoding="utf-8") as f:
        return json.load(f)


def build(case, cat, cache={}):
    """Turn a catalogue case into integer ids: (n, roads, coords, src, dst, updates, names)."""
    spec = cat["networks"][case["network"]]
    if "grid" in spec:
        key = tuple(spec["grid"])
        if key not in cache:
            cache[key] = city_grid(*spec["grid"])
        n, roads, coords = cache[key]
        updates = daily_feed(roads) if case.get("feed") else []
        return n, roads, coords, case["query"][0], case["query"][1], updates, None
    names = list(spec.get("junctions", []))
    for u, v, *_ in spec["roads"]:
        for x in (u, v):
            if x not in names:
                names.append(x)
    ids = {x: i for i, x in enumerate(names)}
    unknown = lambda x: ids.get(x, len(names) + 7)               # noqa: E731  out-of-range id
    roads = []
    for u, v, w, two_way in spec["roads"]:
        roads.append((ids[u], ids[v], w))
        if two_way:
            roads.append((ids[v], ids[u], w))
    updates = [(unknown(u), unknown(v), w) for u, v, w in case.get("updates", [])]
    return len(names), roads, None, unknown(case["query"][0]), unknown(case["query"][1]), updates, names


def reference(n, roads, updates, src, dst):
    """Task 5's Dijkstra on the road list with the feed applied (closed roads removed)."""
    eff = apply_feed_to_list(roads, updates)
    dist, _ = dijkstra_heap(n, eff, src)
    return dist[dst], {(u, v): w for u, v, w in eff}


def run_case(cls, case, cat):
    """Returns (status, expected text, actual text, stats). status: PASS / FAIL / SKIP."""
    if case.get("fixed_only") and cls is not Final:
        return "SKIP", "", "final design only", Counter()
    n, roads, coords, src, dst, updates, names = build(case, cat)
    show = (lambda p: p) if names is None else (lambda p: [names[i] if i < len(names) else "?" for i in p])
    exp = case["expect"]
    eff = None
    if exp.get("reference"):
        rt, eff = reference(n, roads, updates, src, dst)
        exp_text = f"{rt} (reference)"
    elif exp.get("error"):
        exp_text = exp["error"]
    elif exp.get("unreachable"):
        exp_text = "inf, None"
    else:
        exp_text = f"{exp['time']}, {'-'.join(exp['path'])}"
    stats = Counter()
    try:
        svc = cls(n, roads, coords) if cls is Final else cls(n, roads)
        svc.stats = Watchdog(20 * n + 100)
        if updates:
            svc.apply_daily_update(updates)
        methods = ["dijkstra", "astar"] if case.get("method") == "both" else [case.get("method", "dijkstra")]
        results = []
        for m in methods:
            svc.stats = Watchdog(20 * n + 100)
            t0 = time.perf_counter()
            res = svc.route(src, dst, m) if cls is Final else svc.route(src, dst)
            results.append((res, time.perf_counter() - t0))
            stats = svc.stats
        (t, path), secs = results[0]
        actual = f"{t}, {'None' if path is None else '-'.join(map(str, show(path)))}"
    except Exception as e:                                        # crashes are results too
        return ("PASS" if exp.get("error") == type(e).__name__ else "FAIL"), exp_text, \
            f"{type(e).__name__}: {e}"[:60], stats
    if exp.get("error"):
        return "FAIL", exp_text, actual[:60], stats
    if exp.get("unreachable"):
        ok = t == INF and path is None
    elif exp.get("reference"):
        ok = all(r[0] == rt for r, _ in results)
        for (rt_i, p), _ in results:
            ok &= p is not None and p[0] == src and p[-1] == dst and \
                all((a, b) in eff for a, b in zip(p, p[1:])) and sum(eff[(a, b)] for a, b in zip(p, p[1:])) == rt
        ok &= all(s <= case.get("max_seconds", INF) for _, s in results)
        actual = f"{t}, path of {len(path) if path else 0} junctions"
    else:
        ok = t == exp["time"] and path is not None and show(path) == exp["path"]
    if "max_expansions" in case:
        lim = n if case["max_expansions"] == "V" else case["max_expansions"]
        ok &= stats["expansions"] <= lim
        actual += f"; exp {stats['expansions']}"
    if "max_road_scans" in case:
        ok &= stats["road_scans"] <= len(roads)
        actual += f"; scans {stats['road_scans']:,}"
    return ("PASS" if ok else "FAIL"), exp_text, actual[:60], stats


# ----------------------------------------------------------------------------- the session
def small(cat, net):
    """Integer version of a named catalogue network (for the isolation experiments)."""
    n, roads, _, _, _, _, names = build({"network": net, "query": [None, None]}, cat)
    return n, roads, {x: i for i, x in enumerate(names)}, names


def isolate(cat):
    """Minimal reproductions; returns the measured facts used in the defect table."""
    facts = {}
    print("\n2. ISOLATE - minimal reproductions (instrumented)")
    n, roads, ids, nm = small(cat, "G1")
    g = Given(n, roads)
    t, p = g.route(ids["H"], ids["G"])
    facts["D3"] = f"{'-'.join(nm[i] for i in p)}; KeyError"
    print(f"  D3 given route(H, G) returns path {'-'.join(nm[i] for i in p)}: _path() collects dst..first hop, never adds")
    print("     src and never reverses; for an unreachable dst 'v = prev[v]' raises KeyError (the desk crashes).")
    v1 = V1(n, roads)
    t, p = v1.route(ids["H"], ids["A"])
    facts["D1"] = f"{t}, {'-'.join(nm[i] for i in p)}"
    print(f"  D1 V1 route(H, A) = {t} min via {'-'.join(nm[i] for i in p)}: the first expansion (H) relaxes H->A = 4 and")
    print("     returns at once ('if v == dst: return' inside the relaxation loop); B is never expanded, H-B-A = 3 missed.")
    v2 = V2(n, roads)
    v2.apply_daily_update([(ids["C"], ids["D"], -1), (ids["D"], ids["C"], -1)])
    t, p = v2.route(ids["H"], ids["D"])
    facts["D5"] = f"{t} via closed road"
    print(f"  D5 V2 after the feed closes C-D: roads {[(nm[u], nm[v], w) for u, v, w in v2.roads if w < 0]} - the closure")
    print(f"     code became a travel time; route(H, D) = {t} min via {'-'.join(nm[i] for i in p)} (uses the closed road).")
    n2, roads2, ids2, _ = small(cat, "NEG")
    v2n = V2(n2, roads2)
    v2n.stats = Watchdog(1000)
    try:
        v2n.route(ids2["H"], ids2["B"])
    except RuntimeError as e:
        print(f"     Network NEG (H-A = -2 both ways) is a negative cycle: V2 never stops -> {e}.")
    n3, roads3, ids3, _ = small(cat, "RI")
    v3 = V3(n3, roads3)
    v3.route(ids3["s"], ids3["Z"])
    facts["D2"] = f"{v3.stats['expansions']} expansions"
    print(f"  D2 V3 on network RI (7 reachable junctions): {v3.stats['expansions']} expansions - x and t are expanded again")
    print("     from stale heap entries (x is pushed 3 times, t twice); there is no 'if d > dist[u]: continue'.")
    n4, roads4, _, _, _, _, _ = build({"network": "GRID30", "query": [0, 899]}, cat)
    v4 = V4(n4, roads4)
    v4.route(0, 899)
    facts["D4"] = f"{v4.stats['road_scans']:,} scans"
    print(f"  D4 V4 on the 30 x 30 grid (E = {len(roads4):,}): {v4.stats['expansions']} expansions x {len(roads4):,} roads"
          f" = {v4.stats['road_scans']:,} road scans,")
    print("     because neighbours() (and apply_daily_update(), per feed record) scans the whole road list: O(V*E).")
    return facts


def main():
    cat = load_catalogue()
    cases = cat["cases"]
    print("TASK 6 - DEBUGGING THE GIVEN ROUTE SERVICE (reproduce -> isolate -> fix -> re-test)")
    print("=" * 118)
    print(f"1. REPRODUCE - {len(cases)} catalogue cases on the GIVEN code (V0)")
    print(f"  {'case':<6} {'category':<9} {'expected':<24} {'actual (given code)':<62} result")
    for c in cases:
        st, e, a, _ = run_case(Given, c, cat)
        print(f"  {c['id'][3:]:<6} {c['category']:<9} {e[:24]:<24} {a:<62} {st}")
    facts = isolate(cat)
    print("\n3-4. FIX one defect at a time and RE-TEST the whole catalogue after every fix")
    print(f"  {'version':<9} {'fixes applied':<22} {'PASS':>4} {'FAIL':>4} {'SKIP':>4}  failing cases")
    final_rows = None
    for name, cls, fixes in VERSIONS:
        res = [(c["id"][3:], run_case(cls, c, cat)) for c in cases]
        cnt = Counter(r[0] for _, r in res)
        fails = " ".join(i for i, r in res if r[0] == "FAIL") or "-"
        print(f"  {name:<9} {fixes:<22} {cnt['PASS']:>4} {cnt['FAIL']:>4} {cnt['SKIP']:>4}  {fails}")
        final_rows = res
    print("\n  FINAL design, scale cases:")
    for i, (st, e, a, s) in final_rows:
        if i in ("S5", "S6", "L1"):
            extra = "" if "exp " in a else f"; exp {s['expansions']:,}; scans {s['road_scans']:,}"
            print(f"    {i:<3} {st}  expected {e:<18} actual {a}{extra}")
    print("\nDefect table (actual = measured on the version just before the fix; all fixed in FINAL)")
    rows = [("D1", "G2: 3, H-B-A", facts["D1"], "returns when dst is discovered", "return when dst is popped"),
            ("D2", "S1: <= 7 expansions", facts["D2"], "no stale-entry check", "skip if d > dist[u]"),
            ("D3", "G1: H-B-A-C-D-F-G", facts["D3"], "path not reversed, src missing", "walk back, add src, reverse"),
            ("D4", "S5: scans <= 3,330", facts["D4"], "linear scan of the road list", "adjacency lists + road index"),
            ("D5", "G3: 12, H-B-D", facts["D5"], "feed and ids not validated", "validate; -1 = closed (INF)")]
    print(f"  {'id':<3} {'expected':<20} {'actual':<20} {'root cause':<31} fix")
    for r in rows:
        print(f"  {r[0]:<3} {r[1]:<20} {r[2]:<20} {r[3]:<31} {r[4]}")


if __name__ == "__main__":
    main()
