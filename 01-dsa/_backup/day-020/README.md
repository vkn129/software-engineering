# Day 20: Binary Search Variations — Beyond Simple Lookup

## Why This Exists

Yesterday you learned to find a target in a sorted array. That is the trivial case. The real power of binary search is not "find this element" — it is "find the boundary where a property changes." This reframing turns binary search from a lookup technique into a universal problem-solving tool.

Consider: a shipping company needs to determine the minimum ship capacity to deliver all packages within D days. The packages are fixed, the days are fixed, the only variable is capacity. If capacity C works, then capacity C+1 also works. If capacity C fails, then C-1 also fails. This monotonicity — once true, stays true — means binary search applies. You are not searching an array; you are searching a *decision space*.

This is the pattern behind hundreds of algorithm problems and real engineering decisions:
- "What is the minimum server count to handle this traffic?" (monotonic: more servers = more capacity)
- "What is the minimum timeout before we should retry?" (monotonic: longer timeout = higher success rate)
- "What is the smallest batch size that keeps latency under 100ms?" (monotonic in the relevant range)

The variations you learn today — lower bound, upper bound, search on answer — appear in production systems constantly. Python's `bisect` module, C++'s `std::lower_bound`, Java's `Collections.binarySearch` — they all implement these patterns. You need to understand them from the inside.

## Theory (40 min)

### The Fundamental Insight: Monotonic Predicates

Forget "searching for an element." Think instead about a predicate — a function P(x) that returns True or False. If P is monotonic (once it becomes True, it stays True), then binary search can find the exact transition point.

```
Index:    0   1   2   3   4   5   6   7   8   9
P(x):    F   F   F   F   T   T   T   T   T   T
                         ^
                    first True = lower bound
```

Every binary search variation is just: "find where the predicate flips."

### Lower Bound: First Occurrence

Given a sorted array with duplicates, find the *first* occurrence of target.

```
Array:  [1, 3, 5, 5, 5, 5, 7, 9]
Target: 5

Simple binary search might return index 2, 3, 4, or 5 — any occurrence.
Lower bound returns index 2 — the FIRST one.
```

The predicate: P(i) = "arr[i] >= target". We want the first i where P is True.

```python
def lower_bound(arr, target):
    """Find the first index where arr[i] >= target.
    If target exists, this is its first occurrence.
    If target does not exist, this is where it would be inserted."""
    lo, hi = 0, len(arr)  # Note: hi = len(arr), not len(arr) - 1
    while lo < hi:         # Note: lo < hi, not lo <= hi
        mid = lo + (hi - lo) // 2
        if arr[mid] < target:
            lo = mid + 1   # arr[mid] is too small, exclude it
        else:
            hi = mid       # arr[mid] >= target, it MIGHT be the answer
    return lo              # lo == hi == first index where arr[i] >= target
```

**Critical difference from standard binary search:** when arr[mid] >= target, we set `hi = mid` (not `mid - 1`), because mid *might* be the answer. We also use `lo < hi` (not `lo <= hi`), because when lo == hi, we have converged.

### Upper Bound: Just Past the Last Occurrence

Given a sorted array with duplicates, find the index *just past* the last occurrence of target.

```
Array:  [1, 3, 5, 5, 5, 5, 7, 9]
Target: 5

Upper bound returns index 6 — the first element GREATER than 5.
Number of 5s = upper_bound - lower_bound = 6 - 2 = 4.
```

The predicate: P(i) = "arr[i] > target". We want the first i where P is True.

```python
def upper_bound(arr, target):
    """Find the first index where arr[i] > target."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] <= target:
            lo = mid + 1   # arr[mid] is <= target, exclude it
        else:
            hi = mid       # arr[mid] > target, it might be the answer
    return lo
```

The only difference from lower_bound: `<` becomes `<=` in the comparison. That one character changes "first occurrence" to "just past last occurrence."

### Count of an Element

```python
count = upper_bound(arr, target) - lower_bound(arr, target)
```

Both are O(log n). This counts occurrences in O(log n) — far better than the O(n) linear scan.

### Search in Rotated Sorted Array

A sorted array has been rotated: `[4, 5, 6, 7, 0, 1, 2]`. Find a target.

The key insight: at least one half of the array (split at mid) is always sorted. Determine which half is sorted, check if the target falls in that range, and recurse accordingly.

```python
def search_rotated(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid

        # Left half is sorted
        if arr[lo] <= arr[mid]:
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1  # target is in sorted left half
            else:
                lo = mid + 1  # target is in right half
        # Right half is sorted
        else:
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1  # target is in sorted right half
            else:
                hi = mid - 1  # target is in left half
    return -1
```

### Binary Search on the Answer: The Search Space Paradigm

This is the most powerful and least intuitive application. Instead of searching an array, you search a *range of possible answers*.

**Problem:** Ship packages with weights `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` in 5 days. Packages must be shipped in order. What is the minimum ship capacity?

The key observations:
1. Minimum possible capacity = max(weights) = 10 (must fit the heaviest package)
2. Maximum possible capacity = sum(weights) = 55 (ship everything in one day)
3. If capacity C works in D days, then C+1 also works — **monotonic!**

```python
def can_ship(weights, capacity, days):
    """Can we ship all packages with this capacity in this many days?"""
    current_load = 0
    days_needed = 1
    for w in weights:
        if current_load + w > capacity:
            days_needed += 1
            current_load = 0
        current_load += w
    return days_needed <= days

def min_ship_capacity(weights, days):
    """Binary search on the answer."""
    lo = max(weights)       # minimum possible capacity
    hi = sum(weights)       # maximum possible capacity
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if can_ship(weights, mid, days):
            hi = mid        # this capacity works, try smaller
        else:
            lo = mid + 1    # this capacity fails, need bigger
    return lo
```

This pattern applies everywhere:
- Minimize the maximum page sum when splitting an array into k subarrays
- Find the smallest radius to cover all points with k circles
- Determine the minimum time to complete all tasks with m workers

### Python's bisect Module

Python provides `bisect_left` (lower bound) and `bisect_right` (upper bound) in the standard library. Now that you understand the internals, you can use them confidently.

```python
import bisect

arr = [1, 3, 5, 5, 5, 7, 9]
bisect.bisect_left(arr, 5)   # 2  — first index where 5 could be inserted (lower bound)
bisect.bisect_right(arr, 5)  # 5  — last index where 5 could be inserted (upper bound)
bisect.insort(arr, 6)        # inserts 6 at the correct position
```

### Connection to Monotonic Functions and Decision Problems

Binary search works on any monotonic function f: integers -> {True, False}. This makes it applicable to:

- **Optimization problems:** "minimize x such that P(x) is True" — binary search on x
- **Decision problems:** "is there a solution with cost <= C?" — if this is monotonic in C, binary search
- **Numerical methods:** bisection method for finding roots of continuous functions (same idea, continuous domain)

The connection to mathematics is direct: binary search is the discrete analog of the bisection method, which finds zeros of continuous functions by repeatedly halving an interval. Both exploit monotonicity.

## Practice (20 min)

Work through `practice.py`. These exercises build from straightforward lower/upper bound implementations to the "search on answer" paradigm. Run the file to check your solutions.

Also run `binary_search_variations.py` to see visualizations of each variation and timing comparisons.

## Daily Project

Run `binary_search_variations.py`. The script demonstrates:
1. Lower/upper bound with step traces
2. Rotated array search
3. Binary search on the answer (shipping problem)
4. Comparison with Python's bisect module

Your tasks:
1. Implement a new "search on answer" problem: given an array and integer k, find the minimum largest sum when splitting the array into k contiguous subarrays.
2. Verify that bisect_left and bisect_right match your manual implementations.

## Checkpoint Questions

1. Explain the difference between `hi = mid` and `hi = mid - 1`. When do you use each, and why does using the wrong one cause bugs?

2. In the lower bound implementation, why is hi initialized to `len(arr)` instead of `len(arr) - 1`? What goes wrong if you use `len(arr) - 1`?

3. You have a sorted array with 1 million elements, all between 1 and 100. A particular value appears 500,000 times. How do you count its occurrences in O(log n) time?

4. In the "binary search on the answer" pattern, what are the two things you must identify before you can apply it? Why does monotonicity matter?

5. A colleague's lower_bound implementation uses `lo <= hi` with `hi = mid - 1`. It passes most tests but fails on some inputs. Construct a specific input where it fails and explain why.
