# Day 55: Suffix Arrays — Pattern Matching in O(m + log n)

## Why This Exists

A suffix array is a sorted array of all suffix starting positions in a string. It enables O(m log n) substring search (m = pattern length, n = string length) using binary search, and O(m + log n) with an LCP array.

This structure powers:
- **Bioinformatics**: Finding gene sequences in 3-billion-character genomes
- **Text editors**: Fast search-and-replace across massive files
- **Compression**: Burrows-Wheeler Transform (BWT) — used in bzip2
- **Plagiarism detection**: Longest common substring between documents

Suffix trees can do everything suffix arrays do in O(m) lookup, but suffix arrays use 4-8x less memory and have better cache behavior. In practice, suffix arrays dominate.

## Theory (40 min)

### Construction

For string "banana$":

```
Suffixes:         Sorted:              Suffix Array:
0: banana$        5: a$                [5, 3, 1, 0, 4, 2]
1: anana$         3: ana$
2: nana$          1: anana$
3: ana$           0: banana$
4: na$            4: na$
5: a$             2: nana$
```

Naive construction: generate all suffixes, sort them → O(n² log n).
Smarter: O(n log² n) with prefix doubling, O(n) with SA-IS.

### LCP Array (Longest Common Prefix)

LCP[i] = length of longest common prefix between suffix[i] and suffix[i-1] in the sorted order.

Used for:
- Longest repeated substring = max(LCP)
- Number of distinct substrings = n*(n+1)/2 - sum(LCP)
- Converting suffix array into a suffix tree

### Burrows-Wheeler Transform

BWT reorders characters so that repeated patterns cluster together, making the output highly compressible. The BWT of a string can be computed from its suffix array in O(n).

## Practice (20 min)

See `practice.py` — 5 exercises on suffix arrays, LCP, and pattern matching.

## Daily Project

`suffix_structures.py` implements suffix array construction, LCP computation, pattern search, and BWT.

## Checkpoint Questions

1. Why do suffix arrays use less memory than suffix trees?
2. How does binary search on a suffix array find a pattern?
3. What does the LCP array tell you about repeated substrings?
4. Why is the Burrows-Wheeler Transform useful for compression?
5. When would you choose a suffix array over a trie for pattern matching?
