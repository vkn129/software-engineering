"""
Day 153 Practice: Number Theoretic Transform (NTT)

6 exercises: mod inverse, primitive root finding, iterative NTT,
inverse NTT, polynomial multiplication, polynomial power.
Implement the TODO functions, then run: python practice.py
"""


MOD = 998244353  # 119 * 2^23 + 1
G = 3            # primitive root of MOD


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


def _mod_pow(base, exp, mod):
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


# ===================================================================
# Exercise 1: Modular Inverse via Fermat
# ===================================================================
# p is prime. Return a^{-1} mod p using Fermat: a^{p-2} mod p.

def mod_inv(a, p):
    """Return modular inverse of a mod prime p."""
    # TODO: implement
    pass


def _sol_mod_inv(a, p):
    return _mod_pow(a, p - 2, p)


# ===================================================================
# Exercise 2: Primitive n-th root of unity in Z_p
# ===================================================================
# Given prime p, generator g, and n (power of 2 dividing p-1),
# return omega with omega^n = 1 mod p and omega^k != 1 mod p for 0 < k < n.

def primitive_root_n(p, g, n):
    """Return omega = g^((p-1)/n) mod p."""
    # TODO: implement
    pass


def _sol_primitive_root_n(p, g, n):
    return _mod_pow(g, (p - 1) // n, p)


# ===================================================================
# Exercise 3: Iterative NTT (in place)
# ===================================================================
# Same shape as iterative FFT but modular. `invert=False` for forward.

def ntt(a, invert=False, mod=MOD, g=G):
    """Iterative NTT, in-place. Modifies and returns `a`."""
    # TODO: implement
    pass


def _sol_ntt(a, invert=False, mod=MOD, g=G):
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    m = 2
    while m <= n:
        if invert:
            wm = _sol_mod_inv(_mod_pow(g, (mod - 1) // m, mod), mod)
        else:
            wm = _mod_pow(g, (mod - 1) // m, mod)
        half = m // 2
        for k in range(0, n, m):
            w = 1
            for jj in range(half):
                u = a[k + jj]
                t = (w * a[k + jj + half]) % mod
                a[k + jj] = (u + t) % mod
                a[k + jj + half] = (u - t) % mod
                w = (w * wm) % mod
        m <<= 1
    if invert:
        n_inv = _sol_mod_inv(n, mod)
        for i in range(n):
            a[i] = (a[i] * n_inv) % mod
    return a


# ===================================================================
# Exercise 4: NTT round-trip identity
# ===================================================================
# Verify: inverse(forward(a)) == a (mod p). Return the recovered list.

def ntt_round_trip(a):
    """Forward NTT then inverse NTT. Should equal original."""
    # TODO: implement
    pass


def _sol_ntt_round_trip(a):
    b = list(a)
    _sol_ntt(b, invert=False)
    _sol_ntt(b, invert=True)
    return b


# ===================================================================
# Exercise 5: Polynomial multiplication via NTT
# ===================================================================
# Multiply two non-negative-int polynomials. Returns exact integer coefficients
# assuming each result coefficient is < MOD.

def poly_mul_ntt(p, q):
    """Return coefficients of p*q via NTT (integer exact mod MOD)."""
    # TODO: implement
    pass


def _sol_poly_mul_ntt(p, q):
    target = len(p) + len(q) - 1
    n = 1
    while n < target:
        n <<= 1
    pa = list(p) + [0] * (n - len(p))
    qa = list(q) + [0] * (n - len(q))
    _sol_ntt(pa)
    _sol_ntt(qa)
    ra = [(pa[i] * qa[i]) % MOD for i in range(n)]
    _sol_ntt(ra, invert=True)
    return ra[:target]


# ===================================================================
# Exercise 6: Polynomial squaring
# ===================================================================
# Square a polynomial using NTT. Bonus: only one forward NTT needed.

def poly_square(p):
    """Return coefficients of p*p using NTT."""
    # TODO: implement
    pass


def _sol_poly_square(p):
    target = 2 * len(p) - 1
    n = 1
    while n < target:
        n <<= 1
    pa = list(p) + [0] * (n - len(p))
    _sol_ntt(pa)
    ra = [(pa[i] * pa[i]) % MOD for i in range(n)]
    _sol_ntt(ra, invert=True)
    return ra[:target]


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
    print("Exercise 1: Modular inverse via Fermat")
    inv = try_or_sol("mod_inv", 5, MOD)
    check("5 * inv % p == 1", (5 * inv) % MOD, 1)
    inv = try_or_sol("mod_inv", 12345, MOD)
    check("12345 * inv % p == 1", (12345 * inv) % MOD, 1)

    # --- Exercise 2 ---
    print("\nExercise 2: Primitive n-th root of unity")
    omega = try_or_sol("primitive_root_n", MOD, G, 8)
    check("omega^8 == 1", _mod_pow(omega, 8, MOD), 1)
    check("omega^4 != 1", _mod_pow(omega, 4, MOD) != 1, True)
    check("omega^2 != 1", _mod_pow(omega, 2, MOD) != 1, True)

    # --- Exercise 3 ---
    print("\nExercise 3: NTT linearity (transform is reversible)")
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    b = list(a)
    try_or_sol("ntt", b, False)
    # round-trip
    try_or_sol("ntt", b, True)
    check("ntt then inverse recovers input", b, a)

    # --- Exercise 4 ---
    print("\nExercise 4: ntt_round_trip helper")
    a = [10, 20, 30, 40, 50, 60, 70, 80]
    check("round-trip", try_or_sol("ntt_round_trip", a), a)

    # --- Exercise 5 ---
    print("\nExercise 5: Polynomial multiplication")
    # Same examples as FFT day; results identical for small coeffs.
    check("(1+2x+3x^2)(4+5x+6x^2)",
          try_or_sol("poly_mul_ntt", [1, 2, 3], [4, 5, 6]),
          [4, 13, 28, 27, 18])
    check("(1+x)(1+x)", try_or_sol("poly_mul_ntt", [1, 1], [1, 1]),
          [1, 2, 1])
    # Random check vs naive
    import random
    random.seed(0)
    p = [random.randint(0, 99) for _ in range(30)]
    q = [random.randint(0, 99) for _ in range(40)]
    naive = [0] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            naive[i + j] += x * y
    check("random 30x40 exact", try_or_sol("poly_mul_ntt", p, q), naive)

    # --- Exercise 6 ---
    print("\nExercise 6: Polynomial squaring")
    # (1+2x+3x^2)^2 = 1 + 4x + 10x^2 + 12x^3 + 9x^4
    check("square small", try_or_sol("poly_square", [1, 2, 3]),
          [1, 4, 10, 12, 9])
    # random check
    p = [random.randint(0, 50) for _ in range(20)]
    naive = [0] * (2 * len(p) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(p):
            naive[i + j] += x * y
    check("random square", try_or_sol("poly_square", p), naive)

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
