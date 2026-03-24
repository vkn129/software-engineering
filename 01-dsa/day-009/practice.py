"""
Day 9: Practice -- GCD and Extended Euclidean Exercises
========================================================

Fill in the TODO sections. Run this file to check your answers.
Each function has a docstring explaining what to implement and
test cases that verify correctness.

Run: python practice.py
"""


# =============================================================================
# Exercise 1: Iterative GCD
# =============================================================================

def gcd_iterative(a, b):
    """Compute GCD(a, b) using the Euclidean algorithm, iteratively.

    Use the fact that GCD(a, b) = GCD(b, a mod b).
    Handle negative inputs by taking absolute values first.
    Handle zero: GCD(a, 0) = |a|, GCD(0, 0) = 0.

    Examples:
        gcd_iterative(48, 18) -> 6
        gcd_iterative(100, 75) -> 25
        gcd_iterative(17, 13) -> 1
        gcd_iterative(-12, 8) -> 4
        gcd_iterative(0, 5)   -> 5
    """
    # TODO: Implement this function
    # Hint: while b != 0: swap a, b = b, a % b
    pass


# =============================================================================
# Exercise 2: Recursive GCD
# =============================================================================

def gcd_recursive(a, b):
    """Compute GCD(a, b) using the Euclidean algorithm, recursively.

    Same logic as iterative but expressed as recursion.
    Base case: GCD(a, 0) = a.

    Examples:
        gcd_recursive(48, 18) -> 6
        gcd_recursive(252, 105) -> 21
        gcd_recursive(0, 0) -> 0
    """
    # TODO: Implement this function
    pass


# =============================================================================
# Exercise 3: Extended GCD
# =============================================================================

def extended_gcd(a, b):
    """Extended Euclidean Algorithm.

    Returns (gcd, x, y) such that a*x + b*y = gcd.

    Base case: GCD(a, 0) = a, with x=1, y=0.
    Recursive case: from GCD(b, a%b) = b*x1 + (a%b)*y1,
        derive x = y1, y = x1 - (a//b) * y1.

    Examples:
        extended_gcd(48, 18) -> (6, -1, 3)    # 48*(-1) + 18*3 = 6
        extended_gcd(35, 15) -> (5, 1, -2)    # 35*1 + 15*(-2) = 5
        extended_gcd(17, 13) -> (1, ?, ?)     # some x, y where 17x + 13y = 1
    """
    # TODO: Implement this function
    # Hint: recursive approach, unwind the coefficients at each step
    pass


# =============================================================================
# Exercise 4: Modular Inverse
# =============================================================================

def mod_inverse(a, m):
    """Find x such that (a * x) % m == 1.

    Uses the Extended Euclidean Algorithm.
    Returns the inverse in range [0, m-1].
    Raises ValueError if GCD(a, m) != 1.

    Examples:
        mod_inverse(3, 7)   -> 5   (because 3 * 5 = 15, 15 % 7 = 1)
        mod_inverse(7, 11)  -> 8   (because 7 * 8 = 56, 56 % 11 = 1)
        mod_inverse(4, 6)   -> ValueError (GCD(4,6) = 2, not 1)
    """
    # TODO: Implement this function
    # Hint: call extended_gcd, check if gcd == 1, return x % m
    pass


# =============================================================================
# Exercise 5: GCD of Multiple Numbers
# =============================================================================

def gcd_multiple(*args):
    """Compute GCD of multiple numbers.

    Uses the property that GCD(a, b, c) = GCD(GCD(a, b), c).

    Examples:
        gcd_multiple(12, 8, 6)     -> 2
        gcd_multiple(100, 75, 50)  -> 25
        gcd_multiple(17, 13, 7)    -> 1
        gcd_multiple(42)           -> 42
    """
    # TODO: Implement this function
    # Hint: fold gcd_iterative over all arguments
    pass


# =============================================================================
# Exercise 6: Coprimality Check
# =============================================================================

def are_coprime(a, b):
    """Check if two numbers are coprime (GCD = 1).

    Two numbers are coprime if they share no common factor other than 1.
    This is the condition needed for modular inverses to exist.

    Examples:
        are_coprime(8, 15)  -> True   (GCD = 1)
        are_coprime(12, 8)  -> False  (GCD = 4)
        are_coprime(1, n)   -> True   (for any n)
    """
    # TODO: Implement this function
    pass


# =============================================================================
# Exercise 7: Simple RSA Round-Trip
# =============================================================================

def rsa_keygen(p, q, e):
    """Generate RSA public and private keys.

    Given primes p, q and public exponent e:
    1. Compute n = p * q
    2. Compute phi_n = (p-1) * (q-1)
    3. Verify GCD(e, phi_n) = 1
    4. Compute d = mod_inverse(e, phi_n)
    5. Return ((e, n), (d, n))

    Examples:
        rsa_keygen(61, 53, 17) -> ((17, 3233), (2753, 3233))
    """
    # TODO: Implement this function
    pass


def rsa_encrypt(message, public_key):
    """Encrypt: ciphertext = message^e mod n.

    Examples:
        rsa_encrypt(42, (17, 3233)) -> some number
    """
    # TODO: Implement this function
    # Hint: use Python's built-in pow(base, exp, mod) for modular exponentiation
    pass


def rsa_decrypt(ciphertext, private_key):
    """Decrypt: message = ciphertext^d mod n.

    Examples:
        rsa_decrypt(encrypted_42, (2753, 3233)) -> 42
    """
    # TODO: Implement this function
    pass


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests and report results."""
    passed = 0
    failed = 0
    total = 0

    def check(name, got, expected):
        nonlocal passed, failed, total
        total += 1
        if got == expected:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name} -- expected {expected}, got {got}")

    def check_raises(name, func, *args, exception=ValueError):
        nonlocal passed, failed, total
        total += 1
        try:
            func(*args)
            failed += 1
            print(f"  FAIL: {name} -- expected {exception.__name__}, got no exception")
        except exception:
            passed += 1
            print(f"  PASS: {name}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {name} -- expected {exception.__name__}, got {type(e).__name__}")

    print("=" * 55)
    print("Running Day 9 Practice Tests")
    print("=" * 55)

    # Exercise 1: Iterative GCD
    print("\nExercise 1: Iterative GCD")
    check("gcd(48, 18)", gcd_iterative(48, 18), 6)
    check("gcd(100, 75)", gcd_iterative(100, 75), 25)
    check("gcd(17, 13)", gcd_iterative(17, 13), 1)
    check("gcd(-12, 8)", gcd_iterative(-12, 8), 4)
    check("gcd(0, 5)", gcd_iterative(0, 5), 5)
    check("gcd(5, 0)", gcd_iterative(5, 0), 5)
    check("gcd(0, 0)", gcd_iterative(0, 0), 0)

    # Exercise 2: Recursive GCD
    print("\nExercise 2: Recursive GCD")
    check("gcd_r(48, 18)", gcd_recursive(48, 18), 6)
    check("gcd_r(252, 105)", gcd_recursive(252, 105), 21)
    check("gcd_r(0, 0)", gcd_recursive(0, 0), 0)
    check("gcd_r(1, 1)", gcd_recursive(1, 1), 1)

    # Exercise 3: Extended GCD
    print("\nExercise 3: Extended GCD")
    for a, b in [(48, 18), (35, 15), (17, 13), (252, 105), (99, 78)]:
        result = extended_gcd(a, b)
        if result is not None:
            gcd, x, y = result
            bezout_ok = (a * x + b * y == gcd)
            check(f"ext_gcd({a},{b}) bezout", bezout_ok, True)
        else:
            check(f"ext_gcd({a},{b})", result, "not None")

    # Exercise 4: Modular Inverse
    print("\nExercise 4: Modular Inverse")
    check("inv(3, 7)", mod_inverse(3, 7), 5)
    check("inv(7, 11)", mod_inverse(7, 11), 8)
    check("inv(5, 12)", mod_inverse(5, 12), 5)

    # Verify inverses actually work
    for a, m in [(3, 7), (7, 11), (5, 12)]:
        inv = mod_inverse(a, m)
        if inv is not None:
            check(f"  verify {a}*{inv} mod {m}=1", (a * inv) % m, 1)

    check_raises("inv(4, 6) raises", mod_inverse, 4, 6)
    check_raises("inv(6, 9) raises", mod_inverse, 6, 9)

    # Exercise 5: GCD of Multiple Numbers
    print("\nExercise 5: GCD Multiple")
    check("gcd(12,8,6)", gcd_multiple(12, 8, 6), 2)
    check("gcd(100,75,50)", gcd_multiple(100, 75, 50), 25)
    check("gcd(17,13,7)", gcd_multiple(17, 13, 7), 1)
    check("gcd(42)", gcd_multiple(42), 42)

    # Exercise 6: Coprimality
    print("\nExercise 6: Coprimality")
    check("coprime(8,15)", are_coprime(8, 15), True)
    check("coprime(12,8)", are_coprime(12, 8), False)
    check("coprime(1,100)", are_coprime(1, 100), True)
    check("coprime(13,17)", are_coprime(13, 17), True)

    # Exercise 7: RSA Round-Trip
    print("\nExercise 7: RSA Round-Trip")
    keys = rsa_keygen(61, 53, 17)
    if keys is not None:
        pub, priv = keys
        check("public key", pub, (17, 3233))
        check("private key", priv, (2753, 3233))

        for msg in [42, 100, 7, 0, 3000]:
            ct = rsa_encrypt(msg, pub)
            pt = rsa_decrypt(ct, priv)
            check(f"  RSA round-trip msg={msg}", pt, msg)

    # Summary
    print(f"\n{'=' * 55}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    if failed == 0:
        print("All tests passed!")
    else:
        print(f"{failed} test(s) need attention.")
    print("=" * 55)


# =============================================================================
# SOLUTIONS (uncomment to verify tests pass)
# =============================================================================

"""
def gcd_iterative(a, b):
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a

def gcd_recursive(a, b):
    a, b = abs(a), abs(b)
    if b == 0:
        return a
    return gcd_recursive(b, a % b)

def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd, x, y

def mod_inverse(a, m):
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError(f"No inverse: GCD({a},{m})={gcd}")
    return x % m

def gcd_multiple(*args):
    result = args[0]
    for val in args[1:]:
        result = gcd_iterative(result, val)
    return result

def are_coprime(a, b):
    return gcd_iterative(a, b) == 1

def rsa_keygen(p, q, e):
    n = p * q
    phi_n = (p - 1) * (q - 1)
    d = mod_inverse(e, phi_n)
    return (e, n), (d, n)

def rsa_encrypt(message, public_key):
    e, n = public_key
    return pow(message, e, n)

def rsa_decrypt(ciphertext, private_key):
    d, n = private_key
    return pow(ciphertext, d, n)
"""


if __name__ == "__main__":
    run_tests()
