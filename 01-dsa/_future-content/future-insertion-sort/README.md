# Day 23: Insertion Sort — The Best O(n^2) Sort

## Why This Exists

Insertion sort is how most people naturally sort a hand of playing cards: pick up
one card at a time, slide it into its correct position among the cards already in
your hand.

Despite being O(n^2) in the worst case, insertion sort is the **most practical**
of all quadratic sorts:

1. **O(n) on nearly-sorted data** — if each element is at most k positions from its
   final position, insertion sort runs in O(nk) time.
2. **Tiny constant factor** — the inner loop is just a compare-and-shift. No
   function calls, no index tracking. On modern CPUs, this is extremely cache-friendly.
3. **Used inside production sorts** — Python's Timsort and C++'s introsort both
   switch to insertion sort for small subarrays (typically n < 16-64). The overhead
   of recursion and partitioning in quicksort/mergesort isn't worth it for tiny arrays.
4. **Online algorithm** — it can sort elements as they arrive, one at a time.

### The Practical Truth
If you have fewer than ~50 elements, insertion sort often **beats quicksort** in
wall-clock time. This is not theoretical — it's measured. Java's `Arrays.sort()`
uses insertion sort for arrays of size <= 47.

---

## Theory (40 min)

### The Algorithm

```
Start:  [5, 3, 8, 1, 2]
         ^  sorted region (trivially — one element)

Step 1: Insert 3 into [5]
        3 < 5, shift 5 right, place 3
        [3, 5, 8, 1, 2]
         ^^^^  sorted

Step 2: Insert 8 into [3, 5]
        8 > 5, already in place
        [3, 5, 8, 1, 2]
         ^^^^^^^  sorted

Step 3: Insert 1 into [3, 5, 8]
        1 < 8, shift 8 right
        1 < 5, shift 5 right
        1 < 3, shift 3 right
        Place 1 at index 0
        [1, 3, 5, 8, 2]
         ^^^^^^^^^^  sorted

Step 4: Insert 2 into [1, 3, 5, 8]
        2 < 8, shift 8 right
        2 < 5, shift 5 right
        2 < 3, shift 3 right
        2 > 1, place 2 after 1
        [1, 2, 3, 5, 8]
         ^^^^^^^^^^^^^  sorted!
```

### Loop Invariant

**At the start of iteration i, the subarray `a[0..i-1]` contains the same elements
as the original `a[0..i-1]`, but in sorted order.**

Proof:
- *Initialization*: Before iteration 1, `a[0..0]` is a single element (trivially sorted).
- *Maintenance*: In iteration i, we take `a[i]` and insert it into `a[0..i-1]` by
  shifting larger elements right. After insertion, `a[0..i]` is sorted and contains
  the same elements as the original `a[0..i]`.
- *Termination*: After iteration n-1, `a[0..n-1]` is sorted.

### Why It Wins on Nearly-Sorted Data

The inner loop only runs while the current element is less than the element to its
left. If the array is already sorted, the inner loop body **never executes** — each
element is immediately >= the element before it. Total work: n-1 comparisons, 0 shifts.

More precisely, insertion sort's running time is O(n + d), where d is the number of
**inversions** (pairs of elements that are out of order). For a sorted array, d = 0.
For a nearly-sorted array, d is small.

### Inversions: The Formal Measure

An inversion is a pair (i, j) where i < j but a[i] > a[j].
- Sorted array: 0 inversions
- Reverse-sorted array of n elements: n(n-1)/2 inversions (maximum)
- Each swap in bubble sort fixes exactly 1 inversion
- Each shift in insertion sort fixes exactly 1 inversion

### Complexity

| Case | Comparisons | Shifts | When |
|------|------------|--------|------|
| Best | O(n) | 0 | Already sorted |
| Average | O(n^2) | O(n^2) | Random |
| Worst | O(n^2) | O(n^2) | Reverse sorted |

- Space: O(1) — in-place
- Stable: YES (we use `<` not `<=` to decide when to stop shifting)
- Adaptive: YES (O(n) on nearly-sorted data)

### Binary Insertion Sort

We can use binary search to find the insertion point, reducing comparisons to
O(n log n). But we still need O(n^2) shifts because we're working with an array.
This variant is useful when comparisons are expensive (e.g., comparing long strings).

---

## Practice (20 min)

Complete the exercises in `practice.py`:

1. Implement basic insertion sort
2. Implement insertion sort that counts comparisons and shifts
3. Count inversions in an array using insertion sort
4. Implement binary insertion sort

---

## Daily Project

Run `insertion_sort.py` to see:
- Step-by-step visualization
- Benchmark: insertion sort vs quicksort on nearly-sorted data
- Inversion counting
- The crossover point where insertion sort beats quicksort

---

## Checkpoint Questions

1. **Why does Python's Timsort use insertion sort for small runs instead of just
   using mergesort all the way down?**

2. **An array has each element at most 3 positions from its sorted position.
   What's the time complexity of insertion sort on this array? Prove it.**

3. **Why is insertion sort stable but selection sort isn't?**
   (Think about what operation each uses: shifting vs swapping.)

4. **You receive a stream of numbers one at a time and need to maintain a sorted
   list. Why is insertion sort the natural choice? What data structure would make
   it even better?**

5. **If comparison is expensive but moving data is cheap, would you modify
   insertion sort? How?**
