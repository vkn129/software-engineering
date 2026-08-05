# Day 110: Staircase Search in Sorted 2D Matrices

## Scope, Stated First

This day is about matrices that are sorted **along each row and independently
along each column**, and nothing stronger:

```
M[r][c] <= M[r][c+1]        every row ascends left to right
M[r][c] <= M[r+1][c]        every column ascends top to bottom
```

That is the *only* guarantee. Two things follow immediately:

- **You cannot flatten it.** Reading row-major gives `1, 4, 7, 11, 2, 5, ...`
  — not sorted. The flatten-and-binary-search trick belongs to the **globally
  sorted** matrix (every row starts above the previous row's end), and Day 020
  owns it (`day-020/practice.py:129`). Applying it here returns wrong answers,
  not slow answers.
- **Rotated arrays are a different problem entirely** and also belong to
  Day 020.

Read Day 020 first if either of those is fuzzy. Everything below assumes the
weaker row+column condition.

## Why It Matters

The row+column-sorted shape is what you get whenever a 2D table is generated
by a function monotone in **both** arguments — which is extremely common and
almost never labelled as "a sorted matrix":

- **Young tableaux**: the classic combinatorial object; this search is the
  standard membership test.
- **Monotone DP tables**: `dp[i][j]` = cost using first `i` of one resource
  and `j` of another. More resource never costs more, so the table is
  row+column sorted and "is cost `X` achievable?" is exactly this search.
- **Multiplication / cost tables**: `M[i][j] = i * j` over positive ranges,
  the "kth smallest in the n x n multiplication table" problem. The table is
  never materialised; the staircase walks it implicitly.
- **Two-key database grids**: rows ordered by one indexed column, columns by
  another; each cell an aggregate. Sorted both ways, sorted neither globally.
- **Summed-area tables and cumulative histograms**: prefix sums over
  non-negative values are monotone in both indices by construction.

Nobody ships "staircase search" as a named library function. The pattern shows
up as three lines inside a much bigger routine, which is precisely why it is
worth being able to recognise the precondition on sight.

## The Staircase

Start at the **top-right** corner and read the comparison as an elimination.

At cell `(r, c)` with value `v = M[r][c]`:

| Case | What it proves | Move |
|------|----------------|------|
| `v == target` | found | stop |
| `v > target` | every cell **below** in column `c` is `>= v > target`, and rows above `r` are already eliminated. Column `c` is dead. | `c -= 1` |
| `v < target` | every cell **left** in row `r` is `<= v < target`, and columns right of `c` are already eliminated. Row `r` is dead. | `r += 1` |

```
target = 5

      c=3
  1   4   7  11    <- start here (11 > 5) -> drop column 3
  2   5   8  12                (7 > 5)    -> drop column 2
  3   6   9  16                (4 < 5)    -> drop row 0
 10  13  14  17                (5 == 5)   -> found at (1,1)
```

Every step retires an entire row or an entire column, so a matrix with `m`
rows and `n` columns takes at most `m + n - 1` probes. No backtracking, no
recursion, `O(1)` extra space.

## Why Only Two Corners Work

The top-**left** corner is the minimum of the whole matrix, the bottom-**right**
is the maximum. At either one, the two available moves point the *same*
comparison direction:

- At `(0, 0)`: everything to the right is `>=`, everything below is `>=`.
  `v < target` is consistent with the target being right, below, or
  diagonally down-right. You learn nothing and can eliminate nothing.

The two anti-diagonal corners — top-right and bottom-left — are the only cells
where one direction is monotonically increasing and the other monotonically
decreasing. That opposition is what turns a single comparison into a full
row-or-column elimination. Bottom-left works identically with the moves
mirrored (`v < target` -> `c += 1`, `v > target` -> `r -= 1`).

## Counting, and What It Unlocks

The same walk answers "how many entries are `<= x`?" in `O(m + n)`. Start at
the bottom-left instead:

- `M[r][c] <= x` -> every cell **above** it in column `c` is also `<= x`
  (columns ascend downward), so add `r + 1` and step right.
- otherwise step up.

That counting primitive plus Day 106's search-on-answer-space gives
`kth_smallest` on a row+column-sorted matrix: binary search the *value* range
`[M[0][0], M[m-1][n-1]]` for the smallest `v` with `count_le(v) >= k`. Total
`O((m + n) log(max - min))`. Day 106 owns the search-on-answer-space idea; we
are only supplying it with a counting oracle it could not otherwise have.

## When Staircase Is Not Optimal

`O(m + n)` is optimal for square-ish matrices: the boundary separating cells
`< target` from cells `> target` is a monotone staircase up to `m + n - 1`
cells long, and an adversary can hide the target anywhere on it.

For a **very wide** matrix (`m << n`) you can do better. Binary search row 0
for the target's insertion point, and every later row only needs to search to
the left of the previous row's result — the boundary is monotone, so those
searches telescope. That yields `O(m log(n / m))`, the known optimum
(Bird 2006). When `m` and `n` are comparable the two collapse to the same
order and the staircase wins on constants.

The implementation ships both so the difference is measurable rather than
asserted.

## Complexity

| Approach | Precondition | Time | Space |
|----------|--------------|------|-------|
| Brute force scan | none | O(m·n) | O(1) |
| Staircase search | row+column sorted | **O(m + n)** | O(1) |
| Binary search per row | row+column sorted | O(m log n), O(m log(n/m)) with telescoping | O(1) |
| `count_le` staircase | row+column sorted | O(m + n) | O(1) |
| `kth_smallest` | row+column sorted | O((m + n)·log(range)) | O(1) |
| Flatten + binary search | **globally** sorted (Day 020) | O(log(m·n)) | O(1) |

The last row is in the table only to mark the boundary: it needs a stronger
precondition than this day assumes, and silently returns wrong answers if you
apply it here.

## Failure Modes

| Failure | When | Fix |
|---------|------|-----|
| Wrong answer, no error | flatten + binary search used on a merely row+column-sorted matrix | Check the precondition. `[[1,4],[2,5]]` flattens to `1,4,2,5` — unsorted |
| Starts at the wrong corner | top-left or bottom-right | Only anti-diagonal corners eliminate; from `(0,0)` no comparison prunes anything |
| Index error on empty input | `[]` or `[[]]` | Guard both: zero rows *and* zero columns |
| Ragged rows | rows of differing length | Not a matrix; the column invariant is undefined. Validate, do not assume |
| Duplicates give the "wrong" cell | many equal values | The walk returns *a* correct cell, not the first in any particular order. If you need the topmost or leftmost occurrence, keep walking |
| `count_le` off by one | adding `r` instead of `r + 1` | Rows are 0-indexed; a hit at row `r` means `r + 1` cells at or above it |
| `kth_smallest` returns a non-element | binary searching on value and returning the midpoint | Return the smallest `v` with `count_le(v) >= k`; that `v` is always an actual matrix entry |
| Assumed O(log) | expecting binary-search speed | `Omega(m + n)` is a real lower bound here — the weaker ordering genuinely costs more |

## Checkpoint Questions

1. Write a 2x2 matrix that is row+column sorted but whose row-major flattening
   is not sorted. Why does that kill the Day 020 approach?
2. At the top-right cell, prove that `v > target` eliminates the entire
   column and not merely that one cell.
3. Why do the top-left and bottom-right corners eliminate nothing?
4. Why is the number of probes bounded by `m + n - 1` and not `m * n`?
5. Sketch the adversary argument for the `Omega(m + n)` lower bound. Where
   does it stop applying when `m << n`?
6. `count_le` starts from the bottom-left and adds `r + 1`. What breaks if
   you start from the top-right instead?
7. `kth_smallest` binary searches over values, not indices. Why is the value
   it converges on guaranteed to be an actual entry of the matrix?
