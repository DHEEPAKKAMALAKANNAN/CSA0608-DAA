"""ShopSphere audit - graphs for the report (saved to Report/graphs, data to Supporting_Files).

Measured data are read from the CSV files written by the module programs (run them first, or use
run_all.py); curves of the derived closed forms are overlaid on the measurements. Data computed here are
saved as graph_*.csv next to the other CSV files.

Figures
  fig1_growth_all_modules  operation counts of every module vs n (log-log) with the 10-minute budget
  fig2_m1_quadratic        M1 counted comparisons vs n(n-1)/2, and measured time vs c*n^2
  fig3_m2_audits           M2 staircase of counted audits between n-1 and 2n-3; n log2 n claim / actual
  fig4_m3_search           S1 vs S2 comparisons (measured), and S1 average vs probability p
  fig5_m4_m5_recurrences   T(n) of M4 (both designs) and M5 with counted points; doubling ratios
  fig6_f_bound             f(n) between 3n^2 and 4n^2 (n0 = 60) / 63n^2; f(n)/n^2 -> 3 and f(n)/n unbounded
  fig7_scalability_times   estimated time at n = 10^5 and 10^6 against the 600 s window
"""
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from audit_common import NIGHTLY_WINDOW_S, OPS_PER_SECOND, SUPPORT_DIR, fmt_time, write_csv  # noqa: E402
from m2_rate_limiter import closed_form as m2_closed, run_rate_limiter  # noqa: E402
from m3_product_search import make_index, s2_profile, sequential_search  # noqa: E402

GRAPH_DIR = Path(__file__).resolve().parent.parent / "Report" / "graphs"
COLORS = {"M1": "#c0392b", "M2": "#2e86c1", "S1": "#8e44ad", "S2": "#16a085", "M4c": "#d35400",
          "M4r": "#27ae60", "M5": "#2c3e50", "f": "#b7950b", "budget": "#7f8c8d"}
BUDGET_OPS = NIGHTLY_WINDOW_S * OPS_PER_SECOND


def read_csv(name):
    """Read Supporting_Files/<name> as a list of dicts (numbers converted to float)."""
    path = SUPPORT_DIR / name
    if not path.exists():
        raise SystemExit(f"{path} not found - run the module programs (or run_all.py) first.")
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        for key, value in row.items():
            try:
                row[key] = float(value)
            except (TypeError, ValueError):
                pass
    return rows


def style(ax, title, xlabel, ylabel, log=""):
    """Common axis styling: title, labels, grid, legend, optional log axes ('x', 'y' or 'xy')."""
    if "x" in log:
        ax.set_xscale("log")
    if "y" in log:
        ax.set_yscale("log")
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, which="major", alpha=0.35)
    ax.grid(True, which="minor", alpha=0.12)
    ax.legend(fontsize=8)


def save(fig, name):
    """Save a figure as Report/graphs/<name>.png (dpi 150) and close it."""
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    path = GRAPH_DIR / f"{name}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("saved", path.relative_to(GRAPH_DIR.parent.parent))


def log_grid(lo, hi, points=200):
    """Integer grid spaced evenly on a log axis."""
    return sorted({int(round(10 ** (lo + (hi - lo) * i / (points - 1)))) for i in range(points)})


def costs():
    """Closed-form cost functions used in figures 1 and 7."""
    lg = math.log2
    return {"M1 duplicate detector  n(n-1)/2": ("M1", lambda n: n * (n - 1) / 2),
            "M4 current  2n²-n": ("M4c", lambda n: 2 * n * n - n),
            "Report generator  3n²+10n log n+50": ("f", lambda n: 3 * n * n + 10 * n * lg(n) + 50),
            "M5  n log n (log n+1)/2 + n": ("M5", lambda n: n * lg(n) * (lg(n) + 1) / 2 + n),
            "M4 redesign  n log n + n": ("M4r", lambda n: n * lg(n) + n),
            "M2 rate limiter  2^⌈log n⌉-1": ("M2", lambda n: m2_closed(n)),
            "S1 one search (p = 0.5)": ("S1", lambda n: 0.5 * (n + 1) / 2 + 0.5 * n),
            "S2 one search  ⌊log n⌋+1": ("S2", lambda n: math.floor(lg(n)) + 1)}


def fig1_growth():
    """All modules on one log-log chart with the nightly budget line."""
    ns = log_grid(3, 7)
    fig, ax = plt.subplots(figsize=(10, 6))
    rows = {n: [n] for n in ns}
    for label, (key, cost) in costs().items():
        values = [cost(n) for n in ns]
        ax.plot(ns, values, color=COLORS[key], lw=2, label=label,
                ls="--" if key in ("S1", "S2") else "-")
        for n, v in zip(ns, values):
            rows[n].append(f"{v:.6g}")
    ax.axhline(BUDGET_OPS, color=COLORS["budget"], ls=":", lw=2, label="10-min window = 6×10¹⁰ ops")
    for n, text in ((10**5, "today\nn = 10⁵"), (10**6, "in a year\nn = 10⁶")):
        ax.axvline(n, color="grey", ls="-.", lw=1)
        ax.text(n * 1.08, 3, text, fontsize=8, color="dimgrey")
    style(ax, "Basic operations of every ShopSphere module (10⁸ ops/s)", "catalogue size n (products)",
          "basic operations", log="xy")
    sec = ax.secondary_yaxis("right", functions=(lambda o: o / OPS_PER_SECOND, lambda s: s * OPS_PER_SECOND))
    sec.set_ylabel("running time at 10⁸ ops/s (seconds)")
    ax.legend(fontsize=8, loc="upper left")
    save(fig, "fig1_growth_all_modules")
    write_csv("graph_fig1_growth.csv", ["n", "M1", "M4_current", "report_f", "M5", "M4_redesign", "M2",
                                        "S1_search", "S2_search"], list(rows.values()))


def fig2_m1():
    """M1: counted comparisons against n(n-1)/2, measured time against a fitted c*n^2."""
    data = read_csv("m1_comparisons.csv")
    ns = [r["n"] for r in data]
    fine = log_grid(math.log10(ns[0]) - 0.1, math.log10(ns[-1]) + 0.1, 60)
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.3))
    a.plot(fine, [n * (n - 1) / 2 for n in fine], color=COLORS["M1"], lw=1.5, label="theory n(n−1)/2")
    a.plot(ns, [r["title_comparisons"] for r in data], "o", color="black", label="counted title comparisons")
    style(a, "M1 comparisons: counted = n(n−1)/2", "number of products n", "title comparisons", log="xy")
    c = data[-1]["seconds"] / ns[-1] ** 2
    b.plot(fine, [c * n * n for n in fine], color=COLORS["M1"], lw=1.5, label=f"c·n², c = {c:.2e} s")
    b.plot(ns, [r["seconds"] for r in data], "s", color="black", label="measured time (min of 3)")
    style(b, "M1 wall-clock time grows like n²", "number of products n", "time (seconds)", log="xy")
    save(fig, "fig2_m1_quadratic")


def fig3_m2():
    """M2: staircase of counted audits and the over-estimate of the n log2 n claim."""
    ns = list(range(2, 2101))
    counted = [run_rate_limiter([0] * n) for n in ns]
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.3))
    a.step(ns, counted, where="post", color=COLORS["M2"], lw=2, label="counted Audit calls A(n)")
    a.plot(ns, [n - 1 for n in ns], color="grey", ls="--", label="lower bound n − 1")
    a.plot(ns, [2 * n - 3 for n in ns], color="black", ls=":", label="upper bound 2n − 3")
    a.plot(ns, [n * math.log2(n) for n in ns], color=COLORS["M1"], lw=1.2, label="claimed n log₂ n")
    a.set_ylim(0, 4500)
    style(a, "M2 audits stay between n − 1 and 2n − 3", "requests n", "Audit calls")
    big = log_grid(1, 6, 300)
    b.plot(big, [n * math.log2(n) / m2_closed(n) for n in big], color=COLORS["M2"], lw=1.5,
           label="n log₂ n / A(n)")
    b.plot(big, [math.log2(n) for n in big], color="grey", ls="--", label="log₂ n")
    style(b, "The Θ(n log n) claim over-estimates by ≈ log n", "requests n", "claim ÷ actual", log="x")
    save(fig, "fig3_m2_audits")
    write_csv("graph_fig3_m2_staircase.csv", ["n", "audits_counted", "n_minus_1", "2n_minus_3"],
              [[n, c, n - 1, 2 * n - 3] for n, c in zip(ns, counted)])


def fig4_m3():
    """M3: measured S1/S2 comparisons vs n, and S1 average as a function of p."""
    rows = []
    for k in range(1, 15):
        n = 2 ** k
        index = make_index(n, seed=k)
        best, avg_s, worst, avg_u, _ = s2_profile(index)
        s1_avg = sum(sequential_search(index, key)[1] for key in index) / n if n <= 2048 else (n + 1) / 2
        rows.append([n, round(s1_avg, 2), n, round(avg_s, 4), worst])
    write_csv("graph_fig4_m3_search.csv", ["n", "s1_avg_success", "s1_worst", "s2_avg_success", "s2_worst"],
              rows)
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.3))
    ns = [r[0] for r in rows]
    a.plot(ns, [r[2] for r in rows], "-", color=COLORS["S1"], lw=2, label="S1 worst = n")
    a.plot(ns, [r[1] for r in rows], "o", color=COLORS["S1"], ms=5,
           label="S1 average found (measured ≤ 2048)")
    a.plot(ns, [r[4] for r in rows], "-", color=COLORS["S2"], lw=2,
           label="S2 worst = ⌊log₂ n⌋ + 1 (measured)")
    a.plot(ns, [r[3] for r in rows], "o", color=COLORS["S2"], ms=5, label="S2 average found (measured)")
    style(a, "Sequential S1 vs binary S2 search", "catalogue size n", "key comparisons", log="xy")
    ps = [i / 100 for i in range(101)]
    n = 10**6
    b.plot(ps, [(p * (n + 1) / 2 + n * (1 - p)) / n for p in ps], color=COLORS["S1"], lw=2,
           label="formula p(n+1)/2 + n(1−p), n = 10⁶")
    index = make_index(1000, seed=7)
    succ = sum(sequential_search(index, k)[1] for k in index) / 1000      # every successful search run
    fail = sequential_search(index, -1)[1]                                 # an absent key: n comparisons
    pts = [0, 0.25, 0.5, 0.75, 1]
    b.plot(pts, [(p * succ + (1 - p) * fail) / 1000 for p in pts], "ks", label="measured, n = 1,000")
    b.annotate("n = 10⁶, p = 0.5:\n750,000.25 comparisons", xy=(0.5, 0.75000025), xytext=(0.08, 0.6),
               fontsize=8, arrowprops=dict(arrowstyle="->", color="grey"))
    style(b, "S1 average comparisons vs success probability p", "probability p that the product exists",
          "average comparisons ÷ n")
    save(fig, "fig4_m3_search")


def fig5_m4_m5():
    """M4/M5: recurrence values with counted points, and the doubling ratios."""
    rec = read_csv("m4_m5_recurrences.csv")
    sim = read_csv("m4_simulation.csv")
    m5 = read_csv("m5_simulation.csv")
    ns = [r["n"] for r in rec]
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.5))
    for key, col, label in (("M4c", "T_m4_current", "M4 current 4T(n/2)+n"),
                            ("M4r", "T_m4_redesign", "M4 redesign 2T(n/2)+n"),
                            ("M5", "T_m5", "M5 2T(n/2)+n log n")):
        a.plot(ns[1:], [r[col] for r in rec][1:], color=COLORS[key], lw=2, label=label)
    for design, key in (("current", "M4c"), ("redesign", "M4r")):
        pts = [r for r in sim if r["design"] == design]
        a.plot([r["n"] for r in pts], [r["ops_counted"] for r in pts], "o", color=COLORS[key], mfc="white",
               label=f"counted ({design} engine run)")
    a.plot([r["n"] for r in m5], [r["comparisons_counted"] for r in m5], "^", color=COLORS["M5"], mfc="white",
           label="M5 real merge-sort comparisons")
    style(a, "Recurrences (lines) and executed engines (markers)", "data size n", "basic operations T(n)",
          log="xy")
    for key, col, label in (("M4c", "T_m4_current", "M4 current → 4"), ("M4r", "T_m4_redesign",
                            "M4 redesign → 2(lg n+2)/(lg n+1)"), ("M5", "T_m5", "M5 → just over 2")):
        vals = [r[col] for r in rec]
        b.plot(ns[1:-1], [vals[i + 1] / vals[i] for i in range(1, len(vals) - 1)], "o-", ms=3,
               color=COLORS[key], label=label)
    for level in (2, 4):
        b.axhline(level, color="grey", ls=":", lw=1)
    b.set_ylim(1.5, 5)
    style(b, "What happens when the data doubles: T(2n)/T(n)", "data size n (before doubling)",
          "T(2n) / T(n)", log="x")
    save(fig, "fig5_m4_m5_recurrences")


def fig6_f():
    """Part (f): f(n) sandwiched between c1 n^2 and c2 n^2; ratios f/n^2 and f/n."""
    def f(n):
        return 3 * n * n + 10 * n * math.log2(n) + 50
    ns = log_grid(0, 4, 200)
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.3))
    a.plot(ns, [f(n) for n in ns], color=COLORS["f"], lw=2.5, label="f(n) = 3n² + 10n log₂ n + 50")
    a.plot(ns, [3 * n * n for n in ns], color="black", ls="--", label="c₁n² = 3n²")
    a.plot(ns, [4 * n * n for n in ns], color=COLORS["M4r"], ls="-.", label="c₂n² = 4n² (n ≥ 60)")
    a.plot(ns, [63 * n * n for n in ns], color=COLORS["M1"], ls=":", label="c₂n² = 63n² (n ≥ 1)")
    a.axvline(60, color="grey", lw=1)
    a.text(64, 2, "n₀ = 60", fontsize=8)
    style(a, "f(n) is sandwiched: Θ(n²)", "n", "operations", log="xy")
    big = log_grid(0, 6, 200)
    b.plot(big, [f(n) / n**2 for n in big], color=COLORS["f"], lw=2, label="f(n)/n² → 3 (bounded)")
    b.plot(big, [f(n) / n for n in big], color=COLORS["M1"], lw=2, label="f(n)/n → ∞ (not O(n))")
    b.axhline(3, color="black", ls="--", lw=1)
    style(b, "Bounded ratio to n², unbounded ratio to n", "n", "ratio", log="xy")
    save(fig, "fig6_f_bound")
    write_csv("graph_fig6_f_bound.csv", ["n", "f_n", "f_over_n2", "f_over_n"],
              [[n, f"{f(n):.10g}", f"{f(n) / n**2:.6f}", f"{f(n) / n:.6g}"] for n in big])


def fig7_scalability():
    """Part (g): estimated time per module at n = 10^5 and 10^6 against the 600 s window."""
    rows = [r for r in read_csv("scalability_estimates.csv") if r["verdict_1e6"] != "per query"]
    names = [r["module"] for r in rows][::-1]
    t5 = [r["seconds_1e5"] for r in rows][::-1]
    t6 = [r["seconds_1e6"] for r in rows][::-1]
    fig, ax = plt.subplots(figsize=(10, 5))
    ys = range(len(names))
    ax.barh([y + 0.2 for y in ys], t5, height=0.38, color="#aab7c4", label="n = 10⁵ (today)")
    ax.barh([y - 0.2 for y in ys], t6, height=0.38,
            color=[COLORS["M1"] if t > NIGHTLY_WINDOW_S else COLORS["M4r"] for t in t6],
            label="n = 10⁶ (red = misses window, green = fits)")
    for y, t in zip(ys, t6):
        ax.text(t * 1.3, y - 0.2, fmt_time(t), va="center", fontsize=8)
    ax.axvline(NIGHTLY_WINDOW_S, color="black", ls="--", lw=1.5, label="10-minute window (600 s)")
    ax.set_yticks(list(ys))
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlim(1e-4, 1e6)
    style(ax, "Estimated nightly running time at 10⁸ operations per second",
          "running time (seconds, log scale)", "", log="x")
    save(fig, "fig7_scalability_times")


def main():
    for make in (fig1_growth, fig2_m1, fig3_m2, fig4_m3, fig5_m4_m5, fig6_f, fig7_scalability):
        make()


if __name__ == "__main__":
    main()
