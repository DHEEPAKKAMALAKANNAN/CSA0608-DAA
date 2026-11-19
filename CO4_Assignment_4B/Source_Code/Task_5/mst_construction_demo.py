"""
Task 5 - "Do not compare only the final cost": construction traces of Kruskal, Prim and Boruvka on the SAME
facility network (9 facilities, 15 candidate links, distinct costs in Rs lakh).

For every algorithm the program prints its next-safe-edge rule, the information it maintains, the step-by-step
growth of the partial solution, the final MST edges and the total cost; then it validates all three trees
against a brute-force search over every spanning tree and checks the cut property.
Input: test_data/facility_network.csv.   Writes results/t5_construction_summary.csv.
Run:  py -3 mst_construction_demo.py
"""
import csv
import math
import os

from mst_engines import (Network, boruvka, canonical, cut_property_holds, is_spanning_tree, kruskal,
                         mst_bruteforce, prim)

HERE = os.path.dirname(os.path.abspath(__file__))


def components_text(net, uf_members):
    return "{" + "+".join(net.names[v] for v in sorted(uf_members)) + "}"


def show_kruskal(net, res):
    print("\nKRUSKAL  next safe edge = globally lightest unexamined edge whose ends lie in DIFFERENT components")
    print("         maintains: edges sorted by cost + union-find (parent, rank) over facilities -> a FOREST")
    print(f"  {'step':>4} {'edge':<7} {'cost':>4} {'find(u)':>7} {'find(v)':>7}  {'decision':<17} {'components':>10}")
    for k, (e, ru, rv, dec, comps) in enumerate(res.trace, 1):
        why = "ACCEPT (merge)" if dec == "ACCEPT" else "REJECT (cycle)"
        print(f"  {k:>4} {net.edge_label(e):<7} {e[2]:>4} {net.names[ru]:>7} {net.names[rv]:>7}  {why:<17} {comps:>10}")
    print(f"  stopped after {len(res.trace)} of {len(net.edges)} edges (tree complete with n-1 = {net.n - 1} edges); "
          f"{res.ops['sort_comparisons']} sort comparisons, {res.ops['finds']} finds, "
          f"{res.ops['cycle_rejections']} cycle rejections")


def show_prim(net, res):
    print("\nPRIM     next safe edge = lightest edge with exactly ONE end in the tree (cut: tree | rest)")
    print("         maintains: key[v] (cheapest link to the tree), via[v], in_tree[], indexed min-heap -> ONE TREE")
    print(f"  {'step':>4} {'add':<4} {'via edge':<8} {'cost':>4} {'total':>5}  {'keys lowered after adding (v=key)':<40} "
          f"{'heap':>4}")
    for k, (u, e, total, updated, frontier) in enumerate(res.trace, 1):
        via = "(root)" if e is None else net.edge_label(e)
        low = ", ".join(f"{net.names[v]}={w}" for v, w, _ in updated) or "-"
        print(f"  {k:>4} {net.names[u]:<4} {via:<8} {e[2] if e else 0:>4} {total:>5}  {low:<40} {frontier:>4}")
    print(f"  {res.ops['heap_extracts']} extract-min, {res.ops['heap_inserts']} inserts, {res.ops['decrease_keys']} "
          f"decrease-keys, {res.ops['heap_comparisons']} heap comparisons, {res.ops['edge_scans']} adjacency scans")


def show_boruvka(net, res):
    print("\nBORUVKA  next safe edges = for EVERY component its cheapest outgoing edge, all added in the same round")
    print("         maintains: union-find of components + cheapest[component] per round -> components MERGE")
    for rnd, before, cheapest, added, after, scanned in res.trace:
        print(f"  round {rnd}: {before} components, {scanned} edges scanned; cheapest outgoing edge per component:")
        picks = [f"{components_text(net, m)}->{net.edge_label(e)}({e[2]})" for m, e in cheapest]
        for k in range(0, len(picks), 3):
            print("     " + "   ".join(picks[k:k + 3]))
        print(f"     added {len(added)}: {', '.join(net.edge_label(e) for e in added)}  ->  {after} component(s)")
    print(f"  {res.ops['rounds']} rounds (<= ceil(log2 {net.n}) = {math.ceil(math.log2(net.n))}), {res.ops['edge_scans']} edge scans, "
          f"{res.ops['finds']} finds, {res.ops['key_comparisons']} key comparisons")


def main():
    net = Network.from_csv(os.path.join(HERE, "test_data", "facility_network.csv"))
    print("TASK 5 - THREE GREEDY ENGINEERS, ONE NETWORK: construction traces (costs in Rs lakh)")
    print("=" * 112)
    print(f"Test input: {net.n} facilities {', '.join(net.names)}; {len(net.edges)} candidate links (distinct costs)")
    links = [f"{net.edge_label(e)}:{e[2]}" for e in net.edges]
    for k in range(0, len(links), 8):
        print("   " + "  ".join(links[k:k + 8]))
    print("Expected behaviour: costs are distinct -> the MST is UNIQUE, so all three must return the same 8 edges")
    print("and the same cost as an exhaustive search; only the ORDER in which edges are added should differ.")

    kr, pr, br = kruskal(net.n, net.edges), prim(net.n, net.edges, 0), boruvka(net.n, net.edges)
    show_kruskal(net, kr)
    show_prim(net, pr)
    show_boruvka(net, br)

    best, n_msts, n_trees = mst_bruteforce(net.n, net.edges)
    print("\nRESULT  (edges listed in the order each algorithm added them)")
    rows = []
    for res, growth in ((kr, "forest of merging trees"), (pr, "one tree grows from HQ"),
                        (br, "all components merge per round")):
        order = " ".join(net.edge_label(e) for e in res.edges)
        print(f"  {res.algorithm.replace('root=0', 'root=HQ'):<13} cost {res.total:>3}  {order}")
        rows.append(dict(algorithm=res.algorithm.replace("root=0", "root=HQ"), construction_order=order, total_cost=res.total,
                         edges=len(res.edges), partial_solution=growth,
                         valid_tree=is_spanning_tree(net.n, res.edges),
                         cut_property=cut_property_holds(net.n, net.edges, res.edges)))
    same = canonical(kr.edges) == canonical(pr.edges) == canonical(br.edges)
    print(f"Validation: brute force over {n_trees:,} spanning trees -> minimum {best}, {n_msts} MST(s); "
          f"Kruskal {kr.total} = Prim {pr.total} = Boruvka {br.total}: {kr.total == pr.total == br.total == best}")
    print(f"  identical edge sets: {same};  every tree spanning: {all(r['valid_tree'] for r in rows)};  "
          f"cut property holds: {all(r['cut_property'] for r in rows)}")
    with open(os.path.join(HERE, "results", "t5_construction_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
