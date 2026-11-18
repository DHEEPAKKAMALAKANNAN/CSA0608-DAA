# Q7 – Student A's independent initial design proposal

**Author:** Student A – V. Vasudevan (192425324) · **Status:** independent proposal, written before the joint
discussion (part B of Q7) · **Prototype:** `proposal_a_median3_hoare.py`

## 1. The limitation as I saw it (evidence from Q2)

Q2's textbook quick sort (Lomuto partition, last-element pivot) at n = 8,000 orders
(`Q2_MergeSort_QuickSort/Implementation_Code/results/q2_results.csv`):

| Input | Comparisons | n(n − 1)/2 | Recursion depth |
|---|---|---|---|
| random | 123,356 | 31,996,000 | 30 |
| sorted export | 31,996,000 | 31,996,000 | 7,999 |
| reversed export | 29,767,464 | 31,996,000 | 7,449 |
| 64 slot values | 557,308 | 31,996,000 | 163 |
| all equal | 31,996,000 | 31,996,000 | 7,999 |

Two causes: (1) the pivot is taken from a **fixed position**, so an ordered export always yields the largest or
smallest key and a (n − 1) | 0 split; (2) Lomuto's test `A[j] ≤ pivot` sends **every key equal to the pivot to the
left side**, so equal deadlines again give (n − 1) | 0 splits — this is why even the random and median-of-three
pivots of Q2 stayed at n(n − 1)/2 on all-equal data.

## 2. Idea and the property it exploits

1. **Median-of-three pivot** (first, middle, last). On ordered data the middle element is the true median, so the
   split is perfectly balanced; on random data the median of three is closer to the median than one sample.
2. **Hoare partition with pointers that stop on equal keys.** Equal keys are swapped across and end up on **both**
   sides, so a run of equal deadlines is cut in half instead of being peeled off one key at a time.
3. **Recursion into the smaller part only, loop on the larger part.** Each recursive call gets at most half of
   its parent's orders, so the recursion depth (stack) is at most log₂ n on every input.

## 3. Pseudocode

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

## 4. Prediction (made before testing)

About 1.2 n log₂ n comparisons on random, sorted and reversed lists (the median-of-three constant 12/7·ln 2 ≈ 1.19),
about n log₂ n on all-equal lists (perfect halving), recursion depth ≤ log₂ n everywhere.

## 5. Prototype result (n = 2,000, `py proposal_a_median3_hoare.py`)

```
     input | comparisons / n lg n |   moves | depth | correct
    random |      33,803     1.54 |  11,436 |     8 | True
    sorted |      29,982     1.37 |      56 |    10 | True
   reverse |      29,983     1.37 |   2,060 |    10 | True
     slots |      34,069     1.55 |  15,316 |     8 | True
 all-equal |      31,723     1.45 |  21,728 |    10 | True
```

Screenshot: `../Output_Screenshots/q7_proposal_a_output.png`. The quadratic behaviour is gone on all five conditions
and the depth stays ≤ log₂ 2,000 ≈ 11. The constant is higher than predicted (1.37–1.55 instead of 1.2): Hoare's
pointers compare every key once **plus** the keys where they stop and cross, and the asymptotic constant 1.19 is
only reached for very large n.

## 6. Result on the identical Q7 datasets (n = 8,000; `q7_experiments_output.txt`)

| Dataset | Comparisons | / n log₂ n | Moves | Depth |
|---|---|---|---|---|
| random | 155,096 | 1.50 | 53,884 | 10 |
| sorted | 136,505 | 1.32 | 1,084 | 12 |
| reverse | 136,506 | 1.32 | 9,088 | 12 |
| slots | 148,989 | 1.44 | 76,286 | 10 |
| all-equal | 142,907 | 1.38 | 102,912 | 12 |
| killer-A (adversarial) | 16,047,992 | 154.71 | 15,994 | 2 |

**Strengths:** fixes every natural input condition; fewest moves on random and sorted data; stack depth ≤ log₂ n
even under attack. **Weaknesses found in the comparison:** (i) all-equal lists still cost n log₂ n comparisons and
102,912 moves — equal keys are swapped back and forth instead of being finished; (ii) the pivot rule is
deterministic, so an adversary (McIlroy's, `killer-A`) builds an input that makes it quadratic again
(n²/4 = 16,000,000 comparisons, 0.77 s). These two weaknesses fed the joint design.
