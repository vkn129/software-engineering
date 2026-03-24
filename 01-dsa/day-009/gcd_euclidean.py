"""
Day 9: GCD, Extended Euclidean Algorithm -- Why These Matter for RSA
=====================================================================

This file demonstrates the Euclidean algorithm family from first principles.
We start with the naive approach, show why it's slow, then build up to the
Extended Euclidean Algorithm and use it to implement a toy RSA system.

Run: python gcd_euclidean.py
"""


# =============================================================================
# SECTION 1: The Naive Approach (and why it's terrible)
# =============================================================================

print("=" * 65)
print("SECTION 1: Naive GCD -- Why We Need Something Better")
print("=" * 65)


def gcd_naive(a, b):
    """Find GCD by checking every possible divisor from min(a,b) down to 1.

    This is O(min(a,b)) -- fine for small numbers, catastrophic for large ones.
    For RSA-sized numbers (600+ digits), this would take longer than the age
    of the universe.
    """
    if a == 0:
        return b
    if b == 0:
        return a
    a, b = abs(a), abs(b)
    result = 1
    for d in range(1, min(a, b) + 1):
        if a % d == 0 and b % d == 0:
            result = d
    return result


# Demonstrate correctness on small numbers
pairs = [(12, 8), (48, 18), (100, 75), (17, 13), (0, 5), (7, 0)]
print(f"\n{'a':>6} {'b':>6} {'GCD':>6}")
print("-" * 22)
for a, b in pairs:
    print(f"{a:>6} {b:>6} {gcd_naive(a, b):>6}")

# Show why naive is impractical
import time

print("\nTiming naive GCD for growing inputs:")
for size in [1000, 10000, 100000]:
    start = time.perf_counter()
    result = gcd_naive(size, size - 1)
    elapsed = time.perf_counter() - start
    # Consecutive integers are always coprime (GCD = 1)
    print(f"  GCD({size}, {size-1}) = {result}  [{elapsed*1000:.2f} ms]")

print("\nNotice: time grows linearly with input size.")
print("For a 300-digit number, this would take ~10^290 years. Not useful.")


# =============================================================================
# SECTION 2: The Euclidean Algorithm
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 2: The Euclidean Algorithm -- 2300 Years Old, Still Fast")
print("=" * 65)


def gcd_euclidean_recursive(a, b):
    """Euclid's algorithm, recursive form.

    Core insight: GCD(a, b) = GCD(b, a mod b).
    Why? Any common divisor of a and b also divides (a mod b),
    and vice versa. So the set of common divisors is preserved.

    Terminates when b = 0, because GCD(a, 0) = a.
    """
    if b == 0:
        return a
    return gcd_euclidean_recursive(b, a % b)


def gcd_euclidean_iterative(a, b):
    """Euclid's algorithm, iterative form.

    Identical logic, but avoids recursion depth limits.
    This is the production-ready version.
    """
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a


# Show step-by-step execution to build intuition
def gcd_with_trace(a, b):
    """Show each step of the Euclidean algorithm."""
    print(f"  Computing GCD({a}, {b}):")
    step = 1
    while b != 0:
        q, r = a // b, a % b
        print(f"    Step {step}: {a} = {q} * {b} + {r}")
        a, b = b, r
        step += 1
    print(f"    -> GCD = {a}")
    return a


print()
gcd_with_trace(48, 18)
print()
gcd_with_trace(252, 105)

# Why is it fast? The Fibonacci numbers are the worst case.
# GCD(F_n, F_{n-1}) takes n steps, and F_n grows exponentially.
# So the number of steps is O(log(min(a,b))).
print("\nWorst case: consecutive Fibonacci numbers (maximizes steps)")


def fibonacci(n):
    """Generate nth Fibonacci number."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


for n in [10, 20, 30, 40]:
    fn = fibonacci(n)
    fn1 = fibonacci(n - 1)
    start = time.perf_counter()
    result = gcd_euclidean_iterative(fn, fn1)
    elapsed = time.perf_counter() - start
    # Consecutive Fibonacci numbers are always coprime
    print(f"  GCD(F_{n}, F_{n-1}) = GCD({fn}, {fn1}) = {result}  "
          f"[{elapsed*1_000_000:.1f} µs]")

# Compare speed with naive
print("\nSpeed comparison -- Euclidean vs Naive:")
for size in [1000, 10000, 100000]:
    start = time.perf_counter()
    gcd_euclidean_iterative(size, size - 1)
    fast = time.perf_counter() - start

    start = time.perf_counter()
    gcd_naive(size, size - 1)
    slow = time.perf_counter() - start

    speedup = slow / fast if fast > 0 else float('inf')
    print(f"  n={size:>6}: Euclidean {fast*1_000_000:>8.1f} µs, "
          f"Naive {slow*1000:>8.2f} ms  ({speedup:.0f}x faster)")


# =============================================================================
# SECTION 3: Bezout's Identity and Extended Euclidean Algorithm
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 3: Extended Euclidean -- Finding Bezout Coefficients")
print("=" * 65)

print("""
Bezout's Identity: for any integers a, b, there exist integers x, y such that:
    a*x + b*y = GCD(a, b)

This is powerful because it means GCD is not just a number -- it's a number
that can be "reached" by combining a and b. The Extended Euclidean Algorithm
finds x and y.
""")


def extended_gcd(a, b):
    """Extended Euclidean Algorithm.

    Returns (gcd, x, y) such that a*x + b*y = gcd.

    We work backwards through the Euclidean algorithm steps.
    At each step, we express the current remainder as a linear
    combination of the original a and b.

    Base case: GCD(a, 0) = a = a*1 + 0*0, so x=1, y=0.
    Recursive step: if b*x1 + (a%b)*y1 = gcd, then
        a*y1 + b*(x1 - (a//b)*y1) = gcd
    """
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y


def extended_gcd_iterative(a, b):
    """Iterative version of Extended Euclidean Algorithm.

    Uses two pairs of coefficients, updated at each step.
    This avoids recursion and is the version used in practice.
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    # old_r = gcd, old_s = x, old_t = y
    return old_r, old_s, old_t


# Demonstrate with trace
def extended_gcd_with_trace(a, b):
    """Show the extended GCD computation step by step."""
    print(f"\n  Extended GCD({a}, {b}):")

    gcd, x, y = extended_gcd(a, b)

    print(f"    Result: GCD = {gcd}")
    print(f"    Bezout coefficients: x = {x}, y = {y}")
    print(f"    Verification: {a}*{x} + {b}*{y} = {a*x + b*y}")
    assert a * x + b * y == gcd, "Bezout's identity violated!"
    return gcd, x, y


extended_gcd_with_trace(48, 18)
extended_gcd_with_trace(35, 15)
extended_gcd_with_trace(252, 105)
extended_gcd_with_trace(17, 13)

# Verify iterative matches recursive
print("\n  Verifying iterative == recursive:")
test_pairs = [(48, 18), (35, 15), (252, 105), (17, 13), (99, 78), (1, 1)]
for a, b in test_pairs:
    r1 = extended_gcd(a, b)
    r2 = extended_gcd_iterative(a, b)
    assert r1[0] == r2[0], f"GCD mismatch for ({a}, {b})"
    # Coefficients might differ (multiple valid solutions), but equation holds
    assert a * r2[1] + b * r2[2] == r2[0], f"Bezout violated for ({a}, {b})"
    print(f"    ({a:>3}, {b:>3}): GCD={r1[0]}, "
          f"recursive=({r1[1]},{r1[2]}), iterative=({r2[1]},{r2[2]})  ✓")


# =============================================================================
# SECTION 4: Modular Multiplicative Inverse
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 4: Modular Multiplicative Inverse")
print("=" * 65)

print("""
The modular inverse of a (mod m) is a number x such that:
    a * x ≡ 1 (mod m)

It exists if and only if GCD(a, m) = 1 (a and m are coprime).

To find it: solve a*x + m*y = 1 using Extended GCD, then x mod m is the answer.
""")


def mod_inverse(a, m):
    """Find the modular multiplicative inverse of a modulo m.

    Returns x such that (a * x) % m == 1.
    Raises ValueError if the inverse does not exist (when GCD(a,m) != 1).

    Why this matters: RSA private key computation requires this.
    """
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError(f"Modular inverse does not exist: GCD({a}, {m}) = {gcd}")
    # x might be negative; take mod m to get the positive representative
    return x % m


# Demonstrate
print("Finding modular inverses:")
test_cases = [(3, 7), (7, 11), (5, 12), (17, 43), (65537, 3233)]
for a, m in test_cases:
    try:
        inv = mod_inverse(a, m)
        verify = (a * inv) % m
        print(f"  {a}^(-1) mod {m} = {inv}   "
              f"(verify: {a} * {inv} = {a*inv}, mod {m} = {verify})")
    except ValueError as e:
        print(f"  {e}")

# Show when inverse doesn't exist
print("\nWhen inverse does NOT exist (GCD != 1):")
no_inverse_cases = [(4, 8), (6, 9), (10, 15)]
for a, m in no_inverse_cases:
    try:
        mod_inverse(a, m)
    except ValueError as e:
        print(f"  {e}")


# =============================================================================
# SECTION 5: Mini-RSA Implementation
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 5: Mini-RSA -- GCD in Action")
print("=" * 65)

print("""
RSA Algorithm (simplified with small primes for demonstration):
1. Choose two primes p and q
2. Compute n = p * q (the modulus)
3. Compute φ(n) = (p-1)(q-1) (Euler's totient)
4. Choose e coprime to φ(n) (public exponent)
5. Compute d = e^(-1) mod φ(n) (private exponent) ← Extended GCD!
6. Public key: (e, n), Private key: (d, n)
7. Encrypt: ciphertext = message^e mod n
8. Decrypt: message = ciphertext^d mod n
""")


def is_prime(n):
    """Simple primality test. We'll build better ones on Day 11."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def generate_rsa_keys(p, q, e=None):
    """Generate RSA public and private keys from two primes.

    Returns ((e, n), (d, n)) = (public_key, private_key).
    """
    assert is_prime(p) and is_prime(q), "p and q must be prime"
    assert p != q, "p and q must be different primes"

    n = p * q
    phi_n = (p - 1) * (q - 1)

    # Choose e: must be coprime to phi_n
    if e is None:
        # Try common choices: 65537 (standard), then 3, 5, 7, ...
        for candidate in [65537, 3, 5, 7, 11, 13, 17]:
            if gcd_euclidean_iterative(candidate, phi_n) == 1:
                e = candidate
                break

    assert gcd_euclidean_iterative(e, phi_n) == 1, \
        f"e={e} is not coprime to φ(n)={phi_n}"

    # Compute d = e^(-1) mod phi_n using Extended Euclidean
    d = mod_inverse(e, phi_n)

    print(f"  RSA Key Generation:")
    print(f"    p = {p}, q = {q}")
    print(f"    n = p * q = {n}")
    print(f"    φ(n) = (p-1)(q-1) = {phi_n}")
    print(f"    e = {e} (public exponent)")
    print(f"    GCD(e, φ(n)) = {gcd_euclidean_iterative(e, phi_n)} (must be 1)")
    print(f"    d = e^(-1) mod φ(n) = {d} (private exponent)")
    print(f"    Verify: e * d mod φ(n) = {(e * d) % phi_n} (must be 1)")
    print(f"    Public key:  (e={e}, n={n})")
    print(f"    Private key: (d={d}, n={n})")

    return (e, n), (d, n)


def rsa_encrypt(message, public_key):
    """Encrypt a number using RSA public key."""
    e, n = public_key
    assert 0 <= message < n, f"Message must be in [0, {n-1}]"
    return pow(message, e, n)  # Python's built-in modular exponentiation


def rsa_decrypt(ciphertext, private_key):
    """Decrypt a number using RSA private key."""
    d, n = private_key
    return pow(ciphertext, d, n)


# Demo with small primes
print("\n--- Demo 1: Small primes (p=61, q=53) ---")
pub, priv = generate_rsa_keys(61, 53, e=17)

messages = [42, 100, 7, 2021, 0]
print(f"\n  Encrypting and decrypting messages:")
print(f"  {'Message':>10} {'Encrypted':>12} {'Decrypted':>12} {'Match':>7}")
print("  " + "-" * 45)
for msg in messages:
    if msg < pub[1]:  # message must be < n
        ct = rsa_encrypt(msg, pub)
        pt = rsa_decrypt(ct, priv)
        print(f"  {msg:>10} {ct:>12} {pt:>12} {'Yes' if pt == msg else 'NO!':>7}")

# Demo with slightly larger primes
print(f"\n--- Demo 2: Larger primes (p=101, q=103) ---")
pub2, priv2 = generate_rsa_keys(101, 103, e=7)

print(f"\n  Encrypting and decrypting:")
for msg in [42, 999, 5000, 0]:
    if msg < pub2[1]:
        ct = rsa_encrypt(msg, pub2)
        pt = rsa_decrypt(ct, priv2)
        print(f"    {msg} -> encrypt -> {ct} -> decrypt -> {pt}  "
              f"{'OK' if pt == msg else 'FAIL'}")


# =============================================================================
# SECTION 6: GCD Properties and Edge Cases
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 6: GCD Properties and Edge Cases")
print("=" * 65)

# Property 1: GCD(a, 0) = a
print("\nProperty: GCD(a, 0) = a")
for a in [0, 1, 5, 42]:
    print(f"  GCD({a}, 0) = {gcd_euclidean_iterative(a, 0)}")

# Property 2: GCD(a, a) = a
print("\nProperty: GCD(a, a) = a")
for a in [1, 7, 100]:
    print(f"  GCD({a}, {a}) = {gcd_euclidean_iterative(a, a)}")

# Property 3: GCD is commutative
print("\nProperty: GCD(a, b) = GCD(b, a)")
for a, b in [(12, 8), (100, 75)]:
    g1 = gcd_euclidean_iterative(a, b)
    g2 = gcd_euclidean_iterative(b, a)
    print(f"  GCD({a}, {b}) = {g1}, GCD({b}, {a}) = {g2}  "
          f"{'Equal' if g1 == g2 else 'NOT EQUAL!'}")

# Property 4: Coprime numbers (GCD = 1)
print("\nCoprime pairs (GCD = 1) -- these are crucial for RSA:")
coprime_pairs = [(3, 7), (8, 15), (17, 31), (65537, 3120)]
for a, b in coprime_pairs:
    g = gcd_euclidean_iterative(a, b)
    print(f"  GCD({a}, {b}) = {g}  {'(coprime)' if g == 1 else ''}")

# Property 5: LCM relationship
print("\nRelationship: LCM(a, b) = a * b / GCD(a, b)")


def lcm(a, b):
    """Least Common Multiple via GCD. This avoids overflow in languages
    with fixed-size integers by dividing before multiplying."""
    return abs(a) // gcd_euclidean_iterative(a, b) * abs(b)


for a, b in [(12, 8), (6, 4), (15, 20)]:
    g = gcd_euclidean_iterative(a, b)
    l = lcm(a, b)
    print(f"  GCD({a}, {b}) = {g}, LCM({a}, {b}) = {l}, "
          f"product = {a*b}, GCD*LCM = {g*l}")


# =============================================================================
# SECTION 7: Failure Modes -- What Goes Wrong
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 7: Failure Modes")
print("=" * 65)

# Failure 1: Trying to find inverse when it doesn't exist
print("\nFailure 1: Modular inverse with non-coprime inputs")
print("  If GCD(a, m) != 1, no inverse exists.")
print("  In RSA, choosing e not coprime to φ(n) makes key generation impossible.")
try:
    mod_inverse(6, 9)
except ValueError as e:
    print(f"  Caught: {e}")

# Failure 2: Message too large for RSA modulus
print("\nFailure 2: RSA message >= n")
print("  RSA only works for messages in [0, n-1].")
print("  Real systems break messages into blocks smaller than n.")
print(f"  With n={pub[1]}, max message = {pub[1] - 1}")

# Failure 3: Choosing p = q
print("\nFailure 3: p = q breaks RSA security")
print("  If n = p^2, an attacker just computes sqrt(n) to find p.")
print("  RSA requires p != q and both must be large and random.")

# Failure 4: Small primes are insecure
print("\nFailure 4: Small primes can be factored trivially")
print(f"  Our demo n = {pub[1]} = 61 * 53")
print(f"  Real RSA uses n with 2048+ bits (617+ decimal digits)")
print(f"  Factoring such n would take billions of years with current algorithms.")


print("\n" + "=" * 65)
print("All demonstrations complete.")
print("=" * 65)
