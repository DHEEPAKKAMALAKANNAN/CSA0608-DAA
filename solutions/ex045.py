# Exercise 45 - Strassen's matrix multiplication for 2x2 matrices (7 multiplications instead of 8)


def strassen_2x2(A, B):
    """Return (C, [M1..M7]) where C = A x B computed with Strassen's seven products."""
    (a, b), (c, d) = A
    (e, f), (g, h) = B
    m1 = (a + d) * (e + h)
    m2 = (c + d) * e
    m3 = a * (f - h)
    m4 = d * (g - e)
    m5 = (a + b) * h
    m6 = (c - a) * (e + f)
    m7 = (b - d) * (g + h)
    C = [[m1 + m4 - m5 + m7, m3 + m5],
         [m2 + m4, m1 - m2 + m3 + m6]]
    return C, [m1, m2, m3, m4, m5, m6, m7]


def naive_2x2(A, B):
    """Ordinary 8-multiplication product, used only to verify Strassen."""
    return [[sum(A[i][k] * B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def run_case(title, A, B, expected=None):
    C, m = strassen_2x2(A, B)
    print(title)
    print(f"Input   : A = {A}, B = {B}")
    print("Strassen: " + ", ".join(f"M{i + 1}={v}" for i, v in enumerate(m)))
    print(f"Output  : C = {C}")
    print(f"Check   : ordinary multiplication gives {naive_2x2(A, B)} -> match = {C == naive_2x2(A, B)}")
    if expected is not None:
        if C == expected:
            print(f"Expected: {expected}")
        else:
            print(f"Note    : document lists {expected}")
            print(f"          correct value is {C} (e.g. C[0][0] = 1*6 + 7*4 = {C[0][0]}, not {expected[0][0]})")
    print()


if __name__ == "__main__":
    run_case("Given matrices (problem statement)", [[1, 7], [3, 5]], [[1, 3], [7, 5]])
    run_case("Test Case 1", [[1, 7], [3, 5]], [[6, 8], [4, 2]], [[18, 14], [62, 66]])
    print("Formulas: C11 = M1+M4-M5+M7, C12 = M3+M5, C21 = M2+M4, C22 = M1-M2+M3+M6")
    print("Complexity: T(n) = 7T(n/2) + O(n^2) = O(n^log2(7)) ~ O(n^2.81) vs O(n^3) for the ordinary method.")
