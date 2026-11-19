"""
Task 3, Stage C - Production failure: a reachable negative-weight cycle.

A mis-keyed contract loads road E -> C with cost -9 (base network otherwise unchanged). Together with C->D (2)
and D->E (2) it forms the cycle C -> D -> E -> C of total weight -5, reachable from the hub H. Every lap
lowers the cost by 5, so "shortest" distances to C, D, E and to everything reachable from them do not exist.
The engine must DETECT and REPORT this instead of returning misleading numbers:
  * Bellman-Ford: after |V|-1 passes, one more pass; an edge that still relaxes is a witness. Walking the
    predecessor chain |V| steps back from the witness lands on the cycle, which is then listed.
  * Floyd: a negative diagonal entry D[i][i] < 0 marks every vertex that lies on a negative closed walk.
  * Dijkstra is shown only to demonstrate the misleading finite answer it would give.
Writes results/t3_stage_c_detection.csv.  Run:  py -3 stage_c_negative_cycle.py
"""
from collections import Counter

from routing_engine import NegativeCycleError, bellman_ford, dijkstra, floyd, shortest_paths
from routing_io import fmt, modified_network, print_header, print_wrapped, write_csv

SOURCE = "H"


def main():
    g, extra = modified_network("stage_c_negative_cycle.csv")
    print_header("TASK 3 / STAGE C - PRODUCTION FAILURE: REACHABLE NEGATIVE CYCLE")
    print(f"Modification: add {', '.join(f'{u}->{v} {w}' for u, v, w in extra)} to the base network "
          f"({len(g.edges)} roads).  Cycle C->D->E->C = 2 + 2 + (-9) = -5")
    print("PREDICTION (recorded before execution): Bellman-Ford will still be relaxing edges in pass |V|-1 = 9,")
    print("  the detection pass will find a witness edge and report the cycle C, D, E; every depot reachable from")
    print("  the cycle (B, A, C, D, E, F, G, R) has NO shortest path; only H (0) and P (13) remain well defined.\n")

    ops = Counter()
    res = bellman_ford(g, SOURCE, ops)
    print("Bellman-Ford distance vector after each pass (never stabilises -> no early exit)")
    print("  pass " + "".join(f"{c:>5}" for c in g.names) + "   updates")
    for p in res.pass_log:
        print(f"  {p['pass']:>4} " + "".join(f"{fmt(d):>5}" for d in p["dist"]) + f"   {len(p['updates'])}")
    last = res.pass_log[-1]
    print_wrapped(f"  pass {last['pass']} (= |V|-1) still relaxes: ",
                  [f"{g.names[v]}:{fmt(o)}->{fmt(n)} via {g.names[u]}" for v, o, n, u in last["updates"]])
    print(f"  detection pass (pass {g.n}): {ops['detection_checks']} edge checks until the first witness")
    cyc = [g.names[v] for v in res.negative_cycle]
    print(f"\nDETECTED: negative cycle {' -> '.join(cyc + cyc[:1])}, total weight {res.cycle_weight}")
    print(f"  affected depots (reachable from the cycle): {sorted(g.names[v] for v in res.affected)}")

    print("\nReturned result - Bellman-Ford (safe) vs Dijkstra (misleading) from H")
    dd, _, _ = dijkstra(g, SOURCE)
    print(f"  {'depot':<5} {'Bellman-Ford result':<34} {'Dijkstra would print':>20}")
    rows = []
    for v in range(g.n):
        status = "undefined (-inf): negative cycle" if v in res.affected else f"{fmt(res.dist[v])} (valid)"
        print(f"  {g.names[v]:<5} {status:<34} {fmt(dd[v]):>20}{'   misleading' if v in res.affected else ''}")
        rows.append([g.names[v], fmt(res.dist[v]), "yes" if v in res.affected else "no", fmt(dd[v])])
    write_csv("t3_stage_c_detection.csv", ["depot", "bellman_ford", "affected_by_cycle", "dijkstra_misleading"],
              rows)

    fl = floyd(g)
    print(f"\nFloyd check: negative diagonal entries D[i][i] < 0 for "
          f"{', '.join(f'{g.names[i]} ({fmt(fl.dist[i][i])})' for i in fl.negative_vertices)}")
    print("  -> the cycle vertices are flagged; the values themselves are meaningless (E already shows two laps),")
    print("     so the all-pairs matrix must be rejected, not reported.")
    try:
        shortest_paths(g, SOURCE)
        print("Production facade: returned distances (WRONG - should have raised)")
    except NegativeCycleError as exc:
        print(f"Production facade shortest_paths() raised NegativeCycleError: {exc}")
    print(f"Work: {ops['edge_relaxations']} relaxations in {len(res.pass_log)} passes (= |V|-1) "
          f"+ {ops['detection_checks']} detection checks")
    print("Why the check works: a shortest simple path has at most |V|-1 edges, so |V|-1 passes settle every")
    print("distance when no negative cycle is reachable; any improvement in pass |V| must use a repeated vertex,")
    print("i.e. a closed walk of negative weight.")


if __name__ == "__main__":
    main()
