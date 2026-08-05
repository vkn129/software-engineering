# Day 149: Sieve of Eratosthenes

## Why the Sieve Matters

Generating primes is the bedrock of number theory: RSA, ECC, NTT, hash
functions that need primes, primality testing, factoring. If you can list
primes fast, you can unlock cryptography, FFT-over-finite-fields, and a
chunk of competitive programming.

**Trial division** asks each candidate "are you prime?" one at a time —
O(n sqrt n) to find all primes up to n. Slow.

**The sieve** flips the question: it asks each prime "which numbers are
your multiples?" and crosses them off. Each composite is killed by its
smallest prime factor at most. Total cost: **O(n log log n)** — essentially
linear.

## The Algorithm

```
mark[0] = mark[1] = false
for i = 2 .. sqrt(n):
    if mark[i]:
        for j = i*i, i*i+i, i*i+2i, ..., n:
            mark[j] = false
```

**Why start at i*i?** Every composite < i*i with smallest prime factor i
must have a smaller factor < i, and that factor already marked it.

**Why iterate only to sqrt(n)?** Any composite n has at least one factor
<= sqrt(n). After sqrt(n) all unmarked numbers are prime.

## Why O(n log log n)

The cost is `sum over primes p <= n of (n/p)`. By Mertens' theorem,
`sum 1/p for p <= n  ≈  log log n + M`. So total work is `n log log n`.

For n = 10^8, log log n ≈ 3, so ~3 * 10^8 operations. Doable in seconds.

## Segmented Sieve: Why Segmenting Matters

The basic sieve needs a bit-array of size n. To enumerate primes up to
10^12 you would need 125 GB. The machine cannot hold it.

**The fix**: process the range `[lo, hi)` in chunks of size sqrt(n) or
a fixed L1-cache-sized block (~64 KB). For each chunk:

1. Have all primes up to sqrt(hi) precomputed (basic sieve).
2. For each such prime p, compute the smallest multiple of p inside the
   chunk: `start = ceil(lo / p) * p`. Mark from `start` stepping by p.
3. Numbers in the chunk still unmarked are prime.

**Memory**: only sqrt(n) for the small primes + chunk_size for the bitset.
For n = 10^12, sqrt(n) = 10^6 — fits in 125 KB. Each chunk fits in L1.

**Cache effect**: the basic sieve writes to addresses spread over n bytes —
cache-unfriendly for large n. A 64 KB chunk fits in L1, so every write
hits hot cache. Real-world speedup: 2-5x even before memory becomes the
hard constraint.

## Failure Modes

1. **Overflow on `i*i`**: in C, `i*i` wraps if i > sqrt(INT_MAX). Use
   64-bit or check `i > n // i`.
2. **Wrong start in segmented sieve**: forgetting to use `max(p*p, start)`
   means re-marking composites already handled by smaller primes — correct
   but wasteful.
3. **Off-by-one on bit-packing**: dropping even numbers halves the array.
   Easy to slip on the index translation.
4. **Memory blowup**: lists of booleans in Python = 28 bytes each. Use
   `bytearray` or `array.array('b', ...)` for 1 byte each.

## Variants

- **Sieve of Atkin**: O(n) but with a huge constant and complex logic.
  Faster in theory, slower in practice for n < 10^11.
- **Linear sieve**: marks each composite exactly once using its smallest
  prime factor. True O(n) but the constant is similar to Eratosthenes.
  Gives you the smallest-prime-factor table for free — handy for fast
  factoring afterwards.
- **Wheel factorization**: skip multiples of 2, 3, 5, 7 (the wheel). About
  4x faster than naive Eratosthenes.

## Complexity Summary

| Variant | Time | Space | Use when |
|---------|------|-------|----------|
| Basic Eratosthenes | O(n log log n) | O(n) | n <= 10^8 |
| Segmented Eratosthenes | O(n log log n) | O(sqrt n) | n up to 10^14 |
| Linear sieve | O(n) | O(n) | need smallest prime factor |
| Atkin | O(n) | O(n) | n very large, performance critical |

## Real-World Usage

- **Project Euler** problems frequently need primes up to 10^7-10^9.
- **Cryptography**: RSA key gen picks 1024-bit primes — too big to sieve;
  use Miller-Rabin probabilistic test. But sieves seed those tests.
- **Hash table sizing**: pick a prime close to required capacity.
- **FFT/NTT**: certain transforms need a prime p with specific structure
  (e.g., p = k * 2^n + 1).

## Checkpoint Questions

1. Why start the inner loop at `i*i` instead of `2*i`?
2. The segmented sieve runs at the same asymptotic complexity. So why is
   it faster in practice for large n?
3. How would you modify the sieve to also output the smallest prime factor
   of every composite?
4. For n = 10^12, why is the basic sieve impractical even on a 128 GB
   server?
5. Wheel factorization skips multiples of 2, 3, 5. What is the wheel size?
6. Why does Python's list-of-bools sieve use ~28x more memory than a
   `bytearray` sieve?
