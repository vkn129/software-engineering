# Day 150: Fast Exponentiation

## Why It Matters

Computing `a^n` by repeated multiplication is O(n). For n = 10^18 that
is hopeless. **Binary exponentiation** drops it to O(log n) — roughly 60
multiplications for 64-bit n.

You need this for:

- **RSA**: encrypt is `m^e mod N`, decrypt is `c^d mod N`. `d` is ~1024 bits.
  Trial multiplication: 2^1024 multiplies. Binary: ~1024 multiplies.
- **Diffie-Hellman**: `g^a mod p` with `a` huge.
- **Modular inverse via Fermat**: `a^(p-2) mod p` (when p is prime).
- **Matrix exponentiation for recurrences**: Fibonacci in O(log n).
- **Primality testing** (Miller-Rabin), pseudorandomness, hashing.

## The Idea — Binary Decomposition

Write n in binary. Example: 13 = 1101 in binary = 8 + 4 + 1.

So `a^13 = a^8 * a^4 * a^1`.

To compute, we keep doubling `a` (a -> a^2 -> a^4 -> a^8 -> ...) and
multiply into the result whenever the next bit of n is 1.

```
result = 1
base = a
while n > 0:
    if n & 1:           # current low bit is 1
        result *= base
    base *= base        # square: a^(2^k) -> a^(2^(k+1))
    n >>= 1
return result
```

Number of squarings: `floor(log2 n) + 1`. Multiplies into result: at most
the same. Total: **O(log n)** multiplications.

## Modular Power — Crypto's Workhorse

If you do `a^n mod m` by reducing at each step, intermediate values stay
in `[0, m)`. For m a 2048-bit RSA modulus, multiplying two 2048-bit
numbers costs O((log m)^2) bit operations (schoolbook). Total:

```
(log n) multiplies * (log m)^2 bit ops each  =  O(log n * (log m)^2)
```

For RSA-2048 with full 2048-bit `d`, that's roughly 2048 * 2048^2 ≈ 10^10
bit ops — milliseconds on modern CPUs.

Python's built-in `pow(a, n, m)` uses essentially this algorithm
(with optimizations). We will write our own to feel the bones.

## Recursive vs Iterative

Recursive form is elegant:

```
power(a, n) = 1                          if n == 0
            = power(a, n/2)^2            if n even
            = a * power(a, n-1)          if n odd
```

But recursion costs stack frames. Iterative is the production form.

## Matrix Exponentiation

Same trick generalizes. To find the n-th Fibonacci, the recurrence is

```
| F(n+1) |   | 1 1 |^n   | 1 |
|        | = |     |   * |   |
| F(n)   |   | 1 0 |     | 0 |
```

So `F(n) = O(log n)` if we exponentiate the 2x2 matrix in O(log n) steps.
The base operation is now 2x2 matrix multiply (8 multiplies + 4 adds per
step). Total work for F(10^18): ~60 matrix multiplies. Sub-millisecond.

## Failure Modes

1. **Overflow without modulus**: `a^n` blows up exponentially. In Python
   it just gets slow (big ints). In C it overflows silently — must mod.
2. **Negative exponent without inverse**: `a^(-1) mod m` only exists if
   gcd(a, m) = 1. Forget that and you get garbage.
3. **Timing side channels**: branching on the bits of `n` leaks `n` via
   timing. Cryptographic implementations use **constant-time ladders**
   (Montgomery ladder).
4. **Squaring overflow before mod**: in fixed-width languages, you must
   mod after every operation. `(a * a) % m` may overflow if `m` is near
   the type's max.

## Complexity Summary

| Method | Time | Space |
|--------|------|-------|
| Repeated multiplication | O(n) | O(1) |
| Recursive binary | O(log n) | O(log n) stack |
| Iterative binary | O(log n) | O(1) |
| Constant-time ladder | O(log n) | O(1) — leak-free |

## Real-World Usage

| System | Use |
|--------|-----|
| RSA/ElGamal | `m^e mod N` |
| Diffie-Hellman | `g^a mod p` |
| Miller-Rabin | `a^d mod n` |
| Fermat inverse | `a^(p-2) mod p` |
| Matrix recurrences | Fibonacci, linear DP in O(log n) |
| Cryptocurrency signatures | scalar mult on elliptic curves (additive version) |

## Checkpoint Questions

1. Why does `a^13` need 5 multiplications, not 13?
2. Show why `a * a` could overflow before `% m` even when `a < m`.
3. The Montgomery ladder doesn't branch on bits of `n`. Why is that
   important for security?
4. For Fibonacci via matrix exponentiation, how many multiplies does
   F(10^9) need on a 2x2 matrix?
5. When can you use Fermat's little theorem to compute a modular
   inverse, and when must you fall back to extended Euclidean?
6. What's the time cost of `pow(a, n, m)` for an RSA-2048 operation,
   and where does it dominate (multiply or reduce)?
