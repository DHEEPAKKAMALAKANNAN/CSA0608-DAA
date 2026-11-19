"""Q6(a) - Pivot quality in selection: Median of Medians vs QuickSelect (CSA06 DAA, Assignment 3 - CO3).

Question bullets answered with evidence:
  * "Demonstrate the effect of a deterministic poor-pivot strategy"  - first-element pivot on sorted batches;
  * "Explain why randomisation reduces, but does not eliminate, poor partitions" - 300 seeds of randomised QuickSelect
    on ONE batch: distribution of comparisons and of the fraction of each round that is kept;
  * "Explain the worst-case guarantee" - Median of Medians (g = 5) never keeps more than 7n/10 + 6 elements.

A partition round of size n is called POOR when it keeps more than 90 % of its elements for the next round
(and BAD when it keeps more than 75 %).  Only rounds with n >= 100 are classified (tiny rounds are noise).
All runs select the median (k = (n - 1) // 2) of the n = 10,001 delivery times of the demo batch (seed 7) unless
stated otherwise; every result is checked against sorted(a)[k].

Run:  py -3 q6_pivot_quality.py     (writes ../Median_of_Medians/results/q6_pivot_quality*.csv)
"""
import csv
import math
import os
import random
import statistics

from q6_median_of_medians import Counter, delivery_times, mom_select, quickselect_first, quickselect_random

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "Median_of_Medians", "results")
N = 10_001
SEEDS = 300
POOR, BAD, MIN_ROUND = 0.90, 0.75, 100


def classify(keeps):
    """(rounds with n >= 100, poor rounds, bad rounds, largest kept fraction, longest run of consecutive poor rounds)."""
    big = [(n, kept) for n, kept in keeps if n >= MIN_ROUND]
    poor = bad = run = longest = 0
    worst = 0.0
    for n, kept in big:
        f = kept / n
        worst = max(worst, f)
        bad += f > BAD
        if f > POOR:
            poor += 1
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return len(big), poor, bad, worst, longest


def percentile(values, p):
    """p-th percentile (nearest rank) of a list of numbers."""
    s = sorted(values)
    return s[min(len(s) - 1, max(0, math.ceil(p / 100 * len(s)) - 1))]


def run_many(label, runs):
    """runs = list of (comparisons, keeps, correct); returns a summary dict."""
    cpn = [c / N for c, _, _ in runs]
    stats = [classify(k) for _, k, _ in runs]
    rounds = sum(s[0] for s in stats)
    return {"method": label, "runs": len(runs), "min_cpn": round(min(cpn), 3),
            "median_cpn": round(statistics.median(cpn), 3), "mean_cpn": round(statistics.mean(cpn), 3),
            "p95_cpn": round(percentile(cpn, 95), 3), "p99_cpn": round(percentile(cpn, 99), 3),
            "max_cpn": round(max(cpn), 3), "rounds_n_ge_100": rounds,
            "poor_rounds_pct": round(100 * sum(s[1] for s in stats) / rounds, 2),
            "bad_rounds_pct": round(100 * sum(s[2] for s in stats) / rounds, 2),
            "runs_with_poor_round_pct": round(100 * sum(s[1] > 0 for s in stats) / len(runs), 1),
            "max_kept_fraction": round(max(s[3] for s in stats), 4),
            "longest_poor_streak": max(s[4] for s in stats),
            "all_correct": all(ok for _, _, ok in runs)}, cpn, [k / n for _, ks, _ in runs for n, k in ks
                                                             if n >= MIN_ROUND]


def main():
    os.makedirs(RESULTS, exist_ok=True)
    batch = delivery_times(N, seed=7)
    k = (N - 1) // 2
    truth = sorted(batch)[k]
    print("=" * 118)
    print(f"Q6(a) PIVOT QUALITY - median (k = {k:,}) of one batch of n = {N:,} delivery times")
    print(f"      a round is POOR if it keeps > 90 % of its elements, BAD if > 75 % (rounds with n >= {MIN_ROUND})")
    print("=" * 118)

    # 1. randomised QuickSelect: same input, 300 different seeds (randomness inside the algorithm)
    runs = []
    for s in range(1, SEEDS + 1):
        c, keeps = Counter(), []
        v = quickselect_random(batch, k, c, random.Random(s), keeps)
        runs.append((c.comparisons, keeps, v == truth))
    rnd, rnd_cpn, rnd_keep = run_many("QuickSelect random pivot (300 seeds, same batch)", runs)

    # 2. deterministic first-element pivot on 300 random shuffles (randomness in the INPUT)
    runs = []
    rng = random.Random(42)
    for _ in range(SEEDS):
        a = list(batch)
        rng.shuffle(a)
        c, keeps = Counter(), []
        v = quickselect_first(a, k, c, keeps)
        runs.append((c.comparisons, keeps, v == truth))
    fst, fst_cpn, _ = run_many("QuickSelect first pivot (300 shuffled batches)", runs)

    # 3. Median of Medians g = 5 on the same 300 shuffles (deterministic algorithm)
    runs = []
    rng = random.Random(42)
    for _ in range(SEEDS):
        a = list(batch)
        rng.shuffle(a)
        c, keeps = Counter(), []
        v = mom_select(a, k, c, 5, keeps)
        runs.append((c.comparisons, keeps, v == truth))
    mom, mom_cpn, mom_keep = run_many("Median of Medians g=5 (300 shuffled batches)", runs)

    # 4. the adversarial (sorted) batch for the deterministic rules
    srt = sorted(batch)
    adv = []
    for name, fn in (("QuickSelect first pivot", lambda a, c, kp: quickselect_first(a, k, c, kp)),
                     ("Median of Medians g=5", lambda a, c, kp: mom_select(a, k, c, 5, kp)),
                     ("QuickSelect random pivot (seed 1)",
                      lambda a, c, kp: quickselect_random(a, k, c, random.Random(1), kp))):
        c, keeps = Counter(), []
        v = fn(srt, c, keeps)
        r, p, b, w, longest = classify(keeps)
        adv.append({"input": "sorted batch", "method": name, "comparisons": c.comparisons,
                    "comparisons_per_n": round(c.comparisons / N, 2), "rounds_n_ge_100": r, "poor_rounds": p,
                    "max_kept_fraction": round(w, 4), "longest_poor_streak": longest, "correct": v == truth})

    summary = [rnd, fst, mom]
    print(f"\n[1] Comparisons per element (comparisons / n) over {SEEDS} runs each")
    print(f"{'method':<50}{'min':>7}{'median':>8}{'mean':>7}{'p95':>7}{'p99':>7}{'max':>7}{'max/min':>9}  correct")
    print("-" * 118)
    for r in summary:
        print(f"{r['method']:<50}{r['min_cpn']:>7.2f}{r['median_cpn']:>8.2f}{r['mean_cpn']:>7.2f}{r['p95_cpn']:>7.2f}"
              f"{r['p99_cpn']:>7.2f}{r['max_cpn']:>7.2f}{r['max_cpn'] / r['min_cpn']:>9.2f}  {r['all_correct']}")
    print(f"\n[2] Partition quality of every round with n >= {MIN_ROUND}")
    print(f"{'method':<50}{'rounds':>8}{'poor >90%':>11}{'bad >75%':>10}{'runs with poor':>16}{'max kept':>10}"
          f"{'longest poor run':>18}")
    print("-" * 118)
    for r in summary:
        print(f"{r['method']:<50}{r['rounds_n_ge_100']:>8,}{r['poor_rounds_pct']:>10.2f}%{r['bad_rounds_pct']:>9.2f}%"
              f"{r['runs_with_poor_round_pct']:>15.1f}%{r['max_kept_fraction']:>10.4f}{r['longest_poor_streak']:>18}")
    print(f"   MoM bound for the largest kept part: 7n/10 + 6 -> fraction <= 0.7 + 6/n = {0.7 + 6 / MIN_ROUND:.2f} "
          f"at n = {MIN_ROUND}, {0.7 + 6 / N:.4f} at n = {N:,}")

    print(f"\n[3] The SORTED batch (n = {N:,}) - an adversarial input for a deterministic pivot rule")
    print(f"{'method':<36}{'comparisons':>14}{'per n':>9}{'rounds':>8}{'poor':>7}{'max kept':>10}{'longest poor run':>18}"
          f"  correct")
    print("-" * 118)
    for r in adv:
        print(f"{r['method']:<36}{r['comparisons']:>14,}{r['comparisons_per_n']:>9.2f}{r['rounds_n_ge_100']:>8,}"
              f"{r['poor_rounds']:>7,}{r['max_kept_fraction']:>10.4f}{r['longest_poor_streak']:>18}  {r['correct']}")
    formula = 2 * (k + 1) * N - k * (k + 1)
    distinct = len(set(batch))
    print(f"   first pivot: every round removes only the pivot (and its {N - distinct} duplicate times, if any); for n "
          f"distinct values")
    print(f"   2(k+1)n - k(k+1) = {formula:,} comparisons = {formula / (N * N):.3f} n^2 -> Theta(n^2); the batch has "
          f"{distinct:,} distinct times")

    # chance that a random pivot is poor in the FIRST round (k = median): pivot rank in the lowest or highest 10 %
    print("\n[4] Why randomisation cannot eliminate poor rounds")
    print(f"   P(first round is poor) = P(pivot rank < 0.1n or > 0.9n) = 0.20 for the median; observed over all rounds:"
          f" {rnd['poor_rounds_pct']:.2f} %")
    print(f"   P(t consecutive poor rounds) ~ 0.2^t > 0 for every t: t = 5 -> {0.2 ** 5:.5f}, t = 10 -> {0.2 ** 10:.2e}")
    print("   -> the worst case Theta(n^2) keeps a non-zero probability; randomisation only makes it unlikely")
    print(f"   worst seed / best seed = {rnd['max_cpn'] / rnd['min_cpn']:.2f}x ; MoM worst / best input = "
          f"{mom['max_cpn'] / mom['min_cpn']:.2f}x and MoM max kept fraction {mom['max_kept_fraction']} <= 0.76")

    with open(os.path.join(RESULTS, "q6_pivot_quality.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)
    with open(os.path.join(RESULTS, "q6_pivot_quality_sorted.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(adv[0].keys()))
        w.writeheader()
        w.writerows(adv)
    with open(os.path.join(RESULTS, "q6_pivot_quality_runs.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "qs_random_cpn", "qs_first_shuffled_cpn", "mom_g5_shuffled_cpn"])
        for i in range(SEEDS):
            w.writerow([i + 1, round(rnd_cpn[i], 4), round(fst_cpn[i], 4), round(mom_cpn[i], 4)])
    with open(os.path.join(RESULTS, "q6_pivot_quality_keeps.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "kept_fraction"])
        w.writerows([("qs_random", round(x, 4)) for x in rnd_keep])
        w.writerows([("mom_g5", round(x, 4)) for x in mom_keep])
    print("\nCSV written: Median_of_Medians/results/q6_pivot_quality.csv, q6_pivot_quality_sorted.csv, "
          "q6_pivot_quality_runs.csv, q6_pivot_quality_keeps.csv")


if __name__ == "__main__":
    main()
