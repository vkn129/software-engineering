"""
Day 151: RSA — Toy implementation, LEARNING ONLY.

WARNING: Real RSA uses 2048+ bit primes, OAEP padding, constant-time
modular exponentiation, and blinding. This implementation has none of
those. Do not use for real security.

What you will see clearly:
- Key generation flow (pick primes, derive d via extended Euclidean)
- Why m^e then c^d returns m (Euler's theorem in action)
- Why factoring N breaks everything
"""

import random
import time
import math


# ---------------------------------------------------------------------------
# 1. Toy primality + prime generator (sieve-based — small primes)
# ---------------------------------------------------------------------------

def is_prime(n):
    """Trial division. Fine for the small primes we use here."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def random_prime(lo, hi, rng=None):
    """Pick a random prime in [lo, hi]. For real RSA, use Miller-Rabin."""
    rng = rng or random
    while True:
        candidate = rng.randint(lo, hi) | 1  # force odd
        if is_prime(candidate):
            return candidate


# ---------------------------------------------------------------------------
# 2. Extended Euclidean — modular inverse
# ---------------------------------------------------------------------------

def ext_gcd(a, b):
    """Return (g, x, y) where a*x + b*y = g = gcd(a, b)."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(e, phi):
    """Return d with e*d = 1 (mod phi). Raises if no inverse exists."""
    g, x, _ = ext_gcd(e, phi)
    if g != 1:
        raise ValueError(f"No inverse: gcd({e},{phi})={g}")
    return x % phi


# ---------------------------------------------------------------------------
# 3. Modular power (own implementation — see day-150)
# ---------------------------------------------------------------------------

def mod_pow(base, exp, mod):
    result = 1
    base %= mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


# ---------------------------------------------------------------------------
# 4. Key generation
# ---------------------------------------------------------------------------

def generate_keys(prime_lo=10**6, prime_hi=10**7, e=65537, rng=None):
    """
    Return (public_key, private_key) = ((N, e), (N, d)).
    Primes are toy-sized — picked so demos run fast and N is printable.
    """
    rng = rng or random.Random(42)
    p = random_prime(prime_lo, prime_hi, rng)
    q = random_prime(prime_lo, prime_hi, rng)
    while q == p:
        q = random_prime(prime_lo, prime_hi, rng)

    N = p * q
    phi = (p - 1) * (q - 1)
    if math.gcd(e, phi) != 1:
        # rare with e=65537; pick another e
        e = 3
        while math.gcd(e, phi) != 1:
            e += 2
    d = mod_inverse(e, phi)
    return (N, e), (N, d), (p, q)


# ---------------------------------------------------------------------------
# 5. Encrypt / Decrypt (no padding! integer-domain only)
# ---------------------------------------------------------------------------

def encrypt(message, public_key):
    """Encrypt integer message m < N as c = m^e mod N."""
    N, e = public_key
    if message >= N:
        raise ValueError("Message too large for key")
    return mod_pow(message, e, N)


def decrypt(ciphertext, private_key):
    """Decrypt c as m = c^d mod N."""
    N, d = private_key
    return mod_pow(ciphertext, d, N)


# ---------------------------------------------------------------------------
# 6. Attacker simulation: factor N to break the key
# ---------------------------------------------------------------------------

def factor_brute(N):
    """Find p, q with p*q = N. Trial division — only works for tiny N."""
    for p in range(2, int(math.isqrt(N)) + 1):
        if N % p == 0:
            return p, N // p
    return None


def recover_private_key(public_key):
    """
    From (N, e), factor N, derive phi, recover d.
    Demonstrates why factoring breaks RSA.
    """
    N, e = public_key
    p, q = factor_brute(N)
    phi = (p - 1) * (q - 1)
    d = mod_inverse(e, phi)
    return N, d


# ---------------------------------------------------------------------------
# 7. Demos
# ---------------------------------------------------------------------------

def demo_keygen():
    print("=" * 60)
    print("DEMO 1: Key generation")
    print("=" * 60)
    pub, priv, (p, q) = generate_keys()
    N, e = pub
    _, d = priv
    print(f"  p = {p}")
    print(f"  q = {q}")
    print(f"  N = p*q = {N}")
    print(f"  phi = {(p-1)*(q-1)}")
    print(f"  e = {e}")
    print(f"  d = {d}")
    return pub, priv


def demo_encrypt(pub, priv):
    print("\n" + "=" * 60)
    print("DEMO 2: Encrypt and decrypt an integer")
    print("=" * 60)
    m = 1234567
    c = encrypt(m, pub)
    m2 = decrypt(c, priv)
    print(f"  message    = {m}")
    print(f"  ciphertext = {c}")
    print(f"  decrypted  = {m2}")
    print(f"  match? {m == m2}")


def demo_break():
    print("\n" + "=" * 60)
    print("DEMO 3: Attacker breaks toy RSA by factoring N")
    print("=" * 60)
    # smaller primes so brute factoring is fast for the demo
    pub, priv, (p, q) = generate_keys(prime_lo=1000, prime_hi=10000)
    N, e = pub
    _, d_true = priv
    print(f"  Public:    (N={N}, e={e})")
    print(f"  Real d:    {d_true}")

    t = time.perf_counter()
    _, d_attacker = recover_private_key(pub)
    dt = time.perf_counter() - t

    print(f"  Recovered: {d_attacker}  in {dt*1000:.2f} ms")
    assert d_attacker == d_true
    print(f"  Match!  Why this is broken: N had only {N.bit_length()} bits.")
    print(f"  Real RSA: N is 2048-4096 bits. Factoring is infeasible.")


def demo_text():
    print("\n" + "=" * 60)
    print("DEMO 4: Encrypt a short text (byte by byte — toy only)")
    print("=" * 60)
    pub, priv, _ = generate_keys()
    msg = "Hi"  # 2 bytes
    print(f"  message: {msg!r}")
    cipher = [encrypt(b, pub) for b in msg.encode()]
    print(f"  cipher:  {cipher}")
    plain = bytes(decrypt(c, priv) for c in cipher).decode()
    print(f"  decoded: {plain!r}")
    print(f"  (Real RSA encrypts a whole message at once, with padding.)")


if __name__ == "__main__":
    print("!! WARNING: TOY RSA — LEARNING ONLY. NEVER USE FOR REAL SECURITY. !!")
    pub, priv = demo_keygen()
    demo_encrypt(pub, priv)
    demo_break()
    demo_text()
