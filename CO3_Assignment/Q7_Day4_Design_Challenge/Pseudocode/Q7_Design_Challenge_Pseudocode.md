# Q7 – Day-4 Design Challenge: pseudocode of both proposals and the joint design

**Diagnosed limitation (from Q2).** Textbook quick sort (Lomuto, last-element pivot) needs n(n − 1)/2 comparisons and
recursion depth n − 1 on sorted, reversed and all-equal order lists; all three Q2 pivot rules stay quadratic on
all-equal lists and degrade on slot-heavy lists (Lomuto puts every key equal to the pivot on one side).

## Proposal A (Student A) – median-of-three + Hoare partition + smaller-part recursion

- **Divide:** pivot v = median of A[lo], A[mid], A[hi]; Hoare's two pointers stop on keys equal to v, so a run of
  equal keys is split in the middle.
- **Conquer:** recurse into the smaller part only; the larger part is handled by the loop (depth ≤ log₂ n).
- **Combine:** nothing.

```
Algorithm QuickSortA(A, lo, hi)
1. while lo < hi do
2.     v = MedianOfThree(A, lo, hi)              // orders A[lo] <= A[mid] <= A[hi]; v = A[mid]
3.     i = lo - 1;  j = hi + 1
4.     loop
5.         repeat i = i + 1 until A[i] >= v      // stops on equal keys
6.         repeat j = j - 1 until A[j] <= v
7.         if i >= j then break
8.         swap A[i], A[j]
9.     if j - lo < hi - j then QuickSortA(A, lo, j);  lo = j + 1     // smaller part recursively
10.    else QuickSortA(A, j + 1, hi);  hi = j                         // larger part by the loop
```

## Proposal B (Student B) – random pivot + Dijkstra 3-way partition + insertion sort for ≤ 16

- **Divide:** v = random element; one pass splits A into < v | = v | > v.
- **Conquer:** recurse on < v and > v only (the = v block is finished); parts of ≤ 16 orders use insertion sort.
- **Combine:** nothing.

```
Algorithm QuickSortB(A, lo, hi)
1. if hi - lo + 1 <= 16 then InsertionSort(A, lo, hi);  return
2. v = A[random(lo..hi)];  lt = lo;  i = lo;  gt = hi
3. while i <= gt do
4.     if A[i] < v then swap A[lt], A[i];  lt = lt + 1;  i = i + 1
5.     else if A[i] > v then swap A[i], A[gt];  gt = gt - 1
6.     else i = i + 1                             // equal to the pivot: final region
7. QuickSortB(A, lo, lt - 1);  QuickSortB(A, gt + 1, hi)
```

## Joint final design – introsort-style hybrid

- **Divide:** v = median of three (A); **fat partition** (Bentley–McIlroy): A's two-pointer scan, but keys equal to v
  are parked at both ends and swapped to the middle afterwards (B's 3-way idea).
- **Conquer:** smaller part recursively, larger part by the loop (A); parts of ≤ 16 orders by insertion sort (B);
  a path that uses more than 2⌊log₂ n⌋ partition levels is finished by heapsort (joint guard).
- **Combine:** nothing.

```
Algorithm HybridSort(A, n)
1. Sort(A, 0, n - 1, budget = 2 * floor(log2 n))

Algorithm Sort(A, lo, hi, budget)
1. while hi - lo + 1 > 16 do
2.     if budget = 0 then HeapSort(A, lo, hi);  return          // O(m log m) safety net
3.     budget = budget - 1
4.     v = MedianOfThree(A, lo, hi)                             // from A
5.     (lt, gt) = FatPartition(A, lo, hi, v)                    // A[lt..gt] = v are finished
6.     if lt - lo < hi - gt then Sort(A, lo, lt - 1, budget);  lo = gt + 1
7.     else Sort(A, gt + 1, hi, budget);  hi = lt - 1
8. InsertionSort(A, lo, hi)                                     // from B

Algorithm FatPartition(A, lo, hi, v)
1. pa = pb = lo;  pc = pd = hi
2. loop
3.     while pb <= pc and A[pb] <= v do
4.         if A[pb] = v then swap A[pa], A[pb];  pa = pa + 1     // park equal key at the left end
5.         pb = pb + 1
6.     while pc >= pb and A[pc] >= v do
7.         if A[pc] = v then swap A[pc], A[pd];  pd = pd - 1     // park equal key at the right end
8.         pc = pc - 1
9.     if pb > pc then break
10.    swap A[pb], A[pc];  pb = pb + 1;  pc = pc - 1
11. swap the blocks A[lo..pa-1] and A[pa..pb-1] ends;  swap A[pc+1..pd] and A[pd+1..hi] ends
12. return (lo + (pb - pa), hi - (pd - pc))                     // bounds of the '= v' block
```

**Recurrences.** Balanced levels: T(n) = 2T(n/2) + Θ(n) ⇒ Θ(n log n). Without the guard, an adversary can force
T(n) = T(n − 2) + Θ(n) ⇒ Θ(n²). With the guard: at most 2⌊log₂ n⌋ partition levels of Θ(n) work each, plus heapsort
Θ(m log m) on the parts it receives ⇒ worst case O(n log n). All-equal input: one partition, 2n + 3 comparisons.

Design diagram: `../Implementation_Code/results/q7_design_diagram.png`.
