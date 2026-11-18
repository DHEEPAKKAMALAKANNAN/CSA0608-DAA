"""
GIVEN CODE (Task 6) - ambulance route service v0.9, as received from a teammate. DO NOT FIX THIS FILE:
it is kept unchanged as the starting point of the debugging session (task6_debugging.py); the corrected
and optimised design is fixed_route_service.py.

Teammate's notes:
  "Dijkstra with heapq. Junctions are 0..n-1, roads are one-way (u, v, minutes); add both directions for a
   two-way street. route(src, dst) returns (minutes, list of junctions). apply_daily_update() takes the
   overnight feed [(u, v, minutes), ...] from the traffic department; the feed uses -1 for a closed road.
   self.stats counts work for the dashboard."
"""
import heapq
from collections import Counter


class RouteService:
    def __init__(self, n, roads):
        self.n = n
        self.roads = list(roads)
        self.stats = Counter()

    def apply_daily_update(self, updates):
        for u, v, minutes in updates:
            for i, (a, b, w) in enumerate(self.roads):
                self.stats["road_scans"] += 1
                if a == u and b == v:
                    self.roads[i] = (a, b, minutes)

    def neighbours(self, u):
        result = []
        for a, b, w in self.roads:
            self.stats["road_scans"] += 1
            if a == u:
                result.append((b, w))
        return result

    def route(self, src, dst):
        dist = {src: 0}
        prev = {}
        heap = [(0, src)]
        while heap:
            d, u = heapq.heappop(heap)
            self.stats["expansions"] += 1
            for v, w in self.neighbours(u):
                self.stats["relaxations"] += 1
                nd = d + w
                if v not in dist or nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    if v == dst:
                        return nd, self._path(prev, src, dst)
                    heapq.heappush(heap, (nd, v))
        return dist.get(dst, float("inf")), self._path(prev, src, dst)

    def _path(self, prev, src, dst):
        path = []
        v = dst
        while v != src:
            path.append(v)
            v = prev[v]
        return path
