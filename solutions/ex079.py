# Exercise 79 - Kruskal's Algorithm (Minimum Spanning Tree)

class DisjointSet:
    """Union-Find with path compression and union by rank."""
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path halving
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                                    # same component -> cycle
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal(n, edges):
    """Return (list of MST edges in the order chosen, total weight)."""
    ds = DisjointSet(n)
    mst, total = [], 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):       # greedy: lightest edge first
        if ds.union(u, v):                                  # accept only if no cycle forms
            mst.append((u, v, w))
            total += w
            if len(mst) == n - 1:
                break
    return mst, total


def run_test(number, n, edges, expected_edges, expected_weight):
    mst, total = kruskal(n, edges)
    print(f"Test Case {number}")
    print(f"Input   : n = {n}, m = {len(edges)}")
    print(f"          edges = {edges}")
    print(f"Sorted  : {sorted(edges, key=lambda e: e[2])}")
    print(f"Output  : Edges in MST: {mst}")
    print(f"          Total weight of MST: {total}")
    if mst == expected_edges and total == expected_weight:
        print(f"Expected: Edges in MST: {expected_edges}, Total weight of MST: {expected_weight}")
    else:
        print(f"Note    : document lists {expected_edges} / {expected_weight}; "
              f"correct value is {mst} / {total}")
    print()


if __name__ == "__main__":
    run_test(1, 4, [(0, 1, 10), (0, 2, 6), (0, 3, 5), (1, 3, 15), (2, 3, 4)],
             [(2, 3, 4), (0, 3, 5), (0, 1, 10)], 19)
    run_test(2, 5, [(0, 1, 2), (0, 3, 6), (1, 2, 3), (1, 3, 8), (1, 4, 5), (2, 4, 7), (3, 4, 9)],
             [(0, 1, 2), (1, 2, 3), (1, 4, 5), (0, 3, 6)], 16)
    print("Complexity: sorting O(E log E) + union-find O(E * alpha(V)) = O(E log E); space O(V + E).")
