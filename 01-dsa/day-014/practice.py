"""
Day 14 Practice: Mathematical Toolkit (Mini-project)
=====================================================

These exercises apply number theory tools to real cryptographic and
combinatorial problems. You will implement simplified RSA, count
derangements, and solve systems of modular equations.

No external libraries -- everything from first principles.

Fill in the TODO sections. Run this file to check your answers.

Run: python practice.py
"""

import random


# =============================================================================
# Shared Utilities (you may use these in your solutions)
# =============================================================================

def gcd(a, b):
    """Euclidean algorithm: gcd(a, b) = gcd(b, a % b) until b == 0.

    Why this works: if d divides both a and b, then d also divides
    a % b = a - (a // b) * b. So the set of common divisors is preserved
    at each step, and the algorithm terminates because a % b < b.
    """
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """Return (g, x, y) such that a*x + b*y = g = gcd(a, b).

    This is the foundation of modular inverses: if gcd(a, m) = 1, then
    a*x + m*y = 1, so a*x === 1 (mod m), meaning x is the inverse of a mod m.
    """
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def mod_inverse(a, m):
    """Find x such that a*x === 1 (mod m). Requires gcd(a, m) == 1."""
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"No inverse: gcd({a}, {m}) = {g}")
    return x % m


def is_prime(n):
    """Simple trial division primality test (sufficient for small numbers)."""
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


def find_prime(low, high):
    """Find a random prime in [low, high] by trial."""
    while True:
        p = random.randint(low, high)
        if is_prime(p):
            return p


# =============================================================================
# Exercise 1: Simplified RSA
# =============================================================================

def rsa_generate_keys(p, q):
    """Generate RSA public and private keys from two primes p, q.

    RSA key generation:
    1. Compute n = p * q
    2. Compute phi(n) = (p-1)*(q-1)  -- Euler's totient
       Why? The integers coprime to n = p*q are exactly those not divisible
       by p or q. By inclusion-exclusion: n - n/p - n/q + n/(p*q) = (p-1)(q-1).
    3. Choose e such that 1 < e < phi(n) and gcd(e, phi(n)) = 1.
       Common choice: e = 65537 (Fermat prime, fast exponentiation).
    4. Compute d = e^(-1) mod phi(n)  -- the private key exponent.
       d exists because gcd(e, phi(n)) = 1.

    Returns:
        dict with:
        - 'public_key': (e, n)
        - 'private_key': (d, n)
        - 'p': p, 'q': q, 'phi_n': phi(n)

    TODO: Implement key generation.
    """
    # TODO: Compute n and phi(n)
    n = 0  # FIX THIS
    phi_n = 0  # FIX THIS

    # TODO: Choose e. Start with 65537, fall back to smaller if gcd != 1
    e = 0  # FIX THIS
    # Hint: try e = 65537, if gcd(e, phi_n) != 1, try e = 3, 5, 7, ...

    # TODO: Compute d = modular inverse of e mod phi_n
    d = 0  # FIX THIS

    return {
        'public_key': (e, n),
        'private_key': (d, n),
        'p': p,
        'q': q,
        'phi_n': phi_n,
    }


def rsa_encrypt(message, public_key):
    """Encrypt an integer message using RSA.

    RSA encryption: ciphertext = message^e mod n

    Why this works: by Euler's theorem, m^(phi(n)) === 1 (mod n) for
    m coprime to n. Since e*d === 1 (mod phi(n)), we have e*d = 1 + k*phi(n)
    for some k, so m^(e*d) = m * (m^phi(n))^k === m * 1^k = m (mod n).
    Decrypting undoes encrypting.

    Args:
        message: integer in [0, n)
        public_key: (e, n)

    Returns:
        ciphertext integer

    TODO: Implement encryption.
    """
    e, n = public_key
    # TODO: Return message^e mod n
    return 0  # FIX THIS


def rsa_decrypt(ciphertext, private_key):
    """Decrypt a ciphertext using RSA.

    RSA decryption: message = ciphertext^d mod n

    Args:
        ciphertext: encrypted integer
        private_key: (d, n)

    Returns:
        original message integer

    TODO: Implement decryption.
    """
    d, n = private_key
    # TODO: Return ciphertext^d mod n
    return 0  # FIX THIS


# =============================================================================
# Exercise 2: Counting Derangements (Inclusion-Exclusion)
# =============================================================================

def count_derangements(n):
    """Count derangements of n elements using inclusion-exclusion.

    A derangement is a permutation where no element appears in its original
    position. For example, [2,3,1] is a derangement of [1,2,3], but
    [2,1,3] is not (3 is in position 3).

    By inclusion-exclusion:
    D(n) = n! * sum_{k=0}^{n} (-1)^k / k!

    Why inclusion-exclusion? Let A_i = {permutations fixing element i}.
    We want |complement of union of A_i|.
    |A_{i1} intersect ... intersect A_{ik}| = (n-k)! (the remaining n-k
    elements can be in any order).
    By inclusion-exclusion:
    D(n) = sum_{k=0}^{n} (-1)^k * C(n,k) * (n-k)! = n! * sum (-1)^k / k!

    Returns:
        dict with:
        - 'count': number of derangements D(n)
        - 'total_permutations': n!
        - 'probability': D(n) / n! (approaches 1/e as n grows)
        - 'one_over_e': 1/e for comparison

    TODO: Implement using the formula above. Use integer arithmetic for count.
    """
    # TODO: Compute n! (factorial)
    factorial_n = 0  # FIX THIS

    # TODO: Compute D(n) = n! * sum_{k=0}^{n} (-1)^k / k!
    # For exact integer arithmetic, rewrite as:
    # D(n) = sum_{k=0}^{n} (-1)^k * n! / k!
    # Note: n!/k! = n * (n-1) * ... * (k+1), always an integer.
    derangements = 0  # FIX THIS

    probability = derangements / factorial_n if factorial_n > 0 else 0

    import math
    return {
        'count': derangements,
        'total_permutations': factorial_n,
        'probability': probability,
        'one_over_e': 1.0 / math.e,
    }


# =============================================================================
# Exercise 3: Chinese Remainder Theorem Solver
# =============================================================================

def chinese_remainder_theorem(remainders, moduli):
    """Solve a system of simultaneous congruences using CRT.

    Given:
        x === r_1 (mod m_1)
        x === r_2 (mod m_2)
        ...
        x === r_k (mod m_k)

    Where all m_i are pairwise coprime, find the unique x mod (m_1*m_2*...*m_k).

    CRT construction:
    1. M = product of all moduli
    2. For each i: M_i = M / m_i
    3. For each i: y_i = M_i^(-1) mod m_i  (exists because gcd(M_i, m_i) = 1)
    4. x = sum(r_i * M_i * y_i) mod M

    Why this works: the term r_i * M_i * y_i contributes r_i mod m_i
    (since M_i * y_i === 1 mod m_i) and contributes 0 mod m_j for j != i
    (since M_i is divisible by m_j).

    Args:
        remainders: list of r_i values
        moduli: list of m_i values (must be pairwise coprime)

    Returns:
        dict with:
        - 'solution': the unique x in [0, M)
        - 'modulus': M (product of all moduli)
        - 'verification': list of x % m_i values (should equal remainders)

    TODO: Implement the CRT construction.
    """
    # TODO: Compute M = product of all moduli
    M = 0  # FIX THIS

    # TODO: For each equation, compute M_i, y_i, accumulate x
    x = 0  # FIX THIS

    # TODO: Reduce x modulo M
    solution = 0  # FIX THIS

    return {
        'solution': solution,
        'modulus': M,
        'verification': [solution % m for m in moduli],
    }


# =============================================================================
# Exercise 4: System of Modular Equations
# =============================================================================

def solve_modular_system(equations):
    """Solve a system of modular equations, handling non-coprime moduli.

    Each equation is (remainder, modulus): x === remainder (mod modulus).

    When moduli are not pairwise coprime, CRT does not directly apply.
    Strategy: reduce each equation to prime-power moduli, check consistency,
    then apply CRT on the reduced system.

    Simpler approach for this exercise: iteratively merge pairs of equations.
    Given x === r1 (mod m1) and x === r2 (mod m2):
    - x = r1 + k*m1 for some integer k
    - Substituting: r1 + k*m1 === r2 (mod m2)
    - So: k*m1 === (r2 - r1) (mod m2)
    - This has a solution iff gcd(m1, m2) divides (r2 - r1)
    - If solvable, find k and produce a single merged equation

    Args:
        equations: list of (remainder, modulus) tuples

    Returns:
        dict with:
        - 'solution': x (smallest non-negative), or None if inconsistent
        - 'modulus': combined modulus, or None if inconsistent
        - 'consistent': bool

    TODO: Implement iterative merging.
    """
    if not equations:
        return {'solution': 0, 'modulus': 1, 'consistent': True}

    # Start with the first equation
    r, m = equations[0]
    r = r % m

    for r2, m2 in equations[1:]:
        r2 = r2 % m2

        # TODO: Merge (r, m) with (r2, m2)
        # Step 1: Compute g = gcd(m, m2)
        # Step 2: Check if (r2 - r) % g == 0. If not, system is inconsistent.
        # Step 3: Solve k * (m // g) === (r2 - r) // g (mod m2 // g)
        #         using modular inverse
        # Step 4: New r = r + k * m, new m = lcm(m, m2) = m * m2 // g
        pass  # FIX THIS

    return {
        'solution': r % m,
        'modulus': m,
        'consistent': True,
    }


# =============================================================================
# Reference Solutions (scroll down after attempting!)
# =============================================================================
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# SPOILER SPACE -- try the exercises before looking below!
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#


def _solution_1_rsa(p, q):
    n = p * q
    phi_n = (p - 1) * (q - 1)

    # Choose e coprime to phi_n. 65537 is standard; fall back if needed.
    e = 65537
    if gcd(e, phi_n) != 1:
        # Find smallest e > 1 coprime to phi_n
        for candidate in range(3, phi_n, 2):
            if gcd(candidate, phi_n) == 1:
                e = candidate
                break

    d = mod_inverse(e, phi_n)

    return {
        'public_key': (e, n),
        'private_key': (d, n),
        'p': p, 'q': q, 'phi_n': phi_n,
    }


def _solution_1_encrypt(message, public_key):
    e, n = public_key
    return pow(message, e, n)


def _solution_1_decrypt(ciphertext, private_key):
    d, n = private_key
    return pow(ciphertext, d, n)


def _solution_2_derangements(n):
    # Compute n!
    factorial_n = 1
    for i in range(2, n + 1):
        factorial_n *= i

    # D(n) = sum_{k=0}^{n} (-1)^k * n! / k!
    # Compute using integer arithmetic to avoid floating point
    derangements = 0
    k_factorial = 1
    for k in range(n + 1):
        if k > 0:
            k_factorial *= k
        # n!/k! is always an integer
        term = factorial_n // k_factorial
        if k % 2 == 0:
            derangements += term
        else:
            derangements -= term

    import math
    probability = derangements / factorial_n if factorial_n > 0 else 0
    return {
        'count': derangements,
        'total_permutations': factorial_n,
        'probability': probability,
        'one_over_e': 1.0 / math.e,
    }


def _solution_3_crt(remainders, moduli):
    M = 1
    for m in moduli:
        M *= m

    x = 0
    for r_i, m_i in zip(remainders, moduli):
        M_i = M // m_i
        y_i = mod_inverse(M_i, m_i)
        x += r_i * M_i * y_i

    solution = x % M
    return {
        'solution': solution,
        'modulus': M,
        'verification': [solution % m for m in moduli],
    }


def _solution_4_modular_system(equations):
    if not equations:
        return {'solution': 0, 'modulus': 1, 'consistent': True}

    r, m = equations[0]
    r = r % m

    for r2, m2 in equations[1:]:
        r2 = r2 % m2
        g = gcd(m, m2)

        # Consistency check: the two congruences can only agree if
        # r and r2 are equal modulo their gcd
        if (r2 - r) % g != 0:
            return {'solution': None, 'modulus': None, 'consistent': False}

        # Solve: k * (m/g) === (r2 - r)/g  (mod m2/g)
        m_reduced = m // g
        m2_reduced = m2 // g
        diff_reduced = (r2 - r) // g
        k = (diff_reduced * mod_inverse(m_reduced, m2_reduced)) % m2_reduced

        # Merge into single equation
        new_m = m * m2 // g  # lcm(m, m2)
        r = (r + k * m) % new_m
        m = new_m

    return {
        'solution': r % m,
        'modulus': m,
        'consistent': True,
    }


# =============================================================================
# Self-check
# =============================================================================

def run_checks():
    print("=" * 70)
    print("DAY 14 PRACTICE -- Checking your solutions")
    print("=" * 70)

    # Exercise 1: RSA
    print("\n--- Exercise 1: Simplified RSA ---")
    p, q = 61, 53  # small primes for testing
    keys = rsa_generate_keys(p, q)
    if keys['public_key'][0] == 0:
        print("  NOT YET IMPLEMENTED")
    else:
        e, n = keys['public_key']
        d, _ = keys['private_key']
        print(f"  p={p}, q={q}, n={n}, phi={keys['phi_n']}")
        print(f"  Public key e={e}, Private key d={d}")

        # Test encrypt/decrypt round-trip
        test_messages = [42, 100, 0, 1, n - 1]
        all_pass = True
        for msg in test_messages:
            ct = rsa_encrypt(msg, keys['public_key'])
            pt = rsa_decrypt(ct, keys['private_key'])
            if pt != msg:
                print(f"  FAIL: encrypt({msg}) -> {ct} -> decrypt -> {pt} (expected {msg})")
                all_pass = False
        if all_pass:
            print("  PASS: All messages encrypt and decrypt correctly!")
        else:
            print("  Some round-trips failed.")

    # Exercise 2: Derangements
    print("\n--- Exercise 2: Counting Derangements ---")
    # Known values: D(0)=1, D(1)=0, D(2)=1, D(3)=2, D(4)=9, D(5)=44
    known = {0: 1, 1: 0, 2: 1, 3: 2, 4: 9, 5: 44}
    result = count_derangements(5)
    if result['count'] == 0 and result['total_permutations'] == 0:
        print("  NOT YET IMPLEMENTED")
    else:
        all_pass = True
        for n_val, expected in known.items():
            r = count_derangements(n_val)
            if r['count'] != expected:
                print(f"  FAIL: D({n_val}) = {r['count']}, expected {expected}")
                all_pass = False
        if all_pass:
            print("  PASS: All derangement counts correct!")
        r10 = count_derangements(10)
        print(f"  D(10)/10! = {r10['probability']:.10f}")
        print(f"  1/e       = {r10['one_over_e']:.10f}")
        print(f"  (These converge rapidly -- that is the derangement limit theorem)")

    # Exercise 3: Chinese Remainder Theorem
    print("\n--- Exercise 3: Chinese Remainder Theorem ---")
    # Classic example: x === 2 (mod 3), x === 3 (mod 5), x === 2 (mod 7)
    result = chinese_remainder_theorem([2, 3, 2], [3, 5, 7])
    if result['solution'] == 0 and result['modulus'] == 0:
        print("  NOT YET IMPLEMENTED")
    else:
        print(f"  x === 2 (mod 3), x === 3 (mod 5), x === 2 (mod 7)")
        print(f"  Solution: x = {result['solution']} (mod {result['modulus']})")
        print(f"  Verification: {result['verification']}")
        if result['verification'] == [2, 3, 2]:
            print("  PASS: Solution satisfies all congruences!")
        else:
            print("  FAIL: Verification does not match remainders.")

        # Second test: x === 1 (mod 2), x === 2 (mod 3), x === 3 (mod 5)
        r2 = chinese_remainder_theorem([1, 2, 3], [2, 3, 5])
        print(f"  x === 1 (mod 2), x === 2 (mod 3), x === 3 (mod 5)")
        print(f"  Solution: x = {r2['solution']} (mod {r2['modulus']})")
        if r2['verification'] == [1, 2, 3]:
            print("  PASS!")
        else:
            print("  FAIL")

    # Exercise 4: Modular System (non-coprime moduli)
    print("\n--- Exercise 4: System of Modular Equations ---")
    # Coprime case (should work like CRT)
    r1 = solve_modular_system([(2, 3), (3, 5), (2, 7)])
    # Non-coprime but consistent: x === 3 (mod 6), x === 5 (mod 10)
    # gcd(6,10)=2, 3 === 5 (mod 2)? 3%2=1, 5%2=1, yes consistent
    r2 = solve_modular_system([(3, 6), (5, 10)])
    # Inconsistent: x === 1 (mod 4), x === 3 (mod 6)
    # gcd(4,6)=2, 1%2=1, 3%2=1, consistent; solve further...
    # Actually: 1 mod 2 = 1, 3 mod 2 = 1, so consistent
    r3 = solve_modular_system([(1, 4), (3, 6)])
    # Truly inconsistent: x === 1 (mod 4), x === 0 (mod 2)
    # gcd(4,2)=2, (0-1)%2 = 1 != 0, inconsistent
    r4 = solve_modular_system([(1, 4), (0, 2)])

    if r1['solution'] is None and r1['modulus'] is None:
        print("  NOT YET IMPLEMENTED")
    else:
        print(f"  System 1 (coprime): x = {r1['solution']} (mod {r1['modulus']})")
        if r1['solution'] is not None and r1['solution'] % 3 == 2 and r1['solution'] % 5 == 3:
            print("  PASS!")
        else:
            print("  FAIL")

        print(f"  System 2 (non-coprime, consistent): x = {r2['solution']} (mod {r2['modulus']})")
        if r2['solution'] is not None and r2['solution'] % 6 == 3 and r2['solution'] % 10 == 5:
            print("  PASS!")
        else:
            print("  FAIL")

        print(f"  System 3 (non-coprime, consistent): x = {r3['solution']} (mod {r3['modulus']})")
        if r3['solution'] is not None and r3['solution'] % 4 == 1 and r3['solution'] % 6 == 3:
            print("  PASS!")
        else:
            print("  FAIL")

        print(f"  System 4 (inconsistent): consistent = {r4['consistent']}")
        if not r4['consistent']:
            print("  PASS: Correctly detected inconsistency!")
        else:
            print("  FAIL: Should be inconsistent (1 mod 4 vs 0 mod 2)")


if __name__ == "__main__":
    run_checks()
