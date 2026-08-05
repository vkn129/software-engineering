# Day 138: Suffix Arrays & LCP

## Why Suffix Arrays Matter

A **suffix array** is the sorted list of all suffixes' starting positions.
It's the workhorse of string indexing:

- **`grep` over indexed text**: O(m log n) substring query after O(n) build
- **Bioinformatics**: BWA, Bowtie, and most read aligners use SA / FM-index
- **Bzip2, xz**: BWT-based compression depends on SA construction
- **Plagiarism detection at scale**: find common substrings across docs
- **Full-text search**: precursor to FM-index, used in Elasticsearch-class engines
- **Longest repeated substring / longest common substring**: O(n) via SA + LCP

Suffix trees do the same job in O(n) but with 10-20x memory overhead and
complex pointer structures. Suffix arrays give 95% of the power at 1/10 the
memory — that's why every modern system prefers them.

## The Data Structure

For string `s` of length `n`, the suffix array `sa` is a permutation of
`[0, 1, ..., n-1]` such that `s[sa[i]:]` < `s[sa[i+1]:]` lexicographically.

### Example

```
s = "banana"
suffixes:    0:"banana"  1:"anana"  2:"nana"  3:"ana"  4:"na"  5:"a"
sorted:      "a"(5) "ana"(3) "anana"(1) "banana"(0) "na"(4) "nana"(2)
sa = [5, 3, 1, 0, 4, 2]
```

## Naive O(n^2 log n) Construction

```
sa = sorted(range(n), key=lambda i: s[i:])
```

Each comparison is O(n). Python's Timsort: O(n log n) comparisons. Total
**O(n^2 log n)**. Fine for n < 10^4, dies for n ~ 10^6.

## Prefix-Doubling Construction (O(n log^2 n))

The key insight: after sorting by first character, sort by first 2 chars,
then 4, then 8, ... — only log n rounds.

```
rank = [s[i] for i in range(n)]    # initial: rank by first char
k = 1
while k < n:
    # sort by (rank[i], rank[i+k])
    sa = sorted(range(n), key=lambda i: (rank[i], rank[i+k] if i+k < n else -1))
    # rebuild ranks based on sorted order
    new_rank = [0] * n
    new_rank[sa[0]] = 0
    for i in range(1, n):
        prev = (rank[sa[i-1]], rank[sa[i-1]+k] if sa[i-1]+k < n else -1)
        curr = (rank[sa[i]], rank[sa[i]+k] if sa[i]+k < n else -1)
        new_rank[sa[i]] = new_rank[sa[i-1]] + (curr > prev)
    rank = new_rank
    if rank[sa[-1]] == n - 1:
        break  # all suffixes distinct
    k *= 2
```

Each round sorts n items with O(1) comparisons = O(n log n) per round,
log n rounds = **O(n log^2 n)** total. With radix sort: O(n log n).

## SA-IS / DC3 (True O(n))

Real-world implementations use **SA-IS** (Suffix Array — Induced Sorting,
Nong/Zhang/Chan 2009) or **DC3** (Difference Cover modulo 3, Kärkkäinen/
Sanders 2003) — both O(n) with small constants. The implementation is ~500
lines of code per algorithm. For learning purposes we use prefix doubling
(simpler, only slightly slower in practice).

## LCP Array via Kasai's Algorithm

The **LCP array** stores the longest common prefix between consecutive
sorted suffixes:

```
lcp[i] = |LCP(s[sa[i-1]:], s[sa[i]:])|
```

Kasai's algorithm computes LCP in **O(n)** given SA:

```
def kasai(s, sa):
    n = len(s)
    rank = [0] * n
    for i in range(n):
        rank[sa[i]] = i
    lcp = [0] * n
    h = 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h > 0:
                h -= 1
    return lcp
```

The amortized argument: `h` decreases by at most 1 per iteration of the outer
loop. The inner while increments `h` at most 2n times across all iterations.
**O(n)** total.

## Applications

### Substring Search: O(m log n)

To find pattern P in indexed text T: binary search the suffix array for the
range of suffixes starting with P. O(m log n) per query — m for each
comparison, log n binary search.

### Longest Repeated Substring: O(n)

= `max(lcp)`. The two suffixes at positions `sa[argmax]` and `sa[argmax-1]`
share that longest prefix.

### Longest Common Substring of A and B: O(n+m)

Concatenate `A + $ + B + #` (two distinct sentinels). Build SA + LCP. Find
the max LCP value where the two adjacent suffixes come from different
strings (one before `$`, one after).

### Number of Distinct Substrings: O(n)

```
n*(n+1)/2 - sum(lcp)
```

Total substrings of all lengths minus duplicates counted via LCP. Beautiful
identity.

## Failure Modes

### 1. Sentinel Confusion

When concatenating strings, the sentinel must be **smaller than any character
in the alphabet** for SA-IS-style algorithms to work. For ASCII text use
`\0` or `chr(0)`. Using `$` is conventional but fails if `$` appears in text.

### 2. Memory: 5n vs 4n vs 8n Bytes

Naive SA: 4 bytes per index (32-bit). With LCP: +4n. With BWT: +n. Total
~10n bytes for full indexing. For 10^9 char text: 10 GB. Modern systems
use **compressed suffix arrays** (FM-index) to drop to ~n bytes.

### 3. Build Time on Repetitive Inputs

Prefix doubling on `a^n` runs log n rounds, but each round examines ranks
that all tie until the very end. Constants are bad. SA-IS handles this
case in true linear time. Bug: implementations that don't break early on
all-distinct ranks die on `a^10^7`.

### 4. Off-by-One in LCP Index

Many references define `lcp[0] = 0` (no previous suffix). Others use 1-indexed
arrays. Mixing conventions silently breaks downstream code (especially
"longest common substring" finders).

### 5. Adversarial Text for Naive Sort

`s = "a^n"` makes Python's sort do O(n) comparisons each O(n) = O(n^2)
*per call to sort*. Total: O(n^3) without prefix doubling. Real defenders
against this: SA-IS or radix-sort-based prefix doubling.

## Checkpoint Questions

1. Why does the LCP array have n entries even though there are only n-1
   consecutive pairs? (Convention question.)
2. Walk through Kasai's algorithm on "banana". Why does `h` only decrease
   by at most 1 per step?
3. Prove: max(lcp) = length of the longest repeated substring.
4. Why is `sum(lcp)` exactly the number of *redundant* substring counts?
5. Given SA + LCP, how do you find the lexicographically k-th distinct
   substring? (Hint: use the LCP to count.)
6. For DNA matching, suffix array vs Aho-Corasick: when do you choose which?
