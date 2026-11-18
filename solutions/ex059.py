# Exercise 59 - Floyd-Warshall on a 6-router network, with a link failure (B-D)
INF = float("inf")
ROUTERS = "ABCDEF"
LINKS = [("A", "B", 1), ("A", "C", 5), ("B", "C", 2), ("B", "D", 1),
         ("C", "E", 3), ("D", "E", 1), ("D", "F", 6), ("E", "F", 2)]   # undirected links


def initial_tables(links):
    n = len(ROUTERS)
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[i if i == j else None for j in range(n)] for i in range(n)]
    for a, b, w in links:
        i, j = ROUTERS.index(a), ROUTERS.index(b)
        dist[i][j] = dist[j][i] = w
        nxt[i][j], nxt[j][i] = j, i
    return dist, nxt


def floyd_warshall(dist, nxt):
    n = len(dist)
    dist, nxt = [r[:] for r in dist], [r[:] for r in nxt]
    for k in range(n):                       # allow router k as an intermediate hop
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]
    return dist, nxt


def route(nxt, src, dst):
    u, v = ROUTERS.index(src), ROUTERS.index(dst)
    if nxt[u][v] is None:
        return None
    path = [u]
    while u != v:
        u = nxt[u][v]
        path.append(u)
    return " -> ".join(ROUTERS[i] for i in path)


def show(left, right, left_title, right_title):
    cell = lambda x: f"{'INF' if x == INF else x:>4}"
    head = "".join(f"{c:>4}" for c in ROUTERS)
    print(f"   {left_title:<{len(head)}}  |  {right_title}")
    print(f"   {head}  |  {head}")
    for i, name in enumerate(ROUTERS):
        print(f" {name} {''.join(map(cell, left[i]))}  |  {''.join(map(cell, right[i]))}")


if __name__ == "__main__":
    print("Input   : links A-B:1 A-C:5 B-C:2 B-D:1 C-E:3 D-E:1 D-F:6 E-F:2 (bidirectional)")
    print()
    # ---- normal network ----
    direct, nxt0 = initial_tables(LINKS)
    full, nxt1 = floyd_warshall(direct, nxt0)
    print("1) Before the failure")
    show(direct, full, "Initial routing table", "After Floyd-Warshall")
    i, j = ROUTERS.index("A"), ROUTERS.index("F")
    print(f"Output  : Router A to Router F = {full[i][j]}   via {route(nxt1, 'A', 'F')}")
    print("Expected: Router A to Router F = 5")

    # ---- link B-D fails: remove it and recompute ----
    print("\n2) Link B-D fails")
    broken_links = [l for l in LINKS if {l[0], l[1]} != {"B", "D"}]
    direct2, nxt2 = initial_tables(broken_links)
    full2, nxt3 = floyd_warshall(direct2, nxt2)
    show(direct2, full2, "Table without link B-D", "After Floyd-Warshall")
    print(f"Router A to Router F after failure = {full2[i][j]}   via {route(nxt3, 'A', 'F')}")
    print()
    print(f"Summary : A to F  before = {full[i][j]} ({route(nxt1, 'A', 'F')}),"
          f"  after = {full2[i][j]} ({route(nxt3, 'A', 'F')})")
    changed = [(a, b) for x, a in enumerate(ROUTERS) for y, b in enumerate(ROUTERS)
               if x < y and full[x][y] != full2[x][y]]
    print("Router pairs whose distance changed:", ", ".join(a + b for a, b in changed))
