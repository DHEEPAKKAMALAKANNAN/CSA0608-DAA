# Exercise 102 - Maximum Cut: greedy and randomized approximation vs exhaustive search
import random
from itertools import product


def cut_weight(side, weights):
    return sum(w for (u, v), w in weights.items() if side[u] != side[v])


def greedy_max_cut(vertices, weights):
    """Place vertices one by one on the side that cuts more edge weight towards already placed vertices."""
    side = {vertices[0]: 0}
    for v in vertices[1:]:
        to_side = [0, 0]                         # weight of edges from v to placed vertices on side 0 / 1
        for (a, b), w in weights.items():
            other = b if a == v else a if b == v else None
            if other in side:
                to_side[side[other]] += w
        side[v] = 0 if to_side[1] >= to_side[0] else 1      # join the side opposite the heavier neighbours
    return side


def randomized_max_cut(vertices, weights, trials, seed):
    rng = random.Random(seed)
    sides = ({v: rng.randint(0, 1) for v in vertices} for _ in range(trials))
    return max(sides, key=lambda s: cut_weight(s, weights))


def exhaustive_max_cut(vertices, weights):
    best = None
    for bits in product([0, 1], repeat=len(vertices) - 1):    # first vertex fixed on side 0 (symmetry)
        side = dict(zip(vertices, (0,) + bits))
        if best is None or cut_weight(side, weights) > cut_weight(best, weights):
            best = side
    return best


def cut_edges(side, weights):
    return sorted(e for e in weights if side[e[0]] != side[e[1]])


if __name__ == "__main__":
    V = [1, 2, 3, 4]
    W = {(1, 2): 2, (1, 3): 1, (2, 3): 3, (2, 4): 4, (3, 4): 2}
    print("Test Case 1")
    print(f"Input   : V = {V}, edge weights = {W}")
    print(f"          total weight = {sum(W.values())}")
    g, o = greedy_max_cut(V, W), exhaustive_max_cut(V, W)
    r = randomized_max_cut(V, W, 20, 1)
    print(f"Output  : Greedy Maximum Cut: Cut = {cut_edges(g, W)}, Weight = {cut_weight(g, W)}")
    print(f"          (sides: {g})")
    print(f"          Randomized (best of 20, seed 1): Cut = {cut_edges(r, W)}, Weight = {cut_weight(r, W)}")
    print(f"          Optimal Maximum Cut (Exhaustive Search): Cut = {cut_edges(o, W)}, Weight = {cut_weight(o, W)}")
    avg = sum(cut_weight(dict(zip(V, b)), W) for b in product([0, 1], repeat=4)) / 16
    print(f"          Average weight of a uniformly random cut (all 16 assignments) = {avg} = half the total weight")
    print(f"Performance Comparison: greedy achieves {100 * cut_weight(g, W) / cut_weight(o, W):.0f}% of the optimal weight")
    print("Note    : document lists greedy cut {(1,2),(2,4)} = 6 and optimal {(1,2),(2,4),(3,4)} = 8, but neither")
    print("          edge set is a cut ((1,3) and (2,3) uncut puts 1,2,3 on one side, yet (1,2) is cut).")
    print("          Correct: greedy = optimal = 9 (e.g. vertex 2 alone against {1,3,4}).")
    print("\nTest Case 2 - small random weighted graphs (seeded), greedy vs exhaustive search")
    print(" n  edges  total  greedy  random(20)  optimal  greedy/optimal")
    rng = random.Random(7)
    for n in (5, 6, 7, 8, 9, 10):
        verts = list(range(1, n + 1))
        weights = {(a, b): rng.randint(1, 9) for a in verts for b in verts if a < b and rng.random() < 0.6}
        gw = cut_weight(greedy_max_cut(verts, weights), weights)
        rw = cut_weight(randomized_max_cut(verts, weights, 20, n), weights)
        ow = cut_weight(exhaustive_max_cut(verts, weights), weights)
        print(f"{n:2d} {len(weights):6d} {sum(weights.values()):6d} {gw:7d} {rw:11d} {ow:8d} {gw / ow:14.2f}")
    print("Greedy (as coded) takes O(V * E) time and always cuts at least half of the total weight;")
    print("exhaustive search needs O(2^V * E). Optimum 9 of 12 shows the 1/2 bound is not tight here.")
