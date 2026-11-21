"""
draw_diagrams.py - explanatory diagrams for Assignment 4A (slot timeline, DP tables, dependency diagram,
WordBreak state strip, shortest-path tree, Gantt charts of the job schedules, OPT/p(j) strip).

All values are computed by the verification programs in ../../Source_Code (imported below), so the
diagrams always agree with the manual traces and the program output.  PNGs are written next to this file.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(OUT_DIR, "..", "..", "Source_Code")
for t in ("Task_2", "Task_3", "Task_4", "Task_5", "Task_6"):
    sys.path.insert(0, os.path.join(SRC, t))

from job_sequencing import job_sequencing, read_jobs as read_seq_jobs  # noqa: E402
from knapsack_dp import knapsack, read_items  # noqa: E402
from word_break import word_break_corrected, word_break_faulty  # noqa: E402
from graph_common import read_graph  # noqa: E402
from single_source import dijkstra  # noqa: E402
from energy_scheduling import read_jobs as read_energy_jobs, schedule  # noqa: E402

SEL, OTHER, BAD, GOOD = "#4a86c5", "#d0d0d0", "#e06666", "#93c47d"


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(path)


# ----------------------------------------------------------------------------- Task 2 slot timeline
def task2_slots():
    jobs = read_seq_jobs(os.path.join(SRC, "Task_2", "jobs.csv"))
    modified = [(j, d, 90 if j == "B" else p) for j, d, p in jobs]
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6))
    for ax, data, title in ((axes[0], jobs, "Task 2.4 - given instance"),
                            (axes[1], modified, "Task 2.5 - profit of B changed to 90")):
        trace = []
        slot, total, rejected = job_sequencing(data, trace)
        order = {row[0]: k + 1 for k, row in enumerate(trace)}
        prof = {j: p for j, _, p in data}
        dl = {j: d for j, d, _ in data}
        for t in range(1, len(slot)):
            ax.add_patch(Rectangle((t - 1, 1), 1, 1, facecolor=SEL, edgecolor="black"))
            j = slot[t]
            ax.text(t - 0.5, 1.55, f"{j}", ha="center", va="center", fontsize=14, color="white",
                    fontweight="bold")
            ax.text(t - 0.5, 1.2, f"p={prof[j]}, d={dl[j]}\nconsidered {order[j]}{'st' if order[j] == 1 else 'nd' if order[j] == 2 else 'rd' if order[j] == 3 else 'th'}",
                    ha="center", va="center", fontsize=8, color="white")
        for t in range(0, len(slot)):
            ax.text(t, 0.8, str(t), ha="center", fontsize=9)
        ax.text(len(slot) - 1 + 0.1, 0.8, "time", fontsize=8, style="italic")
        y = 0.35
        for j in rejected:
            ax.text(0, y, f"rejected: {j} (p={prof[j]}, d={dl[j]}) - slots 1..{min(dl[j], len(slot) - 1)} "
                    f"already hold more profitable jobs", fontsize=8.5, color="#a00000")
            y -= 0.28
        ax.set_xlim(-0.2, len(slot) - 1 + 0.6)
        ax.set_ylim(y - 0.1, 2.5)
        ax.axis("off")
        ax.set_title(f"{title}: total profit = {total}", fontsize=10.5, fontweight="bold")
    save(fig, "dg_task2_slot_timeline.png")


# ----------------------------------------------------------------------------- Task 3 DP table + path
def task3_table():
    items, W = read_items(os.path.join(SRC, "Task_3", "items.csv"))
    DP, best, sel, steps = knapsack(items, W)
    path = set()
    for i, _, w, _, _, dec, _ in steps:
        path.add((i, w))
    path.add((0, steps[-1][6]))
    n = len(items)
    fig, ax = plt.subplots(figsize=(11, 4.8))
    for i in range(n + 1):
        for w in range(W + 1):
            color = "#f4f4f4" if i == 0 or w == 0 else "white"
            if (i, w) in path:
                color = "#ffe599"
            ax.add_patch(Rectangle((w, n - i), 1, 1, facecolor=color, edgecolor="#777777"))
            ax.text(w + 0.5, n - i + 0.5, str(DP[i][w]), ha="center", va="center", fontsize=12,
                    fontweight="bold" if (i, w) in path else "normal")
    for w in range(W + 1):
        ax.text(w + 0.5, n + 1.15, f"w={w}", ha="center", fontsize=9)
    for i in range(n + 1):
        label = "i=0 (no items)" if i == 0 else f"i={i}: {items[i - 1][0]} (wt {items[i - 1][1]}, val {items[i - 1][2]})"
        ax.text(-0.1, n - i + 0.5, label, ha="right", va="center", fontsize=9)

    def centre(i, w):
        return (w + 0.5, n - i + 0.5)
    for i, iid, w, a, b, dec, nw in steps:
        style = dict(arrowstyle="-|>", mutation_scale=14, lw=2.2,
                     color="#c00000" if dec == "INCLUDE" else "#555555")
        ax.add_patch(FancyArrowPatch(centre(i, w), centre(i - 1, nw), shrinkA=14, shrinkB=14, **style))
        txt = f"include {iid}" if dec == "INCLUDE" else f"exclude {iid}"
        x, y = centre(i, w)
        ax.text((x + nw + 0.5) / 2 + 0.15, y - 0.5, txt, fontsize=8.5,
                color="#c00000" if dec == "INCLUDE" else "#555555", fontweight="bold")
    ax.set_xlim(-3.6, W + 1.2)
    ax.set_ylim(-0.3, n + 1.6)
    ax.axis("off")
    ax.set_title(f"Task 3 - DP[i][w] table for W = {W}; reconstruction path from DP[{n}][{W}] = {best} "
                 f"(red = include): items {', '.join(sel)}", fontsize=10.5, fontweight="bold")
    save(fig, "dg_task3_dp_table_path.png")


def task3_dependency():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    # generic rows i-1 and i
    cols = 9
    for r, label in ((1, "row i − 1\n(complete)"), (0, "row i\n(being filled)")):
        for c in range(cols):
            fc = "#e8f0fa" if r == 1 else "white"
            ax.add_patch(Rectangle((c, r), 1, 1, facecolor=fc, edgecolor="#888888"))
        ax.text(-0.15, r + 0.5, label, ha="right", va="center", fontsize=9)
    wc, wt = 7, 3
    ax.add_patch(Rectangle((wc, 0), 1, 1, facecolor="#ffe599", edgecolor="black", lw=2))
    ax.text(wc + 0.5, 0.5, "DP[i][w]", ha="center", va="center", fontsize=9, fontweight="bold")
    ax.add_patch(Rectangle((wc, 1), 1, 1, facecolor="#d9ead3", edgecolor="black", lw=2))
    ax.text(wc + 0.5, 1.5, "DP[i−1][w]", ha="center", va="center", fontsize=8.5)
    ax.add_patch(Rectangle((wc - wt, 1), 1, 1, facecolor="#f4cccc", edgecolor="black", lw=2))
    ax.text(wc - wt + 0.5, 1.5, "DP[i−1]\n[w − wt[i]]", ha="center", va="center", fontsize=8)
    ax.add_patch(FancyArrowPatch((wc + 0.5, 1.15), (wc + 0.5, 0.85), arrowstyle="-|>", mutation_scale=14,
                                 lw=2, color="#38761d"))
    ax.add_patch(FancyArrowPatch((wc - wt + 0.8, 1.1), (wc + 0.15, 0.85), arrowstyle="-|>", mutation_scale=14,
                                 lw=2, color="#990000", connectionstyle="arc3,rad=0.15"))
    ax.text(wc + 1.1, 1.05, "exclude item i:\nsame capacity, row above", fontsize=8.5, color="#38761d")
    ax.text(wc - wt - 0.1, 0.25, "include item i:\nval[i] + row above, wt[i] columns left", fontsize=8.5,
            color="#990000", ha="right")
    ax.annotate("", xy=(cols, -0.45), xytext=(0, -0.45), arrowprops=dict(arrowstyle="-|>", lw=1.2))
    ax.text(cols / 2, -0.8, "inside a row: w = 1, 2, …, W (left to right);  rows: i = 1, 2, …, n (top to bottom)",
            ha="center", fontsize=9)
    ax.set_xlim(-2.6, cols + 2.6)
    ax.set_ylim(-1.1, 2.4)
    ax.axis("off")
    ax.set_title("Task 3.5 - Dependency of DP[i][w]: both inputs lie in the previous row, never to the right "
                 "or below", fontsize=10.5, fontweight="bold")
    save(fig, "dg_task3_dependency.png")


# ----------------------------------------------------------------------------- Task 4 state strip
def task4_strip():
    text, dic = "catsdog", {"cat", "dog"}
    f = word_break_faulty(text, dic)
    c = word_break_corrected(text, dic)
    n = len(text)
    fig, ax = plt.subplots(figsize=(11, 4.3))
    for i, ch in enumerate(text):
        ax.text(i + 1.0, 3.25, ch, ha="center", fontsize=14, fontfamily="monospace")
    for i in range(n + 1):
        ax.text(i + 0.5, 2.85, f"i={i}", ha="center", fontsize=8.5)
    for row, arr, name in ((2, f, "faulty DP"), (0.6, c, "corrected DP")):
        for i in range(n + 1):
            wrong = f[i] != c[i] and row == 2
            col = BAD if wrong else (GOOD if arr[i] else "#f4f4f4")
            ax.add_patch(Rectangle((i, row), 1, 0.7, facecolor=col, edgecolor="#555555", lw=2 if wrong else 1))
            ax.text(i + 0.5, row + 0.35, "T" if arr[i] else "F", ha="center", va="center", fontsize=12,
                    fontweight="bold")
        ax.text(-0.15, row + 0.35, name, ha="right", va="center", fontsize=10)
    # the word "dog" spans j=4..7
    ax.add_patch(FancyArrowPatch((4.5, 2.75), (7.5, 2.75), connectionstyle="arc3,rad=-0.45",
                                 arrowstyle="-|>", mutation_scale=14, lw=1.6, color="#990000"))
    ax.text(6.0, 3.55, "\"dog\" = substring(Text, 4, 7) ∈ Dictionary", ha="center", fontsize=9, color="#990000")
    ax.annotate("first incorrect state: DP[7] = TRUE\nalthough DP[4] = FALSE (\"cats\" cannot be segmented)",
                xy=(7.5, 2.0), xytext=(8.4, 1.3), fontsize=9, color="#990000",
                arrowprops=dict(arrowstyle="-|>", color="#990000"))
    ax.add_patch(Rectangle((4, 0.6), 1, 0.7, fill=False, edgecolor="#0b5394", lw=2.5))
    ax.text(4.5, 0.35, "DP[4] = F blocks the split j = 4", ha="center", fontsize=8.5, color="#0b5394")
    ax.set_xlim(-2.0, n + 4.6)
    ax.set_ylim(0.1, 3.9)
    ax.axis("off")
    ax.set_title("Task 4.2 - DP states for Text = \"catsdog\", Dictionary = {cat, dog}", fontsize=10.5,
                 fontweight="bold")
    save(fig, "dg_task4_dp_strip.png")


# ----------------------------------------------------------------------------- Task 5 graph + SPT
def task5_graph():
    V, E = read_graph()
    dist, pred = dijkstra(V, E, "A")
    pos = {"A": (0, 1), "B": (2.2, 2.2), "C": (2.2, -0.2), "D": (4.6, 1), "E": (7.0, 1)}
    tree = {(pred[v], v) for v in V if pred[v]}
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for u, v, w in E:
        in_tree = (u, v) in tree
        rad = 0.35 if (u, v) == ("C", "E") else 0.0
        ax.add_patch(FancyArrowPatch(pos[u], pos[v], connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>",
                                     mutation_scale=18, lw=3.2 if in_tree else 1.3,
                                     color="#cc0000" if in_tree else "#777777", shrinkA=20, shrinkB=20))
        (x1, y1), (x2, y2) = pos[u], pos[v]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if (u, v) == ("C", "E"):
            mx, my = mx + 0.5 * rad * (y2 - y1), my - 0.5 * rad * (x2 - x1) - 0.25
        ax.text(mx, my + 0.12, str(w), fontsize=11, ha="center", fontweight="bold",
                color="#cc0000" if in_tree else "#444444",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    for v, (x, y) in pos.items():
        ax.add_patch(plt.Circle((x, y), 0.32, facecolor="#dbe8f6" if v != "A" else "#d9ead3",
                                edgecolor="black", lw=1.5, zorder=3))
        ax.text(x, y, v, ha="center", va="center", fontsize=13, fontweight="bold", zorder=4)
        ax.text(x, y + (0.48 if v != "C" else -0.68), f"dist {dist[v]}" + (f", pred {pred[v]}" if pred[v] else " (source)"),
                ha="center", fontsize=9, color="#0b5394", zorder=4)
    ax.text(3.5, -1.35, "Red = shortest-path tree from A (pred pointers): A→B→C→D→E.  "
            "Grey edges A→C (7), B→D (6), C→E (8) lose every relaxation contest.", ha="center", fontsize=9)
    ax.set_xlim(-0.8, 7.8)
    ax.set_ylim(-1.6, 3.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Task 5 - Given directed graph with the shortest-path tree from source A highlighted",
                 fontsize=10.5, fontweight="bold")
    save(fig, "dg_task5_graph_spt.png")


# ----------------------------------------------------------------------------- Task 6 Gantt + OPT strip
def gantt(jobs, selected, title, name, note):
    J = sorted(jobs, key=lambda x: (x[2], x[1], x[0]))
    fig, ax = plt.subplots(figsize=(11, 0.55 * len(J) + 1.6))
    tmax = max(f for _, _, f, _ in J)
    for r, (jid, s, f, v) in enumerate(reversed(J)):
        on = jid in selected
        ax.add_patch(Rectangle((s, r + 0.15), f - s, 0.7, facecolor=SEL if on else OTHER,
                               edgecolor="black", lw=1.4 if on else 0.8))
        ax.text((s + f) / 2, r + 0.5, f"{jid}  v={v}", ha="center", va="center", fontsize=9,
                color="white" if on else "black", fontweight="bold" if on else "normal")
        ax.text(-0.3, r + 0.5, f"[{s}, {f})", ha="right", va="center", fontsize=8.5)
    sel_jobs = sorted([x for x in J if x[0] in selected], key=lambda x: x[1])
    for a, b in zip(sel_jobs, sel_jobs[1:]):
        if a[2] == b[1]:
            ax.axvline(a[2], color="#cc0000", ls=":", lw=1.2)
    ax.set_xlim(-2.2, tmax + 1)
    ax.set_ylim(-0.2, len(J) + 0.1)
    ax.set_xticks(range(0, tmax + 1))
    ax.set_yticks([])
    ax.set_xlabel("time (units)")
    ax.grid(axis="x", alpha=0.3)
    for sp in ("left", "right", "top"):
        ax.spines[sp].set_visible(False)
    ax.set_title(title, fontsize=10.5, fontweight="bold")
    ax.text(tmax / 2, -1.25 - 0.02 * len(J), note, ha="center", fontsize=8.5, style="italic",
            transform=ax.transData)
    save(fig, name)


def task6_figures():
    jobs = read_energy_jobs(os.path.join(SRC, "Task_6", "jobs.csv"))
    J, p, OPT, dec, sel, best, _ = schedule(jobs)
    gantt(jobs, sel, f"Task 6 - the eight jobs (sorted by finish time); selected = blue: {', '.join(sel)}, "
          f"total value {best}", "dg_task6_gantt.png",
          "dotted red lines: a selected job finishes exactly when the next selected one starts (allowed)")
    # OPT / p(j) strip
    n = len(J)
    fig, ax = plt.subplots(figsize=(11, 3.9))
    chosen = set()
    j = n
    while j > 0:
        if dec[j][2] == "INCLUDE":
            chosen.add(j)
            j = p[j]
        else:
            j -= 1
    for j in range(n + 1):
        col = "#ffe599" if j in chosen else ("#f4f4f4" if j == 0 else "white")
        ax.add_patch(Rectangle((j * 1.25, 0), 1.0, 0.8, facecolor=col, edgecolor="black"))
        ax.text(j * 1.25 + 0.5, 0.4, str(OPT[j]), ha="center", va="center", fontsize=12, fontweight="bold")
        ax.text(j * 1.25 + 0.5, 1.55, f"OPT[{j}]", ha="center", fontsize=8.5, fontweight="bold")
        if j:
            ax.text(j * 1.25 + 0.5, 0.95, f"{J[j - 1][0]}\np({j})={p[j]}", ha="center", fontsize=8)
    for j in range(1, n + 1):
        if True:                                        # draw every include link, adjacent ones too
            on = j in chosen
            ax.add_patch(FancyArrowPatch((j * 1.25 + 0.5, 0.0), (p[j] * 1.25 + 0.5, 0.0),
                                         connectionstyle="arc3,rad=-0.45", arrowstyle="-|>", mutation_scale=12,
                                         lw=2.2 if on else 0.9, color="#cc0000" if on else "#999999"))
    ax.text(n * 0.625 + 0.5, -2.05, "arcs: include-branch link OPT[j] → OPT[p(j)] (red = used in the "
            "reconstruction, grey = not chosen); yellow = states of the jobs selected", ha="center", fontsize=8.5)
    ax.set_xlim(-0.5, n * 1.25 + 1.5)
    ax.set_ylim(-2.3, 1.9)
    ax.axis("off")
    ax.set_title("Task 6 - OPT[j] = max(OPT[j−1], v_j + OPT[p(j)]) and the p(j) links for the official data",
                 fontsize=10.5, fontweight="bold")
    save(fig, "dg_task6_opt_strip.png")
    adv = read_energy_jobs(os.path.join(SRC, "Task_6", "adversarial_jobs.csv"))
    _, _, _, _, sel_a, best_a, _ = schedule(adv)
    gantt(adv, sel_a, f"Task 6 Stage 6 - adversarial set; DP selects {', '.join(sel_a)} = {best_a} "
          "(K1 = 100 and K5 = earliest finish are traps)", "dg_task6_adversarial_gantt.png",
          "K2+K3+K4 (40+40+40) beats the single most valuable job K1 (100) on the same interval [0, 10)")


def main():
    task2_slots()
    task3_table()
    task3_dependency()
    task4_strip()
    task5_graph()
    task6_figures()


if __name__ == "__main__":
    main()
