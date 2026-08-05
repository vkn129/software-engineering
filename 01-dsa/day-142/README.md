# Day 142: Burrows-Wheeler Transform

## Why It Matters

BWT is a reversible permutation of a string that clusters similar contexts
together. Repetitive data becomes runs of identical characters — perfect
fodder for run-length + entropy coding.

- **bzip2**: BWT -> Move-To-Front -> Run-Length -> Huffman. Beats gzip on
  natural text by 20-30%.
- **FM-index**: BWT plus a small auxiliary structure gives O(m) substring
  queries on a compressed string. Used by Bowtie, BWA in DNA alignment.
- **Genome assembly**: SA + BWT + LCP arrays are the substrate of modern
  short-read aligners (Burrows-Wheeler aligner).

The remarkable property: **BWT is invertible** from just the transformed
string plus the index of the original row.

## The Construction

1. Append a unique sentinel `$` (smaller than every character) to S.
2. Form all rotations of S.
3. Sort them lexicographically.
4. The last column L is the BWT.

Example for S = "banana$":

```
rotations:                  sorted rotations (matrix M):
banana$                     $banana       L = "annb$aa"
anana$b                     a$banan
nana$ba                     ana$ban
ana$ban                     anana$b
na$bana                     banana$
a$banan                     na$bana
$banana                     nana$ba
```

Building rotations naively is O(n^2) space. **Use a suffix array**: the BWT
is `S[SA[i] - 1]` (mod n) for each i.

## The Inversion (the magic part)

Given L (the BWT) and the index r of the original row:

**Last-First (LF) mapping**: the i-th occurrence of a character c in L
corresponds to the i-th occurrence of c in F (sorted first column). This holds
because rotations are sorted, so rows starting with c appear in the same
relative order as rows where c precedes the row's prefix.

```
F = sorted(L)            # the first column
def LF(i):               # row i's last char -> its position as first char
    c = L[i]
    rank = count of L[i] equal to c in L[0..i-1]
    return position in F where the (rank+1)-th c lives
```

Walking LF from r reconstructs S in reverse.

## Move-To-Front Transform

BWT output has clusters of identical chars. MTF turns clusters into runs of 0:

- Maintain a list of all symbols.
- For each input char c, output its current index, then move c to position 0.

After MTF on a BWT output, you get many small numbers — Huffman or
arithmetic coding squeezes them tight.

## Complexity

| Operation       | Time           | Notes                          |
|-----------------|----------------|--------------------------------|
| BWT (suffix array) | O(n log n)  | Or O(n) with DC3/SA-IS         |
| BWT naive       | O(n^2 log n)   | Sort all rotations             |
| Inverse BWT     | O(n)           | Build rank tables, walk LF     |
| MTF             | O(n * \|Σ\|)   | Smaller Σ -> faster            |

## Failure Modes

- **Missing sentinel**: if `$` is not unique-smallest, sort is ambiguous and
  inversion may fail. Pick a byte that does not appear in input.
- **Stable sort**: rotation sort must be deterministic — use Python's stable
  `sorted` or sort by suffix array.
- **Off-by-one in LF**: rank is 0-indexed count of prior occurrences, not
  1-indexed.
- **bzip2 reality**: real bzip2 uses block-by-block (~900KB), RLE pre-pass,
  Huffman selection per block. The textbook BWT is just the first stage.

## Checkpoint Questions

1. Why does the BWT cluster similar characters?
2. Why is the sentinel needed for unique invertibility?
3. State the LF property and prove it from rotation sort order.
4. What is the worst case input for BWT compression?
5. Why does MTF help after BWT but hurt before it?
6. How does the FM-index use BWT for O(m) substring search?
