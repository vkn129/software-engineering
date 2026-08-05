# Day 136: Z-Algorithm

## Why Z Matters

KMP is brilliant but its mental model — failure function as "longest proper
prefix-suffix" — is twisty. The **Z-array** asks a simpler question:

> For each position i, what's the longest substring starting at i that matches
> a prefix of the string?

Same O(n) complexity, but the array is often easier to reason about and
generalize. Z shows up in:

- **String matching** (concatenate `P$T`, scan Z-array for hits of length |P|)
- **Longest common prefix of suffix-pairs** in suffix array construction
- **Period detection** (similar to KMP but with a different invariant)
- **Tandem repeat finding** (DNA microsatellites)
- **String compression analysis** (LZ77 lookahead matches)

## Definition

For string `s` of length `n`, define `Z[i]` for `i >= 1` as:

```
Z[i] = length of the longest substring starting at i
       that matches a prefix of s
```

By convention `Z[0] = n` (the whole string trivially matches its own prefix —
some references leave it undefined; we set it to n for cleanliness).

## Example

```
s    = "aabcaabxaaaz"
       0 1 2 3 4 5 6 7 8 9 ...
Z    = [12, 1, 0, 0, 3, 1, 0, 0, 2, 2, 1, 0]
```

- Z[4]=3 because `s[4:7]="aab"` matches prefix `s[0:3]="aab"`.
- Z[1]=1 because `s[1]='a'` matches `s[0]='a'`, but `s[2]='b' != s[1]='a'`.

## Construction — The Z-Box

Maintain a window `[l, r]` representing the rightmost-extending Z-match found
so far. When computing Z[i]:

**Case A**: `i > r` (we're outside the box). Start fresh — extend match
character-by-character from position 0 and i.

**Case B**: `i <= r` (we're inside the box). Let `k = i - l`. We already know
`Z[k]` (computed earlier). Two sub-cases:
- If `Z[k] < r - i + 1`: copy `Z[i] = Z[k]` directly. We can't possibly extend
  further because we'd already have known about it.
- Else: tentatively set `Z[i] = r - i + 1` and try extending from `r`.

Each comparison either succeeds (extending `r`) or fails (terminates extension).
`r` increases monotonically to n. Total work is **O(n)**.

```
def z_array(s):
    n = len(s)
    z = [0] * n
    z[0] = n
    l = r = 0
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    return z
```

## String Matching with Z

To find pattern P in text T:

1. Concatenate `s = P + sentinel + T` where sentinel is a char not in either.
2. Compute Z-array of `s`.
3. Any position `i` where `Z[i] == len(P)` corresponds to a match starting at
   `i - len(P) - 1` in T.

Total: **O(n + m)** time and space — same asymptotic as KMP, slightly more
memory (you store the whole Z-array).

## Failure Modes

### 1. Forgetting the Sentinel

If P and T share characters, a Z-value from inside P matching into P alone
could equal |P| spuriously. The sentinel guarantees the match must straddle
the boundary into T. Use a character genuinely outside the alphabet (`\0`,
`$`, or any byte > 0x7F if your alphabet is ASCII).

### 2. Z[0] Convention

Some treatments leave `Z[0]` undefined. Some set it to 0. Some to n. Pick one
and document it. Mixing conventions across libraries silently breaks matching
code.

### 3. Where Z Goes Wrong vs KMP

Z requires O(n+m) **memory** (the whole array). KMP only needs O(m) (failure
function). For massive texts streamed character-at-a-time, KMP is better —
Z requires random access to s.

### 4. Catastrophic on "Hyper-Periodic" Strings?

Both KMP and Z are O(n+m) worst case. There's no input that makes Z degrade.
But the *constant factor* of Z is slightly worse than KMP in practice for
short patterns because of the `min(r-i+1, z[i-l])` branch in the inner loop.

## Z vs KMP: Same Result, Different Lens

The KMP failure function and Z-array are **equivalent** in information content
— you can derive one from the other in O(n). Choose based on:

- **Z**: easier to teach, generalizes well to "longest match at position i"
  problems. Better for offline/batched analysis.
- **KMP**: smaller memory, streaming-friendly. Used in production string libs.

## Variants

### Z-Array on Reversed String

To find palindromes or right-anchored prefix matches, run Z on `reverse(s)`.
This is the basis for some palindrome algorithms (though Manacher (Day 140)
is better for that specifically).

### Z + Suffix Array

In suffix array construction (Day 138), the Z-array of certain transformed
strings gives the **LCP array** efficiently. Kasai's algorithm uses a
different trick, but Z is foundational.

## Checkpoint Questions

1. Why does setting `z[i] = min(r - i + 1, z[i - l])` work without breaking
   correctness? Walk through both sub-cases.
2. Why is the inner `while` loop's total work O(n) across all i? (Amortized
   argument on r.)
3. Construct an n=10 string where Z[i] > 0 for every i >= 1.
4. Convert Z-array to KMP failure function in your head: given Z, what's the
   relationship?
5. Why do you need a sentinel for pattern matching? Show an example where
   omitting it gives a wrong answer.
6. Compare Z and KMP for searching pattern "aaa" in "aaaaaaaa". Same number
   of comparisons or different?
