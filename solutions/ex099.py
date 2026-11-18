# Exercise 99 - 2-approximation for Vertex Cover compared with the exact brute-force solution
from itertools import combinations
from time import perf_counter


def is_vertex_cover(cover, edges):
    return all(u in cover or v in cover for u, v in edges)


def approx_vertex_cover(edges):
    """Take both endpoints of every edge that is still uncovered (a maximal matching).
    The cover has 2 * |matching| vertices and the optimum needs >= |matching|, so ratio <= 2."""
    cover = set()
    for u, v in edges:
        if u not in cover and v not in cover:
            cover |= {u, v}
    return cover


def exact_vertex_cover(vertices, edges):
    """Brute force: test subsets by increasing size; the first cover found is minimum."""
    for size in range(len(vertices) + 1):
        for subset in combinations(vertices, size):
            if is_vertex_cover(set(subset), edges):
                return set(subset)


def compare(vertices, edges):
    t0 = perf_counter()
    approx = approx_vertex_cover(edges)
    t1 = perf_counter()
    exact = exact_vertex_cover(vertices, edges)
    t2 = perf_counter()
    return approx, exact, (t1 - t0) * 1e6, (t2 - t1) * 1e6


if __name__ == "__main__":
    V = [1, 2, 3, 4, 5]
    E = [(1, 2), (1, 3), (2, 3), (3, 4), (4, 5)]
    print("Test Case 1")
    print(f"Input   : G = (V, E), V = {V}, E = {E}")
    approx, exact, ta, te = compare(V, E)
    print(f"Output  : Approximation Vertex Cover: {sorted(approx)} (size {len(approx)}, valid: {is_vertex_cover(approx, E)})")
    print(f"          Exact Vertex Cover (Brute-Force): {sorted(exact)} (size {len(exact)}, valid: {is_vertex_cover(exact, E)})")
    ratio = len(approx) / len(exact)
    print(f"Performance Comparison: approximation is {ratio:.2f} x optimal (guarantee: at most 2 x optimal)")
    print(f"Check   : document's exact cover {{2, 4}} valid? {is_vertex_cover({2, 4}, E)} (edge (1,3) is uncovered)")
    print("Note    : document lists exact {2, 4}; correct optimum has 3 vertices (triangle needs 2, (4,5) 1 more)")
    print("          document's approx {2, 3, 4} is not what the matching algorithm returns (it adds endpoint pairs)")

    print("\nTest Case 2 - larger graph (16 vertices: cycle plus chords) to compare running time")
    V2 = list(range(16))
    E2 = [(i, (i + 1) % 16) for i in range(16)] + [(i, (i + 5) % 16) for i in range(0, 16, 2)]
    approx, exact, ta, te = compare(V2, E2)
    print(f"Input   : |V| = {len(V2)}, |E| = {len(E2)}")
    print(f"Output  : approximation size {len(approx)}, exact size {len(exact)}, ratio {len(approx) / len(exact):.2f}")
    print(f"Time    : approximation {ta:.1f} us, brute force {te:.1f} us ({te / ta:.0f}x slower)")
    print("Complexity: approximation O(V + E); brute force O(2^V * E). The approximation is within 2x of optimal.")
