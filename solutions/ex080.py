# Exercise 80 - Is the given MST unique? (and find another MST if not)
# Idea: for a valid MST T, T is the ONLY MST iff every non-tree edge (u, v, w) is strictly heavier
# than every tree edge on the T-path u..v.  If some tree edge on that path has weight == w,
# swapping the two edges gives a different spanning tree of the same (minimum) weight.

def key(e):
    return (min(e[0], e[1]), max(e[0], e[1]), e[2])          # undirected edge identity


def kruskal_weight(n, edges):
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    total = 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
    return total


def tree_path(n, tree, src, dst):
    """Edges of the unique path src -> dst inside the tree (DFS)."""
    adj = {i: [] for i in range(n)}
    for e in tree:
        adj[e[0]].append((e[1], e))
        adj[e[1]].append((e[0], e))
    stack, seen = [(src, [])], {src}
    while stack:
        node, path = stack.pop()
        if node == dst:
            return path
        for nxt, e in adj[node]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append((nxt, path + [e]))
    return None                                              # not connected


def check_mst_uniqueness(n, edges, given):
    """Return (is_valid_mst, is_unique, another_mst_or_None)."""
    graph_keys = {key(e) for e in edges}
    if len(given) != n - 1 or any(key(e) not in graph_keys for e in given):
        return False, False, None
    if sum(e[2] for e in given) != kruskal_weight(n, edges):
        return False, False, None                            # not minimum weight
    if any(tree_path(n, given, 0, v) is None for v in range(n)):
        return False, False, None                            # not spanning
    tree_keys = {key(e) for e in given}
    for u, v, w in edges:
        if key((u, v, w)) in tree_keys:
            continue
        path = tree_path(n, given, u, v)
        for old in path:
            if old[2] == w:                                  # tie -> swap gives another MST
                return True, False, [(u, v, w) if e == old else e for e in given]
    return True, True, None


def run_test(number, n, edges, given, exp_unique, exp_other=None):
    valid, unique, other = check_mst_uniqueness(n, edges, given)
    print(f"Test Case {number}")
    print(f"Input   : n = {n}, m = {len(edges)}")
    print(f"          edges = {edges}")
    print(f"          given_mst = {given}")
    print(f"Output  : Given tree is a valid MST? {valid}")
    print(f"          Is the given MST unique? {unique}")
    if other:
        print(f"          Another possible MST: {other}")
        print(f"          Total weight of MST: {sum(e[2] for e in other)}")
    if unique == exp_unique and other == exp_other:          # compare with the document
        print(f"Expected: Is the given MST unique? {exp_unique}")
        if exp_other:
            print(f"          Another possible MST: {exp_other}")
    else:
        print(f"Note    : document lists unique={exp_unique}, another={exp_other}; "
              f"correct value is unique={unique}, another={other}")
    print()


if __name__ == "__main__":
    run_test(1, 4, [(0, 1, 10), (0, 2, 6), (0, 3, 5), (1, 3, 15), (2, 3, 4)],
             [(2, 3, 4), (0, 3, 5), (0, 1, 10)], True)
    run_test(2, 5, [(0, 1, 1), (0, 2, 1), (1, 3, 2), (2, 3, 2), (3, 4, 3), (4, 2, 3)],
             [(0, 1, 1), (0, 2, 1), (1, 3, 2), (3, 4, 3)], False,
             [(0, 1, 1), (0, 2, 1), (2, 3, 2), (3, 4, 3)])
