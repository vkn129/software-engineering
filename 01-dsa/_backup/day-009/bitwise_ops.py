"""
Day 9: Bitwise Operations -- Thinking in Binary
=================================================

This file demonstrates every fundamental bitwise operation with visual
bit patterns, real measurements, and practical applications. After
learning how integers are represented (Day 8), we now learn to
manipulate them at the bit level -- the way the hardware actually works.

Run: python bitwise_ops.py
"""

import time


# ---------------------------------------------------------------------------
# Helper: display bits visually
# ---------------------------------------------------------------------------

def bits(n, width=8):
    """Return a string showing the binary representation of n in fixed width.

    For negative numbers, shows two's complement. We mask to the given
    width because Python integers have arbitrary precision -- in hardware,
    you would see exactly these bits in the register.
    """
    if n < 0:
        n = (1 << width) + n
    return format(n & ((1 << width) - 1), f'0{width}b')


def show_op(a, op_symbol, b, result, width=8):
    """Pretty-print a bitwise operation with aligned bit patterns."""
    print(f"  {bits(a, width)}  ({a:>4})  {op_symbol}")
    print(f"  {bits(b, width)}  ({b:>4})")
    print(f"  {'─' * width}")
    print(f"  {bits(result, width)}  ({result:>4})")
    print()


# ===========================================================================
# SECTION 1: The Six Fundamental Operations
# ===========================================================================

print("=" * 65)
print("SECTION 1: The Six Fundamental Bitwise Operations")
print("=" * 65)

a, b = 0b10101010, 0b11001100  # 170, 204

print(f"\n  a = {bits(a)} = {a}")
print(f"  b = {bits(b)} = {b}\n")

# AND: both bits must be 1
print("--- AND (&): 1 only if BOTH bits are 1 ---")
print("  Use case: masking, extracting specific bits\n")
show_op(a, '&', b, a & b)

# OR: either bit can be 1
print("--- OR (|): 1 if EITHER bit is 1 ---")
print("  Use case: setting bits, combining flags\n")
show_op(a, '|', b, a | b)

# XOR: bits must be different
print("--- XOR (^): 1 if bits are DIFFERENT ---")
print("  Use case: toggling, swapping, finding unique elements\n")
show_op(a, '^', b, a ^ b)

# NOT: flip every bit
print("--- NOT (~): Flip every bit ---")
print(f"  ~{bits(a)} = {bits(~a)} (in 8-bit: {(~a) & 0xFF})")
print(f"  Python shows ~{a} = {~a} because Python integers are arbitrary precision")
print(f"  In a fixed 8-bit register, ~{a} = {(~a) & 0xFF}\n")

# Left Shift: multiply by powers of 2
print("--- Left Shift (<<): Shift bits left, fill with zeros ---")
x = 0b00001101  # 13
print(f"  {bits(x)} ({x}) << 1 = {bits(x << 1)} ({x << 1})  [x * 2]")
print(f"  {bits(x)} ({x}) << 2 = {bits(x << 2)} ({x << 2})  [x * 4]")
print(f"  {bits(x)} ({x}) << 3 = {bits(x << 3, 16)} ({x << 3})  [x * 8]\n")

# Right Shift: divide by powers of 2
print("--- Right Shift (>>): Shift bits right ---")
x = 0b11010000  # 208
print(f"  {bits(x)} ({x}) >> 1 = {bits(x >> 1)} ({x >> 1})  [x // 2]")
print(f"  {bits(x)} ({x}) >> 2 = {bits(x >> 2)} ({x >> 2})  [x // 4]")
print(f"  {bits(x)} ({x}) >> 4 = {bits(x >> 4)} ({x >> 4})  [x // 16]\n")


# ===========================================================================
# SECTION 2: Why XOR Is Special
# ===========================================================================

print("=" * 65)
print("SECTION 2: Why XOR Is Special")
print("=" * 65)

# Property 1: Self-inverse (a ^ b ^ b = a)
print("\n--- Self-inverse: a ^ b ^ b = a ---")
secret = 42
key = 0b11110000
encrypted = secret ^ key
decrypted = encrypted ^ key
print(f"  Original:  {bits(secret)} ({secret})")
print(f"  Key:       {bits(key)} ({key})")
print(f"  Encrypted: {bits(encrypted)} ({encrypted})")
print(f"  Decrypted: {bits(decrypted)} ({decrypted})")
print(f"  Original restored: {secret == decrypted}")

# Property 2: Swap without temp variable
print("\n--- Swap without temporary variable ---")
x, y = 25, 77
print(f"  Before: x={x}, y={y}")
x ^= y   # x now holds x^y
y ^= x   # y now holds y^(x^y) = x
x ^= y   # x now holds (x^y)^x = y
print(f"  After:  x={x}, y={y}")
print("  (Three XOR operations, zero extra memory)")

# Property 3: Find the unique number in a list where every other appears twice
print("\n--- Find the single number (all others appear twice) ---")
numbers = [4, 1, 2, 1, 2, 7, 4]
print(f"  Input: {numbers}")
result = 0
for n in numbers:
    result ^= n
print(f"  XOR of all: {result}")
print(f"  The unique number is {result}")
print("  Why: every pair cancels (x ^ x = 0), leaving only the unique one")


# ===========================================================================
# SECTION 3: Bit Masks -- Surgical Bit Manipulation
# ===========================================================================

print("\n" + "=" * 65)
print("SECTION 3: Bit Masks -- Set, Clear, Toggle, Check")
print("=" * 65)

x = 0b10100101  # 165
print(f"\n  Starting value: {bits(x)} ({x})")

# Set bit 3 (turn it ON)
bit_pos = 3
mask = 1 << bit_pos
result = x | mask
print(f"\n  Set bit {bit_pos}:")
print(f"    {bits(x)} | {bits(mask)} = {bits(result)}")
print(f"    {x} | {mask} = {result}")

# Clear bit 5 (turn it OFF)
bit_pos = 5
mask = 1 << bit_pos
result = x & ~mask
print(f"\n  Clear bit {bit_pos}:")
print(f"    {bits(x)} & ~{bits(mask)} = {bits(x)} & {bits(~mask)} = {bits(result)}")
print(f"    Bit {bit_pos} is now OFF: {result}")

# Toggle bit 0 (flip it)
bit_pos = 0
mask = 1 << bit_pos
result = x ^ mask
print(f"\n  Toggle bit {bit_pos}:")
print(f"    {bits(x)} ^ {bits(mask)} = {bits(result)}")
print(f"    Bit {bit_pos} flipped: was {(x >> bit_pos) & 1}, now {(result >> bit_pos) & 1}")

# Check if bit 7 is set
bit_pos = 7
is_set = (x >> bit_pos) & 1
print(f"\n  Check bit {bit_pos}:")
print(f"    ({bits(x)} >> {bit_pos}) & 1 = {is_set}")
print(f"    Bit {bit_pos} is {'SET' if is_set else 'NOT SET'}")


# ===========================================================================
# SECTION 4: Practical Application -- Unix File Permissions
# ===========================================================================

print("\n" + "=" * 65)
print("SECTION 4: Unix File Permissions (Real Bit Flags)")
print("=" * 65)

# Unix permission bits: rwxrwxrwx (owner, group, others)
# Each group of 3 bits: read (4), write (2), execute (1)

READ    = 0o4  # 100 in binary
WRITE   = 0o2  # 010 in binary
EXECUTE = 0o1  # 001 in binary

def perm_string(perm):
    """Convert a 3-bit permission to rwx string."""
    r = 'r' if perm & READ else '-'
    w = 'w' if perm & WRITE else '-'
    x = 'x' if perm & EXECUTE else '-'
    return r + w + x

def full_perm_string(mode):
    """Convert 9-bit permission mode to full string like rwxr-xr-x."""
    owner = (mode >> 6) & 0o7
    group = (mode >> 3) & 0o7
    others = mode & 0o7
    return perm_string(owner) + perm_string(group) + perm_string(others)

# Demonstrate common permission modes
modes = [0o755, 0o644, 0o700, 0o777, 0o600, 0o444]
print(f"\n  {'Octal':>8} {'Binary':>12} {'String':>12} {'Description'}")
print("  " + "-" * 55)
descriptions = {
    0o755: "Standard executable/directory",
    0o644: "Standard file (owner writes)",
    0o700: "Owner only, full access",
    0o777: "Everyone, full access (dangerous!)",
    0o600: "Owner read/write only (e.g., SSH keys)",
    0o444: "Read-only for everyone",
}
for mode in modes:
    binary = format(mode, '09b')
    print(f"  {oct(mode):>8} {binary:>12} {full_perm_string(mode):>12} {descriptions[mode]}")

# Show bit operations for modifying permissions
print("\n  --- Modifying permissions with bit operations ---")
current = 0o644
print(f"\n  Current: {oct(current)} = {full_perm_string(current)}")

# Add execute for owner
new = current | (EXECUTE << 6)
print(f"  Add owner execute:  {oct(new)} = {full_perm_string(new)}")

# Remove write for owner
new2 = current & ~(WRITE << 6)
print(f"  Remove owner write: {oct(new2)} = {full_perm_string(new2)}")

# Add write for group
new3 = current | (WRITE << 3)
print(f"  Add group write:    {oct(new3)} = {full_perm_string(new3)}")


# ===========================================================================
# SECTION 5: Brian Kernighan's Algorithm -- Counting Set Bits
# ===========================================================================

print("\n" + "=" * 65)
print("SECTION 5: Brian Kernighan's Algorithm (Count Set Bits)")
print("=" * 65)

def count_bits_naive(n):
    """Count set bits by checking each position. O(total_bits)."""
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count

def count_bits_kernighan(n):
    """Brian Kernighan's trick: n & (n-1) clears the lowest set bit.
    Only iterates k times where k = number of set bits.
    O(set_bits), not O(total_bits)."""
    count = 0
    while n:
        n &= (n - 1)  # Clear lowest set bit
        count += 1
    return count

def count_bits_kernighan_verbose(n):
    """Same algorithm but shows each step."""
    original = n
    count = 0
    print(f"\n  Counting set bits in {n} ({bits(n, 16)}):")
    while n:
        prev = n
        n &= (n - 1)
        count += 1
        print(f"    Step {count}: {bits(prev, 16)} & {bits(prev - 1, 16)} = {bits(n, 16)}"
              f"  (cleared lowest set bit)")
    print(f"  Result: {count} set bits")
    return count

# Step-by-step demonstration
count_bits_kernighan_verbose(0b1011_0100_1010_0011)

# Why n & (n-1) works: subtracting 1 flips the lowest set bit and all
# bits below it. ANDing with the original clears that lowest set bit.
print("\n  Why n & (n-1) works:")
print("    n     = ...1000  (lowest set bit is at position 3)")
print("    n-1   = ...0111  (borrow flips bit 3 and all below)")
print("    n&n-1 = ...0000  (bit 3 is cleared)")

# Performance comparison
print("\n  --- Performance: Naive vs. Kernighan ---")
test_numbers = [0b1, 0b11111111, 0b10000000_00000000, 0xFF_FF_FF_FF]
for num in test_numbers:
    naive = count_bits_naive(num)
    kern = count_bits_kernighan(num)
    assert naive == kern
    print(f"  {num:>12} ({bits(num, 32)}): {naive} set bits")


# ===========================================================================
# SECTION 6: Common Bit Tricks
# ===========================================================================

print("\n" + "=" * 65)
print("SECTION 6: Common Bit Tricks")
print("=" * 65)

# Power of 2 check
print("\n--- Is power of 2? (n > 0 and n & (n-1) == 0) ---")
for n in [1, 2, 3, 4, 7, 8, 16, 15, 64, 100]:
    is_pow2 = n > 0 and (n & (n - 1)) == 0
    print(f"  {n:>4} ({bits(n)}): {'YES' if is_pow2 else 'no'}")

print("\n  Why: powers of 2 have exactly ONE set bit. n-1 flips that bit")
print("  and sets all lower bits. AND gives zero only for powers of 2.")

# Get lowest set bit
print("\n--- Lowest set bit: n & (-n) ---")
for n in [12, 10, 8, 7, 6]:
    lowest = n & (-n)
    print(f"  {n:>4} ({bits(n)}): lowest set bit = {lowest} ({bits(lowest)})")

print("\n  Why: -n is two's complement (flip bits + 1). The lowest set bit")
print("  and all zeros below it survive; everything above gets flipped.")

# Even/odd check
print("\n--- Even/Odd check: n & 1 ---")
for n in range(8):
    parity = "odd" if n & 1 else "even"
    print(f"  {n}: {bits(n)} -> {parity}")

print("\n  Why: the least significant bit IS the ones place.")
print("  If it is 1, the number is odd. Period.")


# ===========================================================================
# SECTION 7: Color Channel Extraction (Real-World Bit Packing)
# ===========================================================================

print("\n" + "=" * 65)
print("SECTION 7: RGBA Color Packing (32-bit Integer)")
print("=" * 65)

# Colors in graphics are often packed as 0xAARRGGBB or 0xRRGGBBAA
# Each channel is 8 bits (0-255)

def pack_rgba(r, g, b, a=255):
    """Pack RGBA into a single 32-bit integer."""
    return (r << 24) | (g << 16) | (b << 8) | a

def unpack_rgba(color):
    """Extract RGBA channels from a packed 32-bit integer."""
    r = (color >> 24) & 0xFF
    g = (color >> 16) & 0xFF
    b = (color >>  8) & 0xFF
    a =  color        & 0xFF
    return r, g, b, a

# Pack and unpack
colors = {
    "Red":     (255,   0,   0, 255),
    "Green":   (  0, 255,   0, 255),
    "Blue":    (  0,   0, 255, 255),
    "White":   (255, 255, 255, 255),
    "50% Red": (255,   0,   0, 128),
}

print(f"\n  {'Color':>10} {'R':>4} {'G':>4} {'B':>4} {'A':>4}   {'Packed (hex)':>14}   Unpacked")
print("  " + "-" * 60)
for name, (r, g, b, a) in colors.items():
    packed = pack_rgba(r, g, b, a)
    unpacked = unpack_rgba(packed)
    print(f"  {name:>10} {r:>4} {g:>4} {b:>4} {a:>4}   0x{packed:08X}   {unpacked}")

print("\n  This is exactly how GPUs and image formats store pixel data.")
print("  Each shift+mask extracts one 8-bit channel from the 32-bit word.")


# ===========================================================================
# SECTION 8: Performance -- Bitwise vs. Arithmetic
# ===========================================================================

print("\n" + "=" * 65)
print("SECTION 8: Bitwise vs. Arithmetic Performance")
print("=" * 65)

# Modern CPUs and Python's overhead make the difference small in Python,
# but the principle matters in C/assembly.

N = 1_000_000

# Multiply by 2: arithmetic vs shift
start = time.perf_counter()
for i in range(N):
    _ = i * 2
t_mul = time.perf_counter() - start

start = time.perf_counter()
for i in range(N):
    _ = i << 1
t_shift = time.perf_counter() - start

print(f"\n  Multiply by 2 ({N:,} operations):")
print(f"    i * 2:  {t_mul:.4f}s")
print(f"    i << 1: {t_shift:.4f}s")
print(f"    Note: In Python, the difference is negligible due to interpreter overhead.")
print(f"    In C/assembly, the shift is a single instruction. The compiler")
print(f"    optimizes x*2 to a shift anyway -- but understanding WHY matters.")

# Even check: modulo vs bitwise
start = time.perf_counter()
for i in range(N):
    _ = i % 2 == 0
t_mod = time.perf_counter() - start

start = time.perf_counter()
for i in range(N):
    _ = (i & 1) == 0
t_and = time.perf_counter() - start

print(f"\n  Even check ({N:,} operations):")
print(f"    i % 2 == 0:   {t_mod:.4f}s")
print(f"    (i & 1) == 0: {t_and:.4f}s")


print("\n" + "=" * 65)
print("Done! Study the output, then work through practice.py")
print("=" * 65)
