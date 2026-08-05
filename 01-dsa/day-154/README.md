# Day 154: Discrete Logarithm

## Why It Matters

Day 151 built RSA on one asymmetry: multiplying primes is easy, factoring their
product is hard. Public-key cryptography has a **second** asymmetry, and it is
the one that actually carries most of the internet:

> Computing `g^x mod p` is easy. Recovering `x` from `g^x mod p` is hard.

Day 150 gave you the easy direction — `pow(g, x, p)` in `O(log x)` multiplies.
This day is the hard direction. That gap is the entire security argument for:

| System | What the attacker must invert |
|---|---|
| **Diffie-Hellman** key exchange | `A = g^a mod p` → recover `a` |
| **ElGamal** encryption | same group, same problem |
| **DSA** signatures | `r = (g^k mod p) mod q` → recover the nonce `k` |
| **ECDSA** / Bitcoin / Ethereum signatures | `Q = k·G` on a curve → recover `k` (ECDLP) |
| **Signal / TLS 1.3 handshakes** | X25519, which is ECDH |

RSA and Diffie-Hellman are **not** the same bet. Factoring and discrete log are
different problems; a break in one does not automatically break the other.
(Shor's algorithm breaks both, which is why post-quantum crypto abandons both.)

### Scope note — what this day is not

`day-150` owns fast exponentiation, including matrix exponentiation
(`day-150/README.md:69`). We do not re-derive it. We call `pow(g, x, p)`, which
is the same binary ladder day-150 built from scratch, and spend the whole budget
on **inverting** it. `day-151` owns the extended Euclidean algorithm and modular
inverse (`day-151/rsa.py:50,58`); we call `pow(a, -1, p)`, Python's built-in
spelling of exactly that, rather than writing it a third time.

## The Problem, Precisely

Given a cyclic group `G = <g>` of order `n`, and an element `h ∈ G`, find `x`
with `0 <= x < n` such that:

```
g^x = h
```

We work in `G = Z_p^*` (the nonzero residues mod a prime `p`) under
multiplication. `Z_p^*` is cyclic of order `p - 1`, so a generator `g` exists and
every `h` has exactly one logarithm mod `n`.

**The logarithm is only defined modulo the order of `g`.** If `g` has order `n`,
then `g^x = g^(x + n)`, so "the" answer is a residue class. Every algorithm here
returns the representative in `[0, n)`, and every one of them needs to know `n`.
Getting `n` wrong is the most common way to produce a wrong answer that *looks*
plausible.

## Why It Is Believed Hard

Two different statements, often confused:

1. **Generic groups.** If the algorithm may only multiply, invert, and compare
   group elements — treating them as opaque tokens — then Shoup's 1997 lower
   bound says `Ω(sqrt(n))` group operations are required. Both algorithms below
   *match* that bound, so in the generic model they are optimal. There is no
   cleverness left to find.
2. **`Z_p^*` specifically.** Its elements are integers, not opaque tokens, and
   integers factor. **Index calculus** exploits that and runs in sub-exponential
   time, roughly `exp(c·(log p)^(1/3)·(log log p)^(2/3))` — the same shape as the
   Number Field Sieve for factoring (`day-151/README.md:16`).

Point 2 is why finite-field Diffie-Hellman needs 2048+ bit primes, matching RSA.
Point 1 is why **elliptic-curve** groups need only ~256 bits: no useful notion of
a "smooth" curve point has been found, so index calculus does not apply and
`sqrt(n)` is all an attacker gets. Same problem, 8x smaller keys, purely because
one group leaks structure and the other does not.

## Baseline — Brute Force

```
y = 1
for x in 0 .. n-1:
    if y == h: return x
    y = (y * g) % p
```

`O(n)` multiplies, `O(1)` space. For a 2048-bit prime, `n ≈ 2^2047`. Done.

## Baby-Step Giant-Step (Shanks, 1971)

The classic time/space trade: **meet in the middle over the exponent**.

Write `x` in base `m` where `m = ceil(sqrt(n))`:

```
x = i*m + j        with  0 <= i < m,  0 <= j < m
```

Every `x < n <= m^2` has such a representation. Substitute:

```
g^(i*m + j) = h
g^j         = h · (g^(-m))^i
```

The left side depends only on `j`, the right only on `i`. So:

1. **Baby steps** — compute `g^j` for `j = 0 .. m-1` and store `{g^j : j}` in a
   hash table. `m` multiplies, `m` slots.
2. **Giant steps** — set `factor = g^(-m)` and walk `γ_i = h · factor^i` for
   `i = 0, 1, 2, ...`. Each step is one multiply. The first `γ_i` found in the
   table gives `x = i*m + j`.

Two `sqrt(n)`-length lists, and we look for a collision between them instead of
scanning `n` candidates. `O(sqrt(n))` time **and** `O(sqrt(n))` space.

For `n ≈ 10^18`, `sqrt(n) = 10^9` — a billion table entries, tens of gigabytes.
That is the wall: BSGS is memory-bound long before it is time-bound.

### Details That Bite

- **Store the smallest `j`.** If `g` has small order, `g^j` repeats within the
  baby steps. Keeping the first (smallest) `j` yields the smallest valid `x`.
- **`g^(-m)` needs an inverse.** It exists iff `gcd(g, p) = 1`, which holds for
  prime `p` and `g ≢ 0`. Composite moduli are where this silently breaks.
- **`n` must be a multiple of `g`'s order**, or `i` runs out before the answer
  appears. Using `p - 1` is always safe (Lagrange: every element's order divides
  the group order); using the exact order is faster.
- **"No solution" is a real outcome.** If `h ∉ <g>`, the loop finishes and the
  answer is `None`. Returning 0 or raising on that path is a correctness bug.

## Pollard's Rho for Logarithms (1978)

Same `O(sqrt(n))` time, **`O(1)` space**. It buys back the memory that kills
BSGS, at the cost of being randomized.

The idea: take a pseudo-random walk through the group where every point is
tracked as a known combination of `g` and `h`:

```
invariant:   x_k = g^(a_k) · h^(b_k)
```

The walk partitions the group into three sets by `x mod 3` and steps:

```
x ≡ 0 (mod 3):   x <- x·x        a <- 2a (mod n)    b <- 2b (mod n)
x ≡ 1 (mod 3):   x <- x·g        a <- a+1 (mod n)   b <- b
x ≡ 2 (mod 3):   x <- x·h        a <- a             b <- b+1 (mod n)
```

The group is finite, so the walk must eventually repeat — the trajectory looks
like the Greek letter **ρ**: a tail running into a cycle. By the birthday bound a
collision appears after about `sqrt(π·n/2) ≈ 1.25·sqrt(n)` steps. Floyd's
tortoise-and-hare finds it with two pointers and **no stored history**.

At a collision `x_t = x_h`:

```
g^(a_t) · h^(b_t) = g^(a_h) · h^(b_h)
g^(a_t - a_h)     = h^(b_h - b_t)
```

Substituting `h = g^x` and taking exponents mod `n`:

```
a_t - a_h ≡ x · (b_h - b_t)   (mod n)
x         ≡ (a_t - a_h) · (b_h - b_t)^(-1)   (mod n)
```

### When The Collision Is Useless

`(b_h - b_t)^(-1)` only exists when `gcd(b_h - b_t, n) = 1`. Three cases:

- `b_h - b_t ≡ 0 (mod n)` → the collision carries no information about `x`.
  Restart the walk from a fresh random `(a_0, b_0)`.
- `d = gcd(b_h - b_t, n) > 1` → the congruence has `d` solutions instead of one.
  Divide through by `d`, solve mod `n/d`, and test the `d` candidates against
  `pow(g, x, p) == h`. Cheap when `d` is small.
- `d = 1` → the common case, one answer.

**This is why real systems use prime-order subgroups.** With `n` prime, `d` is 1
or `n` — either it works immediately or it fails outright and you restart. No
candidate enumeration, no partial information. A safe prime `p = 2q + 1` gives
you a clean order-`q` subgroup for free: take `g' = g^2`.

### BSGS vs Rho

| | BSGS | Pollard's rho |
|---|---|---|
| Time | `sqrt(n)` (deterministic) | `~1.25·sqrt(n)` (expected) |
| Space | `sqrt(n)` | `O(1)` |
| Deterministic | yes | no — may need restarts |
| Parallelizes | poorly (shared table) | well (distinguished points) |
| Practical ceiling | `n ≈ 2^60` (memory) | `n ≈ 2^128` (time) |

Every published ECDLP record — Certicom's challenges, the 114-bit curve broken in
2020 — used parallel rho, never BSGS. Memory, not arithmetic, is the binding
constraint.

## Diffie-Hellman: What The Attacker Actually Does

```
public:   p, g
Alice:    picks secret a,  sends A = g^a mod p
Bob:      picks secret b,  sends B = g^b mod p
shared:   s = B^a = A^b = g^(ab) mod p
```

Eve sees `p, g, A, B` — never `a`, `b`, or `s`. To get `s` she solves **one**
discrete log (`a` from `A`), then computes `B^a` herself. One log, not two.

Strictly, breaking DH requires the **Computational Diffie-Hellman** assumption
(given `g^a, g^b`, produce `g^(ab)`), which is *at most* as hard as discrete log.
Nobody knows a way to do CDH without solving DL, but the reduction has only ever
been proved in one direction. `discrete_log.py` demonstrates the attack that
actually exists.

## Why Toy Parameters Break — And Real Ones Do Not

| `p` | `sqrt(p)` | rho steps | verdict |
|---|---|---|---|
| 1,019 | ~32 | instant | breakable by hand |
| 10^9 | ~31,600 | milliseconds | this file breaks it |
| 2^64 | 2^32 | ~4·10^9 | hours on a laptop |
| 2^256 (EC) | 2^128 | 3·10^38 | infeasible, ever |
| 2^2048 (`Z_p^*`) | — | index calculus, not rho | infeasible today |

The two infeasible rows fail for *different reasons*, and that difference is the
whole point of the hardness section above.

## Pohlig-Hellman — Why "Safe Primes" Exist

If `p - 1` factors into small primes (`p - 1` is **smooth**), the discrete log
problem shatters. Pohlig-Hellman (1978) solves the log independently in each
prime-power subgroup and glues the answers with the Chinese Remainder Theorem.
Total cost becomes `O(sqrt(largest prime factor of p-1))` instead of
`O(sqrt(p))`.

Concretely: if `p - 1 = 2^k` then every subgroup has order a power of 2 and the
log falls out in ~`k` steps regardless of how big `p` looks. A 1024-bit prime
with a smooth `p - 1` offers essentially no security.

The defence is a **safe prime**: `p = 2q + 1` with `q` also prime. Then
`p - 1 = 2q` has largest factor `q ≈ p/2`, and Pohlig-Hellman degenerates to
doing nothing.

This is the exact structural twin of `day-151/README.md:68-70`, where RSA primes
must be chosen so `p - 1` is not smooth, to defeat Pollard's `p - 1` **factoring**
method. Same weakness (smoothness), same defence (safe primes), two different
cryptosystems. That is not a coincidence — it is what smooth group order costs
you in any group.

We describe Pohlig-Hellman rather than implement it; the two algorithms this day
owns are BSGS and rho.

## Complexity

| Algorithm | Time | Space | Notes |
|---|---|---|---|
| Brute force | `O(n)` | `O(1)` | the thing to beat |
| Baby-step giant-step | `O(sqrt(n))` | `O(sqrt(n))` | deterministic; memory-bound |
| Pollard's rho | `O(sqrt(n))` expected | `O(1)` | randomized; restarts possible |
| Pohlig-Hellman | `O(sqrt(largest prime factor of n))` | varies | needs `n` factored |
| Index calculus (`Z_p^*` only) | sub-exponential | large | why 2048-bit primes |
| Generic lower bound | `Ω(sqrt(n))` | — | Shoup 1997 |
| `multiplicative_order` (here) | `O(sqrt(p) + log^2 p)` | `O(log p)` | trial-divide `p-1`, then strip factors |

`n` is the order of `g`, not `p`. Using the subgroup order instead of `p - 1`
halves the work for a safe prime — and much more for a general one.

## Failure Modes

1. **Using `p` where you mean `p - 1`.** The group `Z_p^*` has `p - 1` elements,
   not `p`. Off by one here makes BSGS scan one step too far (harmless) or one
   step too short (misses the largest exponent).

2. **Assuming `g` is a generator.** If `g` has order `n < p - 1`, only `n` of the
   `p - 1` residues are reachable, and `h` outside `<g>` has **no** logarithm.
   Code that returns 0 or loops forever instead of reporting "no solution" is
   wrong.

3. **`h = 0`.** `0 ∉ Z_p^*` — no power of `g` is ever 0 mod prime `p`. Reject at
   the boundary; do not search.

4. **Composite modulus.** `Z_m^*` for composite `m` is not necessarily cyclic
   (`Z_8^*` is not), `g^(-m)` may not exist, and "the" logarithm may not be
   unique. Every algorithm here assumes prime `p`.

5. **Pollard's rho with `b_h - b_t ≡ 0`.** A real, regularly-occurring outcome,
   not a bug. Code that divides anyway raises; code that ignores it returns a
   wrong `x`. Restart with a fresh random start.

6. **Rho with no iteration cap.** A walk can enter a short cycle carrying no
   information and spin forever. Cap iterations at a few multiples of `sqrt(n)`
   and restart.

7. **Nonce reuse in DSA/ECDSA.** Not a weakness of the discrete log problem — a
   weakness of *using* it. Sign two messages with the same `k` and the private
   key falls out of two linear equations, no logarithm needed. This broke the
   Sony PS3 (2010) and drained Android Bitcoin wallets (2013). The hard problem
   was never attacked; the protocol leaked around it.

8. **Small-subgroup confinement.** If an attacker sends a public value `A` of
   small order (say order 2), the "shared secret" lands in a tiny subgroup and is
   guessable. Validate received values: `A != 1` and `A^q = 1 mod p`.

## Checkpoint Questions

1. Derive `g^j = h·(g^(-m))^i` from `x = i·m + j`. Why is `m = ceil(sqrt(n))` the
   optimal split, and what happens to time and space if you choose
   `m = n^(1/3)` instead?
2. BSGS is `O(sqrt(n))` in both time and space. For `n = 2^80`, which resource
   runs out first on real hardware, and by roughly what factor?
3. In Pollard's rho, state the invariant maintained at every step and check that
   it holds for all three branches of the step function.
4. A collision gives `a_t - a_h ≡ x(b_h - b_t) mod n`. Show exactly why
   `gcd(b_h - b_t, n) = d > 1` yields `d` candidate logarithms, and how you would
   pick the right one.
5. Why does using a prime-order subgroup make case 4 disappear? What does a safe
   prime `p = 2q+1` give you that a random prime does not?
6. Eve sees `p, g, A, B` in a Diffie-Hellman exchange. Exactly how many discrete
   logs must she solve to recover the shared secret? Why not two?
7. Elliptic-curve keys are 256 bits while finite-field Diffie-Hellman needs 2048.
   Both target ~128-bit security. Explain the gap in terms of which algorithm
   applies to which group.
8. `p - 1 = 2^40 · 3` for some 41-bit prime `p`. Estimate the cost of
   Pohlig-Hellman on it and compare with `sqrt(p)`. What property of `p` did the
   designer fail to check?
9. Day 151's RSA and this day's Diffie-Hellman both die to Shor's algorithm but
   survive different classical attacks. Name a classical advance that would break
   one and leave the other standing.
