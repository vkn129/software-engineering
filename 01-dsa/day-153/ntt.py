"""
Day 153: Number Theoretic Transform — FFT's modular cousin.

Integer-exact polynomial multiplication using a special prime and a
primitive n-th root of unity in Z_p. Same structure as iterative FFT.
"""

import time


# ---------------------------------------------------------------------------
# 1. NTT-friendly prime
# ---------------------------------------------------------------------------

# 998244353 = 119 * 2^23 + 1
# Primitive root: 3
# Supports NTT sizes up to 2^23.
MOD = 998244353
G = 3


def mod_pow(base, exp, mod):
    """Fast modular exponentiation (see day 150)."""
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


def mod_inverse(a, mod):
    """Fermat's little theorem: a^{p-2} mod p for prime p."""
    return mod_pow(a, mod - 2, mod)


# ---------------------------------------------------------------------------
# 2. NTT — iterative, in-place
# ---------------------------------------------------------------------------

def ntt(a, invert=False, mod=MOD, g=G):
    """
    Number theoretic transform. n must be a power of 2 dividing mod-1.
    Modifies and returns `a`.
    """
    n = len(a)
    if n & (n - 1):
        raise ValueError("Length must be a power of 2")

    # bit-reverse permute
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            a[i], a[j] = a[j], a[i]

    # Butterfly stages
    m = 2
    while m <= n:
        # primitive m-th root of unity:
        # omega = g^((mod-1)/m)  (or its inverse for invert NTT)
        if invert:
            wm = mod_inverse(mod_pow(g, (mod - 1) // m, mod), mod)
        else:
            wm = mod_pow(g, (mod - 1) // m, mod)
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
        n_inv = mod_inverse(n, mod)
        for i in range(n):
            a[i] = (a[i] * n_inv) % mod
    return a


# ---------------------------------------------------------------------------
# 3. Polynomial multiplication via NTT — INTEGER EXACT
# ---------------------------------------------------------------------------

def poly_mul_ntt(p, q, mod=MOD):
    """
    Multiply two non-negative-integer polynomials mod `mod`.
    Returns integer coefficients. Exact when no coefficient of the
    true product exceeds `mod`.
    """
    target = len(p) + len(q) - 1
    n = 1
    while n < target:
        n <<= 1
    pa = list(p) + [0] * (n - len(p))
    qa = list(q) + [0] * (n - len(q))
    ntt(pa, invert=False, mod=mod)
    ntt(qa, invert=False, mod=mod)
    ra = [(pa[i] * qa[i]) % mod for i in range(n)]
    ntt(ra, invert=True, mod=mod)
    return ra[:target]


def poly_mul_naive(p, q):
    out = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return out


# ---------------------------------------------------------------------------
# 4. Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: NTT round-trip")
    print("=" * 60)
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    print(f"Input : {a}")
    A = a[:]
    ntt(A)
    print(f"NTT   : {A[:4]}...")
    ntt(A, invert=True)
    print(f"Inverse: {A}")
    print(f"Round-trip OK: {A == a}")


def demo_poly_mul():
    print("\n" + "=" * 60)
    print("DEMO 2: Polynomial multiplication is INTEGER EXACT")
    print("=" * 60)
    p, q = [1, 2, 3], [4, 5, 6, 7]
    naive = poly_mul_naive(p, q)
    fast = poly_mul_ntt(p, q)
    print(f"naive : {naive}")
    print(f"NTT   : {fast}")
    print(f"Exact match: {naive == fast}")


def demo_perf():
    print("\n" + "=" * 60)
    print("DEMO 3: O(n log n) speedup")
    print("=" * 60)
    import random
    random.seed(7)
    for size in [128, 512, 2048]:
        p = [random.randint(0, 99) for _ in range(size)]
        q = [random.randint(0, 99) for _ in range(size)]

        t = time.perf_counter()
        naive = poly_mul_naive(p, q)
        t_n = time.perf_counter() - t

        t = time.perf_counter()
        ntt_r = poly_mul_ntt(p, q)
        t_ntt = time.perf_counter() - t

        # Match (small coefficients fit under mod)
        match = naive == ntt_r
        print(f"  size={size:5d}  naive={t_n*1000:8.2f}ms  "
              f"NTT={t_ntt*1000:8.2f}ms  exact={match}  speedup={t_n/t_ntt:6.1f}x")


def demo_fft_comparison():
    print("\n" + "=" * 60)
    print("DEMO 4: NTT exactness under MOD")
    print("=" * 60)
    # NTT is exact when no coefficient of the product exceeds MOD.
    # With small coefficients, the integer answer is recovered bit-for-bit.
    p = [123] * 32
    q = [456] * 32

    naive = poly_mul_naive(p, q)
    ntt_r = poly_mul_ntt(p, q)
    print(f"max naive coeff: {max(naive)}  (MOD = {MOD})")
    print(f"NTT matches naive exactly: {naive == ntt_r}")

    # If coefficients overflow MOD, NTT returns the answer MOD MOD.
    p2 = [1234567] * 32
    q2 = [987654] * 32
    naive2 = poly_mul_naive(p2, q2)
    ntt2 = poly_mul_ntt(p2, q2)
    print(f"\nLarge coeffs: max naive = {max(naive2)} (> MOD)")
    print(f"Each NTT coeff equals naive % MOD: "
          f"{all(ntt2[i] == naive2[i] % MOD for i in range(len(naive2)))}")
    print(f"For true integer answer with big coeffs, use multi-prime CRT.")


if __name__ == "__main__":
    demo_basic()
    demo_poly_mul()
    demo_perf()
    demo_fft_comparison()
