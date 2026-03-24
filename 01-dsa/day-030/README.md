# Day 30: Monotonic Stack

## Why This Exists

Many problems ask "for each element, find the next/previous greater/smaller element."
The brute-force approach checks every pair — O(n^2). A monotonic stack solves these in
O(n) by maintaining a stack where elements are always in sorted order (either all
increasing or all decreasing from bottom to top). Each element is pushed and popped
**at most once**, giving amortized O(n) across all operations.

This is one of the most elegant examples of amortized analysis turning a quadratic
problem into a linear one.

## Theory

### What Is a Monotonic Stack?

A stack where the elements from bottom to top are either:
- **Monotonically decreasing**: each new element is smaller than the top (used to find *next greater element*)
- **Monotonically increasing**: each new element is larger than the top (used to find *next smaller element*)

When a new element violates the monotonic property, we pop elements until the property
is restored. The popped elements have just "found" their answer — the new element is
their next greater (or smaller) element.

### Why Amortized O(n)?

Every element enters the stack exactly once and leaves exactly once. Even though the
inner while-loop can pop multiple elements on a single iteration of the outer loop,
the **total** number of pops across all iterations is at most n. So the total work is
O(n) pushes + O(n) pops = O(n).

This is the same amortized argument used for dynamic arrays (doubling) — individual
operations may be expensive, but the aggregate cost is bounded.

### Decreasing vs Increasing

| Stack Type (bottom-to-top) | Maintains | Finds |
|---|---|---|
| Decreasing | Elements waiting for a smaller value | Next Smaller Element |
| Increasing | Elements waiting for a larger value | Next Greater Element |

**Careful**: naming conventions vary across sources. What matters is the invariant you
maintain and what triggers a pop.

### Core Patterns

**Next Greater Element (NGE)**
For each element, find the first element to its right that is strictly greater.
- Traverse left-to-right, maintain a decreasing stack (of indices).
- When `arr[i] > stack.top()`, pop and record `arr[i]` as the NGE for the popped index.

**Next Smaller Element (NSE)**
Mirror of NGE — maintain an increasing stack, pop when `arr[i] < stack.top()`.

**Largest Rectangle in Histogram**
For each bar, find how far it can extend left and right without meeting a shorter bar.
This is equivalent to finding the previous and next smaller elements. The rectangle
width for bar `i` is `right_boundary[i] - left_boundary[i] - 1`.

**Stock Span**
For each day, count consecutive days before it (including itself) where price was
<= today's price. This is "distance to previous greater element."

**Daily Temperatures**
"How many days until a warmer temperature?" — direct application of Next Greater Element
on temperature values.

## Practice

See `monotonic_stack.py` for reference implementations and `practice.py` for exercises.

### Exercises (in practice.py)

1. **Trapping Rain Water** (stack-based approach)
2. **Remove K Digits** for smallest number
3. **Sum of Subarray Minimums**
4. **Maximum Width Ramp**
5. **132 Pattern Detection**

## Checkpoint Questions

1. Why is the monotonic stack O(n) and not O(n^2) despite nested loops?
   > Each element is pushed once and popped once. Total operations = 2n = O(n).

2. When would you traverse right-to-left instead of left-to-right?
   > When you need the *previous* greater/smaller element instead of the *next*.

3. Why store indices in the stack instead of values?
   > Indices let you compute distances (spans, widths) and also look up the value via the original array.

4. How does the histogram problem reduce to monotonic stack?
   > Each bar's maximum rectangle extends until it hits a shorter bar on each side — those are the previous and next smaller elements.

5. What is the relationship between monotonic stack and monotonic queue (deque)?
   > Both maintain sorted order. The deque variant supports removal from both ends, enabling sliding-window min/max in O(n). The stack is a special case where we only need one end.
