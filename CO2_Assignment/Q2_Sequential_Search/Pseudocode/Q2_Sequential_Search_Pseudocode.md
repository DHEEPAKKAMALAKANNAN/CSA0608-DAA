# Q2 – Sequential Search for Aircraft Maintenance Tool Tracking: Pseudocode and Pre-Implementation Notes

*Written before implementation. Predictions are compared with measured counts in the report.*

## 1. Problem model

* Active-issue list `L[0..n−1]`, each record `(tool_id, technician_id, issue_time, work_bay)`, e.g.
  `("T-184", "TECH-042", "07:42", "BAY-03")`. Records are appended when a tool is issued and removed when it is
  returned, so the list is in **issue order**, not sorted by tool ID.
* Query: *"Who currently has Tool T-184?"* → return the record (technician, bay, time) or *not issued*.
* **Basic operation counted:** one key comparison `L[i].tool_id = target`.

## 2. Pseudocode

```
SEQUENTIAL-SEARCH(L[0..n−1], target)
    comparisons ← 0
    for i ← 0 to n−1 do
        comparisons ← comparisons + 1
        if L[i].tool_id = target then
            return (i, comparisons)            // successful: stops at the first match
    return (NOT-FOUND, comparisons)             // unsuccessful: every record examined
```

```
ISSUE(L, record)       append record to the end of L                         // O(1)
RETURN(L, tool_id)     (i, c) ← SEQUENTIAL-SEARCH(L, tool_id)                 // O(n) search …
                       L[i] ← L[n−1] ; delete L[n−1]                          // … then O(1) swap-remove
```

## 3. Predictions (before running)

| Situation | Predicted comparisons | Reason |
|---|---|---|
| target at position p (1-based) | exactly **p** | the loop stops at the first match |
| first / middle / last record | 1 / ⌈n/2⌉ / n | special cases of p |
| unsuccessful search | exactly **n** | absence can only be proved by examining every record |
| average successful search (target equally likely anywhere) | **(n+1)/2** | Σ<sub>p=1</sub><sup>n</sup> p / n = (n+1)/2 |
| average with success probability q | q(n+1)/2 + (1−q)n | weighted mix of the two cases |

Growth: all cases except "first" grow **linearly** with n, so 10× more records → 10× more comparisons per query.
Total work per second = (requests per second) × (comparisons per request) ⇒ grows with the **product** λ·n.

## 4. Experiment design

1. **Position experiment** – sizes n = 50, 500, 5 000, 50 000, 500 000, 1 000 000; targets at the first record,
   25 %, 50 %, 75 %, last record, plus an absent tool ID.
2. **Average-case experiment** – for each size, many random successful targets (uniform positions); compare the
   sample mean with (n+1)/2.
3. **Timing** – time unsuccessful scans at n = 1 000 000 to obtain the cost of one comparison *t<sub>c</sub>*
   (secondary evidence, used only to convert counts into seconds).
4. **Operating boundary** – Sequential Search is acceptable while BOTH hold:
   * latency: worst-case lookup n·t<sub>c</sub> ≤ 50 ms (half of a 100 ms "instant response" budget);
   * load: λ · n · t<sub>c</sub> ≤ 0.05 (lookups use at most 5 % of one CPU core).
   ⇒ n<sub>max</sub>(λ) = min(0.05 s / t<sub>c</sub>, 0.05 / (λ · t<sub>c</sub>)).
5. **Changed condition (20 facilities)** – simulate a peak hour of issues, returns and lookups for one hangar and
   for 20 facilities, counting comparisons for (a) the list + Sequential Search and (b) a hash index keyed by
   Tool ID that is updated on every issue/return:

```
INDEXED-STORE:   index ← empty hash map  tool_id → record
ISSUE(rec)       index[rec.tool_id] ← rec                     // O(1) expected
RETURN(id)       delete index[id]                              // O(1) expected
LOOKUP(id)       return index.get(id)                          // O(1) expected, 1 key probe
```

**Prediction for the changed condition:** n grows ≈ 20× and λ grows ≈ 20×, so total comparisons per hour for
Sequential Search grow ≈ 400×, while the hash index grows only ≈ 20× (linear in the number of requests).
