# Q6 – Student B: Meet-in-the-Middle Subset-Sum (primary contributor: Student B)

**Scenario – payload packing.** A drone with payload capacity W grams must carry the heaviest subset of n waiting
parcels whose total does not exceed W (an exact fill is ideal); n is up to 40.

- Code: `../Implementation_Code/q6_meet_in_the_middle.py` (brute force, Meet-in-the-Middle with binary-search and
  two-pointer combine, store-k trade-off variant, DP reference, demo + experiments),
  `../Implementation_Code/q6_mitm_memory.py` (memory and time–memory trade-off), tests in `../Implementation_Code/q6_tests.py`,
  graphs in `../Implementation_Code/q6_graphs.py`
- Pseudocode and flowchart: `../Pseudocode/Q6_Advanced_DC_Pseudocode.md`, `../Pseudocode/q6_flowchart_meet_in_the_middle.png`
- Data and graphs: `results/` (`q6_mitm_growth.csv`, `q6_mitm_limits.csv`, `q6_mitm_memory.csv`, `q6_mitm_tradeoff.csv`, `*.png`)
- Screenshots: `../Output_Screenshots/q6_meet_in_the_middle_*.png`, `q6_mitm_memory_output.png`, `q6_tests_output.png`

## The official bullets in brief

| Bullet | Answer (evidence) |
|---|---|
| How the problem is divided | the parcel set is split into half 1 (first ⌊n/2⌋) and half 2; every subset = (subset of half 1, subset of half 2) |
| Subset results for both halves | `sorted_subset_sums`: start [0], for each parcel merge L with L + w → 2^(n/2) sums per half, already sorted |
| Combine / search | for each a ≤ W of half 1 binary-search the largest b ≤ W − a of half 2 (≈ n/2 probes); or one two-pointer scan |
| Search-space size | 2 · 2^(n/2) stored sums instead of 2ⁿ subsets (2,097,152 vs 1.1 × 10¹² at n = 40); time Θ(n·2^(n/2)) or Θ(2^(n/2)) |
| Additional memory | Θ(2^(n/2)); measured peak 29.1 KiB (n = 16) → 11,456.5 KiB (n = 32), ×4 per 4 parcels, ≈ 90 bytes per stored sum → 0.17 GiB at n = 40, 5.6 GiB at 50, 179 GiB at 60; brute force 0.2–0.3 KiB |
| Compare with 2ⁿ enumeration | n = 24: 33,554,431 vs 70,897 operations (473×), 8.098 s vs 0.016 s; within 2 s: brute force 20 parcels, MitM binary 36, MitM two-pointer 40 |
| Time–memory trade-off | store k parcels (2ᵏ sums), enumerate n − k: at n = 26, k = 8 → 256 sums / 2.10 M ops, k = 13 → 8,192 / 0.15 M, k = 20 → 1,048,576 / 3.15 M; balanced split is optimal, fewer stored parcels trade memory for time |

**Student A verification – why MitM reduces work despite extra storage:** brute force pairs every subset of half 1
with every subset of half 2 (a product, 2^(n/2) · 2^(n/2)); storing one half's sums sorted lets each subset of the
other half find its best partner by binary search, so the work becomes a sum (2^(n/2) + 2^(n/2), plus n/2 per lookup).

**Decision:** two-pointer Meet-in-the-Middle (40 parcels in 1.86 s in the loaded run, about 0.17 GiB extra memory);
if memory is scarce, the store-k variant with a smaller k.
