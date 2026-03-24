"""
Day 4: Array Basics — Contiguous Memory, O(1) Access, and Cache Locality

This script demonstrates the fundamental properties of arrays through
actual measurements. You will SEE that:
- Random access is O(1) regardless of index
- Sequential access is faster than random (cache locality)
- Row-major vs column-major iteration has real performance impact
- Python lists are arrays of pointers (not values like C arrays)

Run: python array_basics.py
"""

import time
import random
import sys
import ctypes


# ---------------------------------------------------------------------------
# Demonstration 1: O(1) random access — index does not matter
# ---------------------------------------------------------------------------

def demonstrate_constant_time_access():
    """Prove that accessing arr[0] takes the same time as arr[999999].

    If arrays used linear search internally (like linked lists), accessing
    later indices would take longer. They don't — because pointer arithmetic
    computes the address in one step.
    """
    print(f"\n{'=' * 65}")
    print("  DEMO 1: O(1) Random Access — Index Does Not Matter")
    print(f"{'=' * 65}")
    print()

    n = 1_000_000
    arr = list(range(n))
    indices_to_test = [0, 100, 10_000, 500_000, 999_999]

    print("  Accessing different indices in a 1,000,000-element array:")
    print(f"  {'Index':>10}  {'Time (ns)':>12}  {'Note':>20}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*20}")

    for idx in indices_to_test:
        # Time many accesses to get measurable results
        iterations = 1_000_000
        start = time.perf_counter()
        for _ in range(iterations):
            _ = arr[idx]
        elapsed = time.perf_counter() - start
        ns_per_access = (elapsed / iterations) * 1e9

        note = ""
        if idx == 0:
            note = "(first element)"
        elif idx == 999_999:
            note = "(last element)"

        print(f"  {idx:>10}  {ns_per_access:>12.1f}  {note:>20}")

    print()
    print("  All indices take ~same time. This IS O(1).")
    print("  address = base + index * element_size  (one multiply, one add)")


# ---------------------------------------------------------------------------
# Demonstration 2: Sequential vs random access (cache locality)
# ---------------------------------------------------------------------------

def demonstrate_cache_locality():
    """Show that iterating sequentially is faster than random access.

    Both do the same number of operations. The difference is cache behavior:
    - Sequential: CPU prefetches next cache line, almost all hits
    - Random: each access likely misses cache, must go to RAM
    """
    print(f"\n{'=' * 65}")
    print("  DEMO 2: Sequential vs Random Access (Cache Locality)")
    print(f"{'=' * 65}")
    print()

    n = 500_000
    arr = list(range(n))
    random_indices = list(range(n))
    random.shuffle(random_indices)

    # Sequential access
    start = time.perf_counter()
    total = 0
    for i in range(n):
        total += arr[i]
    seq_time = time.perf_counter() - start

    # Random access (same number of elements, same operations)
    start = time.perf_counter()
    total = 0
    for i in random_indices:
        total += arr[i]
    rand_time = time.perf_counter() - start

    print(f"  Array size: {n:,} elements")
    print(f"  Sequential iteration: {seq_time:.4f}s")
    print(f"  Random iteration:     {rand_time:.4f}s")
    print(f"  Random / Sequential:  {rand_time / seq_time:.2f}x slower")
    print()
    print("  Same array. Same elements. Same number of accesses.")
    print("  The ONLY difference is memory access pattern.")
    print("  Sequential wins because of CPU cache line prefetching.")
    print()
    print("  Physics: RAM latency ~100ns, L1 cache ~1ns.")
    print("  A cache miss costs 100x more than a cache hit.")


# ---------------------------------------------------------------------------
# Demonstration 3: Row-major vs column-major 2D iteration
# ---------------------------------------------------------------------------

def demonstrate_2d_iteration_order():
    """Show that iterating a 2D array in the wrong order is slow.

    Python lists-of-lists are not true 2D arrays (each row is a separate
    object), but the effect is still visible. With NumPy, the effect is
    dramatic because NumPy uses true contiguous memory.
    """
    print(f"\n{'=' * 65}")
    print("  DEMO 3: Row-Major vs Column-Major 2D Iteration")
    print(f"{'=' * 65}")
    print()

    rows, cols = 1000, 1000
    matrix = [[random.randint(0, 100) for _ in range(cols)] for _ in range(rows)]

    # Row-major: iterate rows, then columns (matches memory layout)
    start = time.perf_counter()
    total = 0
    for r in range(rows):
        for c in range(cols):
            total += matrix[r][c]
    row_major_time = time.perf_counter() - start

    # Column-major: iterate columns, then rows (fights memory layout)
    start = time.perf_counter()
    total = 0
    for c in range(cols):
        for r in range(rows):
            total += matrix[r][c]
    col_major_time = time.perf_counter() - start

    print(f"  Matrix size: {rows}x{cols}")
    print(f"  Row-major iteration:    {row_major_time:.4f}s")
    print(f"  Column-major iteration: {col_major_time:.4f}s")
    print(f"  Column / Row ratio:     {col_major_time / row_major_time:.2f}x")
    print()
    print("  Same matrix. Same sum. Different iteration order.")
    print("  Row-major matches how Python stores list-of-lists.")
    print("  (Effect is even stronger with NumPy's true contiguous arrays.)")


# ---------------------------------------------------------------------------
# Demonstration 4: Python list memory layout — array of pointers
# ---------------------------------------------------------------------------

def demonstrate_python_list_layout():
    """Show that Python lists store pointers, not values.

    A C array of 4-byte ints uses exactly 4n bytes.
    A Python list of ints uses 8n bytes (for pointers) plus the memory
    for each int object. This is the cost of Python's flexibility.
    """
    print(f"\n{'=' * 65}")
    print("  DEMO 4: Python List Memory Layout")
    print(f"{'=' * 65}")
    print()

    # Show that list elements are references (pointers)
    arr = [10, 20, 30, 40, 50]
    print("  arr = [10, 20, 30, 40, 50]")
    print()
    print("  Python lists store POINTERS to objects, not the values directly.")
    print("  Each pointer is 8 bytes on a 64-bit system.")
    print()
    print(f"  {'Index':>6}  {'id(arr[i])':>20}  {'Value':>8}  {'Size of value object':>22}")
    print(f"  {'-'*6}  {'-'*20}  {'-'*8}  {'-'*22}")

    for i, val in enumerate(arr):
        print(f"  {i:>6}  {id(val):>20}  {val:>8}  {sys.getsizeof(val):>18} bytes")

    print()
    print(f"  Size of the list object itself: {sys.getsizeof(arr)} bytes")
    print(f"  (Header + 5 pointers of 8 bytes each = {56 + 5*8} bytes)")
    print()

    # Show memory overhead at scale
    sizes = [100, 1000, 10_000, 100_000]
    print("  Memory overhead at scale:")
    print(f"  {'n':>10}  {'List size':>12}  {'C array would be':>18}  {'Overhead':>10}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*18}  {'-'*10}")

    for n in sizes:
        arr = list(range(n))
        list_size = sys.getsizeof(arr)
        c_size = n * 4  # 4-byte ints in C
        overhead = list_size / c_size
        print(f"  {n:>10}  {list_size:>10} B  {c_size:>16} B  {overhead:>9.1f}x")

    print()
    print("  Python lists use ~2x the memory of C arrays (pointers are 8 bytes,")
    print("  C ints are 4 bytes). Plus each int is a separate object on the heap.")
    print("  This is the price of dynamic typing and garbage collection.")


# ---------------------------------------------------------------------------
# Demonstration 5: Pointer arithmetic in action
# ---------------------------------------------------------------------------

def demonstrate_pointer_arithmetic():
    """Show the address computation that makes O(1) access possible.

    In C: address = base + index * sizeof(element)
    In Python, we can approximate this using id() and ctypes.
    """
    print(f"\n{'=' * 65}")
    print("  DEMO 5: Pointer Arithmetic — How O(1) Access Works")
    print(f"{'=' * 65}")
    print()

    # Use ctypes to peek at the internal array of pointers
    arr = [100, 200, 300, 400, 500]

    print("  arr = [100, 200, 300, 400, 500]")
    print()
    print("  Python's list stores an internal C array of PyObject* pointers.")
    print("  The address of arr[i] = base_of_internal_array + i * 8")
    print()

    # The internal buffer address can be found via ctypes
    # PyListObject has: ob_refcnt, ob_type, ob_size, **ob_item
    # ob_item is the pointer to the internal array
    list_id = id(arr)

    # On CPython, we can read the ob_item pointer
    # PyListObject layout: refcnt(8) + type(8) + size(8) + ob_item(8) = at offset 24
    # But let's use the simpler id() approach for elements
    print(f"  id(arr) = {list_id} (address of the list object)")
    print()

    print("  Element addresses (id of pointed-to int objects):")
    print(f"  {'Index':>6}  {'id(arr[i])':>20}  {'Value':>8}")
    print(f"  {'-'*6}  {'-'*20}  {'-'*8}")
    for i in range(len(arr)):
        print(f"  {i:>6}  {id(arr[i]):>20}  {arr[i]:>8}")

    print()
    print("  Note: the id() values of the int objects may NOT be contiguous")
    print("  because Python int objects are allocated separately on the heap.")
    print("  What IS contiguous is the array of POINTERS to these objects.")
    print()
    print("  In C, if you had: int arr[] = {100,200,300,400,500};")
    print("  The VALUES would be contiguous: 100 at base+0, 200 at base+4, etc.")
    print("  That is why C arrays have better cache behavior than Python lists.")


# ---------------------------------------------------------------------------
# Demonstration 6: Array operations and their complexities
# ---------------------------------------------------------------------------

def demonstrate_operation_costs():
    """Time common array operations to verify their Big-O complexity.

    Access:     O(1)
    Append:     O(1) amortized (covered in Day 5)
    Insert at 0: O(n) — must shift all elements
    Search:     O(n) for unsorted, O(log n) for sorted
    """
    print(f"\n{'=' * 65}")
    print("  DEMO 6: Array Operation Costs")
    print(f"{'=' * 65}")
    print()

    sizes = [10_000, 20_000, 40_000, 80_000]

    # Insert at beginning (O(n) — must shift everything)
    print("  Insert at index 0 (O(n) — shifts all elements right):")
    print(f"  {'n':>10}  {'Time (ms)':>12}  {'Ratio':>8}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*8}")
    prev_t = None
    for n in sizes:
        arr = list(range(n))
        start = time.perf_counter()
        for _ in range(1000):
            arr.insert(0, -1)
            arr.pop(0)  # undo to keep size stable
        t = time.perf_counter() - start
        ratio = f"{t/prev_t:.2f}x" if prev_t and prev_t > 0 else "--"
        print(f"  {n:>10}  {t*1000:>12.2f}  {ratio:>8}")
        prev_t = t

    print("  Doubling n should ~double time (ratio ~2x). This IS O(n).")

    # Append at end (O(1) amortized)
    print()
    print("  Append at end (O(1) amortized):")
    print(f"  {'n':>10}  {'Time (ms)':>12}  {'Ratio':>8}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*8}")
    prev_t = None
    for n in sizes:
        arr = list(range(n))
        start = time.perf_counter()
        for _ in range(10000):
            arr.append(0)
        t = time.perf_counter() - start
        # Pop to keep things stable for next iteration is unnecessary here
        ratio = f"{t/prev_t:.2f}x" if prev_t and prev_t > 0 else "--"
        print(f"  {n:>10}  {t*1000:>12.2f}  {ratio:>8}")
        prev_t = t

    print("  Doubling n should NOT significantly change time (ratio ~1x).")
    print("  Append does not depend on current array size. We explore this tomorrow.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Day 4: Array Basics — Contiguous Memory in Action")
    print("=" * 65)
    print()
    print("Arrays are the foundation. This script proves WHY through measurement.")
    print("Every claim in the README gets an empirical test.")

    demonstrate_constant_time_access()
    demonstrate_cache_locality()
    demonstrate_2d_iteration_order()
    demonstrate_python_list_layout()
    demonstrate_pointer_arithmetic()
    demonstrate_operation_costs()

    print(f"\n{'=' * 65}")
    print("KEY TAKEAWAYS:")
    print("  1. Array access is O(1) via pointer arithmetic: base + i * size")
    print("  2. Sequential iteration is MUCH faster than random (cache locality)")
    print("  3. Row-major vs column-major order matters for 2D arrays")
    print("  4. Python lists store pointers, not values (more memory, less locality)")
    print("  5. Insert at index 0 is O(n) — all elements must shift")
    print("  6. Append at end is O(1) amortized (Day 5 explains why)")
    print("=" * 65)
