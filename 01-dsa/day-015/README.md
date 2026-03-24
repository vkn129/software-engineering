# Day 15: Memory Layout — Contiguous Storage, Cache Lines, Locality of Reference

## Week 3: Arrays — The Foundation

---

## Why This Exists

Every programmer uses arrays, but few understand *why* arrays are fast. The answer
isn't in the algorithm — it's in the hardware. Modern CPUs don't fetch one byte at a
time from RAM. They fetch entire **cache lines** (typically 64 bytes). When you access
`arr[0]`, the CPU quietly loads `arr[1]` through `arr[15]` (for 4-byte ints) into
the cache for free. This is called **spatial locality**, and it's the reason arrays
dominate data structures in practice even when linked lists have better theoretical
complexity for some operations.

In the 1960s, when John Backus designed Fortran, arrays were stored in column-major
order. When Dennis Ritchie designed C, he chose row-major order. This seemingly minor
decision still affects performance today — traversing a 2D array in the wrong order
can be 5-10x slower because of cache misses.

Understanding memory layout isn't academic trivia. It's the difference between code
that runs in 100ms and code that runs in 1 second on identical hardware.

---

## Theory (40 min)

### 1. What "Contiguous" Actually Means (10 min)

An array stores elements in a single, unbroken block of memory. If element 0 lives at
address `0x1000` and each element is 8 bytes, then:
- Element 0: `0x1000`
- Element 1: `0x1008`
- Element 2: `0x1010`
- Element n: `0x1000 + n * 8`

This formula — `base + index * element_size` — is why array access is O(1). No
pointer chasing, no searching. Just arithmetic.

**Python's reality check:** Python `list` is NOT a contiguous array of values. It's a
contiguous array of *pointers* (8 bytes each on 64-bit), where each pointer references
a Python object scattered across the heap. The `array` module and `ctypes` give you
true contiguous storage.

### 2. The Memory Hierarchy (10 min)

```
Register:  ~0.5 ns    |  Few KB
L1 Cache:  ~1 ns      |  32-64 KB
L2 Cache:  ~4 ns      |  256 KB - 1 MB
L3 Cache:  ~10 ns     |  2-32 MB
RAM:       ~100 ns    |  GBs
SSD:       ~100,000 ns|  TBs
```

Each level is roughly 10x slower than the one above. The CPU cache is the key:
- **Cache line**: 64 bytes on most modern CPUs
- **Cache hit**: data already in cache (~1-10 ns)
- **Cache miss**: must fetch from RAM (~100 ns) — 100x penalty

### 3. Spatial vs Temporal Locality (10 min)

**Spatial locality**: If you access memory address X, you'll probably access X+1 soon.
Arrays exploit this perfectly — sequential access means every cache line fetch gives
you ~16 useful integers (64 bytes / 4 bytes per int).

**Temporal locality**: If you accessed address X recently, you'll probably access it
again. Loop variables, accumulators, and frequently-read config values exploit this.

**Why linked lists lose**: Each node can be anywhere in memory. Following a pointer to
the next node almost always causes a cache miss. Even though both arrays and linked
lists are O(n) for traversal, arrays can be 10-100x faster in practice.

### 4. Row-Major vs Column-Major (10 min)

A 2D array is stored in 1D memory. The question is: which dimension is contiguous?

**Row-major (C, Python, Java):** Elements in the same row are adjacent.
```
matrix[0][0], matrix[0][1], matrix[0][2], matrix[1][0], matrix[1][1], ...
```
Traversing row-by-row = cache-friendly. Traversing column-by-column = cache miss on
every access.

**Column-major (Fortran, MATLAB, Julia):** Elements in the same column are adjacent.
```
matrix[0][0], matrix[1][0], matrix[2][0], matrix[0][1], matrix[1][1], ...
```
The opposite access pattern is fast.

This matters in numerical computing. Matrix multiplication implemented wrong can be
5-10x slower purely from cache effects.

---

## Practice (20 min)

1. Run `memory_layout.py` and observe the memory address differences between Python
   list elements vs `array` module elements vs `ctypes` arrays.

2. Run `cache_performance.py` and measure the speed difference between:
   - Sequential array access vs random access
   - Row-major vs column-major 2D array traversal

3. Open `practice_memory.py` and complete the TODO exercises.

---

## Daily Project

Implement a `MemoryProfiler` class that:
- Takes any sequence (list, array, ctypes array)
- Reports: element size, total memory, address stride
- Measures sequential vs random access time
- Prints a visual "memory map" showing where elements live

See `project_memory_profiler.py`.

---

## Checkpoint Questions

1. **Why is `arr[5]` O(1) but `linked_list.get(5)` O(n)?** Explain in terms of
   address arithmetic vs pointer chasing.

2. **A cache line is 64 bytes. You have an array of 8-byte doubles. How many elements
   fit in one cache line?** What happens when you access the first one?

3. **You're summing all elements of a 1000x1000 matrix. You write `for col in range(1000):
   for row in range(1000): total += matrix[row][col]`. Why is this slow in Python/C?**
   How would you fix it?

4. **Python's `list` stores pointers, not values. Does sequential list traversal still
   benefit from spatial locality?** (Hint: think about which level of indirection is
   contiguous.)

5. **If L1 cache is 32 KB and your array is 64 KB, what happens when you traverse it
   twice?** Compare this with an array that's 16 KB.
