# Day 16: Dynamic Arrays — Growth Strategies and Amortized O(1) Append

## Why This Exists

Yesterday you learned that arrays give you O(1) random access because of contiguous
memory and pointer arithmetic. But arrays have a problem: **they have a fixed size**.
When you allocate 10 slots and need to store an 11th element, you are stuck. The memory
after your array might belong to something else. You cannot just "extend" into it.

Dynamic arrays solve this by maintaining a **capacity** that is larger than the current
**size**. When the array fills up, they allocate a new, bigger array, copy everything
over, and free the old one. This single idea — over-allocate and resize on overflow —
is behind Python's `list`, Java's `ArrayList`, C++'s `std::vector`, Go's slices, and
Rust's `Vec`.

The critical question is: **how much bigger should the new array be?**

If you grow by 1 slot each time, you copy n elements on every append, making n appends
cost 1 + 2 + 3 + ... + n = O(n^2) total. That is catastrophically slow.

If you double the capacity each time, the copies become exponentially rare. The total
cost of n appends becomes O(n) — an **amortized O(1)** per append. This is not a trick
or an approximation. It is a provable mathematical result, and understanding it is
essential for reasoning about the cost of real-world code.

CPython does not double. It uses a carefully tuned growth formula that balances memory
waste against copy frequency. We will derive why, implement alternatives, and measure
the consequences.

---

## Theory (40 min)

### 1. The Resize Problem (5 min)

A static array of capacity C can hold at most C elements. When you try to insert
element C+1:

```
Before: [10][20][30][40][??][??]  capacity=6, size=4
                                   ↑ next insert goes here, no problem

After:  [10][20][30][40][50][60]  capacity=6, size=6
                                   ↑ array is FULL

Insert 70? Must:
  1. Allocate new array of capacity > 6
  2. Copy all 6 elements to new array       ← O(n) operation
  3. Insert 70 in new array
  4. Free old array
```

The copy in step 2 is unavoidable — you cannot move contiguous memory piecewise because
the new block might be at a completely different address. This O(n) resize is the price
of contiguous storage.

### 2. Growth Strategies and Their Costs (10 min)

**Additive growth (grow by k):**
Each resize copies all existing elements. After n appends, you resize at sizes k, 2k,
3k, ... With n/k resizes, total copies = k + 2k + 3k + ... + n ≈ n^2/(2k).

Total cost: **O(n^2)**. Amortized cost per append: **O(n)**.

**Multiplicative growth (grow by factor f):**
Resize at sizes C, fC, f^2C, f^3C, ... After n appends, you have ~log_f(n) resizes.
Total copies = C + fC + f^2C + ... + n. This is a geometric series that sums to
n * f/(f-1) = **O(n)**.

Total cost: **O(n)**. Amortized cost per append: **O(1)**.

**The math that matters:**
```
Geometric series:  1 + f + f^2 + ... + f^k = (f^(k+1) - 1) / (f - 1)

For f = 2:  1 + 2 + 4 + ... + n = 2n - 1     → total copies ≈ 2n
For f = 1.5: 1 + 1.5 + 2.25 + ... + n ≈ 3n  → total copies ≈ 3n
For f = 1.25: total copies ≈ 5n              → still O(n)!
```

Any constant factor f > 1 gives amortized O(1). The choice of f trades memory waste
(larger f wastes more) against copy frequency (smaller f copies more often).

### 3. The Banker's Method — Proving Amortized O(1) (10 min)

Imagine every append "charges" 3 coins:
- 1 coin pays for the actual insertion
- 2 coins are "saved" on the element (prepaid for its future copy)

When the array doubles from capacity n to 2n, you must copy n elements. But the last
n/2 elements (those added since the last resize) each saved 2 coins. That is n coins
total — exactly enough to pay for copying n elements.

The accounting always balances. No matter how many appends you do, the 3-coin charge
per append covers all work, including occasional O(n) resizes. This proves the amortized
cost is O(1) (specifically, at most 3 operations per append for doubling).

For growth factor f, the amortized cost per append is f/(f-1):
- f = 2.0: amortized cost = 2 operations per append
- f = 1.5: amortized cost = 3 operations per append
- f = 1.25: amortized cost = 5 operations per append

### 4. How CPython Lists Actually Grow (10 min)

CPython does not use a clean doubling strategy. The growth formula (from
`Objects/listobject.c`) is:

```c
new_allocated = (size_t)newsize + (newsize >> 3) + (newsize < 9 ? 3 : 6);
```

This means: **new capacity = current size + current size/8 + small constant**.

The growth factor is approximately **1.125** (12.5% overallocation), not 2.0. Why?

1. **Memory efficiency.** Doubling wastes up to 50% of allocated memory. A 12.5%
   overshoot wastes at most ~12.5%. For a list with 1 million elements, that is the
   difference between wasting 4MB and 500KB.

2. **Memory allocator friendliness.** Doubling tends to produce sizes that cannot reuse
   previously freed blocks. If you allocate 1MB, free it, then allocate 2MB, the old
   1MB block is stranded. Growth factor < 2 (especially around the golden ratio ~1.618
   or below) allows the allocator to coalesce freed blocks.

3. **The small-list fast path.** The `+3` or `+6` constant ensures tiny lists do not
   resize on every append. A fresh empty list gets capacity 4 on first append.

The actual capacity sequence for CPython:
```
size:     0  1  4  8  16  25  35  46  58  72  88  ...
growth:   -  -  4x 2x 2x  1.56 1.4 1.31 1.26 1.24 1.22 ...
```

It starts aggressive (to avoid frequent resizes for small lists) and converges toward
~1.125x for large lists (to save memory).

### 5. Shrinking — The Forgotten Half (5 min)

Most dynamic array implementations only grow. They never shrink. Python's `list` never
releases memory when you `pop()` elements — a list that once held 1 million elements
keeps its 1-million-slot internal array even when only 3 elements remain.

To reclaim memory, you must explicitly: `my_list = list(my_list)` or use `copy()`.

A production-grade dynamic array should shrink when utilization drops below a threshold
(e.g., 25% full). But you must be careful:
- If you shrink at 50% and grow at 100%, repeated add/remove at the boundary causes
  **thrashing** — constant resizing.
- Safe rule: **grow at 100% full, shrink at 25% full**. This leaves a 2x buffer zone.

---

## Practice (20 min)

Work through `practice.py`. Implement a dynamic array from scratch with:
- Append, insert, delete operations
- Configurable growth strategy
- Shrink-on-underutilization
- Amortized cost measurement

Also run `dynamic_array.py` to see:
- Growth strategies compared head-to-head with benchmarks
- CPython's actual growth pattern exposed
- Array vs linked list performance in practice
- Memory waste analysis for different growth factors

---

## Daily Project

Run `dynamic_array.py` and study the output. The script:
1. Implements a full dynamic array from scratch with configurable growth factor.
2. Benchmarks doubling vs 1.5x vs additive growth on 100K appends.
3. Reveals CPython's internal growth pattern using `sys.getsizeof()`.
4. Compares dynamic array vs linked list for append and iteration.
5. Visualizes memory waste as a fraction of allocated capacity.

Your tasks:
1. Predict which growth strategy will be fastest before running.
2. Explain why CPython chose ~1.125x instead of 2x.
3. Add a shrinking strategy to `DynamicArray` and test it against thrashing patterns.

---

## Checkpoint Questions

1. You append n elements to a dynamic array that doubles on overflow. What is the total
   number of element copies across all resizes? Derive the exact formula using geometric
   series. Why is the amortized cost per append O(1) and not O(log n)?

2. CPython's growth formula adds `newsize >> 3 + 6` to the current size. What is the
   approximate growth factor for a list of 1,000 elements? For 1,000,000? Why does it
   converge rather than stay constant?

3. You have a dynamic array that grows by doubling and shrinks by halving when <50%
   full. Describe a sequence of operations that makes every operation O(n). How would
   you fix this?

4. A dynamic array with growth factor 2 wastes up to 50% memory. A growth factor of
   1.25 wastes up to 20%. But 1.25 copies elements more often. Derive the total number
   of copies for n appends with factor 1.25 vs 2. At what point does the extra copying
   matter more than the memory savings?

5. Connect to Day 15: when a dynamic array resizes, the new allocation is at a different
   memory address. What happens to CPU cache lines that held the old array? Why does
   resizing hurt cache performance beyond just the O(n) copy cost?
