# Task 4: Pseudocode Forensics – Find, Explain and Repair an Algorithmic Defect

## 1. Problem Overview
- **Scenario:** Text segmentation (the classic *Word Break* problem). Determine whether a string $Text$ of length $n$ can be partitioned into a sequence of one or more valid words belonging to a specified $Dictionary$.
- **Problem Classification:** String dynamic programming.
- **Flawed Code Provided:** A junior engineer submitted pseudocode containing a critical logical defect that leads to silent semantic failure and false positives.

---

## 2. Task 4.1: Defect Location & Algorithmic Diagnosis

### The Flawed Pseudocode Snippet:
```text
ALGORITHM WordBreak(Text, Dictionary)
BEGIN
    DP[0] ← TRUE
    FOR i ← 1 TO n DO
        DP[i] ← FALSE
        FOR j ← 0 TO i - 1 DO
            IF substring(Text, j, i) is in Dictionary THEN    ◄ DEFECTIVE LINE
                DP[i] ← TRUE
                BREAK
            END IF
        END FOR
    END FOR
    RETURN DP[n]
END
```

### Exact Location of the Defect:
The incomplete decision resides exclusively in line 7:
$$\text{IF } substring(Text, j, i) \text{ is in Dictionary THEN}$$

### Theoretical & Algorithmic Explanation:
- **Missing Reachability Precondition:** For a prefix of length $i$ ($Text[1..i]$) to be segmentable when split at position $j$, **two independent conditions must simultaneously hold**:
  1. The suffix substring $Text[j+1..i]$ must be a valid dictionary entry.
  2. **The preceding prefix $Text[1..j]$ must itself be completely segmentable**, which is represented by the invariant $\text{DP}[j] = \text{TRUE}$.
- **Flawed Semantics:** The proposed code never reads previously calculated $\text{DP}[j]$ states! As a result, $\text{DP}[i]$ does not mean *"prefix $1..i$ is validly segmented"*; it merely records whether *"some dictionary word ends at index $i$"*.
- If the entire text ends with a dictionary word, the faulty algorithm returns $\text{TRUE}$ regardless of whether the preceding characters can be validly segmented.

---

## 3. Task 4.2: Student-Designed Failing Counter-Example

### Failing Test Case Design:
- **Target Text:** `catsdog` ($n = 7$)
- **Dictionary:** `{ "cat", "dog" }`
- **Ground Truth:** **FALSE**. (Partitioning options: `cat` leaves `sdog`, which is invalid; no dictionary word covers `s`).
- **Faulty Algorithm Output:** **TRUE** (False Positive).

### State-by-State Comparative Trace:
| $i$ | Prefix Examined | Faulty $\text{DP}[i]$ (Reason) | Corrected $\text{DP}[i]$ (Reason) | Anomaly / Diagnosis |
|:---:|:---:|:---:|:---:|:---:|
| **0** | $\epsilon$ (empty) | $\text{TRUE}$ (base) | $\text{TRUE}$ (base) | Concordant |
| **1** | `c` | $\text{FALSE}$ (no word) | $\text{FALSE}$ | Concordant |
| **2** | `ca` | $\text{FALSE}$ (no word) | $\text{FALSE}$ | Concordant |
| **3** | `cat` | $\text{TRUE}$ (`cat` at $j=0$) | $\text{TRUE}$ ($\text{DP}[0]=\text{T} \land \text{cat}$) | Concordant |
| **4** | `cats` | $\text{FALSE}$ (no suffix word) | $\text{FALSE}$ | Concordant |
| **5** | `catsd` | $\text{FALSE}$ (no suffix word) | $\text{FALSE}$ | Concordant |
| **6** | `catsdo` | $\text{FALSE}$ (no suffix word) | $\text{FALSE}$ | Concordant |
| **7** | `catsdog` | **TRUE** (`dog` at $j=4$) | **FALSE** ($\text{DP}[4]=\text{F}$, so `dog` cannot attach) | **FIRST INCORRECT STATE** |

**Forensic Finding:** The first faulty state appears at index $i = 7$. Because $j=4$ produces the substring `dog` (which is in the dictionary), the faulty algorithm blindly sets $\text{DP}[7] = \text{TRUE}$ while ignoring that prefix `cats` ($\text{DP}[4]$) is completely unsegmentable.

---

## 4. Task 4.3: Repaired Minimal Pseudocode

```text
ALGORITHM WordBreak(Text, Dictionary)
INPUT:
    Text       – string of length n
    Dictionary – collection of valid vocabulary words
OUTPUT:
    TRUE if Text can be completely segmented into dictionary words;
    FALSE otherwise
BEGIN
    DP[0] ← TRUE
    FOR i ← 1 TO n DO
        DP[i] ← FALSE
        FOR j ← 0 TO i - 1 DO
            IF DP[j] = TRUE AND substring(Text, j, i) is in Dictionary THEN    ◄ REPAIRED
                DP[i] ← TRUE
                BREAK
            END IF
        END FOR
    END FOR
    RETURN DP[n]
END
```

### Proof of Correctness & Invariant Preservation:
- **Inductive Invariant:** $\text{DP}[i] = \text{TRUE} \iff$ there exists a valid segmentation for the prefix $Text[1..i]$.
- **Base Case:** $\text{DP}[0] = \text{TRUE}$ trivially models the empty string.
- **Inductive Step:** By checking $\text{DP}[j] = \text{TRUE}$, we ensure that any valid suffix word $Text[j+1..i]$ is anchored to a rigorously validated preceding segment.
- **Early Exit (`BREAK`):** A single valid split point $j$ is sufficient to prove segmentability for prefix $i$; therefore, `BREAK` remains optimal.
- **Performance Optimization:** Placing $\text{DP}[j] = \text{TRUE}$ first in the logical conjunction leverages boolean short-circuit evaluation, avoiding expensive substring extraction and hashing lookups whenever $\text{DP}[j]$ is false.

---

## 5. Task 4.4: Regression Testing

### Regression Case 1 (Valid Positive Case):
- **Input:** $Text = \text{"catdog"}$, $Dictionary = \{\text{"cat"}, \text{"dog"}\}$.
- **Ground Truth:** $\text{TRUE}$ (`cat` + `dog`).

| $i$ | Prefix | Original $\text{DP}[i]$ | Repaired $\text{DP}[i]$ (Witness $j$) | Concordance |
|:---:|:---:|:---:|:---:|:---:|
| **3** | `cat` | $\text{TRUE}$ | $\text{TRUE}$ ($j=0, \text{DP}[0]=\text{T}$) | Preserved |
| **6** | `catdog` | $\text{TRUE}$ | $\text{TRUE}$ ($j=3, \text{DP}[3]=\text{T}$) | Preserved |

*Both algorithms yield $\text{TRUE}$. Genuine segmentations are fully preserved.*

### Regression Case 2 (Valid Negative Case):
- **Input:** $Text = \text{"dogcatx"}$, $Dictionary = \{\text{"cat"}, \text{"dog"}\}$.
- **Ground Truth:** $\text{FALSE}$.
- *Result:* Both algorithms return $\text{FALSE}$. No false positives or false negatives are introduced.

---

## 6. Implementation & Verification Details

### File Manifest:
- `word_break.py`: Python implementation containing both faulty and corrected versions, generating visual state arrays and diagnostic comparison.
- `word_break_cases.csv`: Input test dataset.
- `test_word_break.py`: Verification suite benchmarking the corrected algorithm against an independent memoized recursive segmenter across 2,000 random strings.

### How to Run:
```bash
python word_break.py
python test_word_break.py
```

### Verification Result:
```text
=== TASK 4: TEST SUITE ===
PASS test_failing_case_catsdog: corrected returns FALSE, faulty returns TRUE
PASS test_regression_case_catdog: both return TRUE
PASS test_regression_negative_dogcatx: both return FALSE
PASS test_empty_string: returns TRUE
PASS test_single_character_match
PASS test_repeated_words
PASS test_prefix_valid_suffix_invalid
PASS test_memoized_recursive_reference (2000 randomized texts; 480 flaws caught)
PASS test_short_circuit_behavior
PASS test_deterministic_output
RESULT: 10/10 tests passed
```
