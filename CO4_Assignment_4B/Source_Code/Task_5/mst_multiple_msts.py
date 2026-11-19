"""
Task 5 - "Stress the design": modify selected link costs so that several MSTs with the same total cost exist,
then check whether Kruskal, Prim and Boruvka return DIFFERENT edge sets that are all still correct.

The prediction is printed BEFORE any algorithm runs. Every returned tree is then validated independently:
spanning (n-1 edges, no cycle), cost = brute-force minimum, cut property and cycle property; and all MSTs of
the modified network are enumerated exhaustively.
Inputs: test_data/facility_network.csv (original), test_data/facility_network_ties.csv (modified costs).
Writes results/t5_multiple_msts.csv and results/t5_all_msts.csv.
Run:  py -3 mst_multiple_msts.py
"""
import csv
import os

from mst_engines import (Network, boruvka, canonical, cut_property_holds, cycle_property_holds,
                         enumerate_msts, is_spanning_tree, kruskal, prim)

HERE = os.path.dirname(os.path.abspath(__file__))
TIE_GROUPS = [("HQ-WH", "WH-FA"), ("DC-PT", "LB-SC"), ("FA-FB", "FB-LB")]   # the equal-cost alternatives


def labels(net, edge_set):
    return {f"{net.names[u]}-{net.names[v]}" for u, v, _ in edge_set} | \
           {f"{net.names[v]}-{net.names[u]}" for u, v, _ in edge_set}


def tie_choices(net, edge_set):
    got = labels(net, edge_set)
    return [a if a in got else b for a, b in TIE_GROUPS]


def write_csv(name, rows):
    with open(os.path.join(HERE, "results", name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    base = Network.from_csv(os.path.join(HERE, "test_data", "facility_network.csv"))
    net = Network.from_csv(os.path.join(HERE, "test_data", "facility_network_ties.csv"))
    print("TASK 5 - STRESS THE DESIGN: equal-cost alternatives -> multiple MSTs (costs in Rs lakh)")
    print("=" * 108)
    print("Modified links (each now EQUALS the heaviest tree edge on the cycle it closes):")
    for (a, b, w0), (_, _, w1) in zip(base.edges, net.edges):
        if w0 != w1:
            e = (a, b, w1)
            print(f"   {net.edge_label(e):<6} {w0:>3} -> {w1:<3}")
    print("   cycles: HQ-DC-FA-WH (WH-FA 6 vs HQ-WH 6); DC-FA-LB-SC-RS-PT (DC-PT 7 vs LB-SC 7); "
          "FA-FB-LB (FA-FB 10 vs FB-LB 10)")

    print("\nPREDICTION (recorded before running):")
    print("   P1 total cost stays 38: a modified link only TIES the edge it can replace, it is never cheaper.")
    print("   P2 number of MSTs = 2 x 2 x 2 = 8 (three independent cycles, each with two tied heaviest edges).")
    print("   P3 the algorithms can return DIFFERENT edge sets: each breaks ties by a different rule -")
    print("      Kruskal by input order of equal costs, Prim by discovery order from its root, Boruvka by (cost, u, v).")
    print("   P4 every returned tree is still a correct MST (spanning, minimum, cut + cycle property hold).")

    print("\nOBSERVED")
    best, all_msts = enumerate_msts(net.n, net.edges)
    runs = [kruskal(net.n, net.edges), prim(net.n, net.edges, 0), boruvka(net.n, net.edges)]
    print(f"  {'algorithm':<14} {'cost':>4}  {'tie 1':<6} {'tie 2':<6} {'tie 3':<6} {'spanning':>8} {'=min':>5} "
          f"{'cut':>5} {'cycle':>5}  edge set")
    rows = []
    for res in runs:
        name = res.algorithm.replace("root=0", "root=HQ")
        t = tie_choices(net, res.edges)
        checks = (is_spanning_tree(net.n, res.edges), res.total == best,
                  cut_property_holds(net.n, net.edges, res.edges), cycle_property_holds(net.n, net.edges, res.edges))
        print(f"  {name:<14} {res.total:>4}  {t[0]:<6} {t[1]:<6} {t[2]:<6} " +
              " ".join(f"{str(c):>{wd}}" for c, wd in zip(checks, (8, 5, 5, 5))) +
              "  " + " ".join(sorted(net.edge_label(e) for e in res.edges)))
        rows.append(dict(algorithm=name, cost=res.total, tie1=t[0], tie2=t[1], tie3=t[2], spanning=checks[0],
                         minimum=checks[1], cut_property=checks[2], cycle_property=checks[3],
                         edges=" ".join(sorted(net.edge_label(e) for e in res.edges))))
    distinct = {canonical(r.edges) for r in runs}
    print(f"  -> {len(distinct)} different edge sets from the three algorithms, all with cost {best}")

    print("\n  Prim from every root (same algorithm, different start = different tie exposure):")
    prim_sets = {}
    for root in range(net.n):
        res = prim(net.n, net.edges, root)
        prim_sets.setdefault(canonical(res.edges), []).append(net.names[root])
    for k, (s, roots) in enumerate(prim_sets.items(), 1):
        print(f"    tree P{k}: roots {', '.join(roots):<14} ties chosen {', '.join(tie_choices(net, s))}")

    print(f"\n  Exhaustive enumeration: {len(all_msts)} distinct MSTs, each of cost {best}")
    returned = {canonical(r.edges): r.algorithm.split("(")[0] for r in runs}
    all_rows = []
    for k, s in enumerate(all_msts, 1):
        t = tie_choices(net, s)
        who = returned.get(s, "")
        print(f"    MST {k}: {t[0]:<6} {t[1]:<6} {t[2]:<6}  cost {sum(e[2] for e in s)}  {who}")
        all_rows.append(dict(mst=k, tie1=t[0], tie2=t[1], tie3=t[2], cost=sum(e[2] for e in s),
                             returned_by=who))

    print("\nPREDICTION vs OBSERVATION")
    print(f"   P1 cost 38              -> observed {sorted({r.total for r in runs})}  "
          f"{'CONFIRMED' if all(r.total == 38 for r in runs) else 'REFUTED'}")
    print(f"   P2 8 MSTs               -> observed {len(all_msts)}  {'CONFIRMED' if len(all_msts) == 8 else 'REFUTED'}")
    print(f"   P3 different edge sets  -> observed {len(distinct)} distinct sets  "
          f"{'CONFIRMED' if len(distinct) > 1 else 'REFUTED'}")
    print(f"   P4 all correct          -> {'CONFIRMED' if all(all(list(r.values())[5:9]) for r in rows) else 'REFUTED'}")
    print("Conclusion: an MST is unique only when costs are distinct; with ties, 'correct' means minimum TOTAL cost,")
    print("not a particular edge set - so regression tests must compare cost + validity, never exact edge lists.")
    write_csv("t5_multiple_msts.csv", rows)
    write_csv("t5_all_msts.csv", all_rows)


if __name__ == "__main__":
    main()
