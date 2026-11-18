# Exercise 56 - Text Justification (greedy line packing)

def full_justify(words, max_width):
    lines, i = [], 0
    while i < len(words):
        # Greedy: pack as many words as fit (one space minimum between words)
        j, length = i, len(words[i])
        while j + 1 < len(words) and length + 1 + len(words[j + 1]) <= max_width:
            j += 1
            length += 1 + len(words[j])
        line_words = words[i:j + 1]
        if j == len(words) - 1 or len(line_words) == 1:
            # last line, or a line with one word: left-justify and pad on the right
            line = " ".join(line_words).ljust(max_width)
        else:
            spaces = max_width - sum(len(w) for w in line_words)
            gaps = len(line_words) - 1
            each, extra = divmod(spaces, gaps)      # leftmost `extra` gaps get one more
            line = ""
            for k, w in enumerate(line_words[:-1]):
                line += w + " " * (each + (1 if k < extra else 0))
            line += line_words[-1]
        lines.append(line)
        i = j + 1
    return lines


if __name__ == "__main__":
    tests = [
        (["This", "is", "an", "example", "of", "text", "justification."], 16,
         ["This    is    an", "example  of text", "justification.  "]),
        (["What", "must", "be", "acknowledgment", "shall", "be"], 16,
         ["What   must   be", "acknowledgment  ", "shall be        "]),
    ]
    for no, (words, width, expected) in enumerate(tests, 1):
        result = full_justify(words, width)
        print(f"Test Case {no}")
        print(f"Input   : words = {words}, maxWidth = {width}")
        print("Output  :")
        for line in result:
            print(f'   "{line}"   (length {len(line)})')
        print(f"Expected: {expected}")
        print(f"Matches the expected output: {result == expected}")
        print()
    print("Time complexity : O(total characters)  - each word is placed exactly once")
    print("Space complexity: O(total characters)  - for the output lines")
