# Exercise 67 - City With the Smallest Number of Neighbours at a Threshold Distance
INF = float("inf")


def floyd_warshall(n, edges):
    """All-pairs shortest distances for an undirected weighted graph."""
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        dist[u][v] = dist[v][u] = min(dist[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


def find_city(n, edges, threshold):
    dist = floyd_warshall(n, edges)
    reach = {c: [d for d in range(n) if d != c and dist[c][d] <= threshold]
             for c in range(n)}
    # fewest reachable cities; ties -> greatest city number
    best = min(range(n), key=lambda c: (len(reach[c]), -c))
    return best, reach


if __name__ == "__main__":
    tests = [
        (4, [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]], 4, 3),
        (5, [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]], 2, 0),
    ]
    for no, (n, edges, threshold, expected) in enumerate(tests, 1):
        city, reach = find_city(n, edges, threshold)
        print(f"Test Case {no}")
        print(f"Input   : n = {n}, distanceThreshold = {threshold}")
        print(f"          edges = {edges}")
        for c in range(n):
            print(f"  City {c} -> {['City %d' % d for d in reach[c]]}")
        print(f"Output  : {city}")
        print(f"Expected: {expected}")
        print()
    print("Method: Floyd-Warshall all-pairs shortest paths, O(n^3) time, O(n^2) space")
