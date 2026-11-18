# SwiftLogix – Final Algorithmic Design (CO3 case study, Part 6 at a glance)

V. Vasudevan · 192425324 · CSA06. The full derivations and evidence are in `CO3_AT3_Case_Study_Report` (Parts 4–6);
all figures below come from `Supporting_Files/production_workload.py` and the experiment CSVs in
`Supporting_Files/results/`. Machine model: 10⁸ basic operations per second, 1 MB = 10⁶ bytes.

| Module | Final design | Time complexity | Production operations → time | Memory (production) | Throughput |
|---|---|---|---|---|---|
| M1 nightly event sort (5,000,000 events) | stable **natural merge sort** on (8-byte key, 4-byte index) pairs; insertion cutoff 16 for short runs | O(n log r) for r runs, worst O(n log n) | 34,999,999 comparisons + 60,000,000 moves → 0.95 s | 120,000,000 B (120 MB) | ≈ 5.3 M events/s |
| M2 dispatch ranking (2,000,000 orders, scores 0–100) | **introsort-style quick sort**: median of 3 random elements, Dijkstra 3-way partition, insertion ≤ 16, recursion on the smaller side, heap-sort fallback after 2⌊lg n⌋ levels | Θ(n log k) expected (k = 101), O(n log n) worst, O(log n) stack | 19,962,967 comparisons → 0.20 s per cycle | 16,000,000 B (16 MB), ≤ 21 stack frames | ≈ 5 rankings/s (1-s budget met 5×) |
| M3 tracking lookup (10,000,000 IDs, 20,000,000 lookups/day) | sorted array of 16-byte entries + **guarded interpolation search**; plain iterative **binary search** as guarantee/fallback; same-day delta array | O(log n) worst (≤ 24 comparisons; ≤ 2(⌊lg n⌋+1) probes guarded), ≈ O(log log n) typical | ≤ 480,000,000 comparisons/day → 4.8 s/day (3.9 s guarded) | 160,000,000 B (160 MB) | ≈ 416,000 lookups/s per core (cache-miss bound) |
| M4 forecasting (1,024 × 1,024) | **hybrid Strassen**: naive below a tuned cutoff n₀ (8 by operation count, 64 measured in Python), minimal padding to s·2ᵈ | Θ(n^2.807) | 1,100,550,336 operations (n₀ = 8) → 11.01 s; naive 21.46 s | ≈ 65,000,000 B (65 MB) vs 25.2 MB naive | ≈ 327 forecasts/hour |

**Total working memory** of the final design ≈ 120 + 16 + 160 + 65 = **361 MB**.

**Why these designs.** Each keeps the divide-and-conquer core designed in Part 2 and adds the safeguard that the
experiments showed to be necessary:

- M1 – the nightly file is 64 already time-ordered hub feeds; run detection turns the sort into a 6-pass merge
  (1.64× fewer comparisons, 2.3× faster than top-down at n = 131,072) while staying stable; (key, index) pairs cut
  memory from 640 MB to 120 MB.
- M2 – the Part 2 baseline is quadratic on sorted and all-equal input (exactly n(n−1)/2, depth n − 1) and on
  duplicate-heavy scores (≈ n²/(2k)); 3-way partitioning + random sampling + the heap-sort fallback make it
  O(n log n) in all cases and about 65× cheaper on the real score distribution.
- M3 – binary search is optimal in comparisons but each of its 24 probes is a likely cache miss; guarded
  interpolation needs ~6 probes on uniformly issued IDs and stays bounded on clustered IDs, where plain
  interpolation degrades to thousands of probes.
- M4 – pure Strassen beats the naive operation count only at n = 1,024; with a cutoff it wins from n = 16 and
  halves the work at n = 1,024; minimal padding avoids up to 6.35× waste for zone counts that are not powers of two.

**Recommendations.** Tune the cutoffs on the production machine; monitor run count, duplicate share, ID
distribution and zone count; use an external k-way merge for M1 if volumes exceed memory; consider a
cache-friendly (Eytzinger/B-tree) index layout for M3 at much higher query rates; adopt Winograd's 15-addition
variant and parallel M1–M7 products for M4; keep `run_all_tests.py` (65 tests, including closed-form operation
counts) in the build pipeline.
