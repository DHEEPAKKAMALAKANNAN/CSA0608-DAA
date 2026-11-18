"""Q6 growth experiment - combinatorial growth of exhaustive search and the deployment boundary.

Prediction (made before running): candidates = 2^n (x2 per extra package), basic operations = n * 2^n bit checks,
so T(n) ~ c * n * 2^n and T(n+2)/T(n) ~ 4 (n+2)/n.
Sizes n = 10, 12, ..., 22 (random manifests, seeded; every optimum cross-checked with DP).
Deployment: fixed response time 1 s (interactive re-planning) -> largest n with c * n * 2^n <= 1 s, confirmed by
direct runs at n_max and n_max + 1.
Writes results/q6_growth.csv, results/q6_deployment.csv, results/datasets/q6_manifest_n*.csv and
../Output_Screenshots/q6_growth.png.
"""

import csv
import os
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from knapsack_exhaustive import dp_knapsack, exhaustive_airlift, random_instance  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SHOTS = os.path.join(HERE, "..", "Output_Screenshots")
SIZES = [10, 12, 14, 16, 18, 20, 22]
T_RESPONSE = 1.0                         # seconds - chosen response time for the loading planner


def run(n, repeats):
    w, v, cap = random_instance(n, seed=42 + n)
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        mask, best, bw, cnt = exhaustive_airlift(w, v, cap)
        times.append(time.perf_counter() - t0)
    return (w, v, cap), mask, best, bw, cnt, statistics.median(times)


def human(seconds):
    for unit, size in (("years", 365 * 86400), ("days", 86400), ("hours", 3600), ("min", 60)):
        if seconds >= size:
            return f"{seconds / size:,.1f} {unit}"
    return f"{seconds:.2f} s"


def main():
    os.makedirs(os.path.join(RESULTS, "datasets"), exist_ok=True)
    rows = []
    print("Q6 GROWTH - exhaustive search over all 2^n loading plans (prediction: candidates x2 per package)")
    print(f"{'n':>4}{'candidates 2^n':>16}{'feasible':>12}{'bit checks n2^n':>17}{'best value':>12}{'DP':>6}"
          f"{'time (s)':>11}{'x time/+2':>11}{'pred 4(n+2)/n':>15}")
    print("-" * 104)
    prev_t = None
    for n in SIZES:
        (w, v, cap), mask, best, bw, cnt, t = run(n, 3 if n <= 16 else 1)
        with open(os.path.join(RESULTS, "datasets", f"q6_manifest_n{n}.csv"), "w", newline="") as fh:
            wr = csv.writer(fh)
            wr.writerow(["package_id", "weight_kg", "value", "payload_limit_kg"])
            wr.writerows((f"P{i + 1}", w[i], v[i], cap if i == 0 else "") for i in range(n))
        dp = dp_knapsack(w, v, cap)
        ratio = t / prev_t if prev_t else None
        pred_ratio = 4 * n / (n - 2) if prev_t else None
        prev_t = t
        rows.append({"n": n, "candidates": cnt["generated"], "feasible": cnt["feasible"],
                     "bit_checks": cnt["bit_checks"], "best_value": best, "best_weight": bw, "payload": cap,
                     "dp_value": dp, "time_s": round(t, 4), "time_ratio_vs_n-2": round(ratio, 2) if ratio else "",
                     "predicted_ratio": round(pred_ratio, 2) if pred_ratio else ""})
        print(f"{n:>4}{cnt['generated']:>16,}{cnt['feasible']:>12,}{cnt['bit_checks']:>17,}{best:>12,}"
              f"{'ok' if dp == best else 'NO':>6}{t:>11.3f}{(f'{ratio:.2f}' if ratio else ''):>11}"
              f"{(f'{pred_ratio:.2f}' if pred_ratio else ''):>15}")
    exact = all(r["candidates"] == 2 ** r["n"] and r["bit_checks"] == r["n"] * 2 ** r["n"] for r in rows)
    print(f"candidates = 2^n and bit checks = n*2^n at every n: {'YES' if exact else 'NO'};"
          f"  optimum = DP optimum at every n: {'YES' if all(r['best_value'] == r['dp_value'] for r in rows) else 'NO'}")

    fit = [r for r in rows if r["n"] >= 16]
    c = sum(r["time_s"] * r["bit_checks"] for r in fit) / sum(r["bit_checks"] ** 2 for r in fit)
    print(f"\nFit T(n) = c * n * 2^n over n >= 16: c = {c * 1e9:.1f} ns per bit check"
          f"  (= {c * 22 * 1e9:.0f} ns per candidate at n = 22)")
    dep = []
    n_max = max(n for n in range(1, 64) if c * n * 2 ** n <= T_RESPONSE)
    print(f"DEPLOYMENT  response time {T_RESPONSE:.0f} s  ->  largest n = {n_max} packages"
          f" (predicted {c * n_max * 2 ** n_max:.2f} s; n = {n_max + 1} would need {c * (n_max + 1) * 2 ** (n_max + 1):.2f} s)")
    for n_chk in (n_max, n_max + 1):
        (_, _, _), _, best, _, cnt, t = run(n_chk, 1)
        verdict = "within" if t <= T_RESPONSE else "exceeds"
        print(f"  direct check n = {n_chk}: {cnt['generated']:,} candidates, measured {t:.2f} s -> {verdict} the 1 s limit")
        dep.append({"n": n_chk, "kind": "direct check", "candidates": cnt["generated"], "time_s": round(t, 3)})
    sens = []
    for budget in (1, 10, 60, 3600):
        nb = max(n for n in range(1, 64) if c * n * 2 ** n <= budget)
        dep.append({"n": nb, "kind": f"largest n for {budget} s", "candidates": 2 ** nb,
                    "time_s": round(c * nb * 2 ** nb, 3)})
        sens.append(f"{budget} s -> n = {nb}")
    print("Sensitivity (largest n for other budgets): " + ";  ".join(sens))
    print("Projection of T(n) = c n 2^n:")
    for n in (25, 30, 40, 50):
        t = c * n * 2 ** n
        dep.append({"n": n, "kind": "projection", "candidates": 2 ** n, "time_s": round(t, 1)})
        print(f"   n = {n}: {2 ** n:>22,} candidates -> {human(t)}")

    for name, data in (("q6_growth.csv", rows), ("q6_deployment.csv", dep)):
        with open(os.path.join(RESULTS, name), "w", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            wr.writeheader()
            wr.writerows(data)
    print("CSV  : results/q6_growth.csv, results/q6_deployment.csv   datasets: results/datasets/q6_manifest_n*.csv")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    ns = [r["n"] for r in rows]
    axes[0].semilogy(ns, [r["candidates"] for r in rows], "o-", color="#4C72B0", label="candidates generated (2^n)")
    axes[0].semilogy(ns, [r["bit_checks"] for r in rows], "s-", color="#DD8452", label="bit checks (n 2^n)")
    axes[0].semilogy(ns, [r["feasible"] for r in rows], "^-", color="#55A868", label="feasible candidates")
    axes[0].set_xlabel("number of packages n")
    axes[0].set_ylabel("count (log)")
    axes[0].set_title("Solution space doubles with every package")
    axes[0].grid(True, which="both", alpha=0.3)
    axes[0].legend(fontsize=8)
    xs = list(range(10, 31))
    axes[1].semilogy(ns, [r["time_s"] for r in rows], "o", ms=8, color="#4C72B0", label="measured time")
    axes[1].semilogy(xs, [c * n * 2 ** n for n in xs], "k--", lw=1, label=f"fit c n 2^n, c = {c * 1e9:.0f} ns")
    for budget, col in ((1, "#55A868"), (60, "#C44E52")):
        axes[1].axhline(budget, color=col, ls=":", label=f"response limit {budget} s")
    axes[1].axvline(n_max, color="#55A868", lw=0.8)
    axes[1].text(n_max + 0.2, 1e-3, f"n_max = {n_max}", color="#55A868", fontsize=9)
    axes[1].set_xlabel("number of packages n")
    axes[1].set_ylabel("time to decide (s, log)")
    axes[1].set_title("Deployment boundary (Python, this PC)")
    axes[1].grid(True, which="both", alpha=0.3)
    axes[1].legend(fontsize=8, loc="upper left")
    fig.suptitle("Q6 - Exhaustive search for airlift loading: combinatorial growth")
    fig.tight_layout()
    fig.savefig(os.path.join(SHOTS, "q6_growth.png"), dpi=150)
    plt.close(fig)
    print("Graph: ../Output_Screenshots/q6_growth.png")


if __name__ == "__main__":
    main()
