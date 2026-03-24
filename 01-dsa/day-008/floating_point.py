"""
Day 8: Floating Point -- Why Your Computer Cannot Count to 0.3
===============================================================

IEEE 754 floating point is the universal standard for representing
real numbers in hardware. It is an engineering masterpiece AND a
source of endless bugs. This file shows you exactly how it works
and exactly how it fails.

Run: python floating_point.py
"""

import struct
import math
from decimal import Decimal, getcontext


# =============================================================================
# SECTION 1: The Fundamental Problem -- 0.1 + 0.2 != 0.3
# =============================================================================

print("=" * 65)
print("SECTION 1: The Famous Lie -- 0.1 + 0.2 != 0.3")
print("=" * 65)

a, b = 0.1, 0.2
c = a + b
print(f"\n  0.1 + 0.2 = {c}")
print(f"  0.1 + 0.2 == 0.3?  {c == 0.3}")
print(f"  Difference: {c - 0.3}")

# Show what 0.1 ACTUALLY is in the computer
print(f"\n  What the computer stores for '0.1':")
print(f"  {Decimal(0.1)}")
print(f"\n  What the computer stores for '0.2':")
print(f"  {Decimal(0.2)}")
print(f"\n  What the computer stores for '0.3':")
print(f"  {Decimal(0.3)}")
print(f"\n  Actual sum of stored 0.1 + stored 0.2:")
print(f"  {Decimal(0.1) + Decimal(0.2)}")

# WHY this happens: 0.1 in binary is a repeating fraction
print("\n  WHY: 0.1 in decimal = 0.0001100110011001100110011... in binary")
print("  Just as 1/3 = 0.333... never terminates in decimal,")
print("  1/10 = 0.000110011... never terminates in binary.")
print("  The mantissa gets truncated after 52 bits, introducing error.")


# =============================================================================
# SECTION 2: IEEE 754 Anatomy -- Dissecting a Float
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 2: IEEE 754 Internal Structure")
print("=" * 65)

def float_to_bits(f):
    """Convert a Python float (64-bit double) to its bit representation.

    A 64-bit double has:
    - 1 bit: sign (0 = positive, 1 = negative)
    - 11 bits: exponent (biased by 1023)
    - 52 bits: mantissa (with an implicit leading 1)
    """
    # Pack float as bytes, unpack as 64-bit integer
    packed = struct.pack('>d', f)
    bits = struct.unpack('>Q', packed)[0]
    binary = format(bits, '064b')

    sign = binary[0]
    exponent = binary[1:12]
    mantissa = binary[12:]

    return sign, exponent, mantissa


def analyze_float(f):
    """Show the complete internal representation of a float."""
    sign, exponent, mantissa = float_to_bits(f)
    exp_value = int(exponent, 2) - 1023  # Remove bias

    print(f"\n  Float value: {f}")
    print(f"  Exact value: {Decimal(f)}")
    print(f"  Sign bit:    {sign} ({'negative' if sign == '1' else 'positive'})")
    print(f"  Exponent:    {exponent} (biased: {int(exponent, 2)}, actual: {exp_value})")
    print(f"  Mantissa:    {mantissa[:26]}...")
    print(f"  Formula:     (-1)^{sign} * 1.{mantissa[:10]}... * 2^{exp_value}")

analyze_float(1.0)
analyze_float(0.1)
analyze_float(-42.5)
analyze_float(0.0)


# =============================================================================
# SECTION 3: Precision Limits
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 3: Precision Limits -- Where Floats Break Down")
print("=" * 65)

# Machine epsilon: the smallest number that, when added to 1.0, gives
# a result different from 1.0
print("\n--- Machine Epsilon ---")
eps = 1.0
while 1.0 + eps != 1.0:
    eps /= 2
eps *= 2  # Back up one step -- that was the last one that worked
print(f"  Machine epsilon: {eps}")
print(f"  sys.float_info.epsilon: {2**-52}")
print(f"  1.0 + eps = {1.0 + eps}")
print(f"  1.0 + eps/2 = {1.0 + eps/2}  (eps/2 is LOST!)")

# Large numbers lose precision in lower digits
print("\n--- Large Number Precision Loss ---")
big = 2.0 ** 53  # 9,007,199,254,740,992
print(f"  2^53 = {big:.0f}")
print(f"  2^53 + 1 = {big + 1:.0f}  (should be {int(big) + 1})")
print(f"  2^53 + 2 = {big + 2:.0f}")
# At 2^53, the float cannot distinguish consecutive integers!
print(f"  2^53 == 2^53 + 1?  {big == big + 1}  <-- THIS IS TRUE!")
print("  Above 2^53, a 64-bit float cannot represent every integer.")

# The gap between representable floats grows with magnitude
print("\n--- Growing Gaps Between Representable Numbers ---")
for exp in [0, 10, 20, 30, 40, 50]:
    x = 2.0 ** exp
    # nextafter gives the next representable float
    gap = math.nextafter(x, float('inf')) - x
    print(f"  Near 2^{exp:>2} = {x:>20,.0f}, gap = {gap}")


# =============================================================================
# SECTION 4: Accumulation Errors
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 4: Error Accumulation -- Death by a Thousand Cuts")
print("=" * 65)

# Adding 0.1 many times
print("\n--- Adding 0.1 repeatedly ---")
total = 0.0
for i in range(10):
    total += 0.1
print(f"  0.1 added 10 times = {total}")
print(f"  Expected: 1.0")
print(f"  Equal? {total == 1.0}")
print(f"  Error: {total - 1.0}")

# Worse with more iterations
total = 0.0
for i in range(1000):
    total += 0.1
print(f"\n  0.1 added 1000 times = {total}")
print(f"  Expected: 100.0")
print(f"  Error: {total - 100.0}")

total = 0.0
for i in range(1_000_000):
    total += 0.1
print(f"\n  0.1 added 1,000,000 times = {total}")
print(f"  Expected: 100,000.0")
print(f"  Error: {total - 100_000.0}")

# Kahan summation -- the fix
print("\n--- Kahan Summation Algorithm (the fix) ---")
def kahan_sum(values):
    """Compensated summation that tracks accumulated error.

    The key insight: we keep a separate 'compensation' variable
    that accumulates the low-order bits lost during each addition.
    """
    total = 0.0
    compensation = 0.0  # A running compensation for lost low-order bits

    for value in values:
        # 'y' is the value we want to add, corrected by accumulated error
        y = value - compensation
        # 't' is the new total -- but we lose low-order bits of 'y' here
        t = total + y
        # (t - total) recovers the high-order bits of 'y';
        # subtracting y gives us the lost low-order bits (negated)
        compensation = (t - total) - y
        total = t

    return total

naive = sum([0.1] * 1_000_000)
kahan = kahan_sum([0.1] * 1_000_000)
print(f"  Naive sum of 0.1 * 1M:  {naive}")
print(f"  Kahan sum of 0.1 * 1M:  {kahan}")
print(f"  Naive error: {naive - 100_000.0}")
print(f"  Kahan error: {kahan - 100_000.0}")
print(f"  Python math.fsum:       {math.fsum([0.1] * 1_000_000)}")


# =============================================================================
# SECTION 5: Special Values -- Infinity, NaN, and Negative Zero
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 5: Special Values")
print("=" * 65)

print("\n--- Infinity ---")
inf = float('inf')
print(f"  float('inf') = {inf}")
print(f"  inf + 1 = {inf + 1}")
print(f"  inf + inf = {inf + inf}")
print(f"  inf * -1 = {inf * -1}")
print(f"  1 / inf = {1 / inf}")
print(f"  inf > 1e308 = {inf > 1e308}")

print("\n--- NaN (Not a Number) ---")
nan = float('nan')
print(f"  float('nan') = {nan}")
print(f"  nan == nan?  {nan == nan}  <-- NaN is NOT equal to itself!")
print(f"  nan != nan?  {nan != nan}  <-- This is how you detect NaN")
print(f"  math.isnan(nan)? {math.isnan(nan)}  <-- Better way")
print(f"  nan + 1 = {nan + 1}")
print(f"  nan > 0 = {nan > 0}")
print(f"  nan < 0 = {nan < 0}")
print(f"  nan == 0 = {nan == 0}")
print("  NaN is a 'virus' -- any operation with NaN produces NaN")

print("\n--- Negative Zero ---")
pos_zero = 0.0
neg_zero = -0.0
print(f"  0.0 == -0.0?  {pos_zero == neg_zero}  <-- They compare equal!")
print(f"  But: 1/0.0 = {1/pos_zero if False else '+inf'}")  # Would raise error
print(f"  str(0.0) = '{pos_zero}', str(-0.0) = '{neg_zero}'")
print(f"  math.copysign(1, 0.0) = {math.copysign(1, pos_zero)}")
print(f"  math.copysign(1, -0.0) = {math.copysign(1, neg_zero)}")


# =============================================================================
# SECTION 6: Catastrophic Cancellation
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 6: Catastrophic Cancellation")
print("=" * 65)

# When you subtract two nearly-equal numbers, the significant digits
# cancel out, leaving only the noise from rounding errors.
print("\n  Quadratic formula: (-b +/- sqrt(b^2 - 4ac)) / 2a")
print("  When b^2 >> 4ac, one root suffers catastrophic cancellation.\n")

a_coeff, b_coeff, c_coeff = 1.0, 1e8, 1.0

discriminant = b_coeff**2 - 4*a_coeff*c_coeff
sqrt_disc = math.sqrt(discriminant)

# Standard formula
root1 = (-b_coeff + sqrt_disc) / (2 * a_coeff)
root2 = (-b_coeff - sqrt_disc) / (2 * a_coeff)

# Numerically stable alternative for the problematic root
root1_stable = (2 * c_coeff) / (-b_coeff - sqrt_disc)

print(f"  a={a_coeff}, b={b_coeff}, c={c_coeff}")
print(f"  Standard root1: {root1}")
print(f"  Stable root1:   {root1_stable}")
print(f"  Standard root2: {root2}")
print(f"  True root1 (Decimal): {Decimal(-b_coeff) + Decimal(discriminant).sqrt()}")

# The stable version is far more accurate because it avoids subtracting
# two nearly-equal large numbers.


# =============================================================================
# SECTION 7: Safe Comparison
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 7: Safe Floating Point Comparison")
print("=" * 65)

def almost_equal(a, b, rel_tol=1e-9, abs_tol=1e-12):
    """Compare floats safely.

    We use BOTH relative and absolute tolerance:
    - Relative tolerance handles large numbers (where absolute error grows)
    - Absolute tolerance handles numbers near zero (where relative error explodes)

    Python 3.5+ has math.isclose() which does essentially this.
    """
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

print(f"\n  0.1 + 0.2 == 0.3?           {0.1 + 0.2 == 0.3}")
print(f"  almost_equal(0.1+0.2, 0.3)?  {almost_equal(0.1 + 0.2, 0.3)}")
print(f"  math.isclose(0.1+0.2, 0.3)?  {math.isclose(0.1 + 0.2, 0.3)}")

print("\n  Rules for floating point comparison:")
print("  1. NEVER use == with floats (except against 0.0 in specific cases)")
print("  2. Use math.isclose() for general comparison")
print("  3. For money: use integers (cents) or decimal.Decimal")
print("  4. For science: understand your error bounds")

# Demonstrate Decimal for exact arithmetic
print("\n--- decimal.Decimal for Exact Arithmetic ---")
getcontext().prec = 50
d1 = Decimal('0.1')  # Note: string input gives exact 0.1
d2 = Decimal('0.2')
d3 = Decimal('0.3')
print(f"  Decimal('0.1') + Decimal('0.2') = {d1 + d2}")
print(f"  Decimal('0.1') + Decimal('0.2') == Decimal('0.3')? {d1 + d2 == d3}")
print("  Use Decimal with STRING arguments for exact representation.")

print("\n" + "=" * 65)
print("Done! Now try practice.py")
print("=" * 65)
