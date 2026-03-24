# Day 17: Two Pointers — The Fundamental Array Technique

## Why This Exists

Many array problems have an obvious O(n^2) brute-force solution: for each element, scan the rest of the array. Two pointers eliminates this redundancy by maintaining an invariant — a logical guarantee about what the pointers have already ruled out — so you never recheck work.

This is not a "trick." It is a direct application of mathematical reasoning: if you can prove that moving one pointer eliminates entire regions of the search space, you reduce O(n^2) to O(n). The proof structure is always the same: define your invariant, show that each step preserves it, and show that the pointers converge.

Two pointers shows up everywhere in production code, not just interviews. Binary search is two pointers (lo and hi converging). The merge step of merge sort is two pointers walking forward. The TCP sliding window is two pointers on a byte stream. Partition in quicksort is two pointers moving toward each other. Once you see the pattern, you see it constantly.

The reason this technique is worth an entire day is that it teaches you to think in invariants — the single most important skill in algorithm design. An invariant is a property that remains true at every step of your loop. If you can state the invariant, you can prove correctness. If you cannot state it, you are guessing.

---

## Theory (40 min)

### 1. The Core Idea (10 min)

Two pointers means maintaining two indices into an array (or string, which is an array) and moving them according to rules that preserve an invariant.

There are two main patterns:

**Opposite direction (converging):** Pointers start at the two ends and move toward each other. Used when the answer depends on combining elements from different parts of the array.

```
[1, 2, 4, 7, 11, 15]
 ^                 ^
 L                 R
```

**Same direction (fast/slow):** Both pointers start at the beginning. The fast pointer explores ahead while the slow pointer marks a boundary. Used for partitioning, deduplication, and the linked-list cycle detection trick.

```
[0, 0, 1, 1, 1, 2, 2, 3]
 ^
 S,F  (both start here, fast moves ahead)
```

### 2. Opposite Direction — Pair Sum in Sorted Array (10 min)

**Problem:** Given a sorted array and a target sum, find two elements that add up to the target.

**Brute force:** Check every pair. O(n^2).

**Two pointers:** Start L at the beginning, R at the end.
- If `arr[L] + arr[R] == target`: found it.
- If `arr[L] + arr[R] < target`: sum is too small. Moving R left would make it smaller. Move L right.
- If `arr[L] + arr[R] > target`: sum is too big. Moving L right would make it bigger. Move R left.

```python
def pair_sum(arr, target):
    L, R = 0, len(arr) - 1
    while L < R:
        s = arr[L] + arr[R]
        if s == target:
            return (L, R)
        elif s < target:
            L += 1
        else:
            R -= 1
    return None
```

**Why this is O(n):** Each step moves exactly one pointer. Each pointer moves at most n times. Total steps <= 2n = O(n).

**The invariant:** At every step, if a solution (i, j) exists with i >= L and j <= R, we have not ruled it out. Proof: when we move L right, we know `arr[L] + arr[R] < target`, so `arr[L] + arr[k] < target` for all k < R. No valid pair uses the old L. Symmetric argument for moving R left.

### 3. Same Direction — Remove Duplicates In Place (10 min)

**Problem:** Given a sorted array, remove duplicates in-place. Return the new length. The first k elements should contain the unique values.

```
Input:  [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
Output: 5, array = [0, 1, 2, 3, 4, ...]
```

**Two pointers:**
- `slow` marks the position where the next unique element should go.
- `fast` scans ahead looking for new values.

```python
def remove_duplicates(arr):
    if not arr:
        return 0
    slow = 0
    for fast in range(1, len(arr)):
        if arr[fast] != arr[slow]:
            slow += 1
            arr[slow] = arr[fast]
    return slow + 1
```

**The invariant:** `arr[0..slow]` contains exactly the unique elements seen so far, in order. Every time `fast` finds a new value (different from `arr[slow]`), we advance `slow` and place it.

**Why O(n):** `fast` visits each element exactly once. `slow` advances at most n times. One pass.

### 4. Container With Most Water (10 min)

**Problem:** Given n vertical lines at positions 0..n-1 with heights `h[i]`, find two lines that form a container holding the most water.

Water between lines i and j = `min(h[i], h[j]) * (j - i)`.

**Brute force:** Check all pairs. O(n^2).

**Two pointers (opposite direction):**

```python
def max_water(heights):
    L, R = 0, len(heights) - 1
    best = 0
    while L < R:
        water = min(heights[L], heights[R]) * (R - L)
        best = max(best, water)
        if heights[L] < heights[R]:
            L += 1
        else:
            R -= 1
    return best
```

**The invariant and why we move the shorter line:** The width `(R - L)` will only decrease as we converge. If `h[L] < h[R]`, then every container using L has height at most `h[L]` (the shorter line is the bottleneck). Moving R left cannot increase the height above `h[L]` and will decrease the width. So no future pairing with L can beat what we already computed. We are safe to move L right and look for a taller line.

This is the hardest invariant to prove among classic two-pointer problems, and it is a common interview question precisely because the "why" is subtle.

### 5. When Two Pointers Does NOT Apply

Two pointers requires structure — typically that the array is sorted, or that the problem has a monotonic property that lets you reason about which direction to move.

It does NOT work when:
- The array is unsorted and you need pair sums (use a hash set instead — O(n) with O(n) space)
- You need to find all triplets/quadruplets (two pointers reduces one level, but you still need outer loops)
- The relationship between elements is not monotonic

---

## Practice (20 min)

1. Run `two_pointers.py` and study the step-by-step visualizations showing how pointers move and why.

2. Open `practice.py` and complete the TODO exercises:
   - Pair sum in sorted array
   - Palindrome checking with two pointers
   - Remove element in-place
   - Sort colors (Dutch national flag)

---

## Daily Project

The visualized demonstrations are in `two_pointers.py`. After running it:

1. Trace through the container-with-most-water visualization and verify the invariant at each step: why is it safe to skip the pointer we moved past?
2. Implement three-sum (find three elements summing to zero) by combining a loop with two pointers. What is the complexity?
3. Think about why two pointers on an unsorted array does not help for pair sum. What structure in the sorted array makes the invariant work?

---

## Checkpoint Questions

1. **State the invariant for pair-sum in a sorted array.** If `arr[L] + arr[R] < target`, why is it correct to increment L? Why can we not miss a valid pair?

2. **Remove duplicates in-place uses two pointers moving in the same direction. Why does the slow pointer only advance when `arr[fast] != arr[slow]`?** What would break if you advanced it unconditionally?

3. **Container with most water: why do we move the pointer at the shorter line?** If both lines have the same height, does it matter which one we move? Prove it.

4. **You have an unsorted array and need to find if any two elements sum to a target. Can you use two pointers?** What would you need to do first? What is the total complexity? Is there a better approach?

5. **Two pointers reduced pair-sum from O(n^2) to O(n). What is the fundamental reason this works?** Express it in terms of how many candidate pairs each pointer movement eliminates.
