# Exercise 68 - Network Delay Time (Dijkstra)
import heapq


def network_delay_time(times, n, k):
    """Minimum time for a signal from k to reach all n nodes, or -1."""
    graph = {u: [] for u in range(1, n + 1)}
    for u, v, w in times:
        graph[u].append((v, w))
    dist = {}                      # finalised shortest times
    heap = [(0, k)]                # (time, node)
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue
        dist[u] = d
        for v, w in graph[u]:
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return (max(dist.values()), dist) if len(dist) == n else (-1, dist)


if __name__ == "__main__":
    tests = [
        ([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2, 2),
        ([[1, 2, 1]], 2, 1, 1),
        ([[1, 2, 1]], 2, 2, -1),
    ]
    for no, (times, n, k, expected) in enumerate(tests, 1):
        answer, dist = network_delay_time(times, n, k)
        print(f"Test Case {no}")
        print(f"Input   : times = {times}, n = {n}, k = {k}")
        print(f"Arrival : {dict(sorted(dist.items()))}")
        print(f"Output  : {answer}")
        print(f"Expected: {expected}")
        print()
    print("Time complexity : O(E log V) with a binary heap; Space: O(V + E)")
