# Q7 Stages 2–3 – design-comparison record and joint final design

## Stage 2 – comparison record (how the two proposals influenced the final solution)

| Point | Student A | Student B | Joint decision |
|---|---|---|---|
| Agree | midpoint split, one-hour base case, two half-size calls | same | kept |
| Differ | returns the best run (sum, start, end); combine = better half | returns 4 sums; combine includes the crossing run S<sub>L</sub> + P<sub>R</sub> | B's summary adopted |
| Strength | reports *which hours* | O(1), complete case analysis | both kept |
| Weakness | misses crossing runs (410 instead of 690; 100 % wrong at n = 64) | empty runs (0 instead of −15 on an all-loss day); no indices | non-empty prefix/suffix/best; indices added |
| Missing | crossing case, prefix/suffix information | indices, empty input, all-loss input | indices pre_end, suf_start, (bi, bj); error for n = 0 |

We also examined a repaired proposal A, which computes the crossing run with a Θ(n) scan from the middle (textbook
version). It is correct but Θ(n log n), and it is kept as the comparison variant `dc_crossing`.

## Stage 3 – joint final design (implemented as `dc_joint` in `../Implementation_Code/q7_max_subarray.py`)

| Element | Design |
|---|---|
| Decomposition | mid = ⌊(lo + hi)/2⌋; halves of ⌈n/2⌉ and ⌊n/2⌋ hours |
| Subproblems | the same problem on each half (independent, non-overlapping) |
| Base case | one hour: total = prefix = suffix = best = p[lo] |
| Information returned | Summary(total; prefix, pre_end; suffix, suf_start; best, bi, bj) – all runs non-empty |
| Combine | total = T<sub>L</sub> + T<sub>R</sub>; prefix = max(P<sub>L</sub>, T<sub>L</sub> + P<sub>R</sub>); suffix = max(S<sub>R</sub>, T<sub>R</sub> + S<sub>L</sub>); cross = S<sub>L</sub> + P<sub>R</sub>; best = max(B<sub>L</sub>, B<sub>R</sub>, cross) – 4 additions + 4 comparisons |
| Recurrence | T(n) = 2T(n/2) + Θ(1) → Θ(n) (Master case 1); exactly 4(n − 1) additions and 4(n − 1) comparisons |

Full pseudocode: `../Pseudocode/Q7_Max_Subarray_Pseudocode.md`. Flowchart:
`../Pseudocode/q7_flowchart_joint_dc.png`. Recursion tree: `../Implementation_Code/results/q7_recursion_tree.png`.
