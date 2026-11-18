# Exercise 39 - K closest points to the origin
import heapq


def k_closest(points, k):
    """Keep a max-heap of size k holding the k smallest squared distances seen so far.
    Squared distance is enough for comparing (no square root needed)."""
    heap = []                                        # entries: (-squared_distance, point)
    for x, y in points:
        d = x * x + y * y
        if len(heap) < k:
            heapq.heappush(heap, (-d, [x, y]))
        elif d < -heap[0][0]:                        # closer than the farthest kept point
            heapq.heapreplace(heap, (-d, [x, y]))
    return [p for _, p in sorted(heap, reverse=True)]    # nearest first


if __name__ == "__main__":
    tests = [
        ([[1, 3], [-2, 2], [5, 8], [0, 1]], 2, [[-2, 2], [0, 1]]),
        ([[1, 3], [-2, 2]], 1, [[-2, 2]]),
        ([[3, 3], [5, -1], [-2, 4]], 2, [[3, 3], [-2, 4]]),
    ]
    for n, (points, k, expected) in enumerate(tests, 1):
        result = k_closest(points, k)
        same = sorted(result) == sorted(expected)
        print(f"Test Case {n}")
        print(f"Input   : points = {points}, k = {k}")
        print("Squared distances: " + ", ".join(f"{p}->{p[0] ** 2 + p[1] ** 2}" for p in points))
        print(f"Output  : {result}   (nearest first)")
        print(f"Expected: {expected}   -> {'same points (order does not matter)' if same else 'MISMATCH'}")
        print()
    print("Time complexity : O(n log k) - each of the n points costs one O(log k) heap operation")
    print("Space complexity: O(k) for the heap")
