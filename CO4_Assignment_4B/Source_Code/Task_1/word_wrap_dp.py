"""
Task 1 - Word Wrap as a document-layout engine (Dynamic Programming).

Problem: arrange the words w0 .. w(n-1) (in order) into lines of maximum width W characters. Words on a line
are separated by exactly one space. A NON-FINAL line containing s unused spaces costs s^2; the final line
costs 0. Find the arrangement with the minimum total penalty.

DP (suffix formulation), 0-based word indices:
    slack(i, j) = W - (len(w_i) + ... + len(w_(j-1)) + (j - i - 1))      words i..j-1 on one line
    best[n] = 0
    best[i] = min over j in (i, n] with slack(i, j) >= 0 of  linecost(i, j) + best[j]
              where linecost(i, j) = 0 if j == n (final line) else slack(i, j)^2
    next_break[i] = the j that achieved the minimum  ->  the optimal layout is rebuilt by following it from 0.
best[i] is the minimum penalty of laying out the SUFFIX of words starting at word i, so best[0] is the answer.
Work: Theta(n * L) candidate checks, where L = maximum number of words that fit on one line (<= n);
memory: two arrays of n + 1 entries.

The module contains only algorithm logic (no printing): validation, the DP with an optional state trace,
layout reconstruction, a greedy first-fit layout (for comparison) and an exhaustive reference that tries all
2^(n-1) break patterns (used by the tests to validate the DP).
"""
from collections import Counter, namedtuple

INF = float("inf")
Line = namedtuple("Line", "words first last unused penalty")          # first/last = word indices
Candidate = namedtuple("Candidate", "j unused line_cost suffix_cost total")
State = namedtuple("State", "i best next_break candidates")


class LayoutError(ValueError):
    """Raised when the text cannot be laid out at all (e.g. a word is longer than the line width)."""


def tokenize(text):
    """Split a text into words on any whitespace (the layout engine's input format)."""
    return text.split()


def validate(words, width):
    """Check the input; raise ValueError / LayoutError with a clear message instead of failing silently."""
    if isinstance(width, bool) or not isinstance(width, int) or width < 1:
        raise ValueError(f"line width must be a positive integer, got {width!r}")
    for k, w in enumerate(words):
        if not isinstance(w, str) or not w or any(ch.isspace() for ch in w):
            raise ValueError(f"word {k} must be a non-empty string without spaces, got {w!r}")
        if len(w) > width:
            raise LayoutError(f"word {k} {w!r} has {len(w)} characters > line width {width}: no valid layout")


def line_slack(lengths, i, j, width):
    """Unused spaces when words i..j-1 share one line (negative = does not fit)."""
    return width - (sum(lengths[i:j]) + (j - i - 1))


def word_wrap_dp(words, width, ops=None, record_states=False):
    """Minimum-penalty layout by DP.

    Returns (min_penalty, lines, states) where lines is a list of Line tuples and states (only when
    record_states=True) lists, for every i from n-1 down to 0, all feasible candidates j with their costs.
    ops counts 'candidates' (feasible (i, j) pairs examined) and 'states' (DP entries filled).
    """
    ops = Counter() if ops is None else ops
    validate(words, width)
    n = len(words)
    lengths = [len(w) for w in words]
    best = [INF] * (n + 1)
    next_break = [None] * (n + 1)
    best[n] = 0
    states = []
    for i in range(n - 1, -1, -1):                 # solve the shortest suffixes first
        ops["states"] += 1
        used = -1                                  # characters used by words i..j-1 incl. separating spaces
        candidates = []
        for j in range(i + 1, n + 1):
            used += lengths[j - 1] + 1
            unused = width - used
            if unused < 0:                         # word j-1 no longer fits: longer lines fit even less
                break
            ops["candidates"] += 1
            line_cost = 0 if j == n else unused * unused     # the final line carries no penalty
            total = line_cost + best[j]
            if record_states:
                candidates.append(Candidate(j, unused, line_cost, best[j], total))
            if total < best[i]:                    # strict "<": on ties keep the first (shortest) line found
                best[i], next_break[i] = total, j
        if record_states:
            states.append(State(i, best[i], next_break[i], candidates))
    return best[0], reconstruct(words, width, next_break), states


def reconstruct(words, width, next_break):
    """Follow next_break from word 0 and return the lines with their unused spaces and penalties."""
    lines, i, n = [], 0, len(words)
    lengths = [len(w) for w in words]
    while i < n:
        j = next_break[i]
        unused = line_slack(lengths, i, j, width)
        lines.append(Line(words[i:j], i, j - 1, unused, 0 if j == n else unused * unused))
        i = j
    return lines


def greedy_first_fit(words, width):
    """Put as many words as possible on each line (what a naive editor does). Returns (penalty, lines)."""
    validate(words, width)
    n, lengths, i, breaks = len(words), [len(w) for w in words], 0, [None] * (len(words) + 1)
    while i < n:
        j = i + 1
        while j < n and line_slack(lengths, i, j + 1, width) >= 0:
            j += 1
        breaks[i] = j
        i = j
    lines = reconstruct(words, width, breaks)
    return sum(line.penalty for line in lines), lines


def exhaustive_min_penalty(words, width):
    """Independent reference: try all 2^(n-1) break patterns (n <= 22). Returns the minimum penalty."""
    validate(words, width)
    n = len(words)
    if n == 0:
        return 0
    if n > 22:
        raise ValueError("exhaustive reference limited to n <= 22 words")
    lengths, best = [len(w) for w in words], INF
    for mask in range(1 << (n - 1)):               # bit k set = break after word k
        cost, start, ok = 0, 0, True
        for k in range(n):
            if k == n - 1 or mask >> k & 1:
                unused = line_slack(lengths, start, k + 1, width)
                if unused < 0:
                    ok = False
                    break
                cost += 0 if k == n - 1 else unused * unused
                start = k + 1
        if ok and cost < best:
            best = cost
    return best


def layout_signature(lines):
    """The break positions of a layout (index of the last word on every line) - used to compare layouts."""
    return tuple(line.last for line in lines)
