"""
Day 119: Subset-Sum, Partition & Bounded Knapsack

One table, three questions:
  reach[s]  -> "is s a subset sum?"          subset-sum
  reach[s]  -> "is total/2 a subset sum?"    equal partition
  dp[w]     -> "best value at weight <= w"   bounded knapsack

The genuinely new machinery here is BINARY SPLITTING: turning "up to m copies
of this item" into O(log m) one-off packages whose subset totals are exactly
0..m. Not m+1. Exactly m.

Standard library only.
"""

from itertools import product


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def _require_nonneg_ints(nums, what="values"):
    """
    The reach[] table is indexed by a running sum, so it only works when sums
    move in one direction. A negative would need an offset-shifted table; we
    refuse rather than return a confidently wrong answer.
    """
    for x in nums:
        if not isinstance(x, int) or isinstance(x, bool):
            raise TypeError(f"{what} must be plain ints, got {x!r}")
        if x < 0:
            raise ValueError(f"{what} must be non-negative, got {x}")


# ---------------------------------------------------------------------------
# 1. Subset-sum
# ---------------------------------------------------------------------------

def subset_sum_exists(nums, target):
    """
    True iff some subset of nums sums to exactly target.

    The inner loop runs DOWNWARD. That is the entire difference between
    "each item at most once" and "each item unlimited times": going down means
    reach[s - x] still describes the table BEFORE x was offered, so x cannot
    be consumed twice in one pass.
    """
    _require_nonneg_ints(nums)
    if target < 0:
        return False
    reach = [False] * (target + 1)
    reach[0] = True
    for x in nums:
        if x > target:
            continue
        for s in range(target, x - 1, -1):
            if reach[s - x]:
                reach[s] = True
    return reach[target]


def subset_sum_exists_bitset(nums, target):
    """
    Same DP, but the whole row lives in one arbitrary-precision int.

    bit s of `bits` set  <=>  sum s is reachable.
    Shifting left by x is "add x to every reachable sum" for all sums at once,
    so the CPU does ~64 table cells per instruction instead of one.
    """
    _require_nonneg_ints(nums)
    if target < 0:
        return False
    bits = 1  # only sum 0 reachable so far
    mask = (1 << (target + 1)) - 1  # drop sums past target so the int stays small
    for x in nums:
        bits = (bits | (bits << x)) & mask
    return (bits >> target) & 1 == 1


def subset_sum_witness(nums, target):
    """
    Return a list of INDICES whose values sum to target, or None.

    Indices, not values, so duplicated values stay distinguishable — a caller
    that gets [3, 3] back cannot tell whether one element was used twice.

    Keeps a full 2D table because reconstruction needs to know, for each
    prefix length, whether the sum was reachable without the current item.
    """
    _require_nonneg_ints(nums)
    if target < 0:
        return None
    n = len(nums)
    # reach[i][s] = using only nums[:i], is s reachable?
    reach = [[False] * (target + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        reach[i][0] = True
    for i in range(1, n + 1):
        x = nums[i - 1]
        row, prev = reach[i], reach[i - 1]
        for s in range(target + 1):
            row[s] = prev[s] or (s >= x and prev[s - x])
    if not reach[n][target]:
        return None

    chosen = []
    s = target
    for i in range(n, 0, -1):
        # If the prefix without nums[i-1] already reached s, item i-1 was optional.
        if reach[i - 1][s]:
            continue
        chosen.append(i - 1)
        s -= nums[i - 1]
    chosen.reverse()
    return chosen


def count_subsets_with_sum(nums, target):
    """
    Number of distinct index-subsets summing to target.

    A 0 in nums doubles every count (in or out, the sum is identical). That is
    correct and almost never what the caller wanted — see README failure modes.
    """
    _require_nonneg_ints(nums)
    if target < 0:
        return 0
    ways = [0] * (target + 1)
    ways[0] = 1
    for x in nums:
        for s in range(target, x - 1, -1):
            ways[s] += ways[s - x]
    return ways[target]


# ---------------------------------------------------------------------------
# 2. Partition
# ---------------------------------------------------------------------------

def can_partition_equal_sum(nums):
    """
    Can nums be split into two groups of equal sum?

    Parity kills half the inputs before any DP runs: an odd total can never be
    halved into two integer sums.
    """
    _require_nonneg_ints(nums)
    total = sum(nums)
    if total % 2:
        return False
    return subset_sum_exists(nums, total // 2)


def min_subset_sum_difference(nums):
    """
    Minimum |sum(A) - sum(B)| over all 2-way splits.

    If A sums to s then B sums to total - s, so the gap is |total - 2s|.
    Scanning only s <= total // 2 is enough: s and total - s give the same gap,
    so the half we skip is a mirror image.
    """
    _require_nonneg_ints(nums)
    total = sum(nums)
    half = total // 2
    reach = [False] * (half + 1)
    reach[0] = True
    for x in nums:
        if x > half:
            continue
        for s in range(half, x - 1, -1):
            if reach[s - x]:
                reach[s] = True
    best = 0
    for s in range(half, -1, -1):
        if reach[s]:
            best = s
            break
    return total - 2 * best


def partition_groups(nums):
    """
    Recover the actual two groups achieving min_subset_sum_difference.
    Returns (group_a_indices, group_b_indices).
    """
    _require_nonneg_ints(nums)
    total = sum(nums)
    half = total // 2
    for s in range(half, -1, -1):
        picked = subset_sum_witness(nums, s)
        if picked is not None:
            in_a = set(picked)
            rest = [i for i in range(len(nums)) if i not in in_a]
            return picked, rest
    return [], list(range(len(nums)))


# ---------------------------------------------------------------------------
# 3. Binary splitting — the heart of bounded knapsack
# ---------------------------------------------------------------------------

def binary_split_counts(m):
    """
    Decompose multiplicity m into packages 1, 2, 4, ... plus one remainder,
    such that subset sums of the packages are EXACTLY {0, 1, ..., m}.

    Why exactly, and not one more: the packages always sum to m itself, so m is
    a hard ceiling. And the powers 1..2^(j-1) already cover 0..2^j-1 densely, so
    adding a remainder r < 2^j slides that block up to r..r+2^j-1 — the two
    blocks touch, leaving no hole.

    The classic bug is `while k <= m: parts.append(k); k *= 2` WITHOUT
    subtracting k from m, then appending m. Those parts sum to more than m,
    and the knapsack quietly buys copies you do not own.
    """
    if m < 0:
        raise ValueError(f"multiplicity must be non-negative, got {m}")
    parts = []
    k = 1
    while k <= m:
        parts.append(k)
        m -= k        # subtract as we go: this is what keeps the total at m
        k *= 2
    if m > 0:         # skip a zero remainder; a zero-size package is noise
        parts.append(m)
    return parts


def reachable_multiplicities(parts):
    """Every total a subset of `parts` can form. Used to prove exactness."""
    reach = {0}
    for p in parts:
        reach |= {r + p for r in reach}
    return reach


# ---------------------------------------------------------------------------
# 4. Bounded knapsack
# ---------------------------------------------------------------------------

def _best_value_over_pairs(pairs, capacity):
    """
    0/1 pass over (value, weight) pairs. Machinery, not the lesson: each pair
    may be taken at most once, so the weight loop runs downward.
    """
    dp = [0] * (capacity + 1)
    for value, weight in pairs:
        if weight > capacity or weight < 0:
            continue
        for w in range(capacity, weight - 1, -1):
            cand = dp[w - weight] + value
            if cand > dp[w]:
                dp[w] = cand
    return dp[capacity]


def _validate_items(items):
    for value, weight, count in items:
        if weight < 0:
            raise ValueError(f"weight must be non-negative, got {weight}")
        if count < 0:
            raise ValueError(f"count must be non-negative, got {count}")


def bounded_knapsack_expanded(items, capacity):
    """
    Baseline. items = [(value, weight, count), ...].
    Expand each item into `count` identical 0/1 items.

    Obviously correct, and obviously O(capacity * sum(counts)). It exists so
    the fast version has something honest to be checked against.
    """
    _validate_items(items)
    if capacity < 0:
        return 0
    pairs = []
    for value, weight, count in items:
        pairs.extend([(value, weight)] * count)
    return _best_value_over_pairs(pairs, capacity)


def bounded_knapsack_binary(items, capacity):
    """
    Same answer, O(capacity * sum(log count)).

    Each item becomes a few PACKAGES: taking a package of size c means taking c
    copies at once, for value c*value and weight c*weight. Because the package
    sizes reach exactly 0..count, no legal multiplicity is missed and no
    illegal one is invented.
    """
    _validate_items(items)
    if capacity < 0:
        return 0
    pairs = []
    for value, weight, count in items:
        for c in binary_split_counts(count):
            pairs.append((value * c, weight * c))
    return _best_value_over_pairs(pairs, capacity)


def bounded_knapsack_bruteforce(items, capacity):
    """
    Independent ground truth for tiny inputs: try every multiplicity vector.
    Exponential — for tests only.
    """
    _validate_items(items)
    if capacity < 0:
        return 0
    best = 0
    ranges = [range(count + 1) for _, _, count in items]
    for combo in product(*ranges):
        weight = sum(c * items[i][1] for i, c in enumerate(combo))
        if weight <= capacity:
            value = sum(c * items[i][0] for i, c in enumerate(combo))
            if value > best:
                best = value
    return best


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_subset_sum():
    print("=" * 62)
    print("DEMO 1: Subset-Sum")
    print("=" * 62)
    nums = [3, 34, 4, 12, 5, 2]
    for target in (9, 30, 11):
        ok = subset_sum_exists(nums, target)
        bits_ok = subset_sum_exists_bitset(nums, target)
        witness = subset_sum_witness(nums, target)
        picked = [nums[i] for i in witness] if witness else None
        print(f"  target {target:3d}: dp={ok} bitset={bits_ok} witness={picked}")
        assert ok == bits_ok, "bitset and boolean DP must agree"

    print(f"\n  count of subsets of {nums} summing to 9: "
          f"{count_subsets_with_sum(nums, 9)}")
    print("  note: a 0 in the input would double every count.")


def demo_partition():
    print("\n" + "=" * 62)
    print("DEMO 2: Partition")
    print("=" * 62)
    cases = [[1, 5, 11, 5], [1, 2, 3, 5], [3, 1, 4, 2, 2, 1]]
    for nums in cases:
        equal = can_partition_equal_sum(nums)
        gap = min_subset_sum_difference(nums)
        a, b = partition_groups(nums)
        ga = [nums[i] for i in a]
        gb = [nums[i] for i in b]
        print(f"  {nums}: equal-split={equal} min-gap={gap}")
        print(f"      groups {ga} (sum {sum(ga)}) vs {gb} (sum {sum(gb)})")
        assert abs(sum(ga) - sum(gb)) == gap


def demo_binary_split():
    print("\n" + "=" * 62)
    print("DEMO 3: Binary Splitting — exactly 0..m")
    print("=" * 62)
    for m in range(0, 14):
        parts = binary_split_counts(m)
        reach = reachable_multiplicities(parts)
        exact = reach == set(range(m + 1))
        print(f"  m={m:2d} parts={str(parts):16s} sum={sum(parts):2d} "
              f"reaches 0..{max(reach)} exact={exact}")
        assert exact, f"binary split for {m} is not exact"
        assert sum(parts) == m


def demo_bounded_knapsack():
    print("\n" + "=" * 62)
    print("DEMO 4: Bounded Knapsack")
    print("=" * 62)
    # (value, weight, count)
    items = [(10, 1, 3), (7, 2, 2), (25, 5, 1)]
    for capacity in (0, 3, 6, 10):
        a = bounded_knapsack_expanded(items, capacity)
        b = bounded_knapsack_binary(items, capacity)
        c = bounded_knapsack_bruteforce(items, capacity)
        print(f"  capacity {capacity:2d}: expanded={a} binary={b} brute={c}")
        assert a == b == c

    print("\n  The 'one copy too many' trap:")
    trap = [(10, 1, 3)]
    print(f"    items={trap}, capacity=10")
    print(f"    correct optimum   = {bounded_knapsack_bruteforce(trap, 10)}"
          f"  (3 copies, weight 3)")
    print(f"    binary splitting  = {bounded_knapsack_binary(trap, 10)}")
    print("    an off-by-one remainder would report 40 here (4 copies).")


if __name__ == "__main__":
    demo_subset_sum()
    demo_partition()
    demo_binary_split()
    demo_bounded_knapsack()
    print("\nAll day-119 demos complete.")
