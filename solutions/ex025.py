# Exercise 25 - Closest Pair of Points (brute force)
from math import sqrt


def euclidean(p, q):
    return sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def closest_pair_brute_force(points):
    """Check every pair (i < j) and keep the pair with the smallest distance."""
    best_pair, best_dist = None, float("inf")
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = euclidean(points[i], points[j])
            if d < best_dist:
                best_pair, best_dist = (points[i], points[j]), d
    return best_pair, best_dist


if __name__ == "__main__":
    points = [(1, 2), (4, 5), (7, 8), (3, 1)]
    pair, dist = closest_pair_brute_force(points)
    print("Test Case 1")
    print(f"Input   : Points = {points}")
    print(f"Output  : Closest pair: {pair[0]} - {pair[1]}   Minimum distance: {dist}")
    print("Expected: Closest pair: (1, 2) - (3, 1)")
    # The document's distance is wrong: (1,2)-(3,1) has dx = 2, dy = 1, so d = sqrt(5), not sqrt(2).
    print("Note    : document lists 1.4142135623730951 (sqrt 2); correct is 2.23606797749979 (sqrt 5: dx=2, dy=1)")
    print()
    print("All pair distances (to verify the answer):")
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            print(f"  {points[i]} - {points[j]} = {euclidean(points[i], points[j]):.4f}")
    print()
    print("Time complexity : O(n^2) - n(n-1)/2 pair distances are computed")
    print("Space complexity: O(1) extra")
