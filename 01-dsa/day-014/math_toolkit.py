"""
Day 14: Mathematical Toolkit -- Reusable Library of Week 2 Primitives (Days 8-13)
==================================================================================

A single importable library consolidating all mathematical primitives built
during Week 2. Four classes cover four domains:

    ModularArithmetic  -- operations in Z/mZ
    NumberTheory       -- divisibility, GCD, LCM, primality
    Combinatorics      -- counting, generating permutations & combinations
    BitUtils           -- bitwise operations at the hardware level

Every function is implemented from scratch with no external libraries.
Each docstring explains the underlying math and states time complexity.

Run: python math_toolkit.py
"""

import random


# =============================================================================
# CLASS 1: Modular Arithmetic
# =============================================================================

class ModularArithmetic:
    """Operations in Z/mZ -- the integers modulo m.

    Modular arithmetic creates finite algebraic structures from infinite
    integers. Every operation "wraps around" at the modulus, keeping numbers
    bounded. This is why it underpins cryptography (bounded computations
    that are hard to invert) and hashing (mapping infinite key spaces to
    finite table indices).
    """

    @staticmethod
    def mod_pow(base, exp, mod):
        """Compute base^exp mod mod via binary exponentiation.

        Any exponent can be written in binary: exp = b_k * 2^k + ... + b_0.
        So base^exp = product of base^(2^i) for each bit i that is set.
        We compute base^(2^i) iteratively by squaring, and multiply into the
        result only when the corresponding bit is 1.

        Time: O(log exp) -- we halve exp each iteration
        Space: O(1)

        Example:
            >>> ModularArithmetic.mod_pow(3, 13, 100)
            23  # 3^13 = 1594323, 1594323 % 100 = 23
        """
        if mod == 1:
            return 0
        result = 1
        base = base % mod
        while exp > 0:
            if exp & 1:
                result = (result * base) % mod
            exp >>= 1
            base = (base * base) % mod
        return result

    @staticmethod
    def mod_inverse(a, mod):
        """Compute the modular multiplicative inverse of a mod m.

        The inverse a^(-1) mod m is the number x such that a*x = 1 (mod m).
        It exists if and only if gcd(a, m) = 1 (a and m are coprime).

        Uses the extended Euclidean algorithm: find x, y such that
        a*x + m*y = gcd(a, m). When gcd = 1, x is the inverse.

        Time: O(log m) -- via extended GCD
        Space: O(log m) -- recursion depth

        Raises:
            ValueError: if gcd(a, m) != 1 (inverse does not exist)

        Example:
            >>> ModularArithmetic.mod_inverse(3, 7)
            5  # because 3 * 5 = 15 = 1 (mod 7)
        """
        g, x, _ = NumberTheory.extended_gcd(a, mod)
        if g != 1:
            raise ValueError(
                f"Modular inverse does not exist: gcd({a}, {mod}) = {g}"
            )
        return x % mod

    @staticmethod
    def solve_linear_congruence(a, b, mod):
        """Solve the linear congruence a*x = b (mod m).

        A solution exists iff g = gcd(a, m) divides b. When it does, there
        are exactly g incongruent solutions modulo m. The base solution is
        x0 = (b/g) * (a/g)^(-1) mod (m/g), and all solutions are
        x0 + k*(m/g) for k = 0, 1, ..., g-1.

        Derivation:
            a*x = b (mod m)  =>  a*x + m*y = b for some integer y.
            By Bezout's identity, a*x + m*y = g has solution (x0, y0).
            Scale by b/g to get a*(x0*b/g) + m*(y0*b/g) = b.
            So x = x0 * (b/g) mod (m/g) is the base solution.

        Time: O(log m) -- dominated by extended GCD
        Space: O(g) -- to store all g solutions

        Returns:
            List of all incongruent solutions modulo m, or empty list if
            no solution exists.

        Example:
            >>> ModularArithmetic.solve_linear_congruence(6, 3, 9)
            [5, 8, 2]  # three solutions because gcd(6,9)=3 divides 3
        """
        g, x0, _ = NumberTheory.extended_gcd(a, mod)
        if b % g != 0:
            return []  # No solution
        # Reduce to a simpler congruence: (a/g)*x = (b/g) mod (m/g)
        a_reduced = a // g
        b_reduced = b // g
        m_reduced = mod // g
        # x_base is the unique solution mod m_reduced
        _, inv_x, _ = NumberTheory.extended_gcd(a_reduced, m_reduced)
        x_base = (inv_x * b_reduced) % m_reduced
        # All g solutions
        solutions = []
        for k in range(g):
            solutions.append((x_base + k * m_reduced) % mod)
        return solutions


# =============================================================================
# CLASS 2: Number Theory
# =============================================================================

class NumberTheory:
    """Fundamental integer structure: divisibility, GCD, primality.

    These are the building blocks that all other number-theoretic algorithms
    rest on. Euclid's algorithm (300 BCE) is arguably the oldest non-trivial
    algorithm still in daily use.
    """

    @staticmethod
    def gcd(a, b):
        """Compute the greatest common divisor using Euclid's algorithm.

        Why it works: gcd(a, b) = gcd(b, a mod b) because any common divisor
        of a and b also divides a mod b (since a mod b = a - q*b). The
        sequence of remainders strictly decreases, so it terminates at 0.

        Time: O(log min(a, b)) -- the remainder shrinks by at least half
              every two iterations (Fibonacci connection).
        Space: O(1)

        Example:
            >>> NumberTheory.gcd(48, 18)
            6
        """
        a, b = abs(a), abs(b)
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def extended_gcd(a, b):
        """Compute gcd(a, b) and find x, y such that a*x + b*y = gcd(a, b).

        The extended Euclidean algorithm tracks the linear combination
        backwards through the recursion. This is the algorithmic heart of
        modular inverses, Chinese Remainder Theorem, and RSA key generation.

        Time: O(log min(a, b))
        Space: O(log min(a, b)) -- recursion stack

        Returns:
            (gcd, x, y) where a*x + b*y = gcd(a, b)

        Example:
            >>> NumberTheory.extended_gcd(35, 15)
            (5, 1, -2)  # 35*1 + 15*(-2) = 5
        """
        if a == 0:
            return b, 0, 1
        g, x1, y1 = NumberTheory.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return g, x, y

    @staticmethod
    def lcm(a, b):
        """Compute the least common multiple of a and b.

        Identity: lcm(a, b) * gcd(a, b) = |a * b|.
        We divide first to avoid overflow in fixed-width languages.

        Time: O(log min(a, b)) -- dominated by GCD
        Space: O(1)

        Example:
            >>> NumberTheory.lcm(12, 18)
            36
        """
        if a == 0 or b == 0:
            return 0
        return abs(a) // NumberTheory.gcd(a, b) * abs(b)

    @staticmethod
    def is_prime_miller_rabin(n, k=10):
        """Probabilistic primality test using the Miller-Rabin algorithm.

        Why Miller-Rabin over trial division: trial division is O(sqrt(n)),
        impossibly slow for 1024-bit numbers. Miller-Rabin is O(k * log^2 n).

        How it works:
        Write n-1 = 2^s * d (factor out all powers of 2). For a random
        witness a, compute a^d mod n, then square repeatedly s times. By
        Fermat's little theorem, if n is prime we must see 1 or n-1 at
        specific points. If we don't, n is definitely composite.

        Error probability: each round has at most 1/4 chance of missing a
        composite. After k rounds, error < 4^(-k).

        Time: O(k * log^2 n) where k is the number of rounds
        Space: O(1)

        Args:
            n: The number to test.
            k: Number of rounds (default 10). More rounds = lower error.

        Example:
            >>> NumberTheory.is_prime_miller_rabin(104729)
            True
        """
        if n < 2:
            return False
        if n < 4:
            return True
        if n % 2 == 0:
            return False

        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        if n in small_primes:
            return True

        # Write n-1 as 2^s * d
        s, d = 0, n - 1
        while d % 2 == 0:
            d //= 2
            s += 1

        def _check_witness(a):
            """Return True if a witnesses that n is composite."""
            x = ModularArithmetic.mod_pow(a, d, n)
            if x == 1 or x == n - 1:
                return False
            for _ in range(s - 1):
                x = (x * x) % n
                if x == n - 1:
                    return False
            return True

        # Deterministic witnesses for small n; random for large n
        if n < 3_215_031_751:
            witnesses = [2, 3, 5, 7]
        else:
            witnesses = [random.randrange(2, n - 1) for _ in range(k)]

        for a in witnesses:
            if a >= n:
                continue
            if _check_witness(a):
                return False
        return True


# =============================================================================
# CLASS 3: Combinatorics
# =============================================================================

class Combinatorics:
    """Counting structures: how many ways can things be arranged or chosen.

    Combinatorics answers "how many?" questions. These counts appear
    everywhere: algorithm analysis (how many subsets?), probability
    (how many favorable outcomes?), and optimization (how large is the
    search space?).
    """

    @staticmethod
    def factorial(n):
        """Compute n! iteratively.

        n! = 1 * 2 * ... * n. Counts the number of permutations of n
        distinct objects. Grows faster than exponential -- Stirling's
        approximation: n! ~ sqrt(2*pi*n) * (n/e)^n.

        Time: O(n)
        Space: O(1)

        Example:
            >>> Combinatorics.factorial(5)
            120
        """
        if n < 0:
            raise ValueError(f"Factorial not defined for negative numbers, got {n}")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    @staticmethod
    def permutations(n, r):
        """Compute P(n, r) = n! / (n-r)! -- the number of r-permutations of n items.

        An r-permutation is an ordered selection of r items from n distinct items.
        Order matters: choosing A then B is different from B then A.

        Time: O(r) -- r multiplications
        Space: O(1)

        Example:
            >>> Combinatorics.permutations(5, 3)
            60  # 5 * 4 * 3
        """
        if r < 0 or r > n:
            return 0
        result = 1
        for i in range(n, n - r, -1):
            result *= i
        return result

    @staticmethod
    def combinations(n, r):
        """Compute C(n, r) using Pascal's triangle row to avoid overflow.

        Pascal's identity: C(n, r) = C(n-1, r-1) + C(n-1, r).
        We build only the row we need, using the bottom-up DP approach on
        a single array. This avoids computing large factorials directly.

        The key insight: each row of Pascal's triangle only depends on the
        previous row. We can compute row n using a single array of size r+1,
        updating right-to-left so we don't overwrite values we still need.

        Time: O(n * r) -- but avoids large intermediate factorials
        Space: O(r) -- single row of Pascal's triangle

        Example:
            >>> Combinatorics.combinations(10, 3)
            120
        """
        if r < 0 or r > n:
            return 0
        # Exploit symmetry to minimize work
        if r > n - r:
            r = n - r
        # Build the r-th entry of row n of Pascal's triangle
        row = [0] * (r + 1)
        row[0] = 1  # C(i, 0) = 1 for all i
        for i in range(1, n + 1):
            # Update right-to-left to avoid overwriting values we still need
            for j in range(min(i, r), 0, -1):
                row[j] = row[j] + row[j - 1]
        return row[r]

    @staticmethod
    def generate_permutations(items):
        """Yield all permutations of items using Heap's algorithm.

        Heap's algorithm generates each permutation by a single swap from
        the previous one, giving better cache behavior than the naive
        "insert into each position" approach.

        The control array c tracks how many swaps have been done at each
        "level" of the implicit recursion tree.

        Time: O(n!) permutations generated, each in O(1) amortized swap time
        Space: O(n) for the control array (not counting output)

        Yields:
            Each permutation as a list.

        Example:
            >>> list(Combinatorics.generate_permutations([1, 2, 3]))
            [[1, 2, 3], [2, 1, 3], [3, 1, 2], [1, 3, 2], [2, 3, 1], [3, 2, 1]]
        """
        a = list(items)
        n = len(a)
        c = [0] * n
        yield list(a)

        i = 0
        while i < n:
            if c[i] < i:
                if i % 2 == 0:
                    a[0], a[i] = a[i], a[0]
                else:
                    a[c[i]], a[i] = a[i], a[c[i]]
                yield list(a)
                c[i] += 1
                i = 0
            else:
                c[i] = 0
                i += 1

    @staticmethod
    def generate_combinations(items, r):
        """Yield all r-combinations of items using backtracking.

        Uses the recursive structure: for each element, either include it
        or skip it. Pruning ensures we don't explore branches where there
        aren't enough remaining elements to fill the combination.

        Time: O(C(n, r) * r) -- generating and copying each combination
        Space: O(r) for the current combination (not counting output)

        Yields:
            Each r-combination as a list.

        Example:
            >>> list(Combinatorics.generate_combinations([1, 2, 3, 4], 2))
            [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
        """
        items = list(items)
        n = len(items)

        def _backtrack(start, current):
            if len(current) == r:
                yield list(current)
                return
            remaining = n - start
            needed = r - len(current)
            if remaining < needed:
                return
            for i in range(start, n):
                current.append(items[i])
                yield from _backtrack(i + 1, current)
                current.pop()

        yield from _backtrack(0, [])


# =============================================================================
# CLASS 4: Bit Manipulation Utilities
# =============================================================================

class BitUtils:
    """Bitwise operations -- the closest you get to the hardware from Python.

    CPUs think in bits. Many algorithms become dramatically simpler or faster
    when expressed as bit operations: XOR for parity, AND for masking, shifts
    for division by powers of 2. Bitmasks represent subsets in O(1) space.
    """

    @staticmethod
    def count_set_bits(n):
        """Count set bits (1s) using Brian Kernighan's algorithm.

        The trick: n & (n-1) clears the lowest set bit. If the lowest set
        bit is at position k, then n has a 1 at k and 0s below. n-1 flips
        position k to 0 and all below to 1. AND-ing cancels position k.

        This runs exactly popcount(n) iterations instead of scanning all
        bit positions.

        Time: O(number of set bits) -- at most O(log n)
        Space: O(1)

        Example:
            >>> BitUtils.count_set_bits(0b10110101)
            5
        """
        count = 0
        while n:
            n &= n - 1
            count += 1
        return count

    @staticmethod
    def is_power_of_two(n):
        """Check if n is a power of two.

        A power of two in binary is a single 1 followed by zeros: 1, 10, 100.
        So n & (n-1) == 0 for powers of two (the single bit gets cleared).
        We also need n > 0 because 0 is not a power of two.

        Time: O(1)
        Space: O(1)

        Example:
            >>> BitUtils.is_power_of_two(64)
            True
            >>> BitUtils.is_power_of_two(65)
            False
        """
        return n > 0 and (n & (n - 1)) == 0

    @staticmethod
    def next_power_of_two(n):
        """Find the smallest power of two >= n.

        The algorithm "smears" the highest set bit downward by successive
        right-shifts and ORs, filling all lower positions with 1s. Adding 1
        then yields the next power of two.

        Used for hash table resizing, memory alignment, buffer allocation.

        Time: O(1) -- fixed number of operations
        Space: O(1)

        Example:
            >>> BitUtils.next_power_of_two(17)
            32
            >>> BitUtils.next_power_of_two(16)
            16
        """
        if n <= 1:
            return 1
        n -= 1
        n |= n >> 1
        n |= n >> 2
        n |= n >> 4
        n |= n >> 8
        n |= n >> 16
        n |= n >> 32
        return n + 1

    @staticmethod
    def get_bit(n, i):
        """Get the value of bit at position i (0-indexed from LSB).

        Right-shift n by i positions and mask with 1 to isolate that bit.

        Time: O(1)
        Space: O(1)

        Example:
            >>> BitUtils.get_bit(0b1010, 1)
            1
            >>> BitUtils.get_bit(0b1010, 0)
            0
        """
        return (n >> i) & 1

    @staticmethod
    def set_bit(n, i):
        """Set bit at position i to 1 (0-indexed from LSB).

        OR with a mask that has a 1 only at position i. This forces that
        bit to 1 regardless of its current value, leaving all others unchanged.

        Time: O(1)
        Space: O(1)

        Example:
            >>> BitUtils.set_bit(0b1000, 1)
            10  # 0b1010
        """
        return n | (1 << i)

    @staticmethod
    def clear_bit(n, i):
        """Clear bit at position i to 0 (0-indexed from LSB).

        AND with the complement of a mask that has a 1 at position i.
        The complement has 0 only at position i, forcing that bit to 0
        while preserving all others.

        Time: O(1)
        Space: O(1)

        Example:
            >>> BitUtils.clear_bit(0b1010, 1)
            8  # 0b1000
        """
        return n & ~(1 << i)

    @staticmethod
    def toggle_bit(n, i):
        """Toggle (flip) bit at position i (0-indexed from LSB).

        XOR with a mask that has a 1 at position i. XOR flips the bit:
        0 XOR 1 = 1, 1 XOR 1 = 0. All other bits are unchanged because
        x XOR 0 = x.

        Time: O(1)
        Space: O(1)

        Example:
            >>> BitUtils.toggle_bit(0b1010, 1)
            8   # 0b1000 (bit 1 was 1, now 0)
            >>> BitUtils.toggle_bit(0b1010, 0)
            11  # 0b1011 (bit 0 was 0, now 1)
        """
        return n ^ (1 << i)


# =============================================================================
# DEMO: Exercise every function
# =============================================================================

if __name__ == "__main__":

    print("=" * 70)
    print("MATHEMATICAL TOOLKIT -- Day 14 Mini-Project Demo")
    print("=" * 70)

    # ---- Modular Arithmetic ----
    print("\n--- Modular Arithmetic ---")
    MOD = 10**9 + 7

    print(f"  mod_pow(3, 13, 100)     = {ModularArithmetic.mod_pow(3, 13, 100)}")
    print(f"  mod_pow(2, 10, 1000)    = {ModularArithmetic.mod_pow(2, 10, 1000)}")

    inv = ModularArithmetic.mod_inverse(3, 7)
    print(f"  mod_inverse(3, 7)       = {inv}  (verify: 3*{inv} mod 7 = {(3*inv)%7})")

    solutions = ModularArithmetic.solve_linear_congruence(6, 3, 9)
    print(f"  solve_linear_congruence(6, 3, 9) = {solutions}")
    for x in solutions:
        print(f"    verify: 6*{x} mod 9 = {(6*x)%9}")

    no_sol = ModularArithmetic.solve_linear_congruence(6, 4, 9)
    print(f"  solve_linear_congruence(6, 4, 9) = {no_sol}  (no solution: gcd(6,9)=3 does not divide 4)")

    # ---- Number Theory ----
    print("\n--- Number Theory ---")
    print(f"  gcd(48, 18)             = {NumberTheory.gcd(48, 18)}")
    print(f"  gcd(0, 5)               = {NumberTheory.gcd(0, 5)}")

    g, x, y = NumberTheory.extended_gcd(35, 15)
    print(f"  extended_gcd(35, 15)    = ({g}, {x}, {y})  (verify: 35*{x}+15*{y} = {35*x+15*y})")

    print(f"  lcm(12, 18)             = {NumberTheory.lcm(12, 18)}")

    test_primes = [2, 3, 17, 97, 104729, 100, 561, 1]
    print("  Miller-Rabin primality:")
    for n in test_primes:
        result = NumberTheory.is_prime_miller_rabin(n)
        print(f"    is_prime_miller_rabin({n}) = {result}")

    # ---- Combinatorics ----
    print("\n--- Combinatorics ---")
    print(f"  factorial(5)            = {Combinatorics.factorial(5)}")
    print(f"  factorial(10)           = {Combinatorics.factorial(10)}")

    print(f"  permutations(5, 3)      = {Combinatorics.permutations(5, 3)}  (P(5,3) = 60)")
    print(f"  permutations(10, 2)     = {Combinatorics.permutations(10, 2)}  (P(10,2) = 90)")

    print(f"  combinations(10, 3)     = {Combinatorics.combinations(10, 3)}  (C(10,3) = 120)")
    print(f"  combinations(20, 10)    = {Combinatorics.combinations(20, 10)}  (C(20,10) = 184756)")
    print(f"  combinations(50, 25)    = {Combinatorics.combinations(50, 25)}")

    perms = list(Combinatorics.generate_permutations([1, 2, 3]))
    print(f"  generate_permutations([1,2,3]): {len(perms)} permutations")
    for p in perms:
        print(f"    {p}")

    combs = list(Combinatorics.generate_combinations([1, 2, 3, 4], 2))
    print(f"  generate_combinations([1,2,3,4], 2): {len(combs)} combinations")
    for c in combs:
        print(f"    {c}")

    # ---- Bit Utilities ----
    print("\n--- Bit Utilities ---")
    print(f"  count_set_bits(0b10110101)  = {BitUtils.count_set_bits(0b10110101)}  (expected 5)")
    print(f"  is_power_of_two(64)         = {BitUtils.is_power_of_two(64)}")
    print(f"  is_power_of_two(65)         = {BitUtils.is_power_of_two(65)}")
    print(f"  next_power_of_two(17)       = {BitUtils.next_power_of_two(17)}")
    print(f"  next_power_of_two(16)       = {BitUtils.next_power_of_two(16)}")

    n = 0b10110100
    print(f"\n  Bit operations on n = {n} ({bin(n)}):")
    for i in range(8):
        print(f"    get_bit(n, {i}) = {BitUtils.get_bit(n, i)}")

    print(f"  set_bit(0b1000, 1)          = {BitUtils.set_bit(0b1000, 1)}  ({bin(BitUtils.set_bit(0b1000, 1))})")
    print(f"  clear_bit(0b1010, 1)        = {BitUtils.clear_bit(0b1010, 1)}  ({bin(BitUtils.clear_bit(0b1010, 1))})")
    print(f"  toggle_bit(0b1010, 1)       = {BitUtils.toggle_bit(0b1010, 1)}  ({bin(BitUtils.toggle_bit(0b1010, 1))})")
    print(f"  toggle_bit(0b1010, 0)       = {BitUtils.toggle_bit(0b1010, 0)}  ({bin(BitUtils.toggle_bit(0b1010, 0))})")

    # ---- Cross-module composition: RSA mini-demo ----
    print("\n--- Cross-Module Composition: RSA Mini-Demo ---")

    # Generate two distinct 16-bit primes
    p = 0
    while not NumberTheory.is_prime_miller_rabin(p):
        p = random.getrandbits(16) | (1 << 15) | 1
    q = 0
    while not NumberTheory.is_prime_miller_rabin(q) or q == p:
        q = random.getrandbits(16) | (1 << 15) | 1

    n_rsa = p * q
    phi_n = (p - 1) * (q - 1)
    e = 65537
    while NumberTheory.gcd(e, phi_n) != 1:
        e += 2
    d = ModularArithmetic.mod_inverse(e, phi_n)

    message = 42
    encrypted = ModularArithmetic.mod_pow(message, e, n_rsa)
    decrypted = ModularArithmetic.mod_pow(encrypted, d, n_rsa)

    print(f"  p = {p}, q = {q}, n = {n_rsa}")
    print(f"  e = {e}, d = {d}")
    print(f"  message   = {message}")
    print(f"  encrypted = {encrypted}")
    print(f"  decrypted = {decrypted}")
    print(f"  RSA works: {decrypted == message}")

    print("\n" + "=" * 70)
    print("All toolkit functions exercised successfully.")
    print("=" * 70)
