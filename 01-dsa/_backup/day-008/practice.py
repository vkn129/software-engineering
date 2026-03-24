"""
Day 8: Practice -- Integer and Floating Point Exercises
========================================================

Fill in the TODO sections. Run this file to check your answers.
Each function has a docstring explaining what to implement and
test cases that verify correctness.

Run: python practice.py
"""


# =============================================================================
# Exercise 1: Binary Conversion
# =============================================================================

def decimal_to_binary(n, bits=8):
    """Convert a signed integer to its two's complement binary string.

    For positive numbers: standard binary representation, zero-padded.
    For negative numbers: compute two's complement (flip bits + add 1).

    Do NOT use Python's bin() function -- implement the algorithm yourself.

    Examples:
        decimal_to_binary(5, 8)   -> '00000101'
        decimal_to_binary(-1, 8)  -> '11111111'
        decimal_to_binary(-128, 8) -> '10000000'
    """
    # TODO: Implement this function
    # Hint for positive: repeatedly divide by 2 and collect remainders
    # Hint for negative: first get binary of |n|, then flip bits, then add 1
    pass


def binary_to_decimal(binary_str, signed=True):
    """Convert a binary string to its decimal value.

    If signed=True, interpret as two's complement.
    If signed=False, interpret as unsigned.

    Examples:
        binary_to_decimal('11111111', signed=True)  -> -1
        binary_to_decimal('11111111', signed=False) -> 255
        binary_to_decimal('10000000', signed=True)  -> -128
    """
    # TODO: Implement this function
    # Hint for signed: if MSB is 1, the value is negative
    # The MSB contributes -2^(n-1) to the value
    pass


# =============================================================================
# Exercise 2: Overflow Detection
# =============================================================================

def will_overflow_on_add(a, b, bits=32):
    """Determine if adding a + b would overflow in a signed integer of given bit width.

    Returns: (bool, int) -- (whether overflow occurs, the wrapped result)

    Examples:
        will_overflow_on_add(127, 1, 8)     -> (True, -128)
        will_overflow_on_add(100, 20, 8)     -> (True, -136 wrapped to 8-bit)
        will_overflow_on_add(50, 50, 8)      -> (True, ...)
        will_overflow_on_add(10, 20, 8)      -> (False, 30)
    """
    # TODO: Implement this function
    # Hint: compute the true sum, check if it's outside the representable range
    # Range for signed N-bit: -2^(N-1) to 2^(N-1) - 1
    pass


# =============================================================================
# Exercise 3: Float Comparison
# =============================================================================

def safe_float_equal(a, b, epsilon=1e-9):
    """Compare two floats for approximate equality.

    Two floats are "equal" if their absolute difference is less than epsilon.

    Examples:
        safe_float_equal(0.1 + 0.2, 0.3)  -> True
        safe_float_equal(1.0, 1.0 + 1e-10) -> True
        safe_float_equal(1.0, 2.0)          -> False
    """
    # TODO: Implement this function
    pass


# =============================================================================
# Exercise 4: Kahan Summation
# =============================================================================

def kahan_sum(numbers):
    """Implement Kahan compensated summation.

    Regular summation accumulates floating-point errors.
    Kahan summation tracks the error and compensates.

    Algorithm:
        1. Keep a running 'total' and a 'compensation' (initially 0)
        2. For each number:
           a. y = number - compensation
           b. t = total + y
           c. compensation = (t - total) - y
           d. total = t

    Example:
        kahan_sum([0.1] * 10) should be closer to 1.0 than sum([0.1] * 10)
    """
    # TODO: Implement this function
    pass


# =============================================================================
# Exercise 5: Float Bit Inspector
# =============================================================================

def float_bit_breakdown(f):
    """Return the sign, exponent, and mantissa of a 64-bit float.

    Returns a dict with:
        'sign': 0 or 1
        'exponent': the biased exponent (11-bit integer)
        'true_exponent': the actual exponent (exponent - 1023)
        'mantissa_bits': string of 52 mantissa bits

    Use struct.pack('>d', f) to get bytes, struct.unpack('>Q', ...) to get int.

    Example:
        float_bit_breakdown(1.0) -> {
            'sign': 0,
            'exponent': 1023,
            'true_exponent': 0,
            'mantissa_bits': '0000...0000'  (52 zeros)
        }
    """
    import struct
    # TODO: Implement this function
    pass


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests. Green means pass, red means you have work to do."""
    import struct

    passed = 0
    failed = 0
    total = 0

    def check(name, got, expected):
        nonlocal passed, failed, total
        total += 1
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"        Expected: {expected}")
            print(f"        Got:      {got}")
            failed += 1

    print("=" * 65)
    print("Running Tests")
    print("=" * 65)

    # Exercise 1: Binary Conversion
    print("\n--- Exercise 1: Binary Conversion ---")
    check("decimal_to_binary(5, 8)", decimal_to_binary(5, 8), '00000101')
    check("decimal_to_binary(0, 8)", decimal_to_binary(0, 8), '00000000')
    check("decimal_to_binary(127, 8)", decimal_to_binary(127, 8), '01111111')
    check("decimal_to_binary(-1, 8)", decimal_to_binary(-1, 8), '11111111')
    check("decimal_to_binary(-128, 8)", decimal_to_binary(-128, 8), '10000000')
    check("decimal_to_binary(-42, 8)", decimal_to_binary(-42, 8), '11010110')
    check("decimal_to_binary(255, 16)", decimal_to_binary(255, 16), '0000000011111111')

    check("binary_to_decimal('00000101', True)", binary_to_decimal('00000101', True), 5)
    check("binary_to_decimal('11111111', True)", binary_to_decimal('11111111', True), -1)
    check("binary_to_decimal('11111111', False)", binary_to_decimal('11111111', False), 255)
    check("binary_to_decimal('10000000', True)", binary_to_decimal('10000000', True), -128)

    # Exercise 2: Overflow Detection
    print("\n--- Exercise 2: Overflow Detection ---")
    result = will_overflow_on_add(127, 1, 8)
    if result is not None:
        check("will_overflow(127+1, 8bit) overflows", result[0], True)
        check("will_overflow(127+1, 8bit) wraps to", result[1], -128)
    result = will_overflow_on_add(10, 20, 8)
    if result is not None:
        check("will_overflow(10+20, 8bit) no overflow", result[0], False)
        check("will_overflow(10+20, 8bit) result", result[1], 30)

    # Exercise 3: Float Comparison
    print("\n--- Exercise 3: Float Comparison ---")
    check("safe_float_equal(0.1+0.2, 0.3)", safe_float_equal(0.1 + 0.2, 0.3), True)
    check("safe_float_equal(1.0, 2.0)", safe_float_equal(1.0, 2.0), False)
    check("safe_float_equal(1e-10, 2e-10)", safe_float_equal(1e-10, 2e-10), True)

    # Exercise 4: Kahan Summation
    print("\n--- Exercise 4: Kahan Summation ---")
    if kahan_sum is not None and kahan_sum([0.1] * 10) is not None:
        naive = sum([0.1] * 10)
        kahan = kahan_sum([0.1] * 10)
        check("kahan_sum closer to 1.0 than naive",
              abs(kahan - 1.0) <= abs(naive - 1.0), True)

        kahan_million = kahan_sum([0.1] * 1_000_000)
        naive_million = sum([0.1] * 1_000_000)
        check("kahan_sum(0.1 * 1M) closer to 100000",
              abs(kahan_million - 100_000) < abs(naive_million - 100_000), True)

    # Exercise 5: Float Bit Inspector
    print("\n--- Exercise 5: Float Bit Inspector ---")
    result = float_bit_breakdown(1.0)
    if result is not None:
        check("float_bit_breakdown(1.0) sign", result['sign'], 0)
        check("float_bit_breakdown(1.0) exponent", result['exponent'], 1023)
        check("float_bit_breakdown(1.0) true_exponent", result['true_exponent'], 0)
        check("float_bit_breakdown(1.0) mantissa all zeros",
              result['mantissa_bits'], '0' * 52)

    result = float_bit_breakdown(-1.0)
    if result is not None:
        check("float_bit_breakdown(-1.0) sign", result['sign'], 1)

    # Summary
    print(f"\n{'=' * 65}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    if failed == 0 and total > 0:
        print("All exercises complete!")
    elif total == 0 or passed == 0:
        print("No tests passed yet. Implement the TODO functions!")
    else:
        print(f"Keep going -- {failed} more to implement.")
    print("=" * 65)


if __name__ == '__main__':
    run_tests()
