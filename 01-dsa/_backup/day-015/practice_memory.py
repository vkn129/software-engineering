"""
Day 15: Practice — Memory Layout Exercises

Complete the TODO sections to deepen your understanding
of how arrays are stored in memory.

Run: python practice_memory.py
"""

import array
import ctypes
import sys
import time


# ---------------------------------------------------------------------------
# Exercise 1: Calculate memory addresses manually
# ---------------------------------------------------------------------------

def exercise_1():
    """
    Given an array of doubles (8 bytes each) starting at a known base address,
    calculate where each element lives WITHOUT using id() or buffer_info().
    """
    print("Exercise 1: Manual Address Calculation")
    print("-" * 40)

    arr = array.array('d', [1.0, 2.0, 3.0, 4.0, 5.0])
    base_addr, length = arr.buffer_info()
    item_size = arr.itemsize

    print(f"Base address: {base_addr}")
    print(f"Item size: {item_size} bytes")
    print(f"Length: {length}")
    print()

    # TODO: For each index 0-4, calculate the expected address using
    #       the formula: address = base_addr + index * item_size
    #       Then verify it matches what you'd expect.
    #
    # Example for index 0:
    #   expected = base_addr + 0 * item_size
    #   print(f"  arr[0] at {expected:#x}")
    #
    # YOUR CODE HERE:
    pass

    print()


# ---------------------------------------------------------------------------
# Exercise 2: Measure memory overhead
# ---------------------------------------------------------------------------

def exercise_2():
    """
    Calculate the "overhead ratio" for storing N integers in different
    containers. Overhead = actual_bytes / (N * value_size).
    """
    print("Exercise 2: Memory Overhead Ratio")
    print("-" * 40)

    sizes = [10, 100, 1000, 10000]

    for n in sizes:
        # TODO: For each size n, create:
        #   1. A Python list of range(n)
        #   2. An array.array('i', range(n))
        #
        # Calculate:
        #   - raw_data = n * 4  (4 bytes per int in array.array('i'))
        #   - list_total = sys.getsizeof(list) + n * sys.getsizeof(0)
        #   - array_total = sys.getsizeof(array)
        #
        # Print the overhead ratio (total / raw_data) for each
        #
        # YOUR CODE HERE:
        pass

    print()


# ---------------------------------------------------------------------------
# Exercise 3: Verify contiguity
# ---------------------------------------------------------------------------

def exercise_3():
    """
    Prove that array.array elements are contiguous by checking that
    the stride between consecutive elements equals the item size.
    """
    print("Exercise 3: Verify Contiguity")
    print("-" * 40)

    # TODO: Create an array.array of type 'f' (float, 4 bytes) with 10 elements.
    #       Use buffer_info() to get the base address.
    #       Calculate addresses for elements 0 through 9.
    #       Verify that address[i+1] - address[i] == itemsize for all i.
    #       Print "CONTIGUOUS: YES" if all strides match, "NO" otherwise.
    #
    # YOUR CODE HERE:
    pass

    print()


# ---------------------------------------------------------------------------
# Exercise 4: Row-major index calculation
# ---------------------------------------------------------------------------

def exercise_4():
    """
    For a 2D matrix stored in row-major order as a 1D array,
    implement the index calculation: flat_index = row * num_cols + col
    """
    print("Exercise 4: 2D to 1D Index Mapping")
    print("-" * 40)

    rows, cols = 4, 5

    # Store a 4x5 matrix as a flat array
    flat = array.array('i', [0] * (rows * cols))

    # TODO: Fill the flat array so that flat[row * cols + col] = row * 10 + col
    #       This simulates matrix[row][col] = row * 10 + col
    #
    # Then print the matrix in 2D form by reading from the flat array.
    # Expected output:
    #    0  1  2  3  4
    #   10 11 12 13 14
    #   20 21 22 23 24
    #   30 31 32 33 34
    #
    # YOUR CODE HERE:
    pass

    print()


# ---------------------------------------------------------------------------
# Exercise 5: Cache line simulation
# ---------------------------------------------------------------------------

def exercise_5():
    """
    Simulate what a CPU cache does when you access array elements.
    Assume a 64-byte cache line and 4-byte integers.
    """
    print("Exercise 5: Cache Line Simulation")
    print("-" * 40)

    CACHE_LINE_SIZE = 64  # bytes
    ELEM_SIZE = 4         # bytes (int32)
    ELEMS_PER_LINE = CACHE_LINE_SIZE // ELEM_SIZE  # 16 elements

    n = 64  # 64 elements = 4 cache lines worth

    # TODO: Simulate sequential access (indices 0, 1, 2, ..., 63)
    #       Count cache misses. A miss occurs when you access an element
    #       whose cache line hasn't been loaded yet.
    #
    #       Cache line number for index i = i // ELEMS_PER_LINE
    #       A miss occurs the FIRST time you touch a new cache line.
    #
    #       Print: total accesses, cache misses, hit rate
    #
    # Then simulate stride-2 access (indices 0, 2, 4, ..., 62)
    # and stride-16 access (indices 0, 16, 32, 48)
    #
    # YOUR CODE HERE:
    pass

    print()


if __name__ == "__main__":
    print("DAY 15 PRACTICE: Memory Layout Exercises")
    print("=" * 50)
    print("Complete the TODO sections in this file.\n")

    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()

    print("Done! Check your answers against the theory from README.md.")
