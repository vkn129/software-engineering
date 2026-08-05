"""
Day 150: Fast Exponentiation — O(log n) by binary decomposition.

Iterative and recursive forms, modular power for crypto,
matrix exponentiation for linear recurrences.
"""

import time


# ---------------------------------------------------------------------------
# 1. Naive — O(n)
# ---------------------------------------------------------------------------

def pow_naive(a, n):
    """Repeated multiplication. O(n)."""
    result = 1
    for _ in range(n):
        result *= a
    return result


# ---------------------------------------------------------------------------
# 2. Recursive binary — O(log n)
# ---------------------------------------------------------------------------

def pow_recursive(a, n):
    """Recursive square-and-multiply. O(log n) time, O(log n) stack."""
    if n == 0:
        return 1
    if n & 1:
        return a * pow_recursive(a, n - 1)
    half = pow_recursive(a, n // 2)
    return half * half


# ---------------------------------------------------------------------------
# 3. Iterative binary — O(log n) — the production form
# ---------------------------------------------------------------------------

def pow_iter(a, n):
    """Square-and-multiply, walking the bits of n from low to high."""
    result = 1
    base = a
    while n > 0:
        if n & 1:
            result *= base
        base *= base
        n >>= 1
    return result


# ---------------------------------------------------------------------------
# 4. Modular power — crypto workhorse
# ---------------------------------------------------------------------------

def pow_mod(a, n, m):
    """a^n mod m in O(log n) multiplies, each modded."""
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


# ---------------------------------------------------------------------------
# 5. Modular inverse via Fermat's little theorem
# ---------------------------------------------------------------------------

def mod_inverse_fermat(a, p):
    """a^(p-2) mod p — only valid when p is prime and gcd(a, p) = 1."""
    return pow_mod(a, p - 2, p)


# ---------------------------------------------------------------------------
# 6. Matrix exponentiation
# ---------------------------------------------------------------------------

def mat_mul(A, B, m=None):
    """2x2 matrix multiply, optionally mod m."""
    a, b, c, d = A
    e, f, g, h = B
    r = (a*e + b*g, a*f + b*h, c*e + d*g, c*f + d*h)
    if m is not None:
        r = tuple(x % m for x in r)
    return r


def mat_pow(M, n, m=None):
    """M^n where M is a flat 2x2 tuple (a,b,c,d). O(log n) multiplies."""
    result = (1, 0, 0, 1)  # identity
    base = M
    while n > 0:
        if n & 1:
            result = mat_mul(result, base, m)
        base = mat_mul(base, base, m)
        n >>= 1
    return result


def fib(n, m=None):
    """Fibonacci F(n) in O(log n). Optionally mod m."""
    if n == 0:
        return 0
    # [[1,1],[1,0]]^n -> top-left is F(n+1), top-right is F(n)
    a, b, c, d = mat_pow((1, 1, 1, 0), n, m)
    return b


# ---------------------------------------------------------------------------
# 7. Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Three forms agree")
    print("=" * 60)
    a, n = 3, 13
    print(f"3^13 naive     = {pow_naive(a, n)}")
    print(f"3^13 recursive = {pow_recursive(a, n)}")
    print(f"3^13 iterative = {pow_iter(a, n)}")
    print(f"3^13 (Python)  = {a**n}")


def demo_modular():
    print("\n" + "=" * 60)
    print("DEMO 2: Modular Power")
    print("=" * 60)
    # 2^1000000 mod 1000003 — finite-field flavor
    print(f"2^1000000 mod 1000003 = {pow_mod(2, 1000000, 1000003)}")
    print(f"Built-in pow(2, 1000000, 1000003) = {pow(2, 1000000, 1000003)}")
    # Fermat inverse
    p = 1000003  # prime
    a = 5
    inv = mod_inverse_fermat(a, p)
    print(f"\nFermat inverse of {a} mod {p}: {inv}")
    print(f"Verify: {a} * {inv} mod {p} = {(a*inv) % p} (expect 1)")


def demo_perf():
    print("\n" + "=" * 60)
    print("DEMO 3: Speedup vs Naive")
    print("=" * 60)
    a, n = 7, 20000
    t = time.perf_counter()
    pow_naive(a, n)
    t_naive = time.perf_counter() - t
    t = time.perf_counter()
    pow_iter(a, n)
    t_iter = time.perf_counter() - t
    print(f"7^{n}:")
    print(f"  naive    : {t_naive*1000:8.3f} ms")
    print(f"  iterative: {t_iter*1000:8.3f} ms")
    print(f"  speedup  : {t_naive/t_iter:.1f}x")


def demo_matrix_fib():
    print("\n" + "=" * 60)
    print("DEMO 4: Matrix exponentiation (Fibonacci)")
    print("=" * 60)
    for n in [0, 1, 10, 50, 100]:
        print(f"F({n}) = {fib(n)}")
    big = 10**8
    t = time.perf_counter()
    val = fib(big, m=10**9 + 7)
    dt = time.perf_counter() - t
    print(f"\nF(10^8) mod 1e9+7 = {val}")
    print(f"Time: {dt*1000:.2f} ms (O(log n) matrix multiplies)")


if __name__ == "__main__":
    demo_basic()
    demo_modular()
    demo_perf()
    demo_matrix_fib()
