"""
Day 9: Practice -- Bit Manipulation Exercises
===============================================

Fill in the TODO sections. Use ONLY bitwise operators (&, |, ^, ~, <<, >>).
No arithmetic shortcuts (*, /, %) unless the exercise specifically says otherwise.

Run: python practice.py
"""


# =============================================================================
# Exercise 1: Count Set Bits (Brian Kernighan's Algorithm)
# =============================================================================

def count_set_bits(n):
    """Count the number of 1-bits in the binary representation of n.

    Use Brian Kernighan's algorithm: n & (n - 1) clears the lowest set bit.
    Repeat until n is 0. The number of iterations is the answer.

    Examples:
        count_set_bits(0)   -> 0
        count_set_bits(1)   -> 1
        count_set_bits(7)   -> 3   (111)
        count_set_bits(255) -> 8   (11111111)
        count_set_bits(128) -> 1   (10000000)
    """
    # TODO: Implement using Kernighan's algorithm
    pass


# =============================================================================
# Exercise 2: Check Power of Two
# =============================================================================

def is_power_of_two(n):
    """Return True if n is a positive power of 2, False otherwise.

    A power of 2 has exactly one set bit. Use the n & (n-1) trick.

    Examples:
        is_power_of_two(1)   -> True   (2^0)
        is_power_of_two(2)   -> True   (2^1)
        is_power_of_two(16)  -> True   (2^4)
        is_power_of_two(0)   -> False
        is_power_of_two(6)   -> False  (110)
        is_power_of_two(-4)  -> False
    """
    # TODO: Implement this. One line is enough.
    pass


# =============================================================================
# Exercise 3: Find the Single Number
# =============================================================================

def find_single_number(nums):
    """Every element appears exactly twice except one. Find it.

    Use the XOR property: a ^ a = 0 and a ^ 0 = a.
    XOR all numbers together -- pairs cancel, leaving the unique one.

    Must be O(n) time, O(1) space. No hash maps or sorting.

    Examples:
        find_single_number([2, 3, 2])       -> 3
        find_single_number([4, 1, 2, 1, 2]) -> 4
        find_single_number([1])             -> 1
    """
    # TODO: Implement using XOR
    pass


# =============================================================================
# Exercise 4: Get, Set, Clear, Toggle Bit
# =============================================================================

def get_bit(n, i):
    """Return the value of bit at position i (0-indexed from right).

    Examples:
        get_bit(0b1010, 1) -> 1
        get_bit(0b1010, 0) -> 0
        get_bit(0b1010, 3) -> 1
    """
    # TODO: Implement
    pass


def set_bit(n, i):
    """Set bit at position i to 1. Return the new number.

    Examples:
        set_bit(0b1010, 0) -> 0b1011 (11)
        set_bit(0b1010, 2) -> 0b1110 (14)
    """
    # TODO: Implement
    pass


def clear_bit(n, i):
    """Clear bit at position i to 0. Return the new number.

    Examples:
        clear_bit(0b1010, 1) -> 0b1000 (8)
        clear_bit(0b1010, 3) -> 0b0010 (2)
    """
    # TODO: Implement
    pass


def toggle_bit(n, i):
    """Toggle bit at position i. Return the new number.

    Examples:
        toggle_bit(0b1010, 0) -> 0b1011 (11)
        toggle_bit(0b1010, 1) -> 0b1000 (8)
    """
    # TODO: Implement
    pass


# =============================================================================
# Exercise 5: Swap Two Numbers Without Temp
# =============================================================================

def swap_xor(a, b):
    """Swap a and b using only XOR. Return (b, a).

    The classic three-step XOR swap:
      a ^= b
      b ^= a
      a ^= b

    Examples:
        swap_xor(5, 10) -> (10, 5)
        swap_xor(0, 42) -> (42, 0)
    """
    # TODO: Implement with three XOR operations
    pass


# =============================================================================
# Exercise 6: Reverse Bits
# =============================================================================

def reverse_bits(n, width=8):
    """Reverse the bit order of n within the given width.

    Examples:
        reverse_bits(0b10110000, 8) -> 0b00001101 (13)
        reverse_bits(0b00000001, 8) -> 0b10000000 (128)
        reverse_bits(0b11111111, 8) -> 0b11111111 (255)
    """
    # TODO: Implement
    # Hint: iterate through each bit position, extract bit from source,
    # place it in the mirror position of result
    pass


# =============================================================================
# Exercise 7: Unix Permission Check
# =============================================================================

READ    = 0o4
WRITE   = 0o2
EXECUTE = 0o1

def has_permission(mode, who, perm):
    """Check if the given permission is set for the given user class.

    Args:
        mode: 9-bit permission integer (e.g., 0o755)
        who: 'owner', 'group', or 'others'
        perm: READ, WRITE, or EXECUTE constant

    Examples:
        has_permission(0o755, 'owner', EXECUTE)  -> True
        has_permission(0o755, 'owner', WRITE)    -> True
        has_permission(0o755, 'group', WRITE)    -> False
        has_permission(0o644, 'others', READ)    -> True
        has_permission(0o644, 'others', WRITE)   -> False
    """
    # TODO: Implement using bit shifts and AND
    # Hint: owner bits are at positions 6-8, group at 3-5, others at 0-2
    pass


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests. Green means pass, red means you have work to do."""
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

    # Exercise 1: Count Set Bits
    print("\n--- Exercise 1: Count Set Bits ---")
    check("count_set_bits(0)", count_set_bits(0), 0)
    check("count_set_bits(1)", count_set_bits(1), 1)
    check("count_set_bits(7)", count_set_bits(7), 3)
    check("count_set_bits(255)", count_set_bits(255), 8)
    check("count_set_bits(128)", count_set_bits(128), 1)
    check("count_set_bits(0b10101010)", count_set_bits(0b10101010), 4)

    # Exercise 2: Power of Two
    print("\n--- Exercise 2: Power of Two ---")
    check("is_power_of_two(1)", is_power_of_two(1), True)
    check("is_power_of_two(2)", is_power_of_two(2), True)
    check("is_power_of_two(16)", is_power_of_two(16), True)
    check("is_power_of_two(1024)", is_power_of_two(1024), True)
    check("is_power_of_two(0)", is_power_of_two(0), False)
    check("is_power_of_two(6)", is_power_of_two(6), False)
    check("is_power_of_two(-4)", is_power_of_two(-4), False)

    # Exercise 3: Single Number
    print("\n--- Exercise 3: Find Single Number ---")
    check("find_single_number([2,3,2])", find_single_number([2, 3, 2]), 3)
    check("find_single_number([4,1,2,1,2])", find_single_number([4, 1, 2, 1, 2]), 4)
    check("find_single_number([1])", find_single_number([1]), 1)
    check("find_single_number([99,1,1])", find_single_number([99, 1, 1]), 99)

    # Exercise 4: Bit Operations
    print("\n--- Exercise 4: Get/Set/Clear/Toggle Bit ---")
    check("get_bit(0b1010, 1)", get_bit(0b1010, 1), 1)
    check("get_bit(0b1010, 0)", get_bit(0b1010, 0), 0)
    check("get_bit(0b1010, 3)", get_bit(0b1010, 3), 1)
    check("set_bit(0b1010, 0)", set_bit(0b1010, 0), 0b1011)
    check("set_bit(0b1010, 2)", set_bit(0b1010, 2), 0b1110)
    check("clear_bit(0b1010, 1)", clear_bit(0b1010, 1), 0b1000)
    check("clear_bit(0b1010, 3)", clear_bit(0b1010, 3), 0b0010)
    check("toggle_bit(0b1010, 0)", toggle_bit(0b1010, 0), 0b1011)
    check("toggle_bit(0b1010, 1)", toggle_bit(0b1010, 1), 0b1000)

    # Exercise 5: XOR Swap
    print("\n--- Exercise 5: XOR Swap ---")
    check("swap_xor(5, 10)", swap_xor(5, 10), (10, 5))
    check("swap_xor(0, 42)", swap_xor(0, 42), (42, 0))
    check("swap_xor(7, 7)", swap_xor(7, 7), (7, 7))

    # Exercise 6: Reverse Bits
    print("\n--- Exercise 6: Reverse Bits ---")
    check("reverse_bits(0b10110000, 8)", reverse_bits(0b10110000, 8), 0b00001101)
    check("reverse_bits(0b00000001, 8)", reverse_bits(0b00000001, 8), 0b10000000)
    check("reverse_bits(0b11111111, 8)", reverse_bits(0b11111111, 8), 0b11111111)
    check("reverse_bits(0b10000000, 8)", reverse_bits(0b10000000, 8), 0b00000001)

    # Exercise 7: Unix Permissions
    print("\n--- Exercise 7: Unix Permissions ---")
    check("has_permission(0o755, 'owner', EXECUTE)", has_permission(0o755, 'owner', EXECUTE), True)
    check("has_permission(0o755, 'owner', WRITE)", has_permission(0o755, 'owner', WRITE), True)
    check("has_permission(0o755, 'group', WRITE)", has_permission(0o755, 'group', WRITE), False)
    check("has_permission(0o755, 'group', READ)", has_permission(0o755, 'group', READ), True)
    check("has_permission(0o644, 'others', READ)", has_permission(0o644, 'others', READ), True)
    check("has_permission(0o644, 'others', WRITE)", has_permission(0o644, 'others', WRITE), False)
    check("has_permission(0o700, 'group', READ)", has_permission(0o700, 'group', READ), False)

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


# =============================================================================
# SOLUTIONS (try yourself first!)
# =============================================================================

def _check_solutions():
    """Reference solutions. Only look after attempting all exercises."""

    def _sol_count_set_bits(n):
        count = 0
        while n:
            n &= (n - 1)
            count += 1
        return count

    def _sol_is_power_of_two(n):
        return n > 0 and (n & (n - 1)) == 0

    def _sol_find_single_number(nums):
        result = 0
        for x in nums:
            result ^= x
        return result

    def _sol_get_bit(n, i):
        return (n >> i) & 1

    def _sol_set_bit(n, i):
        return n | (1 << i)

    def _sol_clear_bit(n, i):
        return n & ~(1 << i)

    def _sol_toggle_bit(n, i):
        return n ^ (1 << i)

    def _sol_swap_xor(a, b):
        a ^= b
        b ^= a
        a ^= b
        return (a, b)

    def _sol_reverse_bits(n, width=8):
        result = 0
        for i in range(width):
            result = (result << 1) | (n & 1)
            n >>= 1
        return result

    def _sol_has_permission(mode, who, perm):
        shift = {'owner': 6, 'group': 3, 'others': 0}[who]
        return bool((mode >> shift) & perm)

    print("\nSolutions loaded. Compare with your implementations.")


if __name__ == '__main__':
    run_tests()
