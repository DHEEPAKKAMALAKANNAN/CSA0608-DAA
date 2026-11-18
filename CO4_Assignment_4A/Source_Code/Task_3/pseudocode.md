# Task 3 – Pseudocode: Warshall's Algorithm (transitive closure / network reachability)

Written before the implementation (`warshall_closure.py`). A[1..n, 1..n] = adjacency matrix of the one-way links.

## DP formulation
- **State:** R(k)[i][j] = 1 iff there is a directed path from i to j (length ≥ 1) whose *intermediate* vertices
  are all numbered ≤ k.
- **Recurrence:** R(k)[i][j] = R(k−1)[i][j] **or** (R(k−1)[i][k] **and** R(k−1)[k][j]) — either vertex k is not
  needed, or the path goes i → … → k → … → j using only vertices ≤ k − 1 on both halves.
- **Base case:** R(0) = A (paths with no intermediate vertex = direct links).
- **Order of computation:** k = 1 … n (outer); inside, any order of (i, j). Row k and column k do not change during
  iteration k (R[k][k] = 1 would only re-add what is there), so one matrix can be updated in place.
- **Answer:** R(n) = transitive closure.

## 1. Warshall (Levitin)
```
Algorithm Warshall(A[1..n, 1..n])
// Input: adjacency matrix A of a digraph      Output: transitive closure R
1. R = A                                                   // R(0)
2. for k = 1 to n do
3.     for i = 1 to n do
4.         for j = 1 to n do                               // inner step (count): n^3 in total
5.             R[i][j] = R[i][j] or (R[i][k] and R[k][j])
6. return R                                                // R(n)
```

## 2. Row-skip improvement
```
Algorithm WarshallRowSkip(A)
1. R = A
2. for k = 1 to n do
3.     for i = 1 to n do
4.         if R[i][k] = 1 then                             // otherwise row i cannot change in this iteration
5.             for j = 1 to n do R[i][j] = R[i][j] or R[k][j]
6. return R
```

## 3. Bitset rows (word-parallel)
```
Algorithm WarshallBitset(A)
1. for i = 1 to n do row[i] = bit mask of the 1s in A[i]
2. for k = 1 to n do
3.     for i = 1 to n do
4.         if bit k of row[i] = 1 then row[i] = row[i] OR row[k]   // one row OR (count)
5. return the bits of row[1..n]
```

## 4. Reference for verification (BFS from every vertex)
```
Algorithm ClosureBFS(A)
1. for s = 1 to n do
2.     queue = all direct successors of s;  mark them reachable from s
3.     while queue not empty do
4.         u = dequeue();  for each successor t of u not yet marked: mark t, enqueue t
5. return the marks as matrix R
```
Costs: Warshall Θ(n³) time, Θ(n²) space; row-skip O(n³) (fewer steps on sparse graphs);
bitset Θ(n³ / word size); BFS reference Θ(n(n + m)).
