"""
Day 16: Practice — String as Array Exercises

Complete the TODO sections. Each exercise treats strings as what they
really are: arrays of integers with encoding rules on top.

Run: python practice.py
"""

import time


# ---------------------------------------------------------------------------
# Exercise 1: Manual encoding / decoding
# ---------------------------------------------------------------------------

def exercise_1():
    """
    Convert between strings and their integer representations manually.
    This cements the mental model: string = int[].
    """
    print("Exercise 1: Manual Encoding / Decoding")
    print("-" * 40)

    # TODO: Given this list of ASCII values, reconstruct the string
    #       using chr() and "".join().
    #       Expected output: "Python"
    ascii_values = [80, 121, 116, 104, 111, 110]

    # YOUR CODE HERE:
    decoded = None  # Replace with your implementation

    print(f"  ASCII values: {ascii_values}")
    print(f"  Decoded: {decoded}")
    assert decoded == "Python", f"Expected 'Python', got '{decoded}'"
    print("  PASSED")

    # TODO: Given this string, produce its list of Unicode code points
    #       using ord().
    #       Expected: [72, 101, 108, 108, 111, 33]
    s = "Hello!"

    # YOUR CODE HERE:
    code_points = None  # Replace with your implementation

    print(f"  String: '{s}'")
    print(f"  Code points: {code_points}")
    assert code_points == [72, 101, 108, 108, 111, 33], f"Wrong code points: {code_points}"
    print("  PASSED")
    print()


# ---------------------------------------------------------------------------
# Exercise 2: Count UTF-8 bytes without using .encode()
# ---------------------------------------------------------------------------

def exercise_2():
    """
    Given a string, calculate how many bytes its UTF-8 encoding would use,
    WITHOUT calling .encode(). Use the code point ranges:
      U+0000 - U+007F:   1 byte
      U+0080 - U+07FF:   2 bytes
      U+0800 - U+FFFF:   3 bytes
      U+10000 - U+10FFFF: 4 bytes
    """
    print("Exercise 2: UTF-8 Byte Count (Manual)")
    print("-" * 40)

    def utf8_byte_count(s):
        """
        Return the number of bytes needed to encode string s in UTF-8.
        Do NOT use s.encode(). Use ord() and the code point ranges above.
        """
        # YOUR CODE HERE:
        pass

    test_cases = [
        ("Hello", 5),        # All ASCII, 1 byte each
        ("café", 5),         # 'é' is U+00E9, takes 2 bytes
        ("你好", 6),          # Each CJK char takes 3 bytes
        ("🎉", 4),           # Emoji takes 4 bytes
        ("Hi! 🐍", 7),       # Mix: 4 ASCII (1 each) + 1 emoji (4) - wait, space counts
    ]

    # Recalculate expected for "Hi! 🐍": H=1, i=1, !=1, space=1, 🐍=4 → 8
    test_cases[-1] = ("Hi! 🐍", 8)

    for s, expected in test_cases:
        result = utf8_byte_count(s)
        status = "PASS" if result == expected else "FAIL"
        actual_bytes = len(s.encode('utf-8'))
        print(f"  [{status}] '{s}': your count = {result}, "
              f"expected = {expected}, actual = {actual_bytes}")

    print()


# ---------------------------------------------------------------------------
# Exercise 3: Build strings efficiently
# ---------------------------------------------------------------------------

def exercise_3():
    """
    Implement a function that builds a comma-separated string from a list
    of integers. Do it TWO ways and compare performance.
    """
    print("Exercise 3: Efficient String Building")
    print("-" * 40)

    numbers = list(range(10000))

    def build_slow(nums):
        """Build comma-separated string using += in a loop. O(n^2)."""
        # YOUR CODE HERE:
        # Use result = "" and result += ... pattern
        pass

    def build_fast(nums):
        """Build comma-separated string using join. O(n)."""
        # YOUR CODE HERE:
        # Use str(), list comprehension, and "".join() or ",".join()
        pass

    # Verify correctness
    expected_start = "0,1,2,3,4"
    slow_result = build_slow(numbers[:5]) if build_slow(numbers[:5]) else ""
    fast_result = build_fast(numbers[:5]) if build_fast(numbers[:5]) else ""
    print(f"  Slow result (first 5): '{slow_result}'")
    print(f"  Fast result (first 5): '{fast_result}'")

    if slow_result and fast_result:
        assert slow_result == fast_result == expected_start, \
            f"Results don't match: slow='{slow_result}', fast='{fast_result}'"
        print("  Results match!")

        # Benchmark
        start = time.perf_counter()
        build_slow(numbers)
        t_slow = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        build_fast(numbers)
        t_fast = (time.perf_counter() - start) * 1000

        print(f"  Slow (+=):   {t_slow:.2f} ms")
        print(f"  Fast (join): {t_fast:.2f} ms")
        print(f"  Ratio: {t_slow / t_fast:.1f}x")
    else:
        print("  (Implement both functions to see the benchmark)")

    print()


# ---------------------------------------------------------------------------
# Exercise 4: Is anagram (frequency array approach)
# ---------------------------------------------------------------------------

def exercise_4():
    """
    Determine if two strings are anagrams using a fixed-size frequency array.
    This is the string-as-array technique: map characters to indices 0-25,
    count frequencies, compare arrays.

    Constraint: Use a list of 26 integers, not a dictionary.
    """
    print("Exercise 4: Anagram Check (Frequency Array)")
    print("-" * 40)

    def is_anagram(s1, s2):
        """
        Return True if s1 and s2 are anagrams (same characters, same counts).
        Assume lowercase English letters only.

        Approach:
        - Create a freq array of size 26 (one slot per letter)
        - Increment for each char in s1
        - Decrement for each char in s2
        - If all zeros at the end, they're anagrams

        Time: O(n), Space: O(1) (fixed 26-element array)
        """
        # YOUR CODE HERE:
        pass

    test_cases = [
        ("listen", "silent", True),
        ("hello", "world", False),
        ("anagram", "nagaram", True),
        ("rat", "car", False),
        ("", "", True),
        ("a", "a", True),
        ("ab", "ba", True),
        ("ab", "aa", False),
    ]

    for s1, s2, expected in test_cases:
        result = is_anagram(s1, s2)
        status = "PASS" if result == expected else "FAIL"
        print(f"  [{status}] is_anagram('{s1}', '{s2}') = {result} "
              f"(expected {expected})")

    print()


# ---------------------------------------------------------------------------
# Exercise 5: Reverse words in a string
# ---------------------------------------------------------------------------

def exercise_5():
    """
    Given a string with words separated by spaces, reverse the order of
    the words (not the characters within words).

    Example: "hello world foo" → "foo world hello"

    Do this TWO ways:
    1. Using split() and join() — Pythonic, O(n)
    2. Manual approach using only indexing — treat string as char array
    """
    print("Exercise 5: Reverse Words")
    print("-" * 40)

    def reverse_words_pythonic(s):
        """Reverse word order using split and join. O(n)."""
        # YOUR CODE HERE:
        pass

    def reverse_words_manual(s):
        """
        Reverse word order by treating the string as a character array.
        Steps:
        1. Convert to list of characters
        2. Reverse the entire list
        3. Reverse each word within the list
        4. Join back to string

        This is the classic in-place approach used in C/C++.
        """
        # YOUR CODE HERE:
        pass

    test_cases = [
        ("hello world", "world hello"),
        ("the sky is blue", "blue is sky the"),
        ("a", "a"),
        ("  hello  world  ", "world hello"),  # strip extra spaces
    ]

    for s, expected in test_cases:
        r1 = reverse_words_pythonic(s)
        print(f"  Pythonic: '{s}' → '{r1}' "
              f"{'PASS' if r1 == expected else 'FAIL (expected: ' + expected + ')'}")

        r2 = reverse_words_manual(s)
        if r2 is not None:
            print(f"  Manual:   '{s}' → '{r2}' "
                  f"{'PASS' if r2 == expected else 'FAIL (expected: ' + expected + ')'}")

    print()


# ---------------------------------------------------------------------------
# Exercise 6: First non-repeating character
# ---------------------------------------------------------------------------

def exercise_6():
    """
    Find the first character in a string that appears exactly once.
    Return its index, or -1 if no such character exists.

    This is a frequency-counting problem: build frequency array, then
    scan left to right for the first character with count == 1.
    Time: O(n), Space: O(1) (at most 26 entries for lowercase)
    """
    print("Exercise 6: First Non-Repeating Character")
    print("-" * 40)

    def first_unique_char(s):
        """
        Return the index of the first non-repeating character in s.
        Return -1 if all characters repeat.
        Assume lowercase English letters only.
        """
        # YOUR CODE HERE:
        pass

    test_cases = [
        ("leetcode", 0),      # 'l' is first unique
        ("loveleetcode", 2),  # 'v' is first unique
        ("aabb", -1),         # no unique character
        ("a", 0),
        ("aab", 2),           # 'b' is first unique
    ]

    for s, expected in test_cases:
        result = first_unique_char(s)
        status = "PASS" if result == expected else "FAIL"
        print(f"  [{status}] first_unique_char('{s}') = {result} "
              f"(expected {expected})")

    print()


# ===========================================================================
# SOLUTIONS — scroll down only after attempting all exercises above
# ===========================================================================


SOLUTIONS = """
+=====================================================================+
|                           SOLUTIONS                                  |
+=====================================================================+

Exercise 1: Manual Encoding / Decoding
    decoded = "".join(chr(v) for v in ascii_values)
    code_points = [ord(c) for c in s]

Exercise 2: UTF-8 Byte Count
    def utf8_byte_count(s):
        total = 0
        for ch in s:
            cp = ord(ch)
            if cp <= 0x7F:
                total += 1
            elif cp <= 0x7FF:
                total += 2
            elif cp <= 0xFFFF:
                total += 3
            else:
                total += 4
        return total

Exercise 3: Efficient String Building
    def build_slow(nums):
        result = ""
        for i, n in enumerate(nums):
            if i > 0:
                result += ","
            result += str(n)
        return result

    def build_fast(nums):
        return ",".join(str(n) for n in nums)

Exercise 4: Anagram Check
    def is_anagram(s1, s2):
        if len(s1) != len(s2):
            return False
        freq = [0] * 26
        for ch in s1:
            freq[ord(ch) - ord('a')] += 1
        for ch in s2:
            freq[ord(ch) - ord('a')] -= 1
        return all(f == 0 for f in freq)

Exercise 5: Reverse Words
    def reverse_words_pythonic(s):
        return " ".join(s.split()[::-1])

    def reverse_words_manual(s):
        chars = list(s.split())  # split handles extra spaces
        left, right = 0, len(chars) - 1
        while left < right:
            chars[left], chars[right] = chars[right], chars[left]
            left += 1
            right -= 1
        return " ".join(chars)

Exercise 6: First Non-Repeating Character
    def first_unique_char(s):
        freq = [0] * 26
        for ch in s:
            freq[ord(ch) - ord('a')] += 1
        for i, ch in enumerate(s):
            if freq[ord(ch) - ord('a')] == 1:
                return i
        return -1
"""


def show_solutions():
    print(SOLUTIONS)


if __name__ == "__main__":
    print("DAY 16 PRACTICE: String as Array Exercises")
    print("=" * 50)
    print("Complete the TODO sections in this file.\n")

    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
    exercise_6()

    print("-" * 50)
    print("To see solutions, uncomment the line below or scroll to the bottom.")
    # show_solutions()
