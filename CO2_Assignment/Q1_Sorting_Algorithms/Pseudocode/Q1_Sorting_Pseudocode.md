# Q1 – Sorting Under Different Data Conditions: Pseudocode and Pre-Implementation Notes

*Written before any code was implemented or run. Every prediction below is checked against the measured
counts in `../Implementation_Code/results/` and in the final report.*

## 1. Problem model

* An **order record** is `(priority_score, order_id)`. Orders are dispatched in **ascending** priority score
  (score 1 = dispatch first). Only the score is compared; the `order_id` lets us check *stability*.
* **Basic operations counted** (primary evidence):
  * `comparisons` – one key comparison between two priority scores;
  * `swaps` (Selection, Bubble) / `shifts` (Insertion) – the algorithm's own data-movement step;
  * `writes` – number of array slots written (a swap writes 2 slots, an insertion shift writes 1 slot,
    placing the saved key writes 1 slot only if it actually moved);
  * `passes` – outer-loop passes actually executed.
* Execution time (`time.perf_counter`, median of repeats) is secondary evidence only.

## 2. Predictions (made before implementation) and the algorithmic reason

Let *n* be the number of orders and *I* the number of **inversions** (pairs *i < j* with `score[i] > score[j]`).

| Input arrangement | Selection Sort | Bubble Sort (early-exit flag) | Insertion Sort |
|---|---|---|---|
| Already sorted | n(n−1)/2 comparisons, 0 swaps | 1 pass, n−1 comparisons, 0 swaps | n−1 comparisons, 0 shifts |
| Random | n(n−1)/2 comparisons, ≈ n swaps | ≈ n²/2 comparisons, ≈ n²/4 swaps | ≈ n²/4 comparisons and shifts |
| Reverse sorted | n(n−1)/2 comparisons, ⌊n/2⌋ swaps | n(n−1)/2 comparisons **and** swaps | n(n−1)/2 comparisons and shifts |
| 95 % sorted + 5 % new batch at end | n(n−1)/2 comparisons | still ≈ n²/2 comparisons (see below) | ≈ n + I comparisons, I small-ish |
| One urgent order appended at end | n(n−1)/2 comparisons | n−1 passes → n(n−1)/2 comparisons | ≈ 2(n−1) comparisons, n−1 shifts |
| Few distinct scores (duplicates) | n(n−1)/2 comparisons | ≈ quadratic, but fewer passes | ≈ n + I comparisons |

**Reasons.**

1. **Selection Sort is not adaptive.** To find the minimum of the unsorted suffix it must look at *every*
   element of that suffix, whatever the order: Σ<sub>i=0</sub><sup>n−2</sup>(n−1−i) = n(n−1)/2 comparisons in every case.
   Its strength is data movement: at most one swap per pass, ≤ n−1 swaps in total.
2. **Bubble Sort (with the "swapped" flag) is adaptive only to *how far elements must travel left*.** One pass
   moves every out-of-place element only **one** position to the left, but carries a large element all the way
   right. The number of passes is therefore 1 + (largest number of bigger elements that precede any one element).
   A single small, high-priority order at the end of the list (a "turtle") forces n−1 passes, so the early exit
   gives almost no saving. Swaps always equal *I*.
3. **Insertion Sort does work proportional to the disorder.** Each shift removes exactly one inversion, so
   `shifts = I` and `comparisons = I + (n−1) − F`, where *F* is the number of keys that become a new strict
   minimum (they stop at position 0 without a final failing comparison). With few inversions it is almost linear.
4. **Prediction for the fulfilment-centre case:** Insertion Sort will be the clear winner; Bubble Sort will look
   good on swaps but *not* on comparisons, because the new orders sit at the end of the list and must travel left;
   Selection Sort will cost the same n(n−1)/2 comparisons as for random data.

## 3. Designed input conditions

| Id | Name | Construction (seeded, reproducible) | Why it exposes a difference |
|---|---|---|---|
| D1 | **Contrast A – Reverse sorted** ("significantly disordered") | scores n, n−1, …, 1 | maximum inversions n(n−1)/2: worst case for Bubble/Insertion, Selection unchanged |
| D2 | **Contrast B – 95 % sorted + 5 % new batch** | 95 % of the orders sorted, then a batch of 5 % new orders with random scores appended | the real operating condition: low disorder, but disorder sits at the end |
| D3 | **Edge case – single urgent order at end** | n−1 sorted orders, then one order with the smallest score | only n−1 inversions, but the element must travel the whole list: separates Bubble from Insertion |
| R | Random (baseline) | uniformly random scores | typical "randomly ordered" input |
| S | Already sorted (baseline) | scores 1..n | best case for adaptive algorithms |
| E2 | Few distinct scores (duplicates edge case) | scores drawn from {1..5} | many equal keys: tests "strict >" handling and stability |

Sizes: n = 100, 1 000, 5 000 (enough to see quadratic growth while keeping pure-Python runs short).

## 4. Pseudocode

### 4.1 Selection Sort (counts comparisons and swaps)
```
SELECTION-SORT(A[0..n−1])
    comparisons ← 0 ; swaps ← 0
    for i ← 0 to n−2 do
        min ← i
        for j ← i+1 to n−1 do                 // scan the whole unsorted suffix
            comparisons ← comparisons + 1
            if A[j].score < A[min].score then min ← j
        if min ≠ i then                       // at most one exchange per pass
            swap A[i], A[min] ; swaps ← swaps + 1
    return A, comparisons, swaps
```

### 4.2 Bubble Sort with early-exit flag
```
BUBBLE-SORT(A[0..n−1])
    comparisons ← 0 ; swaps ← 0 ; passes ← 0
    for p ← 0 to n−2 do
        swapped ← false ; passes ← passes + 1
        for j ← 0 to n−2−p do                 // largest unsorted key bubbles to position n−1−p
            comparisons ← comparisons + 1
            if A[j].score > A[j+1].score then  // strict ">" keeps equal keys in order (stable)
                swap A[j], A[j+1] ; swaps ← swaps + 1 ; swapped ← true
        if not swapped then break             // early exit: list already sorted
    return A, comparisons, swaps, passes
```

### 4.3 Insertion Sort
```
INSERTION-SORT(A[0..n−1])
    comparisons ← 0 ; shifts ← 0
    for i ← 1 to n−1 do
        current ← A[i] ; j ← i − 1
        while j ≥ 0 do
            comparisons ← comparisons + 1
            if A[j].score > current.score then // strict ">" → stable, no work for equal keys
                A[j+1] ← A[j] ; shifts ← shifts + 1 ; j ← j − 1
            else break
        A[j+1] ← current
    return A, comparisons, shifts
```

### 4.4 Exact predictions computed from the data (used to cross-check the counters)
```
INVERSION-PROFILE(scores)          // Fenwick tree, O(n log n) – NOT part of the sorting algorithms
    I ← total inversions ; L ← max over k of (#earlier scores > scores[k]) ; F ← #new strict minima
    predicted selection comparisons = n(n−1)/2
    predicted bubble passes P = min(L+1, n−1);  comparisons = P(n−1) − P(P−1)/2;  swaps = I
    predicted insertion shifts = I;  comparisons = I + (n−1) − F
```

## 5. Complexity summary (derived in the report)

| Algorithm | Best | Average | Worst | Swaps / moves | Stable |
|---|---|---|---|---|---|
| Selection | Θ(n²) | Θ(n²) | Θ(n²) | O(n) | No |
| Bubble (flag) | Θ(n) | Θ(n²) | Θ(n²) | Θ(I) swaps | Yes |
| Insertion | Θ(n) | Θ(n²) | Θ(n²) | Θ(I) shifts | Yes |
