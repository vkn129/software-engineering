"""
Day 151 Practice: RSA fundamentals (toy)

WARNING: learning only. Do NOT use any of this for real security.

6 exercises: extended GCD, modular inverse, key gen, encrypt, decrypt,
attacker-recovers-key-by-factoring.
Implement the TODO functions, then run: python practice.py
"""

import math


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


# Built-in mod_pow used by exercises
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
# Exercise 1: Extended Euclidean
# ===================================================================
# Return (g, x, y) with a*x + b*y = g = gcd(a, b).

def ext_gcd(a, b):
    """Return (g, x, y)."""
    # TODO: implement (recursive or iterative)
    pass


def _sol_ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = _sol_ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


# ===================================================================
# Exercise 2: Modular Inverse via Extended Euclidean
# ===================================================================
# Return d with e*d = 1 (mod m). Assume gcd(e, m) = 1.

def mod_inverse(e, m):
    """Return modular inverse of e modulo m."""
    # TODO: implement using ext_gcd
    pass


def _sol_mod_inverse(e, m):
    g, x, _ = _sol_ext_gcd(e, m)
    if g != 1:
        return None
    return x % m


# ===================================================================
# Exercise 3: RSA Key Generation
# ===================================================================
# Given primes p, q, and public exponent e, return (N, e, d).
# d must satisfy e*d = 1 (mod phi(N)).

def rsa_keygen(p, q, e):
    """Return (N, e, d) tuple."""
    # TODO: implement
    pass


def _sol_rsa_keygen(p, q, e):
    N = p * q
    phi = (p - 1) * (q - 1)
    d = _sol_mod_inverse(e, phi)
    return N, e, d


# ===================================================================
# Exercise 4: RSA Encrypt
# ===================================================================
# c = m^e mod N.

def rsa_encrypt(m, N, e):
    """Return ciphertext."""
    # TODO: implement
    pass


def _sol_rsa_encrypt(m, N, e):
    return _mod_pow(m, e, N)


# ===================================================================
# Exercise 5: RSA Decrypt
# ===================================================================
# m = c^d mod N.

def rsa_decrypt(c, N, d):
    """Return plaintext."""
    # TODO: implement
    pass


def _sol_rsa_decrypt(c, N, d):
    return _mod_pow(c, d, N)


# ===================================================================
# Exercise 6: Attacker — recover d by factoring N
# ===================================================================
# Trial division to find p, q. Then derive phi and d. Demonstrates
# why a small N is insecure.

def recover_d(N, e):
    """Factor N, then return d."""
    # TODO: implement
    pass


def _sol_recover_d(N, e):
    for p in range(2, int(math.isqrt(N)) + 1):
        if N % p == 0:
            q = N // p
            phi = (p - 1) * (q - 1)
            return _sol_mod_inverse(e, phi)
    return None


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
    print("Exercise 1: Extended Euclidean")
    g, x, y = try_or_sol("ext_gcd", 30, 12)
    check("gcd(30,12) == 6", g, 6)
    check("30x + 12y = 6", 30 * x + 12 * y, 6)
    g, x, y = try_or_sol("ext_gcd", 17, 5)
    check("gcd(17,5) == 1", g, 1)
    check("17x + 5y = 1", 17 * x + 5 * y, 1)

    # --- Exercise 2 ---
    print("\nExercise 2: Modular Inverse")
    inv = try_or_sol("mod_inverse", 3, 11)
    check("3 * inv % 11 == 1", (3 * inv) % 11, 1)
    inv = try_or_sol("mod_inverse", 17, 3120)
    check("17 * inv % 3120 == 1", (17 * inv) % 3120, 1)

    # --- Exercise 3 ---
    print("\nExercise 3: RSA Key Generation")
    # Classic textbook example: p=61, q=53, e=17 -> d=2753
    N, e, d = try_or_sol("rsa_keygen", 61, 53, 17)
    check("N = 61*53", N, 3233)
    check("d = 2753", d, 2753)
    check("e*d mod phi == 1", (e * d) % (60 * 52), 1)

    # --- Exercise 4 ---
    print("\nExercise 4: RSA Encrypt")
    # 65 -> ? with N=3233, e=17
    c = try_or_sol("rsa_encrypt", 65, 3233, 17)
    check("encrypt(65)", c, pow(65, 17, 3233))

    # --- Exercise 5 ---
    print("\nExercise 5: RSA Decrypt — round-trip")
    for m in [42, 100, 1000, 2999]:
        c = try_or_sol("rsa_encrypt", m, 3233, 17)
        m2 = try_or_sol("rsa_decrypt", c, 3233, 2753)
        check(f"round-trip m={m}", m2, m)

    # --- Exercise 6 ---
    print("\nExercise 6: Attacker recovers d by factoring N")
    # Same toy key — show attacker can recover d from (N, e) alone
    d_recovered = try_or_sol("recover_d", 3233, 17)
    check("recovered d == 2753", d_recovered, 2753)
    # And the recovered d actually works on a fresh ciphertext
    c = try_or_sol("rsa_encrypt", 1729, 3233, 17)
    m = try_or_sol("rsa_decrypt", c, 3233, d_recovered)
    check("recovered d decrypts correctly", m, 1729)

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print("REMINDER: Toy RSA — learning only. Not safe for real use.")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
