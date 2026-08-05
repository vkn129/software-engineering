# Day 134: String Hashing & Rabin-Karp

## Why String Hashing Matters

Comparing two strings of length m costs O(m). Comparing two **hashes** costs O(1).
String hashing trades a tiny probability of error for massive speed:

- **Plagiarism detection**: hash 5-word windows across millions of documents
- **Rsync / dedup**: rolling hashes find unchanged blocks in changed files
- **Bioinformatics**: locate gene patterns in genomes (3 billion base pairs)
- **Compilers**: identify duplicate subexpressions in CSE
- **Anti-cheat**: signature scanning across game memory
- **Search engines**: shingle hashing for near-duplicate detection

## Rabin-Karp: The Idea

To find pattern P (length m) in text T (length n):

1. Compute hash(P) once.
2. Slide a window of size m across T.
3. At each position i, compare hash(T[i:i+m]) with hash(P).
4. On hash match, verify character-by-character (defends against collisions).

Naive recomputation of the window hash is O(m) per shift = O(nm) total.
The trick is the **rolling hash**: update in O(1) per shift.

## Rolling Hash (Polynomial)

Treat the substring as a number in base `b` mod a prime `p`:

```
hash(s) = (s[0]*b^(m-1) + s[1]*b^(m-2) + ... + s[m-1]) mod p
```

Shifting the window by one position:

```
new_hash = ((old_hash - s[i]*b^(m-1)) * b + s[i+m]) mod p
```

One subtraction, one multiply, one add — O(1) per shift. Total: **O(n + m)**.

## Choosing `b` and `p`

- `b`: base larger than the alphabet (e.g., 257 for byte strings).
- `p`: a large prime. The **birthday paradox** says collisions become likely when
  you've hashed sqrt(p) distinct strings. So for n = 10^6 substrings, you want
  p > 10^12 — use 64-bit primes like `(1<<61) - 1` (Mersenne prime).

## Failure Modes

### 1. Hash Collision Attacks (Adversarial Input)

If your modulus is small or public, an attacker can construct strings that all
hash to the same bucket. Real exploits:

- **Python <3.4 dict DoS** (CVE-2012-1150): one HTTP request with 1000 colliding
  keys turns O(1) dict insertion into O(n^2).
- **Hash flooding** on web servers — adversarial POST params.

Mitigation: **randomized seed** chosen at startup; never publish your prime.

### 2. Modular Arithmetic Bugs

`(a - b) mod p` in Python is fine (always non-negative). In C, `%` can return
negative values — `((a - b) % p + p) % p` is the safe form.

### 3. Birthday Paradox

For ~10^9 substrings and a 32-bit hash, collisions are near-certain. Use
**double hashing**: two independent (b, p) pairs, accept only if both match.
Collision probability drops from 1/p to 1/p^2 ≈ 10^-37 for two 64-bit hashes.

### 4. Worst Case Without Verification

Skipping the character-by-character verify after a hash match means false
positives slip through. Always verify (unless you're OK with probabilistic
output, like Bloom filters).

## Variants

### Multi-Pattern Rabin-Karp

To search for k patterns simultaneously, store all pattern hashes in a set.
At each window, check membership in O(1). Total: O(n + km).

### 2D Rabin-Karp

Match a pattern matrix in a text matrix: hash each row's window, then hash
the column of row-hashes. Used in image template matching.

### Rolling Hash for Substring Equality

Precompute prefix hashes of T. Then hash of T[i:j] is computable in O(1):

```
hash(T[i:j]) = (prefix[j] - prefix[i] * b^(j-i)) mod p
```

This is the foundation of suffix array LCP queries, palindrome counting, etc.

## Complexity Summary

| Operation | Naive | Rabin-Karp (avg) | Rabin-Karp (worst) |
|-----------|-------|------------------|--------------------|
| Single pattern | O(nm) | O(n + m) | O(nm) (all collisions) |
| k patterns | O(knm) | O(n + km) | O(knm) |
| Substring equality | O(m) | O(1) after O(n) prep | O(1) |

Worst case is theoretical — with proper p and double hashing, you'll never see it
on non-adversarial data.

## Checkpoint Questions

1. Why is `p = 10^9 + 7` risky for n > 10^4 substrings? (Birthday paradox math.)
2. If you skip the verify step, what's the expected number of false positives in
   a text of length 10^9 with a 64-bit hash?
3. How does double hashing change the collision probability — additively or
   multiplicatively? Why?
4. In a multi-pattern search where all k patterns have different lengths, can
   you still use Rabin-Karp efficiently? What changes?
5. Why does `(1<<61) - 1` allow faster modular reduction than a random 61-bit prime?
6. An attacker submits patterns to your dedup service. Show how they could
   construct strings that all collide under a known (b, p), forcing worst-case O(nm).
