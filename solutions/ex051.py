# Exercise 51 - Travelling Salesperson with 4 cities, then a fifth city E is added (brute force)
from itertools import permutations


def build_matrix(edges):
    """Symmetric distance lookup dist[(x, y)] from the 'X-Y: d' list."""
    dist = {}
    for (x, y), d in edges.items():
        dist[(x, y)] = dist[(y, x)] = d
    return dist


def all_tours(cities, dist):
    """Every distinct tour starting at the first city (a route and its reverse count once)."""
    start, rest = cities[0], cities[1:]
    tours = []
    for perm in permutations(rest):
        if perm[0] > perm[-1]:                    # skip the mirror image of an already seen tour
            continue
        route = (start,) + perm + (start,)
        length = sum(dist[(route[i], route[i + 1])] for i in range(len(route) - 1))
        tours.append((length, route))
    return sorted(tours)


def report(title, cities, dist):
    tours = all_tours(cities, dist)
    print(f"{title}: {len(tours)} distinct tours")
    for length, route in tours:
        print(f"   {' -> '.join(route)} = {length}")
    best = tours[0][0]
    winners = [" -> ".join(r) for d, r in tours if d == best]
    print(f"   Shortest route(s): {winners} with total distance {best}")
    return best


if __name__ == "__main__":
    four = {("A", "B"): 10, ("A", "C"): 15, ("A", "D"): 20, ("B", "C"): 35, ("B", "D"): 25, ("C", "D"): 30}
    five = dict(four)
    five.update({("A", "E"): 25, ("B", "E"): 30, ("C", "E"): 20, ("D", "E"): 15})
    print("Test Case 1: symmetric distances")
    print("Input   : A-B 10, A-C 15, A-D 20, A-E 25, B-C 35, B-D 25, B-E 30, C-D 30, C-E 20, D-E 15")
    print()
    before = report("Before adding E (cities A, B, C, D)", "ABCD", build_matrix(four))
    print()
    after = report("After adding E (cities A, B, C, D, E)", "ABCDE", build_matrix(five))
    print()
    print(f"Output  : shortest route for 5 cities has distance {after} (was {before} with 4 cities)")
    example = sum(build_matrix(five)[p] for p in zip("ABDECA", "BDECA"))
    print(f"Note    : the document's example route A -> B -> D -> E -> C -> A costs {example}"
          f" ({'the shortest' if example == after else 'not the shortest'})")
    print("Cost of adding a city: (n-1)!/2 tours grows from 3 to 12 (factor n-1 = 4), O(n!) overall.")
