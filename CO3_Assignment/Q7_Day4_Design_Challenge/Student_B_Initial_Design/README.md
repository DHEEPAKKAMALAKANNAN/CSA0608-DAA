# Q7 – Student B's independent initial design proposal

**Author:** Student B – [Student B Name] ([Reg. No.]) · **Status:** independent proposal, written before the joint
discussion (part C of Q7) · **Prototype:** `proposal_b_threeway_cutoff.py`

## 1. The limitation as I saw it (evidence from Q2)

The scheduler's real data is dominated by **equal deadlines** (orders are booked in 15-minute slots). In Q2, at
n = 8,000, the three Lomuto quick sorts needed 556,977–577,950 comparisons on the 64-slot list (5.4 n log₂ n,
growing ×3.65 per doubling of n) and exactly n(n − 1)/2 = 31,996,000 on an all-equal batch, whatever the pivot rule.
Each equal key is compared with the pivot again at every level, and Lomuto puts all of them on one side.
The many calls on tiny sub-arrays (Q2: up to 15,999 recursive calls for 8,000 orders) are a second, smaller cost.

## 2. Idea and the property it exploits

1. **Dijkstra's 3-way partition** (< v | = v | > v). Every key equal to the pivot is in its final place after one
   pass and is never compared again. With k distinct deadlines the recursion can have at most k pivot values on a
   path, so the work is about n log₂ k instead of n log₂ n (k = 64 slots → log₂ k = 6).
2. **Random pivot** (seeded generator), so that no fixed arrival order (sorted or reversed exports) is bad on average.
3. **Insertion sort for sub-arrays of ≤ 16 orders**: on tiny parts it is cheaper than further partitioning and
   removes most of the recursive calls.

## 3. Pseudocode

```
Algorithm QuickSortB(A, lo, hi)
1. if hi - lo + 1 <= 16 then InsertionSort(A, lo, hi);  return
2. v = A[random(lo..hi)];  lt = lo;  i = lo;  gt = hi
3. while i <= gt do
4.     if A[i] < v then swap A[lt], A[i];  lt = lt + 1;  i = i + 1
5.     else if A[i] > v then swap A[i], A[gt];  gt = gt - 1
6.     else i = i + 1                             // equal to the pivot: already in its final region
7. QuickSortB(A, lo, lt - 1);  QuickSortB(A, gt + 1, hi)
```

## 4. Prediction (made before testing)

About 1.4–1.6 n log₂ n comparisons on random, sorted and reversed lists (random-pivot quick sort ≈ 1.39 n log₂ n,
plus the second comparison of the 3-way test); exactly 2n comparisons on an all-equal list (one partition, two tests
per key); about n log₂ 64 = 6n on the 64-slot list; expected recursion depth about 2 log₂ n.

## 5. Prototype result (n = 2,000, `py proposal_b_threeway_cutoff.py`)

```
     input | comparisons / n lg n |   moves | depth | correct
    random |      37,625     1.72 |  37,562 |    17 | True
    sorted |      36,034     1.64 |  27,742 |    17 | True
   reverse |      36,805     1.68 |  27,952 |    17 | True
     slots |      20,333     0.93 |  21,838 |    14 | True
 all-equal |       4,000     0.18 |       0 |     1 | True
```

Screenshot: `../Output_Screenshots/q7_proposal_b_output.png`. The all-equal prediction was exact (4,000 = 2n, depth 1,
no moves). The 64-slot list took 20,333 comparisons, about 10n rather than 6n, because each key costs up to two
comparisons per level; still 2.5× fewer than the Q2 quick sorts at this size. Random/sorted/reversed were slightly
above the predicted range (1.64–1.72).

## 6. Result on the identical Q7 datasets (n = 8,000; `q7_experiments_output.txt`)

| Dataset | Comparisons | / n log₂ n | Moves | Depth |
|---|---|---|---|---|
| random | 186,917 | 1.80 | 178,970 | 22 |
| sorted | 183,340 | 1.77 | 142,126 | 21 |
| reverse | 179,391 | 1.73 | 143,026 | 23 |
| slots | 82,165 | 0.79 | 84,782 | 10 |
| all-equal | 16,000 | 0.15 | 0 | 1 |
| killer-B (adversarial, seed 42) | 32,004,690 | 308.55 | 31,992,698 | 3,993 |

**Strengths:** by far the best on the scheduler's duplicate-heavy data (all-equal 16,000 = 2n comparisons; slots
0.79 n log₂ n); no fixed input order is bad. **Weaknesses found in the comparison:** (i) on distinct keys it makes
the most comparisons (1.73–1.80 n log₂ n) and far more moves than proposal A (3.3× on random keys, 142,126 vs
1,084 on the sorted export), because Dijkstra's partition swaps every key larger than the pivot; (ii) the guarantee is only *expected* O(n log n): with the fixed seed that a
reproducible service uses, McIlroy's adversary built `killer-B`, which drove it to n²/2 comparisons and recursion
depth 3,993 (2.4 s). With a different (secret) seed the same input cost only 188,066 comparisons. Recursion is
not bounded because both sides are recursed.
