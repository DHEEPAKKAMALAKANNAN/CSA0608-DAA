# Q6 – Student A: Median of Medians (primary contributor: Student A)

**Scenario – SLA reporting.** The drone-delivery dashboard must report the median and the 90th-percentile delivery
time of every batch of n deliveries (n up to 1,000,000) within a *guaranteed* worst-case time (k-th smallest element).

- Code: `../Implementation_Code/q6_median_of_medians.py` (Median of Medians, randomised and first-element QuickSelect,
  sort-then-pick, demo + experiments), `../Implementation_Code/q6_pivot_quality.py` (pivot-quality study),
  tests in `../Implementation_Code/q6_tests.py`, graphs in `../Implementation_Code/q6_graphs.py`
- Pseudocode and flowcharts: `../Pseudocode/Q6_Advanced_DC_Pseudocode.md`, `../Pseudocode/q6_flowchart_median_of_medians.png`,
  `../Pseudocode/q6_flowchart_quickselect.png`
- Data and graphs: `results/` (`q6_mom_comparisons.csv`, `q6_mom_worstcase.csv`, `q6_pivot_quality*.csv`, `*.png`)
- Screenshots: `../Output_Screenshots/q6_median_of_medians_*.png`, `q6_pivot_quality_output.png`, `q6_tests_output.png`

## The official bullets in brief

| Bullet | Answer (evidence) |
|---|---|
| Implement MoM for the k-th smallest | `mom_select(a, k, counter, group=5)`; every one of 72 experiment results and all test ranks equal `sorted(a)[k]` |
| Grouping strategy | ⌈n/5⌉ groups of 5, each insertion-sorted (≤ 10 comparisons), middle element = group median; g = 3 is Θ(n log n) (13.42n at 10⁶ and growing), g = 5 and g = 7 linear (10.05n, 10.11n) |
| Pivot determination | pivot = median of the group medians, found by a recursive call on n/5 values |
| Disastrous partitions prevented | ≥ 3n/10 − 6 values lie on each side of the pivot → kept part ≤ 7n/10 + 6; measured largest kept fraction 0.5584 (300 shuffles, n = 10,001) and 0.598 (n ≥ 100, all sizes) |
| Compare against QuickSelect | random pivot: 4.4–7.2n comparisons on average, ≈ 4× faster, but 2.23n … 10.27n over 300 seeds (4.6× spread); MoM 9–10n on random data |
| Deterministic poor-pivot strategy | first element on a sorted batch: exactly 2(k+1)n − k(k+1) ≈ 3n²/4 comparisons (750,500 / 3,001,000 / 12,002,000 for n = 1,000 / 2,000 / 4,000); 7,481n at n = 10,001 (4,985 of 4,986 rounds poor) vs 7.29n for MoM |
| Randomisation reduces, does not eliminate | P(poor round) ≈ 0.2 for the median; observed 17.81 % poor rounds, 79.3 % of runs with ≥ 1 poor round, streaks up to 4; P(t poor rounds in a row) ≈ 0.2ᵗ > 0 |
| Worst-case guarantee | T(n) ≤ T(⌈n/5⌉) + T(7n/10 + 6) + cn; recursion tree (9/10)ⁱcn → T(n) ≤ 10cn = Θ(n); substitution with d = 20c for n ≥ 140 |

**Student B verification – why pivot quality is central:** the cost of selection is the sum of the round sizes
n + n₁ + n₂ + …; a pivot that keeps a constant fraction α < 1 gives n/(1 − α) (linear), an extreme pivot gives ≈ n²/2.
Same partition code and same batch: MoM 7.29n, random pivot 4.88n, first-element pivot 7,481n.

**Decision:** the dashboard uses Median of Medians with groups of 5 (guaranteed linear; about 1.1 s per selection at
10⁶ in pure Python on a quiet machine, 2.3 s in the loaded measurement run), ideally wrapped as an introselect
(random pivot first, MoM fallback when a round shrinks too little).
