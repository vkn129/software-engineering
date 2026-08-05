"""
Day 154: Discrete Logarithm — From Scratch

Given prime p, base g, and h in Z_p^*, find x with g^x = h (mod p).

Day 150 gave the easy direction (g^x mod p in O(log x)). This is the hard
direction, and the gap between them is what Diffie-Hellman sells.

  1. brute_force_log      O(n)         the thing to beat
  2. multiplicative_order the group order — every algorithm below needs it
  3. bsgs                 O(sqrt n) time, O(sqrt n) space, deterministic
  4. pollard_rho_log      O(sqrt n) time, O(1) space, randomized
  5. Diffie-Hellman       the attack the two above actually enable

Boundaries respected on purpose:
  - `pow(g, x, p)` is day-150's binary ladder. We do not rewrite it.
  - `pow(a, -1, p)` is day-151's extended Euclid. We do not rewrite it either.
Both are called out at the point of use, so the reuse is visible, not hidden.
"""

import math
import random
import time


# ---------------------------------------------------------------------------
# 0. Small number-theory helpers
# ---------------------------------------------------------------------------

def is_prime(n):
    """Trial division. Fine to ~10^12; day-149's sieve is the bulk tool."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def prime_factors(n):
    """Distinct prime factors of n, ascending. Trial division to sqrt(n)."""
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


def multiplicative_order(g, p):
    """
    Smallest n > 0 with g^n = 1 (mod p), for prime p.

    Not by counting — that is O(p). Lagrange says the order divides p-1, so
    start at p-1 and, for each prime factor q, divide it out as long as the
    smaller exponent still kills g. What remains is the true order.
    """
    g %= p
    if g == 0:
        raise ValueError("0 has no multiplicative order")
    n = p - 1
    for q in prime_factors(p - 1):
        while n % q == 0 and pow(g, n // q, p) == 1:
            n //= q
    return n


# ---------------------------------------------------------------------------
# 1. Brute force — the baseline
# ---------------------------------------------------------------------------

def brute_force_log(g, h, p, n=None):
    """
    Walk the whole subgroup. O(n) multiplies, O(1) space.
    Smallest x in [0, n) with g^x = h, else None.
    """
    if n is None:
        n = p - 1
    h %= p
    y = 1
    for x in range(n):
        if y == h:
            return x
        y = (y * g) % p
    return None


# ---------------------------------------------------------------------------
# 2. Baby-step giant-step — meet in the middle over the exponent
# ---------------------------------------------------------------------------

def baby_steps(g, p, m):
    """
    {g^j mod p : j} for j in [0, m).

    Keep the SMALLEST j per value: if g has small order the powers repeat, and
    the smallest j yields the smallest valid logarithm.
    """
    table = {}
    y = 1
    for j in range(m):
        if y not in table:
            table[y] = j
        y = (y * g) % p
    return table


def bsgs(g, h, p, n=None):
    """
    Solve g^x = h (mod p) for x in [0, n). None if h is not in <g>.

    Write x = i*m + j with m = ceil(sqrt(n)). Then

        g^(i*m + j) = h    <=>    g^j = h * (g^-m)^i

    Left side ranges over j only, right over i only. Tabulate one side, walk
    the other, look for the meeting point: sqrt(n) work instead of n.
    """
    g %= p
    h %= p
    if h == 0:
        return None  # 0 is not in Z_p^*, so no power of g reaches it
    if n is None:
        n = p - 1
    m = math.isqrt(n - 1) + 1 if n > 1 else 1  # ceil(sqrt(n))

    table = baby_steps(g, p, m)

    # g^-m. pow(a, -1, p) is Python's spelling of day-151's extended Euclid;
    # it exists because p is prime and g != 0, so gcd(g, p) = 1.
    factor = pow(g, -m, p)

    gamma = h
    for i in range(m):
        j = table.get(gamma)
        if j is not None:
            x = i * m + j
            if x < n:
                return x
        gamma = (gamma * factor) % p
    return None  # h is genuinely not a power of g


# ---------------------------------------------------------------------------
# 3. Pollard's rho for logarithms — same time, constant space
# ---------------------------------------------------------------------------

def _rho_step(x, a, b, g, h, p, n):
    """
    One step of the pseudo-random walk, preserving  x = g^a * h^b (mod p).

    The three-way split by x mod 3 is arbitrary — it only has to be cheap and
    to mix. What matters is that every branch updates (a, b) consistently, or
    the invariant breaks and the collision tells you nothing.
    """
    r = x % 3
    if r == 0:
        return (x * x) % p, (2 * a) % n, (2 * b) % n
    if r == 1:
        return (x * g) % p, (a + 1) % n, b
    return (x * h) % p, a, (b + 1) % n


def _solve_congruence(lhs, coeff, n, g, h, p):
    """
    Solve  coeff * x = lhs (mod n), returning the root that actually satisfies
    g^x = h, else None.

    coeff is invertible only when gcd(coeff, n) = 1. Otherwise there are
    d = gcd(coeff, n) roots (or none) and we must test them — exactly the case
    that vanishes when n is prime, which is why prime-order subgroups are the
    production choice.
    """
    coeff %= n
    lhs %= n
    if coeff == 0:
        return None  # collision carries no information about x
    d = math.gcd(coeff, n)
    if d == 1:
        x = (lhs * pow(coeff, -1, n)) % n
        return x if pow(g, x, p) == h else None
    if lhs % d != 0:
        return None  # no solution from this collision
    n2 = n // d
    x0 = ((lhs // d) * pow((coeff // d) % n2, -1, n2)) % n2
    for k in range(d):
        x = x0 + k * n2
        if pow(g, x, p) == h:
            return x
    return None


def pollard_rho_log(g, h, p, n=None, max_restarts=20, rng=None):
    """
    Discrete log by pseudo-random walk + Floyd cycle detection. O(1) space.

    Expected ~1.25*sqrt(n) steps (birthday bound). Randomized: a walk can
    collide uselessly, so we cap iterations and restart from a fresh random
    (a0, b0). None if every restart failed.
    """
    g %= p
    h %= p
    if h == 0:
        return None
    if h == 1:
        return 0
    if n is None:
        n = multiplicative_order(g, p)
    rng = rng or random.Random(154)

    # Cap the walk at a few multiples of sqrt(n): past that a collision either
    # already happened or this walk fell into a degenerate short cycle.
    limit = 4 * math.isqrt(n) + 16

    for _ in range(max_restarts):
        a0 = rng.randrange(n)
        b0 = rng.randrange(n)
        start = (pow(g, a0, p) * pow(h, b0, p)) % p

        xt, at, bt = start, a0, b0          # tortoise: one step per round
        xh, ah, bh = start, a0, b0          # hare: two steps per round
        for _ in range(limit):
            xt, at, bt = _rho_step(xt, at, bt, g, h, p, n)
            xh, ah, bh = _rho_step(xh, ah, bh, g, h, p, n)
            xh, ah, bh = _rho_step(xh, ah, bh, g, h, p, n)
            if xt == xh:
                # g^at h^bt = g^ah h^bh  =>  g^(at-ah) = h^(bh-bt),
                # and h = g^x, so  at - ah = x*(bh - bt)  (mod n).
                x = _solve_congruence(at - ah, bh - bt, n, g, h, p)
                if x is not None:
                    return x
                break  # useless collision — restart from a new random point
    return None


# ---------------------------------------------------------------------------
# 4. Diffie-Hellman and the attack on it
# ---------------------------------------------------------------------------

def dh_public(g, secret, p):
    """A = g^a mod p. Day-150's ladder; O(log a) multiplies."""
    return pow(g, secret, p)


def dh_shared(other_public, secret, p):
    """s = B^a = g^(ab) = A^b mod p. Both sides compute the same value."""
    return pow(other_public, secret, p)


def break_dh(g, p, A, B, n=None, solver=bsgs):
    """
    Recover the shared secret from public data only.

    Eve needs exactly ONE discrete log, not two: get `a` from A, then compute
    B^a herself — the same arithmetic Alice does. Solving for `b` too is
    wasted work.
    """
    a = solver(g, A, p, n)
    if a is None:
        return None
    return pow(B, a, p)


# ---------------------------------------------------------------------------
# Parameters — verified at runtime, not trusted
# ---------------------------------------------------------------------------

# Safe primes p = 2q+1 with q prime. The order-q subgroup <g^2> is where the
# clean (prime-order) versions of both algorithms live.
SMALL = (1019, 2)              # q = 509
MEDIUM = (100043, 2)           # q = 50021
LARGE = (1000000007, 5)        # q = 500000003


def check_params(p, g):
    """A safe prime and a generator, or the demos below are teaching a lie."""
    q = (p - 1) // 2
    assert is_prime(p), f"{p} is not prime"
    assert is_prime(q), f"{p} is not a SAFE prime: {q} is composite"
    assert multiplicative_order(g, p) == p - 1, f"{g} does not generate Z_{p}^*"
    return q


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_the_asymmetry():
    print("=" * 68)
    print("DEMO 1: the asymmetry — forward is trivial, backward is the day")
    print("=" * 68)
    p, g = SMALL
    q = check_params(p, g)
    print(f"\n  p = {p} (safe prime, q = {q}), g = {g}, |Z_p^*| = {p - 1}")
    print("\n     x  | g^x mod p        <- day-150, O(log x)")
    for x in [1, 2, 10, 500, 1017]:
        print(f"  {x:5d}  | {pow(g, x, p)}")
    print("\n  Going the other way is the entire rest of this file.")
    print(f"  order(g)   = {multiplicative_order(g, p)}  (g generates everything)")
    print(f"  order(g^2) = {multiplicative_order(pow(g, 2, p), p)}  "
          f"(the prime-order subgroup)")
    print(f"  order(p-1) = {multiplicative_order(p - 1, p)}  "
          f"(p-1 = -1 mod p, so it squares to 1)")


def demo_brute_vs_bsgs():
    print("\n" + "=" * 68)
    print("DEMO 2: brute force vs baby-step giant-step")
    print("=" * 68)
    p, g = MEDIUM
    check_params(p, g)
    n = p - 1
    secret = 48765
    h = pow(g, secret, p)
    print(f"\n  p = {p}, g = {g}, h = g^{secret} = {h}")

    t0 = time.perf_counter()
    x1 = brute_force_log(g, h, p, n)
    t1 = time.perf_counter()
    x2 = bsgs(g, h, p, n)
    t2 = time.perf_counter()

    m = math.isqrt(n - 1) + 1
    print(f"\n  brute force : x = {x1}   {t1 - t0:.4f}s   ~{n} multiplies")
    print(f"  BSGS        : x = {x2}   {t2 - t1:.4f}s   ~{2 * m} multiplies, "
          f"{m} table slots")
    assert x1 == x2 == secret
    print(f"  operation-count ratio: {n / (2 * m):.0f}x fewer for BSGS")


def demo_bsgs_structure():
    print("\n" + "=" * 68)
    print("DEMO 3: what BSGS is actually doing")
    print("=" * 68)
    p, g = SMALL
    n = p - 1
    secret = 777
    h = pow(g, secret, p)
    m = math.isqrt(n - 1) + 1
    table = baby_steps(g, p, m)

    print(f"\n  p = {p}, g = {g}, h = {h}, n = {n}, m = ceil(sqrt(n)) = {m}")
    print(f"  baby-step table holds {len(table)} entries (g^0 .. g^{m - 1})")
    factor = pow(g, -m, p)
    gamma = h
    for i in range(m):
        if gamma in table:
            j = table[gamma]
            print(f"  giant step i = {i:2d}: gamma = {gamma} IS in the table "
                  f"at j = {j}")
            print(f"  => x = i*m + j = {i}*{m} + {j} = {i * m + j}")
            assert i * m + j == secret
            break
        gamma = (gamma * factor) % p
    print(f"\n  Found after {m} baby steps + {i + 1} giant steps = "
          f"{m + i + 1} multiplies, vs {n} for brute force.")


def demo_rho():
    print("\n" + "=" * 68)
    print("DEMO 4: Pollard's rho — same time, O(1) space")
    print("=" * 68)
    p, g_full = LARGE
    q = check_params(p, g_full)
    g = pow(g_full, 2, p)  # generator of the prime-order-q subgroup
    assert multiplicative_order(g, p) == q

    secret = 424242424
    h = pow(g, secret, p)
    print(f"\n  p = {p} (safe prime)")
    print(f"  working in the order-q subgroup, q = {q} (prime)")
    print(f"  h = g^{secret},  sqrt(q) ~ {math.isqrt(q)}")

    t0 = time.perf_counter()
    x_bsgs = bsgs(g, h, p, q)
    t1 = time.perf_counter()
    x_rho = pollard_rho_log(g, h, p, q)
    t2 = time.perf_counter()

    print(f"\n  BSGS : x = {x_bsgs}   {t1 - t0:.3f}s   "
          f"~{math.isqrt(q)} table entries held in RAM")
    print(f"  rho  : x = {x_rho}   {t2 - t1:.3f}s   6 integers held in RAM")
    assert x_bsgs == x_rho == secret
    print("\n  Same answer, same asymptotic time. The difference is memory —")
    print("  which is why every real ECDLP record used rho, never BSGS.")


def demo_rho_failure_case():
    print("\n" + "=" * 68)
    print("DEMO 5: when a rho collision is useless")
    print("=" * 68)
    print("\n  A collision gives   a_t - a_h = x * (b_h - b_t)  (mod n),")
    print("  solvable for x only when gcd(b_h - b_t, n) = 1.")
    p, g = MEDIUM
    n = p - 1  # composite (= 2q), so gcd > 1 is reachable
    secret = 31337
    h = pow(g, secret, p)
    print("\n  _solve_congruence handles all three cases:")
    print(f"    coeff = 0        -> None (no information) : "
          f"{_solve_congruence(5, 0, n, g, h, p)}")
    lhs = (2 * secret) % n  # gcd(2, n) = 2: two candidate roots, one correct
    print(f"    gcd(coeff,n) = 2 -> tests 2 candidates    : "
          f"{_solve_congruence(lhs, 2, n, g, h, p)} (secret = {secret})")
    print(f"    gcd(coeff,n) = 1 -> single inverse        : "
          f"{_solve_congruence(secret, 1, n, g, h, p)}")
    print("\n  With n PRIME the middle case cannot occur: gcd is 1 or n.")
    print("  That is the entire argument for prime-order subgroups.")


def demo_break_diffie_hellman():
    print("\n" + "=" * 68)
    print("DEMO 6: breaking Diffie-Hellman with a discrete log")
    print("=" * 68)
    p, g = LARGE
    check_params(p, g)
    rng = random.Random(2024)
    a = rng.randrange(2, p - 1)
    b = rng.randrange(2, p - 1)

    A = dh_public(g, a, p)
    B = dh_public(g, b, p)
    s_alice = dh_shared(B, a, p)
    s_bob = dh_shared(A, b, p)
    assert s_alice == s_bob
    print(f"\n  public : p = {p}, g = {g}")
    print(f"  Alice  : secret a = {a}   sends A = {A}")
    print(f"  Bob    : secret b = {b}   sends B = {B}")
    print(f"  shared : s = {s_alice}   (both sides agree)")

    print("\n  Eve knows only p, g, A, B. She solves ONE discrete log:")
    t0 = time.perf_counter()
    s_eve = break_dh(g, p, A, B, n=p - 1)
    t1 = time.perf_counter()
    a_eve = bsgs(g, A, p, p - 1)
    print(f"    recovered a = {a_eve}   (true a = {a})")
    print(f"    recovered s = {s_eve}   (true s = {s_alice})")
    print(f"    time: {t1 - t0:.3f}s")
    assert s_eve == s_alice and a_eve == a
    print("\n  This 30-bit prime dies in milliseconds. Real DH uses 2048 bits,")
    print("  where index calculus — not this code — is the relevant attack.")


def demo_edge_cases():
    print("\n" + "=" * 68)
    print("DEMO 7: the answers that are not numbers")
    print("=" * 68)
    p = 23
    g = 2  # order 11, NOT a generator of Z_23^* (which has order 22)
    n = multiplicative_order(g, p)
    print(f"\n  p = {p}, g = {g}, order(g) = {n} (g is not a generator)")
    reachable = sorted({pow(g, x, p) for x in range(n)})
    print(f"  <g> = {reachable}  ({len(reachable)} of {p - 1} residues)")
    for h in [1, 8, 5, 0]:
        got = bsgs(g, h, p, n)
        why = ("h = 1 is always g^0" if h == 1 else
               "0 is not in Z_p^*" if h == 0 else
               "in <g>" if h in reachable else "NOT in <g> — no logarithm exists")
        print(f"    bsgs(g={g}, h={h:2d}) = {str(got):5s}   ({why})")
    print("\n  None is a correct answer, not an error. Returning 0 instead")
    print("  would be a silent wrong answer — the worst kind.")


if __name__ == "__main__":
    demo_the_asymmetry()
    demo_brute_vs_bsgs()
    demo_bsgs_structure()
    demo_rho()
    demo_rho_failure_case()
    demo_break_diffie_hellman()
    demo_edge_cases()
