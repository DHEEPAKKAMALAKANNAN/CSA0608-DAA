# Exercise 74 - Dijkstra's Algorithm on an Edge List (source -> target)
# The statement says each tuple (u, v, w) is an edge FROM u TO v, so edges are
# treated as directed.  The 'undirected' reading is also shown for comparison.
import heapq


def dijkstra_path(n, edges, source, target, directed=True):
    graph = [[] for _ in range(n)]
    for u, v, w in edges:
        graph[u].append((v, w))
        if not directed:
            graph[v].append((u, w))
    dist = [float("inf")] * n
    parent = [None] * n
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                       # stale heap entry
        for v, w in graph[u]:
            if d + w < dist[v]:
                dist[v], parent[v] = d + w, u
                heapq.heappush(heap, (dist[v], v))
    path, node = [], target
    while node is not None and dist[target] != float("inf"):
        path.append(node)
        node = parent[node]
    return dist[target], path[::-1]


if __name__ == "__main__":
    tests = [
        (6, [(0, 1, 7), (0, 2, 9), (0, 5, 14), (1, 2, 10), (1, 3, 15), (2, 3, 11),
             (2, 5, 2), (3, 4, 6), (4, 5, 9)], 0, 4, 20),
        (5, [(0, 1, 10), (0, 4, 3), (1, 2, 2), (1, 4, 4), (2, 3, 9), (3, 2, 7),
             (4, 1, 1), (4, 2, 8), (4, 3, 2)], 0, 3, 8),
    ]
    for no, (n, edges, source, target, doc) in enumerate(tests, 1):
        print(f"Test Case {no}")
        print(f"Input   : n = {n}, source = {source}, target = {target}")
        print(f"          edges = {edges[:5]}")
        print(f"                  {edges[5:]}")
        dist, path = dijkstra_path(n, edges, source, target)
        udist, upath = dijkstra_path(n, edges, source, target, directed=False)
        print(f"Output  : {dist}   path = {path}   (directed edges, as stated)")
        print(f"Undirected reading: {udist}   path = {upath}")
        if dist == doc:
            print(f"Expected: {doc}")
        else:
            print(f"Note    : document lists {doc}; correct value is {dist} for directed edges"
                  + (f" ({udist} only if edges are undirected)" if udist == doc
                     else f" ({udist} even if undirected)"))
        print()
    print("Time complexity : O((V + E) log V) with a binary heap; Space: O(V + E)")
