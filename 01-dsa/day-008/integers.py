"""
Day 8: Integer Representation -- Two's Complement, Overflow
============================================================

This file demonstrates how integers are ACTUALLY stored in computers.
Python hides the ugly truth (arbitrary precision integers), so we
simulate fixed-width behavior to show what C, Java, Rust, etc. do.

Run: python integers.py
"""


# =============================================================================
# SECTION 1: Binary Representation Basics
# =============================================================================

def int_to_binary_string(n, bits=8):
    """Convert an integer to its binary string representation with fixed width.

    We use Python's bin() and then pad/truncate to show exactly what
    the hardware stores. For negative numbers, we compute the two's
    complement representation manually.
    """
    if n >= 0:
        # Positive: straightforward binary, zero-padded
        return format(n & ((1 << bits) - 1), f'0{bits}b')
    else:
        # Negative: two's complement = flip bits and add 1
        # Shortcut: add 2^bits to the negative number
        twos_comp = (1 << bits) + n
        return format(twos_comp, f'0{bits}b')


print("=" * 65)
print("SECTION 1: Binary Representation")
print("=" * 65)

# Show how decimal maps to binary
examples = [0, 1, 5, 42, 127, 255]
print(f"\n{'Decimal':>10} {'8-bit Binary':>15} {'16-bit Binary':>20}")
print("-" * 50)
for num in examples:
    print(f"{num:>10} {int_to_binary_string(num, 8):>15} {int_to_binary_string(num, 16):>20}")

# Key insight: each position is a power of 2
print("\nWhy 42 = 00101010:")
print("  0*128 + 0*64 + 1*32 + 0*16 + 1*8 + 0*4 + 1*2 + 0*1")
print(f"  = 32 + 8 + 2 = {32 + 8 + 2}")


# =============================================================================
# SECTION 2: Two's Complement -- How Negative Numbers Work
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 2: Two's Complement")
print("=" * 65)

def show_twos_complement(n, bits=8):
    """Show the step-by-step process of two's complement negation."""
    if n == 0:
        print(f"  {n} is zero -- same in all representations")
        return

    positive = abs(n)
    binary_pos = int_to_binary_string(positive, bits)

    # Step 1: Flip all bits (one's complement)
    flipped = ''.join('1' if b == '0' else '0' for b in binary_pos)

    # Step 2: Add 1 (two's complement)
    twos = int_to_binary_string(-positive, bits)

    print(f"  To represent {n} in {bits}-bit two's complement:")
    print(f"    Start with |{n}| = {positive}:     {binary_pos}")
    print(f"    Flip all bits:            {flipped}  (one's complement)")
    print(f"    Add 1:                    {twos}  (two's complement)")

    # Verify: interpreting the two's complement bits
    # MSB has weight -2^(bits-1), rest are positive powers of 2
    msb_weight = -(1 << (bits - 1))
    value = msb_weight * int(twos[0])
    for i, bit in enumerate(twos[1:], 1):
        value += int(bit) * (1 << (bits - 1 - i))
    print(f"    Verify: {twos[0]}*({msb_weight}) + rest = {value}")

# Demonstrate for several values
for num in [-1, -42, -127, -128]:
    show_twos_complement(num)
    print()

# Show the complete 4-bit two's complement number line
print("Complete 4-bit two's complement number line:")
print(f"{'Binary':>8} {'Unsigned':>10} {'Signed (2s comp)':>18}")
print("-" * 40)
for i in range(16):
    binary = format(i, '04b')
    unsigned = i
    # Two's complement: if MSB is 1, subtract 2^4
    signed = i if i < 8 else i - 16
    marker = " <-- same bit pattern, different interpretation!" if i >= 8 and i <= 9 else ""
    print(f"{binary:>8} {unsigned:>10} {signed:>18}{marker}")


# =============================================================================
# SECTION 3: Integer Overflow -- When Numbers Wrap Around
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 3: Integer Overflow (Simulated Fixed-Width)")
print("=" * 65)

def simulate_fixed_width(value, bits=8, signed=True):
    """Simulate what happens in C/Java with fixed-width integers.

    Python integers never overflow, but in C, Java, Rust, etc.,
    integers have fixed widths and WRAP AROUND silently.

    This function shows what the hardware actually does.
    """
    if signed:
        # Signed range: -2^(bits-1) to 2^(bits-1) - 1
        max_val = (1 << (bits - 1)) - 1
        min_val = -(1 << (bits - 1))
        # Wrap into range using modular arithmetic
        range_size = 1 << bits
        result = ((value - min_val) % range_size) + min_val
    else:
        # Unsigned range: 0 to 2^bits - 1
        result = value % (1 << bits)
    return result

# The classic overflow: MAX + 1 wraps to MIN
print("\n--- Signed 8-bit overflow (range: -128 to 127) ---")
for val in [126, 127, 128, 129, 200, 256, -128, -129, -130]:
    result = simulate_fixed_width(val, bits=8, signed=True)
    overflow = " <-- OVERFLOW!" if val != result else ""
    print(f"  Store {val:>5} in int8 -> get {result:>5}  "
          f"[binary: {int_to_binary_string(result, 8)}]{overflow}")

print("\n--- The infamous 32-bit overflow ---")
int32_max = 2_147_483_647  # 2^31 - 1
print(f"  INT32_MAX     = {int32_max:>15,}")
print(f"  INT32_MAX + 1 = {simulate_fixed_width(int32_max + 1, 32, True):>15,}  <-- wraps to negative!")
print(f"  INT32_MAX + 2 = {simulate_fixed_width(int32_max + 2, 32, True):>15,}")

# Real-world example: YouTube's Gangnam Style view counter
print("\n--- Real-World Overflow Stories ---")
print("  YouTube used a 32-bit counter for video views.")
print(f"  Max views possible: {int32_max:,}")
print("  Gangnam Style exceeded this in Dec 2014.")
print("  YouTube had to upgrade to 64-bit integers.")
print(f"  New max: {2**63 - 1:,}")

# Demonstrate why overflow is dangerous in loops
print("\n--- Overflow in Loops (C behavior simulated) ---")
print("  In C: for (int8_t i = 0; i < 200; i++) loops FOREVER")
print("  because i goes 0, 1, 2, ..., 127, -128, -127, ..., -1, 0, 1, ...")
print("  Simulating first 135 iterations:")
i = 0
iterations = 0
visited = []
for _ in range(135):
    visited.append(i)
    i = simulate_fixed_width(i + 1, bits=8, signed=True)
    iterations += 1
print(f"  Values around the wrap: ...{visited[125:135]}")
print(f"  After {iterations} iterations, i = {i} (not 135!)")


# =============================================================================
# SECTION 4: Python's Arbitrary Precision -- The Safety Net
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 4: Python's Arbitrary Precision Integers")
print("=" * 65)

# Python integers grow as large as memory allows
import sys

big = 2 ** 100
print(f"\n  2^100 = {big}")
print(f"  Number of digits: {len(str(big))}")
print(f"  Bytes to store this: {sys.getsizeof(big)}")

huge = 2 ** 1000
print(f"\n  2^1000 has {len(str(huge))} digits")
print(f"  Bytes to store: {sys.getsizeof(huge)}")
print(f"  First 50 digits: {str(huge)[:50]}...")

# Python does NOT overflow, but this is UNUSUAL among languages
print("\n  Key takeaway: Python protects you from overflow.")
print("  C, C++, Java, Rust, Go do NOT. If you ever use those")
print("  languages, overflow bugs WILL bite you.")

# But even Python uses fixed-width integers internally for NumPy
print("\n  WARNING: NumPy arrays in Python DO overflow!")
print("  import numpy as np")
print("  np.int32(2147483647) + np.int32(1)  # Returns -2147483648")


# =============================================================================
# SECTION 5: Bitwise Representation Helper
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 5: Number Inspector")
print("=" * 65)

def inspect_integer(n, bits=32):
    """Complete analysis of how an integer is stored."""
    print(f"\n  Inspecting: {n}")
    print(f"  Decimal: {n}")
    print(f"  Binary ({bits}-bit): {int_to_binary_string(n, bits)}")
    print(f"  Hexadecimal: {hex(n & ((1 << bits) - 1))}")
    print(f"  Octal: {oct(n & ((1 << bits) - 1))}")

    # Show if it fits in various widths
    for width in [8, 16, 32, 64]:
        if -(1 << (width - 1)) <= n <= (1 << (width - 1)) - 1:
            print(f"  Fits in {width}-bit signed: YES")
        else:
            wrapped = simulate_fixed_width(n, width, True)
            print(f"  Fits in {width}-bit signed: NO (would become {wrapped})")

inspect_integer(42)
inspect_integer(-42)
inspect_integer(1_000_000_000)
inspect_integer(3_000_000_000)  # Overflows 32-bit signed

print("\n" + "=" * 65)
print("Done! Read the comments, then move to floating_point.py")
print("=" * 65)
