"""
Task 3 - Warshall's algorithm: reachability in a data-centre replication network      (CO4, Assignment 4A)

Application context: five data centres replicate data over ONE-WAY links (A Chennai, B Bengaluru, C Hyderabad,
D Mumbai, E Pune). Operations must know, for every ordered pair (i, j), whether data written at i can eventually
reach j through a chain of links - the TRANSITIVE CLOSURE of the link digraph.

DP formulation (Levitin 8.4):  R(k)[i][j] = 1 iff there is a path i -> j whose intermediate vertices are all
among the first k vertices.   R(0) = adjacency matrix,   R(n) = transitive closure,
    R(k)[i][j] = R(k-1)[i][j]  or  ( R(k-1)[i][k] and R(k-1)[k][j] ).
Instrumented algorithms:
  warshall          Levitin's triple loop (in place; row k and column k do not change in iteration k)  n^3 steps
  warshall_row_skip skips row i when R[i][k] = 0 (whole inner loop would change nothing)
  warshall_bitset   each row is an n-bit integer: row_i |= row_k   (n^2 word-parallel OR operations)
  closure_bfs       reference: breadth-first search from every vertex, Theta(n(n + m))
Run:  py -3 warshall_closure.py     -> R(0) ... R(5) for the 5-vertex network, used as the manual trace
"""
import csv
import os
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))


def load_network(path=os.path.join(HERE, "test_data", "network_links.csv")):
    """Read the one-way links; returns (vertex labels, adjacency matrix, link descriptions)."""
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    labels = sorted({r["from"] for r in rows} | {r["to"] for r in rows})
    idx = {v: i for i, v in enumerate(labels)}
    A = [[0] * len(labels) for _ in labels]
    for r in rows:
        A[idx[r["from"]]][idx[r["to"]]] = 1
    return labels, A, [r["link"] for r in rows]


def _check_square(A):
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("adjacency matrix must be square")
    return n


def warshall(A, snapshots=None):
    """Levitin's Warshall(A[1..n, 1..n]). Returns (R, ops). If `snapshots` is a list, R(0)..R(n) are appended."""
    n = _check_square(A)
    R = [row[:] for row in A]
    ops = {"inner_steps": 0, "new_ones": []}
    if snapshots is not None:
        snapshots.append([row[:] for row in R])
    for k in range(n):
        added = 0
        Rk = R[k]
        for i in range(n):
            Ri = R[i]
            rik = Ri[k]
            for j in range(n):
                ops["inner_steps"] += 1
                if not Ri[j] and rik and Rk[j]:      # R[i][j] or (R[i][k] and R[k][j])
                    Ri[j] = 1
                    added += 1
        ops["new_ones"].append(added)
        if snapshots is not None:
            snapshots.append([row[:] for row in R])
    return R, ops


def warshall_row_skip(A):
    """Same recurrence, but the j-loop is executed only for rows that can reach k (R[i][k] = 1)."""
    n = _check_square(A)
    R = [row[:] for row in A]
    ops = {"inner_steps": 0, "rows_skipped": 0}
    for k in range(n):
        Rk = R[k]
        for i in range(n):
            Ri = R[i]
            if not Ri[k]:
                ops["rows_skipped"] += 1
                continue
            for j in range(n):
                ops["inner_steps"] += 1
                if Rk[j]:
                    Ri[j] = 1
    return R, ops


def warshall_bitset(A):
    """Rows stored as Python integers (bit j = 1 if i reaches j); row_i |= row_k is one word-parallel OR."""
    n = _check_square(A)
    rows = [sum(1 << j for j in range(n) if A[i][j]) for i in range(n)]
    ops = {"row_ors": 0}
    for k in range(n):
        bit, rk = 1 << k, rows[k]
        for i in range(n):
            if rows[i] & bit:
                rows[i] |= rk
                ops["row_ors"] += 1
    return [[(rows[i] >> j) & 1 for j in range(n)] for i in range(n)], ops


def closure_bfs(A):
    """Reference closure: BFS from each vertex s; R[s][t] = 1 iff t is reached by a path of length >= 1."""
    n = _check_square(A)
    adj = [[j for j in range(n) if A[i][j]] for i in range(n)]
    R = [[0] * n for _ in range(n)]
    for s in range(n):
        queue = deque(adj[s])
        for t in adj[s]:
            R[s][t] = 1
        while queue:
            u = queue.popleft()
            for t in adj[u]:
                if not R[s][t]:
                    R[s][t] = 1
                    queue.append(t)
    return R


# --------------------------------------------------------------------------------------- printing
def print_matrices(snaps, labels, ks, names):
    """Print several matrices side by side; a newly added 1 is shown as [1]."""
    n = len(labels)
    width = 5 + 4 * n
    print(("    " + "".join(f"{names[k]:<{width + 4}}" for k in ks)).rstrip())
    print(("    " + "".join(("    " + "".join(f"{lab:^4}" for lab in labels)).ljust(width + 4) for _ in ks)).rstrip())
    for i in range(n):
        line = ""
        for k in ks:
            cells = ""
            for j in range(n):
                v = snaps[k][i][j]
                new = k > 0 and v and not snaps[k - 1][i][j]
                cells += f"{'[1]' if new else str(v):^4}"
            line += f" {labels[i]:<3}{cells}".ljust(width + 4)
        print(("    " + line).rstrip())


def main():
    labels, A, links = load_network()
    n = len(labels)
    print("=" * 100)
    print(" TASK 3 - WARSHALL'S ALGORITHM: REACHABILITY BETWEEN 5 DATA CENTRES (one-way replication links)")
    print("=" * 100)
    print("[1] One-way links (test_data/network_links.csv); A Chennai, B Bengaluru, C Hyderabad, D Mumbai, E Pune:")
    print("    " + ", ".join(links[:3]))
    print("    " + ", ".join(links[3:]))

    snaps = []
    R, ops = warshall(A, snaps)
    names = ["R(0) = A"] + [f"R({k}) via {labels[k - 1]}" for k in range(1, n + 1)]
    print("\n[2] Matrices R(0) ... R(5)   ([1] = 1 added in this iteration)")
    print_matrices(snaps, labels, [0, 1, 2], names)
    print()
    print_matrices(snaps, labels, [3, 4, 5], names)

    print("\n[3] What each iteration added (rule: R[i][j] = 1 if R[i][k] = 1 and R[k][j] = 1)")
    for k in range(1, n + 1):
        prev, cur = snaps[k - 1], snaps[k]
        into = [labels[i] for i in range(n) if prev[i][k - 1]]
        outof = [labels[j] for j in range(n) if prev[k - 1][j]]
        new = [f"{labels[i]}->{labels[j]}" for i in range(n) for j in range(n) if cur[i][j] and not prev[i][j]]
        print(f"    k={k} ({labels[k-1]}): rows reaching {labels[k-1]} = {{{', '.join(into)}}}, "
              f"{labels[k-1]} reaches {{{', '.join(outof)}}} -> {len(new)} new: {', '.join(new) or 'none'}")

    print(f"\n[4] Cost: inner steps = {ops['inner_steps']} = n^3 = {n}^3;  new 1s per iteration = {ops['new_ones']}")
    _, osk = warshall_row_skip(A)
    _, obs = warshall_bitset(A)
    print(f"    row-skip version: {osk['inner_steps']} inner steps ({osk['rows_skipped']} rows skipped); "
          f"bitset version: {obs['row_ors']} row ORs")
    ok = R == closure_bfs(A) == warshall_row_skip(A)[0] == warshall_bitset(A)[0]
    print(f"    closure agrees with BFS from every vertex and with both optimised versions: {ok}")

    print("\n[5] Interpretation")
    for i in range(n):
        reach = [labels[j] for j in range(n) if R[i][j]]
        print(f"    data written at {labels[i]} reaches: {', '.join(reach)}")
    cannot = [f"{labels[i]}->{labels[j]}" for i in range(n) for j in range(n) if i != j and not R[i][j]]
    print(f"    unreachable ordered pairs: {', '.join(cannot)}  (no link leads from {{D, E}} back to {{A, B, C}})")


if __name__ == "__main__":
    main()
