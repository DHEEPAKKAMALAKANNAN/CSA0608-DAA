# Exercise 91 - Graph coloring (minimum colors) and the You/Alice/Bob map-coloring game
def build_adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def is_safe(v, color, colors, adj):
    return all(colors[u] != color for u in adj[v])


def color_graph(v, n, k, adj, colors):
    """Backtracking: colour vertices v..n-1 using at most k colours."""
    if v == n:
        return True
    for c in range(k):
        if is_safe(v, c, colors, adj):
            colors[v] = c
            if color_graph(v + 1, n, k, adj, colors):
                return True
            colors[v] = -1
    return False


def minimum_colors(n, adj):
    """Try k = 1, 2, 3, ... and return the first k that works (the chromatic number)."""
    for k in range(1, n + 1):
        colors = [-1] * n
        if color_graph(0, n, k, adj, colors):
            return k, colors


def max_regions_you_color(n, adj, k):
    """Turns go You, Alice, Bob, You, ... Each turn colours one uncoloured region with a legal
    colour (no neighbour already has it). Search all move sequences that colour every region
    and return the largest number of regions colored by You."""
    best = -1

    def play(colors, turn, mine):
        nonlocal best
        if -1 not in colors:
            best = max(best, mine)
            return
        for v in range(n):
            if colors[v] == -1:
                for c in range(k):
                    if is_safe(v, c, colors, adj):
                        colors[v] = c
                        play(colors, turn + 1, mine + (turn % 3 == 0))
                        colors[v] = -1

    play([-1] * n, 0, 0)
    return best


if __name__ == "__main__":
    n, k = 4, 3
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
    adj = build_adjacency(n, edges)
    print("Test Case 1")
    print(f"Input   : n = {n}, edges = {edges}, colors k = {k}")
    chi, colors = minimum_colors(n, adj)
    print(f"Minimum colors needed (backtracking): {chi}")
    print(f"Coloring (vertex: color): {dict(enumerate(colors))}")
    print(f"Number of colors k = {k} is {'enough' if k >= chi else 'NOT enough'} for a proper coloring")
    mine = max_regions_you_color(n, adj, k)
    print(f"Output  : Maximum number of regions you can color: {mine}")
    print("Expected: Maximum number of regions you can color: 2")
    print(f"Check   : turns alternate You/Alice/Bob, so with {n} regions you color turns 1 and 4 = {mine}")
