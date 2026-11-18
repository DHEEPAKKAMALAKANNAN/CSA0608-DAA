# Exercise 78 - Minimum Number of Containers (greedy, fill the current container first)
# The stated greedy rule = "next fit": keep loading items (in the given order) into the
# current container; when the next item does not fit, close it and open a new one.


def containers_next_fit(weights, capacity):
    containers, current, used = [], [], 0
    for w in weights:
        if used + w > capacity:            # current container is as full as it gets
            containers.append(current)
            current, used = [], 0
        current.append(w)
        used += w
    if current:
        containers.append(current)
    return containers


def containers_first_fit_decreasing(weights, capacity):
    """For comparison: heaviest item first, into the first container with room."""
    bins = []
    for w in sorted(weights, reverse=True):
        for b in bins:
            if sum(b) + w <= capacity:
                b.append(w)
                break
        else:
            bins.append([w])
    return bins


if __name__ == "__main__":
    tests = [([5, 10, 15, 20, 25, 30, 35], 50, 4),
             ([10, 20, 30, 40, 50, 60, 70, 80], 100, 6)]
    for no, (weights, cap, doc) in enumerate(tests, 1):
        boxes = containers_next_fit(weights, cap)
        better = containers_first_fit_decreasing(weights, cap)
        print(f"Test Case {no}")
        print(f"Input   : n = {len(weights)}, weights = {weights}, max_capacity = {cap}")
        for i, b in enumerate(boxes, 1):
            print(f"  Container {i}: {b} (load {sum(b)})")
        print(f"Output  : {len(boxes)}")
        if len(boxes) == doc:
            print(f"Expected: {doc}")
        else:
            print(f"Note    : document lists {doc}; correct value is {len(boxes)} "
                  f"for the stated greedy rule")
        print(f"Compare : first-fit decreasing needs {len(better)}; "
              f"lower bound ceil(sum/cap) = {-(-sum(weights) // cap)}")
        print()
    print("Time complexity : O(n) for the stated greedy; Space: O(n)")
