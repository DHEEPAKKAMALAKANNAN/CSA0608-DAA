# Exercise 28 - Travelling Salesman Problem (exhaustive search)
from itertools import permutations
from math import dist


def distance(city1, city2):
    """Euclidean distance between two cities."""
    return dist(city1, city2)


def path_length(path):
    """Sum of distances between consecutive cities on the path."""
    return sum(distance(path[i], path[i + 1]) for i in range(len(path) - 1))


def tsp(cities):
    """Try every ordering of the cities after the first one; keep the shortest tour."""
    start, others = cities[0], cities[1:]
    best_distance, best_path = float("inf"), None
    for perm in permutations(others):
        path = [start, *perm, start]
        d = path_length(path)
        if d < best_distance:
            best_distance, best_path = d, path
    return best_distance, best_path


if __name__ == "__main__":
    tests = [
        ([(1, 2), (4, 5), (7, 1), (3, 6)],
         7.0710678118654755, [(1, 2), (4, 5), (7, 1), (3, 6), (1, 2)]),
        ([(2, 4), (8, 1), (1, 7), (6, 3), (5, 9)],
         14.142135623730951, [(2, 4), (1, 7), (6, 3), (5, 9), (8, 1), (2, 4)]),
    ]
    for n, (cities, doc_dist, doc_path) in enumerate(tests, 1):
        d, path = tsp(cities)
        print(f"Test Case {n}:")
        print(f"Input   : cities = {cities}")
        print(f"Shortest Distance: {d}")
        print(f"Shortest Path    : {path}")
        if abs(d - doc_dist) < 1e-9:
            print(f"Expected: {doc_dist}")
        else:
            print(f"Note    : document lists {doc_dist}; correct value is {d:.6f}")
            print(f"          (the document's own path has length {path_length(doc_path):.6f})")
        print()
    print("Time complexity : O((n-1)!) permutations x O(n) per tour = O(n!)")
    print("Space complexity: O(n) for the current/best path")
