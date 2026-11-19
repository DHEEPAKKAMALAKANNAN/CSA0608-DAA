"""
Task 3 - draws the flowcharts and network diagrams of the routing engine (matplotlib, standard symbols:
terminal = rounded, process = rectangle, decision = diamond, input/output = parallelogram).

Writes to ../../Report/Screenshots/:
  t3_flow_dijkstra.png, t3_flow_bellman_ford.png, t3_flow_floyd.png, t3_flow_warshall.png   (flowcharts)
  t3_network_spt.png      base network with Dijkstra's shortest-path tree from H and the finalisation order
  t3_stage_b_graph.png    negative edge P->D: Dijkstra's (wrong) tree vs Bellman-Ford's (correct) tree
  t3_stage_c_graph.png    negative cycle C->D->E->C and the depots whose distance becomes undefined
  t3_matrices.png         heat maps of Floyd's distance matrix and Warshall's reachability matrix
All numbers in the diagrams are computed here by the same routing_engine functions used by the drivers.
Run:  py -3 draw_diagrams_t3.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

from routing_engine import INF, bellman_ford, dijkstra, floyd, warshall  # noqa: E402
from routing_io import base_network, fmt, modified_network  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "Report", "Screenshots"))
FILL = {"terminal": "#d9ead3", "process": "#dbe8f6", "decision": "#fff2cc", "io": "#e8dff5",
        "call": "#fde3cf"}
POS = {"H": (0, 2.1), "A": (2.2, 3.7), "B": (2.2, 0.5), "C": (4.3, 2.1), "P": (4.3, -1.3), "D": (6.4, 0.5),
       "E": (6.4, 3.7), "F": (8.5, 3.1), "G": (8.5, 0.5), "R": (10.6, 1.8)}


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
    """Draw a polyline through `points` with an arrow head at the end; optional label near a vertex."""
    xs, ys = zip(*points)
    ax.plot(xs, ys, color="#333333", lw=1.2, ls="--" if dashed else "-")
    ax.annotate("", xy=points[-1], xytext=points[-2],
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.2, shrinkA=0, shrinkB=0))
    if label:
        x, y = points[label_at]
        if label_at == 0 and points[1][0] == x and points[1][1] < y and (dx, dy) == (0.12, 0.12):
            dy = -0.45                                 # downward exit of a decision: label beside the line
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
    print(path)


# ----------------------------------------------------------------------------- flowcharts
def flowchart_dijkstra():
    fig, ax = new_canvas(11, 0.6, 15.4, "Dijkstra(G, s) - binary heap, greedy finalisation")
    n0 = Node(ax, 5, 14.7, "Start", "terminal", w=2.2)
    n1 = Node(ax, 5, 13.6, "Input: graph G = (V, E, w), source s", "io", w=5.6)
    n2 = Node(ax, 5, 12.4, "dist[v] <- inf, pred[v] <- nil for all v\ndist[s] <- 0;  push (0, s)", "process",
              w=5.6, h=1.0)
    d1 = Node(ax, 5, 10.9, "heap empty ?", "decision", w=3.2, h=1.2)
    n3 = Node(ax, 5, 9.5, "(d, u) <- extract-min(heap)", "process", w=4.4)
    d2 = Node(ax, 5, 8.1, "u finalised or\nd > dist[u] ?", "decision", w=3.6, h=1.5)
    n4 = Node(ax, 5, 6.6, "finalise u (append to order)", "process", w=4.4)
    n5 = Node(ax, 5, 5.4, "for each edge (u, v, w)", "process", w=4.0)
    d3 = Node(ax, 5, 3.9, "v not finalised and\ndist[u] + w < dist[v] ?", "decision", w=4.6, h=1.6)
    n6 = Node(ax, 5, 2.1, "dist[v] <- dist[u] + w;  pred[v] <- u\npush (dist[v], v)", "process", w=5.2, h=1.0)
    n7 = Node(ax, 9.1, 10.9, "Output: dist, pred,\nfinalisation order", "io", w=2.9, h=1.0)
    n8 = Node(ax, 9.1, 9.3, "End", "terminal", w=2.0)
    arrow(ax, [n0.bottom(), n1.top()])
    arrow(ax, [n1.bottom(), n2.top()])
    arrow(ax, [n2.bottom(), d1.top()])
    arrow(ax, [d1.right(), n7.left()], "Yes", 0, dy=0.15)
    arrow(ax, [n7.bottom(), n8.top()])
    arrow(ax, [d1.bottom(), n3.top()], "No", 0)
    arrow(ax, [n3.bottom(), d2.top()])
    arrow(ax, [d2.left(), (1.0, d2.y), (1.0, d1.y), d1.left()], "Yes (stale)", 0, dx=-1.6, dy=0.15)
    arrow(ax, [d2.bottom(), n4.top()], "No", 0)
    arrow(ax, [n4.bottom(), n5.top()])
    arrow(ax, [n5.bottom(), d3.top()])
    arrow(ax, [d3.bottom(), n6.top()], "Yes", 0)
    arrow(ax, [d3.right(), (8.0, d3.y), (8.0, n5.y), n5.right()], "No / next edge", 0, dx=0.1, dy=0.15)
    arrow(ax, [n6.right(), (8.0, n6.y), (8.0, d3.y)])
    arrow(ax, [n5.left(), (0.5, n5.y), (0.5, d1.y + 0.25), (d1.x - 1.1, d1.y + 0.25)], "all edges done", 1,
          dx=0.1, dy=1.6, dashed=True)
    ax.text(5.5, 0.9, "Greedy invariant: the extracted vertex has the smallest tentative distance; valid only if w >= 0",
            ha="center", fontsize=8.5, style="italic")
    save(fig, "t3_flow_dijkstra.png")


def flowchart_bellman_ford():
    fig, ax = new_canvas(12, 0.2, 15.4, "Bellman-Ford(G, s) - with early exit and negative-cycle detection")
    n0 = Node(ax, 5, 14.7, "Start", "terminal", w=2.2)
    n1 = Node(ax, 5, 13.6, "Input: G = (V, E, w), source s", "io", w=5.0)
    n2 = Node(ax, 5, 12.5, "dist[v] <- inf, pred[v] <- nil;  dist[s] <- 0;  k <- 1", "process", w=6.4)
    d1 = Node(ax, 5, 11.1, "k <= |V| - 1 ?", "decision", w=3.4, h=1.2)
    n3 = Node(ax, 5, 9.6, "one pass: for every edge (u, v, w):\nif dist[u] + w < dist[v] then update dist[v], pred[v]",
              "process", w=6.6, h=1.0)
    d2 = Node(ax, 5, 8.0, "any update in\nthis pass ?", "decision", w=3.4, h=1.4)
    n4 = Node(ax, 9.6, 8.0, "k <- k + 1", "process", w=2.0)
    n5 = Node(ax, 5, 6.3, "detection pass (pass |V|):\nfind an edge with dist[u] + w < dist[v]", "process",
              w=5.8, h=1.0)
    d3 = Node(ax, 5, 4.7, "witness edge\nfound ?", "decision", w=3.2, h=1.4)
    n6 = Node(ax, 9.4, 4.7, "walk pred |V| steps back -> on cycle;\nlist cycle; mark vertices reachable\n"
                            "from it as -inf (undefined)", "process", w=4.8, h=1.3, size=8.5)
    n7 = Node(ax, 9.4, 2.8, "Output: NEGATIVE CYCLE\n(cycle, weight, affected)", "io", w=4.2, h=1.0)
    n8 = Node(ax, 3.0, 2.8, "Output: dist, pred\n(valid shortest paths)", "io", w=3.6, h=1.0)
    n9 = Node(ax, 6.2, 1.0, "End", "terminal", w=2.0)
    arrow(ax, [n0.bottom(), n1.top()])
    arrow(ax, [n1.bottom(), n2.top()])
    arrow(ax, [n2.bottom(), d1.top()])
    arrow(ax, [d1.bottom(), n3.top()], "Yes", 0)
    arrow(ax, [n3.bottom(), d2.top()])
    arrow(ax, [d2.right(), n4.left()], "Yes", 0, dy=0.15)
    arrow(ax, [n4.top(), (n4.x, d1.y), d1.right()])
    arrow(ax, [d2.bottom(), n5.top()], "No (early exit)", 0, dx=0.12, dy=-0.5)
    arrow(ax, [d1.left(), (1.0, d1.y), (1.0, n5.y), n5.left()], "No", 0, dx=-0.7)
    arrow(ax, [n5.bottom(), d3.top()])
    arrow(ax, [d3.right(), n6.left()], "Yes", 0, dy=0.15)
    arrow(ax, [n6.bottom(), n7.top()])
    arrow(ax, [d3.left(), (n8.x, d3.y), n8.top()], "No", 0, dx=-0.8)
    arrow(ax, [n8.bottom(), (n8.x, n9.y), n9.left()])
    arrow(ax, [n7.bottom(), (n7.x, n9.y), n9.right()])
    save(fig, "t3_flow_bellman_ford.png")


def flowchart_closure(kind):
    floyd_mode = kind == "floyd"
    title = ("Floyd(W) - all-pairs shortest-path costs" if floyd_mode
             else "Warshall(A) - transitive closure (reachability)")
    fig, ax = new_canvas(12.6, 0.4, 14.4, title)
    n0 = Node(ax, 5, 13.7, "Start", "terminal", w=2.2)
    n1 = Node(ax, 5, 12.6, ("Input: cost matrix W (n x n), W[i][i] = 0, inf = no road" if floyd_mode
                            else "Input: adjacency matrix A (n x n)"), "io", w=6.6)
    n2 = Node(ax, 5, 11.4, ("D <- W;  nxt[i][j] <- j if road i->j;  k <- 1" if floyd_mode
                            else "R <- A;  k <- 1"), "process", w=5.6)
    d1 = Node(ax, 5, 10.0, "k <= n ?", "decision", w=2.8, h=1.2)
    n3 = Node(ax, 5, 8.6, "for every pair (i, j)", "process", w=3.8)
    d2 = Node(ax, 5, 7.0, ("D[i][k] + D[k][j] < D[i][j] ?" if floyd_mode
                           else "R[i][k] = 1 and R[k][j] = 1 ?"), "decision", w=5.4, h=1.5)
    n4 = Node(ax, 5, 5.3, ("D[i][j] <- D[i][k] + D[k][j]\nnxt[i][j] <- nxt[i][k]" if floyd_mode
                           else "R[i][j] <- 1"), "process", w=4.6, h=1.0 if floyd_mode else 0.8)
    n5 = Node(ax, 5, 3.9, "all pairs done for this k:\nrecord D(k) / changes;  k <- k + 1" if floyd_mode
              else "all pairs done for this k:\nrecord R(k) / new 1s;  k <- k + 1", "process", w=5.2, h=1.0)
    n6 = Node(ax, 10.7, 10.0, ("Output: D(n), nxt;\nD[i][i] < 0 => negative cycle" if floyd_mode
                              else "Output: R(n)\n(reachability matrix)"), "io", w=3.6, h=1.1)
    n7 = Node(ax, 10.7, 8.4, "End", "terminal", w=2.0)
    arrow(ax, [n0.bottom(), n1.top()])
    arrow(ax, [n1.bottom(), n2.top()])
    arrow(ax, [n2.bottom(), d1.top()])
    arrow(ax, [d1.right(), n6.left()], "No", 0, dy=0.15)
    arrow(ax, [n6.bottom(), n7.top()])
    arrow(ax, [d1.bottom(), n3.top()], "Yes", 0)
    arrow(ax, [n3.bottom(), d2.top()])
    arrow(ax, [d2.bottom(), n4.top()], "Yes", 0)
    arrow(ax, [d2.right(), (8.6, d2.y), (8.6, n3.y), n3.right()], "No / next pair", 0, dx=0.1, dy=0.15)
    arrow(ax, [n4.right(), (8.6, n4.y), (8.6, d2.y)])
    arrow(ax, [n3.left(), (1.5, n3.y), (1.5, n5.y), n5.left()], dashed=True)
    ax.text(0.9, 6.4, "pairs\nexhausted", ha="center", fontsize=8.5, fontweight="bold", color="#7f3f00")
    arrow(ax, [n5.bottom(), (n5.x, 2.9), (0.3, 2.9), (0.3, d1.y), d1.left()])
    ax.text(5.5, 1.4, ("Theta(n^3) cell examinations; D(k) allows only depots 1..k as intermediates" if floyd_mode
                       else "Theta(n^3) cell examinations; R(k) = reachable using depots 1..k as intermediates"),
            ha="center", fontsize=8.5, style="italic")
    save(fig, f"t3_flow_{kind}.png")


# ----------------------------------------------------------------------------- network drawings
def draw_network(ax, g, title, highlight=(), hl_color="#2e7d32", special=(), sp_color="#c62828", labels=None,
                 node_color=None):
    """Draw g at POS. highlight/special: sets of (u_code, v_code) drawn thick in hl_color / sp_color."""
    edges = {(g.names[u], g.names[v]): w for u, v, w in g.edges}
    ax.set_xlim(-0.8, 11.4)
    ax.set_ylim(-2.3, 4.5)
    ax.set_aspect("equal")
    ax.apply_aspect()
    px = ax.transData.transform((0.38, 0))[0] - ax.transData.transform((0, 0))[0]
    shrink = px * 72 / ax.figure.dpi + 2              # node radius in points: arrows end on the circle
    for (u, v), w in edges.items():
        (x1, y1), (x2, y2) = POS[u], POS[v]
        rad = 0.18 if (v, u) in edges else 0.0
        rad = {("P", "R"): 0.25, ("H", "P"): 0.3}.get((u, v), rad)
        if (u, v) in special:
            color, lw, ls = sp_color, 2.8, "--"
        elif (u, v) in highlight:
            color, lw, ls = hl_color, 3.0, "-"
        else:
            color, lw, ls = "#9e9e9e", 1.1, "-"
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}",
                                     arrowstyle="-|>", mutation_scale=14, color=color, lw=lw, ls=ls,
                                     shrinkA=shrink, shrinkB=shrink, zorder=1))
        t = 0.5 if rad else 0.4                         # straight edges: label at 40 % to avoid crossings
        mx, my = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
        dx, dy = x2 - x1, y2 - y1
        length = (dx * dx + dy * dy) ** 0.5
        off = (rad * length / 2) if rad else 0.0
        nx, ny = dy / length, -dx / length
        lx, ly = mx + nx * off, my + ny * off
        ax.text(lx, ly, str(w), fontsize=9, ha="center", va="center", zorder=3,
                color=sp_color if (u, v) in special else "#222222", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9))
    for name, (x, y) in POS.items():
        fc = (node_color or {}).get(name, "#dbe8f6")
        ax.add_patch(Circle((x, y), 0.38, fc=fc, ec="#1f3864", lw=1.6, zorder=4))
        ax.text(x, y, name, ha="center", va="center", fontsize=12, fontweight="bold", zorder=5)
        if labels and name in labels:
            ax.text(x, y - 0.62, labels[name], ha="center", va="center", fontsize=8.5, color="#1f3864", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))
    ax.axis("off")
    ax.set_title(title, fontsize=11, fontweight="bold")


def tree_edges(g, pred):
    return {(g.names[pred[v]], g.names[v]) for v in range(g.n) if pred[v] != -1}


def network_spt():
    g, _ = base_network()
    dist, pred, order = dijkstra(g, "H")
    labels = {g.names[v]: f"d={fmt(dist[v])}  #{order.index(v) + 1}" for v in range(g.n)}
    fig, ax = plt.subplots(figsize=(12, 7))
    draw_network(ax, g, "Base logistics network (10 depots, 19 one-way roads) - Dijkstra shortest-path tree "
                        "from H (green)", highlight=tree_edges(g, pred), labels=labels)
    ax.text(5.3, -2.15, "label under each depot: d = shortest distance from H, #k = k-th vertex finalised;  "
            "grey = roads not used by any shortest route", ha="center", fontsize=9, style="italic")
    save(fig, "t3_network_spt.png")


def stage_b_graph():
    g, _ = modified_network("stage_b_negative_edge.csv")
    dd, dp, order = dijkstra(g, "H")
    bf = bellman_ford(g, "H")
    fig, axes = plt.subplots(1, 2, figsize=(17, 6.6))
    wrong = {g.names[v]: "#f8d7da" for v in range(g.n) if dd[v] != bf.dist[v]}
    draw_network(axes[0], g, "Dijkstra with P->D = -5: tree and distances (WRONG for red depots)",
                 highlight=tree_edges(g, dp), hl_color="#ef6c00", special={("P", "D")},
                 labels={g.names[v]: f"d={fmt(dd[v])}  #{order.index(v) + 1}" for v in range(g.n)},
                 node_color=wrong)
    draw_network(axes[1], g, "Bellman-Ford: correct tree and distances (route to R now via P->D)",
                 highlight=tree_edges(g, bf.pred), hl_color="#1565c0", special={("P", "D")},
                 labels={g.names[v]: f"d={fmt(bf.dist[v])}" for v in range(g.n)})
    fig.text(0.5, 0.02, "red dashed = negative edge P->D (-5): D is finalised at step 5 (d = 10) before P (step 7, "
             "d = 13), so the cheaper offer 13 - 5 = 8 is refused", ha="center", fontsize=10, style="italic")
    save(fig, "t3_stage_b_graph.png")


def stage_c_graph():
    g, _ = modified_network("stage_c_negative_cycle.csv")
    res = bellman_ford(g, "H")
    cyc = [g.names[v] for v in res.negative_cycle]
    cycle_edges = {(cyc[i], cyc[(i + 1) % len(cyc)]) for i in range(len(cyc))}
    colours = {g.names[v]: "#f8d7da" for v in res.affected}
    colours.update({"H": "#d9ead3", "P": "#d9ead3"})
    labels = {g.names[v]: ("-inf" if v in res.affected else f"d={fmt(res.dist[v])} valid")
              for v in range(g.n)}
    fig, ax = plt.subplots(figsize=(12, 7))
    draw_network(ax, g, f"Stage C - negative cycle {' -> '.join(cyc + cyc[:1])} (weight {res.cycle_weight}) "
                        "reported by Bellman-Ford", special=cycle_edges, labels=labels, node_color=colours)
    ax.text(5.3, -2.15, "red = cycle edges and depots reachable from the cycle (-inf: no shortest path exists); "
            "green = depots whose distance is still valid", ha="center", fontsize=9, style="italic")
    save(fig, "t3_stage_c_graph.png")


def matrices():
    g, _ = base_network()
    fl = floyd(g, keep_snapshots=False)
    reach, _, _ = warshall(g)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.6))
    finite = [[x if x != INF else float("nan") for x in row] for row in fl.dist]
    im = a1.imshow(finite, cmap="YlGnBu")
    for i in range(g.n):
        for j in range(g.n):
            a1.text(j, i, fmt(fl.dist[i][j]) if fl.dist[i][j] != INF else "inf", ha="center", va="center",
                    fontsize=8, color="#555555" if fl.dist[i][j] == INF else ("white" if fl.dist[i][j] > 12 else "black"))
    a1.set_title("Floyd: final distance matrix D(10) (white = unreachable)")
    fig.colorbar(im, ax=a1, label="shortest cost (minutes)")
    a2.imshow(reach, cmap="Greens", vmin=0, vmax=1.6)
    for i in range(g.n):
        for j in range(g.n):
            a2.text(j, i, str(reach[i][j]), ha="center", va="center", fontsize=9)
    a2.set_title("Warshall: reachability matrix R(10)")
    for a in (a1, a2):
        a.set_xticks(range(g.n), g.names)
        a.set_yticks(range(g.n), g.names)
        a.set_xlabel("to depot j")
        a.set_ylabel("from depot i")
    save(fig, "t3_matrices.png")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    flowchart_dijkstra()
    flowchart_bellman_ford()
    flowchart_closure("floyd")
    flowchart_closure("warshall")
    network_spt()
    stage_b_graph()
    stage_c_graph()
    matrices()


if __name__ == "__main__":
    main()
