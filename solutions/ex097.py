# Exercise 97 - Classes P and NP: Hamiltonian Path (NP verifier) vs Connectivity (P algorithm)
from collections import deque
from itertools import permutations


def verify_hamiltonian_path(vertices, edges, certificate):
    """NP verifier, polynomial time O(V + E): is `certificate` a path visiting every vertex once?"""
    if sorted(certificate) != sorted(vertices):
        return False
    edge_set = {frozenset(e) for e in edges}
    return all(frozenset(step) in edge_set for step in zip(certificate, certificate[1:]))


def find_hamiltonian_path(vertices, edges):
    """Deterministic search for a certificate: tries all V! orders (exponential). A non-deterministic
    machine would simply 'guess' the right order and then run the verifier above."""
    for order in permutations(vertices):
        if verify_hamiltonian_path(vertices, edges, list(order)):
            return list(order)
    return None


def is_connected(vertices, edges):
    """A problem that is in P: BFS decides connectivity in O(V + E) with no guessing."""
    adj = {v: [] for v in vertices}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen, queue = {vertices[0]}, deque([vertices[0]])
    while queue:
        for w in adj[queue.popleft()]:
            if w not in seen:
                seen.add(w)
                queue.append(w)
    return len(seen) == len(vertices)


if __name__ == "__main__":
    V = ["A", "B", "C", "D"]
    cases = [
        ("Graph 1 (cycle)", [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")]),
        ("Graph 2 (star)", [("A", "B"), ("A", "C"), ("A", "D")]),
    ]
    for number, (name, E) in enumerate(cases, 1):
        print(f"Test Case {number}: {name}")
        print(f"Input   : V = {V}, E = {E}")
        path = find_hamiltonian_path(V, E)
        print(f"Output  : Hamiltonian Path Exists: {path is not None}", end="")
        print(f" (Path: {' -> '.join(path)})" if path else "")
        accepted = sum(verify_hamiltonian_path(V, E, list(p)) for p in permutations(V))
        print(f"Verifier: {accepted} of 24 possible vertex orders are accepted as certificates")
        bad = ["A", "C", "B", "D"]
        print(f"Verifier: wrong certificate {bad} accepted = {verify_hamiltonian_path(V, E, bad)}")
        print(f"P-class contrast: Connectivity (BFS) of this graph = {is_connected(V, E)}")
        print()
    print("Test Case 1 expected: Hamiltonian Path Exists: True (Path: A -> B -> C -> D)")
    print("Classification:")
    print("  Hamiltonian Path is in NP: a certificate (vertex order) is checked in O(V + E) time.")
    print("  No polynomial-time algorithm is known (finding one needs V! tries), and it is NP-complete.")
    print("  Connectivity is in P: BFS decides it in O(V + E). Every problem in P is also in NP.")
