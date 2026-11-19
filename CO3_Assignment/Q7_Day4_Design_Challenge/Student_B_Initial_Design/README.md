# Q7 Stage 1 – Student B's independent design proposal

*Student B. Written before discussing the problem with Student A and kept unchanged as evidence. The paper states
that no marks are deducted because an initial design is incorrect.*

**Day-4 problem (chosen by the pair):** the most profitable contiguous run of delivery hours (Maximum Subarray Sum)
of hourly profit/loss data p[0..n−1].

| Element | Proposal B |
|---|---|
| Possible decomposition | left half / right half at the middle |
| Base case | one hour x → (x, max(x,0), max(x,0), max(x,0)), so an empty choice of value 0 is allowed |
| Required subproblem information | 4 sums per half: total, best prefix, best suffix, best run |
| Possible combine strategy | total = T<sub>L</sub> + T<sub>R</sub>; prefix = max(P<sub>L</sub>, T<sub>L</sub> + P<sub>R</sub>); suffix = max(S<sub>R</sub>, T<sub>R</sub> + S<sub>L</sub>); best = max(B<sub>L</sub>, B<sub>R</sub>, S<sub>L</sub> + P<sub>R</sub>) – O(1) |

```
Algorithm ProposalB(p, lo, hi)
1. if lo = hi then x = p[lo]; return (x, max(x,0), max(x,0), max(x,0))
2. mid = floor((lo + hi) / 2)
3. (TL, PL, SL, BL) = ProposalB(p, lo, mid);  (TR, PR, SR, BR) = ProposalB(p, mid + 1, hi)
4. return (TL + TR, max(PL, TL + PR), max(SR, TR + SL), max(BL, BR, SL + PR))
```

- Flowchart: `q7_flowchart_proposal_b.png`
- Program: `proposal_b_four_tuple.py`; output in `../Output_Screenshots/q7_proposal_b_output.png`

**What Stage 2 found.** The O(1) combine is correct and handles the crossing run. However:

- Empty runs are allowed, so an all-loss "storm day" [−40, −15, −90, −25] gives 0 instead of −15. This happens on
  100 % of all-loss inputs.
- The proposal reports no start or end hour.

Retained ideas: the 4-number summary and the O(1) combine formulas.
