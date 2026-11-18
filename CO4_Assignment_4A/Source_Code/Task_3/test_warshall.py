"""
Task 3 - test suite for warshall_closure.py.

* Table-driven graphs from test_data/warshall_test_graphs.csv (given + own + boundary cases) with hand-derived
  expected closures: plain, row-skip and bitset Warshall and the BFS reference must all produce them.
* 200 random digraphs vs BFS, operation-count properties, closure properties, invalid input.
Prints PASS/FAIL lines and "RESULT: k/k tests passed".   Run:  py -3 test_warshall.py
"""
import csv
import os
import random

from warshall_closure import closure_bfs, load_network, warshall, warshall_bitset, warshall_row_skip

HERE = os.path.dirname(os.path.abspath(__file__))
results = []


def check(name, condition, detail=""):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))


def build(n, edges):
    A = [[0] * n for _ in range(n)]
    for e in filter(None, edges.split(";")):
        i, j = map(int, e.split("-"))
        A[i][j] = 1
    return A


def table_cases():
    with open(os.path.join(HERE, "test_data", "warshall_test_graphs.csv"), encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            n = int(row["n"])
            A = build(n, row["edges"])
            expected = [[int(c) for c in r] for r in row["expected_closure"].split("/")] if n else []
            outs = [warshall(A)[0], warshall_row_skip(A)[0], warshall_bitset(A)[0], closure_bfs(A)]
            ok = all(o == expected for o in outs)
            check(f"{row['case_id']:<4}({row['category']:<8}) n={n} {row['description']}", ok,
                  f"closure has {sum(map(sum, expected))} ones")


def property_tests():
    labels, A, _ = load_network()
    snaps = []
    R, ops = warshall(A, snaps)
    check("given network: R(0) equals the adjacency matrix and R(5) equals the closure", snaps[0] == A and
          snaps[-1] == R and len(snaps) == 6)
    check("given network: R(k-1) <= R(k) element-wise (1s are never removed)",
          all(snaps[k - 1][i][j] <= snaps[k][i][j] for k in range(1, 6) for i in range(5) for j in range(5)))
    check("given network: 1s added per iteration = [1, 2, 5, 4, 1], inner steps = 125 = 5^3",
          ops["new_ones"] == [1, 2, 5, 4, 1] and ops["inner_steps"] == 125)
    rng = random.Random(42)
    agree, steps_ok, trans_ok = True, True, True
    for _ in range(200):
        n = rng.randint(1, 12)
        p = rng.random()
        G = [[1 if rng.random() < p else 0 for _ in range(n)] for _ in range(n)]
        R1, o1 = warshall(G)
        agree &= R1 == warshall_row_skip(G)[0] == warshall_bitset(G)[0] == closure_bfs(G)
        steps_ok &= o1["inner_steps"] == n ** 3
        trans_ok &= all(not (R1[i][k] and R1[k][j]) or R1[i][j]
                        for i in range(n) for j in range(n) for k in range(n))
    check("200 random digraphs (n <= 12, any density): plain = row-skip = bitset = BFS", agree)
    check("200 random digraphs: plain version always performs exactly n^3 inner steps", steps_ok)
    check("200 random digraphs: result is transitive (R[i][k] and R[k][j] imply R[i][j])", trans_ok)
    G = [[0, 1], [1, 0]]
    warshall(G)
    check("input matrix is not modified (the algorithm works on a copy)", G == [[0, 1], [1, 0]])
    try:
        warshall([[0, 1], [0]])
        ok = False
    except ValueError:
        ok = True
    check("non-square matrix rejected with ValueError", ok)


def main():
    print("Task 3 - Warshall's algorithm: test run")
    table_cases()
    property_tests()
    print(f"RESULT: {sum(results)}/{len(results)} tests passed")


if __name__ == "__main__":
    main()
