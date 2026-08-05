"""
Day 150 Practice: Fast Exponentiation

6 exercises: iterative binary pow, modular pow, Fermat inverse,
matrix multiply, matrix power, Fibonacci by doubling.
Implement the TODO functions, then run: python practice.py
"""


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Iterative binary exponentiation
# ===================================================================
# Compute a^n in O(log n) for integer n >= 0. Do NOT use Python's `**` or `pow`.

def fast_pow(a, n):
    """Return a**n using square-and-multiply."""
    # TODO: implement
    pass


def _sol_fast_pow(a, n):
    result = 1
    base = a
    while n > 0:
        if n & 1:
            result *= base
        base *= base
        n >>= 1
    return result


# ===================================================================
# Exercise 2: Modular power
# ===================================================================
# Compute a^n mod m. Mod after every multiply.

def mod_pow(a, n, m):
    """Return (a**n) % m using square-and-multiply."""
    # TODO: implement (do not use Python's pow(a, n, m))
    pass


def _sol_mod_pow(a, n, m):
    if m == 1:
        return 0
    result = 1
    base = a % m
    while n > 0:
        if n & 1:
            result = (result * base) % m
        base = (base * base) % m
        n >>= 1
    return result


# ===================================================================
# Exercise 3: Modular inverse by Fermat's little theorem
# ===================================================================
# Given prime p and a not divisible by p, return a^(-1) mod p.

def mod_inverse(a, p):
    """Return modular inverse of a modulo prime p."""
    # TODO: implement using mod_pow
    pass


def _sol_mod_inverse(a, p):
    return _sol_mod_pow(a, p - 2, p)


# ===================================================================
# Exercise 4: 2x2 matrix multiply
# ===================================================================
# Matrix is a 4-tuple (a, b, c, d) representing [[a, b], [c, d]].

def mat_mul(A, B):
    """Return A * B for 2x2 matrices A, B."""
    # TODO: implement
    pass


def _sol_mat_mul(A, B):
    a, b, c, d = A
    e, f, g, h = B
    return (a*e + b*g, a*f + b*h, c*e + d*g, c*f + d*h)


# ===================================================================
# Exercise 5: 2x2 matrix power
# ===================================================================
# Compute M^n in O(log n) matrix multiplies.

def mat_pow(M, n):
    """Return M**n for 2x2 matrix M and integer n >= 0."""
    # TODO: implement
    pass


def _sol_mat_pow(M, n):
    result = (1, 0, 0, 1)  # identity
    base = M
    while n > 0:
        if n & 1:
            result = _sol_mat_mul(result, base)
        base = _sol_mat_mul(base, base)
        n >>= 1
    return result


# ===================================================================
# Exercise 6: Fibonacci F(n) in O(log n)
# ===================================================================
# Use matrix exponentiation [[1,1],[1,0]]^n.

def fib_fast(n):
    """Return the n-th Fibonacci number. F(0)=0, F(1)=1, F(2)=1, ..."""
    # TODO: use mat_pow
    pass


def _sol_fib_fast(n):
    if n == 0:
        return 0
    a, b, c, d = _sol_mat_pow((1, 1, 1, 0), n)
    return b


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    expected: {expected}")
            print(f"    got:      {got}")
            failed += 1

    # --- Exercise 1 ---
    print("Exercise 1: fast_pow")
    check("2^0", try_or_sol("fast_pow", 2, 0), 1)
    check("3^13", try_or_sol("fast_pow", 3, 13), 1594323)
    check("2^20", try_or_sol("fast_pow", 2, 20), 1048576)

    # --- Exercise 2 ---
    print("\nExercise 2: mod_pow")
    check("2^10 mod 1000", try_or_sol("mod_pow", 2, 10, 1000), 24)
    check("3^200 mod 50", try_or_sol("mod_pow", 3, 200, 50), pow(3, 200, 50))
    check("any mod 1", try_or_sol("mod_pow", 5, 7, 1), 0)
    check("big crypto-style", try_or_sol("mod_pow", 65537, 12345, 10**9+7),
          pow(65537, 12345, 10**9+7))

    # --- Exercise 3 ---
    print("\nExercise 3: Fermat inverse")
    p = 1000003  # prime
    inv = try_or_sol("mod_inverse", 5, p)
    check("5 * inv % p == 1", (5 * inv) % p, 1)
    inv = try_or_sol("mod_inverse", 1234, p)
    check("1234 * inv % p == 1", (1234 * inv) % p, 1)

    # --- Exercise 4 ---
    print("\nExercise 4: mat_mul")
    A = (1, 2, 3, 4)  # [[1,2],[3,4]]
    B = (5, 6, 7, 8)  # [[5,6],[7,8]]
    # AB = [[19,22],[43,50]]
    check("[[1,2],[3,4]] * [[5,6],[7,8]]", try_or_sol("mat_mul", A, B),
          (19, 22, 43, 50))
    I = (1, 0, 0, 1)
    check("identity", try_or_sol("mat_mul", A, I), A)

    # --- Exercise 5 ---
    print("\nExercise 5: mat_pow")
    check("I^5", try_or_sol("mat_pow", (1, 0, 0, 1), 5), (1, 0, 0, 1))
    # [[1,1],[1,0]]^3 = [[3,2],[2,1]]  (since F4=3, F3=2, F2=1)
    check("Fib matrix ^3", try_or_sol("mat_pow", (1, 1, 1, 0), 3),
          (3, 2, 2, 1))

    # --- Exercise 6 ---
    print("\nExercise 6: fib_fast")
    check("F(0)", try_or_sol("fib_fast", 0), 0)
    check("F(1)", try_or_sol("fib_fast", 1), 1)
    check("F(10)", try_or_sol("fib_fast", 10), 55)
    check("F(50)", try_or_sol("fib_fast", 50), 12586269025)

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
