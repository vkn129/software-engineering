# Day 14: Mini-Project -- Mathematical Toolkit (Reusable Library of Week 2 Primitives)

## Why This Exists

Over the past week (Days 8-13), you built individual mathematical primitives: modular arithmetic, GCD, combinatorics, primality testing, bit manipulation, and formal correctness proofs. Each one lived in isolation. Real engineering does not work that way.

Cryptographic protocols combine modular exponentiation with primality testing and GCD. Competitive programming problems demand that you chain combinatorial identities with modular inverses in milliseconds. Database hash functions fuse bit manipulation with modular arithmetic. The value of these primitives multiplies when they compose.

This day forces you to do three things that separate working engineers from students:

1. **Organize** -- group related functions into coherent modules with clean interfaces.
2. **Compose** -- solve problems that require reaching across module boundaries (RSA needs primes AND modular exponentiation AND GCD).
3. **Trust** -- because you proved correctness with loop invariants on Day 13, you can compose with confidence instead of hoping.

The result is a `math_toolkit.py` module you can import into any future project. Every function carries its own documentation: what it does, why the math works, its time complexity, and a usage example. This is how professional libraries are built.

## Theory (40 min)

### 1. Why Reusable Libraries Matter

The cost of software is dominated by maintenance, not initial writing. A function you write once and reuse 50 times amortizes its development cost by 50x. But reuse only works if:

- **Interfaces are clear**: the caller should not need to read the implementation.
- **Contracts are explicit**: preconditions, postconditions, and edge cases are documented.
- **Composition is safe**: combining two correct functions should yield a correct result. This is where Day 13's formal proofs pay off -- if `gcd` is provably correct and `mod_inverse` is provably correct, their composition in RSA key generation is correct by construction.

### 2. Module Architecture

We organize into five classes, each grouping functions by mathematical domain:

| Class | Responsibility | Key Functions |
|-------|---------------|---------------|
| `ModularArithmetic` | Operations in Z/mZ | `mod_pow`, `mod_inverse`, `mod_add`, `mod_mul` |
| `NumberTheory` | Integer structure | `gcd`, `extended_gcd`, `lcm`, `euler_totient` |
| `Combinatorics` | Counting | `factorial`, `binomial`, `permutations`, `combinations_list`, `derangements` |
| `PrimalityTesting` | Primality and factoring | `is_prime_trial`, `is_prime_miller_rabin`, `generate_prime`, `prime_sieve` |
| `BitUtils` | Bitwise operations | `count_bits`, `is_power_of_two`, `next_power_of_two`, `bit_subsets` |

### 3. How the Primitives Compose

**RSA Key Generation** (combines 3 modules):
1. `PrimalityTesting.generate_prime()` -- find two large primes p, q
2. `NumberTheory.euler_totient()` -- compute phi(n) = (p-1)(q-1)
3. `NumberTheory.gcd()` -- find e coprime to phi(n)
4. `ModularArithmetic.mod_inverse()` -- compute d = e^(-1) mod phi(n)
5. `ModularArithmetic.mod_pow()` -- encrypt/decrypt via m^e mod n

**Counting Derangements** (combines 2 modules):
1. `Combinatorics.binomial()` -- compute C(n, k)
2. Inclusion-exclusion principle -- alternate sum over binomial coefficients
3. `Combinatorics.factorial()` -- verify via the formula D(n) = n! * sum((-1)^k / k!)

**Modular Combinatorics** (combines 2 modules):
1. `Combinatorics.factorial()` -- compute n!
2. `ModularArithmetic.mod_inverse()` -- compute (k!)^(-1) mod p
3. Chain them: C(n,k) mod p = n! * mod_inverse(k!) * mod_inverse((n-k)!) mod p

### 4. Complexity Summary

| Function | Time | Space | Notes |
|----------|------|-------|-------|
| `mod_pow(base, exp, mod)` | O(log exp) | O(1) | Binary exponentiation |
| `extended_gcd(a, b)` | O(log min(a,b)) | O(log min(a,b)) | Recursion depth |
| `mod_inverse(a, m)` | O(log m) | O(log m) | Via extended GCD |
| `binomial(n, k)` | O(k) | O(1) | Multiplicative formula |
| `miller_rabin(n, rounds)` | O(rounds * log^2 n) | O(1) | Probabilistic |
| `prime_sieve(n)` | O(n log log n) | O(n) | Sieve of Eratosthenes |
| `permutations(arr)` | O(n! * n) | O(n! * n) | Generates all |
| `combinations_list(arr, k)` | O(C(n,k) * k) | O(C(n,k) * k) | Generates all |

## Practice (20 min)

Work through `practice.py`. Each exercise requires combining multiple toolkit primitives to solve a problem that no single primitive handles alone:

1. **RSA Key Generation & Encryption** -- generate primes, compute keys, encrypt and decrypt a message.
2. **Counting Derangements** -- use inclusion-exclusion with binomial coefficients and factorials.
3. **Modular Equation Solver** -- solve ax ≡ b (mod m) using extended GCD and modular inverse.
4. **Bit-Parallel Subset Sum Verification** -- combine bit manipulation with combinatorial generation.
5. **Prime Factorization with Totient** -- factor a number and compute Euler's totient from the factorization.

## Daily Project

Build and test `math_toolkit.py`. Then use it in `practice.py` to solve every exercise. Your goal: every function call in `practice.py` should import from `math_toolkit` -- no reimplementing primitives.

Verify your toolkit by running:
```bash
python math_toolkit.py    # Should print demo output with no errors
python practice.py        # Should print test results for each exercise
```

## Checkpoint Questions

1. Why does `mod_inverse(a, m)` only exist when `gcd(a, m) = 1`? What happens to RSA if you pick `e` that shares a factor with `phi(n)`?
2. Miller-Rabin is probabilistic. How many rounds do you need to reduce the false-positive probability below 2^(-80)? Why is this acceptable for RSA key generation but not for a mathematical proof?
3. The inclusion-exclusion formula for derangements has alternating signs. What would go wrong if you dropped the alternation (used all positive terms)?
4. Why is `mod_pow` O(log exp) instead of O(exp)? Trace the computation of `mod_pow(3, 13, 100)` showing which squarings and multiplications happen.
5. When solving `ax ≡ b (mod m)` and `gcd(a, m) = d > 1`, there are either 0 or d solutions. Explain why geometrically (think of the number line mod m as a circle).
