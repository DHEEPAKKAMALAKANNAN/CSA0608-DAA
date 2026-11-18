# Exercise 73 - Dijkstra's Algorithm on an Adjacency Matrix
INF = float("inf")


def dijkstra_matrix(graph, source):
    """Shortest distance from source to every vertex; O(V^2) with a matrix."""
    n = len(graph)
    dist = [INF] * n
    dist[source] = 0
    done = [False] * n
    for _ in range(n):
        # pick the closest vertex not finalised yet
        u = min((v for v in range(n) if not done[v]), key=lambda v: dist[v])
        if dist[u] == INF:
            break                      # remaining vertices are unreachable
        done[u] = True
        for v in range(n):             # relax every edge u -> v
            if graph[u][v] != INF and dist[u] + graph[u][v] < dist[v]:
                dist[v] = dist[u] + graph[u][v]
    return dist


if __name__ == "__main__":
    tests = [
        ([[0, 10, 3, INF, INF], [INF, 0, 1, 2, INF], [INF, 4, 0, 8, 2],
          [INF, INF, INF, 0, 7], [INF, INF, INF, 9, 0]], 0, [0, 7, 3, 9, 5]),
        ([[0, 5, INF, 10], [INF, 0, 3, INF], [INF, INF, 0, 1], [INF, INF, INF, 0]],
         0, [0, 5, 8, 9]),
    ]
    for no, (graph, source, expected) in enumerate(tests, 1):
        print(f"Test Case {no}")
        print(f"Input   : n = {len(graph)}, source = {source}, graph =")
        for row in graph:
            print("   ", " ".join(f"{'Inf' if x == INF else x:>4}" for x in row))
        result = dijkstra_matrix(graph, source)
        print(f"Output  : {result}")
        print(f"Expected: {expected}")
        print()
    print("Time complexity : O(V^2) for the matrix version; Space: O(V)")
