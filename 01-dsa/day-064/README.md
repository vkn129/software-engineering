# Day 64: Hash Functions Deep Dive — Why Distribution Is Everything

## Why This Exists

Every hash table, bloom filter, cache, and load balancer depends on the same primitive: a function that maps arbitrary keys to bounded integers. If that function is bad, your O(1) hash table degrades to O(n). If it's good, you get uniform distribution across buckets and near-perfect performance.

But "good" is context-dependent. A hash function for a hash table needs to be **fast** and **well-distributed**. A hash function for password storage needs to be **slow** and **irreversible**. A hash function for detecting file changes needs to be **collision-resistant**. Understanding these trade-offs is what separates using hash tables from understanding them.

## Theory (40 min)

### What Makes a Hash Function

A hash function h: U -> {0, 1, ..., m-1} maps a universe of keys to a fixed range. Three essential properties:

1. **Deterministic**: Same input always produces same output
2. **Uniform distribution**: Keys spread evenly across the output range
3. **Avalanche effect**: Flipping 1 bit in the input changes ~50% of output bits

### The Birthday Paradox — Why Collisions Are Inevitable

With m buckets, how many items before a collision? Intuitively you'd guess m/2, but the answer is much smaller: ~sqrt(m). This is the birthday paradox.

For a 365-day year, you only need ~23 people for a 50% chance of a shared birthday. For a hash table with 1 million buckets, expect a collision after only ~1,177 insertions. This is why collision handling isn't optional — it's fundamental.

**Math**: P(no collision after k inserts into m buckets) = product((m-i)/m for i in 0..k-1). This drops below 0.5 when k ~ sqrt(2m * ln(2)) ~ 1.177 * sqrt(m).

### Division Method vs Multiplication Method

**Division method**: h(k) = k mod m

- Simple, fast
- Sensitive to m: if m = 2^p, only the lowest p bits matter
- Best when m is a prime not close to a power of 2

**Multiplication method**: h(k) = floor(m * (k * A mod 1)) where 0 < A < 1

- Knuth suggests A = (sqrt(5) - 1) / 2 ~ 0.6180339887 (the golden ratio)
- Works well for any m, even powers of 2
- Better at extracting information from all bits of the key

### Hash Function Families

**DJB2** (Daniel J. Bernstein):
```
hash = 5381
for each byte c in key:
    hash = hash * 33 + c
```
Why 5381 and 33? Empirically chosen — 33 = 2^5 + 1 so multiplication is a shift-and-add. 5381 is a prime that produces good distribution. Simple, fast, but not great for all workloads.

**FNV-1a** (Fowler-Noll-Vo):
```
hash = 2166136261  (FNV offset basis)
for each byte c in key:
    hash = hash XOR c
    hash = hash * 16777619  (FNV prime)
```
XOR-then-multiply (FNV-1a) gives better avalanche than multiply-then-XOR (FNV-1). The magic constants are carefully chosen primes that produce good dispersion.

**Multiplicative hash** (Knuth):
```
hash = (key * 2654435761) >> shift
```
The constant 2654435761 is close to 2^32 / phi (golden ratio). Bit shifting extracts the most-mixed high bits.

### Cryptographic vs Non-Cryptographic Hashes

| Property | Non-Cryptographic (DJB2, FNV, MurmurHash) | Cryptographic (SHA-256, BLAKE3) |
|----------|--------------------------------------------|---------------------------------|
| Speed | Very fast (GB/s) | Slower (100s MB/s) |
| Collision resistance | Statistical, not guaranteed | Computationally infeasible |
| Pre-image resistance | None (can reverse) | Cannot find input from output |
| Use case | Hash tables, checksums, caches | Passwords, signatures, integrity |

**Rule of thumb**: If an adversary can choose the inputs, you need either cryptographic hashing or universal hashing. Non-cryptographic hashes are for trusted inputs where you just need distribution.

### Universal Hashing

A hash family is **universal** if for any two distinct keys x != y, the probability of collision P(h(x) = h(y)) <= 1/m when h is chosen randomly from the family.

Carter-Wegman family: h(x) = ((a*x + b) mod p) mod m, where p is prime > universe size and a, b are random with a != 0.

This gives provable bounds on collision probability regardless of the input distribution — the randomness is in the choice of hash function, not in the keys.

## Practice (20 min)

See `practice.py` — 5 exercises from polynomial rolling hash to universal hashing.

## Daily Project

`hash_functions.py` implements DJB2, FNV-1a, and multiplicative hash with distribution quality testing (chi-squared), avalanche analysis, and visual comparison.

## Checkpoint Questions

1. Why does the birthday paradox mean collisions happen after only ~sqrt(m) insertions into m buckets?
2. Why should you avoid using a power of 2 as the modulus in the division method?
3. What is the avalanche effect and why does it matter for hash quality?
4. When would you choose a cryptographic hash over a non-cryptographic one?
5. How does universal hashing defend against adversarial inputs even though each individual hash function is simple?
6. Why does FNV-1a XOR before multiplying instead of after?
