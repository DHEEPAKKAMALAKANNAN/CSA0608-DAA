# Exercise 98 - 3-SAT solver and NP-completeness proof by reduction Vertex Cover -> 3-SAT
from itertools import product, combinations


def satisfied(clauses, model):            # literal +i means x_i, -i means NOT x_i
    return all(any(model.get(abs(l), False) == (l > 0) for l in c) for c in clauses)


def assign_literal(clauses, lit):
    """Make `lit` true: drop satisfied clauses, shrink the others; None if a clause becomes empty."""
    out = []
    for c in clauses:
        if lit in c:
            continue
        rest = [l for l in c if l != -lit]
        if not rest:
            return None
        out.append(rest)
    return out


def dpll(clauses, model=None):
    """DPLL SAT solver (unit propagation + branching). Returns a model dict or None."""
    model = dict(model or {})
    while True:
        unit = next((c[0] for c in clauses if len(c) == 1), None)
        if unit is None:
            break
        clauses = assign_literal(clauses, unit)
        if clauses is None:
            return None
        model[abs(unit)] = unit > 0
    if not clauses:
        return model
    lit = clauses[0][0]
    for choice in (lit, -lit):
        reduced = assign_literal(clauses, choice)
        if reduced is not None:
            found = dpll(reduced, {**model, abs(choice): choice > 0})
            if found is not None:
                return found
    return None


def vertex_cover_to_3sat(vertices, edges, k):
    """Variable x_v = 'v is in the cover'. Edge (u,v) -> (x_u OR x_v). 'At most k true' is encoded by a
    sequential counter (Sinz) with auxiliary variables; short clauses are padded to exactly 3 literals."""
    n = len(vertices)
    x = {i + 1: i + 1 for i in range(n)}
    var = {v: i + 1 for i, v in enumerate(vertices)}
    s = {(i, j): n + (i - 1) * k + j for i in range(1, n) for j in range(1, k + 1)}
    cl = [[var[u], var[v]] for u, v in edges]
    cl += [[-x[1], s[1, 1]]] + [[-s[1, j]] for j in range(2, k + 1)]
    for i in range(2, n):
        cl += [[-x[i], s[i, 1]], [-s[i - 1, 1], s[i, 1]], [-x[i], -s[i - 1, k]]]
        for j in range(2, k + 1):
            cl += [[-x[i], -s[i - 1, j - 1], s[i, j]], [-s[i - 1, j], s[i, j]]]
    cl.append([-x[n], -s[n - 1, k]])
    nxt, out = n + (n - 1) * k + 1, []
    for c in cl:                                  # pad with fresh variables y: (c v y) and (c v NOT y)
        if len(c) == 3:
            out.append(c)
        elif len(c) == 2:
            out += [c + [nxt], c + [-nxt]]
            nxt += 1
        else:
            out += [c + [a, b] for a in (nxt, -nxt) for b in (nxt + 1, -(nxt + 1))]
            nxt += 2
    return out, var, nxt - 1


def min_vertex_cover_size(vertices, edges):
    for size in range(len(vertices) + 1):
        if any(all(u in c or v in c for u, v in edges) for c in map(set, combinations(vertices, size))):
            return size


if __name__ == "__main__":
    formula = [[1, 2, -3], [-1, 2, 4], [3, -4, 5]]
    print("Test Case 1 - 3-SAT: (x1 v x2 v ~x3) ^ (~x1 v x2 v x4) ^ (x3 v ~x4 v x5)")
    sols = [dict(zip(range(1, 6), bits)) for bits in product([False, True], repeat=5)]
    sols = [m for m in sols if satisfied(formula, m)]
    model = dpll(formula)
    full = {i: model.get(i, False) for i in range(1, 6)}
    print(f"Output  : Satisfiability: {model is not None}")
    print(f"          Satisfying assignment (DPLL): {full}, valid = {satisfied(formula, full)}")
    print(f"          Brute force over 2^5 = 32 assignments: {len(sols)} satisfy the formula")
    doc = {1: True, 2: True, 3: False, 4: True, 5: False}
    print(f"Check   : document's example assignment satisfies it? {satisfied(formula, doc)}  (clause 3 is False)")
    print("Note    : document lists x1=T,x2=T,x3=F,x4=T,x5=F as satisfying; it is not (clause 3 fails). The formula")
    print("          itself is satisfiable, e.g. with the assignment above.")
    print("\nTest Case 2 - Reduction Vertex Cover -> 3-SAT")
    V, E = [1, 2, 3, 4, 5], [(1, 2), (1, 3), (2, 3), (3, 4), (4, 5)]
    print(f"Input   : V = {V}, E = {E}")
    print(f"          minimum vertex cover (brute force) = {min_vertex_cover_size(V, E)}")
    agree = True
    for k in range(1, 6):
        cnf, var, nvars = vertex_cover_to_3sat(V, E, k)
        m = dpll(cnf)
        cover = {v for v in V if m and m.get(var[v], False)}
        has_cover = min_vertex_cover_size(V, E) <= k
        decoded_ok = not m or (len(cover) <= k and all(u in cover or v in cover for u, v in E))
        agree &= ((m is not None) == has_cover) and decoded_ok
        print(f"  k={k}: 3-CNF {nvars:2d} vars, {len(cnf):3d} clauses -> SAT = {str(m is not None):5}"
              f"| cover <= {k} exists = {str(has_cover):5}" + (f"| decoded cover {sorted(cover)}" if m else ""))
    print(f"NP-Completeness Verification: formula satisfiable <=> vertex cover of size <= k for all k: {agree}")
    print("  3-SAT is in NP (a given assignment is checked in O(clauses)); Vertex Cover is NP-complete and reduces")
    print("  to 3-SAT in polynomial time (O(V*k + E) clauses) => 3-SAT is NP-hard, hence NP-complete.")
