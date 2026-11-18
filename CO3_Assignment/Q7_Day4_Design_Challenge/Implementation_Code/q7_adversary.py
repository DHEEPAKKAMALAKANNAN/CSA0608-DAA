"""Q7 - adversarial ("killer") inputs for deterministic quick sorts, after M. D. McIlroy (1999),
"A Killer Adversary for Quicksort", Software - Practice and Experience 29(4).

Idea: the sort is run on n placeholder items whose values are NOT decided in advance ("gas"). When two gas
items are compared, one of them is frozen to the next smallest value; a gas item always compares larger than
a frozen one. A quick sort that chooses its pivot with a few comparisons therefore almost always meets a
pivot that becomes one of the smallest values, so each partition splits off only a constant number of items.
All answers are consistent with the final values, so running the same deterministic sort on those values
repeats exactly the same comparisons - the values form an input that makes this particular sort quadratic.
Requirement: the sort must only compare items with <, <=, > or >= (no arithmetic on keys) - true for every
sort in Q2 and Q7.
"""


class Adversary:
    """Decides values lazily, as in McIlroy's paper."""

    def __init__(self, n):
        self.gas = n                    # 'not yet decided' (larger than every frozen value)
        self.val = [n] * n
        self.nsolid = 0
        self.candidate = 0
        self.comparisons = 0

    def freeze(self, x):
        self.val[x] = self.nsolid
        self.nsolid += 1

    def cmp(self, x, y):
        """Three-way comparison of items x and y (negative, 0, positive)."""
        self.comparisons += 1
        val, gas = self.val, self.gas
        if val[x] == gas and val[y] == gas:
            if x == self.candidate:
                self.freeze(x)
            else:
                self.freeze(y)
        if val[x] == gas:
            self.candidate = x
        elif val[y] == gas:
            self.candidate = y
        return val[x] - val[y]


class GasItem:
    """Placeholder key whose comparisons are answered by the adversary."""

    __slots__ = ("ident", "adv")

    def __init__(self, ident, adv):
        self.ident, self.adv = ident, adv

    def __lt__(self, other):
        return self.adv.cmp(self.ident, other.ident) < 0

    def __le__(self, other):
        return self.adv.cmp(self.ident, other.ident) <= 0

    def __gt__(self, other):
        return self.adv.cmp(self.ident, other.ident) > 0

    def __ge__(self, other):
        return self.adv.cmp(self.ident, other.ident) >= 0


def make_killer(sort_fn, n):
    """Return (killer input of n distinct-ish integers, comparisons made under attack) for sort_fn(list)."""
    adv = Adversary(n)
    items = [GasItem(i, adv) for i in range(n)]
    sort_fn(items)
    for i in range(n):                  # at most one item is still undecided: give it the largest value
        if adv.val[i] == adv.gas:
            adv.freeze(i)
    return list(adv.val), adv.comparisons


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Student_A_Initial_Design"))
    from proposal_a_median3_hoare import quick_sort_a
    killer, c = make_killer(quick_sort_a, 1000)
    print(f"killer for proposal A, n = 1,000: {c:,} comparisons under attack; first values {killer[:12]}")
    print(f"proposal A on the killer: {quick_sort_a(list(killer)).comparisons:,} comparisons")
