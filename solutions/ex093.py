# Exercise 93 - Hamiltonian cycle using bitmask dynamic programming (Held-Karp style)
def hamiltonian_cycle_dp(n, edges):
    """reach[(mask, last)] = previous vertex, for every path that starts at 0, visits exactly the
    vertices in `mask` and ends at `last`. A full mask whose last vertex touches 0 is a cycle."""
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = adj[v][u] = True
    full = (1 << n) - 1
    reach = {(1, 0): None}
    for mask in range(1, full + 1):
        if not mask & 1:
            continue                                    # every path starts at vertex 0
        for last in range(n):
            if (mask, last) not in reach:
                continue
            for nxt in range(n):
                if adj[last][nxt] and not (mask >> nxt) & 1:
                    reach.setdefault((mask | 1 << nxt, nxt), last)
    for last in range(1, n):
        if (full, last) in reach and adj[last][0]:
            path, mask, cur = [], full, last
            while cur is not None:                      # walk the parents back to vertex 0
                path.append(cur)
                prev = reach[(mask, cur)]
                mask ^= 1 << cur
                cur = prev
            return path[::-1] + [0]
    return None


if __name__ == "__main__":
    n = 4
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
    print("Test Case 1")
    print(f"Input   : n = {n}, edges = {edges}")
    cycle = hamiltonian_cycle_dp(n, edges)
    print(f"Output  : Hamiltonian Cycle Exists: {cycle is not None}", end="")
    print(f" (Example cycle: {' -> '.join(map(str, cycle))})" if cycle else "")
    print("Expected: Hamiltonian Cycle Exists: True (Example cycle: 0 -> 1 -> 2 -> 3 -> 0; any valid cycle is fine)")
    steps = {frozenset(p) for p in zip(cycle, cycle[1:])}
    print(f"Check   : every step of the cycle is a graph edge: {steps <= {frozenset(e) for e in edges}}")
    print("\nTest Case 2 (extra check: a star graph has no cycle)")
    star = [(0, 1), (0, 2), (0, 3)]
    print(f"Input   : n = {n}, edges = {star}")
    print(f"Output  : Hamiltonian Cycle Exists: {hamiltonian_cycle_dp(n, star) is not None}")
    print("\nComplexity: O(2^n * n^2) time, O(2^n * n) space (better than the O(n!) of plain backtracking)")
