# Day 116: 2D Dynamic Programming

## When DP Becomes 2D

If the state needs TWO indices (or one index over a 2D structure), we get
a 2D table dp[i][j]. The state space is O(n·m); work per state is usually
O(1) for grid problems. Total: O(n·m) time, O(n·m) space.

Many 2D DPs collapse to O(min(n,m)) space because each row depends only
on the previous row.

## Three Canonical Problems

### 1. Unique Paths (Grid)

Robot starts at top-left of an m×n grid. Each step moves right or down.
How many distinct paths to the bottom-right?

```
dp[i][j] = dp[i-1][j] + dp[i][j-1]
dp[0][j] = 1 for all j        (only one way along the top row)
dp[i][0] = 1 for all i        (only one way along the left column)
```

Closed form: C(m+n-2, m-1). DP reaches the same answer combinatorially.

### 2. Unique Paths with Obstacles

Same grid, but some cells are blocked (1 = blocked, 0 = open).

```
dp[i][j] = 0                                if grid[i][j] == 1
         = dp[i-1][j] + dp[i][j-1]          otherwise
dp[0][0] = 0 if grid[0][0] == 1 else 1
```

Edge case: if start or end is blocked, answer is 0.

### 3. Minimum Path Sum

Each cell has a non-negative cost. Find min total cost from top-left to
bottom-right moving only right or down.

```
dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])
dp[0][0] = grid[0][0]
dp[0][j] = dp[0][j-1] + grid[0][j]
dp[i][0] = dp[i-1][0] + grid[i][0]
```

**Wrong-but-tempting greedy**: "at each cell, take the smaller of right/down."
Fails because a small step now can force large steps later. Example:
```
1  3  1
1  5  1
4  2  1
```
From (0,0) greedy goes right (3 vs 1)... actually let's pick: at (0,0)
options are right=3, down=1, so greedy goes down to (1,0). Then right=5,
down=4, greedy goes down to (2,0). Then right=2, only option, then 1.
Total: 1+1+4+2+1 = 9. But optimal: 1+3+1+1+1 = 7 (right, right, down, down).
Greedy is short-sighted; DP looks at all future choices.

## State Space Visualisation

Think of the DP table as the grid itself. Each cell stores the answer to
"how do I get to here optimally?" Recurrence is **local**: only nearest
neighbors matter. This is why 2D DP has the same shape as shortest path
on a DAG, and Bellman-Ford is essentially DP.

## Math Notation

Let f(i,j) = min cost from (0,0) to (i,j) moving right or down.
```
f(0,0) = c(0,0)
f(i,j) = c(i,j) + min(f(i-1,j), f(i,j-1))
```
Boundary: cells with i<0 or j<0 are unreachable -> +∞.

## Space Compression Pattern

Row-by-row: dp[j] = (old dp[j]) + (new dp[j-1]) — same row's left + previous
row's same column. O(n) space instead of O(m·n).

```
dp = [INF] * n
dp[0] = grid[0][0]
for j in 1..n-1: dp[j] = dp[j-1] + grid[0][j]
for i in 1..m-1:
    dp[0] += grid[i][0]
    for j in 1..n-1:
        dp[j] = grid[i][j] + min(dp[j], dp[j-1])
return dp[n-1]
```

## Counting vs Optimizing — Same Shape

Note that unique paths (sum) and min path sum (min) use the SAME recurrence
shape, only the operator changes:
- Count: dp[i][j] = dp[i-1][j] + dp[i][j-1]
- Min:   dp[i][j] = c + min(dp[i-1][j], dp[i][j-1])
- Max:   dp[i][j] = c + max(dp[i-1][j], dp[i][j-1])

This is the **semiring abstraction** behind DP. Same DAG, swap the operator.

## Failure Modes

- **Off-by-one in obstacle path**: forgetting to zero out dp[0][j] after
  the first obstacle in row 0.
- **Mutating input grid**: cleanest to keep dp separate; many "in-place"
  variants are read-then-write order traps.
- **Wrong base case in min path**: dp[0][0] = c(0,0), not 0.
- **Greedy intuition**: short-circuiting to "always take smaller neighbor"
  ignores downstream effects.
- **8-directional movement**: doesn't have the DAG property; needs Dijkstra.

## Real-World Echoes

- **Grid pathfinding** in games / robotics (variant of Dijkstra/A*)
- **Bioinformatics** sequence alignment (Smith-Waterman, Needleman-Wunsch)
- **Image processing** seam carving
- **Finance** lattice option pricing — same shape, costs on edges
- **Manufacturing** assembly-line scheduling (CLRS, "Assembly-Line")

## Checkpoint Questions

1. Why does unique paths have a closed-form solution but min path sum
   does not?
2. State the space-compressed recurrence for unique paths and walk through
   a 3×3 example by hand.
3. When does the greedy "take smaller neighbor" coincide with the DP
   optimum?
4. How would you modify min path sum to also return the path?
5. Why does diagonal movement break the DAG structure for these problems?
6. Compute the number of unique paths in an 18×18 grid. Does the closed
   form match your DP?
