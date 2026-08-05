"""
Day 115: 1D DP with Decisions.

Three problems where each state chooses among k options:
  1. Coin Change — min coins to reach an amount
  2. Coin Change — count of combinations summing to amount
  3. Decode Ways — count digit-string decodings A=1..Z=26
"""

import math


# ---------------------------------------------------------------------------
# 1. Min coins to make amount
# ---------------------------------------------------------------------------
# dp[a] = min coins. dp[0] = 0. dp[a] = 1 + min(dp[a-c]) over coins.

def min_coins(coins, amount):
    """Min number of coins summing to amount, or -1 if impossible."""
    if amount < 0:
        return -1
    INF = amount + 1
    dp = [INF] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1


def min_coins_with_trace(coins, amount):
    """Return (min_count, coins_used)."""
    INF = amount + 1
    dp = [INF] * (amount + 1)
    choice = [-1] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
                choice[a] = c
    if dp[amount] == INF:
        return -1, []
    used = []
    a = amount
    while a > 0:
        used.append(choice[a])
        a -= choice[a]
    return dp[amount], sorted(used, reverse=True)


def min_coins_greedy_wrong(coins, amount):
    """Greedy: always take the largest coin <= remaining. May fail."""
    coins_sorted = sorted(coins, reverse=True)
    count = 0
    for c in coins_sorted:
        while amount >= c:
            amount -= c
            count += 1
    return count if amount == 0 else -1


# ---------------------------------------------------------------------------
# 2. Count combinations summing to amount
# ---------------------------------------------------------------------------
# Outer loop coins, inner loop amounts -> combinations (unordered).
# Outer loop amounts, inner loop coins -> permutations (ordered).

def count_combinations(coins, amount):
    """Number of unordered combinations of coins summing to amount."""
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]


def count_permutations(coins, amount):
    """Number of ordered sequences (different orders count separately)."""
    dp = [0] * (amount + 1)
    dp[0] = 1
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] += dp[a - c]
    return dp[amount]


# ---------------------------------------------------------------------------
# 3. Decode Ways
# ---------------------------------------------------------------------------
# A=1..Z=26.  dp[i] = ways to decode s[:i].

def decode_ways(s):
    """Number of valid decodings of the digit string s."""
    n = len(s)
    if n == 0:
        return 0
    if s[0] == "0":
        return 0
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        # single digit s[i-1]
        if s[i - 1] != "0":
            dp[i] += dp[i - 1]
        # pair s[i-2..i-1]
        pair = int(s[i - 2:i])
        if 10 <= pair <= 26:
            dp[i] += dp[i - 2]
    return dp[n]


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_min_coins():
    print("=" * 60)
    print("DEMO 1: Min Coins")
    print("=" * 60)

    cases = [
        ([1, 3, 4], 6),    # greedy fails: 4+1+1=3 vs 3+3=2
        ([1, 2, 5], 11),
        ([2], 3),          # impossible
        ([1, 5, 10, 25], 30),  # US coins, greedy works
    ]
    for coins, amt in cases:
        opt, used = min_coins_with_trace(coins, amt)
        greedy = min_coins_greedy_wrong(coins, amt)
        flag = "ok" if greedy == opt else f"WRONG (got {greedy})"
        print(f"  coins={coins}, amt={amt:3} -> dp={opt} {used}  greedy={flag}")


def demo_count_ways():
    print("\n" + "=" * 60)
    print("DEMO 2: Count Combinations vs Permutations")
    print("=" * 60)

    coins = [1, 2, 3]
    for amt in [3, 4, 5]:
        c = count_combinations(coins, amt)
        p = count_permutations(coins, amt)
        print(f"  amt={amt}: combinations={c}, permutations={p}")
    print("\nKey insight: loop order determines whether 1+2 and 2+1 are "
          "counted as one or two solutions.")


def demo_decode():
    print("\n" + "=" * 60)
    print("DEMO 3: Decode Ways")
    print("=" * 60)

    cases = ["12", "226", "0", "06", "10", "11106", "27", "100"]
    for s in cases:
        print(f"  '{s}' -> {decode_ways(s)} ways")


if __name__ == "__main__":
    demo_min_coins()
    demo_count_ways()
    demo_decode()
