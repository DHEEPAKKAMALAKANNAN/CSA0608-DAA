# Exercise 76 - Decode a Huffman Encoded String
import heapq


def build_huffman_tree(chars, freqs):
    """Greedy Huffman construction. Leaf = character, internal node = (left, right)."""
    heap = [(f, i, c) for i, (c, f) in enumerate(zip(chars, freqs))]
    heapq.heapify(heap)
    tie = len(heap)
    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, tie, (left, right)))
        tie += 1
    return heap[0][2]


def code_table(node, prefix="", table=None):
    table = {} if table is None else table
    if isinstance(node, str):
        table[node] = prefix or "0"
    else:
        code_table(node[0], prefix + "0", table)
        code_table(node[1], prefix + "1", table)
    return table


def decode(root, bits):
    """Walk from the root: '0' -> left, '1' -> right; a leaf emits its character
    and the walk restarts at the root.  Returns (text, unused trailing bits)."""
    text, node, pending = [], root, ""
    for b in bits:
        node = node[0] if b == "0" else node[1]
        pending += b
        if isinstance(node, str):
            text.append(node)
            node, pending = root, ""
    return "".join(text), pending


if __name__ == "__main__":
    tests = [
        (['a', 'b', 'c', 'd'], [5, 9, 12, 13], '1101100111110', "abacd"),
        (['f', 'e', 'd', 'c', 'b', 'a'], [5, 9, 12, 13, 16, 45],
         '110011011100101111001011', "fcbade"),
    ]
    for no, (chars, freqs, bits, doc) in enumerate(tests, 1):
        tree = build_huffman_tree(chars, freqs)
        codes = code_table(tree)
        text, rest = decode(tree, bits)
        print(f"Test Case {no}")
        print(f"Input   : n = {len(chars)}, characters = {chars}, frequencies = {freqs}")
        print(f"          encoded_string = '{bits}'")
        print(f"Codes   : {dict(sorted(codes.items()))}")
        print(f"Output  : \"{text}\"" + (f"  (trailing bits '{rest}' are not a complete code)"
                                        if rest else ""))
        right = "".join(codes[c] for c in doc)       # correct encoding of the document's answer
        back, _ = decode(tree, right)
        print(f"Check   : encode(\"{doc}\") = '{right}' -> decode gives \"{back}\"")
        if (text, rest) == (doc, ""):
            print(f"Expected: \"{doc}\"")
        else:
            print(f"Note    : document lists \"{doc}\"; given string is not an encoding of it "
                  f"(correct: '{right}')")
        print()
    print("Time complexity : O(n log n) to build the tree, O(L) to decode L bits")
