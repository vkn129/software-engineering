# Day 120: Palindrome DP

## Why Palindromes Get Their Own Day

Palindromes show up everywhere: DNA hairpin loops, compression dictionaries,
typo detection, error-correcting codes. The reason DP dominates here is that
palindromes have **two-sided recursive structure** — a palindrome is a
character + a smaller palindrome + the same character.

That structure invites two distinct DP families:

1. **Longest Palindromic Subsequence (LPS)** — characters need not be
   contiguous. Classic 2D DP, equivalent to LCS(s, reverse(s)).
2. **Longest Palindromic Substring** — characters must be contiguous.
   Naive DP is O(n^2). **Manacher's algorithm** does it in **O(n)** by
   reusing palindrome radii across centers.

Most DP bugs are state design bugs. Get the state right and the recurrence
writes itself.

## State Design: LPS

**State**: `dp[i][j]` = length of longest palindromic subsequence of `s[i..j]`
(inclusive).

**Recurrence**:
- `s[i] == s[j]`: `dp[i][j] = dp[i+1][j-1] + 2`
- `s[i] != s[j]`: `dp[i][j] = max(dp[i+1][j], dp[i][j-1])`

**Base**: `dp[i][i] = 1` for all i. `dp[i][i-1] = 0` (empty).

**Order**: fill by increasing length of substring (`j - i + 1`).
This is **interval DP** — same skeleton as MCM (day 121).

### Subproblem Dependency Graph

```
   dp[i][j]
   /  |  \
  /   |   \
dp[i+1][j-1]  dp[i+1][j]  dp[i][j-1]
```

Each cell depends on three smaller cells — one diagonal, one below, one left.
Hence the increasing-length traversal order: every dependency is already
computed.

## State Design: Longest Palindromic Substring (O(n^2))

**State**: `dp[i][j]` = True iff `s[i..j]` is a palindrome.

**Recurrence**: `dp[i][j] = (s[i] == s[j]) AND (j-i < 2 OR dp[i+1][j-1])`

This works but uses O(n^2) time and space. Manacher's does the same job
in O(n) — by **never re-comparing characters already known to match**.

## Manacher's Algorithm

The key insight: if you know palindrome radii for centers to the left,
you can **transfer** that knowledge to mirrored centers on the right —
**without re-comparing**.

### Step 1: Eliminate the Odd/Even Case Split

Insert sentinels between every character:

```
s  = "abba"
t  = "^#a#b#b#a#$"
```

Now every palindrome in `t` has odd length. `^` and `$` are unique
boundaries to prevent index overrun.

### Step 2: Track Center C and Right Edge R

`P[i]` = radius of longest palindrome centered at `t[i]`.
Maintain `C` (center of current rightmost palindrome) and `R = C + P[C]`.

For each i:
- **Mirror index**: `i_mirror = 2*C - i`
- **If i < R**: initialize `P[i] = min(R - i, P[i_mirror])`
- **Otherwise**: `P[i] = 0`
- **Expand** from this initial radius using direct character comparison.
- **Update C, R** if `i + P[i] > R`.

### Why It's O(n)

Each character comparison either **extends R** (advances right edge) or
**fails once**. R only moves right. Total comparisons: O(n).

This amortized argument is identical to the one for Z-algorithm or KMP.

### Subproblem Dependency Graph

```
   P[i_mirror]  (already known)
        |
        v
     P[i]  --(expansion)--> P[i+1], P[i+2], ...
        |
        v
     update C, R
```

No table — just a left-to-right sweep with one pointer (R) that never
goes backward.

## Pitfalls

1. **LPS vs LCS confusion**: LPS of s = LCS(s, reverse(s)). True, but
   wastes a factor of 2 in space if you don't notice.
2. **Manacher index translation**: position in `t` is `2*i + 2` for
   character at position `i` in `s` (with `^` prepended). Off-by-one
   bugs here cost hours.
3. **Forgetting that even-length palindromes exist**: in the naive
   substring DP, you must check both odd and even centers, or use
   the table-based version.
4. **State order**: filling `dp[i][j]` before `dp[i+1][j-1]` is wrong.
   Length-major order is mandatory for interval DP.

## Real-World Usage

| System | Application | Why Palindrome DP |
|--------|-------------|-------------------|
| **Bioinformatics** | RNA secondary structure prediction | Hairpin loops are palindromic |
| **Text editors** | Auto-suggest palindrome typo fixes | LPS distance |
| **Compression** | Dictionary palindrome runs (LZ77 variants) | Substring matching |
| **Cryptography** | Reversibility checks in block ciphers | Symmetric structure |
| **DNA assembly** | Reverse complement matching | Palindrome ≈ reverse complement |

## Checkpoint Questions

1. Why does LPS take O(n^2) time but Manacher's takes O(n) for the
   substring version? What does the substring problem give you that
   the subsequence problem does not?
2. In Manacher's, what is the role of the sentinel characters `^`
   and `$`? What goes wrong if you omit them?
3. Construct a string where the naive O(n^2) palindromic substring
   DP performs ~n^2/2 character comparisons but Manacher's performs
   ~2n.
4. If you wanted to count **all** palindromic substrings (not just
   the longest), how would you modify Manacher's?
5. Why is LPS equivalent to LCS(s, reverse(s))? Prove it formally.
