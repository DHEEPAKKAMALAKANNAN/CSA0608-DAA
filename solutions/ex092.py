# Exercise 92 - Hamiltonian cycle in an undirected graph (backtracking)
def build_adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def hamiltonian_cycle(n, edges):
    """Return a Hamiltonian cycle as a vertex list (start repeated at the end), or None."""
    adj = build_adjacency(n, edges)
    path = [0]

    def extend():
        if len(path) == n:
            return 0 in adj[path[-1]]          # last vertex must connect back to the start
        for v in adj[path[-1]]:
            if v not in path:
                path.append(v)
                if extend():
                    return True
                path.pop()                      # backtrack
        return False

    return path + [0] if extend() else None


def is_valid_cycle(n, edges, cycle):
    edge_set = {frozenset(e) for e in edges}
    steps = list(zip(cycle, cycle[1:]))
    missing = [s for s in steps if frozenset(s) not in edge_set]
    return sorted(cycle[:-1]) == list(range(n)) and cycle[0] == cycle[-1] and not missing, missing


if __name__ == "__main__":
    n = 5
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (2, 4), (4, 0)]
    print("Test Case 1")
    print(f"Input   : n = {n}, edges = {edges}")
    cycle = hamiltonian_cycle(n, edges)
    print(f"Output  : Hamiltonian Cycle Exists: {cycle is not None}")
    if cycle:
        print("Cycle   :", " -> ".join(map(str, cycle)))
    adj = build_adjacency(n, edges)
    print("Degrees :", {v: len(adj[v]) for v in range(n)})
    print("Reason  : vertices 1, 3, 4 each have only the neighbours {0, 2}; a cycle would need both of")
    print("          their edges, giving vertex 0 three cycle edges instead of two -> impossible.")
    doc_cycle = [0, 1, 2, 4, 3, 0]
    ok, missing = is_valid_cycle(n, edges, doc_cycle)
    print(f"Check   : document's cycle {doc_cycle} valid? {ok}; edges not in graph: {missing}")
    print("Note    : document lists True (cycle 0->1->2->4->3->0); correct value is False (no edge (4,3))")
    print("Time    : O(n!) worst case for backtracking; Hamiltonian Cycle is NP-complete")
