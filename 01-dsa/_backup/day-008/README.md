# Day 8: Integer Representation -- Two's Complement, Overflow, and Why Floating Point Lies

## Why This Exists

Every number you type into a program is a lie -- or at least, a carefully negotiated
approximation. When you write `x = 42`, the CPU does not see "forty-two." It sees a
pattern of voltages across 64 tiny transistor gates. When you write `x = 0.1`, the CPU
cannot represent that number *at all* -- it stores the closest value it can, which is
0.1000000000000000055511151231257827021181583404541015625. Understanding how numbers
are actually represented is not academic trivia; it is the difference between code that
works and code that silently produces wrong answers.

The Ariane 5 rocket exploded 37 seconds after launch on June 4, 1996, because a 64-bit
floating point number was converted to a 16-bit signed integer and overflowed. The
Patriot missile defense system failed to intercept a Scud missile in 1991 because of
a floating-point rounding error that accumulated over 100 hours of operation, resulting
in 28 deaths. The Vancouver Stock Exchange lost 25% of its index value over 22 months
because of truncation errors in price calculations.

These are not edge cases. They are the inevitable consequence of mapping infinite
mathematical numbers onto finite physical hardware. This day teaches you the actual
rules your computer follows, so you can predict when it will betray you.

## Theory (40 min)

### 1. Binary Representation Basics

Computers use binary (base 2) because transistors have two states: on and off.
A single binary digit (bit) stores 0 or 1. With N bits, you can represent 2^N
distinct values.

- 8 bits (1 byte): 256 values (0 to 255 unsigned)
- 16 bits: 65,536 values
- 32 bits: ~4.3 billion values
- 64 bits: ~18.4 quintillion values

**Positional notation**: Just as decimal 347 means 3*100 + 4*10 + 7*1,
binary 1011 means 1*8 + 0*4 + 1*2 + 1*1 = 11.

### 2. Unsigned Integers

The simplest representation. N bits represent values 0 through 2^N - 1.
Every bit is a power of 2. No negative numbers possible.

### 3. Signed Integers: The Problem

We need to represent negative numbers. Three historical approaches:

**Sign-magnitude**: Use the leftmost bit as a sign flag (0 = positive, 1 = negative).
Problem: Two representations of zero (+0 and -0), and addition hardware becomes complex.

**One's complement**: Negate by flipping all bits. Problem: Still two zeros, and
arithmetic requires an "end-around carry."

**Two's complement** (the winner): Negate by flipping all bits and adding 1.
One zero, simple addition, and the hardware for addition is identical for signed
and unsigned numbers.

### 4. Two's Complement In Depth

For N bits, the range is -2^(N-1) to 2^(N-1) - 1.

- 8-bit: -128 to 127
- 32-bit: -2,147,483,648 to 2,147,483,647
- 64-bit: -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807

Key insight: The most significant bit has weight -2^(N-1), not +2^(N-1).
For 8-bit: the bit pattern 10000000 = -128 (not +128).

**Why it works**: In two's complement, addition of positive and negative numbers
uses the exact same circuitry as unsigned addition. The CPU does not need separate
"add" and "subtract" hardware -- subtraction is just "negate and add."

### 5. Integer Overflow

What happens when a calculation exceeds the representable range?

In C/C++/Java: The bits wrap around silently. MAX_INT + 1 = MIN_INT.
In Python: Integers have arbitrary precision -- they grow as needed. Python
will never overflow, but the simulation in `integers.py` shows what happens
in languages that do.

### 6. IEEE 754 Floating Point

Real numbers are stored in scientific notation: (-1)^sign * mantissa * 2^exponent.

**32-bit float**: 1 sign bit, 8 exponent bits, 23 mantissa bits
**64-bit double**: 1 sign bit, 11 exponent bits, 52 mantissa bits

**The fundamental problem**: Many decimal fractions (like 0.1) are infinite repeating
fractions in binary, just as 1/3 = 0.333... in decimal. The mantissa gets truncated,
introducing error.

**Special values**: +Infinity, -Infinity, NaN (Not a Number), +0, -0.

### 7. Floating Point Gotchas

- **Comparison**: Never use `==` with floats. Use `abs(a - b) < epsilon`.
- **Accumulation**: Errors compound. Adding 0.1 ten thousand times does not give 1000.0.
- **Associativity**: `(a + b) + c != a + (b + c)` in floating point.
- **Catastrophic cancellation**: Subtracting nearly equal numbers destroys precision.

## Practice (20 min)

Work through the three Python files in order:

1. `integers.py` -- Run it to see two's complement and overflow in action.
   Read every comment. Modify the bit width and observe how ranges change.

2. `floating_point.py` -- Run it to see all the ways floats betray you.
   Try the experiments suggested in comments.

3. `practice.py` -- Fill in the TODO sections to test your understanding.

## Daily Project

Build a "Number Inspector" that takes any number and reports:
- Its binary representation (with two's complement for negatives)
- Whether it can be exactly represented as a float
- The actual float value vs. the intended value
- The accumulated error after N additions

This is implemented in `integers.py` and `floating_point.py`. Run both and study
the output carefully.

## Checkpoint Questions

1. Why does two's complement have one more negative number than positive? (Hint: where
   does zero live in the range?)

2. Why is `0.1 + 0.2 != 0.3` in virtually every programming language, and what does
   this tell you about testing financial software?

3. If you add 0.1 to itself one million times, will the result be greater than, less
   than, or exactly equal to 100,000? Why?

4. A 32-bit signed integer overflows at ~2.1 billion. Why might a social media company
   hit this limit, and what would happen?

5. Why does IEEE 754 have both +0 and -0? Can you think of a situation where the
   distinction matters?
