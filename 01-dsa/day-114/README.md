# Day 114: 1D Dynamic Programming

## What 1D DP Means

The state is a single index `i` (often a prefix or a position). The recurrence
relates `dp[i]` to a constant number of earlier cells:

```
dp[i] = f(dp[i-1], dp[i-2], ..., dp[i-k])  for some small k
```

State space: O(n). Work per state: O(k) = O(1). Total: O(n).
Space can usually drop to O(1) by keeping only the last `k` values.

## Three Canonical Problems

### 1. Climbing Stairs

Count distinct ways to reach step n with jumps of 1 or 2.

```
dp[i] = dp[i-1] + dp[i-2]   (last jump was 1 or 2)
dp[0] = dp[1] = 1
```

Same shape as Fibonacci. Why? Because the **last decision** has exactly 2
options and each splits into a disjoint subproblem.

### 2. House Robber (Linear)

Houses in a row with values v[i]. You cannot rob two adjacent houses.
Maximize total loot.

```
dp[i] = max(dp[i-1],            (skip house i)
            dp[i-2] + v[i])     (rob house i)
dp[0] = v[0]
dp[1] = max(v[0], v[1])
```

**The state captures everything we need**: dp[i] is "best loot using houses
0..i". Whether we robbed i-1 is implied by which branch we took.

**Wrong-but-tempting greedy**: "always rob the largest remaining house and
skip its neighbors." Fails on `[2, 1, 1, 2]`: greedy takes the leftmost 2,
forced to skip the 1s and a 2 → total 4. But `[2, _, _, 2]` is 4, while
`[2, 1, 1, 2]` could pick indices 0 and 3 for the same 4 — here they tie.
Try `[2, 7, 9, 3, 1]`: greedy picks 9, blocks 7 and 3, then 1 → 10.
Optimal: 7 + 3 + 1 = 11 (or 2 + 9 + 1 = 12). DP gets 12.

### 3. Maximum Subarray (Kadane's Algorithm)

Largest sum of any contiguous subarray.

```
best_ending_here[i] = max(a[i], best_ending_here[i-1] + a[i])
answer = max(best_ending_here[0..n-1])
```

The brilliant insight: the **state is "best subarray ending exactly at i"**,
not "best subarray in 0..i". This makes the recurrence O(1).

**Wrong-but-tempting greedy**: "include any positive element." Fails on
`[5, -10, 4]`: greedy takes 5+4=9 but the elements aren't contiguous.
Kadane resets when running sum drops below zero.

## Math Notation (Kadane)

Define M(i) = max contiguous sum of subarray ending at index i.
```
M(i) = max(a[i], M(i-1) + a[i])
Answer = max_{0 <= i < n} M(i)
```

Why is this correct? Any contiguous subarray ends somewhere; trying all
endings covers all subarrays. At each ending we either extend or restart.

## State Transitions as a Decision Tree

Each DP cell encodes "what's the last decision and what does it cost?"
For house robber the decision is binary (rob/skip); for stairs it's
binary (last jump was 1 or 2); for Kadane it's binary (extend/restart).

## Space Compression Pattern

```
prev2 = base case 0
prev1 = base case 1
for i in 2..n:
    curr = recurrence(prev1, prev2)
    prev2, prev1 = prev1, curr
return prev1
```

Works whenever the recurrence depends on a sliding window of fixed size.

## Failure Modes

- **Off-by-one in base cases**: house robber with 1 element vs 2 elements
- **Negative-only arrays in Kadane**: must allow the answer to be negative,
  do NOT clamp to 0
- **Mutating input**: don't write back into the array you're scanning
- **Reading dp[i] before computing it**: only happens with wrong loop order
- **Greedy mindset**: assuming "biggest first" works; it almost never does
  in non-matroid optimization

## Real-World Echoes

- **Climbing stairs** -> counting paths in any small-degree DAG
- **House robber** -> scheduling non-conflicting jobs on a timeline
- **Kadane** -> sliding-window anomaly detection in stock returns,
  signal processing, image gradients

## Checkpoint Questions

1. Why does the house robber recurrence have exactly two terms?
2. State the loop invariant of Kadane's algorithm.
3. How does Kadane handle an all-negative array?
4. What's the smallest house-robber input where the greedy heuristic fails?
5. Derive an O(1)-space version of the stairs problem.
6. Suppose you can rob 3 houses if they're separated by at least 2 gaps —
   write the new recurrence. How does state space change?
