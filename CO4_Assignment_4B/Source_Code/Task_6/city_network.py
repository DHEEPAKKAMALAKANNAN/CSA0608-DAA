"""
Task 6 - test-data generator: a city road grid with coordinates and a nightly traffic feed.

city_grid(rows, cols, seed): junction (r, c) has id r*cols + c and coordinates (0.2c, 0.2r) km +/- 40 m;
two-way streets to the right and downwards (5% of streets missing). Every 10th row/column is an arterial
road at 60 km/h, other streets 20-40 km/h; each direction gets its own congestion factor 1.0-1.5.
Travel times are integer seconds. daily_feed() re-times ~5% of the roads (x0.8..x1.6) and closes ~0.5% (-1).
"""
import math
import random


def city_grid(rows, cols, seed=42):
    rng = random.Random(seed)
    n = rows * cols
    coords = [(0.2 * (i % cols) + rng.uniform(-0.04, 0.04), 0.2 * (i // cols) + rng.uniform(-0.04, 0.04))
              for i in range(n)]
    roads = []
    for r in range(rows):
        for c in range(cols):
            u = r * cols + c
            for dr, dc in ((0, 1), (1, 0)):
                rr, cc = r + dr, c + dc
                if rr >= rows or cc >= cols or rng.random() < 0.05:
                    continue
                v = rr * cols + cc
                arterial = (r % 10 == 0 and dr == 0) or (c % 10 == 0 and dc == 0)
                kmh = 60 if arterial else rng.uniform(20, 40)
                km = math.dist(coords[u], coords[v])
                for a, b in ((u, v), (v, u)):
                    roads.append((a, b, max(1, round(km / kmh * 3600 * rng.uniform(1.0, 1.5)))))
    return n, roads, coords


def daily_feed(roads, seed=7, retime=0.05, close=0.005):
    """Overnight feed [(u, v, seconds or -1)] for a random sample of existing roads."""
    rng = random.Random(seed)
    feed = []
    for u, v, w in roads:
        x = rng.random()
        if x < close:
            feed.append((u, v, -1))
        elif x < close + retime:
            feed.append((u, v, max(1, round(w * rng.uniform(0.8, 1.6)))))
    return feed


def apply_feed_to_list(roads, feed):
    """Reference semantics of the feed on a plain road list: closed roads removed, others re-timed."""
    new = {(u, v): w for u, v, w in roads}
    for u, v, w in feed:
        if w == -1:
            new.pop((u, v), None)
        else:
            new[(u, v)] = w
    return [(u, v, w) for (u, v), w in new.items()]
