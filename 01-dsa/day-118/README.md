# Day 118: LCS and LIS

## Longest Common Subsequence (LCS)

Given strings `a` and `b`, find the longest sequence that appears in both
as a (not-necessarily contiguous) subsequence.

```
a = "ABCBDAB"
b = "BDCAB"
LCS = "BCAB" or "BDAB"  (length 4)
```

### Recurrence

`dp[i][j]` = length of LCS of `a[:i]` and `b[:j]`.

```
dp[0][j] = 0 for all j        (empty a -> empty LCS)
dp[i][0] = 0 for all i

if a[i-1] == b[j-1]:
    dp[i][j] = 1 + dp[i-1][j-1]
else:
    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
```

### Math Notation

Let L(i, j) = |LCS(a[:i], b[:j])|.
```
L(0, j) = L(i, 0) = 0
L(i, j) = L(i-1, j-1) + 1                 if a[i-1] = b[j-1]
        = max(L(i-1, j), L(i, j-1))       otherwise
```

State space: O(n·m). Work per state: O(1). Total: O(n·m) time, O(n·m) space.
With rolling rows: O(min(n,m)) space (but loses easy backtrace).

### Backtrace to Recover the LCS

Walk from (n, m) toward (0, 0):
- match diagonal: a[i-1] == b[j-1] -> prepend, move (i-1, j-1)
- else: move in direction of the larger neighbor

### Wrong-but-tempting greedy for LCS

"Match the first equal character then recurse." Fails on
- a = "AABB", b = "BBAA"
- Greedy matches A at a[0] vs b[2]; remaining a="ABB" vs b="AA" -> 1 more A
  -> length 2.
- Optimal: "AA" or "BB" -> length 2. (Greedy ties here.)

Try a = "ABCDGH", b = "AEDFHR":
- Greedy: match A (a[0], b[0]); now find longest of "BCDGH" vs "EDFHR".
- Eventually finds "ADH" -> 3. Optimal is also 3.

LCS doesn't have a glaring single-greedy failure, but it has no
linear-time algorithm either — DP is the right tool.

## Longest Increasing Subsequence (LIS)

Given an array, find the longest strictly increasing subsequence.

```
[10, 9, 2, 5, 3, 7, 101, 18]  ->  LIS = [2, 3, 7, 18]  (length 4)
```

### Naive DP — O(n^2)

`dp[i]` = length of LIS ending at index i.

```
dp[i] = 1 + max(dp[j] for j < i if a[j] < a[i])
        = 1 if no such j
answer = max(dp)
```

State space: O(n). Work per state: O(n). Total: O(n^2).

### Patience Sorting — O(n log n)

Card-game intuition: deal cards left to right, place each on the leftmost
pile whose top is >= the card (or start a new pile). The number of piles
at the end equals the LIS length.

In code we maintain `tails[k]` = smallest possible tail of an increasing
subsequence of length k+1 so far.

```
tails = []
for x in a:
    pos = bisect_left(tails, x)
    if pos == len(tails):
        tails.append(x)        # extend
    else:
        tails[pos] = x         # improve
return len(tails)
```

Each insertion is O(log n); total O(n log n).

**Note**: `tails` is NOT a valid subsequence — it's just a length tracker.
To recover the actual subsequence we also store back-pointers.

### Why It Works (intuition)

`tails[k]` = the smallest number that ends some increasing subsequence of
length k+1 seen so far. Replacing a larger end with a smaller one never
shortens what's possible. The list `tails` is always strictly increasing,
so binary search applies.

### Wrong-but-tempting greedy for LIS

"Take elements one by one if they're larger than the last taken." Fails on
- a = [3, 1, 2, 4]
- Greedy: 3, then skip 1, skip 2, take 4 -> [3, 4] length 2.
- Optimal: [1, 2, 4] length 3.

Greedy is too eager to start with a large value. LIS requires considering
restarting with a smaller value (patience sorting captures this).

## Failure Modes

- **LCS confusion with longest common substring** (contiguous). Different
  recurrence: max over the diagonals.
- **LIS strict vs non-strict**: bisect_left for strict, bisect_right for
  non-strict.
- **Recovering the LIS from patience sorting**: the `tails` array is NOT
  the LIS. Use predecessor pointers.
- **All equal elements** in LIS: tails stays length 1 (strict) or grows
  (non-strict).
- **Off-by-one in DP indexing**: confusing prefix length with last-included
  index.

## Real-World Echoes

- **DNA / protein sequence alignment** — Smith-Waterman is a weighted LCS
- **Diff tools** — minimal edit script = n + m - 2·LCS
- **Stock trading** — longest sequence of increasing prices
- **Plagiarism detection** — long shared subsequences signal copying
- **File patching** — Myers diff algorithm reduces to LCS

## Checkpoint Questions

1. Why is LCS not the same as longest common substring? How do recurrences
   differ?
2. Derive O(n + m) space LCS with backtrace (Hirschberg's algorithm sketch).
3. Why does patience sorting work? Prove tails is always strictly
   increasing.
4. How would you modify LIS for strictly DECREASING subsequence?
5. State edit distance in terms of LCS (when only insert+delete are
   allowed).
6. Given an array, how would you count the NUMBER of distinct LIS?
