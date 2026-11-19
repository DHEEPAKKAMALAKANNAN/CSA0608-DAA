"""
Task 3, Stage B - Introduce a carefully selected negative edge: P -> D with cost -5.

Business story: the Port Terminal pays a backhaul credit for every truck that carries empty containers from
the Port to the Dockyard, so the net cost of road P->D is -5. The edge is chosen so that it is RELEVANT:
P is far from the hub (13) and is finalised by Dijkstra only AFTER the Dockyard D (10), yet P->D offers D a
cheaper cost 13 - 5 = 8. No cycle passes through P (P has a single incoming road from H), so shortest paths
are still well defined and Bellman-Ford must find them.
The PREDICTION is printed before any algorithm is executed. Writes results/t3_stage_b_comparison.csv.
Run:  py -3 stage_b_negative_edge.py
"""
from collections import Counter

from routing_engine import bellman_ford, dijkstra, floyd, path_to, shortest_paths
from routing_io import fmt, modified_network, print_header, print_wrapped, route_text, write_csv

SOURCE = "H"
PREDICTED_AFFECTED = ["D", "E", "F", "G", "R"]


def print_prediction():
    print("PREDICTION (recorded before execution):")
    print("  1. Dijkstra will NOT remain valid: D is finalised at 10 (step 5) before P (13); when P is finalised")
    print("     the cheaper offer 13 + (-5) = 8 for D arrives too late and is refused by the greedy invariant.")
    print("  2. Affected decisions: D and every depot whose best route runs through D -> D, E, F, G, R.")
    print("     The Retail Park route should change from H-B-A-C-D-E-F-G-R (19) to H-P-D-E-F-G-R (17).")
    print("  3. Unaffected: H, A, B, C, P (their best routes never use P->D).")
    print("  4. Bellman-Ford (no greedy commitment, repeated relaxation of all edges) will return the true values.")


def main():
    g, extra = modified_network("stage_b_negative_edge.csv")
    print_header("TASK 3 / STAGE B - A NEGATIVE EDGE P->D = -5 (backhaul credit)")
    print(f"Modification: add {', '.join(f'{u}->{v} {w}' for u, v, w in extra)};  network now has {len(g.edges)} "
          f"roads; has_negative_edge() = {g.has_negative_edge()}\n")
    print_prediction()

    s = g.vertex(SOURCE)
    dops, trace = Counter(), []
    ddist, dpred, order = dijkstra(g, SOURCE, dops, trace)
    print("\nEXECUTION 1 - Dijkstra run exactly as written (finalised vertices are never reopened)")
    first_wrong = None
    for k, step in enumerate(trace, 1):
        rel = ", ".join(f"{g.names[v]}:{fmt(o)}->{fmt(n)}" for v, o, n in step["relaxed"]) or "-"
        ref = "; ".join(f"REFUSED {g.names[v]}: {fmt(c)} < final {fmt(f)}" for v, c, f in step["refused"])
        print(f"  {k:>2}  finalise {g.names[step['vertex']]} = {fmt(step['dist']):>2}   {rel}   {ref}".rstrip())
        if step["refused"] and first_wrong is None:
            first_wrong = (k, step)

    bops = Counter()
    bf = bellman_ford(g, SOURCE, bops)
    print("\nEXECUTION 2 - Bellman-Ford: distance vector after each pass over all 20 edges (input order)")
    print("  pass " + "".join(f"{c:>5}" for c in g.names) + "   updates in this pass")
    for p in bf.pass_log:
        print(f"  {p['pass']:>4} " + "".join(f"{fmt(d):>5}" for d in p["dist"]) + f"   {len(p['updates'])}")
    for p in bf.pass_log:
        ups = [f"{g.names[v]}:{fmt(o)}->{fmt(n)} via {g.names[u]}" for v, o, n, u in p["updates"]]
        print_wrapped(f"  pass {p['pass']} relaxations: ", ups or ["none -> early exit"])
    print(f"  detection pass: no edge relaxes -> no negative cycle (negative_cycle = {bf.negative_cycle})")

    fl = floyd(g)
    print("\nComparison from H (Floyd's row H as an independent third opinion)")
    print(f"  {'depot':<5} {'Dijkstra':>8} {'Bellman-Ford':>12} {'Floyd':>6}  {'Dijkstra path':<19} "
          f"{'Bellman-Ford path':<17}")
    rows, observed = [], []
    for v in range(g.n):
        dp, bp = path_to(dpred, s, v), path_to(bf.pred, s, v)
        dtxt, btxt = route_text(g, dp, "-"), route_text(g, bp, "-")
        flag = "" if ddist[v] == bf.dist[v] else "  <-- WRONG"
        if flag:
            observed.append(g.names[v])
        print(f"  {g.names[v]:<5} {fmt(ddist[v]):>8} {fmt(bf.dist[v]):>12} {fmt(fl.dist[s][v]):>6}  "
              f"{dtxt:<19} {btxt:<17}{flag}".rstrip())
        rows.append([g.names[v], fmt(ddist[v]), fmt(bf.dist[v]), fmt(fl.dist[s][v]), dtxt, btxt,
                     "yes" if flag else "no"])
    write_csv("t3_stage_b_comparison.csv", ["depot", "dijkstra", "bellman_ford", "floyd", "dijkstra_path",
                                            "bellman_ford_path", "dijkstra_wrong"], rows)

    k, step = first_wrong
    v, cand, final = step["refused"][0]
    print(f"\nFirst wrong finalisation: {g.names[v]} finalised at step {order.index(v) + 1} with {fmt(final)}; "
          f"at step {k} (finalising {g.names[step['vertex']]}) the route via P->D costs {fmt(cand)}, "
          f"but D is already closed.")
    print(f"Prediction check: predicted affected {PREDICTED_AFFECTED}, observed wrong {observed} -> "
          f"{'CONFIRMED' if observed == PREDICTED_AFFECTED else 'NOT confirmed'}")
    print(f"Work: Dijkstra {dops['edge_relaxations']} relaxations;  "
          f"Bellman-Ford {bops['edge_relaxations']} relaxations in {len(bf.pass_log)} passes "
          f"+ {bops['detection_checks']} detection checks")
    algo, dist, _ = shortest_paths(g, SOURCE)
    print(f"Production facade shortest_paths(): negative edge detected -> uses {algo}; "
          f"dist(H, R) = {fmt(dist[g.vertex('R')])}")


if __name__ == "__main__":
    main()
