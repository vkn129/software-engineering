"""
Day 8: Modular Arithmetic — Why Cryptography and Hashing Depend On It
=====================================================================

Modular arithmetic is clock arithmetic: after reaching some modulus m,
numbers wrap around to 0. This is not a curiosity — it is the mathematical
foundation of:

  - Cryptography (RSA, Diffie-Hellman, elliptic curves)
  - Hash tables (index = hash(key) % table_size)
  - Checksums and error detection (CRC, ISBN)
  - Random number generators (linear congruential generators)
  - Computer graphics (texture wrapping, circular buffers)

The reason modular arithmetic is so useful is that it creates FINITE
algebraic structures from infinite integers. Cryptography needs
computations that are easy to do forward but hard to reverse — and
modular exponentiation provides exactly that.

Run: python modular_arithmetic.py
"""


# =============================================================================
# SECTION 1: Modular Arithmetic Basics
# =============================================================================

print("=" * 65)
print("SECTION 1: Modular Arithmetic Basics — Clock Math")
print("=" * 65)

# The modulo operation: a % m gives the remainder when a is divided by m.
# Equivalently: a ≡ b (mod m) means m divides (a - b).

print("\n--- The Clock Analogy ---")
print("  A 12-hour clock is arithmetic mod 12.")
print("  10 o'clock + 5 hours = 3 o'clock, because (10 + 5) % 12 = 3")
print(f"  Python: (10 + 5) % 12 = {(10 + 5) % 12}")

print("\n--- Key Properties ---")
m = 7
a, b = 15, 23
print(f"  Working mod {m}, a = {a}, b = {b}")
print(f"  a mod m = {a % m}, b mod m = {b % m}")
print()

# Property 1: (a + b) mod m = ((a mod m) + (b mod m)) mod m
prop1_left = (a + b) % m
prop1_right = ((a % m) + (b % m)) % m
print(f"  Addition:       (a + b) % m = {prop1_left}")
print(f"                  ((a%m) + (b%m)) % m = {prop1_right}")
print(f"                  Equal? {prop1_left == prop1_right}")

# Property 2: (a * b) mod m = ((a mod m) * (b mod m)) mod m
prop2_left = (a * b) % m
prop2_right = ((a % m) * (b % m)) % m
print(f"\n  Multiplication: (a * b) % m = {prop2_left}")
print(f"                  ((a%m) * (b%m)) % m = {prop2_right}")
print(f"                  Equal? {prop2_left == prop2_right}")

# WHY this matters: you can reduce intermediate results at every step,
# preventing numbers from growing huge. This is critical for cryptography
# where exponents are 2048+ bits.
print("\n  WHY THIS MATTERS:")
print("  You can take mod at EVERY step of a computation.")
print("  Without this: computing 2^2048 gives a number with 617 digits.")
print("  With modular reduction at each step: numbers stay small.")


# =============================================================================
# SECTION 2: Modular Exponentiation — The Heart of Cryptography
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 2: Modular Exponentiation — From Scratch")
print("=" * 65)


def mod_exp_naive(base, exp, mod):
    """Compute (base^exp) % mod using naive repeated multiplication.

    Multiply base by itself exp times, taking mod at each step
    to keep numbers small.

    Time: O(exp) — linear in the exponent.
    This is USELESS for cryptography where exp has 2048 bits (exp ≈ 2^2048).
    """
    result = 1
    base = base % mod
    for _ in range(exp):
        result = (result * base) % mod
    return result


def mod_exp_fast(base, exp, mod):
    """Compute (base^exp) % mod using repeated squaring.

    The insight: express exp in binary and use the identity:
        base^exp = base^(b_k * 2^k + ... + b_1 * 2 + b_0)
                 = (base^(2^k))^b_k * ... * (base^2)^b_1 * base^b_0

    At each step we square the running base (doubling the exponent),
    and if the current bit of exp is 1, we multiply into the result.

    Time: O(log exp) — logarithmic in the exponent.
    For a 2048-bit exponent, this takes ~2048 multiplications instead of 2^2048.

    This is what makes RSA, Diffie-Hellman, and all public-key cryptography
    computationally feasible.
    """
    if mod == 1:
        return 0

    result = 1
    base = base % mod

    # Process each bit of the exponent from least significant to most
    while exp > 0:
        # If the current bit is 1, multiply result by current base
        if exp % 2 == 1:
            result = (result * base) % mod

        # Square the base (move to next bit position)
        base = (base * base) % mod

        # Shift exponent right by 1 (move to next bit)
        exp //= 2

    return result


# Demonstrate correctness
print("\n--- Correctness Check ---")
test_cases = [
    (2, 10, 1000),
    (3, 13, 50),
    (7, 256, 13),
    (123, 456, 789),
]
for b, e, m in test_cases:
    naive = mod_exp_naive(b, e, m)
    fast = mod_exp_fast(b, e, m)
    builtin = pow(b, e, m)  # Python's built-in 3-arg pow uses fast exponentiation
    print(f"  {b}^{e} mod {m} = {fast}  "
          f"(naive={naive}, builtin={builtin}, match={naive == fast == builtin})")

# Demonstrate the speed difference
print("\n--- Speed: Why Fast Exponentiation Matters ---")
import time

# Moderate exponent: both work, but fast is quicker
base_val, exp_val, mod_val = 2, 100_000, 1_000_000_007

start = time.perf_counter()
result_fast = mod_exp_fast(base_val, exp_val, mod_val)
time_fast = time.perf_counter() - start

start = time.perf_counter()
result_naive = mod_exp_naive(base_val, exp_val, mod_val)
time_naive = time.perf_counter() - start

print(f"  2^100000 mod 10^9+7:")
print(f"    Fast (O(log n)):  {time_fast*1000:.3f} ms  result = {result_fast}")
print(f"    Naive (O(n)):     {time_naive*1000:.3f} ms  result = {result_naive}")
print(f"    Speedup: ~{time_naive/max(time_fast, 1e-9):.0f}x")

# Large exponent: only fast works in reasonable time
large_exp = 10**18
start = time.perf_counter()
result = mod_exp_fast(2, large_exp, 1_000_000_007)
elapsed = time.perf_counter() - start
print(f"\n  2^(10^18) mod 10^9+7 = {result}")
print(f"    Computed in {elapsed*1000:.3f} ms using fast exponentiation")
print(f"    Naive would take ~{large_exp / 1e9:.0f} seconds (≈ {large_exp / 1e9 / 3.15e7:.0f} years)")


# =============================================================================
# SECTION 3: Step-by-Step Trace of Fast Exponentiation
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 3: Step-by-Step Trace")
print("=" * 65)


def mod_exp_traced(base, exp, mod):
    """Same algorithm as mod_exp_fast, but prints each step."""
    print(f"\n  Computing {base}^{exp} mod {mod}")
    print(f"  exp in binary: {bin(exp)}")
    print(f"  {'Step':>6} {'exp':>10} {'bit':>5} {'base':>12} {'result':>12}")
    print(f"  {'-'*50}")

    if mod == 1:
        return 0

    result = 1
    base = base % mod
    step = 0

    while exp > 0:
        bit = exp % 2
        if bit == 1:
            result = (result * base) % mod
        print(f"  {step:>6} {exp:>10} {bit:>5} {base:>12} {result:>12}")
        base = (base * base) % mod
        exp //= 2
        step += 1

    return result


result = mod_exp_traced(3, 13, 50)
print(f"\n  Final result: {result}")
print(f"  Verification: 3^13 = {3**13}, mod 50 = {3**13 % 50}")


# =============================================================================
# SECTION 4: Applications — Why Modular Arithmetic Is Everywhere
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 4: Real-World Applications")
print("=" * 65)

# --- Application 1: Hash Table Index ---
print("\n--- Hash Tables ---")
print("  A hash table with N buckets maps keys to indices using:")
print("  index = hash(key) % N")
print()
table_size = 16
keys = ["alice", "bob", "charlie", "david", "eve"]
for key in keys:
    h = hash(key)  # Python's built-in hash
    index = h % table_size
    print(f"  hash('{key}') % {table_size} = {h} % {table_size} = {index}")
print("\n  The mod operation guarantees the index is in [0, N-1].")
print("  Without mod, the hash could be any integer — useless as an array index.")

# --- Application 2: RSA Key Concept ---
print("\n--- RSA Encryption (Simplified) ---")
print("  RSA relies on modular exponentiation being EASY to compute")
print("  but HARD to reverse (the discrete logarithm problem).")
print()

# Tiny RSA example (not secure — just for illustration)
p, q = 61, 53              # Two primes
n = p * q                   # Public modulus
phi = (p - 1) * (q - 1)    # Euler's totient
e = 17                      # Public exponent (must be coprime with phi)
# Private exponent: d such that e*d ≡ 1 (mod phi)
# We need the modular inverse of e mod phi
d = pow(e, -1, phi)         # Python 3.8+ supports modular inverse

message = 42
encrypted = mod_exp_fast(message, e, n)
decrypted = mod_exp_fast(encrypted, d, n)

print(f"  p = {p}, q = {q}, n = p*q = {n}")
print(f"  phi(n) = (p-1)(q-1) = {phi}")
print(f"  Public key:  (e={e}, n={n})")
print(f"  Private key: (d={d}, n={n})")
print(f"  Message:    {message}")
print(f"  Encrypted:  {message}^{e} mod {n} = {encrypted}")
print(f"  Decrypted:  {encrypted}^{d} mod {n} = {decrypted}")
print(f"  Round-trip correct? {message == decrypted}")
print()
print("  The security of RSA depends on the fact that factoring n = p*q")
print("  is computationally hard when p and q are large primes (~1024 bits each).")
print("  Without knowing p and q, you cannot compute phi(n), and without")
print("  phi(n), you cannot find the private key d.")

# --- Application 3: Checksum / ISBN ---
print("\n--- ISBN-10 Check Digit ---")
print("  ISBN-10 uses modular arithmetic to detect transcription errors.")
isbn_digits = [0, 3, 0, 6, 4, 0, 6, 1, 5]  # First 9 digits of "The C Programming Language"
weighted_sum = sum(d * w for d, w in zip(isbn_digits, range(1, 10)))
check_digit = weighted_sum % 11
print(f"  ISBN digits: {isbn_digits}")
print(f"  Weighted sum: {' + '.join(f'{d}*{w}' for d, w in zip(isbn_digits, range(1, 10)))}")
print(f"             = {weighted_sum}")
print(f"  Check digit: {weighted_sum} mod 11 = {check_digit}")
print(f"  Full ISBN: 0-306-40615-{check_digit if check_digit < 10 else 'X'}")


# =============================================================================
# SECTION 5: Modular Inverse — Division in Modular Arithmetic
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 5: Modular Inverse — 'Division' in Mod World")
print("=" * 65)

print("\n  In regular math: a / b = a * (1/b) = a * b^(-1)")
print("  In modular math: a / b (mod m) = a * b^(-1) (mod m)")
print("  where b^(-1) is the number x such that b*x ≡ 1 (mod m)")
print()
print("  b^(-1) mod m exists if and only if gcd(b, m) = 1")
print("  (b and m share no common factors).")


def extended_gcd(a, b):
    """Extended Euclidean Algorithm: find gcd(a,b) and coefficients x,y
    such that a*x + b*y = gcd(a,b).

    The modular inverse of a mod b is x (when gcd = 1).

    This is computed from scratch — no library calls.
    """
    if a == 0:
        return b, 0, 1

    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1

    return gcd, x, y


def mod_inverse(a, m):
    """Compute the modular inverse of a mod m using the Extended Euclidean Algorithm.

    Returns x such that (a * x) % m == 1, or None if no inverse exists.
    """
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        return None  # Inverse does not exist
    return x % m


# Demonstrate
print("\n--- Examples ---")
examples = [(3, 7), (17, 3120), (5, 12), (6, 12)]
for a_val, m_val in examples:
    inv = mod_inverse(a_val, m_val)
    if inv is not None:
        print(f"  {a_val}^(-1) mod {m_val} = {inv}   "
              f"(verify: {a_val} * {inv} mod {m_val} = {(a_val * inv) % m_val})")
    else:
        print(f"  {a_val}^(-1) mod {m_val} = DOES NOT EXIST  "
              f"(gcd({a_val}, {m_val}) = {extended_gcd(a_val, m_val)[0]} ≠ 1)")


# =============================================================================
# SECTION 6: Failure Modes — When Modular Arithmetic Bites You
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 6: Failure Modes")
print("=" * 65)

# Failure 1: Negative numbers and mod
print("\n--- Failure 1: Negative Numbers ---")
print("  Python's % always returns a non-negative result (for positive modulus).")
print("  C/C++/Java may return negative remainders!")
print(f"  Python: -7 % 3 = {-7 % 3}   (mathematically correct)")
print(f"  C/Java: -7 % 3 = {-7 - 3 * (-7 // 3)}  (may return -1)")
print("  Always add m and take mod again if porting from C: ((a % m) + m) % m")

# Failure 2: Modular division pitfall
print("\n--- Failure 2: Division Is Not Regular Division ---")
print("  (a / b) % m  ≠  (a % m) / (b % m)")
print("  You MUST use the modular inverse: (a * mod_inverse(b, m)) % m")
a_val, b_val, m_val = 20, 4, 7
wrong = ((a_val % m_val) // (b_val % m_val))
right = (a_val * mod_inverse(b_val, m_val)) % m_val
print(f"  20/4 mod 7: wrong way = {wrong}, correct way = {right}")
print(f"  Verify: 20/4 = 5, and 5 mod 7 = {5 % 7}")

# Failure 3: Overflow in intermediate multiplication
print("\n--- Failure 3: Intermediate Overflow ---")
print("  Even if the final result fits in 64 bits, intermediate")
print("  products can overflow. Always reduce mod at each step.")
print(f"  (10^18 * 10^18) mod (10^9+7):")
big_a = 10**18
big_m = 10**9 + 7
# Safe: reduce first
safe = ((big_a % big_m) * (big_a % big_m)) % big_m
print(f"    Safe (reduce first):  {safe}")
print("  In C/Java, (10^18 * 10^18) overflows a 64-bit int!")
print("  Python handles it, but the principle matters for other languages.")

print("\n" + "=" * 65)
print("KEY TAKEAWAYS:")
print("  1. (a op b) mod m = ((a mod m) op (b mod m)) mod m  for +, -, *")
print("  2. Modular exponentiation via repeated squaring: O(log exp)")
print("  3. This makes RSA, Diffie-Hellman, and hashing possible")
print("  4. Division requires modular inverse (Extended Euclidean Algorithm)")
print("  5. Always reduce mod at every step to prevent overflow")
print("  6. Watch out for negative remainders in C/Java")
print("=" * 65)
