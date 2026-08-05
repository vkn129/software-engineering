# Day 117: Edit Distance (Levenshtein)

## What Edit Distance Computes

Given two strings `a` and `b`, the **Levenshtein distance** is the minimum
number of single-character edits to turn `a` into `b`. Allowed edits:

- **insert** a character
- **delete** a character
- **substitute** one character for another

Each edit costs 1 (variants weight differently).

## The Recurrence

Let `dp[i][j]` = edit distance between `a[:i]` and `b[:j]`.

```
dp[0][j] = j     (insert j characters)
dp[i][0] = i     (delete i characters)

if a[i-1] == b[j-1]:
    dp[i][j] = dp[i-1][j-1]                           (no cost)
else:
    dp[i][j] = 1 + min(
        dp[i-1][j],      # delete a[i-1]
        dp[i][j-1],      # insert b[j-1]
        dp[i-1][j-1]     # substitute a[i-1] -> b[j-1]
    )
```

State space: O(n·m). Work per state: O(1). Total: O(n·m).

## Why This Works

Look at the LAST operation in the optimal sequence aligning a[:i] with b[:j]:
- It was a **match** → answer = dp[i-1][j-1] (both indices advance).
- It was a **substitute** → 1 + dp[i-1][j-1].
- It was a **delete** of a[i-1] → 1 + dp[i-1][j] (a advances, b doesn't).
- It was an **insert** of b[j-1] → 1 + dp[i][j-1] (b advances, a doesn't).

Take the min. The recurrence enumerates every way the last edit could go.

## Math Notation

Let d(i, j) = Levenshtein distance between a[:i] and b[:j]. Then
```
d(i, j) = 0                                if i = j = 0
        = i                                if j = 0
        = j                                if i = 0
        = d(i-1, j-1)                      if a[i-1] = b[j-1]
        = 1 + min( d(i-1,j), d(i,j-1), d(i-1,j-1) )   otherwise
```

## Backtrace — Recover the Edit Sequence

After filling `dp`, walk from (n, m) back to (0, 0):
- match: a[i-1] == b[j-1] and dp[i][j] == dp[i-1][j-1] → "keep"
- sub:   dp[i][j] == dp[i-1][j-1] + 1 → "sub a[i-1] -> b[j-1]"
- del:   dp[i][j] == dp[i-1][j] + 1 → "del a[i-1]"
- ins:   dp[i][j] == dp[i][j-1] + 1 → "ins b[j-1]"

Reverse to get the operations from start to end.

## Why Spell Checkers Use It

A misspelled word "recieve" has edit distance:
- to "receive" = 1 (one substitution)
- to "relieve" = 2 (two substitutions)
- to "recover" = 4

Suggestion = nearest dictionary word within edit-distance threshold (usually 1-2).
For large dictionaries we use **BK-trees** or **Levenshtein automata** to avoid
computing distance to every word — but the underlying primitive is this DP.

## Space Compression

dp[i][j] depends only on dp[i-1][·] and dp[i][j-1]. We can keep two rows
of length m+1, alternating, for O(min(n,m)) space. Or one row with a
temporary saved value.

## The Wrong-But-Tempting Greedy

"Walk both strings, match where possible, substitute otherwise." Fails on
shifted strings.
- a = "abcdef", b = "bcdefg"
- Greedy: index 0 mismatch (a vs b) → substitute → "bbcdef" then match
  bcdef, then end with f vs g sub → 2 subs = 2.
- Optimal: delete 'a' (1 op) and insert 'g' (1 op) = 2.
  Same here, but try a = "kitten", b = "sitting":
- Greedy lockstep: k→s sub, i match, t match, t match, e→i sub, n match,
  then 'g' insert → 3. That's also optimal here.

The real failure: a = "ab", b = "ba".
- Greedy: a→b sub, b→a sub = 2.
- Optimal: 2 (swap is not a single op; need two subs). Same again.

Try a = "abc", b = "yabcd":
- Greedy: a→y sub, b→a sub, c→b sub, then add c, d → 5 ops.
- Optimal: insert 'y' at front (1), match a, match b, match c, insert 'd' (1) = 2.

Greedy locks step instead of considering shifts.

## Variants

- **Damerau-Levenshtein**: adds a "transpose adjacent" op (cost 1). Captures
  typos like "teh" → "the".
- **Weighted edits**: insert/delete/sub have different costs (e.g., based
  on keyboard adjacency).
- **Hamming**: only substitutions allowed; strings must be equal length.
- **LCS-derived**: edit distance with only insert+delete (no sub) is
  n + m - 2·LCS(a, b).

## Failure Modes

- **Off-by-one in indexing**: a[i-1] vs a[i] confusion when 1-indexing dp.
- **Wrong base case**: dp[0][0] = 0, NOT 1.
- **Computing distance to all dictionary words** for a spell checker; use
  pruning or specialised data structures.
- **Forgetting Unicode**: edit distance on bytes != edit distance on
  characters for non-ASCII text.

## Real-World Echoes

- **Spell checkers** (Aspell, Hunspell, browsers)
- **DNA sequence alignment** (Needleman-Wunsch is edit distance with sub
  scores)
- **Diff tools** (`diff`, git): minimal edit script
- **Plagiarism detection** at chunk level
- **Speech recognition** word error rate

## Checkpoint Questions

1. Derive the base cases `dp[0][j] = j` and `dp[i][0] = i` from first
   principles.
2. Why are 3 terms (delete, insert, substitute) needed when the strings
   could be transformed in many more ways?
3. How does edit-distance reduce to LCS when substitutions are forbidden?
4. What's the time and space complexity? Can you compute distance with
   O(min(n,m)) space?
5. For a 1M-word dictionary, why is edit distance per word too slow?
   What data structure helps?
6. Sketch how Damerau-Levenshtein adds the transpose case to the recurrence.
