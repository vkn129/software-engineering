"""
Day 11: Probability in Algorithms -- Randomized Algorithms, Expected Value
==========================================================================

This file implements core randomized algorithms from scratch. No external
libraries -- only Python's built-in 'random' module for random number generation.

We build: Miller-Rabin primality, randomized quicksort with comparison counting,
reservoir sampling, and birthday paradox simulation.

Run: python probability_algorithms.py
"""

import random
import math
import time


# =============================================================================
# SECTION 1: Modular Exponentiation (prerequisite for Miller-Rabin)
# =============================================================================

print("=" * 65)
print("SECTION 1: Modular Exponentiation -- The Engine of Primality Tests")
print("=" * 65)


def mod_pow(base, exp, mod):
    """Compute (base^exp) % mod efficiently using repeated squaring.

    Why not just pow(base, exp) % mod?
    Because base^exp can be astronomically large. For a 1000-digit prime,
    base^exp has billions of digits -- it won't fit in memory.

    Repeated squaring keeps all intermediate values < mod^2 by reducing
    after every multiplication. This gives O(log exp) multiplications,
    each on numbers at most 2*log2(mod) bits long.

    Python's built-in pow(base, exp, mod) does exactly this, but we
    implement it to understand why it works.
    """
    if mod == 1:
        return 0
    result = 1
    base = base % mod
    while exp > 0:
        # If exp is odd, multiply result by base
        if exp % 2 == 1:
            result = (result * base) % mod
        # Square the base and halve the exponent
        exp = exp >> 1
        base = (base * base) % mod
    return result


# Verify against Python's built-in
print("\nModular exponentiation verification:")
test_cases = [(2, 10, 1000), (3, 100, 97), (7, 256, 13), (2, 1000, 1000000007)]
for b, e, m in test_cases:
    ours = mod_pow(b, e, m)
    builtin = pow(b, e, m)
    status = "OK" if ours == builtin else "MISMATCH"
    print(f"  {b}^{e} mod {m} = {ours}  [{status}]")


# =============================================================================
# SECTION 2: Miller-Rabin Primality Test
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 2: Miller-Rabin Primality Test")
print("=" * 65)

print("""
Why Miller-Rabin over trial division?
  Trial division: O(sqrt(n)) -- for a 100-digit number, that's 10^50 operations.
    Even at 10^9 ops/sec, that's 10^41 seconds (universe is ~10^17 seconds old).
  Miller-Rabin: O(k * log^2(n)) -- a few hundred multiplications. Milliseconds.

This is the algorithm that makes RSA possible. Every time your browser opens
an HTTPS connection, Miller-Rabin (or a variant) generates the primes.
""")


def miller_rabin_test(n, a):
    """Single round of Miller-Rabin with witness a.

    Returns True if n passes (might be prime), False if n is definitely composite.

    The math: write n-1 = 2^s * d where d is odd.
    Compute x = a^d mod n, then square s times.

    If n is prime, Fermat says a^(n-1) = 1 mod n.
    But more: the only square roots of 1 mod p (prime) are 1 and p-1.
    So the sequence x, x^2, x^4, ..., x^(2^s) must either:
      - Start with 1 (a^d = 1 mod n), or
      - Hit n-1 at some point before reaching 1

    If neither happens, n is definitely composite.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Factor out powers of 2 from n-1: n-1 = 2^s * d
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1

    # Compute a^d mod n
    x = mod_pow(a, d, n)

    # If a^d = 1 or a^d = n-1, this witness says "probably prime"
    if x == 1 or x == n - 1:
        return True

    # Square x up to s-1 times, looking for n-1
    for _ in range(s - 1):
        x = (x * x) % n
        if x == n - 1:
            return True
        # If x == 1, we found a non-trivial square root of 1 -- composite
        if x == 1:
            return False

    # Never hit n-1 in the squaring chain -- composite
    return False


def is_prime(n, k=20):
    """Miller-Rabin primality test with k rounds.

    Error probability <= (1/4)^k.
    k=20 gives error < 10^(-12), sufficient for most applications.
    k=40 gives error < 10^(-24), sufficient for cryptographic primes.

    Why (1/4)^k? For any composite n, at least 3/4 of all bases in [2, n-2]
    are "witnesses" that reveal n as composite. Each round independently
    has at most 1/4 chance of failing to detect compositeness.
    """
    if n < 2:
        return False
    # Small primes: handle directly
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    if n in small_primes:
        return True
    if any(n % p == 0 for p in small_primes):
        return False

    # k rounds of Miller-Rabin with random witnesses
    for _ in range(k):
        a = random.randrange(2, n - 1)
        if not miller_rabin_test(n, a):
            return False
    return True


# Test against known primes and composites
print("Miller-Rabin test results:")
test_numbers = [
    (2, True), (3, True), (4, False), (17, True), (561, False),
    (1009, True), (1000000007, True), (1000000009, True),
    (1000000006, False), (104729, True),
]
for n, expected in test_numbers:
    result = is_prime(n)
    status = "OK" if result == expected else "WRONG"
    label = "prime" if result else "composite"
    print(f"  {n:>15}: {label:>10}  (expected {'prime' if expected else 'composite'})  [{status}]")

# 561 is the smallest Carmichael number -- Fermat's test fails on it,
# but Miller-Rabin catches it
print(f"\n  561 is a Carmichael number (fools Fermat, not Miller-Rabin):")
print(f"    2^560 mod 561 = {mod_pow(2, 560, 561)}  (Fermat says 'prime' -- WRONG)")
print(f"    Miller-Rabin says: {'prime' if is_prime(561) else 'composite'}  (CORRECT)")

# Find primes in a range
print("\nPrimes between 900 and 1000:")
primes_in_range = [n for n in range(900, 1001) if is_prime(n)]
print(f"  {primes_in_range}")

# Time Miller-Rabin on a large number
large_prime = 10**18 + 9  # Known prime
start = time.perf_counter()
result = is_prime(large_prime, k=40)
elapsed = time.perf_counter() - start
print(f"\n  is_prime(10^18 + 9) = {result} in {elapsed*1000:.2f} ms (40 rounds)")


# =============================================================================
# SECTION 3: Randomized Quicksort with Comparison Counting
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 3: Randomized Quicksort -- Expected Value in Action")
print("=" * 65)

print("""
Deterministic quicksort with first-element pivot:
  - O(n log n) average on random inputs
  - O(n^2) on sorted/reverse-sorted inputs (adversarial!)

Randomized quicksort (random pivot):
  - O(n log n) EXPECTED on ALL inputs
  - No adversary can force worst case because the randomness is ours

Expected comparisons: 2n*H_n where H_n = 1 + 1/2 + 1/3 + ... + 1/n
For n=1000: 2*1000*7.49 ~= 14,978 comparisons.
""")

comparison_count = 0  # Global counter to track comparisons


def randomized_quicksort(arr):
    """Quicksort with random pivot selection.

    The random pivot ensures that no matter what the input looks like,
    the expected partition is roughly balanced. Even sorted input gives
    O(n log n) expected time.
    """
    global comparison_count
    if len(arr) <= 1:
        return arr

    # Random pivot: this is the key to breaking adversarial inputs
    pivot_idx = random.randrange(len(arr))
    pivot = arr[pivot_idx]

    left = []
    middle = []
    right = []
    for x in arr:
        comparison_count += 1  # Each element compared to pivot
        if x < pivot:
            left.append(x)
        elif x > pivot:
            right.append(x)
        else:
            middle.append(x)

    return randomized_quicksort(left) + middle + randomized_quicksort(right)


def harmonic(n):
    """Compute the nth harmonic number: H_n = 1 + 1/2 + 1/3 + ... + 1/n."""
    return sum(1.0 / i for i in range(1, n + 1))


# Compare actual comparisons to theoretical expected value
print("Comparison count vs theoretical 2n*H_n:")
print(f"  {'n':>6} {'Expected':>12} {'Actual (avg 10 runs)':>22} {'Ratio':>8}")
print("  " + "-" * 55)

for n in [100, 500, 1000, 5000]:
    expected = 2 * n * harmonic(n)
    actuals = []
    for _ in range(10):
        comparison_count = 0
        arr = list(range(n))  # Sorted input -- worst case for deterministic
        random.shuffle(arr)    # Not needed for correctness, but fair comparison
        randomized_quicksort(arr)
        actuals.append(comparison_count)
    avg_actual = sum(actuals) / len(actuals)
    ratio = avg_actual / expected
    print(f"  {n:>6} {expected:>12.0f} {avg_actual:>22.0f} {ratio:>8.2f}")

# Show that sorted input is NOT worst case for randomized quicksort
print("\nSorted input (adversarial for deterministic quicksort):")
for n in [100, 500, 1000]:
    expected = 2 * n * harmonic(n)
    actuals = []
    for _ in range(10):
        comparison_count = 0
        arr = list(range(n))  # Already sorted -- deterministic QS would be O(n^2)
        randomized_quicksort(arr)
        actuals.append(comparison_count)
    avg_actual = sum(actuals) / len(actuals)
    ratio = avg_actual / expected
    print(f"  n={n:>5}: avg comparisons = {avg_actual:>8.0f}, "
          f"expected = {expected:>8.0f}, ratio = {ratio:.2f}")
    print(f"           O(n^2) would be ~{n*n//2:>8}, "
          f"actual/n^2 = {avg_actual / (n*n):.3f}")


# =============================================================================
# SECTION 4: Birthday Paradox Simulation
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 4: Birthday Paradox -- When Collisions Happen")
print("=" * 65)

print("""
The birthday paradox: in a group of just 23 people, there is a >50% chance
that two share a birthday. This feels wrong because we think about matching
a SPECIFIC birthday (1/365), but the question is about ANY pair matching.

With n people, there are C(n,2) = n*(n-1)/2 pairs to check. For n=23,
that's 253 pairs -- plenty of chances for a match.

General formula: with d possible values, collision probability exceeds 50%
after approximately sqrt(pi*d/2) ~ 1.177*sqrt(d) samples.

For 365 days: sqrt(pi*365/2) ~ 23.9 -- matches the birthday paradox.
""")


def birthday_paradox_simulation(num_days, num_trials=10000):
    """Simulate the birthday paradox to find when first collision occurs.

    Returns average number of people needed for a collision.

    This is fundamentally about hash collisions: if your hash function maps
    to num_days buckets, this tells you how many items until a collision.
    """
    total_people = 0
    for _ in range(num_trials):
        seen = set()
        count = 0
        while True:
            birthday = random.randrange(num_days)
            count += 1
            if birthday in seen:
                break
            seen.add(birthday)
        total_people += count
    return total_people / num_trials


def birthday_theoretical(num_days):
    """Theoretical expected number of samples until first collision.

    Approximation: sqrt(pi * num_days / 2)
    """
    return math.sqrt(math.pi * num_days / 2)


print("Birthday paradox: samples until first collision")
print(f"  {'Values (d)':>12} {'Theory':>10} {'Simulated':>12} {'Hash bits':>10}")
print("  " + "-" * 50)

for d, label in [(365, "days"), (1000, "1K"), (10000, "10K"),
                  (100000, "100K"), (1000000, "1M")]:
    theory = birthday_theoretical(d)
    simulated = birthday_paradox_simulation(d, num_trials=5000)
    bits = math.log2(d)
    print(f"  {d:>12} {theory:>10.1f} {simulated:>12.1f} {bits:>10.1f}")

# Connection to hash collisions
print("\nHash collision implications:")
for bits in [16, 32, 64, 128]:
    d = 2 ** bits
    theory = birthday_theoretical(d)
    print(f"  {bits:>3}-bit hash: collision expected after ~{theory:.2e} items "
          f"= 2^{math.log2(theory):.1f}")


# Birthday paradox: probability of collision for n people in 365 days
print("\nCollision probability vs group size (365 days):")
print(f"  {'People':>8} {'P(collision)':>15}")
print("  " + "-" * 28)


def birthday_collision_prob(n, d=365):
    """Exact probability that at least 2 of n people share a birthday out of d days.

    P(no collision) = (d/d) * ((d-1)/d) * ((d-2)/d) * ... * ((d-n+1)/d)
    P(collision) = 1 - P(no collision)
    """
    if n > d:
        return 1.0
    p_no_collision = 1.0
    for i in range(n):
        p_no_collision *= (d - i) / d
    return 1.0 - p_no_collision


for n in [5, 10, 15, 20, 23, 30, 40, 50, 57, 70, 100]:
    p = birthday_collision_prob(n)
    bar = "#" * int(p * 40)
    print(f"  {n:>8} {p:>15.4f}  {bar}")


# =============================================================================
# SECTION 5: Reservoir Sampling
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 5: Reservoir Sampling -- Randomness in Streaming")
print("=" * 65)

print("""
Problem: you're processing a massive data stream (log files, sensor data,
Twitter firehose). You want a random sample of k items, but you don't know
how many items there are, and you can't store them all.

Reservoir sampling solves this in O(n) time and O(k) space, and every item
has exactly the same probability of being in the final sample.

This is used in:
  - Database query sampling (TABLESAMPLE in PostgreSQL)
  - A/B testing on streaming data
  - Approximate algorithms for massive datasets
""")


def reservoir_sample(stream, k):
    """Select k items uniformly at random from a stream of unknown length.

    Algorithm R (Vitter, 1985):
    1. Fill reservoir with first k items
    2. For each subsequent item i (0-indexed from k):
       - Generate random j in [0, i]
       - If j < k, replace reservoir[j] with stream[i]

    Why this works: at step i, each item has probability k/i of being
    in the reservoir. The replacement maintains this invariant because:
    - New item enters with probability k/(i+1)
    - Each existing item survives with probability 1 - 1/(i+1) = i/(i+1)
    - Combined: (k/i) * (i/(i+1)) = k/(i+1)
    """
    reservoir = []

    for i, item in enumerate(stream):
        if i < k:
            # Fill the reservoir with the first k items
            reservoir.append(item)
        else:
            # Replace a random element with decreasing probability
            j = random.randrange(i + 1)
            if j < k:
                reservoir[j] = item

    return reservoir


# Verify uniformity: sample 1 item from [0..9], repeat many times
print("Reservoir sampling uniformity test (k=1, stream=[0..9], 100000 trials):")
counts = [0] * 10
num_trials = 100000
for _ in range(num_trials):
    sample = reservoir_sample(range(10), 1)
    counts[sample[0]] += 1

print(f"  Expected frequency per item: {num_trials/10:.0f}")
print(f"  Actual frequencies:")
for i, c in enumerate(counts):
    bar = "#" * (c // 500)
    deviation = (c - num_trials/10) / (num_trials/10) * 100
    print(f"    item {i}: {c:>6} ({deviation:>+5.1f}%)  {bar}")

# Verify uniformity for k > 1
print("\nReservoir sampling with k=3, stream=[0..19], 50000 trials:")
counts_k3 = [0] * 20
num_trials_k3 = 50000
for _ in range(num_trials_k3):
    sample = reservoir_sample(range(20), 3)
    for item in sample:
        counts_k3[item] += 1

expected_per_item = num_trials_k3 * 3 / 20  # Each item has prob k/n = 3/20
print(f"  Expected count per item: {expected_per_item:.0f}")
max_dev = max(abs(c - expected_per_item) / expected_per_item * 100 for c in counts_k3)
print(f"  Max deviation from expected: {max_dev:.1f}%")
print(f"  All items within 10%: {all(abs(c - expected_per_item) / expected_per_item < 0.10 for c in counts_k3)}")

# Demonstrate streaming usage
print("\nStreaming demo: sample 5 from a stream of unknown length")


def infinite_stream(limit):
    """Simulate a data stream. In real life this could be log lines, sensor data, etc."""
    for i in range(limit):
        yield f"event_{i:04d}"


stream_size = 10000
sample = reservoir_sample(infinite_stream(stream_size), 5)
print(f"  Stream size: {stream_size}")
print(f"  Sample of 5: {sample}")
print(f"  (Items are spread across the stream, not clustered at start or end)")


# =============================================================================
# SECTION 6: Las Vegas vs Monte Carlo -- Side by Side
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 6: Las Vegas vs Monte Carlo -- Side by Side")
print("=" * 65)


def las_vegas_find_target(arr, target):
    """Las Vegas algorithm: always finds target (if present), random time.

    Strategy: check random positions until we find the target.
    Expected time: n/k checks where k = number of occurrences.
    Always correct, but could theoretically run forever on bad luck.

    This is silly for search (just scan linearly), but illustrates the concept.
    Las Vegas = correct answer, random runtime.
    """
    n = len(arr)
    checked = set()
    attempts = 0
    while len(checked) < n:
        idx = random.randrange(n)
        attempts += 1
        if arr[idx] == target:
            return idx, attempts  # Always correct
        checked.add(idx)
    return -1, attempts  # Target not in array


def monte_carlo_majority(arr, k=20):
    """Monte Carlo algorithm: fast, but might be wrong.

    Check k random positions. If any value appears > k/2 times in our sample,
    declare it the majority element.

    If a true majority exists (appears > n/2 times), we find it with high
    probability. If no majority exists, we might incorrectly declare one.

    Monte Carlo = bounded runtime, possible error.
    """
    n = len(arr)
    from collections import Counter
    samples = [arr[random.randrange(n)] for _ in range(k)]
    counts = Counter(samples)
    most_common, freq = counts.most_common(1)[0]
    if freq > k // 2:
        return most_common, True  # Confident
    return None, False  # No majority detected


# Las Vegas demo
print("\nLas Vegas search (always correct, random time):")
arr = [0] * 1000
arr[42] = 1  # One needle in a haystack
attempts_list = []
for _ in range(100):
    _, attempts = las_vegas_find_target(arr, 1)
    attempts_list.append(attempts)
avg_attempts = sum(attempts_list) / len(attempts_list)
print(f"  Array size: 1000, target appears once")
print(f"  Expected attempts: ~1000, Actual avg: {avg_attempts:.0f}")
print(f"  Min: {min(attempts_list)}, Max: {max(attempts_list)}")

# Monte Carlo demo
print("\nMonte Carlo majority (fast, might be wrong):")
arr_majority = [1] * 600 + [2] * 400  # 1 is majority (60%)
correct = 0
trials = 1000
for _ in range(trials):
    result, confident = monte_carlo_majority(arr_majority, k=20)
    if result == 1 and confident:
        correct += 1
print(f"  Array: 60% ones, 40% twos (majority = 1)")
print(f"  Correctly found majority: {correct}/{trials} ({correct/trials*100:.1f}%)")


# =============================================================================
# SECTION 7: Putting It All Together -- Why Randomization Matters
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 7: Summary -- Why Randomization Matters")
print("=" * 65)

print("""
Key takeaways:

1. ADVERSARY RESISTANCE: Randomized algorithms have no worst-case inputs.
   An adversary would need to predict your random bits to craft bad inputs.

2. SIMPLICITY: Randomized quicksort is 10 lines. Deterministic linear-time
   selection (median of medians) is 50+ lines with worse constants.

3. FEASIBILITY: Miller-Rabin tests 1000-digit primes in milliseconds.
   No known deterministic algorithm is practical for this task.

4. STREAMING: Reservoir sampling handles infinite streams in O(k) space.
   No deterministic algorithm can do this without knowing the stream length.

5. MATHEMATICAL GUARANTEES: "Probably correct" is not hand-waving.
   Error probability 2^(-100) is less likely than your hardware failing.
   Monte Carlo with enough rounds is MORE reliable than deterministic code
   running on physical hardware.

The cost? A source of randomness. In practice, pseudorandom generators
(seeded from /dev/urandom) are sufficient for all non-cryptographic uses.
""")

print("=" * 65)
print("All demonstrations complete.")
print("=" * 65)
