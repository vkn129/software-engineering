# Day 9: Bitwise Operations -- Thinking in Binary

## Why This Exists

Yesterday you learned how integers are represented as bit patterns. Today you learn to *manipulate* those patterns directly. This is not systems-programming trivia -- bitwise operations are how the hardware actually works, and understanding them unlocks performance tricks, compact data representations, and a way of thinking that surfaces everywhere in computer science.

Unix file permissions (rwxr-xr-x) are bit flags. Network subnet masks are AND operations. XOR is the foundation of parity checks, error correction, and cryptographic ciphers. Graphics engines pack RGBA colors into single 32-bit integers and extract channels with masks and shifts. Hash functions use XOR to combine bits. Even something as mundane as "is this number even?" is, at the hardware level, checking a single bit.

The reason these operations are fast is that they map directly to single CPU instructions. No loops, no conditionals -- the ALU (Arithmetic Logic Unit) performs them in one clock cycle on all bits simultaneously. When you write `x & 0xFF`, the CPU does not iterate through 8 bits. It applies the AND gate to all 64 bits in parallel. This is the physics: electricity flows through transistor gates at near-light speed, and all gates operate simultaneously.

Every senior engineer eventually encounters a codebase that uses bit manipulation heavily -- file format parsers, network protocols, embedded systems, database storage engines. If you cannot read bit operations fluently, those codebases are opaque. Today we make them transparent.

## Theory (40 min)

### 1. The Six Fundamental Bitwise Operations

All bitwise operations work on individual bits of an integer, in parallel.

```
AND (&):  1 only if BOTH bits are 1
  1010 & 1100 = 1000

OR (|):   1 if EITHER bit is 1
  1010 | 1100 = 1110

XOR (^):  1 if bits are DIFFERENT
  1010 ^ 1100 = 0110

NOT (~):  Flip every bit (one's complement)
  ~1010 = 0101  (in fixed-width)

Left Shift (<<):  Shift bits left, fill with zeros
  1010 << 1 = 10100  (multiply by 2)

Right Shift (>>): Shift bits right
  1010 >> 1 = 0101   (divide by 2)
```

### 2. Why XOR Is Special

XOR has mathematical properties that make it uniquely useful:

- **Self-inverse**: `a ^ b ^ b = a`. XOR-ing something twice undoes it. This is the basis of XOR encryption and the famous "swap without a temp variable" trick.
- **Commutative and associative**: `a ^ b = b ^ a` and `(a ^ b) ^ c = a ^ (b ^ c)`.
- **Identity element is 0**: `a ^ 0 = a`.
- **Self-cancellation**: `a ^ a = 0`.

These properties mean you can XOR a set of numbers in any order and get the same result. If every number appears twice except one, XOR them all and the pairs cancel, leaving the unique number. This solves "find the missing number" in O(n) time, O(1) space.

### 3. Bit Masks: Setting, Clearing, Toggling, and Checking Bits

A bit mask is an integer used as a pattern to manipulate specific bits of another integer.

```python
# Set bit i (turn it ON)
x = x | (1 << i)

# Clear bit i (turn it OFF)
x = x & ~(1 << i)

# Toggle bit i (flip it)
x = x ^ (1 << i)

# Check if bit i is set
is_set = (x >> i) & 1
```

Why the shift? `1 << i` creates a number with only bit `i` set. This is your surgical tool for operating on individual bits.

### 4. Practical Application: Unix File Permissions

```
rwxr-xr-x = 755 in octal = 111 101 101 in binary

Owner:  rwx = 111 = 7  (read + write + execute)
Group:  r-x = 101 = 5  (read + execute)
Others: r-x = 101 = 5  (read + execute)

To check if owner has write permission:
  permissions & 0o200  (AND with 010 000 000)

To add execute for others:
  permissions | 0o001  (OR with 000 000 001)

To remove write for group:
  permissions & ~0o020  (AND with NOT 000 010 000)
```

This is real -- `chmod` does exactly these bit operations.

### 5. Shifts as Multiplication and Division

Left shift by k positions multiplies by 2^k. Right shift divides by 2^k (with truncation for odd numbers). This is faster than multiplication in some contexts, though modern compilers optimize this automatically.

```python
x << 1  # x * 2
x << 3  # x * 8
x >> 1  # x // 2
x >> 4  # x // 16
```

The physics: shifting is literally moving electrons one position over in a register. It is the cheapest possible operation.

### 6. Brian Kernighan's Algorithm: Counting Set Bits

The naive way to count set bits: check each of 32 (or 64) positions. Kernighan's insight: `n & (n - 1)` clears the *lowest* set bit. So you repeat until n is 0, and the number of iterations equals the number of set bits.

```
n = 1011 0100
n-1 = 1011 0011
n & (n-1) = 1011 0000  (cleared the lowest set bit)

Repeat until zero. Count iterations.
```

This runs in O(k) where k is the number of set bits, not O(bits). For sparse numbers, this is much faster.

### 7. Common Bit Tricks

```python
# Check if n is a power of 2
n > 0 and (n & (n - 1)) == 0

# Get the lowest set bit
lowest = n & (-n)

# Check if n is even
(n & 1) == 0

# Swap two variables without temp
a ^= b; b ^= a; a ^= b

# Turn off the rightmost set bit
n & (n - 1)
```

Each of these exploits the binary structure of integers. They are not clever tricks to memorize -- they are logical consequences of how bits work.

## Practice (20 min)

Work through `practice.py`. Each exercise asks you to implement a bit manipulation function. Use only bitwise operators -- no arithmetic shortcuts. The tests will verify your solutions.

## Daily Project

Run `bitwise_ops.py` to see all the bitwise operations demonstrated with visual bit patterns. The script measures and compares bitwise operations against arithmetic equivalents, shows the Kernighan algorithm step by step, and demonstrates real-world applications including Unix permissions and color channel extraction.

## Checkpoint Questions

1. Why can XOR swap two variables without a temporary, but AND and OR cannot? What mathematical property of XOR makes this possible?

2. Why is `n & (n - 1) == 0` the correct test for powers of 2? Walk through the bit pattern of 8 (1000) and 7 (0111) to explain.

3. In a network, a subnet mask like 255.255.255.0 is ANDed with an IP address. Why AND? What would happen if you used OR instead?

4. If you left-shift a 32-bit signed integer by 31 positions, what happens? Why is this dangerous in C but not in Python?

5. Brian Kernighan's algorithm counts set bits in O(k) where k is the number of set bits. The naive approach is O(b) where b is the total bit width. Under what conditions does Kernighan's algorithm provide no advantage?
