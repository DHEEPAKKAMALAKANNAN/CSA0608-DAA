"""
draw_diagrams_t5.py - flowcharts and graph diagrams for Task 5 (Kruskal, Prim, Boruvka).

Flowcharts use standard symbols (terminal = rounded, process = rectangle, decision = diamond with Yes/No,
input/output = parallelogram, predefined process = rectangle with side bars); helpers copied from
_tools/flowchart_reference.py so the assignment stays self-contained.
Graph drawings are computed from REAL runs of mst_engines (not drawn by hand): the facility network, each
algorithm's MST with its construction order, and the three different equal-cost MSTs of the tie network.
Writes PNGs (dpi 150) into ../../Report/Screenshots/t5_*.png.
Run:  py -3 draw_diagrams_t5.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle  # noqa: E402

from mst_engines import Network, boruvka, canonical, kruskal, prim  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "..", "Report", "Screenshots")
FILL = {"terminal": "#d9ead3", "process": "#dbe8f6", "decision": "#fff2cc", "io": "#e8dff5",
        "call": "#fde3cf"}
POS = {"HQ": (0, 2), "DC": (2, 3.3), "WH": (2, 0.7), "FA": (4, 2), "PT": (4.6, 4.3), "FB": (4, -0.3),
       "LB": (6.2, 1), "RS": (6.6, 3.6), "SC": (8.4, 2.3)}


# ----------------------------------------------------------------------------- flowchart helpers
class Node:
    """A flowchart symbol centred at (x, y) with width w and height h."""

    def __init__(self, ax, x, y, text, kind="process", w=3.6, h=0.8, size=9):
        self.x, self.y, self.w, self.h = x, y, w, h
        style = dict(facecolor=FILL[kind], edgecolor="#333333", linewidth=1.2)
        if kind == "terminal":
            ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                        boxstyle=f"round,pad=0,rounding_size={h / 2}", **style))
        elif kind == "decision":
            ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)], **style))
        elif kind == "io":
            s = 0.25
            ax.add_patch(Polygon([(x - w / 2 + s, y + h / 2), (x + w / 2 + s, y + h / 2),
                                  (x + w / 2 - s, y - h / 2), (x - w / 2 - s, y - h / 2)], **style))
        else:
            ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, **style))
            if kind == "call":
                for dx in (0.18, w - 0.18):
                    ax.plot([x - w / 2 + dx] * 2, [y - h / 2, y + h / 2], color="#333333", lw=1.0)
        ax.text(x, y, text, ha="center", va="center", fontsize=size)

    def top(self):
        return (self.x, self.y + self.h / 2)

    def bottom(self):
        return (self.x, self.y - self.h / 2)

    def left(self):
        return (self.x - self.w / 2, self.y)

    def right(self):
        return (self.x + self.w / 2, self.y)


def arrow(ax, points, label=None, label_at=0, dx=0.12, dy=0.12, dashed=False):
    """Polyline through `points` with an arrow head at the end; optional label near a vertex."""
    xs, ys = zip(*points)
    ax.plot(xs, ys, color="#333333", lw=1.2, ls="--" if dashed else "-")
    ax.annotate("", xy=points[-1], xytext=points[-2],
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2, shrinkA=0, shrinkB=0))
    if label:
        x, y = points[label_at]
        ax.text(x + dx, y + dy, label, fontsize=9, fontweight="bold", color="#7f3f00")


def new_canvas(width, y_low, y_high, title):
    fig, ax = plt.subplots(figsize=(width * 0.62, (y_high - y_low) * 0.62))
    ax.set_xlim(0, width)
    ax.set_ylim(y_low, y_high)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold")
    return fig, ax


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(os.path.normpath(path))


# ----------------------------------------------------------------------------- flowcharts
def flowchart_kruskal():
    fig, ax = new_canvas(13, 1.2, 14.6, "Kruskal's algorithm - global cheapest edge, union-find forest")
    s = Node(ax, 4.6, 13.9, "Start", "terminal", w=2.2)
    i = Node(ax, 4.6, 12.8, "Input: facilities V, links E (u, v, cost)", "io", w=5.6)
    a = Node(ax, 4.6, 11.6, "sort E by cost (stable)\nMakeSet(v) for every facility; T <- {}", "process",
             w=5.2, h=1.0)
    d1 = Node(ax, 4.6, 10.0, "|T| < V-1 and\nedges left ?", "decision", w=3.6, h=1.5)
    b = Node(ax, 4.6, 8.3, "(u, v) <- next cheapest edge\nru <- Find(u);  rv <- Find(v)", "call", w=4.8, h=1.0)
    d2 = Node(ax, 4.6, 6.6, "ru != rv ?\n(different components)", "decision", w=4.0, h=1.6)
    acc = Node(ax, 4.6, 4.9, "T <- T + {(u, v)}; Union(ru, rv)\n(safe edge: components merge)", "process",
               w=4.8, h=1.0)
    rej = Node(ax, 1.35, 6.6, "reject:\nwould form\na cycle", "process", w=1.9, h=1.2, size=8.5)
    o = Node(ax, 8.9, 10.0, "Output: T, cost = sum of T", "io", w=3.6)
    d3 = Node(ax, 8.9, 8.3, "|T| = V-1 ?", "decision", w=2.8, h=1.3)
    bad = Node(ax, 11.85, 8.3, "report: network\ndisconnected (T is\na spanning FOREST)", "process", w=2.2,
               h=1.3, size=8.5)
    e = Node(ax, 8.9, 2.2, "End: MST found", "terminal", w=2.8)
    for p, q in ((s, i), (i, a), (a, d1)):
        arrow(ax, [p.bottom(), q.top()])
    arrow(ax, [d1.bottom(), b.top()], "Yes", 0)
    arrow(ax, [b.bottom(), d2.top()])
    arrow(ax, [d2.bottom(), acc.top()], "Yes", 0)
    arrow(ax, [d2.left(), rej.right()], "No", 0, dx=-0.5, dy=0.15)
    arrow(ax, [acc.left(), (0.2, acc.y), (0.2, d1.y), d1.left()], "next edge", 1, dx=0.1, dy=2.7)
    arrow(ax, [rej.bottom(), (rej.x, acc.y)])
    arrow(ax, [d1.right(), o.left()], "No", 0, dy=0.15)
    arrow(ax, [o.bottom(), d3.top()])
    arrow(ax, [d3.bottom(), e.top()], "Yes", 0)
    arrow(ax, [d3.right(), bad.left()], "No", 0, dx=0.0, dy=0.15)
    arrow(ax, [bad.bottom(), (bad.x, e.y), e.right()])
    ax.text(4.6, 3.6, "stops as soon as V-1 edges are accepted;  O(E log E) sort + almost-O(1) Find/Union",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "t5_flowchart_kruskal.png")


def flowchart_prim():
    fig, ax = new_canvas(11, 2.0, 14.6, "Prim's algorithm - one tree grown from a root, indexed min-heap")
    s = Node(ax, 5, 13.9, "Start", "terminal", w=2.2)
    i = Node(ax, 5, 12.8, "Input: facilities, links, root r", "io", w=5.0)
    a = Node(ax, 5, 11.6, "key[v] <- inf, via[v] <- none for all v\nkey[r] <- 0; insert r into heap H",
             "process", w=5.4, h=1.0)
    d1 = Node(ax, 5, 10.0, "H not empty ?", "decision", w=3.2, h=1.3)
    b = Node(ax, 5, 8.5, "u <- ExtractMin(H); in_tree[u] <- true\nif via[u]: T <- T + {via[u]}", "call",
             w=5.4, h=1.0)
    c = Node(ax, 5, 7.1, "for each link (u, v, w)", "process", w=3.6)
    d2 = Node(ax, 5, 5.6, "v not in tree and\nw < key[v] ?", "decision", w=3.8, h=1.5)
    up = Node(ax, 5, 3.9, "key[v] <- w; via[v] <- (u, v)\ninsert / DecreaseKey(H, v)", "call", w=4.8, h=1.0)
    o = Node(ax, 8.85, 10.0, "Output: tree T, cost;\nunreached v -> disconnected", "io", w=3.4, h=1.1, size=8.5)
    e = Node(ax, 8.85, 8.3, "End", "terminal", w=2.0)
    for p, q in ((s, i), (i, a), (a, d1)):
        arrow(ax, [p.bottom(), q.top()])
    arrow(ax, [d1.bottom(), b.top()], "Yes", 0)
    arrow(ax, [b.bottom(), c.top()])
    arrow(ax, [c.bottom(), d2.top()])
    arrow(ax, [d2.bottom(), up.top()], "Yes", 0)
    arrow(ax, [d2.right(), (8.0, d2.y), (8.0, c.y), c.right()], "No / next link", 0, dx=0.1, dy=0.2)
    arrow(ax, [up.right(), (8.0, up.y), (8.0, c.y)], dashed=False)
    arrow(ax, [c.left(), (1.4, c.y), (1.4, d1.y), d1.left()], "all links done", 1, dx=0.1, dy=1.0)
    arrow(ax, [d1.right(), o.left()], "No", 0, dy=0.15)
    arrow(ax, [o.bottom(), e.top()])
    ax.text(5, 2.7, "safe edge = lightest link crossing the cut (tree | rest);  O((V + E) log V) with a binary heap",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "t5_flowchart_prim.png")


def flowchart_boruvka():
    fig, ax = new_canvas(11, 1.4, 14.6, "Boruvka's algorithm - each component picks its cheapest edge per round")
    s = Node(ax, 5, 13.9, "Start", "terminal", w=2.2)
    i = Node(ax, 5, 12.8, "Input: facilities V, links E", "io", w=4.6)
    a = Node(ax, 5, 11.7, "MakeSet(v) for all v (V components); T <- {}", "process", w=5.6)
    d1 = Node(ax, 5, 10.3, "components > 1 ?", "decision", w=3.6, h=1.3)
    b = Node(ax, 5, 8.7, "cheapest[c] <- none for each component c\nscan every link (u, v): if Find(u) != Find(v)\n"
             "update cheapest[Find(u)], cheapest[Find(v)]\n(ties: smaller (cost, u, v) wins)", "call", w=6.4, h=1.6,
             size=8.5)
    d2 = Node(ax, 5, 6.6, "any cheapest\nedge found ?", "decision", w=3.4, h=1.4)
    c = Node(ax, 5, 4.9, "for each chosen edge (u, v):\nif Union(u, v): T <- T + {(u, v)}\n(components at least halve)",
             "process", w=5.2, h=1.2)
    o1 = Node(ax, 9.3, 10.3, "Output: MST T,\ncost", "io", w=2.8, h=1.0)
    o2 = Node(ax, 9.3, 6.6, "Output: FOREST\n(disconnected)", "io", w=2.8, h=1.0)
    e = Node(ax, 9.3, 3.0, "End", "terminal", w=2.0)
    for p, q in ((s, i), (i, a), (a, d1)):
        arrow(ax, [p.bottom(), q.top()])
    arrow(ax, [d1.bottom(), b.top()], "Yes", 0)
    arrow(ax, [b.bottom(), d2.top()])
    arrow(ax, [d2.bottom(), c.top()], "Yes", 0)
    arrow(ax, [d2.right(), o2.left()], "No", 0, dy=0.15)
    arrow(ax, [c.left(), (1.2, c.y), (1.2, d1.y), d1.left()], "next round", 1, dx=0.1, dy=2.2)
    arrow(ax, [d1.right(), o1.left()], "No", 0, dy=0.15)
    arrow(ax, [o1.right(), (10.85, o1.y), (10.85, e.y), e.right()])
    arrow(ax, [o2.bottom(), e.top()])
    ax.text(5, 1.9, "at most ceil(log2 V) rounds; the per-component searches of one round are independent (parallel)",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "t5_flowchart_boruvka.png")


# ----------------------------------------------------------------------------- graph drawings
def draw_graph(ax, net, title, highlight=None, labels=None, colors=None, tie_edges=()):
    """Draw net on ax. highlight: set of canonical edges to draw thick; labels: {edge: text}; colors: {edge: c}."""
    highlight, labels, colors = highlight or set(), labels or {}, colors or {}
    for u, v, w in net.edges:
        (x1, y1), (x2, y2) = POS[net.names[u]], POS[net.names[v]]
        key = (min(u, v), max(u, v), w)
        on = key in highlight
        ls = "--" if key in tie_edges and not on else "-"
        ax.plot([x1, x2], [y1, y2], color=colors.get(key, "#d62728") if on else "#b0b0b0",
                lw=4 if on else 1.3, ls=ls, zorder=1)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        text = f"{w}" + (f"\n{labels[key]}" if key in labels else "")
        ax.text(mx, my, text, ha="center", va="center", fontsize=8, zorder=3,
                fontweight="bold" if on else "normal",
                bbox=dict(boxstyle="round,pad=0.15", fc="#fff8dc" if on else "white",
                          ec="#999999" if on else "none", lw=0.6))
    for name, (x, y) in POS.items():
        ax.scatter([x], [y], s=620, c="#dbe8f6", edgecolors="#1f3864", linewidths=1.5, zorder=2)
        ax.text(x, y, name, ha="center", va="center", fontsize=9, fontweight="bold", zorder=4)
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_xlim(-0.7, 9.1)
    ax.set_ylim(-0.9, 4.9)
    ax.set_aspect("equal")
    ax.axis("off")


def key_of(e):
    return (min(e[0], e[1]), max(e[0], e[1]), e[2])


def graph_figures():
    net = Network.from_csv(os.path.join(HERE, "test_data", "facility_network.csv"))
    fig, ax = plt.subplots(figsize=(8, 5))
    draw_graph(ax, net, "Facility network: 9 facilities, 15 candidate links (cost in Rs lakh)")
    save(fig, "t5_network.png")

    kr, pr, br = kruskal(net.n, net.edges), prim(net.n, net.edges, 0), boruvka(net.n, net.edges)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.2))
    draw_graph(axes[0], net, f"Kruskal: global order (#k = k-th accepted edge), cost {kr.total}",
               canonical(kr.edges), {key_of(e): f"#{k}" for k, e in enumerate(kr.edges, 1)})
    draw_graph(axes[1], net, f"Prim from HQ: one growing tree (#k = k-th edge), cost {pr.total}",
               canonical(pr.edges), {key_of(e): f"#{k}" for k, e in enumerate(pr.edges, 1)},
               {key_of(e): "#2ca02c" for e in pr.edges})
    round_of = {key_of(e): rnd for rnd, _, _, added, _, _ in br.trace for e in added}
    draw_graph(axes[2], net, f"Boruvka: R1 = round 1 (7 edges at once), R2 = round 2, cost {br.total}",
               canonical(br.edges), {k: f"R{r}" for k, r in round_of.items()},
               {k: ("#9467bd" if r == 1 else "#ff7f0e") for k, r in round_of.items()})
    fig.suptitle("Same network, same MST, three different construction sequences", fontweight="bold")
    save(fig, "t5_mst_construction.png")

    tie = Network.from_csv(os.path.join(HERE, "test_data", "facility_network_ties.csv"))
    ties = {key_of(e) for e in tie.edges if tie.edge_label(e) in
            ("HQ-WH", "WH-FA", "DC-PT", "LB-SC", "FA-FB", "FB-LB")}
    runs = [kruskal(tie.n, tie.edges), prim(tie.n, tie.edges, 0), boruvka(tie.n, tie.edges)]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.2))
    for ax, res, col in zip(axes, runs, ("#1f77b4", "#2ca02c", "#9467bd")):
        chosen = canonical(res.edges)
        cols = {k: ("#ff7f0e" if k in ties else col) for k in chosen}
        draw_graph(ax, tie, f"{res.algorithm.replace('root=0', 'root=HQ')}: cost {res.total}", chosen,
                   {k: "tie" for k in chosen & ties}, cols, tie_edges=ties)
    fig.suptitle("Modified costs (HQ-WH 6, LB-SC 7, FB-LB 10): three DIFFERENT edge sets, all MSTs of cost 38 "
                 "(orange = chosen tied edge, dashed = rejected tied alternative)", fontweight="bold", fontsize=11)
    save(fig, "t5_multiple_msts.png")


def main():
    flowchart_kruskal()
    flowchart_prim()
    flowchart_boruvka()
    graph_figures()


if __name__ == "__main__":
    main()
