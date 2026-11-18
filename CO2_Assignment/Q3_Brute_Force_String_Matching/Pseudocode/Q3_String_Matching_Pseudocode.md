# Q3 – Brute-Force String Matching for Cybersecurity Log Screening: Pseudocode and Pre-Implementation Notes

*Written before implementation. The three test conditions and their predictions are fixed here; the program prints
each prediction **before** it executes the corresponding test.*

## 1. Problem model

* Text `T[0..n−1]` = a block of system-log characters; pattern `P[0..m−1]` = a known event signature.
* A log screener needs **every** occurrence (each hit is an alert), so the algorithm tries **all** n−m+1
  alignments (shifts) and reports every shift where the whole pattern matches.
* **Basic operation counted:** one character comparison `T[s+j] = P[j]` (successful or not).

## 2. Pseudocode

```
BRUTE-FORCE-MATCH-ALL(T[0..n−1], P[0..m−1])
    comparisons ← 0 ; matches ← empty list
    for s ← 0 to n−m do                        // every possible alignment of P under T
        j ← 0
        while j < m do
            comparisons ← comparisons + 1
            if T[s+j] ≠ P[j] then break       // first mismatch ends this alignment
            j ← j + 1
        if j = m then append s to matches     // all m characters matched
    return matches, comparisons
```

Work at shift s = (length of the matched prefix at s) + 1, or m if the pattern matches completely, so

  **C = Σ<sub>s=0</sub><sup>n−m</sup> min(m, ℓ<sub>s</sub> + 1)**, where ℓ<sub>s</sub> = number of leading characters of P that match at shift s.

Bounds: n−m+1 ≤ C ≤ m(n−m+1).

## 3. Designed test conditions and predictions (n = 100 000 characters, m = 38 for all three)

The same n and m are used on purpose: any difference in work is caused by *content*, not by input size.

| Condition | Text | Pattern | Predicted comparisons | Algorithmic reason |
|---|---|---|---|---|
| C1 – little work | realistic SSH/auth log | `#IOC:RANSOMWARE-SHADOWCOPY-DELETE-0x7F` | exactly n−m+1 = **99 963** | `#` never occurs in the log, so every alignment fails on its **first** comparison (ℓ<sub>s</sub> = 0) |
| C2 – engineered heavy work | `AAAA…A` (a run of identical bytes, like a base64 / NOP-sled payload) | `AAA…AB` (37 × A then B) | exactly m(n−m+1) = **3 798 594** | every alignment matches 37 characters and fails only on the last one (ℓ<sub>s</sub> = m−1) |
| C3 – own choice: realistic log, signature that shares a long prefix with benign lines | realistic SSH/auth log | `Failed password for invalid user admin` | independence model ≈ 1.01 (n−m+1); my expectation: **1.0–1.3 × (n−m+1)** | first character `F` is rare, so most alignments stop at once, but every benign `Failed password for …` line matches a 20–33 character prefix before failing |

Independence model used for the C3 point prediction (character frequencies f(c) measured on the text):
E[comparisons per shift] = Σ<sub>k=0</sub><sup>m−1</sup> Π<sub>i<k</sub> f(P[i]). It assumes characters are independent; real
log lines are highly structured, so I expect the observed value to be *higher* than this model.

## 4. Extra experiments

* **Size sweep:** n = 1 000, 10 000, 100 000, 1 000 000 for C1–C3 (m = 38). Prediction: all three grow linearly
  in n, but C2's slope is m = 38 times C1's slope.
* **Pattern-length sweep:** n = 100 000, m = 2, 4, 8, …, 128 for C1 and C2. Prediction: C1 stays ≈ n while
  C2 grows ≈ m·n, i.e. the "same input size" can mean 1× or 128× the work.

## 5. Complexity

Best case (each shift fails at once) Θ(n); worst case Θ(m·n) (precisely m(n−m+1)); for natural-language-like
or log text the average is close to the best case because the first character usually mismatches.
