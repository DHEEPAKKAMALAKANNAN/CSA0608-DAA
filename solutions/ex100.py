# Exercise 100 - Greedy approximation for Set Cover, compared with the optimal solution
import random
from itertools import combinations
from math import log
from time import perf_counter


def greedy_set_cover(universe, sets):
    """Repeatedly pick the set that covers the most still-uncovered elements (ties: first in list)."""
    uncovered, chosen = set(universe), []
    while uncovered:
        best = max(sets, key=lambda s: len(uncovered & s))
        if not uncovered & best:
            return None                                    # universe cannot be covered
        chosen.append(best)
        uncovered -= best
    return chosen


def optimal_set_cover(universe, sets):
    """Exhaustive search over combinations of increasing size; the first one that covers is optimal."""
    target = set(universe)
    for size in range(1, len(sets) + 1):
        for combo in combinations(sets, size):
            if set().union(*combo) >= target:
                return list(combo)


def random_instance(n, m, seed):
    rng = random.Random(seed)
    sets = [set(rng.sample(range(1, n + 1), rng.randint(2, max(3, n // 3)))) for _ in range(m)]
    for e in range(1, n + 1):
        if not any(e in s for s in sets):
            sets[rng.randrange(m)].add(e)
    return sets


def show(family):
    return "{" + ", ".join("{" + ", ".join(map(str, sorted(s))) + "}" for s in family) + "}"


if __name__ == "__main__":
    U = set(range(1, 8))
    S = [{1, 2, 3}, {2, 4}, {3, 4, 5, 6}, {4, 5}, {5, 6, 7}, {6, 7}]
    print("Test Case 1")
    print(f"Input   : U = {show([U])[1:-1]}, S = {show(S)}")
    greedy, optimal = greedy_set_cover(U, S), optimal_set_cover(U, S)
    print(f"Output  : Greedy Set Cover: {show(greedy)}")
    print(f"          Optimal Set Cover: {show(optimal)}")
    print(f"Performance Analysis: greedy uses {len(greedy)} sets, optimal uses {len(optimal)} sets "
          f"(ratio {len(greedy) / len(optimal):.2f})")
    print(f"Check   : document's optimal {{{{1,2,3}}, {{3,4,5,6}}}} covers {sorted(set.union({1,2,3},{3,4,5,6}))} -> misses 7")
    print("Note    : document lists optimal = 2 sets; correct value is 3 (only {1,2,3} contains 1, and no single set")
    print("          covers the remaining {4,5,6,7}), so here greedy is optimal. Document's greedy answer matches.")

    print("\nTest Case 2 - performance on different input sizes (seeded random instances + a trap instance)")
    print(" n   m  greedy  optimal  ratio  ln(n)+1 bound  greedy time(us)")
    trap_u = set(range(1, 15))
    trap = [set(range(1, 8)), set(range(8, 15)), {1, 2, 3, 4, 8, 9, 10, 11}, {5, 6, 12, 13}, {7, 14}]
    cases = [(n, 2 * n, random_instance(n, 2 * n, n)) for n in (8, 12, 16, 20, 24)] + [(14, 5, trap)]
    for n, m, fam in cases:
        universe = trap_u if fam is trap else set(range(1, n + 1))
        t0 = perf_counter()
        g = greedy_set_cover(universe, fam)
        elapsed = (perf_counter() - t0) * 1e6
        o = optimal_set_cover(universe, fam)
        print(f"{n:2d} {m:3d} {len(g):6d} {len(o):8d} {len(g) / len(o):6.2f} {log(n) + 1:13.2f} {elapsed:15.1f}")
    print("Greedy is O(|U| * |S|) and always within ln(n)+1 of optimal; the exact search is exponential in |S|.")
    print("The trap row (n=14) shows greedy can be worse than optimal: it picks the 8-element set first.")
