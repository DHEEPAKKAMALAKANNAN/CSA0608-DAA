# Q7 – Day-4 Design Challenge: Diagnose, Redesign and Validate — Design Notes and Pseudocode

*Selected solution: **Q4 Brute-Force Closest Pair (drone collision-risk monitoring)**. These notes were written
after the Q1–Q6 evidence was collected and **before** the redesign was implemented. The diagnosis numbers quoted here
come from `Q4_Brute_Force_Closest_Pair/Implementation_Code/results/q4_growth.csv` and are re-measured by
`q7_diagnosis.py`.*

## Why Q4 (and not the others)

| Candidate | Limitation seen in my evidence | Chosen? |
|---|---|---|
| Q1 sorting | quadratic, but Insertion Sort already adapts to the real (nearly sorted) data | no |
| Q2 sequential search | linear per lookup; fixed by a standard index (little algorithmic design) | no |
| Q3 string matching | m(n−m+1) only on adversarial text; real logs ≈ 1.1 comparisons per shift | no |
| **Q4 closest pair** | **exactly n(n−1)/2 distance calculations on every input; the 100 ms limit is reached at ≈ 1 250–1 450 drones (depending on machine load)** | **yes** |
| Q5 convex hull | Θ(n³), but reserves have tens of stations, so n is small in practice | no |
| Q6 exhaustive search | 2ⁿ – the limitation is the problem's solution space itself | no |

## A. Diagnosis (evidence from Q4)

* **Where the effort goes:** 100 % of the work is in the inner loop – one distance calculation per pair:
  49 995 000 calculations at n = 10 000 (≈ 5–6 s in my environment).
* **Which operation grows:** the number of distance calculations, n(n−1)/2 ∈ Θ(n²); ×4 for every doubling of n.
* **Useful work is tiny:** at n = 10 000 only **20** of the 49 995 000 calculations improved the best-so-far answer.
  The final closest distance δ\* is 0.62 m in a 10 000 m area, so for almost every pair the **x-difference alone** is
  already thousands of times larger than δ\*. These pairs cannot possibly be the answer, yet the algorithm still
  computes their full distance.
* **Unnecessary repetition:** the algorithm already *knows* a good bound (the best distance so far, δ) after a few
  pairs, but never uses it to skip anything – every later pair is still examined in full. It also uses no ordering:
  drones that are far apart are compared as eagerly as neighbours.
* **Characteristic that causes the limitation:** the candidate set is *all pairs* and it is fixed in advance,
  independent of the geometry of the data and of the information gathered while running.

## B. Design objective (measurable)

1. Return **exactly the same closest distance** as the brute force on every test dataset.
2. Reduce the number of **distance calculations by at least 100×** at n = 10 000 for the uniform fleet
   (from 49 995 000 to < 500 000), and avoid *examining* (even cheaply) most pairs, not just skip the arithmetic.
3. Time: process at least **5× more drones within the 100 ms response limit** defined in Q4
   (≈ 1 250–1 450 drones for the brute force → at least ≈ 7 000 drones).

## C. Redesigned strategy – "sort once, sweep, stop when the gap is too large"

What changes and why:

* **Exploit ordering (preprocessing):** sort the drones once by one coordinate. Θ(n log n) key comparisons, done
  with a hand-written merge sort so that its cost is counted.
* **Choose the sweep axis from the data:** sort along the axis with the larger spread (max − min). A north–south
  corridor (all x almost equal) is then swept along y, where drones are spread out.
* **Reuse previously computed information:** keep δ² = best squared distance so far. When drone *i* is compared with
  the drones after it in sorted order, the gap along the sweep axis only grows, so as soon as gap² ≥ δ² **no later
  drone can be closer** → `break` (all remaining pairs for *i* are never examined).
* **Cheap filter before the full distance:** if the gap on the *other* axis alone already satisfies gap² ≥ δ², the
  pair cannot improve δ → skip the full distance calculation.
* **Extra memory:** O(n) for the sorted index array and coordinate lists (brute force: O(1)).
* **New trade-offs:** a sorting cost is paid even for small n; the work now depends on the data distribution; for
  drones spread along *both* axes in degenerate ways (two straight perpendicular routes) many drones share the same
  sweep coordinate, the gap test cannot prune, and the examined pairs remain Θ(n²) (distance calculations are still
  cut by the second filter).

Pseudocode:

```
Algorithm SweepClosestPair(D, n)                 // D[k] = (x_k, y_k), n >= 2
1.  if spread(x) >= spread(y) then a = x, b = y else a = y, b = x      // sweep axis
2.  order = MergeSortIndices(0..n-1, key = a)                         // counted key comparisons
3.  best2 = +infinity ; pair = none
4.  for p = 0 to n-2 do
5.      i = order[p]
6.      for q = p+1 to n-1 do
7.          j = order[q] ; candidates = candidates + 1
8.          ga = a[j] - a[i]                     // >= 0 because of the sort
9.          if ga*ga >= best2 then break         // every later drone is even farther away: stop
10.         gb = b[j] - b[i]
11.         if gb*gb >= best2 then continue      // other-axis gap alone too large: no full distance
12.         d2 = ga*ga + gb*gb ; distanceCalcs = distanceCalcs + 1
13.         if d2 < best2 then best2 = d2 ; pair = (i, j)
14. return pair, sqrt(best2), sortComparisons, candidates, distanceCalcs
```

Correctness argument: a pair (i, j) is skipped only when gap² ≥ δ² on one axis, and then
d(i, j)² = gap<sub>a</sub>² + gap<sub>b</sub>² ≥ δ², so it cannot be *strictly* closer than the current best; the `break` is
valid because the sweep-axis gap of every later drone is at least as large. Hence no pair that could improve δ is
ever discarded, and the final δ equals the true minimum.

## D. Prediction before implementing

* **Uniform fleet (n = 10 000):** δ quickly falls to a few metres or less, so each drone's window (drones within δ
  along the sweep axis) contains on average less than one other drone. I predict ≈ 1–3 candidate pairs per drone
  (≈ 10 000–30 000 examined pairs) and fewer than 2 n = 20 000 distance calculations, plus ≈ n log₂ n ≈ 120 000 sort
  comparisons. **Distance calculations should drop by > 2 000× and total key operations by ≈ 200–300×.**
* **Clustered fleet:** same behaviour (δ is even smaller inside the dense hubs).
* **Corridor:** with axis selection the sweep runs along y and behaves like the uniform case; with a fixed x-axis
  sweep (ablation) the pruning would weaken badly.
* **Cross (two exact perpendicular routes):** the n/2 drones on the north–south route share one x value, so the gap
  test never prunes them: predicted ≈ (n/2)²/2 = n²/8 examined pairs – only ≈ 4× fewer than brute force – but the
  second filter keeps distance calculations close to linear.
* **Time:** improvement smaller than the count reduction because the hand-written merge sort dominates; I predict
  ≈ 50–100× faster at n = 10 000 and ≥ 10 000 drones within 100 ms.
