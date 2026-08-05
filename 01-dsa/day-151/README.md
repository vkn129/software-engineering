# Day 151: RSA Fundamentals (Toy Implementation)

> WARNING — LEARNING ONLY. This implementation is for understanding the
> math, not for protecting anything real. Small primes, no padding (no
> OAEP), no constant-time operations, no key-blinding. A real attacker
> would break it in seconds. Use a vetted library for production crypto.

## The Big Idea

RSA's security rests on a single asymmetry:

> Multiplying two big primes is *easy*. Factoring their product is *hard*.

If `p` and `q` are 1024-bit primes, computing `N = p * q` takes microseconds.
Recovering `p, q` from `N` is, as far as anyone knows, exponential in
the size of `N`. The best known classical algorithm, the General Number
Field Sieve, runs in roughly `exp(c * (log N)^(1/3))` — sub-exponential
but still infeasible for `N` ~ 2048 bits.

Quantum computers running Shor's algorithm break this in polynomial time.
That's why we're moving to post-quantum crypto.

## The Math (Just Enough)

### Setup

1. Pick two large primes `p, q` (real RSA: 1024+ bits each).
2. Compute `N = p * q` — the **modulus**.
3. Compute `phi = (p-1)(q-1)` — **Euler's totient** of N.
4. Pick `e` coprime with `phi`. Common: `e = 65537` (small prime, fast).
5. Compute `d = e^(-1) mod phi` — **private exponent**.

**Public key**: `(N, e)`. Anyone can have it.
**Private key**: `d`. Keep secret.

### Encrypt / Decrypt

For a message `m` with `0 <= m < N`:

- Encrypt: `c = m^e mod N`
- Decrypt: `m = c^d mod N`

### Why It Works (Euler / Fermat)

Euler's theorem: if `gcd(m, N) = 1`, then `m^phi(N) = 1 mod N`.
We chose `d` so `e*d = 1 mod phi`. Thus `e*d = 1 + k*phi` for some k.

```
c^d = m^(e*d) = m^(1 + k*phi) = m * (m^phi)^k = m * 1^k = m   (mod N)
```

(The `gcd(m, N) != 1` case still works for RSA — extra cases via CRT.)

### Why Factoring N Breaks Everything

If you know `p` and `q`, you know `phi = (p-1)(q-1)`, then compute
`d = e^(-1) mod phi` by extended Euclidean. Public key + factoring = full
private key.

## Why Toy Keys Are Insecure

This day uses primes in the range ~10^6 to 10^9 to keep things printable.
A real attacker breaks toy RSA via:

1. **Trial division**: try every prime up to sqrt(N). For 60-bit N, that's
   2^30 ≈ 10^9 trials — a few seconds.
2. **Pollard's rho**: O(N^(1/4)) — way faster.
3. **Smooth primes**: if `p-1` is "smooth" (product of small primes),
   Pollard's p-1 algorithm factors quickly. Real RSA primes are chosen
   to be **safe primes** to defeat this.

Plus, our toy version has none of the production protections:

| Attack | Why Toy Fails | Production Fix |
|--------|---------------|----------------|
| Factoring | 32-bit N | 2048+ bit N |
| Chosen-plaintext (Bleichenbacher) | No padding | OAEP padding |
| Timing side channel | Branchy `mod_pow` | Constant-time ladder |
| Power analysis | Direct exponentiation | Blinding: `m' = m * r^e`, decrypt, divide by r |
| Small `e` + small `m` | `m^3 < N` => no modular reduction => cube root attack | Pad before encrypt |
| Common modulus | Reusing N across users | Unique N per key |

## Generating the Keys

1. Random odd `n` of right size, test primality (Miller-Rabin in
   production). For our toy: use the sieve.
2. Pick `e` (usually 65537). Verify `gcd(e, phi) = 1`.
3. Compute `d = e^(-1) mod phi` via extended Euclidean.

### Extended Euclidean Algorithm

For `a * x + b * y = gcd(a, b)`. We need `e * d + phi * y = 1`. The
`d` from this is the modular inverse.

```
gcd(a, 0) = a,   coefficients (1, 0)
gcd(a, b) = gcd(b, a mod b)
            recurse: (g, x', y') = ext_gcd(b, a mod b)
            return (g, y', x' - (a // b) * y')
```

## Signature (Sketch)

RSA signing reverses roles: sign with `d`, verify with `e`. In practice
you sign the *hash* of the message, not the message itself, and use a
padding scheme (PSS).

## Failure Modes

1. **Small primes**: trivially factorable.
2. **Reusing primes across keys**: if `gcd(N1, N2) > 1`, both moduli leak.
3. **Encrypting `m = 0` or `m = 1`**: ciphertext is also 0 or 1.
4. **`m >= N`**: message wraps mod N — irrecoverable.
5. **Bad RNG**: predictable primes = breakable keys (Debian OpenSSL 2008).
6. **Mishandling padding errors**: revealing padding-validity to the
   attacker enables Bleichenbacher's attack.

## Real-World Usage

| System | Use |
|--------|-----|
| TLS (older versions) | RSA key exchange |
| SSH | Server identity, user authentication |
| GPG/PGP | Email signing/encryption |
| Certificate Authorities | Signing X.509 certs |
| JWT | RS256 token signing |
| Blockchain (some) | Identity, signatures (though ECC more common now) |

## Checkpoint Questions

1. Why must `e` be coprime to `phi(N)`?
2. Show concretely that with `e = 3` and `m^3 < N`, an attacker recovers
   `m` without the private key.
3. Why does padding (OAEP) defeat the cube-root attack?
4. If an attacker learns `phi(N)`, can they recover `d` without
   factoring `N`?
5. Pollard's rho factors in O(N^(1/4)). For a 2048-bit modulus, why is
   that still infeasible?
6. Why is signing the hash of the message, not the message itself,
   essential for security?
