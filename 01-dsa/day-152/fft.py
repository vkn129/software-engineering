"""
Day 152: FFT — Cooley-Tukey radix-2 from scratch.

Recursive and iterative forms. Polynomial multiplication in O(n log n).
"""

import cmath
import math
import time


# ---------------------------------------------------------------------------
# 1. Recursive FFT (clear, but slow due to Python recursion + copies)
# ---------------------------------------------------------------------------

def fft_recursive(a):
    """
    Discrete Fourier Transform via radix-2 Cooley-Tukey. n must be a power of 2.
    Returns a new list of complex values.
    """
    n = len(a)
    if n == 1:
        return [a[0]]
    if n & (n - 1):
        raise ValueError("Length must be a power of 2")

    even = fft_recursive(a[0::2])
    odd = fft_recursive(a[1::2])

    out = [0] * n
    for k in range(n // 2):
        # twiddle factor w^k where w = e^(-2*pi*i/n)
        t = cmath.exp(-2j * math.pi * k / n) * odd[k]
        out[k] = even[k] + t
        out[k + n // 2] = even[k] - t
    return out


# ---------------------------------------------------------------------------
# 2. Iterative in-place FFT — production form
# ---------------------------------------------------------------------------

def bit_reverse_permute(a):
    """In-place bit-reversal permutation."""
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


def fft(a, invert=False):
    """
    In-place iterative FFT. Modifies and returns `a`.
    `invert=True` performs the inverse FFT (divides by n at the end).
    """
    n = len(a)
    if n & (n - 1):
        raise ValueError("Length must be a power of 2")
    bit_reverse_permute(a)

    m = 2
    while m <= n:
        # primitive m-th root of unity
        ang = (2 * math.pi / m) * (1 if invert else -1)
        wm = cmath.exp(1j * ang)
        half = m // 2
        for k in range(0, n, m):
            w = 1 + 0j
            for j in range(half):
                u = a[k + j]
                t = w * a[k + j + half]
                a[k + j] = u + t
                a[k + j + half] = u - t
                w *= wm
        m <<= 1

    if invert:
        for i in range(n):
            a[i] /= n
    return a


# ---------------------------------------------------------------------------
# 3. Polynomial multiplication via FFT
# ---------------------------------------------------------------------------

def poly_mul_fft(p, q):
    """
    Multiply two polynomials (coefficient vectors) using FFT.
    Returns coefficients of product. Real-valued; rounds to int if inputs are int.
    """
    n = 1
    target = len(p) + len(q) - 1
    while n < target:
        n <<= 1

    pa = [complex(x) for x in p] + [0j] * (n - len(p))
    qa = [complex(x) for x in q] + [0j] * (n - len(q))

    fft(pa)
    fft(qa)
    ra = [pa[i] * qa[i] for i in range(n)]
    fft(ra, invert=True)

    # If inputs were ints, round to int.
    if all(isinstance(x, int) for x in p) and all(isinstance(x, int) for x in q):
        return [int(round(r.real)) for r in ra[:target]]
    return [r.real for r in ra[:target]]


def poly_mul_naive(p, q):
    """O(n^2) reference."""
    out = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return out


# ---------------------------------------------------------------------------
# 4. Demos
# ---------------------------------------------------------------------------

def demo_fft_basic():
    print("=" * 60)
    print("DEMO 1: FFT of a simple signal")
    print("=" * 60)
    # [1, 1, 1, 1] -> only DC component (k=0) nonzero, equals n
    a = [1, 1, 1, 1]
    print(f"Input: {a}")
    A = fft_recursive(a)
    print(f"FFT: {[round(z.real,3)+round(z.imag,3)*1j for z in A]}")
    print(f"(Expected: [4, 0, 0, 0] — pure DC)")


def demo_round_trip():
    print("\n" + "=" * 60)
    print("DEMO 2: FFT round-trip (forward then inverse)")
    print("=" * 60)
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    print(f"Original: {a}")
    A = a[:]
    fft(A)
    fft(A, invert=True)
    print(f"Restored: {[round(z.real, 6) for z in A]}")


def demo_recursive_vs_iter():
    print("\n" + "=" * 60)
    print("DEMO 3: Recursive vs iterative agree")
    print("=" * 60)
    import random
    random.seed(0)
    a = [random.uniform(-1, 1) for _ in range(16)]
    A_rec = fft_recursive(a)
    A_iter = a[:]
    fft(A_iter)
    max_err = max(abs(A_rec[i] - A_iter[i]) for i in range(16))
    print(f"Max diff over 16 outputs: {max_err:.2e}")


def demo_poly_mul():
    print("\n" + "=" * 60)
    print("DEMO 4: Polynomial multiplication")
    print("=" * 60)
    # (1 + 2x + 3x^2) * (4 + 5x + 6x^2 + 7x^3)
    p, q = [1, 2, 3], [4, 5, 6, 7]
    naive = poly_mul_naive(p, q)
    fft_result = poly_mul_fft(p, q)
    print(f"p = {p}, q = {q}")
    print(f"naive: {naive}")
    print(f"FFT:   {fft_result}")
    print(f"match? {naive == fft_result}")


def demo_perf():
    print("\n" + "=" * 60)
    print("DEMO 5: O(n log n) vs O(n^2) for polynomial multiply")
    print("=" * 60)
    import random
    random.seed(7)
    for size in [128, 512, 2048]:
        p = [random.randint(0, 9) for _ in range(size)]
        q = [random.randint(0, 9) for _ in range(size)]

        t = time.perf_counter()
        poly_mul_naive(p, q)
        t_naive = time.perf_counter() - t

        t = time.perf_counter()
        poly_mul_fft(p, q)
        t_fft = time.perf_counter() - t

        print(f"  size={size:5d}  naive={t_naive*1000:8.2f}ms  "
              f"fft={t_fft*1000:8.2f}ms  speedup={t_naive/t_fft:6.1f}x")


if __name__ == "__main__":
    demo_fft_basic()
    demo_round_trip()
    demo_recursive_vs_iter()
    demo_poly_mul()
    demo_perf()
