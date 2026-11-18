# Exercise 75 - Huffman Tree and Huffman Codes
import heapq


def build_huffman_tree(chars, freqs):
    """Repeatedly merge the two least frequent nodes (greedy).
    A leaf is a character (str); an internal node is a (left, right) tuple."""
    heap = [(f, i, c) for i, (c, f) in enumerate(zip(chars, freqs))]
    heapq.heapify(heap)                    # (frequency, tie-breaker, node)
    tie = len(heap)
    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, tie, (left, right)))
        tie += 1
    return heap[0][2]


def huffman_codes(node, prefix="", codes=None):
    """Walk the tree: left edge = '0', right edge = '1'."""
    codes = {} if codes is None else codes
    if isinstance(node, str):
        codes[node] = prefix or "0"        # a lone character still needs one bit
    else:
        huffman_codes(node[0], prefix + "0", codes)
        huffman_codes(node[1], prefix + "1", codes)
    return codes


def encoded_length(codes, chars, freqs):
    return sum(f * len(codes[c]) for c, f in zip(chars, freqs))


if __name__ == "__main__":
    tests = [
        (['a', 'b', 'c', 'd'], [5, 9, 12, 13],
         [('a', '110'), ('b', '10'), ('c', '0'), ('d', '111')]),
        (['f', 'e', 'd', 'c', 'b', 'a'], [5, 9, 12, 13, 16, 45],
         [('a', '0'), ('b', '101'), ('c', '100'), ('d', '111'), ('e', '1101'), ('f', '1100')]),
    ]
    for no, (chars, freqs, doc) in enumerate(tests, 1):
        codes = huffman_codes(build_huffman_tree(chars, freqs))
        result = sorted(codes.items())
        cost = encoded_length(codes, chars, freqs)
        doc_cost = encoded_length(dict(doc), chars, freqs)
        print(f"Test Case {no}")
        print(f"Input   : n = {len(chars)}, characters = {chars}, frequencies = {freqs}")
        print(f"Output  : {result}")
        print(f"Cost    : sum(freq x code length) = {cost} bits")
        if result == doc:
            print(f"Expected: {doc}")
        else:
            print(f"Document: {doc}")
            if doc_cost == cost:
                print(f"Note    : document's codes differ in bits only (same lengths, cost {cost}); "
                      "Huffman codes are not unique")
            else:
                print(f"Note    : document lists non-optimal codes (cost {doc_cost} bits); "
                      f"correct Huffman cost is {cost} bits")
        print()
    print("Time complexity : O(n log n) using a min-heap; Space: O(n)")
