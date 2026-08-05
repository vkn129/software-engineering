# Day 135: KMP (Knuth-Morris-Pratt)

## Why KMP Matters

Rabin-Karp is probabilistic. KMP is deterministic and **never backtracks** the
text pointer. Real systems that need worst-case O(n+m) bounds use KMP:

- **grep / ripgrep / ag**: literal pattern fallback when regex is non-existent
- **memmem(3)** in glibc: uses a Two-Way variant of KMP for libc substring search
- **Snort / Suricata IDS**: pattern matching on packet payloads (DoS-safe path)
- **Compiler lexers**: keyword scanning with guaranteed linear behavior
- **DNA / protein sequence search**: when probabilistic isn't acceptable

KMP is the canonical example of "preprocess the pattern once, then scan linearly."
The preprocessing produces a **failure function** (also called π or LPS array).

## The Naive Problem

Brute-force substring search at position i in text T:

```
for i in range(n - m + 1):
    if T[i:i+m] == P: matches.append(i)
```

Worst case: T = "aaaa...a", P = "aaa...ab". Every prefix of P matches T up to the
last character, then fails. We restart at i+1 and redo the same m-1 comparisons.
**O(nm)** total — catastrophic on `a^10^6` vs `a^1000 b`.

## KMP's Insight: Don't Re-Scan What You've Already Matched

When P[0..j-1] matched T[i-j..i-1] and then P[j] != T[i]:
- We know exactly which suffix of `P[0..j-1]` is also a prefix of P.
- That's the longest **proper prefix that is also a suffix** (LPS) of P[0..j-1].
- Skip ahead to that prefix length; **don't move i back**.

The failure function precomputes "after matching P[0..j-1], if we fail, how
many characters can I keep matched?"

## Failure Function Construction

```
fail[0] = 0
fail[j] = length of longest proper prefix of P[0..j] that is also a suffix
```

Build in O(m) using a similar matching-against-self technique:

```
def build_fail(P):
    fail = [0] * len(P)
    k = 0
    for i in range(1, len(P)):
        while k > 0 and P[k] != P[i]:
            k = fail[k - 1]      # the recursive fallback
        if P[k] == P[i]:
            k += 1
        fail[i] = k
    return fail
```

The `while` loop runs amortized O(m) total — `k` never exceeds `i`, and each
iteration decreases it strictly. Outer increments it at most m times.

## Example

```
P = "ababaca"
       0 1 2 3 4 5 6
P    : a b a b a c a
fail : 0 0 1 2 3 0 1
```

After matching "ababa" (j=5) and failing on P[5]='c' vs some text char,
fail[4] = 3 means: keep the "aba" prefix matched, continue from P[3].

## Matching Phase

```
def kmp_search(T, P):
    fail = build_fail(P)
    j = 0
    matches = []
    for i in range(len(T)):
        while j > 0 and P[j] != T[i]:
            j = fail[j - 1]
        if P[j] == T[i]:
            j += 1
        if j == len(P):
            matches.append(i - j + 1)
            j = fail[j - 1]      # find next match
    return matches
```

## Why O(n+m)

**Amortized argument**: i strictly increases each outer step (n iterations).
j changes by +1 (match) or decreases (failure). Across all iterations, j is
incremented at most n times, so it can be decremented at most n times.
Total work: **2n + m** = O(n+m).

## Failure Modes

### 1. Catastrophic Naive Search

Naive matcher on `a^10^6` vs `a^999 b` takes ~10^9 char comparisons.
KMP: 10^6 comparisons. **3-4 orders of magnitude** difference.

### 2. Off-by-One in Failure Function

The classic bug: confusing "prefix length" vs "index of last matched char."
`fail[j]` is a *length*, so `P[fail[j]]` is the next character to compare on
fallback. Get this wrong and the matcher silently misses occurrences or
infinite-loops.

### 3. Misusing KMP for Approximate Matching

KMP is for **exact** match. For edit-distance-bounded search, you need
Aho-Corasick with bitmap tricks or Wu-Manber. People reach for KMP and
write buggy fuzzy-match logic on top of it.

### 4. Memory on Massive Patterns

`fail` is O(m). For m = 10^9 patterns (e.g., entire genome as a pattern),
this matters. In practice, KMP is for "pattern << text"; flip to suffix
automaton / FM-index for "text << many patterns".

## KMP vs Rabin-Karp vs Z-Algorithm

| Property | KMP | Rabin-Karp | Z-Algorithm |
|----------|-----|------------|-------------|
| Time | O(n+m) worst | O(n+m) avg, O(nm) worst | O(n+m) worst |
| Space | O(m) | O(1) extra | O(n+m) |
| Adversarial-safe | Yes | No (without random seed) | Yes |
| Multi-pattern | No (use Aho-Corasick) | Yes (same length) | No |
| 2D / streaming | OK | Easier in streaming | Harder |
| Mental model | failure function | hash window | extension array |

## Variants

### KMP Automaton

You can convert the failure function into a full DFA: `delta[state][char]`
gives the next state. O(m·|Σ|) space but **truly** O(n) match (no while loop).
Used when matching against a fixed pattern repeatedly (e.g., compiler keywords).

### Aho-Corasick (Day 137)

Generalizes KMP to **many patterns**. Build a trie, then add failure links.
Each text character triggers O(1) amortized state transitions plus output emit.

## Checkpoint Questions

1. Why does the failure-function construction look almost identical to the
   search phase? What's the operational equivalence?
2. What's `fail[0]` and why?
3. For P = "aaaa", what's the failure array? What does each value mean physically?
4. Show with example why "move i back on mismatch" is incorrect.
5. If KMP is O(n+m) worst case, why do real `grep` implementations sometimes
   use Boyer-Moore-Horspool instead?
6. Construct a pattern of length 10 where the failure function reaches its
   maximum useful value at position 9.
