# Q7 Stage 1 – Student A's independent design proposal

*Student A (V. Vasudevan). Written before discussing the problem with Student B and kept unchanged as evidence.
The paper states that no marks are deducted because an initial design is incorrect.*

**Day-4 problem (chosen by the pair, because the paper leaves the problem to Day 4):** the most profitable
contiguous run of delivery hours. Given the hourly net profit/loss p[0..n−1] of a delivery hub, find i ≤ j that
maximises p[i] + … + p[j] (Maximum Subarray Sum).

| Element | Proposal A |
|---|---|
| Possible decomposition | split the hours at the middle, mid = ⌊(lo + hi)/2⌋ |
| Base case | one hour → (p[lo], lo, lo) |
| Required subproblem information | the best run of each half: (sum, start hour, end hour) |
| Possible combine strategy | return the better of the two halves' best runs |

```
Algorithm ProposalA(p, lo, hi)
1. if lo = hi then return (p[lo], lo, lo)
2. mid = floor((lo + hi) / 2)
3. L = ProposalA(p, lo, mid);  R = ProposalA(p, mid + 1, hi)
4. if L.sum >= R.sum then return L else return R
```

- Flowchart: `q7_flowchart_proposal_a.png`
- Program: `proposal_a_midpoint_split.py` (`py -3 proposal_a_midpoint_split.py`); output in
  `../Output_Screenshots/q7_proposal_a_output.png`

**What Stage 2 found.** The proposal never considers a run that crosses the split. On the demo hours
[−120, 340, −60, 410, −380, 150, 220, −90] it returns 410 instead of 690. On random data it is wrong in 78.6 % of
8-hour instances and in 100 % at n = 64. Retained ideas: the midpoint split, the one-hour base case and returning
the hours (start, end).
