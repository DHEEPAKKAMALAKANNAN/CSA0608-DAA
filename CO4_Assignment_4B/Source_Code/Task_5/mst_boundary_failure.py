"""
Task 5 - boundary and failure tests for the three MST engines.

Boundary cases (smallest networks, parallel links, self-loop, all-equal costs, a negative-cost subsidised
link) are checked against the brute-force reference. Failure cases: a DISCONNECTED network (no spanning tree
exists - each engine must report a minimum spanning forest / the unreached part, and the production policy
require_spanning_tree must refuse) and invalid inputs (unknown facility, NaN / non-numeric cost, no facilities).
Input: test_data/disconnected_network.csv.
Run:  py -3 mst_boundary_failure.py
"""
import os

from mst_engines import Network, boruvka, kruskal, mst_bruteforce, prim, require_spanning_tree

HERE = os.path.dirname(os.path.abspath(__file__))

BOUNDARY = [
    ("B1 one facility, no links", ["A"], []),
    ("B2 two facilities, one link", ["A", "B"], [(0, 1, 7)]),
    ("B3 parallel A-B (9 and 4) + self-loop B-B", ["A", "B", "C"], [(0, 1, 9), (0, 1, 4), (1, 1, 1), (1, 2, 5)]),
    ("B4 all four costs equal (K4, cost 3)", list("ABCD"), [(a, b, 3) for a in range(4) for b in range(a + 1, 4)]),
    ("B5 negative-cost subsidised link B-C = -2", list("ABCD"),
     [(0, 1, 4), (1, 2, -2), (2, 3, 6), (0, 3, 5), (0, 2, 3)]),
]


def main():
    print("TASK 5 - BOUNDARY AND FAILURE TESTS (Kruskal / Prim / Boruvka vs brute force)")
    print("=" * 104)
    print(f"  {'case':<44} {'Kruskal':>7} {'Prim':>5} {'Boruvka':>7} {'brute':>6} {'#MSTs':>6}  status")
    for name, names, edges in BOUNDARY:
        net = Network(names, edges)
        costs = [kruskal(net.n, net.edges).total, prim(net.n, net.edges).total, boruvka(net.n, net.edges).total]
        best, n_msts, _ = mst_bruteforce(net.n, net.edges)
        ok = all(c == best for c in costs)
        print(f"  {name:<44} {costs[0]:>7} {costs[1]:>5} {costs[2]:>7} {best:>6} {n_msts:>6}  {'PASS' if ok else 'FAIL'}")

    net = Network.from_csv(os.path.join(HERE, "test_data", "disconnected_network.csv"))
    print(f"\nF1 disconnected network: {net.n} facilities, links "
          + ", ".join(f"{net.edge_label(e)}:{e[2]}" for e in net.edges))
    print("   expected: no spanning tree exists -> report a spanning FOREST, never a misleading 'MST'")
    for res in (kruskal(net.n, net.edges), prim(net.n, net.edges, 0), boruvka(net.n, net.edges)):
        res = res._replace(algorithm=res.algorithm.replace("root=0", "root=HQ"))
        print(f"   {res.algorithm:<13} {len(res.edges)} edges, cost {res.total:>2}, components {res.components}: "
              + ", ".join(net.edge_label(e) for e in res.edges))
        try:
            require_spanning_tree(res)
            print("      require_spanning_tree -> accepted (WRONG)")
        except ValueError as exc:
            print(f"      require_spanning_tree -> ValueError: {exc}")
    print("   (Prim from HQ only reaches HQ's component; its other 'components' are the unreached facilities.)")

    print("\nF2 invalid inputs (must be rejected before any algorithm runs)")
    bad = [("unknown facility index 5", ["A", "B"], [(0, 5, 3)]),
           ("cost is NaN", ["A", "B"], [(0, 1, float("nan"))]),
           ("cost is a string", ["A", "B"], [(0, 1, "7")]),
           ("no facilities at all", [], [])]
    for name, names, edges in bad:
        try:
            Network(names, edges)
            print(f"   {name:<28} -> accepted (WRONG)")
        except ValueError as exc:
            print(f"   {name:<28} -> ValueError: {exc}")


if __name__ == "__main__":
    main()
