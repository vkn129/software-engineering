"""
Day 152 Practice: FFT (Cooley-Tukey radix-2)

6 exercises: bit-reverse, recursive FFT, iterative FFT, inverse FFT,
polynomial multiplication, big-integer multiplication via FFT.
Implement the TODO functions, then run: python practice.py
"""

import cmath
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


def _close(a, b, tol=1e-6):
    if isinstance(a, list):
        return len(a) == len(b) and all(_close(x, y, tol) for x, y in zip(a, b))
    return abs(complex(a) - complex(b)) < tol


# ===================================================================
# Exercise 1: Bit-reversal permutation
# ===================================================================
# Return a NEW list with elements in bit-reversed order.
# (Lengths are always a power of 2.)

def bit_reverse(a):
    """Return list with elements at bit-reversed indices."""
    # TODO: implement
    pass


def _sol_bit_reverse(a):
    n = len(a)
    bits = (n - 1).bit_length()
    out = [None] * n
    for i in range(n):
        # reverse the lowest `bits` bits of i
        r = 0
        x = i
        for _ in range(bits):
            r = (r << 1) | (x & 1)
            x >>= 1
        out[r] = a[i]
    return out


# ===================================================================
# Exercise 2: Recursive FFT
# ===================================================================
# n is a power of 2. Return list of complex numbers.

def fft_recursive(a):
    """Radix-2 Cooley-Tukey, recursive."""
    # TODO: implement
    pass


def _sol_fft_recursive(a):
    n = len(a)
    if n == 1:
        return [complex(a[0])]
    even = _sol_fft_recursive(a[0::2])
    odd = _sol_fft_recursive(a[1::2])
    out = [0j] * n
    for k in range(n // 2):
        t = cmath.exp(-2j * math.pi * k / n) * odd[k]
        out[k] = even[k] + t
        out[k + n // 2] = even[k] - t
    return out


# ===================================================================
# Exercise 3: Iterative FFT
# ===================================================================
# In-place. Modifies and returns `a`. `invert=False` for forward FFT.

def fft_iter(a, invert=False):
    """In-place iterative FFT."""
    # TODO: implement
    pass


def _sol_fft_iter(a, invert=False):
    n = len(a)
    # bit-reverse permute in place
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
        ang = (2 * math.pi / m) * (1 if invert else -1)
        wm = cmath.exp(1j * ang)
        half = m // 2
        for k in range(0, n, m):
            w = 1 + 0j
            for jj in range(half):
                u = a[k + jj]
                t = w * a[k + jj + half]
                a[k + jj] = u + t
                a[k + jj + half] = u - t
                w *= wm
        m <<= 1
    if invert:
        for i in range(n):
            a[i] /= n
    return a


# ===================================================================
# Exercise 4: Inverse FFT (using forward FFT)
# ===================================================================
# Implement inverse FFT using ONLY the forward FFT, via the conjugate trick:
# ifft(A) = conj(fft(conj(A))) / n

def ifft_via_fft(A):
    """Return inverse of A using forward FFT only."""
    # TODO: implement (use fft_iter forward only)
    pass


def _sol_ifft_via_fft(A):
    n = len(A)
    conj = [complex(z).conjugate() for z in A]
    _sol_fft_iter(conj, invert=False)
    return [conj[i].conjugate() / n for i in range(n)]


# ===================================================================
# Exercise 5: Polynomial multiplication via FFT
# ===================================================================
# p and q are integer-coefficient polynomials.
# Return integer-coefficient product. Pad to next power of 2.

def poly_mul(p, q):
    """Return coefficients of p*q via FFT."""
    # TODO: implement
    pass


def _sol_poly_mul(p, q):
    n = 1
    target = len(p) + len(q) - 1
    while n < target:
        n <<= 1
    pa = [complex(x) for x in p] + [0j] * (n - len(p))
    qa = [complex(x) for x in q] + [0j] * (n - len(q))
    _sol_fft_iter(pa)
    _sol_fft_iter(qa)
    ra = [pa[i] * qa[i] for i in range(n)]
    _sol_fft_iter(ra, invert=True)
    return [int(round(z.real)) for z in ra[:target]]


# ===================================================================
# Exercise 6: Big-integer multiplication via polynomial multiplication
# ===================================================================
# Represent integers in base 10 as polynomials (low digit first).
# Multiply via poly_mul, then carry.

def bigint_mul(a, b):
    """Multiply non-negative integers a, b using FFT-based poly mul."""
    # TODO: implement
    pass


def _sol_bigint_mul(a, b):
    if a == 0 or b == 0:
        return 0
    da = [int(c) for c in str(a)[::-1]]
    db = [int(c) for c in str(b)[::-1]]
    coeffs = _sol_poly_mul(da, db)
    # carry
    carry = 0
    digits = []
    for c in coeffs:
        c += carry
        digits.append(c % 10)
        carry = c // 10
    while carry:
        digits.append(carry % 10)
        carry //= 10
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()
    return int("".join(str(d) for d in digits[::-1]))


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

    def check_close(name, got, expected, tol=1e-6):
        nonlocal passed, failed
        if _close(got, expected, tol):
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    expected: {expected}")
            print(f"    got:      {got}")
            failed += 1

    # --- Exercise 1 ---
    print("Exercise 1: Bit-reverse permutation")
    check("len 4", try_or_sol("bit_reverse", [0, 1, 2, 3]), [0, 2, 1, 3])
    check("len 8", try_or_sol("bit_reverse", [0, 1, 2, 3, 4, 5, 6, 7]),
          [0, 4, 2, 6, 1, 5, 3, 7])

    # --- Exercise 2 ---
    print("\nExercise 2: Recursive FFT")
    out = try_or_sol("fft_recursive", [1, 1, 1, 1])
    check_close("constant -> DC only", out, [4 + 0j, 0, 0, 0])
    out = try_or_sol("fft_recursive", [1, 0, 0, 0])
    check_close("impulse -> flat", out, [1, 1, 1, 1])

    # --- Exercise 3 ---
    print("\nExercise 3: Iterative FFT (matches recursive)")
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    rec = try_or_sol("fft_recursive", a)
    it = a[:]
    try_or_sol("fft_iter", it)
    check_close("8-point", it, rec)

    # --- Exercise 4 ---
    print("\nExercise 4: Inverse FFT round-trip")
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    A = a[:]
    try_or_sol("fft_iter", A)
    back = try_or_sol("ifft_via_fft", A)
    check_close("ifft(fft(a)) == a", back, [complex(x) for x in a])

    # --- Exercise 5 ---
    print("\nExercise 5: Polynomial multiplication")
    # (1+2x+3x^2) * (4+5x+6x^2) = 4 +13x +28x^2 +27x^3 +18x^4
    check("small product", try_or_sol("poly_mul", [1, 2, 3], [4, 5, 6]),
          [4, 13, 28, 27, 18])
    check("(1+x)*(1+x)", try_or_sol("poly_mul", [1, 1], [1, 1]), [1, 2, 1])
    # bigger random check via reference
    import random
    random.seed(0)
    p = [random.randint(0, 9) for _ in range(40)]
    q = [random.randint(0, 9) for _ in range(50)]
    naive = [0] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            naive[i + j] += x * y
    check("random 40x50", try_or_sol("poly_mul", p, q), naive)

    # --- Exercise 6 ---
    print("\nExercise 6: Big-integer multiplication via FFT")
    check("123 * 456", try_or_sol("bigint_mul", 123, 456), 56088)
    check("0 * 99", try_or_sol("bigint_mul", 0, 99), 0)
    a = 123456789012345
    b = 987654321098765
    check("15-digit * 15-digit", try_or_sol("bigint_mul", a, b), a * b)

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
