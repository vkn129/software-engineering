"""
Day 154 Practice: Discrete Logarithm

6 exercises. Implement TODOs, then run: python practice.py

Exercise 1 is the O(n) baseline. Exercise 2 is the group order every later
algorithm needs. Exercises 3-4 build baby-step giant-step. Exercise 5 is
Pollard's rho. Exercise 6 is the payoff: breaking Diffie-Hellman.

Boundaries: day-150 owns fast exponentiation, day-151 owns extended Euclid and
modular inverse. Use `pow(g, x, p)` and `pow(a, -1, m)` — do not rewrite them.
"""

import math
import random


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: brute-force discrete log
# ---------------------------------------------------------------------------

def brute_force_log(g, h, p, n):
    """
    Smallest x in [0, n) with g^x = h (mod p), or None if there is none.
    O(n) multiplies, O(1) space. This is the bar the rest must clear.
    """
    # TODO: implement
    pass


def _sol_brute_force_log(g, h, p, n):
    h %= p
    y = 1
    for x in range(n):
        if y == h:
            return x
        y = (y * g) % p
    return None


# ---------------------------------------------------------------------------
# Exercise 2: multiplicative order
# ---------------------------------------------------------------------------

def multiplicative_order(g, p):
    """
    Smallest n > 0 with g^n = 1 (mod p), for prime p.

    Counting up is O(p). Lagrange says the order divides p-1: start at p-1 and
    strip each prime factor while the smaller exponent still kills g.
    """
    # TODO: implement using the prime factors of p-1
    pass


def _sol_prime_factors(n):
    out = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out.append(n)
    return out


def _sol_multiplicative_order(g, p):
    g %= p
    n = p - 1
    for q in _sol_prime_factors(p - 1):
        while n % q == 0 and pow(g, n // q, p) == 1:
            n //= q
    return n


# ---------------------------------------------------------------------------
# Exercise 3: the baby-step table
# ---------------------------------------------------------------------------

def baby_steps(g, p, m):
    """
    Return {g^j mod p: j} for j in [0, m).

    Keep the SMALLEST j per value — powers repeat when g has small order, and
    the smallest j gives the smallest valid logarithm.
    """
    # TODO: implement with m-1 multiplies, no pow() per entry
    pass


def _sol_baby_steps(g, p, m):
    table = {}
    y = 1
    for j in range(m):
        if y not in table:
            table[y] = j
        y = (y * g) % p
    return table


# ---------------------------------------------------------------------------
# Exercise 4: baby-step giant-step
# ---------------------------------------------------------------------------

def bsgs(g, h, p, n):
    """
    Solve g^x = h (mod p) for x in [0, n). None if h is not in <g>.

    x = i*m + j with m = ceil(sqrt(n)) turns g^x = h into
        g^j = h * (g^-m)^i
    Left side depends on j only, right on i only: tabulate one, walk the other.

    "No solution" is a real outcome — return None, never 0.
    """
    # TODO: implement in O(sqrt(n)) time and space
    pass


def _sol_bsgs(g, h, p, n):
    g %= p
    h %= p
    if h == 0:
        return None  # 0 is not in Z_p^*
    m = math.isqrt(n - 1) + 1 if n > 1 else 1  # ceil(sqrt(n))
    table = _sol_baby_steps(g, p, m)
    # pow(a, -1, p) is Python's spelling of day-151's extended Euclid.
    factor = pow(g, -m, p)
    gamma = h
    for i in range(m):
        j = table.get(gamma)
        if j is not None and i * m + j < n:
            return i * m + j
        gamma = (gamma * factor) % p
    return None


# ---------------------------------------------------------------------------
# Exercise 5: Pollard's rho for logarithms
# ---------------------------------------------------------------------------

def pollard_rho_log(g, h, p, n, seed=0):
    """
    Same O(sqrt n) time as BSGS but O(1) space. n must be the order of g; take
    it PRIME (a subgroup of a safe prime) so the gcd case cannot bite.

    Walk (x, a, b) keeping the invariant x = g^a * h^b, branch on x mod 3, and
    find a collision with Floyd's tortoise and hare. At a collision:
        a_t - a_h = x * (b_h - b_t)  (mod n)
    Restart from a fresh random (a0, b0) if b_h - b_t is 0 mod n.
    """
    # TODO: implement the walk + Floyd cycle detection
    pass


def _sol_rho_step(x, a, b, g, h, p, n):
    r = x % 3
    if r == 0:
        return (x * x) % p, (2 * a) % n, (2 * b) % n
    if r == 1:
        return (x * g) % p, (a + 1) % n, b
    return (x * h) % p, a, (b + 1) % n


def _sol_pollard_rho_log(g, h, p, n, seed=0):
    g %= p
    h %= p
    if h == 1:
        return 0
    rng = random.Random(seed)
    limit = 4 * math.isqrt(n) + 16  # a degenerate walk must not spin forever
    for _ in range(40):
        a0, b0 = rng.randrange(n), rng.randrange(n)
        start = (pow(g, a0, p) * pow(h, b0, p)) % p
        xt, at, bt = start, a0, b0
        xh, ah, bh = start, a0, b0
        for _ in range(limit):
            xt, at, bt = _sol_rho_step(xt, at, bt, g, h, p, n)
            xh, ah, bh = _sol_rho_step(xh, ah, bh, g, h, p, n)
            xh, ah, bh = _sol_rho_step(xh, ah, bh, g, h, p, n)
            if xt == xh:
                coeff = (bh - bt) % n
                if coeff == 0:
                    break  # collision carries no information — restart
                x = ((at - ah) * pow(coeff, -1, n)) % n
                if pow(g, x, p) == h:
                    return x
                break
    return None


# ---------------------------------------------------------------------------
# Exercise 6: break Diffie-Hellman
# ---------------------------------------------------------------------------

def break_dh(g, p, A, B, n):
    """
    Given only the public values, return the shared secret g^(ab) mod p.

    Eve needs ONE discrete log, not two: recover a from A = g^a, then compute
    B^a — exactly the arithmetic Alice does. Return None if a is unrecoverable.
    """
    # TODO: implement using bsgs
    pass


def _sol_break_dh(g, p, A, B, n):
    a = _sol_bsgs(g, A, p, n)
    if a is None:
        return None
    return pow(B, a, p)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    # p = 23 with g = 5 is a generator of Z_23^* (order 22).
    # 1019 = 2*509+1 and 1000000007 = 2*500000003+1 are safe primes.
    print("Exercise 1: brute_force_log")
    check("5^6 = 8 mod 23", try_or_sol("brute_force_log", 5, 8, 23, 22), 6)
    check("5^16 = 3 mod 23", try_or_sol("brute_force_log", 5, 3, 23, 22), 16)
    check("h=1 -> x=0", try_or_sol("brute_force_log", 5, 1, 23, 22), 0)
    check("5^2 = 2 mod 23", try_or_sol("brute_force_log", 5, 2, 23, 22), 2)

    print("\nExercise 2: multiplicative_order")
    check("order(5,23) = 22 (generator)",
          try_or_sol("multiplicative_order", 5, 23), 22)
    check("order(2,23) = 11", try_or_sol("multiplicative_order", 2, 23), 11)
    check("order(22,23) = 2 (-1)", try_or_sol("multiplicative_order", 22, 23), 2)
    check("order(1,23) = 1", try_or_sol("multiplicative_order", 1, 23), 1)
    check("order(2,1019) = 1018", try_or_sol("multiplicative_order", 2, 1019), 1018)
    check("order(4,1019) = 509 (subgroup)",
          try_or_sol("multiplicative_order", 4, 1019), 509)

    print("\nExercise 3: baby_steps")
    check("g=5,p=23,m=5", try_or_sol("baby_steps", 5, 23, 5),
          {1: 0, 5: 1, 2: 2, 10: 3, 4: 4})
    check("m=1 is just g^0", try_or_sol("baby_steps", 5, 23, 1), {1: 0})
    # g=2 mod 23 has order 11, so j=11 wraps back to 1 — smallest j must win.
    check("repeats keep smallest j", try_or_sol("baby_steps", 2, 23, 13)[1], 0)

    print("\nExercise 4: bsgs")
    check("5^6 = 8 mod 23", try_or_sol("bsgs", 5, 8, 23, 22), 6)
    check("5^16 = 3 mod 23", try_or_sol("bsgs", 5, 3, 23, 22), 16)
    check("h=1 -> 0", try_or_sol("bsgs", 5, 1, 23, 22), 0)
    check("h=0 -> None (not in Z_p^*)", try_or_sol("bsgs", 5, 0, 23, 22), None)
    # g=2 has order 11; 5 is not a power of 2 mod 23, so no logarithm exists.
    check("no solution -> None", try_or_sol("bsgs", 2, 5, 23, 11), None)
    # Round-trip: verify by re-exponentiating, not against a hardcoded answer.
    p, g, secret = 1019, 2, 777
    x = try_or_sol("bsgs", g, pow(g, secret, p), p, p - 1)
    check("round-trip p=1019 re-exponentiates", pow(g, x, p), pow(g, secret, p))
    check("round-trip p=1019 is exact", x, secret)
    p2, g2, secret2 = 1000000007, 5, 123456789
    x2 = try_or_sol("bsgs", g2, pow(g2, secret2, p2), p2, p2 - 1)
    check("round-trip p=1e9+7", x2, secret2)

    print("\nExercise 5: pollard_rho_log")
    # <4> mod 1019 is the prime-order-509 subgroup of a safe prime.
    q, gq = 509, 4
    for s in (1, 200, 508):
        got = try_or_sol("pollard_rho_log", gq, pow(gq, s, 1019), 1019, q)
        check(f"subgroup order 509, x={s}", got, s)
    # <4> mod 100043 has prime order 50021.
    q2, gq2 = 50021, 4
    got = try_or_sol("pollard_rho_log", gq2, pow(gq2, 31337, 100043), 100043, q2)
    check("subgroup order 50021, x=31337", got, 31337)
    check("h=1 -> 0", try_or_sol("pollard_rho_log", gq, 1, 1019, q), 0)
    # Two independent algorithms must agree.
    h = pow(gq2, 4242, 100043)
    check("rho agrees with bsgs",
          try_or_sol("pollard_rho_log", gq2, h, 100043, q2),
          try_or_sol("bsgs", gq2, h, 100043, q2))

    print("\nExercise 6: break_dh")
    p, g = 1019, 2
    a, b = 613, 227
    A, B = pow(g, a, p), pow(g, b, p)
    check("shared == B^a == A^b", pow(B, a, p), pow(A, b, p))
    check("recovers shared secret",
          try_or_sol("break_dh", g, p, A, B, p - 1), pow(g, a * b, p))
    p2, g2 = 1000000007, 5
    a2, b2 = 987654321, 192837465
    A2, B2 = pow(g2, a2, p2), pow(g2, b2, p2)
    check("30-bit prime falls too",
          try_or_sol("break_dh", g2, p2, A2, B2, p2 - 1), pow(g2, a2 * b2, p2))

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    print('=' * 50)


if __name__ == "__main__":
    run_tests()
