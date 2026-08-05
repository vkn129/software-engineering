"""
Day 130: Fractional Knapsack — Greedy is Optimal.
Plus: 0/1 knapsack counterexample where greedy fails.

Fractional: sort by density (value/weight) descending. O(n log n).
0/1: density-greedy is NOT optimal. DP is needed for optimal answer.
"""

from math import inf


# ---------------------------------------------------------------------------
# Fractional Knapsack — Greedy
# ---------------------------------------------------------------------------

def fractional_knapsack(items, capacity):
    """
    items: list of (value, weight) with weight > 0.
    capacity: total weight allowed.
    Returns: (max_total_value, list of (idx, fraction_taken) in selection order).

    Time: O(n log n)
    """
    if capacity <= 0 or not items:
        return 0.0, []

    indexed = [(v, w, i) for i, (v, w) in enumerate(items)]
    indexed.sort(key=lambda x: x[0] / x[1], reverse=True)

    total_value = 0.0
    selection = []
    remaining = capacity

    for v, w, i in indexed:
        if remaining <= 0:
            break
        if w <= remaining:
            total_value += v
            remaining -= w
            selection.append((i, 1.0))
        else:
            frac = remaining / w
            total_value += v * frac
            remaining = 0
            selection.append((i, frac))
            break

    return total_value, selection


# ---------------------------------------------------------------------------
# Density-greedy applied to 0/1 (WRONG — for demonstration)
# ---------------------------------------------------------------------------

def greedy_01_by_density(items, capacity):
    """
    Take items whole, by density descending, while they fit.
    NOT optimal for 0/1. Returns total value taken.
    """
    indexed = sorted(items, key=lambda x: x[0] / x[1], reverse=True)
    total = 0
    rem = capacity
    for v, w in indexed:
        if w <= rem:
            total += v
            rem -= w
    return total


# ---------------------------------------------------------------------------
# 0/1 Knapsack — Optimal via DP (for comparison)
# ---------------------------------------------------------------------------

def knapsack_01_dp(items, capacity):
    """
    DP: dp[i][c] = max value using first i items, capacity c.
    Time: O(n * W). Space: O(W) with rolling array.
    """
    n = len(items)
    dp = [0] * (capacity + 1)
    for v, w in items:
        # iterate capacity descending to avoid using item twice
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]


# ---------------------------------------------------------------------------
# Modified greedy: 2-approximation for 0/1 knapsack
# ---------------------------------------------------------------------------

def knapsack_01_greedy_2approx(items, capacity):
    """
    max(density-greedy, single largest-value item that fits)
    Provably within factor 2 of optimal.
    """
    g = greedy_01_by_density(items, capacity)
    best_single = max((v for v, w in items if w <= capacity), default=0)
    return max(g, best_single)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("=" * 65)
    print("Day 130 — Fractional Knapsack (greedy works) vs 0/1 (greedy fails)")
    print("=" * 65)

    # 1. Fractional example
    print("\n--- Fractional knapsack ---")
    items = [(60, 10), (100, 20), (120, 30)]  # (value, weight)
    capacity = 50
    val, sel = fractional_knapsack(items, capacity)
    print(f"  Items (v, w): {items}")
    print(f"  Capacity: {capacity}")
    print(f"  Max value: {val}")
    print(f"  Selection: {sel}  (item idx, fraction)")
    print("  Take all of #0, all of #1, then 2/3 of #2.")

    # 2. Same instance under 0/1
    print("\n--- Same items as 0/1 (whole-only) ---")
    g = greedy_01_by_density(items, capacity)
    opt = knapsack_01_dp(items, capacity)
    print(f"  Density-greedy: {g}  (takes #0 then #1, can't fit #2)")
    print(f"  Optimal (DP):   {opt}  (skip #0, take #1 and #2)")
    print(f"  Greedy is {g/opt*100:.0f}% of optimal.")

    # 3. Worst-case ratio for greedy 0/1
    print("\n--- 0/1 greedy can be arbitrarily bad ---")
    W = 1000
    items_bad = [(1, 1), (W - 1, W)]
    g = greedy_01_by_density(items_bad, W)
    opt = knapsack_01_dp(items_bad, W)
    print(f"  Items: {items_bad}, W={W}")
    print(f"  Greedy: {g}   Optimal: {opt}   Ratio: {g/opt:.4f}")

    # 4. 2-approximation rescue
    print("\n--- 2-approximation: max(greedy, best single) ---")
    g2 = knapsack_01_greedy_2approx(items_bad, W)
    print(f"  max(greedy, single best fit) = {g2}  (vs optimal {opt})")
    print(f"  Within factor 2: {g2 >= opt / 2}")

    # 5. When 0/1 == fractional (lucky case)
    print("\n--- When 0/1 and fractional agree ---")
    items_lucky = [(10, 5), (20, 10), (30, 15)]  # all densities equal = 2
    cap = 25
    f_val, _ = fractional_knapsack(items_lucky, cap)
    g_val = greedy_01_by_density(items_lucky, cap)
    o_val = knapsack_01_dp(items_lucky, cap)
    print(f"  Items {items_lucky}, cap {cap}")
    print(f"  Fractional: {f_val}   0/1 greedy: {g_val}   0/1 optimal: {o_val}")
    print("  Equal because all densities tied and total weight matches cap.")

    print("\n" + "=" * 65)
    print("Fractional allows tiny exchanges → greedy is optimal.")
    print("0/1 forbids them → greedy is only a 2-approx; DP gives true optimum.")


if __name__ == "__main__":
    demo()
