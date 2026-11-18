# Exercise 58 - Floyd-Warshall all-pairs shortest paths on a city network
INF = float("inf")


def build_matrix(n, edges, directed):
    """Initial distance matrix and 'next hop' matrix (for path reconstruction)."""
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[i if i == j else None for j in range(n)] for i in range(n)]
    for a, b, w in edges:
        dist[a][b], nxt[a][b] = w, b
        if not directed:
            dist[b][a], nxt[b][a] = w, a
    return dist, nxt


def floyd_warshall(dist, nxt):
    """Try every city k as an intermediate stop for every pair (i, j)."""
    n = len(dist)
    dist, nxt = [r[:] for r in dist], [r[:] for r in nxt]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]
    return dist, nxt


def get_path(nxt, u, v):
    if nxt[u][v] is None:
        return None
    path = [u]
    while u != v and len(path) <= len(nxt):      # length cap guards against negative cycles
        u = nxt[u][v]
        path.append(u)
    return path


def show(before, after, names):
    cell = lambda x: f"{'INF' if x == INF else x:>5}"
    head = "".join(f"{x:>5}" for x in names)
    print(f"     {'BEFORE Floyd-Warshall':<{len(head)}}  |  AFTER Floyd-Warshall")
    print(f"     {head}  |  {head}")
    for i, name in enumerate(names):
        print(f"{name:>4} {''.join(map(cell, before[i]))}  |  {''.join(map(cell, after[i]))}")


def quietest_city(dist, threshold):
    """City with the fewest cities within the threshold (ties -> greatest number)."""
    n = len(dist)
    near = [[j for j in range(n) if j != i and dist[i][j] <= threshold] for i in range(n)]
    best = min(range(n), key=lambda i: (len(near[i]), -i))
    return best, near


if __name__ == "__main__":
    # ---- Test Case 1: n = 4, undirected, distanceThreshold = 4 ----
    edges = [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]]
    print("Test Case 1\nInput   : n = 4, edges = [[0,1,3],[1,2,1],[1,3,4],[2,3,1]], distanceThreshold = 4")
    before, nxt = build_matrix(4, edges, directed=False)
    after, nxt = floyd_warshall(before, nxt)
    show(before, after, list(range(4)))
    city, near = quietest_city(after, 4)
    for i, lst in enumerate(near):
        print(f"City {i} -> [{', '.join('City ' + str(j) for j in lst)}]")
    print(f"Output  : {city}")
    print("Expected: 3")
    p = get_path(nxt, 0, 3)
    print(f"Shortest path City 0 to City 3: {' -> '.join(map(str, p))}  (distance {after[0][3]})")

    # ---- Test Case 2 (a): 4 cities, one-way roads, some negative weights ----
    print("\nTest Case 2 (a)\nInput   : 1->2:3  1->3:8  1->4:-4  2->4:1  2->3:4  3->1:2  4->3:-5  4->2:6")
    roads = [(1, 2, 3), (1, 3, 8), (1, 4, -4), (2, 4, 1), (2, 3, 4), (3, 1, 2), (4, 3, -5), (4, 2, 6)]
    before, nxt = build_matrix(4, [(a - 1, b - 1, w) for a, b, w in roads], directed=True)
    after, nxt = floyd_warshall(before, nxt)
    show(before, after, ["1", "2", "3", "4"])
    print(f"Output  : City 1 to City 3 = {after[0][2]}")
    print("Expected: City 1 to City 3 = -9")
    print("Path    : " + " -> ".join(f"City {c + 1}" for c in get_path(nxt, 0, 2)))
    print("Note    : the document's graph has a negative cycle 1->4->3->1 (-4-5+2 = -7), visible as the")
    print("          negative diagonal above; shortest walks are then unbounded, but -9 is the best")
    print("          simple path 1->4->3 and equals Floyd's value for the pair (1,3).")
