"""
Task 3 - Huffman coding of Security Operations Centre (SOC) event logs.

Every log record carries one event-type symbol (L = login OK, F = failed login, ...). Fixed-length codes
spend ceil(log2 m) bits per symbol; Huffman's greedy algorithm builds an optimal PREFIX code:
repeatedly merge the two least-frequent trees (greedy choice) until one tree remains.

Contents
  MinHeap            hand-written binary heap with a comparison counter (priority = (freq, tie key))
  build_huffman      heap version, Theta(m log m); prints/records the queue state before every merge;
                     tie policy 'fifo' (older node first = minimum-variance) or 'lifo' (newest first)
  huffman_naive      Theta(m^2) version: linear scan for the two minima (the un-optimised design)
  huffman_two_queue  Theta(m) after sorting (van Leeuwen's two-queue method) - the optimisation
  make_codes / encode / decode / entropy / average length helpers
Run:  py -3 huffman_coding.py     (given test case: queue states, merges, tree, codes, round trip, edge cases)
"""
import math
from collections import Counter, deque


class Node:
    """Huffman tree node. Leaves carry a symbol; internal nodes carry left (bit 0) and right (bit 1)."""
    __slots__ = ("freq", "symbol", "left", "right", "label")

    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq, self.symbol, self.left, self.right = freq, symbol, left, right
        self.label = symbol if symbol is not None else left.label + right.label

    def is_leaf(self):
        return self.symbol is not None


class MinHeap:
    """Binary min-heap of (key, item) pairs; every key comparison is counted in ops['heap_comparisons']."""

    def __init__(self, ops):
        self.a, self.ops = [], ops

    def __len__(self):
        return len(self.a)

    def _less(self, i, j):
        self.ops["heap_comparisons"] += 1
        return self.a[i][0] < self.a[j][0]

    def push(self, key, item):
        a = self.a
        a.append((key, item))
        i = len(a) - 1
        while i > 0 and self._less(i, (i - 1) // 2):
            p = (i - 1) // 2
            a[i], a[p] = a[p], a[i]
            i = p

    def pop(self):
        a = self.a
        top = a[0]
        last = a.pop()
        if a:
            a[0] = last
            i, n = 0, len(a)
            while True:
                small, l, r = i, 2 * i + 1, 2 * i + 2
                if l < n and self._less(l, small):
                    small = l
                if r < n and self._less(r, small):
                    small = r
                if small == i:
                    break
                a[i], a[small] = a[small], a[i]
                i = small
        return top

    def snapshot(self):
        """Queue contents in priority order (for printing only; not counted)."""
        return [item for _, item in sorted(self.a, key=lambda e: e[0])]


def validate_freqs(freqs):
    if not freqs:
        raise ValueError("empty alphabet: nothing to encode")
    for s, f in freqs.items():
        if f <= 0:
            raise ValueError(f"symbol {s!r} has non-positive frequency {f}")


def build_huffman(freqs, tie="fifo", ops=None, trace=None):
    """Greedy Huffman construction with a binary heap. freqs: {symbol: count}.
    tie='fifo': equal frequencies -> the node created EARLIER leaves the queue first (leaves before merged
    nodes; gives the minimum-variance code). tie='lifo': the most recently created node first.
    trace (list) receives (queue snapshot, x, y, merged) for every merge."""
    ops = Counter() if ops is None else ops
    validate_freqs(freqs)
    heap, seq = MinHeap(ops), 0

    def key(f):
        nonlocal seq
        seq += 1
        return (f, seq if tie == "fifo" else -seq)

    for s, f in freqs.items():                      # insertion order = order in the input table
        heap.push(key(f), Node(f, s))
    while len(heap) > 1:
        snap = heap.snapshot() if trace is not None else None
        _, x = heap.pop()                           # greedy choice: the two least frequent trees
        _, y = heap.pop()
        z = Node(x.freq + y.freq, left=x, right=y)
        ops["merges"] += 1
        heap.push(key(z.freq), z)
        if trace is not None:
            trace.append((snap, x, y, z))
    return heap.pop()[1]


def make_codes(root):
    """Code table {symbol: bitstring}. A one-symbol alphabet gets the 1-bit code '0'."""
    if root.is_leaf():
        return {root.symbol: "0"}
    codes, stack = {}, [(root, "")]
    while stack:
        node, path = stack.pop()
        if node.is_leaf():
            codes[node.symbol] = path
        else:
            stack.append((node.right, path + "1"))
            stack.append((node.left, path + "0"))
    return codes


def encode(symbols, codes):
    try:
        return "".join(codes[s] for s in symbols)
    except KeyError as e:
        raise ValueError(f"symbol {e.args[0]!r} is not in the code table") from None


def decode(bits, root):
    """Walk the tree bit by bit. Raises ValueError on an invalid bit or an incomplete final code word."""
    if root.is_leaf():                              # one-symbol alphabet: every '0' is that symbol
        if set(bits) - {"0"}:
            raise ValueError("invalid bit for a one-symbol code")
        return [root.symbol] * len(bits)
    out, node = [], root
    for i, b in enumerate(bits):
        if b not in "01":
            raise ValueError(f"invalid character {b!r} at bit {i}")
        node = node.left if b == "0" else node.right
        if node.is_leaf():
            out.append(node.symbol)
            node = root
    if node is not root:
        raise ValueError("bitstream ends in the middle of a code word (truncated or corrupted)")
    return out


def total_bits(freqs, codes):
    return sum(f * len(codes[s]) for s, f in freqs.items())


def average_length(freqs, codes):
    return total_bits(freqs, codes) / sum(freqs.values())


def fixed_length(m):
    return max(1, math.ceil(math.log2(m)))


def entropy(freqs):
    n = sum(freqs.values())
    return -sum(f / n * math.log2(f / n) for f in freqs.values())


def huffman_naive(freqs, ops=None):
    """Theta(m^2): keep an unsorted list; find the two smallest by linear scans. Returns total cost
    (sum of merged weights = total encoded bits)."""
    ops = Counter() if ops is None else ops
    validate_freqs(freqs)
    pool, cost = list(freqs.values()), 0
    if len(pool) == 1:
        return pool[0]
    while len(pool) > 1:
        picked = []
        for _ in range(2):
            m = 0
            for i in range(1, len(pool)):
                ops["scan_comparisons"] += 1
                if pool[i] < pool[m]:
                    m = i
            picked.append(pool[m])
            pool[m] = pool[-1]
            pool.pop()
        cost += picked[0] + picked[1]
        pool.append(picked[0] + picked[1])
    return cost


def huffman_two_queue(sorted_freqs, ops=None):
    """Theta(m) for frequencies ALREADY in non-decreasing order: leaves wait in queue 1, merged trees are
    created in non-decreasing order and wait in queue 2; the minimum is always at one of the two fronts."""
    ops = Counter() if ops is None else ops
    q1, q2, cost = deque(sorted_freqs), deque(), 0
    if len(q1) == 1:
        return q1[0]

    def take():
        if q1 and q2:
            ops["queue_comparisons"] += 1
            return q1.popleft() if q1[0] <= q2[0] else q2.popleft()
        return q1.popleft() if q1 else q2.popleft()
    while len(q1) + len(q2) > 1:
        a, b = take(), take()
        cost += a + b
        q2.append(a + b)
    return cost


def tree_lines(node, prefix="", bit="", out=None):
    """ASCII drawing of the tree, children indented under their parent with the edge bit."""
    out = [] if out is None else out
    name = f"{node.symbol}:{node.freq}" if node.is_leaf() else f"({node.label}:{node.freq})"
    out.append(f"{prefix}{'' if not bit else '+-' + bit + '- '}{name}")
    if not node.is_leaf():
        child_prefix = prefix + ("" if not bit else ("|     " if bit == "0" else "      "))
        tree_lines(node.left, child_prefix, "0", out)
        tree_lines(node.right, child_prefix, "1", out)
    return out


GIVEN_G1 = {"L": 45, "F": 13, "W": 12, "D": 16, "S": 9, "M": 5}
EVENT = {"L": "login success", "F": "failed login", "W": "firewall drop", "D": "DNS query",
         "S": "port scan", "M": "malware alert"}


def main():
    print("TASK 3 - HUFFMAN CODING OF SOC EVENT LOGS")
    print("=" * 100)
    print("Given test case G1: event frequencies (thousands of events per day)")
    print("  " + "  ".join(f"{s} {EVENT[s]} = {f}" for s, f in GIVEN_G1.items()))
    ops, trace = Counter(), []
    root = build_huffman(GIVEN_G1, "fifo", ops, trace)
    print("\nPriority-queue state before each merge (front = least frequent; ties: older node first)")
    for k, (snap, x, y, z) in enumerate(trace, 1):
        q = "  ".join(f"{n.label}:{n.freq}" for n in snap)
        print(f"  merge {k}: queue [{q}]")
        print(f"           pop {x.label}:{x.freq} (bit 0) + pop {y.label}:{y.freq} (bit 1) -> push {z.label}:{z.freq}")
    print(f"  {ops['merges']} merges, {ops['heap_comparisons']} heap comparisons")
    print("\nHuffman tree")
    for line in tree_lines(root):
        print("  " + line)
    codes = make_codes(root)
    print(f"\n  {'sym':<4}{'event':<15}{'freq':>5}  {'code':<6}{'bits':>4}{'freq x bits':>12}")
    for s in sorted(codes, key=lambda s: (len(codes[s]), codes[s])):
        print(f"  {s:<4}{EVENT[s]:<15}{GIVEN_G1[s]:>5}  {codes[s]:<6}{len(codes[s]):>4}"
              f"{GIVEN_G1[s] * len(codes[s]):>12}")
    tb, n = total_bits(GIVEN_G1, codes), sum(GIVEN_G1.values())
    print(f"  Total {tb} kbit; average {tb / n:.2f} bits/event vs fixed length {fixed_length(6)} bits "
          f"({100 * (1 - tb / (n * fixed_length(6))):.1f}% smaller); entropy {entropy(GIVEN_G1):.4f} bits")

    msg = list("LLFDLWLMSLDL")
    bits = encode(msg, codes)
    back = decode(bits, root)
    print(f"\nRound trip: {''.join(msg)} -> {bits} ({len(bits)} bits, fixed: {3 * len(msg)}) -> "
          f"{''.join(back)}  {'OK' if back == msg else 'MISMATCH'}")

    print("\nTie handling (G2: a=1, b=1, c=2, d=2) - different trees, same optimal cost")
    g2 = {"a": 1, "b": 1, "c": 2, "d": 2}
    for pol in ("fifo", "lifo"):
        c = make_codes(build_huffman(g2, pol))
        print(f"  {pol}: codes {dict(sorted(c.items()))}  cost {total_bits(g2, c)}  "
              f"max length {max(map(len, c.values()))}")

    print("\nBoundary and failure cases")
    one = build_huffman({"L": 7})
    print(f"  B1 single symbol L:7      -> codes {make_codes(one)}, decode('000') = {decode('000', one)}")
    two = {"L": 99, "M": 1}
    c2 = make_codes(build_huffman(two))
    print(f"  B2 two symbols L:99, M:1  -> codes {c2}: {average_length(two, c2):.2f} bit/event, entropy only "
          f"{entropy(two):.3f} (limit: >= 1 bit/symbol)")
    eq = {chr(65 + i): 10 for i in range(8)}
    ce = make_codes(build_huffman(eq))
    print(f"  B3 8 equal frequencies    -> all lengths {sorted(set(map(len, ce.values())))} = fixed length 3")
    fib = {chr(65 + i): f for i, f in enumerate([1, 1, 2, 3, 5, 8, 13, 21])}
    cf = make_codes(build_huffman(fib))
    print(f"  B4 Fibonacci 1..21        -> lengths {[len(cf[s]) for s in fib]} (degenerate tree, depth m-1)")
    for name, call in [("F1 empty alphabet", lambda: build_huffman({})),
                       ("F2 truncated stream 0110", lambda: decode(encode(["L", "M"], codes)[:-1], root)),
                       ("F3 unknown symbol X", lambda: encode(["L", "X"], codes))]:
        try:
            call()
            print(f"  {name:<25} -> accepted (UNEXPECTED)")
        except ValueError as e:
            print(f"  {name:<25} -> ValueError: {e}")


if __name__ == "__main__":
    main()
