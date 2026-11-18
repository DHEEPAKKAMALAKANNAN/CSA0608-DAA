# Q2 – Merge Sort and Quick Sort: pseudocode (written before implementation)

**Scenario.** The dispatch scheduler sorts pending delivery orders by deadline. Input conditions: random, already
sorted, reversed, many equal deadlines (15-minute slots), all equal.

## 1. Merge Sort

- **Divide:** split A[lo..hi] at mid = ⌊(lo + hi)/2⌋ (no comparisons).
- **Conquer:** sort A[lo..mid] and A[mid+1..hi] recursively; a list of one order is sorted.
- **Combine:** merge the two sorted halves (at most n − 1 comparisons, n element copies out and n back).

```
Algorithm MergeSort(A, lo, hi)
1. if lo >= hi then return                     // 0 or 1 order
2. mid = floor((lo + hi) / 2)                  // DIVIDE
3. MergeSort(A, lo, mid)                       // CONQUER
4. MergeSort(A, mid + 1, hi)
5. Merge(A, lo, mid, hi)                       // COMBINE

Algorithm Merge(A, lo, mid, hi)
1. copy A[lo..hi] to AUX[lo..hi]               // hi - lo + 1 moves
2. i = lo;  j = mid + 1
3. for k = lo to hi do                         // hi - lo + 1 moves
4.     if i > mid then A[k] = AUX[j];  j = j + 1
5.     else if j > hi then A[k] = AUX[i];  i = i + 1
6.     else if AUX[j] < AUX[i] then A[k] = AUX[j];  j = j + 1     // one comparison
7.     else A[k] = AUX[i];  i = i + 1                             // ties take the left order: stable
```

**Recurrence (comparisons, worst case):** C(n) = 2C(n/2) + (n − 1), C(1) = 0 ⇒ C(n) = n log₂ n − n + 1 for n = 2ᵏ;
best case (sorted or reversed) C(n) = 2C(n/2) + n/2 ⇒ (n/2) log₂ n. Moves: M(n) = 2M(n/2) + 2n ⇒ 2n log₂ n.

## 2. Quick Sort (Lomuto partition) with three pivot rules

- **Divide:** choose a pivot (last element / random element / median of first, middle, last), move it to A[hi],
  partition into A[lo..p−1] ≤ pivot < A[p+1..hi] (hi − lo comparisons).
- **Conquer:** sort both parts recursively.
- **Combine:** nothing — the pivot is already in its final position.

```
Algorithm QuickSort(A, lo, hi, rule)
1. if lo >= hi then return
2. p = Partition(A, lo, hi, rule)              // DIVIDE
3. QuickSort(A, lo, p - 1, rule)               // CONQUER
4. QuickSort(A, p + 1, hi, rule)               // (no combine step)

Algorithm Partition(A, lo, hi, rule)
1. if rule = 'random'  then swap A[random(lo..hi)], A[hi]
2. if rule = 'median3' then swap A[median index of A[lo], A[mid], A[hi]], A[hi]    // 2-3 comparisons
3. x = A[hi];  i = lo - 1
4. for j = lo to hi - 1 do                     // one comparison per element
5.     if A[j] <= x then i = i + 1;  swap A[i], A[j]
6. swap A[i+1], A[hi]
7. return i + 1
```

**Recurrences:** best/balanced T(n) = 2T(n/2) + (n − 1) ⇒ Θ(n log n); worst (pivot always the largest or smallest,
e.g. last element on sorted data, or any rule on all-equal data with Lomuto's "≤") T(n) = T(n − 1) + (n − 1) ⇒
n(n − 1)/2 = Θ(n²); average with a random pivot T(n) = (n − 1) + (2/n) Σ T(k) ⇒ 2(n + 1)Hₙ − 4n ≈ 1.39 n log₂ n.

Decomposition diagrams: `../Implementation_Code/results/q2_mergesort_tree.png`, `q2_quicksort_trees.png`.
