# Exercise 57 - Prefix and Suffix Search (WordFilter using a trie)

class WordFilter:
    """Every word is inserted once for each of its suffixes in the form
    '<suffix>{<word>' (the '{' separator is not a lowercase letter).
    A query for (pref, suff) is then the single trie path '<suff>{<pref>'.
    Words are inserted in index order, so each node keeps the LARGEST index."""

    def __init__(self, words):
        self.root = {}
        for index, word in enumerate(words):
            for i in range(len(word) + 1):
                node = self.root
                for ch in word[i:] + "{" + word:
                    node = node.setdefault(ch, {})
                    node["#"] = index            # later words overwrite earlier ones

    def f(self, pref, suff):
        node = self.root
        for ch in suff + "{" + pref:
            if ch not in node:
                return -1
            node = node[ch]
        return node["#"]


def run(operations, arguments):
    """Replay a LeetCode-style call list: ['WordFilter', 'f', ...] with its arguments."""
    outputs, obj = [], None
    for op, args in zip(operations, arguments):
        if op == "WordFilter":
            obj = WordFilter(*args)
            outputs.append("null")
        else:
            outputs.append(str(obj.f(*args)))
    return "[" + ", ".join(outputs) + "]"


if __name__ == "__main__":
    tests = [
        (["WordFilter", "f"], [[["apple"]], ["a", "e"]], "[null, 0]"),
        # extra case: several words, largest index wins, and a miss
        (["WordFilter", "f", "f", "f", "f"],
         [[["apple", "apply", "ample"]], ["a", "e"], ["app", "y"], ["ap", "e"], ["b", "e"]],
         None),
    ]
    for no, (ops, args, expected) in enumerate(tests, 1):
        print(f"Test Case {no}" + ("   (extra)" if expected is None else ""))
        print(f"Input   : {ops}")
        print(f"          {args}")
        print(f"Output  : {run(ops, args)}")
        if expected:
            print(f"Expected: {expected}")
        print()
    print("Time complexity : build O(N * L^2) for N words of length <= L; each query O(|pref| + |suff|)")
    print("Space complexity: O(N * L^2) trie nodes")
