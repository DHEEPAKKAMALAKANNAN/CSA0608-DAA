# Exercise 63 - Cat and Mouse (game on a graph, solved by retrograde analysis / topological sort)
from collections import deque

DRAW, MOUSE, CAT = 0, 1, 2          # game results; also used as "whose turn" markers


def cat_mouse_game(graph):
    """State = (mouse node, cat node, player to move).  Start from the states whose result is
    known (mouse in hole -> mouse wins, cat on mouse -> cat wins) and propagate the result
    backwards.  States that never get a result are draws (they can repeat forever)."""
    n = len(graph)
    result = [[[DRAW] * 3 for _ in range(n)] for _ in range(n)]
    degree = [[[0] * 3 for _ in range(n)] for _ in range(n)]     # moves not yet proven losing
    for m in range(n):
        for c in range(1, n):
            degree[m][c][MOUSE] = len(graph[m])
            degree[m][c][CAT] = len(graph[c]) - (0 in graph[c])  # cat may not enter the hole
    queue = deque()
    for c in range(1, n):
        for turn in (MOUSE, CAT):
            result[0][c][turn] = MOUSE                           # mouse is in the hole
            queue.append((0, c, turn))
            result[c][c][turn] = CAT                             # cat caught the mouse
            queue.append((c, c, turn))

    def previous_states(m, c, turn):
        if turn == CAT:                       # the mouse has just moved
            return [(pm, c, MOUSE) for pm in graph[m]]
        return [(m, pc, CAT) for pc in graph[c] if pc != 0]      # the cat has just moved

    while queue:
        m, c, turn = queue.popleft()
        winner = result[m][c][turn]
        for pm, pc, pturn in previous_states(m, c, turn):
            if result[pm][pc][pturn] != DRAW:
                continue
            if pturn == winner:                   # mover can step into a winning state
                result[pm][pc][pturn] = winner
                queue.append((pm, pc, pturn))
            else:                                 # this move is bad; if all moves are bad, mover loses
                degree[pm][pc][pturn] -= 1
                if degree[pm][pc][pturn] == 0:
                    result[pm][pc][pturn] = winner
                    queue.append((pm, pc, pturn))
    return result[1][2][MOUSE]                    # mouse at 1, cat at 2, mouse moves first


if __name__ == "__main__":
    meaning = {0: "draw", 1: "mouse wins", 2: "cat wins"}
    tests = [([[2, 5], [3], [0, 4, 5], [1, 4, 5], [2, 3], [0, 2, 3]], 0),
             ([[1, 3], [0], [3], [0, 2]], 1)]
    for no, (graph, expected) in enumerate(tests, 1):
        answer = cat_mouse_game(graph)
        print(f"Test Case {no}")
        print(f"Input   : graph = {graph}")
        print(f"Output  : {answer}   ({meaning[answer]})")
        print(f"Expected: {expected}")
        print()
    print("Time complexity : O(n^3) - n*n*2 states, each state has up to n predecessor edges")
    print("Space complexity: O(n^2) for the result / degree tables")
