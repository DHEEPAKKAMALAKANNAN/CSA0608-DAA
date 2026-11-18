# Q5 – Brute-Force Convex Hull for Wildlife-Reserve Boundary Monitoring: Derivation and Pseudocode

*Derived from the single given principle before any code was written: "A line joining two candidate points may form
part of the outer boundary if all remaining points lie on an appropriate single side of that line."*

## 1. Turning the principle into a computation

**(a) How two candidate points define a line.** Stations Pᵢ = (xᵢ, yᵢ) and Pⱼ = (xⱼ, yⱼ) define the directed line
Pᵢ → Pⱼ with direction vector (xⱼ − xᵢ, yⱼ − yᵢ). I deliberately avoid the slope form y = mx + c because a
vertical boundary (xᵢ = xⱼ) would need a division by zero.

**(b) Position of another point relative to the line.** For a third station Pₖ compute the 2-D cross product

  orient(Pᵢ, Pⱼ, Pₖ) = (xⱼ − xᵢ)(yₖ − yᵢ) − (yⱼ − yᵢ)(xₖ − xᵢ)

  * > 0 ⇒ Pₖ lies to the **left** of Pᵢ → Pⱼ (counter-clockwise turn)
  * < 0 ⇒ Pₖ lies to the **right** (clockwise turn)
  * = 0 ⇒ Pₖ is **collinear** with Pᵢ and Pⱼ.

  This is the same quantity as (a·xₖ + b·yₖ − c) for the line a·x + b·y = c with a = yⱼ − yᵢ, b = xᵢ − xⱼ,
  c = xᵢyⱼ − yᵢxⱼ (Levitin's form), up to sign. With integer coordinates it is computed exactly.

**(c) How the remaining points are examined.** For each pair (i < j) every other station k ≠ i, j is classified
once as left / right / collinear-inside-segment / collinear-outside-segment.

**(d) Condition that identifies a hull edge.** Segment PᵢPⱼ is accepted iff

  1. no station is strictly on one of the two sides (all on the left **or** all on the right), **and**
  2. every collinear station lies **between** Pᵢ and Pⱼ (inside the segment's bounding box).

  Rule 2 handles collinear boundary stations: if a station lies on the line *beyond* Pⱼ, then PᵢPⱼ is only part
  of a longer boundary edge and Pⱼ is not a corner, so the pair is rejected; the pair formed by the two outermost
  collinear stations is the one accepted. Stations strictly between them lie on the boundary but are not corners.

**(e) How the final boundary is constructed.** Each accepted edge is stored **directed** so that all other
stations are on its left (if they were all on the right, store Pⱼ → Pᵢ instead). Every corner then has exactly one
outgoing edge, so the boundary is obtained by starting at the lowest (then left-most) corner and following
`next[·]` until returning to the start: a counter-clockwise polygon.

**Pre-processing for the challenge configuration:** duplicate stations (identical coordinates) are removed first
(O(n) with a hash set) – a duplicate would otherwise create a zero-length "line" for which every point is
collinear. Degenerate inputs: 0–2 distinct stations, or all stations collinear, return the 1–2 extreme stations.

## 2. Pseudocode

```
ORIENT(p, q, r)  return (q.x − p.x)(r.y − p.y) − (q.y − p.y)(r.x − p.x)

BETWEEN(p, q, r) // r is known to be collinear with p and q
    return min(p.x,q.x) ≤ r.x ≤ max(p.x,q.x) and min(p.y,q.y) ≤ r.y ≤ max(p.y,q.y)

BRUTE-FORCE-HULL(S)
    P ← S with duplicate coordinates removed ; n ← |P|
    if n ≤ 2 then return P
    tests ← 0 ; next ← empty map
    for i ← 0 to n−2 do
        for j ← i+1 to n−1 do                      // C(n,2) candidate segments
            left ← 0 ; right ← 0 ; outside ← false
            for k ← 0 to n−1, k ∉ {i, j} do         // n−2 other stations
                tests ← tests + 1
                o ← ORIENT(P[i], P[j], P[k])
                if o > 0 then left ← left + 1
                else if o < 0 then right ← right + 1
                else if not BETWEEN(P[i], P[j], P[k]) then outside ← true
            if outside or (left > 0 and right > 0) then continue     // not a hull edge
            if right = 0 then next[i] ← j else next[j] ← i            // keep others on the left (CCW)
    if next has a single entry (all stations collinear) then return its two endpoints
    start ← corner with smallest y (then smallest x) ; hull ← [start] ; v ← next[start]
    while v ≠ start do append v to hull ; v ← next[v]
    return hull (counter-clockwise), tests
```

Optional refinement measured separately ("early rejection"): stop scanning k as soon as both a left and a right
station (or a collinear-outside station) has been seen – it can only *reject* faster; acceptance still needs all
n−2 tests.

## 3. Predicted computational work

Orientation tests (full scan) = C(n,2)·(n−2) = n(n−1)(n−2)/2 ∈ Θ(n³). Doubling n multiplies the work by ≈ 8.
For n = 320: 320·319·318/2 = 16 230 240 tests. Early rejection should make random inputs much cheaper
(most segments are rejected after a few stations) but cannot improve the Θ(n³) worst case guarantee.

## 4. Test configurations

* **Config A – boundary + interior:** 10 stations on the reserve perimeter (convex position on an ellipse) and 30
  interior stations. Expected hull = exactly the 10 perimeter stations.
* **Config B – designed challenge:** a rectangular reserve with extra stations along every side (collinear
  boundary points, including two vertical sides where a slope would be undefined), two exact duplicate stations
  (a corner and an interior one), and interior stations collinear with a diagonal. Expected hull = the 4 corners
  only; side stations reported as "on boundary, not corners"; duplicates removed.
* **Degenerate unit tests:** single station, two stations, three collinear stations, all stations on one line.
