"""
Generates the Task 6 test data into test_data/ (deterministic: seed 45, chosen so that the optimal tour of the
main instance is unique up to its direction):
  delivery_locations.csv   map coordinates (km) of the hub and the 6 delivery locations A-F
  delivery_costs.csv       travel-cost matrix (minutes): straight-line distance x a seeded road-detour factor
                           in [1.00, 1.40], rounded; the same factor is used in both directions (symmetric roads)
  validation_hub4.csv      hub + 4 delivery locations (A-D sub-matrix) for the exhaustive validation of Task 6.4
  asymmetric_hub5.csv      hub + 5 locations with one-way-street asymmetry (cost[i][j] != cost[j][i])
  unreachable_hub3.csv     hub + 3 locations where location C has no road back to the hub or to A/B
Run:  py -3 make_delivery_data.py
"""
import csv
import os
import random

from tsp_held_karp import euclid

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "test_data")
LOCATIONS = [("Hub", 0.0, 0.0), ("A", 4.0, 7.0), ("B", -5.0, 6.0), ("C", 8.0, -2.0), ("D", -7.0, -4.0),
             ("E", 2.0, -8.0), ("F", -1.0, 10.0)]


def write_matrix(path, names, cost):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["from"] + names)
        for name, row in zip(names, cost):
            w.writerow([name] + ["inf" if c == float("inf") else c for c in row])


def main():
    rng = random.Random(45)
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "delivery_locations.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "x_km", "y_km"])
        w.writerows(LOCATIONS)
    names, size = [n for n, _, _ in LOCATIONS], len(LOCATIONS)
    cost = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(i + 1, size):
            detour = 1.0 + 0.4 * rng.random()
            minutes = round(2.0 * euclid(LOCATIONS[i][1:], LOCATIONS[j][1:]) * detour)   # 30 km/h average
            cost[i][j] = cost[j][i] = minutes
    write_matrix(os.path.join(DATA, "delivery_costs.csv"), names, cost)
    write_matrix(os.path.join(DATA, "validation_hub4.csv"), names[:5], [row[:5] for row in cost[:5]])
    asym = [row[:6] for row in cost[:6]]
    for i, j, extra in ((1, 3, 9), (2, 5, 7), (4, 0, 6)):                                # one-way detours
        asym[i][j] += extra
    write_matrix(os.path.join(DATA, "asymmetric_hub5.csv"), names[:6], asym)
    inf = float("inf")
    unreachable = [[0, 10, 12, 8], [10, 0, 6, inf], [12, 6, 0, inf], [8, inf, inf, 0]]
    write_matrix(os.path.join(DATA, "unreachable_hub3.csv"), ["Hub", "A", "B", "C"], unreachable)
    print("written:", ", ".join(sorted(os.listdir(DATA))))


if __name__ == "__main__":
    main()
