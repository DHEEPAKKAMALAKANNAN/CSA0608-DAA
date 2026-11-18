# Exercise 46 - Karatsuba multiplication of two integers


def karatsuba(x, y, depth=0, trace=False):
    """Multiply x and y with three recursive multiplications instead of four."""
    if x < 10 or y < 10:
        return x * y
    half = max(len(str(x)), len(str(y))) // 2
    p = 10 ** half
    a, b = divmod(x, p)                      # x = a*p + b
    c, d = divmod(y, p)                      # y = c*p + d
    z2 = karatsuba(a, c, depth + 1, trace)           # a*c
    z0 = karatsuba(b, d, depth + 1, trace)           # b*d
    z3 = karatsuba(a + b, c + d, depth + 1, trace)   # (a+b)*(c+d)
    z1 = z3 - z2 - z0                                 # a*d + b*c
    result = z2 * p * p + z1 * p + z0
    if trace and depth == 0:
        print(f"Step 1  : split with p = 10^{half}: a={a}, b={b}, c={c}, d={d}")
        print(f"Step 2  : z2 = a*c = {z2}, z0 = b*d = {z0}, (a+b)*(c+d) = {z3}")
        print(f"Step 3  : z1 = {z3} - {z2} - {z0} = {z1}")
        print(f"Step 4  : z = z2*10^{2 * half} + z1*10^{half} + z0 = {z2 * p * p} + {z1 * p} + {z0}")
    return result


if __name__ == "__main__":
    x, y = 1234, 5678
    print("Test Case 1")
    print(f"Input   : x = {x}, y = {y}")
    z = karatsuba(x, y, trace=True)
    print(f"Output  : z = {x} x {y} = {z}")
    print(f"Check   : built-in multiplication gives {x * y} -> match = {z == x * y}")
    claimed = 7016652
    if z != claimed:
        print(f"Note    : document lists {claimed}; correct value is {z} (the document has a typo)")
    print()
    print("Complexity: T(n) = 3T(n/2) + O(n) = O(n^log2(3)) ~ O(n^1.585) versus O(n^2) for schoolbook.")
