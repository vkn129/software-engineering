"""
Day 15: Memory Layout — Contiguous Storage Demonstration

This script shows the fundamental difference between how Python lists,
the array module, and ctypes arrays store data in memory.

WHY THIS MATTERS:
Python lists store POINTERS to objects, not the objects themselves.
This means list elements can be scattered across the heap.
True arrays (array module, ctypes) store VALUES contiguously,
which is what gives arrays their cache-friendly performance.

Run: python memory_layout.py
"""

import array
import ctypes
import sys


def show_python_list_layout():
    """
    Python list internals: a contiguous array of PyObject* pointers.
    The pointers are contiguous, but the objects they point to are NOT.
    """
    print("=" * 70)
    print("1. PYTHON LIST — Array of Pointers")
    print("=" * 70)

    nums = [10, 20, 30, 40, 50]

    print(f"\nList object address: {id(nums):#x}")
    print(f"List object size:    {sys.getsizeof(nums)} bytes")
    print(f"  (includes: PyObject header + array of {len(nums)} pointers)")
    print(f"  (pointer size on this system: {ctypes.sizeof(ctypes.c_void_p)} bytes)")
    print()

    # Show where each INTEGER OBJECT actually lives in memory
    print("Element addresses (where the actual int objects live):")
    print("-" * 50)
    prev_addr = None
    for i, val in enumerate(nums):
        addr = id(val)
        stride = f"  (delta: {addr - prev_addr:+d} bytes)" if prev_addr else ""
        print(f"  nums[{i}] = {val:3d}  →  object at {addr:#x}{stride}")
        prev_addr = addr

    print()
    print("KEY INSIGHT: The int objects are NOT necessarily adjacent.")
    print("Small ints (-5 to 256) are cached by CPython, so they may")
    print("appear close together. Larger objects will be scattered.\n")

    # Now show with larger, non-cached integers
    big_nums = [10000 + i * 7 for i in range(5)]
    print("With non-cached integers (>256):")
    print("-" * 50)
    prev_addr = None
    for i, val in enumerate(big_nums):
        addr = id(val)
        stride = f"  (delta: {addr - prev_addr:+d} bytes)" if prev_addr else ""
        print(f"  big[{i}] = {val}  →  object at {addr:#x}{stride}")
        prev_addr = addr

    print()
    print("These addresses may jump around — objects are heap-allocated.\n")


def show_array_module_layout():
    """
    The array module stores raw C-type values contiguously.
    No Python objects, no pointers — just values packed together.
    """
    print("=" * 70)
    print("2. ARRAY MODULE — Contiguous Values")
    print("=" * 70)

    # 'i' = signed int (typically 4 bytes), 'l' = signed long
    arr = array.array('i', [10, 20, 30, 40, 50])

    print(f"\nArray object address: {id(arr):#x}")
    print(f"Array object size:    {sys.getsizeof(arr)} bytes")
    print(f"Type code: '{arr.typecode}' (signed int)")
    print(f"Item size: {arr.itemsize} bytes per element")
    print(f"Length:    {len(arr)} elements")
    print(f"Data size: {arr.itemsize * len(arr)} bytes (pure data)")
    print()

    # Get the buffer address
    buf_addr, buf_len = arr.buffer_info()
    print(f"Buffer address: {buf_addr:#x}")
    print(f"Buffer length:  {buf_len} elements")
    print()

    print("Calculated element addresses (base + index * itemsize):")
    print("-" * 50)
    for i in range(len(arr)):
        addr = buf_addr + i * arr.itemsize
        print(f"  arr[{i}] = {arr[i]:3d}  →  stored at {addr:#x}  "
              f"(base + {i} * {arr.itemsize} = base + {i * arr.itemsize})")

    print()
    print("KEY INSIGHT: Elements are exactly itemsize bytes apart.")
    print("This is TRUE contiguous storage — cache-line friendly.\n")


def show_ctypes_array_layout():
    """
    ctypes arrays: the closest Python gets to raw C arrays.
    Completely contiguous, fixed-type, fixed-size.
    """
    print("=" * 70)
    print("3. CTYPES ARRAY — Raw C-Style Array")
    print("=" * 70)

    # Create a C-style array of 5 ints
    CIntArray5 = ctypes.c_int * 5
    carr = CIntArray5(10, 20, 30, 40, 50)

    print(f"\nArray type: {type(carr)}")
    print(f"Element type: c_int ({ctypes.sizeof(ctypes.c_int)} bytes)")
    print(f"Total size: {ctypes.sizeof(carr)} bytes")
    print()

    print("Element addresses:")
    print("-" * 50)
    base = ctypes.addressof(carr)
    elem_size = ctypes.sizeof(ctypes.c_int)
    for i in range(5):
        addr = base + i * elem_size
        print(f"  carr[{i}] = {carr[i]:3d}  →  address {addr:#x}  "
              f"(base + {i * elem_size})")

    print()
    print("KEY INSIGHT: Identical to C memory layout. No Python overhead.")
    print("This is what numpy arrays look like under the hood.\n")


def compare_memory_overhead():
    """
    Compare memory usage for the same data across all three approaches.
    """
    print("=" * 70)
    print("4. MEMORY OVERHEAD COMPARISON")
    print("=" * 70)

    n = 1000
    data = list(range(n))

    # Python list
    py_list = list(data)
    list_size = sys.getsizeof(py_list)  # Just the list object (pointers)
    # Each int object also takes memory
    obj_size = sys.getsizeof(0)  # Size of a single int object
    list_total = list_size + n * obj_size  # Approximate

    # array module
    arr = array.array('i', data)
    arr_size = sys.getsizeof(arr)

    # ctypes
    CArr = ctypes.c_int * n
    c_arr = CArr(*data)
    c_size = ctypes.sizeof(c_arr)

    # Pure data (what you'd use in C)
    raw_data = n * ctypes.sizeof(ctypes.c_int)

    print(f"\nStoring {n} integers:")
    print("-" * 50)
    print(f"  Pure data (C equivalent):  {raw_data:>8,} bytes")
    print(f"  ctypes array:              {c_size:>8,} bytes  "
          f"({c_size / raw_data:.1f}x)")
    print(f"  array.array('i'):          {arr_size:>8,} bytes  "
          f"({arr_size / raw_data:.1f}x)")
    print(f"  Python list (total est.):  {list_total:>8,} bytes  "
          f"({list_total / raw_data:.1f}x)")
    print()
    print(f"  Python list breakdown:")
    print(f"    List object (pointers): {list_size:>6,} bytes")
    print(f"    Int objects ({n} x {obj_size}B): {n * obj_size:>6,} bytes")
    print()
    print("KEY INSIGHT: Python lists use ~7-10x more memory than raw arrays.")
    print("This bloat also means fewer elements fit in each cache line.\n")


def demonstrate_address_arithmetic():
    """
    Show how O(1) access works: it's just address arithmetic.
    """
    print("=" * 70)
    print("5. WHY ARRAY ACCESS IS O(1) — Address Arithmetic")
    print("=" * 70)

    arr = array.array('d', [1.1, 2.2, 3.3, 4.4, 5.5])  # 'd' = double (8 bytes)
    base_addr, _ = arr.buffer_info()
    elem_size = arr.itemsize

    print(f"\nBase address: {base_addr:#x}")
    print(f"Element size: {elem_size} bytes (double)")
    print()

    # Simulate what the CPU does for arr[3]
    index = 3
    computed_addr = base_addr + index * elem_size
    print(f"To access arr[{index}]:")
    print(f"  address = base + index * size")
    print(f"  address = {base_addr:#x} + {index} * {elem_size}")
    print(f"  address = {base_addr:#x} + {index * elem_size}")
    print(f"  address = {computed_addr:#x}")
    print(f"  value   = {arr[index]}")
    print()
    print("This is ONE multiplication and ONE addition — O(1).")
    print("No loops. No searching. No pointer chasing.")
    print("This is why arrays are the most fundamental data structure.\n")


if __name__ == "__main__":
    show_python_list_layout()
    show_array_module_layout()
    show_ctypes_array_layout()
    compare_memory_overhead()
    demonstrate_address_arithmetic()
