"""
Task 3 - input/output layer of the routing engine (kept separate from the algorithm core in routing_engine.py).

Loads the logistics network and its modifications from test_data/, formats distances, routes and matrices
for the console, and writes the CSV files behind the report's tables to results/.
"""
import csv
import os

from routing_engine import INF, Graph, load_edges, load_names

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "test_data")
RESULTS = os.path.join(HERE, "results")


def base_network():
    """(Graph, {code: full name}) of the Stage A network: 10 depots, 19 one-way roads."""
    codes, full = load_names(os.path.join(DATA, "depots.csv"))
    return Graph(codes, load_edges(os.path.join(DATA, "base_network.csv"))), full


def modified_network(change_file):
    """Base network plus the edges listed in test_data/<change_file>; returns (graph, added edges)."""
    g, _ = base_network()
    extra = load_edges(os.path.join(DATA, change_file))
    return g.with_extra_edges(extra), extra


def fmt(d):
    """Distance as text: integer, 'inf' (unreachable) or '-inf' (undefined because of a negative cycle)."""
    if d == INF:
        return "inf"
    if d == -INF:
        return "-inf"
    return str(int(d)) if float(d).is_integer() else f"{d:.2f}"


def route_text(g, route, sep=" -> "):
    return sep.join(g.names[v] for v in route) if route else "(no route)"


def print_wrapped(prefix, items, width=118, indent=8):
    """Print comma-separated items after prefix, wrapping at `width` characters."""
    line = prefix
    for k, item in enumerate(items):
        piece = item + (", " if k < len(items) - 1 else "")
        if len(line) + len(piece) > width:
            print(line.rstrip())
            line = " " * indent
        line += piece
    print(line.rstrip())


def print_header(title):
    print(title)
    print("=" * 112)


def print_edges(g, per_line=7):
    items = [f"{g.names[u]}->{g.names[v]} {w:>3}" for u, v, w in g.edges]
    for i in range(0, len(items), per_line):
        print("    " + "   ".join(items[i:i + per_line]))


def print_matrix(g, m, label, cell=lambda x: fmt(x), width=5):
    """Square matrix with vertex codes as row/column headings."""
    print(f"    {label:<6}" + "".join(f"{c:>{width}}" for c in g.names))
    for i, row in enumerate(m):
        print(f"    {g.names[i]:<6}" + "".join(f"{cell(x):>{width}}" for x in row))


def write_csv(name, header, rows):
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path


def matrix_rows(g, m, cell=lambda x: fmt(x)):
    return [[g.names[i]] + [cell(x) for x in row] for i, row in enumerate(m)]
