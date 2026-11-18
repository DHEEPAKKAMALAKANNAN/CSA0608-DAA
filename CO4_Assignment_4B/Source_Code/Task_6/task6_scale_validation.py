"""
Task 6 - optimisation evidence and large-input validation for the changed requirement
(100,000 junctions, travel times replaced by a feed every night).

E1  Why the teammate's data structure cannot scale: V4 (all correctness defects fixed, but still the linear
    road-list scans of D4) against the FINAL design on growing city grids - road scans, feed cost and time;
    the measured cost per road scan is used to extrapolate V4 to 100,000 junctions.
E2  FINAL design on 10,000 .. 100,000 junctions with the nightly feed applied: build time, feed time and
    10 random ambulance queries per size with Dijkstra (early exit) and A*; every answer is validated against
    Task 5's full Dijkstra on the same (feed-applied) road list, including the route length.
Writes results/task6_*.csv and results/task6_scale.png.
Run:  py -3 task6_scale_validation.py
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Task_5"))
from city_network import apply_feed_to_list, city_grid, daily_feed  # noqa: E402
from dijkstra_routing import dijkstra_heap  # noqa: E402
from fixed_route_service import RouteService as Final  # noqa: E402
from task6_debugging import V4  # noqa: E402

RES = os.path.join(HERE, "results")
SEED = 42


def write_csv(name, rows):
    with open(os.path.join(RES, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def e1_list_vs_adjacency(sides=(10, 20, 30, 40, 50)):
    rows = []
    print("E1  Teammate's road list (V4: correct, but linear scans) vs FINAL adjacency design, corner-to-corner query")
    print(f"    {'V':>6} {'E':>7} {'feed':>5} | {'V4 feed scans':>13} {'V4 route scans':>14} {'V4 ms':>8} | "
          f"{'FINAL feed ops':>14} {'FINAL scans':>11} {'FINAL ms':>8} | {'same':>4}")
    for side in sides:
        n, roads, coords = city_grid(side, side)
        feed = daily_feed(roads)
        v4 = V4(n, roads)
        t0 = time.perf_counter()
        v4.apply_daily_update(feed)
        feed_scans = v4.stats["road_scans"]
        r4 = v4.route(0, n - 1)
        t4 = (time.perf_counter() - t0) * 1e3
        route_scans = v4.stats["road_scans"] - feed_scans
        fin = Final(n, roads, coords)
        t0 = time.perf_counter()
        fin.apply_daily_update(feed)
        rf = fin.route(0, n - 1)
        tf = (time.perf_counter() - t0) * 1e3
        same = r4[0] == rf[0]
        rows.append(dict(V=n, E=len(roads), feed_records=len(feed), v4_feed_scans=feed_scans,
                         v4_route_scans=route_scans, v4_ms=round(t4, 1), final_feed_ops=len(feed),
                         final_route_scans=fin.stats["road_scans"], final_ms=round(tf, 2), same_time=same))
        print(f"    {n:>6,} {len(roads):>7,} {len(feed):>5} | {feed_scans:>13,} {route_scans:>14,} {t4:>8.1f} | "
              f"{len(feed):>14,} {fin.stats['road_scans']:>11,} {tf:>8.2f} | {str(same):>4}")
    big = rows[-1]
    ns_per_scan = big["v4_ms"] * 1e6 / (big["v4_feed_scans"] + big["v4_route_scans"])
    write_csv("task6_01_list_vs_adjacency.csv", rows)
    return rows, ns_per_scan


def e2_final_at_scale(shapes=((100, 100), (160, 160), (200, 250), (250, 400)), queries=10):
    rng = random.Random(SEED)
    rows = []
    print("\nE2  FINAL design with the nightly feed: build + feed + 10 random queries per size (validated vs Task 5)")
    print(f"    {'V':>7} {'E':>7} {'build ms':>8} {'feed ms':>7} | {'Dijkstra exp':>12} {'ms':>6} | {'A* exp':>8} "
          f"{'ms':>6} {'A* saves':>8} | {'full SSSP ms':>12} | {'valid':>5}")
    for rows_, cols in shapes:
        n, roads, coords = city_grid(rows_, cols)
        feed = daily_feed(roads)
        t0 = time.perf_counter(); svc = Final(n, roads, coords); tb = (time.perf_counter() - t0) * 1e3
        t0 = time.perf_counter(); svc.apply_daily_update(feed); tfeed = (time.perf_counter() - t0) * 1e3
        eff = apply_feed_to_list(roads, feed)
        w = {(u, v): x for u, v, x in eff}
        dexp, dms, aexp, ams, fms, valid = [], [], [], [], [], 0
        for _ in range(queries):
            s, t = rng.randrange(n), rng.randrange(n)
            t0 = time.perf_counter(); ref, _ = dijkstra_heap(n, eff, s); fms.append((time.perf_counter() - t0) * 1e3)
            ok = True
            for method, exps, mss in (("dijkstra", dexp, dms), ("astar", aexp, ams)):
                svc.stats.clear()
                t0 = time.perf_counter(); tt, path = svc.route(s, t, method); mss.append((time.perf_counter() - t0) * 1e3)
                exps.append(svc.stats["expansions"])
                ok &= tt == ref[t]
                if path is not None:
                    ok &= path[0] == s and path[-1] == t and sum(w[(a, b)] for a, b in zip(path, path[1:])) == tt
            valid += ok
        row = dict(V=n, E=len(roads), feed_records=len(feed), build_ms=round(tb, 1), feed_ms=round(tfeed, 1),
                   dijkstra_expansions_median=statistics.median(dexp), dijkstra_ms_median=round(statistics.median(dms), 1),
                   astar_expansions_median=statistics.median(aexp), astar_ms_median=round(statistics.median(ams), 1),
                   astar_saving_pct=round(100 * (1 - sum(aexp) / sum(dexp)), 1),
                   full_sssp_ms_median=round(statistics.median(fms), 1), queries=queries, valid=valid)
        rows.append(row)
        print(f"    {n:>7,} {len(roads):>7,} {tb:>8.1f} {tfeed:>7.1f} | {row['dijkstra_expansions_median']:>12,.0f} "
              f"{row['dijkstra_ms_median']:>6.1f} | {row['astar_expansions_median']:>8,.0f} {row['astar_ms_median']:>6.1f} "
              f"{row['astar_saving_pct']:>7.1f}% | {row['full_sssp_ms_median']:>12.1f} | {valid:>2}/{queries}")
    write_csv("task6_02_final_at_scale.csv", rows)
    return rows


def plot(r1, est, r2):
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.4))
    v = [r["V"] for r in r1]
    ax[0].loglog(v, [r["v4_feed_scans"] + r["v4_route_scans"] for r in r1], "s-", label="road list (V4): feed + query")
    ax[0].loglog(v, [r["final_feed_ops"] + r["final_route_scans"] for r in r1], "o-",
                 label="adjacency + index (FINAL)")
    ax[0].loglog([r2[-1]["V"]], [est], "rx", ms=9, label="V4 extrapolated (feed + median query)")
    ax[0].loglog([r["V"] for r in r2], [r["feed_records"] + r["E"] for r in r2], "o--", color="#2E7D32",
                 label="FINAL bound (feed + E) at scale")
    ax[0].set_xlabel("junctions V"); ax[0].set_ylabel("road scans + feed operations (count)")
    ax[0].set_title("E1: data structure (teammate vs final)"); ax[0].legend(fontsize=7)
    ax[0].grid(True, which="both", alpha=0.3)
    v2 = [r["V"] for r in r2]
    ax[1].plot(v2, [r["dijkstra_ms_median"] for r in r2], "o-", label="Dijkstra, early exit (median)")
    ax[1].plot(v2, [r["astar_ms_median"] for r in r2], "^-", label="A* (median)")
    ax[1].plot(v2, [r["full_sssp_ms_median"] for r in r2], "s:", label="full single-source Dijkstra (Task 5)")
    ax[1].plot(v2, [r["build_ms"] + r["feed_ms"] for r in r2], "d--", label="nightly rebuild + feed")
    ax[1].set_xlabel("junctions V"); ax[1].set_ylabel("time (ms)")
    ax[1].set_title("E2: final design at scale"); ax[1].legend(fontsize=7); ax[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "task6_scale.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(RES, exist_ok=True)
    print("TASK 6 - OPTIMISATION AND LARGE-INPUT VALIDATION (seed 42)")
    print("=" * 120)
    r1, ns_per_scan = e1_list_vs_adjacency()
    r2 = e2_final_at_scale()
    big = r2[-1]
    feed_scans = big["feed_records"] * big["E"]
    query_scans = big["dijkstra_expansions_median"] * big["E"]
    est = (feed_scans + query_scans) * ns_per_scan / 1e9
    print(f"\nE3  Extrapolation of V4 to {big['V']:,} junctions at the measured {ns_per_scan:.0f} ns per road scan:")
    print(f"    feed {big['feed_records']:,} records x {big['E']:,} roads = {feed_scans:.2e} scans; median "
          f"query {big['dijkstra_expansions_median']:,.0f} expansions x {big['E']:,} = {query_scans:.2e} scans")
    print(f"    -> about {est / 3600:.1f} hours for one feed + one query, against "
          f"{(big['build_ms'] + big['feed_ms'] + big['dijkstra_ms_median']) / 1e3:.2f} s for the FINAL design "
          f"(rebuild + feed + median query).")
    write_csv("task6_03_extrapolation.csv", [dict(V=big["V"], E=big["E"], feed_records=big["feed_records"],
                                                  ns_per_scan=round(ns_per_scan, 1), v4_feed_scans=feed_scans,
                                                  v4_query_scans=query_scans, v4_estimated_hours=round(est / 3600, 2),
                                                  final_seconds=round((big["build_ms"] + big["feed_ms"] +
                                                                       big["dijkstra_ms_median"]) / 1e3, 3))])
    plot(r1, (feed_scans + query_scans), r2)
    print("\nWrote results/task6_01..03_*.csv and results/task6_scale.png")


if __name__ == "__main__":
    main()
