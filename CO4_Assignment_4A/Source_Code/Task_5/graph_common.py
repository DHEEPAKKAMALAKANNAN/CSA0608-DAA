"""graph_common.py - shared input reader for Task 5 (edge list CSV -> vertices, edges)."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INF = float("inf")


def read_graph(name="graph.csv"):
    """Return (sorted vertex list, edge list [(u, v, w)] in file order)."""
    edges = []
    with open(os.path.join(HERE, name), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            edges.append((r["from"], r["to"], int(r["weight"])))
    vertices = sorted({u for u, _, _ in edges} | {v for _, v, _ in edges})
    return vertices, edges


def fmt(x):
    return "inf" if x == INF else str(x)
