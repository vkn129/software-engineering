"""
Day 134: Rabin-Karp & Rolling Hash — From Scratch

Polynomial rolling hash + sliding window = O(n + m) substring search.
Double hashing defends against birthday-paradox collisions.
"""

import random
import time


# ---------------------------------------------------------------------------
# 1. Polynomial Rolling Hash
# ---------------------------------------------------------------------------

# Mersenne prime, fits in 62 bits — allows fast modular reduction.
MOD = (1 << 61) - 1
BASE = 131  # > 128 (ASCII range)


def poly_hash(s, base=BASE, mod=MOD):
    """Compute hash of string s as a polynomial in `base` mod `mod`."""
    h = 0
    for ch in s:
        h = (h * base + ord(ch)) % mod
    return h


# ---------------------------------------------------------------------------
# 2. Naive Substring Search (for comparison)
# ---------------------------------------------------------------------------

def naive_search(text, pattern):
    """O(nm) brute force — for benchmarking only."""
    n, m = len(text), len(pattern)
    matches = []
    for i in range(n - m + 1):
        if text[i:i + m] == pattern:
            matches.append(i)
    return matches


# ---------------------------------------------------------------------------
# 3. Rabin-Karp (Single Hash)
# ---------------------------------------------------------------------------

def rabin_karp(text, pattern, base=BASE, mod=MOD):
    """
    Find all occurrences of pattern in text.
    Average O(n + m). Worst case O(nm) under adversarial collisions.
    """
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []

    # Precompute base^(m-1) mod p — used to remove the leading character.
    base_m_minus_1 = pow(base, m - 1, mod)

    pat_hash = poly_hash(pattern, base, mod)
    win_hash = poly_hash(text[:m], base, mod)

    matches = []
    for i in range(n - m + 1):
        if win_hash == pat_hash:
            # Hash match: VERIFY character by character.
            # Without this, collisions yield false positives.
            if text[i:i + m] == pattern:
                matches.append(i)

        if i < n - m:
            # Roll the window: drop leading char, append next.
            leading = ord(text[i]) * base_m_minus_1
            win_hash = ((win_hash - leading) * base + ord(text[i + m])) % mod

    return matches


# ---------------------------------------------------------------------------
# 4. Rabin-Karp with Double Hashing
# ---------------------------------------------------------------------------

# Two independent (base, mod) pairs — collision probability ~ 1/(mod1*mod2).
MOD1 = (1 << 61) - 1
MOD2 = (1 << 31) - 1
BASE1 = 131
BASE2 = 137


def rabin_karp_double(text, pattern):
    """
    Same as rabin_karp but with two hashes. A "match" requires both to agree.
    Verification still recommended for correctness — never trust hashes alone
    in adversarial settings.
    """
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []

    bm1_1 = pow(BASE1, m - 1, MOD1)
    bm1_2 = pow(BASE2, m - 1, MOD2)

    ph1 = poly_hash(pattern, BASE1, MOD1)
    ph2 = poly_hash(pattern, BASE2, MOD2)
    wh1 = poly_hash(text[:m], BASE1, MOD1)
    wh2 = poly_hash(text[:m], BASE2, MOD2)

    matches = []
    for i in range(n - m + 1):
        if wh1 == ph1 and wh2 == ph2:
            if text[i:i + m] == pattern:  # safety verify
                matches.append(i)

        if i < n - m:
            c_out, c_in = ord(text[i]), ord(text[i + m])
            wh1 = ((wh1 - c_out * bm1_1) * BASE1 + c_in) % MOD1
            wh2 = ((wh2 - c_out * bm1_2) * BASE2 + c_in) % MOD2

    return matches


# ---------------------------------------------------------------------------
# 5. Multi-Pattern Rabin-Karp (same-length patterns)
# ---------------------------------------------------------------------------

def multi_pattern_search(text, patterns):
    """
    Search for many patterns of the SAME length simultaneously.
    Returns dict: pattern -> list of start positions.
    O(n + k*m) where k = number of patterns.
    """
    if not patterns:
        return {}
    m = len(patterns[0])
    if any(len(p) != m for p in patterns):
        raise ValueError("All patterns must have equal length")

    n = len(text)
    if m > n:
        return {p: [] for p in patterns}

    base_m_minus_1 = pow(BASE, m - 1, MOD)

    # Map hash -> patterns with that hash (handle internal collisions).
    pat_table = {}
    for p in patterns:
        h = poly_hash(p, BASE, MOD)
        pat_table.setdefault(h, []).append(p)

    results = {p: [] for p in patterns}
    win_hash = poly_hash(text[:m], BASE, MOD)

    for i in range(n - m + 1):
        if win_hash in pat_table:
            window = text[i:i + m]
            for cand in pat_table[win_hash]:
                if cand == window:  # verify
                    results[cand].append(i)
        if i < n - m:
            leading = ord(text[i]) * base_m_minus_1
            win_hash = ((win_hash - leading) * BASE + ord(text[i + m])) % MOD

    return results


# ---------------------------------------------------------------------------
# 6. Prefix Hash for O(1) Substring Queries
# ---------------------------------------------------------------------------

class PrefixHash:
    """
    Precompute prefix hashes of a string. Query hash of any substring in O(1).
    Foundation for suffix arrays, palindrome counting, LCP queries.
    """

    def __init__(self, s, base=BASE, mod=MOD):
        self.s = s
        self.base = base
        self.mod = mod
        n = len(s)
        self.h = [0] * (n + 1)
        self.pw = [1] * (n + 1)
        for i, ch in enumerate(s):
            self.h[i + 1] = (self.h[i] * base + ord(ch)) % mod
            self.pw[i + 1] = (self.pw[i] * base) % mod

    def hash(self, i, j):
        """Hash of s[i:j], O(1)."""
        return (self.h[j] - self.h[i] * self.pw[j - i]) % self.mod

    def equal(self, i1, j1, i2, j2):
        """Are s[i1:j1] and s[i2:j2] equal? Probabilistic."""
        if j1 - i1 != j2 - i2:
            return False
        return self.hash(i1, j1) == self.hash(i2, j2)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 65)
    print("DEMO 1: Rabin-Karp Basic Search")
    print("=" * 65)
    text = "abracadabra-abracadabra"
    pattern = "abra"
    print(f"  text:    {text!r}")
    print(f"  pattern: {pattern!r}")
    print(f"  matches: {rabin_karp(text, pattern)}")
    print(f"  naive:   {naive_search(text, pattern)}")


def demo_naive_vs_rk():
    print("\n" + "=" * 65)
    print("DEMO 2: Rabin-Karp vs Naive (worst-case-friendly input)")
    print("=" * 65)

    # Friendly text — most window comparisons fail at char 1.
    text = "a" * 100000 + "b"
    pattern = "a" * 50 + "b"

    t0 = time.perf_counter()
    naive_search(text, pattern)
    naive_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    rabin_karp(text, pattern)
    rk_time = time.perf_counter() - t0

    print(f"  text len {len(text)}, pattern len {len(pattern)}")
    print(f"  naive:      {naive_time:.4f}s")
    print(f"  rabin-karp: {rk_time:.4f}s")
    # On near-degenerate inputs Python's slice equality dominates;
    # RK still avoids the O(m) compare on every position.


def demo_multi_pattern():
    print("\n" + "=" * 65)
    print("DEMO 3: Multi-Pattern Search")
    print("=" * 65)
    text = "the quick brown fox jumps over the lazy dog the cat"
    patterns = ["the", "cat", "fox", "dog"]
    results = multi_pattern_search(text, patterns)
    for p, positions in results.items():
        print(f"  {p!r:8s} found at {positions}")


def demo_prefix_hash():
    print("\n" + "=" * 65)
    print("DEMO 4: Prefix Hash — O(1) Substring Equality")
    print("=" * 65)
    s = "abcabcabc"
    ph = PrefixHash(s)
    print(f"  s = {s!r}")
    print(f"  s[0:3] == s[3:6]? {ph.equal(0, 3, 3, 6)}  (abc == abc)")
    print(f"  s[0:3] == s[6:9]? {ph.equal(0, 3, 6, 9)}  (abc == abc)")
    print(f"  s[0:4] == s[3:7]? {ph.equal(0, 4, 3, 7)}  (abca == abca)")
    print(f"  s[0:3] == s[1:4]? {ph.equal(0, 3, 1, 4)}  (abc == bca)")


def demo_collision_attack():
    print("\n" + "=" * 65)
    print("DEMO 5: Collision Attack — Why Verification Matters")
    print("=" * 65)
    # Tiny mod for demonstration. NEVER use a small mod in production.
    SMALL_MOD = 101
    print(f"  Using mod={SMALL_MOD} (intentionally tiny).")

    # Build many short strings, count hash collisions.
    random.seed(0)
    alpha = "abcdefgh"
    strings = []
    for _ in range(500):
        strings.append("".join(random.choice(alpha) for _ in range(4)))

    buckets = {}
    for s in strings:
        h = poly_hash(s, BASE, SMALL_MOD)
        buckets.setdefault(h, []).append(s)
    collisions = sum(1 for v in buckets.values() if len(set(v)) > 1)
    print(f"  500 strings -> {collisions} buckets with collisions.")
    print(f"  Birthday paradox: collisions expected once #strings ~ sqrt(mod).")
    print(f"  sqrt({SMALL_MOD}) ~ {int(SMALL_MOD ** 0.5)}, so 500 >> threshold.")


if __name__ == "__main__":
    demo_basic()
    demo_naive_vs_rk()
    demo_multi_pattern()
    demo_prefix_hash()
    demo_collision_attack()
