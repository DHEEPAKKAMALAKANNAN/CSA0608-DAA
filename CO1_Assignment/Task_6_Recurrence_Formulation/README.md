# Task 6 – Formulate the Recurrence Relation [3 Marks]

> Part of **CSA06 Assignment 1 (CO1)** – V. Vasudevan (192425324). Full report: [`Report/Documentation/CO1_Assignment_Report.md`](../Report/Documentation/CO1_Assignment_Report.md) · [project README](../README.md)

> For the recursive approach, formulate a recurrence relation directly from the behaviour of the algorithm. Clearly identify:
> - the input size of the original problem;
> - the size of the recursive subproblem;
> - the number of recursive calls;
> - the work performed outside the recursive call;
> - the base case;
> - how these components lead to the recurrence relation.
> The recurrence must be derived from your algorithm, rather than simply writing a known recurrence formula.

**Ans:**

## 1. The algorithm the recurrence is derived from

The recursive approach is `binary_search_recursive(sorted_records, key, low, high, counter)` in `search_algorithms.py` (pseudocode `BinSearch`, Task 1). One activation does the following:

```
1. counter.calls += 1
2. if low > high: return None                          # base case: empty range
3. mid = (low + high) // 2
4. mid_key = sorted_records[mid].reg_no
5. counter.comparisons += 1                            # ONE three-way comparison key : A[mid]
6. if key == mid_key: return sorted_records[mid]       # found: no further call
7. if key < mid_key: return binary_search_recursive(..., low, mid - 1, ...)
8. return binary_search_recursive(..., mid + 1, high, ...)
```

## 2. The components, read from the code

**Input size of the original problem.** The problem is described by the range A[low..high]; its size is **n = high − low + 1**. The first call has low = 0, high = n − 1, i.e. the whole database.

**Size of the recursive subproblem.** With mid = ⌊(low + high)/2⌋:

- left half A[low..mid − 1] has size mid − low = ⌊(low + high)/2⌋ − low = ⌊(high − low)/2⌋ = **⌊(n − 1)/2⌋**;
- right half A[mid + 1..high] has size high − mid = (n − 1) − ⌊(n − 1)/2⌋ = ⌈(n − 1)/2⌉ = **⌊n/2⌋**.

The larger subproblem therefore has size ⌊n/2⌋ (for n = 1,000,000 the halves are 499,999 and 500,000).

**Number of recursive calls.** Lines 7 and 8 are alternatives (`if … return`), so an activation makes **at most one** recursive call, and none when the key is found on line 6. This is the decisive difference from merge sort, which makes two calls.

**Work outside the recursive call.** Lines 1–6: computing mid, reading A[mid] and **one** three-way comparison, i.e. f(n) = 1 basic operation (Θ(1) time), independent of n.

**Base case.** n = 0 (low > high): the function returns NOT FOUND after **0** comparisons, so C(0) = 0. (A size-1 range is not a base case in my code: it makes one comparison and, if unsuccessful, one call on an empty range; this gives C(1) = C(0) + 1 = 1.)

## 3. The recurrences

Combining "comparisons of this activation (1)" + "comparisons of the one recursive call on the larger half (worst case)":

**C<sub>worst</sub>(n) = C<sub>worst</sub>(⌊n/2⌋) + 1 for n ≥ 1,  C<sub>worst</sub>(0) = 0**

Table 9: Components of the recurrence, taken from the code

| Component | Value in `binary_search_recursive` | Contribution to the recurrence |
|---|---|---|
| Input size | n = high − low + 1 | C(n) |
| Subproblem size | ⌊(n − 1)/2⌋ (left) or ⌊n/2⌋ (right) | worst case uses ⌊n/2⌋ |
| Number of recursive calls | at most 1 (left **or** right) | coefficient a = 1 |
| Work outside the call | one three-way comparison + Θ(1) arithmetic | + 1 |
| Base case | n = 0 (low > high): 0 comparisons | C(0) = 0 |

Related recurrences from the same reasoning:

- **Best case:** the key is A[mid] in the first activation: C<sub>best</sub>(n) = 1 for n ≥ 1 (no recursive call).
- **Running time:** T(n) = T(⌊n/2⌋) + c for n ≥ 1, T(0) = d, where c is the constant cost of lines 1–6.
- **Recursion depth / stack space:** D(n) = D(⌊n/2⌋) + 1, D(0) = 1 frame — the same form as C(n).
- **Total over all n successful searches** (used for the exact average in Task 3): every search makes the root comparison, then ⌊(n − 1)/2⌋ of them continue left and ⌈(n − 1)/2⌉ continue right, so S(n) = n + S(⌊(n − 1)/2⌋) + S(⌈(n − 1)/2⌉), S(0) = 0.

## 4. Recurrence of the recursive preprocessing (merge sort)

`_merge_sort(a, aux, low, high)` sorts A[low..mid] (size ⌈n/2⌉) and A[mid + 1..high] (size ⌊n/2⌋) with **two** recursive calls and then merges them with at most n − 1 comparisons; a range of 0 or 1 record is the base case with 0 comparisons:

**C<sub>sort</sub>(n) = C<sub>sort</sub>(⌈n/2⌉) + C<sub>sort</sub>(⌊n/2⌋) + (n − 1) for n ≥ 2,  C<sub>sort</sub>(1) = 0,** which for n = 2ᵏ is C<sub>sort</sub>(n) = 2C<sub>sort</sub>(n/2) + n − 1.
