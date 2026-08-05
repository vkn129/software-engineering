"""
Day 114: 1D Dynamic Programming.

Three canonical problems with O(n) time and O(1) space:
  1. Climbing stairs (count paths)
  2. House robber (max non-adjacent sum)
  3. Maximum subarray (Kadane's algorithm)
"""


# ---------------------------------------------------------------------------
# 1. Climbing Stairs
# ---------------------------------------------------------------------------
# Recurrence: ways(n) = ways(n-1) + ways(n-2),  ways(0) = ways(1) = 1.

def climb_stairs(n):
    """Number of distinct ways to climb n stairs taking 1 or 2 steps."""
    if n <= 1:
        return 1
    prev2, prev1 = 1, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1


def climb_stairs_with_table(n):
    """Same answer, but returns the full dp table for inspection."""
    dp = [0] * (n + 1)
    dp[0] = 1
    if n >= 1:
        dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp


# ---------------------------------------------------------------------------
# 2. House Robber (linear)
# ---------------------------------------------------------------------------
# dp[i] = max(dp[i-1], dp[i-2] + v[i]).
# State = "best loot using houses 0..i". Base cases small.

def house_robber(values):
    """Max non-adjacent sum from a list of house values."""
    if not values:
        return 0
    if len(values) == 1:
        return values[0]

    prev2 = values[0]
    prev1 = max(values[0], values[1])
    for i in range(2, len(values)):
        prev2, prev1 = prev1, max(prev1, prev2 + values[i])
    return prev1


def house_robber_with_trace(values):
    """Return (max_loot, list_of_robbed_indices)."""
    n = len(values)
    if n == 0:
        return 0, []
    if n == 1:
        return values[0], [0]

    dp = [0] * n
    dp[0] = values[0]
    dp[1] = max(values[0], values[1])
    for i in range(2, n):
        dp[i] = max(dp[i - 1], dp[i - 2] + values[i])

    # Backtrace from end
    picked = []
    i = n - 1
    while i >= 0:
        if i == 0:
            picked.append(0)
            break
        if i == 1:
            picked.append(0 if values[0] >= values[1] else 1)
            break
        # We robbed i iff dp[i] != dp[i-1]
        if dp[i] != dp[i - 1]:
            picked.append(i)
            i -= 2
        else:
            i -= 1
    return dp[-1], sorted(picked)


def house_robber_greedy_wrong(values):
    """
    Tempting wrong heuristic: repeatedly pick the largest remaining value
    and remove its neighbors. Used here to demonstrate failure.
    """
    n = len(values)
    alive = [True] * n
    total = 0
    while any(alive):
        best_i = -1
        best_v = float("-inf")
        for i in range(n):
            if alive[i] and values[i] > best_v:
                best_v = values[i]
                best_i = i
        if best_i == -1 or best_v <= 0:
            break
        total += best_v
        alive[best_i] = False
        if best_i - 1 >= 0:
            alive[best_i - 1] = False
        if best_i + 1 < n:
            alive[best_i + 1] = False
    return total


# ---------------------------------------------------------------------------
# 3. Maximum Subarray (Kadane's Algorithm)
# ---------------------------------------------------------------------------
# M(i) = max(a[i], M(i-1) + a[i]).
# Answer = max over all i of M(i).
# Works on negative-only arrays too — answer is the single largest element.

def max_subarray(a):
    """Largest sum of any contiguous subarray. O(n) time, O(1) space."""
    if not a:
        return 0
    best_ending_here = a[0]
    best_overall = a[0]
    for x in a[1:]:
        best_ending_here = max(x, best_ending_here + x)
        best_overall = max(best_overall, best_ending_here)
    return best_overall


def max_subarray_with_bounds(a):
    """Return (max_sum, left_index, right_index_inclusive)."""
    if not a:
        return 0, -1, -1
    best_ending_here = a[0]
    best_overall = a[0]
    start = 0
    best_l = best_r = 0
    for i in range(1, len(a)):
        if a[i] > best_ending_here + a[i]:
            best_ending_here = a[i]
            start = i
        else:
            best_ending_here += a[i]
        if best_ending_here > best_overall:
            best_overall = best_ending_here
            best_l, best_r = start, i
    return best_overall, best_l, best_r


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_stairs():
    print("=" * 60)
    print("DEMO 1: Climbing Stairs")
    print("=" * 60)
    print("\nn  | ways  (= Fibonacci shifted)")
    print("-" * 40)
    for n in range(0, 11):
        print(f"{n:3} | {climb_stairs(n)}")
    print("\nFull table for n=8:", climb_stairs_with_table(8))


def demo_robber():
    print("\n" + "=" * 60)
    print("DEMO 2: House Robber")
    print("=" * 60)

    cases = [
        [2, 7, 9, 3, 1],
        [2, 1, 1, 2],
        [10, 1, 1, 10, 1, 1, 10],
        [5, 5, 5, 5, 5],
        [0, 0, 0, 0],
    ]
    for v in cases:
        opt, picks = house_robber_with_trace(v)
        greedy = house_robber_greedy_wrong(v)
        flag = " <-- GREEDY MATCHES" if greedy == opt else f" (greedy={greedy} WRONG)"
        print(f"  {v} -> optimal={opt} robbed={picks}{flag}")


def demo_kadane():
    print("\n" + "=" * 60)
    print("DEMO 3: Maximum Subarray (Kadane's)")
    print("=" * 60)

    cases = [
        [-2, 1, -3, 4, -1, 2, 1, -5, 4],
        [1, 2, 3, 4, 5],
        [-1, -2, -3, -4],   # all negative
        [5],
        [3, -2, 5, -1],
    ]
    for a in cases:
        s, l, r = max_subarray_with_bounds(a)
        print(f"  {a}")
        print(f"    max sum = {s}, window = a[{l}..{r}] = {a[l:r+1]}")


if __name__ == "__main__":
    demo_stairs()
    demo_robber()
    demo_kadane()
