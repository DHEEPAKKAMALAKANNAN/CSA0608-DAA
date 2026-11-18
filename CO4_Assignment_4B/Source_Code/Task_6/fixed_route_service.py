"""
Task 6 - FINAL DESIGN of the ambulance route service: debugged and optimised for the changed requirement
(the road network grows to 100,000 junctions and the travel times are replaced by a feed every night).

Defects of the given code (given_faulty_route_service.py) and where they are fixed here:
  D1  route() stopped when dst was first DISCOVERED -> stop only when dst is SETTLED (popped)   [route]
  D2  stale heap entries were expanded again        -> skip an entry whose time > best known   [route]
  D3  path reversed, source missing, KeyError when dst unreachable -> _path() / (inf, None)   [_path]
  D4  every neighbour lookup and every update scanned the whole road list, O(E) each
                                                    -> adjacency lists + (u, v) index, O(1)   [__init__]
  D5  daily feed not validated: -1 ('closed') used as a travel time, other negative times and
      unknown roads accepted silently -> validated, atomic update; closed = INF  [apply_daily_update]
Optimisations for 100,000 junctions:
  * adjacency lists built once per day, O(V + E); updates applied in O(1) each through the road index;
  * Dijkstra with a hand-written binary heap + lazy deletion, early exit at the destination;
  * optional A* (method="astar") when coordinates are known: h(v) = straight-line km to dst x the smallest
    seconds-per-km of any open road (re-calibrated after every update, so h never overestimates).
Travel times are integers (seconds in the city feed, minutes in the small test networks) so all sums are
exact; self.stats counts expansions, road scans and heap work.
"""
import math
from collections import Counter

INF = float("inf")


class MinHeap:
    """Binary min-heap of tuples with counted comparisons (lazy deletion: an entry may become stale)."""

    def __init__(self, stats):
        self.a, self.stats = [], stats

    def __len__(self):
        return len(self.a)

    def push(self, item):
        a = self.a
        a.append(item)
        self.stats["heap_pushes"] += 1
        i = len(a) - 1
        while i > 0:
            p = (i - 1) // 2
            self.stats["heap_comparisons"] += 1
            if a[i] < a[p]:
                a[i], a[p] = a[p], a[i]
                i = p
            else:
                break

    def pop(self):
        a = self.a
        top, last = a[0], a.pop()
        if a:
            a[0] = last
            i, n = 0, len(a)
            while True:
                s, l, r = i, 2 * i + 1, 2 * i + 2
                if l < n:
                    self.stats["heap_comparisons"] += 1
                    if a[l] < a[s]:
                        s = l
                if r < n:
                    self.stats["heap_comparisons"] += 1
                    if a[r] < a[s]:
                        s = r
                if s == i:
                    break
                a[i], a[s] = a[s], a[i]
                i = s
        return top


class RouteService:
    CLOSED = -1                                          # code used by the traffic feed for a closed road

    def __init__(self, n, roads, coords=None):
        """n junctions 0..n-1; roads = [(u, v, time)] one-way; coords = [(x_km, y_km)] or None."""
        if n < 1:
            raise ValueError("the network needs at least one junction")
        self.n, self.coords, self.stats = n, coords, Counter()
        self.adj = [[] for _ in range(n)]                # FIX D4: adjacency lists, built once in O(V + E)
        self.road = {}                                   # FIX D4: (u, v) -> its [v, seconds] entry
        for u, v, w in roads:
            self._check(u)
            self._check(v)
            if w < 0:
                raise ValueError(f"road ({u}, {v}) has negative travel time {w}")
            if u == v:
                continue                                 # a self-loop never shortens a route
            if (u, v) in self.road:                      # parallel roads: keep the faster one
                self.road[(u, v)][1] = min(self.road[(u, v)][1], w)
            else:
                entry = [v, w]
                self.adj[u].append(entry)
                self.road[(u, v)] = entry
        self._calibrate()

    def _check(self, j):
        if not (isinstance(j, int) and 0 <= j < self.n):
            raise ValueError(f"unknown junction {j!r}")

    def _calibrate(self):
        """Smallest seconds per km over all open roads: makes the A* heuristic admissible."""
        self.sec_per_km = 0.0
        if self.coords is None:
            return
        best = INF
        for u in range(self.n):
            xu, yu = self.coords[u]
            for v, w in self.adj[u]:
                km = math.hypot(self.coords[v][0] - xu, self.coords[v][1] - yu)
                if w != INF and km > 0:
                    best = min(best, w / km)
        self.sec_per_km = 0.0 if best == INF else best

    def apply_daily_update(self, updates):
        """updates = [(u, v, seconds)]; seconds = -1 closes the road, any value >= 0 (re)opens it.
        The whole feed is validated first, so a bad record leaves the network unchanged (atomic)."""
        for u, v, w in updates:                          # FIX D5: validate before changing anything
            self._check(u)
            self._check(v)
            if (u, v) not in self.road:
                raise ValueError(f"update for unknown road ({u}, {v})")
            if w < 0 and w != self.CLOSED:
                raise ValueError(f"invalid travel time {w} for road ({u}, {v})")
        summary = Counter()
        for u, v, w in updates:
            entry = self.road[(u, v)]                    # FIX D4: O(1) per record, not O(E)
            if w == self.CLOSED:
                entry[1] = INF                           # closed: never relaxed, can be reopened later
                summary["closed"] += 1
            else:
                summary["reopened" if entry[1] == INF else "retimed"] += 1
                entry[1] = w
        self._calibrate()
        return summary

    def _h(self, v, dst):
        if self.sec_per_km == 0.0:
            return 0
        (x1, y1), (x2, y2) = self.coords[v], self.coords[dst]
        return math.hypot(x2 - x1, y2 - y1) * self.sec_per_km

    def route(self, src, dst, method="dijkstra"):
        """Fastest route. Returns (seconds, [src, ..., dst]) or (inf, None) if dst cannot be reached."""
        self._check(src)
        self._check(dst)
        astar = method == "astar" and self.coords is not None
        h = (lambda v: self._h(v, dst)) if astar else (lambda v: 0)
        dist, prev = {src: 0}, {}
        heap = MinHeap(self.stats)
        heap.push((h(src), 0, src))
        while heap:
            _, g, u = heap.pop()
            if g > dist[u]:                              # FIX D2: stale entry - u was improved later
                self.stats["stale_skipped"] += 1
                continue
            self.stats["expansions"] += 1
            if u == dst:                                 # FIX D1: dst is final only when it is SETTLED
                return g, self._path(prev, src, dst)
            for v, w in self.adj[u]:
                self.stats["road_scans"] += 1
                ng = g + w
                if ng < dist.get(v, INF):
                    dist[v], prev[v] = ng, u
                    heap.push((ng + h(v), ng, v))
        return INF, None                                 # FIX D3: unreachable is a result, not a crash

    @staticmethod
    def _path(prev, src, dst):
        path = [dst]                                     # FIX D3: walk back, include src, then reverse
        while path[-1] != src:
            path.append(prev[path[-1]])
        return path[::-1]
