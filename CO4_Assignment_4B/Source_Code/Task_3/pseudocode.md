# Task 3 – Pseudocode: Huffman Coding of SOC Event Logs

Written before the implementation (`huffman_coding.py`).

## Greedy construction with a binary min-heap

```
Algorithm Huffman(F, m)                           // F = {symbol: frequency}, m symbols
1. if m = 0 or some frequency <= 0 then error
2. Q = empty min-heap ordered by (frequency, tie key)
3. for each symbol s do Insert(Q, leaf(s, F[s]))
4. while |Q| > 1 do                                           // m - 1 merges
5.     x = ExtractMin(Q);  y = ExtractMin(Q)                  // greedy choice: two least frequent trees
6.     z = new node(freq = x.freq + y.freq, left = x, right = y)
7.     Insert(Q, z)
8. return ExtractMin(Q)                                       // root; Theta(m log m)
// tie key: 'fifo' = creation order (older first, minimum variance); 'lifo' = newest first
```

## Codes, encoding and decoding

```
Algorithm MakeCodes(root)
1. if root is a leaf then return {root.symbol: "0"}           // one-symbol alphabet
2. walk the tree: append 0 for a left edge, 1 for a right edge; code(leaf) = path label

Algorithm Decode(bits, root)
1. node = root;  out = empty
2. for each bit b do
3.     if b not in {0, 1} then error
4.     node = (b = 0) ? node.left : node.right
5.     if node is a leaf then append node.symbol to out;  node = root
6. if node != root then error "truncated code word"
7. return out
```

## Alternative constructions compared in the experiments

```
Algorithm HuffmanNaive(F, m)                      // Theta(m^2): no priority queue
1. P = list of frequencies;  cost = 0
2. while |P| > 1 do
3.     remove the two smallest values a, b of P by two linear scans
4.     cost = cost + a + b;  append a + b to P
5. return cost

Algorithm HuffmanTwoQueues(F sorted increasing)   // Theta(m) after sorting
1. Q1 = sorted leaves;  Q2 = empty queue;  cost = 0
2. while |Q1| + |Q2| > 1 do
3.     a = smaller front of Q1, Q2 (dequeue);  b = smaller front of Q1, Q2 (dequeue)
4.     cost = cost + a + b;  enqueue a + b at the back of Q2    // merged sums arrive in sorted order
5. return cost
```
