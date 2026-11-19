# Q2 – The Quality of Decomposition in Sorting: pseudocode and flowcharts

**Scenario.** The dispatch scheduler of the drone-delivery operations centre sorts pending delivery orders by deadline.
**Stated Quick Sort pivot strategy (shared decision): the LAST element of the sub-array, Lomuto partition.**
Random and median-of-three pivots are implemented only as comparison points for the joint design question.

Code: `../Implementation_Code/q2_sorting.py` (algorithms, counters, `record` of partition sizes, `designed_input`),
`q2_partition_study.py` (Student A's balanced / unbalanced study), `q2_experiments.py`, `q2_tests.py`.

## 1. Merge Sort

- **Divide:** split A[lo..hi] at mid = ⌊(lo + hi)/2⌋ – by position, independent of the data.
- **Conquer:** sort A[lo..mid] and A[mid+1..hi] recursively; a list of 0 or 1 order is sorted (base case).
- **Combine:** merge the two sorted halves (at most m − 1 comparisons, m copies out and m back; stable).

```
Algorithm MergeSort(A, lo, hi)
1. if lo >= hi then return                     // base case: 0 or 1 order
2. mid = floor((lo + hi) / 2)                  // DIVIDE (halves ceil(m/2) | floor(m/2))
3. MergeSort(A, lo, mid)                       // CONQUER
4. MergeSort(A, mid + 1, hi)
5. Merge(A, lo, mid, hi)                       // COMBINE

Algorithm Merge(A, lo, mid, hi)
1. copy A[lo..hi] to AUX[lo..hi]
2. i = lo;  j = mid + 1
3. for k = lo to hi do
4.     if i > mid then A[k] = AUX[j];  j = j + 1
5.     else if j > hi then A[k] = AUX[i];  i = i + 1
6.     else if AUX[j] < AUX[i] then A[k] = AUX[j];  j = j + 1     // one comparison
7.     else A[k] = AUX[i];  i = i + 1                             // ties take the left order: stable
```

Flowchart: `q2_flowchart_merge_sort.png`. Recurrence: C(n) = 2C(n/2) + (n − 1) ⇒ n log₂ n − n + 1 (worst), depth ⌈log₂ n⌉.

## 2. Quick Sort, pivot = last element (Lomuto)

- **Divide:** pivot x = A[hi]; partition into A[lo..p−1] ≤ x < A[p+1..hi] (m − 1 comparisons); record (L, R).
- **Conquer:** sort both parts recursively. **Combine:** nothing – the pivot is in its final place.

```
Algorithm QuickSort(A, lo, hi)
1. if lo >= hi then return                     // base case
2. p = Partition(A, lo, hi)                    // DIVIDE (by value)
3. record (depth, p - lo, hi - p)              // partition sizes L | R (instrumentation)
4. QuickSort(A, lo, p - 1)                     // CONQUER
5. QuickSort(A, p + 1, hi)                     // no combine step

Algorithm Partition(A, lo, hi)
1. x = A[hi];  i = lo - 1                      // pivot = last element
2. for j = lo to hi - 1 do                     // one comparison per key
3.     if A[j] <= x then i = i + 1;  swap A[i], A[j]
4. swap A[i+1], A[hi]                          // pivot to its final place
5. return i + 1
```

Flowchart: `q2_flowchart_quick_sort.png`. Recurrence: T(n) = T(L) + T(R) + (n − 1) with L + R = n − 1.

## 3. Student A – designing inputs for the last-element pivot

```
Algorithm DesignInput(V[0..m-1] sorted, f)      // f = 0.5 balanced, f = 0.9 for 90:10
1. if m <= 1 then return V
2. r = floor((m - 1) / 2) if f = 0.5 else floor(f (m - 1))     // rank of the pivot in this sub-array
3. DL = DesignInput(V[0..r-1], f);   DR = DesignInput(V[r+1..m-1], f)
4. R = [last of DR] + DR without its last element   // Lomuto's final swap moves R[0] to the end
5. return DL + R + [V[r]]                        // pivot placed LAST
```

- Balanced input (f = 0.5): every pivot is the median → L | R = ⌊(m−1)/2⌋ | ⌈(m−1)/2⌉, depth log₂(n+1) − 1.
- Severely unbalanced input: the already sorted export → every pivot is the maximum → (m−1) | 0, depth n − 1.

Decomposition diagrams: `../Implementation_Code/results/q2_mergesort_tree.png`, `q2_quicksort_trees.png`;
partition evidence: `q2_partition_depth.png`.
