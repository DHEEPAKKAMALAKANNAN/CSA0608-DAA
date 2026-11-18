# Exercise 60 - Floyd-Warshall: all-pairs shortest paths, neighbour counts and directed test cases
INF = float("inf")


def initial_tables(n, edges, directed):
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[i if i == j else None for j in range(n)] for i in range(n)]
    for a, b, w in edges:
        dist[a][b], nxt[a][b] = w, b
        if not directed:
            dist[b][a], nxt[b][a] = w, a
    return dist, nxt


def floyd_warshall(dist, nxt):
    n = len(dist)
    dist, nxt = [r[:] for r in dist], [r[:] for r in nxt]
    for k in range(n):                       # k = allowed intermediate city
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]
    return dist, nxt


def get_path(nxt, names, u, v):
    if nxt[u][v] is None:
        return "no path"
    path = [u]
    while u != v:
        u = nxt[u][v]
        path.append(u)
    return " -> ".join(str(names[x]) for x in path)


def show(before, after, names):
    cell = lambda x: f"{'INF' if x == INF else x:>4}"
    head = "".join(f"{x:>4}" for x in names)
    print(f"     {'BEFORE Floyd-Warshall':<{len(head)}}  |  AFTER Floyd-Warshall")
    print(f"     {head}  |  {head}")
    for i, name in enumerate(names):
        print(f"{name:>4} {''.join(map(cell, before[i]))}  |  {''.join(map(cell, after[i]))}")


def named_directed_test(title, roads, src, dst, expected):
    """roads: list of 'XY w' strings meaning a one-way road X -> Y of length w."""
    names = sorted({c for r in roads for c in r[:2]})
    idx = {c: i for i, c in enumerate(names)}
    edges = [(idx[r[0]], idx[r[1]], int(r[3:])) for r in roads]
    before, nxt = initial_tables(len(names), edges, directed=True)
    after, nxt = floyd_warshall(before, nxt)
    print(f"\n{title}\nInput   : " + "  ".join(f"{r[0]}->{r[1]}:{r[3:]}" for r in roads))
    show(before, after, names)
    print(f"Output  : {src} to {dst} = {after[idx[src]][idx[dst]]}")
    print(f"Expected: {src} to {dst} = {expected}")
    print(f"Shortest path {src} to {dst}: {get_path(nxt, names, idx[src], idx[dst])}")


if __name__ == "__main__":
    # ---- Test Case 1: n = 5, undirected, distanceThreshold = 2 ----
    n, threshold = 5, 2
    edges = [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]]
    print("Test Case 1")
    print(f"Input   : n = 5, edges = {str(edges).replace(' ', '')}, distanceThreshold = 2")
    before, nxt = initial_tables(n, edges, directed=False)
    after, nxt = floyd_warshall(before, nxt)
    show(before, after, list(range(n)))
    near = [[j for j in range(n) if j != i and after[i][j] <= threshold] for i in range(n)]
    for i, lst in enumerate(near):
        print(f"City {i} -> [{', '.join('City ' + str(j) for j in lst)}]")
    best = min(range(n), key=lambda i: (len(near[i]), -i))   # fewest neighbours, ties -> larger id
    print(f"Output  : {best}")
    print("Expected: 0")
    print(f"Shortest path City 0 to City 3: {get_path(nxt, list(range(n)), 0, 3)}  (distance {after[0][3]})")

    named_directed_test("Test Case 2 (a)  shortest path from C to A",
                        ["BA 2", "AC 3", "CD 1", "DA 6", "CB 7"], "C", "A", 7)
    named_directed_test("Test Case 3 (b)  shortest path from E to C",
                        ["CA 2", "AB 4", "BC 1", "BE 6", "EA 1", "AD 5", "DE 2", "ED 4", "DC 1", "CD 3"],
                        "E", "C", 5)
