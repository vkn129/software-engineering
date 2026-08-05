# Day 140: Manacher's Algorithm

## Why It Matters

Day 136 promised this day (`day-136/README.md:129`): the Z-array on a reversed
string gets you *some* palindrome facts, but Manacher's is the algorithm built
for the job. It computes, in **O(n) time and O(n) space**, the radius of the
longest palindrome centered at *every* position — all 2n+1 centers at once.

The output is not "the longest palindrome". The output is an **index**. Once you
hold the radius array you can answer, in O(1) each:

- Is `s[i..j]` a palindrome?
- What is the longest palindrome centered at position `i`?
- What is the longest palindromic prefix / suffix?

Where this actually runs:

- **Bioinformatics** — DNA reverse-complement palindromes mark restriction-enzyme
  sites and RNA hairpin loops. Genomes are 10^9 bases; O(n^2) is not an option.
- **String-algorithm pipelines** — palindromic factorization, palindromic trees
  (eertree), and border analysis all take the radius array as input.
- **Compression** — LZ77-family encoders scan for reversed repeats; the radius
  array is a cheap prefilter.
- **Interviews / contests** — the canonical "O(n^2) → O(n) by reusing work"
  example, in the same family as KMP and the Z-algorithm (day-136).

## Relationship to Day 120 — Read This First

`day-120` owns **palindrome DP**: longest palindromic *subsequence* (interval DP),
the O(n^2) palindromic-substring table, minimum palindrome cuts, minimum
insertions. It also ships a compact working `manacher()` at
`day-120/palindrome_dp.py:107` as the fast path for one specific question —
"give me the longest palindromic substring".

This day is the other direction. We do **not** re-derive palindrome DP and we do
not re-solve day-120's problems. We derive Manacher's from first principles and
treat its output as a data structure:

| | day-120 | day-140 (here) |
|---|---|---|
| Frame | palindromes as a DP recurrence | palindromes as an O(n) **index** |
| Product | one answer (longest substring, min cuts, ...) | the radius array itself |
| `is_palindrome(i, j)` | O(1) query, **O(n^2) space** table | O(1) query, **O(n) space** |
| Even/odd split | handled by the DP table's loops | handled by the interleave trick, **derived** |
| Why it's linear | asserted | amortized argument on `R`, proved below |

The O(n^2) DP table and the radius array answer the *same* query in the same
O(1). The difference is 10^12 booleans versus 2·10^6 integers for a megabyte of
text. That is the entire reason this algorithm exists.

## The Problem With Even Lengths

Palindromes come in two shapes and they do not share a center:

```
"aba"   -> odd  length, center is the character 'b'      (index 1)
"abba"  -> even length, center is the *gap* between the two 'b's
```

An odd palindrome is centered **on** a character. An even palindrome is centered
**between** two characters. A naive implementation therefore writes the whole
algorithm twice, once per parity. That is the even/odd problem.

### Solution 1 — Write It Twice (`d1` and `d2`)

The honest baseline. Two arrays:

- `d1[i]` = number of odd palindromes centered at `i`.
  The longest has length `2*d1[i] - 1`. Always `>= 1` (a single char).
- `d2[i]` = number of even palindromes centered in the gap **before** `i`
  (between `s[i-1]` and `s[i]`). The longest has length `2*d2[i]`.
  `d2[0] = 0` always — there is no gap before the string.

```
s  =  a  b  b  a
d1 = [1, 1, 1, 1]      # no odd palindrome longer than one char
d2 = [0, 0, 2, 0]      # d2[2] = 2  ->  even palindrome of length 4 = "abba"
```

Both loops have identical structure but different index arithmetic — `d2` is
where the off-by-one bugs live. `manacher.py` implements both so you can see the
duplication that motivates the fix.

### Solution 2 — The Interleave Trick (One Loop)

Insert a separator between every pair of characters, and at both ends:

```
s = "abba"
t = "^ # a # b # b # a # $"
     0 1 2 3 4 5 6 7 8 9 10
```

**Why every palindrome in `t` is now odd.** Ignoring the guards, `t` alternates
strictly: separator, character, separator, character, ..., separator. Take any
palindromic window of `t` with first index `a` and last index `b`. A palindrome
satisfies `a + b = 2 * center`, so `a` and `b` have the same parity exactly when
the center is an integer index. Same parity means both ends are separators or
both are real characters — and in a strictly alternating string, a window whose
ends match in kind has odd length. **Every palindrome in `t` has odd length, so
every palindrome in `t` has a single integer center.** One loop suffices.

This is not a hack that "happens to work". It is a bijection:

- center in `t` at an **even** index `2j+2` = the real character `s[j]`
  → the odd palindromes of `s` centered at `j`
- center in `t` at an **odd** index `2j+1` = the gap before `s[j]`
  → the even palindromes of `s` centered in that gap

**Why the radius reads off as a length.** Define `P[i]` as the radius in `t`
*excluding* the center. The palindrome spans `t[i-P[i] .. i+P[i]]`, which is
`2*P[i]+1` characters of `t`. Those alternate, so exactly `P[i]` of them are real
characters of `s` — check it on `"aba"` (center on `b`, `P=3`, real chars
`a,b,a`) and on `"abba"` (center on the middle `#`, `P=4`, real chars
`a,b,b,a`). Hence:

> `P[i]` is **exactly** the length, in `s`, of the longest palindrome centered
> at that position.

No division, no parity case at the call site. That is why the trick is worth its
2x memory.

The guards `^` and `$` are chosen to appear nowhere else, so the expansion loop
`while t[i+P+1] == t[i-P-1]` fails at the boundary on its own. Without them you
need an explicit bounds check on every iteration of the hot loop.

### Recovering `d1` / `d2` From `P`

```
d1[j] = (P[2*j + 2] + 1) // 2       # center on character j
d2[j] =  P[2*j + 1]      // 2       # center in the gap before character j
```

`manacher.py` asserts these agree with the hand-written two-loop version on
random inputs. If your interleave indexing is wrong, that assertion is where you
find out.

## The Mirror Trick — Why It Is Linear

Maintain the palindrome found so far that reaches **furthest right**: its center
`C` and its right edge `R = C + P[C]`. When we arrive at a new center `i`:

- **`i >= R`** — outside the known box. No information. Start at radius 0 and
  expand by direct character comparison.
- **`i < R`** — inside the box. Let `m = 2*C - i` be `i`'s mirror across `C`.
  Everything in `[C-P[C], R]` is a palindrome around `C`, so the neighbourhood
  of `i` is a mirror image of the neighbourhood of `m`. Initialize:

```
P[i] = min(R - i, P[m])
```

then keep expanding from there.

Three cases justify that `min`:

1. **`P[m] < R - i`** — the mirror's palindrome sits strictly inside the box. The
   mirror image is exact, so `P[i] = P[m]` and it **cannot** be longer: if it
   were, reflecting that longer palindrome back across `C` would have made
   `P[m]` longer too, and `P[m]` is already final. No expansion needed.
2. **`P[m] > R - i`** — the mirror's palindrome pokes out past the box's *left*
   edge. Only the part inside the box is mirrored knowledge. We can trust
   `R - i` and no more; beyond `R` the characters have never been compared.
3. **`P[m] == R - i`** — exactly reaches the edge. Trustworthy up to `R`, and it
   may or may not extend further. Start at `R - i` and try to expand.

### Case 2 Is Not Theoretical — `s = "abab"`

`"abab"` is the **shortest** string that breaks if you write `P[i] = P[m]`
instead of `min(R - i, P[m])`:

```
s = "abab"
t = "^ # a # b # a # b # $"
     0 1 2 3 4 5 6 7 8 9 10

correct: P = [0, 0, 1, 0, 3, 0, 3, 0, 1, 0, 0]
no-min:  P = [0, 0, 1, 0, 3, 0, 3, 0, 3, 0, 0]
                                    ^^^ wrong
```

At `i = 8` the box is `C = 6, R = 9`. The mirror is `m = 2*6 - 8 = 4`, and
`P[4] = 3` — that is `"aba"` around `t[4]`, which extends past the box's left
edge. But `R - i = 1`. The truth is `P[8] = 1` (`s[3] = 'b'` alone). Copying
`P[m]` claims a length-3 palindrome centered at the last character of a
4-character string — running off the end of the string entirely. `manacher.py`
runs both variants side by side and reports this.

### The O(n) Argument

Every character comparison in the expansion loop has exactly two outcomes:

- **Success** → `P[i]` grows. We only ever expand strictly past `R` (everything
  at or before `R` was *copied* from the mirror, not compared), so each
  successful comparison pushes `R` one step right.
- **Failure** → the expansion loop for this `i` ends. At most one failure per `i`.

`R` starts at 0, never decreases, and is bounded by `|t| = 2n+3`. So successes
total `O(n)` and failures total `O(n)` (one per center). **Total comparisons
`O(n)`** even though any individual center may expand a long way.

This is the same amortized argument as the Z-algorithm's `r` pointer
(`day-136/README.md:58`) and KMP's shift counter. Once you have seen it three
times it stops feeling like magic: *a monotone pointer bounds the total work no
matter how spiky the per-step work is.*

## The Radius Array As An Index

With `P` in hand:

**O(1) palindrome test.** The `t`-center of the `s`-substring `s[i..j]` is
`i + j + 2`, and the substring's length is `j - i + 1`. So:

```
is_palindrome(i, j)  ==  P[i + j + 2] >= j - i + 1
```

One array lookup and one comparison. No table, no recursion.

**All maximal palindromes.** For each center, `P[i]` gives its longest
palindrome. There are `2n+1` centers, so at most `2n+1` *maximal* palindromes —
even though a string can contain `Θ(n^2)` palindromic substrings, every one of
them is obtained by trimming equal numbers of characters off both ends of one of
these `2n+1`. That is the compression: a `Θ(n^2)` set described in `O(n)` space.

**Longest palindromic prefix / suffix.** A prefix palindrome is one whose
occurrence reaches the left guard: `i - P[i] == 1`. A suffix palindrome reaches
the right guard: `i + P[i] == len(t) - 2`. One scan gives both. The longest
palindromic prefix is exactly what `shortest_palindrome` needs — prepend the
reverse of everything after it and you have the shortest palindrome having `s`
as a prefix.

## Complexity

| Operation | Time | Space | Notes |
|---|---|---|---|
| Naive: check every substring | O(n^3) | O(1) | 2 nested loops + O(n) check |
| Naive: expand around all centers | O(n^2) | O(1) | 2n+1 centers, O(n) each |
| day-120 DP table | O(n^2) | O(n^2) | O(1) queries, quadratic memory |
| Two-loop `d1`/`d2` Manacher | O(n) | O(n) | correct, duplicated code |
| Interleaved Manacher | O(n) | O(n) | one loop, `2n+3` transformed chars |
| Query `is_palindrome(i, j)` | O(1) | — | from the radius array |
| Enumerate maximal palindromes | O(n) | O(n) | `2n+1` of them |
| Longest palindromic substring | O(n) | O(n) | `max(P)` |

Constant factors: the interleaved version does roughly 2x the character
comparisons of the two-loop version, because `t` is twice as long and half of it
is separators. It is chosen for correctness-per-line-of-code, not raw speed.
Production string libraries that care use the `d1`/`d2` form.

## Failure Modes

1. **Dropping the `min`.** Shown above with `s = "abab"`. Produces radii that
   claim palindromes running off the end of the string. In Python you get a
   wrong answer; in C you get an out-of-bounds read.

2. **Index translation off-by-one.** With `t = "^#" + "#".join(s) + "#$"`,
   character `s[j]` lives at `t[2j+2]` and the gap before `s[j]` at `t[2j+1]`.
   Using `t = "#" + "#".join(s) + "#"` (no guards) shifts everything by 2 and
   every downstream formula silently changes. Pick one transform, never mix.

3. **Guard character collision.** If `^` or `$` occurs in `s`, expansion can walk
   off the array. Use characters outside the alphabet, or drop the guards and pay
   for explicit bounds checks. Binary data has no safe ASCII guard — bounds-check
   there. Same trap as the Z-algorithm sentinel (`day-136/README.md:90`).

4. **`R` initialized wrong.** `C = R = 0` with the loop running `1 .. len(t)-2`
   is correct for the guarded transform. Starting the loop at 0, or initializing
   `R = -1`, changes whether `i < R` is ever true early on. The symptom is a
   *correct* answer that is quietly O(n^2) — it never fails a test, it just gets
   slow on adversarial input like `"aaaa...a"`.

5. **Unicode.** `len(s)` counts code points, not grapheme clusters. `"é"` may be
   one code point or two (`e` + combining acute), and reversing across a
   combining mark reorders it onto the wrong base character. Normalize (NFC)
   before running, or operate on grapheme clusters.

6. **Assuming Manacher finds palindromic *subsequences*.** It does not. It finds
   contiguous substrings only. Longest palindromic subsequence is day-120's
   interval DP at O(n^2); no linear algorithm is known for it.

7. **Reverse-complement palindromes.** In DNA, `"GAATTC"` is a palindrome under
   *reverse complement* (A↔T, C↔G), not under plain reversal. The expansion loop
   transfers if you swap `==` for a complement predicate — but the odd-center
   case degenerates, because no base is its own complement, so all
   reverse-complement palindromes are even-length. Do not assume the string
   version transfers for free.

## Checkpoint Questions

1. Prove that every palindromic window of the interleaved string `t` has odd
   length. Where does the argument use the fact that separators and real
   characters strictly alternate?
2. `P[i]` is a radius in `t` but equals a *length* in `s`. Do the counting
   argument on `"aba"` and on `"abba"`: of the `2*P[i]+1` characters of `t`
   inside the palindrome, why are exactly `P[i]` of them real characters of `s`?
3. In case 1 of the mirror trick (`P[m] < R - i`) we skip expansion entirely.
   Prove expansion could not have succeeded — reflect the hypothetical longer
   palindrome back across `C` and derive a contradiction.
4. Trace `s = "abab"` by hand through `i = 4, 6, 8`. Show exactly where
   `min(R - i, P[m])` fires, what wrong answer the no-`min` version gives, and
   why that is not merely wrong but memory-unsafe in C.
5. The expansion loop can run `Θ(n)` times for a single `i`. Explain why the
   total is still `O(n)`. Which quantity is the potential function?
6. You have `P` for `s`. Give O(1) formulas for: (a) is `s[i..j]` a palindrome,
   (b) the longest palindrome centered on character `i`, (c) the longest
   palindrome centered in the gap before character `i`.
7. A string of length `n` can contain `Θ(n^2)` distinct palindromic substrings
   (give an example). The radius array is `O(n)` numbers. Explain how `O(n)`
   numbers describe `Θ(n^2)` objects without losing information.
8. When would you still choose day-120's `O(n^2)` DP table over the radius array?
   Name a query the table answers directly that the radius array does not.
