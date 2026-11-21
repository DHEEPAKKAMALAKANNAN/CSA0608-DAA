# Task 5: Same Graph, Different Algorithmic Reasoning – Dijkstra, Bellman-Ford, and Floyd

## 1. Problem Overview
- **Scenario:** Optimal routing over a directed weighted graph representing a communication or transportation network.
- **Topology:** Vertices $V = \{A, B, C, D, E\}$, with 7 directed edges:
  $$\{(A \to B, 4), \; (A \to C, 7), \; (B \to C, 2), \; (B \to D, 6), \; (C \to D, 1), \; (D \to E, 3), \; (C \to E, 8)\}$$
- **Comparative Focus:** Contrasting three distinct algorithmic paradigms over the identical graph:
  1. **Greedy Single-Source Shortest Paths (Dijkstra):** Irrevocable commitments under non-negative weights.
  2. **Dynamic Programming Single-Source by Edge Bound (Bellman-Ford):** Repeated relaxation tolerating negative weights and detecting negative cycles.
  3. **Dynamic Programming All-Pairs by Intermediate Vertices (Floyd-Warshall):** All-pairs matrix optimization.

---

## 2. Task 5.1: Greedy Shortest-Path Design (Dijkstra)

### Algorithmic Concept:
Under non-negative edge weights ($w(u, v) \ge 0$), the vertex with the minimum tentative distance in the priority queue cannot be improved by any unexplored path, because any alternative path must traverse an already unsettled vertex whose path distance is already larger or equal.

### SIMATS Standard Pseudocode:
```text
ALGORITHM GreedyShortestPaths(V, E, w, s)
INPUT:
    V – set of graph vertices
    E – set of directed edges (u, v) with non-negative weights w(u, v) >= 0
    s – source vertex (s ∈ V)
OUTPUT:
    dist – array where dist[v] is the shortest path weight from s to v
    pred – array where pred[v] is the predecessor vertex on the shortest path
BEGIN
    // Step 1: Initialisation
    FOR each vertex v ∈ V DO
        dist[v] ← ∞
        pred[v] ← NIL
    END FOR
    dist[s] ← 0
    
    Q ← PriorityQueue of all vertices v ∈ V, keyed by dist[v]
    Settled ← ∅
    
    // Step 2: Extraction and Relaxation Loop
    WHILE Q is not empty DO
        u ← EXTRACT_MIN(Q)
        IF dist[u] = ∞ THEN
            BREAK    // Remaining vertices are unreachable
        END IF
        
        Settled ← Settled ∪ {u}    // Greedy commitment: dist[u] is finalized
        
        FOR each edge (u, v) ∈ E with v ∉ Settled DO
            IF dist[u] + w(u, v) < dist[v] THEN
                dist[v] ← dist[u] + w(u, v)    // Distance update
                pred[v] ← u                    // Predecessor update
                DECREASE_KEY(Q, v, dist[v])
            END IF
        END FOR
    END WHILE
    
    RETURN dist, pred
END
```

### Manual Desk-Check Trace from Source A:
| Step | Extracted $u$ ($\text{dist}[u]$) | Directed Edges Relaxed $(u \to v)$ | Relaxation Calculations | $\text{dist}$ Vector `[A, B, C, D, E]` | Predecessor Updates |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **Init** | – | – | $\text{dist}[A] = 0$ | `[0, ∞, ∞, ∞, ∞]` | All `NIL` |
| **1** | **A (0)** | $A \to B, \; A \to C$ | $0+4=4 < \infty \implies 4$<br>$0+7=7 < \infty \implies 7$ | `[0, 4, 7, ∞, ∞]` | $pred[B]=A$<br>$pred[C]=A$ |
| **2** | **B (4)** | $B \to C, \; B \to D$ | $4+2=6 < 7 \implies 6$<br>$4+6=10 < \infty \implies 10$ | `[0, 4, 6, 10, ∞]` | $pred[C]=B$<br>$pred[D]=B$ |
| **3** | **C (6)** | $C \to D, \; C \to E$ | $6+1=7 < 10 \implies 7$<br>$6+8=14 < \infty \implies 14$ | `[0, 4, 6, 7, 14]` | $pred[D]=C$<br>$pred[E]=C$ |
| **4** | **D (7)** | $D \to E$ | $7+3=10 < 14 \implies 10$ | `[0, 4, 6, 7, 10]` | $pred[E]=D$ |
| **5** | **E (10)** | None | Out-degree = 0; $Q = \emptyset$ | `[0, 4, 6, 7, 10]` | – |

**Final Single-Source Results from A:**
- $\text{dist}[A] = 0$
- $\text{dist}[B] = 4 \quad (\text{Path: } A \to B)$
- $\text{dist}[C] = 6 \quad (\text{Path: } A \to B \to C)$
- $\text{dist}[D] = 7 \quad (\text{Path: } A \to B \to C \to D)$
- $\text{dist}[E] = 10 \quad (\text{Path: } A \to B \to C \to D \to E)$
- *Shortest-Path Tree (SPT) Edges:* $\{(A, B), (B, C), (C, D), (D, E)\}$.

---

## 3. Task 5.2: Relaxing Graph Assumptions – Bellman-Ford

### Why Greedy Commitment Fails under Negative Edges:
- The fundamental premise of Dijkstra is the **irrevocable closure** $\text{Settled} \leftarrow \text{Settled} \cup \{u\}$. Once settled, $u$ is never re-examined.
- **Counter-Example (Scenario N1):** Let $A \to B = 2$, $A \to C = 4$, and $C \to B = -3$.
  - Dijkstra extracts $B$ with tentative distance $2$ and permanently settles it.
  - Dijkstra then extracts $C$ with distance $4$, discovering the edge $C \to B$ which offers path distance $4 + (-3) = 1$.
  - Because $B$ is already settled, Dijkstra ignores this update and outputs $\text{dist}[B] = 2$ instead of the true shortest distance $1$ (Path: $A \to C \to B$).

### Bellman-Ford Pseudocode (Repeated Relaxation):
```text
ALGORITHM BellmanFord(V, E, w, s)
INPUT:
    V – set of vertices
    E – set of directed edges (weights w(u, v) may be negative)
    s – source vertex
OUTPUT:
    dist, pred, and NegCycle (TRUE if negative cycle reachable, FALSE otherwise)
BEGIN
    FOR each vertex v ∈ V DO
        dist[v] ← ∞
        pred[v] ← NIL
    END FOR
    dist[s] ← 0
    
    // Core Invariant: |V| - 1 passes guarantees shortest paths with <= |V|-1 edges
    FOR k ← 1 TO |V| - 1 DO
        Changed ← FALSE
        FOR each edge (u, v) ∈ E DO
            IF dist[u] ≠ ∞ AND dist[u] + w(u, v) < dist[v] THEN
                dist[v] ← dist[u] + w(u, v)
                pred[v] ← u
                Changed ← TRUE
            END IF
        END FOR
        IF Changed = FALSE THEN
            BREAK    // Early convergence
        END IF
    END FOR
    
    // Negative Cycle Detection: |V|-th pass
    NegCycle ← FALSE
    FOR each edge (u, v) ∈ E DO
        IF dist[u] ≠ ∞ AND dist[u] + w(u, v) < dist[v] THEN
            NegCycle ← TRUE
            BREAK
        END IF
    END FOR
    
    RETURN dist, pred, NegCycle
END
```

### Algorithmic Reasoning:
- **No Early Greedy Commitments:** All distances remain provisional throughout execution.
- **Pass Invariant:** After pass $k$, $\text{dist}[v]$ is upper-bounded by the weight of the shortest path from $s$ to $v$ that traverses at most $k$ edges. Any simple path contains at most $|V|-1$ edges; hence, $|V|-1$ passes suffice.
- **Negative Cycle Detection:** A path containing a cycle has $\ge |V|$ edges. If any edge can still undergo relaxation on the $|V|$-th pass, distance values can decrease infinitely, confirming the presence of a reachable negative-weight cycle.

---

## 4. Task 5.3: Changing Requirements – All-Pairs Shortest Paths (Floyd-Warshall)

### State Definition:
$$D^{(k)}[i][j]$$
represents the **length of the shortest path** from vertex $v_i$ to vertex $v_j$ such that all intermediate vertices on the path belong exclusively to the subset $\{v_1, v_2, \dots, v_k\}$.
- $D^{(0)}[i][j]$ is initialized directly from the adjacency weight matrix.
- $D^{(|V|)}[i][j]$ contains the global all-pairs shortest distances.

### State Transition Recurrence:
$$D^{(k)}[i][j] = \min\Big(D^{(k-1)}[i][j], \; D^{(k-1)}[i][k] + D^{(k-1)}[k][j]\Big)$$

### Floyd Pseudocode:
```text
ALGORITHM Floyd(W, n)
INPUT:
    W – n x n weight matrix (W[i][i] = 0; W[i][j] = weight of edge i->j, or ∞)
    n – number of vertices
OUTPUT:
    D    – n x n matrix of all-pairs shortest distances
    Next – n x n matrix for reconstructing shortest path routes
BEGIN
    FOR i ← 1 TO n DO
        FOR j ← 1 TO n DO
            D[i][j] ← W[i][j]
            IF i ≠ j AND W[i][j] ≠ ∞ THEN
                Next[i][j] ← j
            ELSE
                Next[i][j] ← NIL
            END IF
        END FOR
    END FOR
    
    // Triply nested DP transition
    FOR k ← 1 TO n DO
        FOR i ← 1 TO n DO
            FOR j ← 1 TO n DO
                IF D[i][k] + D[k][j] < D[i][j] THEN
                    D[i][j] ← D[i][k] + D[k][j]
                    Next[i][j] ← Next[i][k]
                END IF
            END FOR
        END FOR
    END FOR
    
    RETURN D, Next
END
```

### Complete All-Pairs Distance Matrix $D^{(5)}$:
| From \ To | **A** | **B** | **C** | **D** | **E** |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **A** | **0** | **4** | **6** | **7** | **10** |
| **B** | $\infty$ | **0** | **2** | **3** | **6** |
| **C** | $\infty$ | $\infty$ | **0** | **1** | **4** |
| **D** | $\infty$ | $\infty$ | $\infty$ | **0** | **3** |
| **E** | $\infty$ | $\infty$ | $\infty$ | $\infty$ | **0** |

*(Notice Row A identically reproduces the single-source results of Dijkstra and Bellman-Ford: `[0, 4, 6, 7, 10]`).*

---

## 5. Comparative Paradigm Matrix

| Dimension | Dijkstra | Bellman-Ford | Floyd-Warshall |
|:---|:---|:---|:---|
| **Strategy** | Greedy commitment | Dynamic Programming | Dynamic Programming |
| **Scope** | Single-Source | Single-Source | All-Pairs |
| **State Interpretation** | Minimum tentative distance discovered so far | Shortest path distance restricted to $\le k$ edges | Shortest path distance restricted to intermediate vertices $\in \{v_1..v_k\}$ |
| **Edge Weights** | Non-negative only ($w \ge 0$) | Arbitrary real weights | Arbitrary real weights (no negative cycles) |
| **Negative Cycles** | Silent failure / incorrect result | Detects reachable negative cycles | Detects negative cycles via $D[i][i] < 0$ |
| **Time Complexity** | $O((V + E) \log V)$ with min-heap | $\Theta(V \cdot E)$ | $\Theta(V^3)$ |
| **Space Complexity** | $\Theta(V)$ | $\Theta(V)$ | $\Theta(V^2)$ |

---

## 6. Implementation & Verification Details

### File Manifest:
- `single_source.py`: Dijkstra, Bellman-Ford, and negative weight test cases.
- `floyd_all_pairs.py`: Floyd-Warshall all-pairs matrix DP and path reconstruction.
- `graph_common.py`: Shared graph data structures and parsers.
- `graph.csv`: Graph topology dataset.
- `test_shortest_paths.py`: Test suite verifying equivalence against brute-force path enumeration across 400 random graphs.

### How to Run:
```bash
python single_source.py
python floyd_all_pairs.py
python test_shortest_paths.py
```

### Verification Result:
```text
=== TASK 5: TEST SUITE ===
PASS test_dijkstra_official_distances: [0, 4, 6, 7, 10]
PASS test_bellman_ford_official_distances: matches Dijkstra
PASS test_floyd_row_a_matches_single_source
PASS test_dijkstra_fails_on_negative_edge (Scenario N1 caught)
PASS test_bellman_ford_succeeds_on_negative_edge
PASS test_negative_cycle_detected (Scenario N2 detected)
PASS test_all_pairs_dense_graph (200 randomized non-negative graphs)
PASS test_all_pairs_dag_negative_edges (200 randomized DAGs)
PASS test_disconnected_graph_infinity
PASS test_single_vertex_graph
PASS test_path_reconstruction_fidelity
RESULT: 11/11 tests passed
```
