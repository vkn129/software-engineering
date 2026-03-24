"""
Day 18: Sliding Window — Fixed and Variable Width Patterns

This script demonstrates the sliding window technique from first principles.
We build each algorithm step by step, showing the window state at every
iteration so you can see exactly what is happening and why.

The core idea: instead of recomputing from scratch for every subarray,
maintain a running state and update it incrementally as the window moves.

Run: python sliding_window.py
"""


# ===========================================================================
# SECTION 1: Fixed-Width Sliding Window
# ===========================================================================

def max_sum_brute_force(arr, k):
    """O(nk) brute force — compute each window sum from scratch.
    This is the baseline we want to beat."""
    n = len(arr)
    if n < k:
        return None

    max_sum = float('-inf')
    for i in range(n - k + 1):
        window_sum = 0
        for j in range(i, i + k):
            window_sum += arr[j]
        max_sum = max(max_sum, window_sum)
    return max_sum


def max_sum_sliding_window(arr, k):
    """O(n) sliding window — each element is added once and subtracted once.

    The recurrence: S(i+1) = S(i) - arr[i] + arr[i+k]
    This is what makes it O(n): each transition costs O(1)."""
    n = len(arr)
    if n < k:
        return None

    # Compute the first window
    window_sum = sum(arr[:k])
    max_sum = window_sum

    # Slide: subtract the element leaving, add the element entering
    for i in range(k, n):
        leaving = arr[i - k]
        entering = arr[i]
        window_sum = window_sum - leaving + entering
        max_sum = max(max_sum, window_sum)

    return max_sum


def demo_fixed_window():
    """Visual demonstration of fixed-width sliding window."""
    arr = [2, 1, 5, 1, 3, 2, 8, 1]
    k = 3

    print("=" * 70)
    print("FIXED-WIDTH SLIDING WINDOW: Max sum of k consecutive elements")
    print("=" * 70)
    print(f"\nArray: {arr}")
    print(f"Window size k = {k}")
    print()

    # Show each window state
    window_sum = sum(arr[:k])
    max_sum = window_sum
    best_start = 0

    print(f"Step 0: window [{0}..{k-1}] = {arr[:k]}, sum = {window_sum}")

    for i in range(k, len(arr)):
        leaving = arr[i - k]
        entering = arr[i]
        window_sum = window_sum - leaving + entering
        start = i - k + 1

        # Build a visual showing the window position
        visual = ""
        for j, val in enumerate(arr):
            if start <= j <= i:
                visual += f"[{val}]"
            else:
                visual += f" {val} "

        print(f"Step {i - k + 1}: window [{start}..{i}] = {arr[start:i+1]}, "
              f"sum = {window_sum}  (- {leaving} + {entering})")
        print(f"         {visual}")

        if window_sum > max_sum:
            max_sum = window_sum
            best_start = start

    print(f"\nMax sum = {max_sum} at window [{best_start}..{best_start + k - 1}] "
          f"= {arr[best_start:best_start + k]}")

    # Verify brute force gives the same answer
    brute = max_sum_brute_force(arr, k)
    assert brute == max_sum, f"Mismatch: brute={brute}, sliding={max_sum}"
    print(f"Verified against brute force: {brute}")


# ===========================================================================
# SECTION 2: Variable-Width Sliding Window — Longest Substring Without Repeats
# ===========================================================================

def longest_unique_substring_brute(s):
    """O(n^3) brute force — check every substring for uniqueness."""
    n = len(s)
    best = 0
    for i in range(n):
        for j in range(i, n):
            # Check if s[i..j] has all unique characters
            if len(set(s[i:j+1])) == j - i + 1:
                best = max(best, j - i + 1)
    return best


def longest_unique_substring(s):
    """O(n) sliding window with a character frequency map.

    The window [left..right] always contains unique characters.
    When we add a character that creates a duplicate, we shrink
    from the left until uniqueness is restored.

    Why O(n): left moves at most n times total across all iterations
    of right. Each character is added once and removed at most once."""
    char_count = {}  # character -> count in current window
    left = 0
    best = 0

    for right in range(len(s)):
        ch = s[right]
        char_count[ch] = char_count.get(ch, 0) + 1

        # Shrink window until no duplicates
        while char_count[ch] > 1:
            left_ch = s[left]
            char_count[left_ch] -= 1
            if char_count[left_ch] == 0:
                del char_count[left_ch]
            left += 1

        best = max(best, right - left + 1)

    return best


def demo_longest_unique_substring():
    """Visual demonstration of variable-width sliding window."""
    s = "abcabcbb"

    print("\n" + "=" * 70)
    print("VARIABLE-WIDTH SLIDING WINDOW: Longest substring without repeats")
    print("=" * 70)
    print(f"\nString: \"{s}\"")
    print()

    char_count = {}
    left = 0
    best = 0
    best_window = ""

    for right in range(len(s)):
        ch = s[right]
        char_count[ch] = char_count.get(ch, 0) + 1

        # Show expansion
        print(f"Step {right}: Add '{ch}' at right={right}")

        # Shrink if needed
        while char_count[ch] > 1:
            left_ch = s[left]
            print(f"  Duplicate '{ch}'! Remove '{left_ch}' at left={left}")
            char_count[left_ch] -= 1
            if char_count[left_ch] == 0:
                del char_count[left_ch]
            left += 1

        window = s[left:right + 1]
        if right - left + 1 > best:
            best = right - left + 1
            best_window = window

        # Visual
        visual = ""
        for i, c in enumerate(s):
            if left <= i <= right:
                visual += f"[{c}]"
            else:
                visual += f" {c} "
        print(f"  Window: [{left}..{right}] = \"{window}\", length = {right - left + 1}")
        print(f"  {visual}")
        print()

    print(f"Longest unique substring: \"{best_window}\", length = {best}")

    # Verify
    brute = longest_unique_substring_brute(s)
    assert brute == best, f"Mismatch: brute={brute}, sliding={best}"
    print(f"Verified against brute force: {brute}")


# ===========================================================================
# SECTION 3: Minimum Window Substring
# ===========================================================================

def min_window_substring(s, t):
    """Find the minimum window in s that contains all characters of t.

    Two-phase approach in each step:
    1. Expand right until all characters of t are covered.
    2. Contract left to find the smallest such window.

    We track 'formed' = number of distinct characters in t that have
    the required count in the current window. When formed == required,
    the window is valid.

    Why O(n): right moves n times. left moves at most n times total.
    Each character is processed at most twice (once by right, once by left)."""
    if not s or not t:
        return ""

    # Count characters needed from t
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1

    required = len(need)  # number of distinct chars in t that must be satisfied
    formed = 0  # how many distinct chars currently have enough count
    have = {}  # character counts in current window

    best_len = float('inf')
    best_start = 0
    left = 0

    for right in range(len(s)):
        ch = s[right]
        have[ch] = have.get(ch, 0) + 1

        # Check if this character's count now matches what we need
        if ch in need and have[ch] == need[ch]:
            formed += 1

        # Contract from left while window is valid
        while formed == required:
            # Record this valid window if it is the smallest
            window_len = right - left + 1
            if window_len < best_len:
                best_len = window_len
                best_start = left

            # Remove leftmost character
            left_ch = s[left]
            have[left_ch] -= 1
            if left_ch in need and have[left_ch] < need[left_ch]:
                formed -= 1
            left += 1

    if best_len == float('inf'):
        return ""
    return s[best_start:best_start + best_len]


def demo_min_window_substring():
    """Visual demonstration of minimum window substring."""
    s = "ADOBECODEBANC"
    t = "ABC"

    print("\n" + "=" * 70)
    print("MINIMUM WINDOW SUBSTRING")
    print("=" * 70)
    print(f"\nString s: \"{s}\"")
    print(f"String t: \"{t}\"")
    print(f"Find the shortest window in s containing all characters of t.\n")

    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1

    required = len(need)
    formed = 0
    have = {}
    left = 0
    best_len = float('inf')
    best_start = 0
    step = 0

    for right in range(len(s)):
        ch = s[right]
        have[ch] = have.get(ch, 0) + 1

        if ch in need and have[ch] == need[ch]:
            formed += 1

        # Show state before contraction
        if formed == required:
            print(f"Step {step}: right={right} ('{ch}'), window covers all of t!")

        while formed == required:
            window_len = right - left + 1
            window = s[left:right + 1]

            # Visual
            visual = ""
            for i, c in enumerate(s):
                if left <= i <= right:
                    visual += f"[{c}]"
                else:
                    visual += f" {c} "

            marker = ""
            if window_len < best_len:
                best_len = window_len
                best_start = left
                marker = " <-- NEW BEST"

            print(f"  Valid window [{left}..{right}] = \"{window}\", "
                  f"len={window_len}{marker}")
            print(f"  {visual}")

            # Contract
            left_ch = s[left]
            have[left_ch] -= 1
            if left_ch in need and have[left_ch] < need[left_ch]:
                formed -= 1
                print(f"  Remove '{left_ch}' at left={left} -> coverage broken, expand right")
            else:
                print(f"  Remove '{left_ch}' at left={left} -> still valid, keep shrinking")
            left += 1
            step += 1

        step += 1

    result = s[best_start:best_start + best_len] if best_len != float('inf') else ""
    print(f"\nMinimum window: \"{result}\" (length {best_len})")


# ===========================================================================
# SECTION 4: Kadane's Algorithm — Maximum Subarray Sum
# ===========================================================================

def kadane(arr):
    """Kadane's algorithm for maximum subarray sum.

    At each position i, we decide: extend the current subarray, or start fresh.
    If the running sum is negative, carrying it forward would only make any
    future subarray smaller. So we reset.

    This is a sliding window where the left boundary jumps forward implicitly
    whenever the accumulated sum becomes a liability rather than an asset."""
    max_sum = current = arr[0]
    start = end = temp_start = 0

    for i in range(1, len(arr)):
        if current + arr[i] < arr[i]:
            # Starting fresh at i is better than extending
            current = arr[i]
            temp_start = i
        else:
            current += arr[i]

        if current > max_sum:
            max_sum = current
            start = temp_start
            end = i

    return max_sum, start, end


def demo_kadane():
    """Visual demonstration of Kadane's algorithm."""
    arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

    print("\n" + "=" * 70)
    print("KADANE'S ALGORITHM: Maximum Subarray Sum")
    print("=" * 70)
    print(f"\nArray: {arr}")
    print(f"\nAt each step, we decide: extend the current subarray or start fresh.")
    print(f"Rule: if running sum < current element, the prefix is a liability.\n")

    max_sum = current = arr[0]
    start = end = temp_start = 0

    print(f"i=0: element={arr[0]:>3}, current_sum={current:>3}, "
          f"max_sum={max_sum:>3}, window=[{start}..{end}]")

    for i in range(1, len(arr)):
        if current + arr[i] < arr[i]:
            decision = "START FRESH"
            current = arr[i]
            temp_start = i
        else:
            decision = "extend     "
            current += arr[i]

        if current > max_sum:
            max_sum = current
            start = temp_start
            end = i

        # Visual: highlight the current subarray
        visual = ""
        for j, val in enumerate(arr):
            if temp_start <= j <= i:
                visual += f"[{val:>2}]"
            else:
                visual += f" {val:>2} "

        print(f"i={i}: element={arr[i]:>3}, {decision}, current_sum={current:>3}, "
              f"max_sum={max_sum:>3}")
        print(f"      {visual}")

    print(f"\nMaximum subarray sum = {max_sum}")
    print(f"Subarray: arr[{start}..{end}] = {arr[start:end+1]}")


# ===========================================================================
# SECTION 5: When Sliding Window Fails — The Monotonicity Requirement
# ===========================================================================

def demo_when_sliding_window_fails():
    """Show a problem where sliding window does NOT work, and explain why."""
    print("\n" + "=" * 70)
    print("WHEN SLIDING WINDOW FAILS: Subarray Sum Equals K (with negatives)")
    print("=" * 70)

    arr = [1, -1, 5, -2, 3]
    k = 3

    print(f"\nArray: {arr}")
    print(f"Target sum k = {k}")
    print(f"Find the number of subarrays that sum to exactly k.\n")

    # Brute force — correct answer
    count = 0
    subarrays = []
    for i in range(len(arr)):
        total = 0
        for j in range(i, len(arr)):
            total += arr[j]
            if total == k:
                count += 1
                subarrays.append(arr[i:j+1])

    print(f"Brute force finds {count} subarrays: {subarrays}")

    print(f"""
Why sliding window fails here:

  Consider window [0..2] = [1, -1, 5], sum = 5 > k=3.
  Should we shrink from left? Remove 1, sum = 4 > k. Remove -1, sum = 5 > k!
  Removing a negative number INCREASED the sum — shrinking made it worse.

  The monotonicity property is violated: expanding the window can either
  increase or decrease the sum (because of negative numbers). So we cannot
  guarantee that shrinking from the left will move us toward the target.

  Solution: use prefix sums + hash map (Day 19 technique).
  prefix[j] - prefix[i] = sum(arr[i..j-1])
  For each j, we need prefix[j] - k to exist in previous prefix sums.
""")

    # Prefix sum solution — O(n)
    prefix_count = {0: 1}
    prefix_sum = 0
    result = 0
    for num in arr:
        prefix_sum += num
        if prefix_sum - k in prefix_count:
            result += prefix_count[prefix_sum - k]
        prefix_count[prefix_sum] = prefix_count.get(prefix_sum, 0) + 1

    print(f"  Prefix sum + hash map finds {result} subarrays (correct: {count})")
    assert result == count


# ===========================================================================
# SECTION 6: Performance Comparison
# ===========================================================================

def demo_performance():
    """Empirical comparison of brute force vs sliding window."""
    import time

    print("\n" + "=" * 70)
    print("PERFORMANCE: Brute Force vs Sliding Window")
    print("=" * 70)

    sizes = [1_000, 5_000, 10_000, 50_000]
    k = 100

    print(f"\nMax sum of k={k} consecutive elements:\n")
    print(f"  {'n':>8}  {'Brute O(nk)':>14}  {'Sliding O(n)':>14}  {'Speedup':>8}")
    print(f"  {'-'*8}  {'-'*14}  {'-'*14}  {'-'*8}")

    for n in sizes:
        arr = list(range(n))

        start = time.perf_counter()
        b = max_sum_brute_force(arr, k)
        t_brute = time.perf_counter() - start

        start = time.perf_counter()
        s = max_sum_sliding_window(arr, k)
        t_slide = time.perf_counter() - start

        assert b == s, f"Results differ: brute={b}, sliding={s}"

        speedup = t_brute / t_slide if t_slide > 0 else float('inf')
        print(f"  {n:>8}  {t_brute:>13.6f}s  {t_slide:>13.6f}s  {speedup:>7.1f}x")


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    print("Day 18: Sliding Window — Fixed and Variable Width Patterns")
    print("=" * 70)

    demo_fixed_window()
    demo_longest_unique_substring()
    demo_min_window_substring()
    demo_kadane()
    demo_when_sliding_window_fails()
    demo_performance()

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("""
1. Fixed window: S(i+1) = S(i) - arr[i] + arr[i+k]. O(1) per slide, O(n) total.

2. Variable window: right expands, left contracts. Both move at most n times
   total, so O(n) despite the nested loop.

3. Kadane's is a sliding window where the left boundary jumps forward when
   the accumulated sum becomes negative (a liability, not an asset).

4. Sliding window requires MONOTONICITY: expanding/contracting the window
   must have a predictable effect on the condition. With negative numbers
   and exact-sum targets, monotonicity breaks — use prefix sums instead.

5. The pattern appears everywhere: TCP windows, rolling averages, rate
   limiters, stream processing. Same math, different domains.
""")
