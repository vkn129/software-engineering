# Day 11: Probability in Algorithms -- Randomized Algorithms, Expected Value

## Why This Exists

Deterministic algorithms have a weakness: adversarial inputs. If an attacker knows
your algorithm, they can craft inputs that trigger worst-case behavior every time.
Quicksort with a fixed pivot on already-sorted data? O(n^2). Hash tables with a
predictable hash function? O(n) lookups via collision attacks.

Randomization breaks this. When the algorithm makes random choices, no adversary
can predict them. Randomized quicksort has O(n log n) *expected* time on *every*
input, not just average inputs. Miller-Rabin can test whether a 1000-digit number
is prime in milliseconds, something no known deterministic algorithm achieves
efficiently.

This is not about "hoping for the best." Probability gives us precise mathematical
guarantees: expected values, error bounds, concentration inequalities. A Monte Carlo
algorithm with error probability 2^(-100) is more reliable than a deterministic
algorithm running on hardware with a higher bit-flip rate.

Understanding probability in algorithms unlocks:
- **Cryptography**: Miller-Rabin generates the primes that secure HTTPS
- **Databases**: reservoir sampling for approximate query processing
- **Load balancing**: randomized hashing distributes work evenly
- **Streaming**: processing data you cannot store (reservoir sampling)
- **Hash tables**: the birthday paradox tells you exactly when collisions explode

## Theory (40 min)

### 1. Las Vegas vs Monte Carlo Algorithms

Two fundamental classes of randomized algorithms:

**Las Vegas**: Always produces the correct answer, but runtime is random.
Example: randomized quicksort. It always sorts correctly, but the number of
comparisons varies. We analyze the *expected* runtime.

**Monte Carlo**: Always runs in bounded time, but the answer may be wrong.
Example: Miller-Rabin primality test. It runs in O(k log^2 n) time, but has
a probability <= 4^(-k) of incorrectly calling a composite number "prime."

Key insight: you can often convert Monte Carlo to "almost Las Vegas" by repeating
the test. Run Miller-Rabin 40 times and the error probability is 4^(-40) ~= 10^(-24).
That is less likely than a cosmic ray flipping a bit in your RAM.

### 2. Expected Value Analysis

The expected value E[X] of a random variable X is the weighted average of its
possible values: E[X] = sum of (value * probability) over all outcomes.

**Linearity of expectation** is the most powerful tool in algorithm analysis:
    E[X + Y] = E[X] + E[Y]
This holds even if X and Y are dependent. This is why we can analyze randomized
quicksort by summing over all pairs of elements.

**Randomized quicksort expected comparisons**: For n elements, the expected number
of comparisons is 2n*H_n ~ 2n*ln(n), where H_n is the nth harmonic number.
The proof: element i and element j are compared if and only if one of them is
chosen as a pivot before any element between them. That probability is 2/(j-i+1).
Sum over all pairs to get 2n*H_n.

### 3. Miller-Rabin Primality Test

The gold standard for primality testing in practice.

**Fermat's Little Theorem**: If p is prime and gcd(a, p) = 1, then a^(p-1) = 1 (mod p).

**Problem**: Some composites (Carmichael numbers like 561) fool Fermat's test for
ALL bases. Miller-Rabin fixes this by examining the *square roots of 1 modulo n*.

Write n-1 = 2^s * d (factor out all 2s). Then for a random base a:
1. Compute x = a^d mod n
2. Square x repeatedly (s times)
3. If we ever see x^2 = 1 mod n but x != 1 and x != n-1, then n is composite

If n is composite, at least 3/4 of all bases a reveal this. So k rounds give
error probability <= (1/4)^k.

### 4. Birthday Paradox and Hash Collisions

In a room of 23 people, there is a >50% chance two share a birthday.
Generally: with n possible values, you expect a collision after ~sqrt(pi*n/2)
random samples.

For hash tables: with a 32-bit hash (4 billion values), expect a collision after
~77,000 insertions. With a 64-bit hash, after ~5 billion. This is why hash
functions need sufficient output size.

The birthday paradox also explains:
- Why UUIDs work (128-bit = collision after ~2^64 IDs, practically never)
- Why hash-based data structures need good distribution, not just large range
- Birthday attacks in cryptography (why hash outputs need to be 2x the security level)

### 5. Reservoir Sampling

**Problem**: Select k items uniformly at random from a stream of unknown length.
You see items one at a time and cannot store the entire stream.

**Algorithm (reservoir sampling, k=1)**:
1. Keep the first item
2. When you see the ith item, replace your choice with it with probability 1/i

**Proof it works**: After seeing n items, each item has probability 1/n of being
selected. Item i was selected with probability 1/i and survived (n-i) subsequent
rounds, each with probability (j-1)/j for j = i+1..n.
P(item i selected) = (1/i) * (i/(i+1)) * ((i+1)/(i+2)) * ... * ((n-1)/n) = 1/n.
The probabilities telescope.

### 6. Why Randomization Helps: Breaking Adversarial Inputs

**Quickselect** (find kth smallest): Deterministic median-of-medians gives O(n)
worst case but with a large constant. Random pivot gives O(n) *expected* with a
small constant. In practice, random pivot is faster.

**Treaps and skip lists**: Balanced BSTs (AVL, red-black) have complex rotations.
A treap assigns random priorities and maintains heap order, giving O(log n) expected
height with simpler code. Skip lists use coin flips for level assignment.

**Hashing**: Universal hash families choose a random hash function at startup,
guaranteeing O(1) expected lookup regardless of input distribution.

## Practice (20 min)

Complete the exercises in `practice.py`:
1. Implement Fermat primality test
2. Analyze expected comparisons in randomized partition
3. Monte Carlo pi estimation
4. Coupon collector problem simulation

## Daily Project

Build randomized algorithm implementations from scratch: Miller-Rabin primality
test, randomized quicksort with comparison counting, reservoir sampling, and
birthday paradox simulation. See `probability_algorithms.py`.

## Checkpoint Questions

1. Why can't an adversary construct a worst-case input for randomized quicksort?
   (Answer: the pivot is chosen randomly, so the adversary cannot predict which
   element will be the pivot. Every input has the same expected O(n log n) behavior.)
2. Miller-Rabin with k=20 rounds has error probability at most 4^(-20) ~= 10^(-12).
   Is this acceptable for generating RSA primes? Why or why not?
3. How many people do you need in a room for a >99% chance of a shared birthday?
   (Answer: 57 people.)
4. In reservoir sampling, why does each item have exactly probability 1/n of being
   chosen after n items have been seen? Trace the telescoping product for n=5.
5. Randomized quicksort makes ~2n*ln(n) expected comparisons. Standard quicksort
   with median-of-three makes ~1.7n*ln(n) on average inputs. When would you prefer
   the randomized version?
