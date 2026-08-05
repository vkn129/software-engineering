# Day 115: 1D DP with Decisions

## What "DP with Decisions" Means

In Day 114 the recurrence had a fixed shape (Fibonacci-like). Now each state
must **choose among several options**, and the recurrence is a min/max/sum
over those options:

```
dp[i] = min/max/sum_{decision d}  cost(d) + dp[next_state(i, d)]
```

The state space is still O(n), but **work per state can be O(k)** where k
is the number of available decisions. Total: O(n·k).

## Three Canonical Problems

### 1. Coin Change — Minimum Coins

Given coin denominations and a target amount, find the minimum number of
coins that sum to amount, or -1 if impossible.

```
dp[a] = 1 + min_{c in coins, c <= a}  dp[a - c]
dp[0] = 0
```

State: dp[a] = "min coins to make amount a." Decision at state a: which coin
do we use last? Try every coin; pick the one minimizing 1 + dp[a-c].

**Wrong-but-tempting greedy**: "always take the largest coin <= remaining."
Fails on coins=[1, 3, 4], amount=6:
- Greedy: 4 + 1 + 1 = 3 coins.
- Optimal: 3 + 3 = 2 coins.
Greedy works for **canonical coin systems** (US coins) — those are matroids.
General denominations are not.

### 2. Coin Change — Count Ways

Same coins, same amount; how many distinct **combinations** (unordered) sum
to amount?

```
dp[a] = number of combinations summing to a using coins
Initialize: dp[0] = 1, dp[a>0] = 0
for each coin c:                  <-- outer loop: coin
    for a in c..amount:            <-- inner loop: amount
        dp[a] += dp[a - c]
```

**Critical**: looping coins outside and amounts inside counts **combinations**.
Swapping the loops counts **permutations** (different orderings).

This is the **unbounded knapsack** template.

### 3. Decode Ways

Given a digit string (e.g., "226"), count decodings where 'A'=1, ..., 'Z'=26.
"226" decodes as "BZ", "VF", "BBF" → 3 ways.

```
dp[i] = ways to decode s[:i].  dp[0] = 1.
dp[i] += dp[i-1]              if s[i-1] in '1'..'9'        (single digit)
dp[i] += dp[i-2]              if s[i-2:i] in '10'..'26'    (pair)
```

State: prefix length. Decision: does the last 1 digit form a letter? Does
the last 2 digits form a letter?

**Wrong-but-tempting greedy**: "always pair digits when possible." Fails
on "12": both "AB" (1+2) and "L" (12) are valid → 2 ways, not 1.

## Math Notation Discipline

For each problem state:
- min coins: dp[a] = 1 + min{dp[a-c] : c in coins, dp[a-c] < inf}
- count ways: dp[a] = sum over coins of dp[a-c]   (with loop order trick)
- decode: dp[i] = dp[i-1]·valid_single + dp[i-2]·valid_pair

## Failure Modes

- **Coin change min**: forgetting to special-case impossibility. Use
  `inf` (= amount+1) as sentinel and check at end.
- **Count ways**: swapping the loops accidentally counts permutations.
  6 = 1+2+3 = 1+3+2 = 2+1+3... — usually NOT what you want.
- **Decode ways**: leading '0'. "06" is NOT 6, it's invalid. Each substring
  starting with '0' fails the single-digit check; '0' alone has 0 ways.
- **Integer overflow**: not a Python issue, but in C++ count ways grows
  exponentially in worst case.
- **Greedy intuition trap**: students try greedy first, only see DP after
  it fails on a curated input.

## Greedy vs DP — When Greedy Works for Coins

Greedy is optimal for the coin system {c_0, c_1, ...} iff at every amount
a, taking the largest coin <= a is part of some optimal solution. This is
the **matroid exchange property**. For US coins {1, 5, 10, 25} it holds;
for {1, 3, 4} it doesn't. No simple test other than DP verification on
amounts up to ~4·c_max.

## Real-World Echoes

- **Min coins**: change-making in cash registers; partial fill in trade
  execution.
- **Count ways**: number of partitions; counting paths in a DAG.
- **Decode ways**: speech recognition n-best decoding; tokenization
  ambiguity.

## Checkpoint Questions

1. Why does looping coins outside and amounts inside count combinations?
2. Construct a 3-coin system where greedy beats DP. (Trick — impossible.)
3. Why is dp[0] = 1 in count-ways but dp[0] = 0 in min-coins?
4. How does decode-ways handle the input "0"?
5. What is the space complexity of count-ways with the standard DP table?
6. Why is min-coins NP-hard if denominations are arbitrary? (Hint: it isn't —
   pseudo-polynomial. Explain why.)
