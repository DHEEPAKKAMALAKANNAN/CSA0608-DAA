# Exercise 64 - Path with Maximum Probability (Dijkstra with a max-heap)
import heapq


def max_probability_path(n, edges, succ_prob, start, end):
    """Dijkstra where the 'distance' is a product of probabilities (all <= 1), so extending a
    path never increases it and the greedy choice stays correct.  heapq is a min-heap, so
    probabilities are stored negated."""
    adj = [[] for _ in range(n)]
    for (a, b), p in zip(edges, succ_prob):
        adj[a].append((b, p))
        adj[b].append((a, p))
    best = [0.0] * n
    best[start] = 1.0
    parent = {start: None}
    heap = [(-1.0, start)]
    while heap:
        neg_p, node = heapq.heappop(heap)
        if node == end:
            break
        if -neg_p < best[node]:
            continue                                  # stale heap entry
        for nxt, p in adj[node]:
            if best[node] * p > best[nxt]:
                best[nxt] = best[node] * p
                parent[nxt] = node
                heapq.heappush(heap, (-best[nxt], nxt))
    if best[end] == 0.0:
        return 0.0, []
    path, node = [], end
    while node is not None:                           # rebuild the path from parents
        path.append(node)
        node = parent[node]
    return best[end], path[::-1]


if __name__ == "__main__":
    tests = [
        (3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2, "0.25000"),
        (3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.3], 0, 2, "0.30000"),
        (3, [[0, 1]], [0.5], 0, 2, "0.00000"),         # extra: no path from start to end
    ]
    for no, (n, edges, probs, s, e, expected) in enumerate(tests, 1):
        prob, path = max_probability_path(n, edges, probs, s, e)
        print(f"Test Case {no}" + ("   (extra: unreachable end node)" if no == 3 else ""))
        print(f"Input   : n = {n}, edges = {edges}, succProb = {probs}, start = {s}, end = {e}")
        print(f"Output  : {prob:.5f}")
        print(f"Expected: {expected}")
        print("Best path: " + (" -> ".join(map(str, path)) if path else "none (probability 0)"))
        print()
    print("Time complexity : O((V + E) log V) with a binary heap")
    print("Space complexity: O(V + E)")
