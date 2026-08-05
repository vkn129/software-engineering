# Day 153: Number Theoretic Transform (NTT)

## Why NTT Exists

The FFT is brilliant but uses floating-point complex numbers. For
applications that need **exact integer arithmetic** — cryptography,
competitive programming, big-integer libraries — floating-point round-off
is unacceptable.

NTT replaces the n-th roots of unity in `C` with n-th roots of unity in
the finite field `Z_p` (integers mod a special prime `p`). The structure
is identical to the FFT — but every operation is integer-exact.

**Same algorithm. Same O(n log n). Zero round-off.**

## What We Need: a Special Prime

The FFT uses `w = e^(-2*pi*i/n)`, a primitive n-th root of unity in `C`.

NTT needs the analog in `Z_p`: a number `g` with `g^n = 1 (mod p)` but
`g^k != 1 (mod p)` for any `0 < k < n`. Such a `g` is a **primitive
n-th root of unity** mod p.

For an n-th root to exist, **n must divide p-1**. We need n to be a
power of 2 (often very large, like 2^20). So we choose `p` of the form

```
p = c * 2^k + 1     for some odd c and large k
```

These are called **NTT-friendly primes**. Famous choices:

| Prime | Factorization | Max n |
|-------|---------------|-------|
| 998244353 | 119 * 2^23 + 1 | 2^23 = 8388608 |
| 754974721 | 45 * 2^24 + 1 | 2^24 |
| 167772161 | 5 * 2^25 + 1 | 2^25 |

`998244353` is the competitive-programming standard.

## Finding a Generator

A **primitive root g of p** is a number whose powers `g, g^2, g^3, ...`
hit every nonzero residue mod p. Once you have one:

```
omega = g^((p-1)/n) mod p
```

is a primitive n-th root of unity mod p. For `p = 998244353`, a known
primitive root is `g = 3`.

## The Algorithm

Identical to the iterative FFT. Replace every complex multiply with a
modular multiply.

```
for m = 2; m <= n; m *= 2:
    w_m = omega^(n/m)            # primitive m-th root
    for k = 0; k < n; k += m:
        w = 1
        for j = 0; j < m/2; j++:
            t = (w * a[k + j + m/2]) % p
            u = a[k + j]
            a[k + j]         = (u + t) % p
            a[k + j + m/2]   = (u - t) % p
            w = (w * w_m) % p
```

Inverse NTT uses `omega^{-1} mod p`, then multiplies every output by
`n^{-1} mod p` at the end.

## Modular Inverse Aside

We need `n^{-1} mod p` and `omega^{-1} mod p`. Use Fermat:
`a^{-1} = a^{p-2} mod p` (since p is prime). See day 150.

## Polynomial Multiplication via NTT

Exactly like FFT-based poly mul, but in `Z_p`:

1. Pad p, q to power-of-two length `n`.
2. Forward NTT both.
3. Pointwise multiply mod p.
4. Inverse NTT.

**Result is exact** (no rounding). If coefficient magnitude of the
product can fit in `p`, you have the true integer answer.

For very large coefficients you can split into smaller pieces, run
multiple NTTs with different primes, and recombine via Chinese Remainder
Theorem (CRT). This is what GMP does for ultra-large integer multiplies.

## Why It's Used in Crypto

Modern lattice-based cryptography (Kyber, Dilithium — NIST PQC winners)
performs polynomial multiplication mod a small prime. NTT makes those
multiplications fast:

- Without NTT: O(n^2) — too slow for real-time TLS handshakes.
- With NTT: O(n log n) — fast enough that lattice crypto is practical.

The Kyber spec literally specifies NTT operations bit-for-bit.

## Failure Modes

1. **Wrong prime**: if `n` doesn't divide `p - 1`, no primitive n-th root
   exists. Algorithm produces garbage.
2. **Wrong generator**: not all `g` are primitive roots. Test
   `g^((p-1)/q) != 1 mod p` for every prime factor `q` of `p-1`.
3. **Coefficient overflow**: if the true product of polynomial coefficients
   exceeds `p`, you wrap. Multi-prime CRT fixes this.
4. **Forgetting modular inverse**: dividing by `n` in inverse NTT must
   use `n^{-1} mod p`, not float division.
5. **Negative intermediates**: subtractions in butterfly can go negative.
   Add `p` and mod, or rely on Python's well-behaved modulo (Python's
   `%` returns non-negative for positive divisor).

## Complexity Summary

| Operation | Naive | FFT | NTT |
|-----------|-------|-----|-----|
| Polynomial multiply (small coeffs) | O(n²) | O(n log n) | O(n log n) |
| Exact integer convolution | O(n²) | rounding error | exact |
| Modular polynomial multiply | O(n²) | needs CRT | native |

## Real-World Usage

| System | Why NTT |
|--------|---------|
| Kyber / Dilithium (NIST PQC) | Fast polynomial mul mod q |
| GMP (big-int) | Multi-prime FFT for huge multiplies |
| Falcon (PQC signatures) | NTT over ring `Z_q[x]/(x^n+1)` |
| Competitive programming | Exact convolution under 998244353 |
| Homomorphic encryption (BFV, CKKS) | Fast operations on ciphertext polynomials |

## Checkpoint Questions

1. Why must `n` divide `p - 1` for an NTT to work?
2. Show why `998244353 = 119 * 2^23 + 1` lets NTTs of size up to `2^23`.
3. To run NTT for `n = 2^20`, what is the smallest `omega` (in terms of
   the generator `g = 3` and `p = 998244353`)?
4. NTT is exact, FFT is not. When does the *FFT* still beat NTT in
   practice?
5. If your polynomial product has coefficients up to `10^18` but `p ~ 10^9`,
   how do you stay correct? (Hint: CRT.)
6. Lattice crypto picks primes specifically to be NTT-friendly. Why is
   speed of NTT a security-relevant property of the spec?
