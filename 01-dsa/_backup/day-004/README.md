# Day 4: Arrays — Contiguous Memory and O(1) Access

## Why This Exists

The array is the most important data structure in computing. Not the fanciest, not the most flexible — the most important. Every other data structure is either built on top of arrays (hash tables, heaps, dynamic arrays) or exists specifically because arrays have a particular weakness (linked lists, trees). If you do not understand arrays at the memory level, you cannot understand anything that comes after.

An array is a contiguous block of memory where elements sit next to each other with no gaps. This single property — contiguity — gives you two things that shape all of computer science:

1. **O(1) random access via pointer arithmetic.** If you know the base address and element size, you can compute the address of any element with one multiplication and one addition. No traversal. No searching. One step. This is what makes binary search possible, what makes hash tables fast, what makes indexing into a database page instant.

2. **Cache locality.** Modern CPUs do not fetch one byte at a time from RAM. They fetch cache lines — 64 bytes at a time on x86. When your data is contiguous, accessing element i almost always pre-loads elements i+1 through i+15 (for 4-byte ints) into L1 cache. This is not a minor optimization. Iterating a contiguous array can be 10-100x faster than chasing pointers through a linked list, because RAM latency is ~100 nanoseconds while L1 cache is ~1 nanosecond. The gap between "in cache" and "in RAM" is the gap between San Francisco and the Moon.

In 2009, Linus Torvalds called linked lists "fundamentally horrible" for most workloads and said arrays should be the default. He was not being provocative — he was being accurate about hardware.

## Theory (40 min)

### Memory Layout

RAM is a flat array of bytes, addressed from 0 to some maximum. When you allocate an array of n integers (4 bytes each), the OS gives you a contiguous block of 4n bytes:

```
Address:  1000  1004  1008  1012  1016  1020  1024  1028
Value:    [ 42 ][ 17 ][ 93 ][ 8  ][ 55 ][ 31 ][ 72 ][ 60 ]
Index:      0      1     2     3     4     5     6     7
```

### Pointer Arithmetic: Why O(1) Access Works

To find element at index i:
```
address(arr[i]) = base_address + i * element_size
```

This is one multiplication and one addition — two CPU instructions. It does not depend on n. Whether your array has 10 elements or 10 billion, accessing index 5 takes the same time.

```python
# In Python, this is hidden behind the [] operator, but the
# underlying C implementation does exactly this calculation.
arr = [42, 17, 93, 8, 55]
print(arr[3])  # Computes: base + 3 * 8 (Python objects are 8-byte pointers)
```

Compare with a linked list: to access element i, you must follow i pointers. That is O(n) — and each pointer-chase is likely a cache miss.

### Cache Locality: The Hidden Constant

Big-O notation ignores constants, but cache behavior is a "constant" that can be 100x. Consider iterating 1 million integers:

```
Array (contiguous):
  - First access: cache miss, load 64 bytes (16 ints) from RAM
  - Next 15 accesses: cache hits (already loaded!)
  - Total cache misses: ~62,500
  - Time: ~6.25 ms (at 100ns per miss)

Linked list (scattered):
  - Every access: likely cache miss (next node is at random address)
  - Total cache misses: ~1,000,000
  - Time: ~100 ms
```

This 16x difference is the BEST case. In practice, linked list nodes are scattered across memory, causing not just L1 misses but L2 and even L3 misses. The real difference can be 50-100x.

### Static vs Dynamic Arrays

**Static arrays** have a fixed size determined at creation. C's `int arr[100]` allocates exactly 100 integers — no more, no less. If you need 101, you are out of luck (or you allocate a new, larger array and copy).

**Dynamic arrays** (Python's `list`, Java's `ArrayList`, C++'s `vector`) can grow. They manage a static array internally, and when it fills up, they allocate a bigger one and copy everything over. We will study this in detail tomorrow (Day 5).

### Bounds Checking

Accessing index i when i < 0 or i >= n is undefined behavior in C (can read/write random memory, crash, or silently corrupt data). Python raises an IndexError. Java throws ArrayIndexOutOfBoundsException.

```c
// C: no bounds checking — this silently corrupts memory
int arr[5] = {1, 2, 3, 4, 5};
arr[10] = 999;  // writes to memory 20 bytes past the array
                // could overwrite a return address → security exploit
```

This is how buffer overflow attacks work. The 1988 Morris Worm, Code Red, Heartbleed — all exploited the lack of array bounds checking.

### Multi-Dimensional Arrays

A 2D array is just a 1D array with clever indexing. There are two conventions:

**Row-major (C, Python/NumPy default):** rows are stored contiguously.
```
Matrix:  [[1, 2, 3],
          [4, 5, 6]]

Memory:  [1, 2, 3, 4, 5, 6]
Index:    0  1  2  3  4  5

address(m[row][col]) = base + (row * num_cols + col) * element_size
```

**Column-major (Fortran, MATLAB, Julia):** columns are stored contiguously.
```
Memory:  [1, 4, 2, 5, 3, 6]
Index:    0  1  2  3  4  5

address(m[row][col]) = base + (col * num_rows + row) * element_size
```

This matters for performance. If your matrix is row-major and you iterate column-by-column, you get a cache miss on every access. Scientific code has been 10x slower because someone iterated in the wrong order.

```python
# FAST (row-major iteration matches memory layout):
for row in range(n):
    for col in range(n):
        process(matrix[row][col])

# SLOW (column-major iteration causes cache misses):
for col in range(n):
    for row in range(n):
        process(matrix[row][col])
```

## Practice (20 min)

Work through `practice.py`. Implement array operations from scratch: linear search, reverse in-place, rotation, and more. Each exercise builds intuition about how contiguous memory enables (and constrains) what you can do efficiently.

Also run `array_basics.py` to see empirical measurements of array access patterns, cache effects, and the actual difference between sequential and random access.

## Daily Project

Run `array_basics.py` and study the output. The script measures:
1. O(1) random access at different indices (proving it is truly constant).
2. Sequential vs random iteration (demonstrating cache locality effects).
3. Row-major vs column-major iteration on 2D arrays.
4. Memory layout using `id()` and `ctypes` to show actual addresses.

Your tasks:
1. Predict the performance ratios before running.
2. Explain why random access is slower than sequential even though both are "O(n)" per element.
3. Add a measurement that compares iterating a Python list vs a NumPy array (if NumPy is installed).

## Checkpoint Questions

1. Why is array access O(1) but linked list access O(n)? What specific property of memory layout makes the difference?

2. A CPU has a 64-byte cache line. Your array stores 8-byte doubles. How many elements fit in one cache line? If you iterate sequentially, what fraction of accesses are cache misses?

3. You have a 1000x1000 matrix stored in row-major order. You need to sum each column. What is the Big-O complexity? What is the actual performance problem, and how would you fix it?

4. Why does C not check array bounds by default? What is the trade-off that the language designers chose, and why do languages like Python and Java make the opposite choice?

5. An array of n elements uses O(n) space. A linked list of n elements also uses O(n) space. Why does the array typically use LESS total memory? (Hint: think about what a linked list node must store beyond the data.)
