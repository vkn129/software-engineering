# Day 18: Sliding Window — Fixed and Variable Width Patterns

## Why This Exists

The brute-force approach to subarray problems is to check every possible subarray: O(n^2) subarrays, each potentially requiring O(n) work to evaluate, giving O(n^3) or O(n^2). Sliding window exploits a simple observation: when you slide from subarray [i..j] to [i+1..j+1], you lose one element on the left and gain one on the right. If you can update your answer incrementally instead of recomputing from scratch, you eliminate the redundant work.

This is not an algorithm — it is a design pattern for maintaining a running computation over a contiguous slice of data. The key insight is **incrementality**: if you can express `answer([i+1..j+1])` in terms of `answer([i..j])` plus a constant amount of work, you get O(n) total.

Sliding window is everywhere in production systems. TCP flow control uses a sliding window over byte sequences. Time-series databases compute rolling averages with sliding windows. Stream processing frameworks (Kafka Streams, Flink) have "windowed aggregations" as a core primitive. Rate limiters count events in a sliding time window. Every one of these is the same mathematical idea.

There are two flavors:
- **Fixed-width**: window size k is given. Slide it across. O(n).
- **Variable-width**: window grows and shrinks to satisfy a condition. O(n) when the condition is monotonic — meaning once it is violated, shrinking the window can restore it.

The critical question for any sliding window problem is: **does the condition have the monotonicity property?** If expanding the window can only make things "worse" (or only "better"), then sliding window works. If the effect of expansion is unpredictable, it does not.

---

## Theory (40 min)

### 1. Fixed-Width Sliding Window (10 min)

**Problem:** Given an array of n integers and a window size k, find the maximum sum of any k consecutive elements.

**Brute force:** For each starting index i, sum elements i through i+k-1. That is O(n*k).

**Sliding window:** Compute the sum of the first window. Then slide: subtract the element leaving, add the element entering.

```
Array: [2, 1, 5, 1, 3, 2], k=3

Window [0..2]: 2+1+5 = 8
Window [1..3]: 8 - 2 + 1 = 7    (subtract arr[0], add arr[3])
Window [2..4]: 7 - 1 + 3 = 9    (subtract arr[1], add arr[4])
Window [3..5]: 9 - 5 + 2 = 6    (subtract arr[2], add arr[5])

Max = 9
```

**Why O(n):** Each element is added exactly once and subtracted exactly once. Total operations: 2n.

**The math:** Let S(i) = sum of window starting at index i. Then:
```
S(i+1) = S(i) - arr[i] + arr[i+k]
```
This recurrence is what makes the window "slide" — each new sum costs O(1) to compute from the previous one.

### 2. Variable-Width Sliding Window (15 min)

Variable-width windows grow and shrink. Two pointers `left` and `right` define the window. `right` expands to explore, `left` contracts to restore a condition.

**Template:**
```python
left = 0
for right in range(n):
    # Add arr[right] to window state
    while window_condition_violated():
        # Remove arr[left] from window state
        left += 1
    # Update answer from current window [left..right]
```

**Why O(n):** The key invariant is that `left` only moves right. Over the entire execution, `left` moves at most n times total (not n times per iteration of `right`). So total work = O(n) for right + O(n) for left = O(n).

**Example — Longest substring without repeating characters:**

```
s = "abcabcbb"

right=0 (a): window={a}, len=1
right=1 (b): window={a,b}, len=2
right=2 (c): window={a,b,c}, len=3
right=3 (a): duplicate! shrink: remove a, left=1. window={b,c,a}, len=3
right=4 (b): duplicate! shrink: remove b, left=2. window={c,a,b}, len=3
right=5 (c): duplicate! shrink: remove c, left=3. window={a,b,c}, len=3
right=6 (b): duplicate! shrink: remove a,b left=5. window={c,b}, len=2
right=7 (b): duplicate! shrink: remove c,b left=7. window={b}, len=1

Answer: 3
```

**Monotonicity:** If a window [left..right] has no duplicates, then any sub-window of it also has no duplicates. If it has a duplicate, expanding it cannot remove the duplicate. This monotonicity is what makes the two-pointer approach correct.

### 3. Minimum Window Substring (10 min)

**Problem:** Given strings s and t, find the minimum window in s that contains all characters of t.

This is the classic hard variable-width sliding window problem.

**Approach:**
1. Count character frequencies needed from t.
2. Expand right to include characters until all of t is covered.
3. Contract left to find the minimum window that still covers t.
4. Record the minimum, then contract left once more to break the condition, and continue expanding right.

**Why it works:** Once all characters of t are in the window, shrinking from the left can only remove characters (making coverage worse). Once coverage is broken, only expanding right can restore it. This monotonicity drives the two-pointer approach.

### 4. Kadane's Algorithm as Sliding Window (5 min)

Kadane's algorithm for maximum subarray sum is a special case of variable-width sliding window where the "window" is implicit.

**The insight:** A subarray ending at position i either:
- Extends the subarray ending at i-1 (if that sum was positive)
- Starts fresh at i (if the previous sum was negative — carrying it forward would only hurt)

```python
def kadane(arr):
    max_sum = current = arr[0]
    for i in range(1, len(arr)):
        current = max(arr[i], current + arr[i])
        max_sum = max(max_sum, current)
    return max_sum
```

**Why this is a sliding window:** `current` tracks the sum of the "current window." When `current` drops below `arr[i]`, the window resets to start at i. The left boundary jumps forward implicitly.

**Monotonicity:** If the running sum is negative, extending the window backward (keeping those elements) can only make any future subarray worse. So we discard the entire prefix.

### 5. When Sliding Window Does NOT Work

Sliding window requires that the window condition be monotonic with respect to window size.

**It fails when:**
- Elements can be negative AND you need exact sums (not max/min) — the sum can go up or down unpredictably as you expand
- The condition depends on the specific arrangement of elements, not just what is in the window
- You need non-contiguous subsequences (not subarrays)

**Example of failure:** "Find the number of subarrays with sum exactly equal to k" when elements can be negative. Expanding the window might increase or decrease the sum, so you cannot use two pointers. You need prefix sums + hash map instead (Day 19's technique).

---

## Practice (20 min)

1. Run `sliding_window.py` and study the step-by-step visualizations showing how the window slides, expands, and contracts.

2. Open `practice.py` and complete the TODO exercises:
   - Maximum sum of k consecutive elements (fixed window)
   - Maximum subarray sum (Kadane's algorithm)
   - Longest substring without repeating characters
   - Minimum window substring

---

## Daily Project

After running `sliding_window.py`:

1. Trace through the minimum-window-substring visualization. At each step, verify: why is it safe to contract the left boundary? What invariant does the contraction maintain?
2. Modify Kadane's algorithm to also return the start and end indices of the maximum subarray. What additional state do you need to track?
3. Think about this: "Find the longest subarray with sum <= k" where all elements are positive. Does sliding window work? What if elements can be negative? Why does the sign matter?

---

## Checkpoint Questions

1. **Fixed-width sliding window computes each new window sum in O(1). What is the recurrence?** Write it as S(i+1) = f(S(i), arr). Why does this give O(n) total instead of O(nk)?

2. **Variable-width sliding window is O(n) even though it has a nested while loop. Explain why.** Use the argument about how many times `left` moves in total across all iterations.

3. **Kadane's algorithm resets the current sum when it goes negative. Why is it correct to discard the entire prefix, rather than just removing one element from the left?** What property of negative prefixes guarantees this?

4. **"Longest substring without repeating characters" works with sliding window. "Number of subarrays with sum exactly k (with negative numbers)" does not. What is the fundamental difference?** Express it in terms of monotonicity.

5. **You are designing a rate limiter that allows at most k requests per sliding window of T seconds. How would you implement this using the sliding window pattern?** What data structure holds the window state?
