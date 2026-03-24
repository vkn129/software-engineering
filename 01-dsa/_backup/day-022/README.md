# Day 22: Bubble Sort & Selection Sort

## Why This Exists

Before quicksort, mergesort, or any clever algorithm existed, people needed to put
things in order. The earliest computer scientists — working on machines with kilobytes
of memory — invented the simplest possible approaches: compare two things, swap if
wrong. Repeat until done.

Bubble sort and selection sort are **not efficient**. Nobody uses them in production
for large datasets. So why study them?

1. **They teach you to think about correctness.** You can *prove* these algorithms
   work using loop invariants — a skill that transfers to every algorithm you'll
   ever write.
2. **They teach you to think about performance.** Understanding *why* O(n^2) is bad
   gives you the vocabulary to appreciate O(n log n) later.
3. **They appear in interviews** — not as "implement bubble sort" but as "why is
   this code O(n^2)?" You need to recognize the pattern.
4. **Selection sort has a real use case**: minimizing the number of *swaps*. If
   writing to memory is expensive (flash memory, network writes), selection sort's
   O(n) swaps beats everything.

### Historical note
Bubble sort was analyzed by mathematicians as early as 1956. Donald Knuth famously
wrote: "the bubble sort seems to have nothing to recommend it, except a catchy name."
Yet it persists in education because it's the most intuitive sorting idea humans
invent independently.

---

## Theory (40 min)

### Bubble Sort

**Idea**: Walk through the array comparing adjacent elements. If they're out of order,
swap them. After one full pass, the largest element has "bubbled" to the end. Repeat,
ignoring the last (already sorted) element each time.

```
Pass 1: [5, 3, 8, 1, 2]
         ^--^  swap -> [3, 5, 8, 1, 2]
            ^--^  ok   [3, 5, 8, 1, 2]
               ^--^  swap -> [3, 5, 1, 8, 2]
                  ^--^  swap -> [3, 5, 1, 2, 8]  <- 8 is in place

Pass 2: [3, 5, 1, 2, | 8]   (ignore last)
         ^--^  ok
            ^--^  swap -> [3, 1, 5, 2, | 8]
               ^--^  swap -> [3, 1, 2, 5, | 8]  <- 5 is in place

Pass 3: [3, 1, 2, | 5, 8]
         ^--^  swap -> [1, 3, 2, | 5, 8]
            ^--^  swap -> [1, 2, 3, | 5, 8]  <- 3 is in place

Pass 4: [1, 2, | 3, 5, 8]
         ^--^  ok  <- no swaps, array is sorted!
```

**Loop invariant for bubble sort**: After pass `i`, the largest `i` elements are in
their final sorted positions at the end of the array.

**Proof of correctness**:
- *Initialization*: Before pass 1, zero elements are in final position (trivially true).
- *Maintenance*: During pass `i`, we compare all adjacent pairs in the unsorted region.
  The maximum element in that region will be swapped rightward at every step until it
  reaches position `n - i`. So after pass `i`, the `i`-th largest element is in place.
- *Termination*: After `n-1` passes, the largest `n-1` elements are in place, which
  means the smallest element is also in place. The array is sorted.

**Complexity**:
- Worst case: O(n^2) comparisons, O(n^2) swaps (reverse-sorted input)
- Best case: O(n) comparisons, O(1) swaps (already sorted, with early-exit optimization)
- Space: O(1) — in-place

**Stability**: Bubble sort IS stable. Equal elements are never swapped (we only swap
when `a[j] > a[j+1]`, not `>=`), so their relative order is preserved.

---

### Selection Sort

**Idea**: Find the minimum element in the unsorted region. Swap it into position.
Repeat for the next position.

```
[5, 3, 8, 1, 2]
 Find min in [0..4] -> 1 at index 3
 Swap arr[0] and arr[3] -> [1, 3, 8, 5, 2]

[1, | 3, 8, 5, 2]
 Find min in [1..4] -> 2 at index 4
 Swap arr[1] and arr[4] -> [1, 2, 8, 5, 3]

[1, 2, | 8, 5, 3]
 Find min in [2..4] -> 3 at index 4
 Swap arr[2] and arr[4] -> [1, 2, 3, 5, 8]

[1, 2, 3, | 5, 8]
 Find min in [3..4] -> 5 at index 3
 No swap needed -> [1, 2, 3, 5, 8]

Done!
```

**Loop invariant for selection sort**: After iteration `i`, the first `i` elements
contain the `i` smallest values in sorted order.

**Proof of correctness**:
- *Initialization*: Before iteration 1, zero elements are placed (trivially true).
- *Maintenance*: In iteration `i`, we scan the unsorted region `[i..n-1]` and find
  the minimum. We swap it into position `i`. Since all elements in `[0..i-1]` are
  already <= everything in `[i..n-1]` (they're the smallest `i` values), and we just
  placed the next smallest, positions `[0..i]` now contain the `i+1` smallest values
  in sorted order.
- *Termination*: After `n-1` iterations, the first `n-1` positions are correct, so
  position `n-1` must also be correct.

**Complexity**:
- Always O(n^2) comparisons — no best case improvement
- Always O(n) swaps — this is selection sort's advantage
- Space: O(1)

**Stability**: Selection sort is NOT stable by default. The swap can move equal
elements past each other.

Example: `[(2,'a'), (2,'b'), (1,'c')]`
- Find min: `(1,'c')` at index 2. Swap with index 0.
- Result: `[(1,'c'), (2,'b'), (2,'a')]` — the two 2s swapped relative order!

---

### Comparison Table

| Property          | Bubble Sort      | Selection Sort   |
|-------------------|------------------|------------------|
| Comparisons       | O(n^2)           | O(n^2)           |
| Swaps (worst)     | O(n^2)           | O(n)             |
| Best case         | O(n) with flag   | O(n^2)           |
| Stable?           | Yes              | No               |
| Adaptive?         | Yes (early exit) | No               |
| Use case          | Teaching only    | Minimize writes  |

---

## Practice (20 min)

Complete the exercises in `practice.py`:

1. Implement bubble sort with the early-exit optimization
2. Implement selection sort
3. Count the exact number of comparisons and swaps for a given input
4. Make selection sort stable (hint: use insertion into position instead of swap)

---

## Daily Project

Run `bubble_selection_sort.py` to see:
- Step-by-step visualization of both algorithms
- Comparison and swap counts
- Stability demonstration with concrete examples
- Performance comparison on different input types

---

## Checkpoint Questions

1. **Why does bubble sort's early-exit optimization help on nearly-sorted data but
   selection sort has no equivalent optimization?**
   (Think about what information each pass gives you.)

2. **You're writing data to a flash drive where each write costs 100x more than a
   read. Which O(n^2) sort do you pick and why?**

3. **Can you modify selection sort to be stable? What's the cost?**
   (Hint: instead of swapping, what if you *inserted*?)

4. **A coworker says "bubble sort is O(n) best case, so it's actually good for
   sorted data." What's the flaw in this reasoning?**

5. **Prove that bubble sort's inner loop processes one fewer element each pass.
   What does this tell you about the total number of comparisons?**
   (Sum: (n-1) + (n-2) + ... + 1 = n(n-1)/2)
