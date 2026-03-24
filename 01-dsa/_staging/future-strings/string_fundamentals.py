"""
Day 16: Strings as Arrays — Encoding, Immutability, and Patterns

This script demonstrates that strings are arrays of integers with encoding
rules layered on top. We explore ASCII/Unicode/UTF-8, measure the cost of
immutability, and show why string problems are really array problems.

WHY THIS MATTERS:
If you don't understand that strings are arrays, you will:
- Write O(n^2) concatenation code in production
- Miscount characters in multilingual text
- Fail to see that most string interview problems are array problems

Run: python string_fundamentals.py
"""

import sys
import time


# ---------------------------------------------------------------------------
# 1. STRINGS ARE INTEGER ARRAYS
# ---------------------------------------------------------------------------

def strings_are_arrays():
    """
    A string is a sequence of integers. Each integer maps to a character
    via an encoding table. Python's ord() and chr() make this explicit.
    """
    print("=" * 70)
    print("1. STRINGS ARE INTEGER ARRAYS")
    print("=" * 70)

    s = "Hello"
    print(f"\nString: '{s}'")
    print(f"Length: {len(s)}")
    print(f"Type:   {type(s)}")
    print()

    # Show the integer representation
    print("Character-by-character (the array view):")
    print("-" * 50)
    for i, ch in enumerate(s):
        print(f"  s[{i}] = '{ch}'  →  ord = {ord(ch):>5}  →  "
              f"binary = {ord(ch):08b}  →  hex = {ord(ch):#04x}")

    print()
    print("Reverse mapping — integers back to characters:")
    ints = [72, 101, 108, 108, 111]
    reconstructed = "".join(chr(n) for n in ints)
    print(f"  {ints} → '{reconstructed}'")

    print()
    print("KEY INSIGHT: A string IS an array. s[i] is O(1) array access.")
    print("Every array technique you know works on strings.\n")


# ---------------------------------------------------------------------------
# 2. ASCII vs UNICODE vs UTF-8
# ---------------------------------------------------------------------------

def encoding_deep_dive():
    """
    Show the difference between code points (Unicode) and byte
    representations (UTF-8). This is where most bugs happen.
    """
    print("=" * 70)
    print("2. ENCODING: ASCII vs UNICODE vs UTF-8")
    print("=" * 70)

    test_strings = [
        ("ASCII",    "Hello"),
        ("Accented", "café"),
        ("Chinese",  "你好"),
        ("Emoji",    "🎉🐍"),
        ("Mixed",    "Hi! 你好 🎉"),
    ]

    print(f"\n{'Label':<10} {'String':<12} {'chars':>5} {'UTF-8 bytes':>11} "
          f"{'UTF-16 bytes':>12} {'UTF-32 bytes':>12}")
    print("-" * 70)

    for label, s in test_strings:
        n_chars = len(s)
        n_utf8 = len(s.encode('utf-8'))
        n_utf16 = len(s.encode('utf-16-le'))  # -le to skip BOM
        n_utf32 = len(s.encode('utf-32-le'))
        print(f"{label:<10} {s:<12} {n_chars:>5} {n_utf8:>11} "
              f"{n_utf16:>12} {n_utf32:>12}")

    print()
    print("Character-level UTF-8 breakdown for 'café':")
    print("-" * 50)
    for ch in "café":
        utf8_bytes = ch.encode('utf-8')
        hex_bytes = " ".join(f"{b:02x}" for b in utf8_bytes)
        print(f"  '{ch}'  code point: U+{ord(ch):04X}  "
              f"UTF-8: {hex_bytes} ({len(utf8_bytes)} byte{'s' if len(utf8_bytes) > 1 else ''})")

    print()
    print("Character-level UTF-8 breakdown for '🎉🐍':")
    print("-" * 50)
    for ch in "🎉🐍":
        utf8_bytes = ch.encode('utf-8')
        hex_bytes = " ".join(f"{b:02x}" for b in utf8_bytes)
        print(f"  '{ch}'  code point: U+{ord(ch):04X}  "
              f"UTF-8: {hex_bytes} ({len(utf8_bytes)} bytes)")

    print()
    print("KEY INSIGHT: len('café') = 4 characters, but 5 UTF-8 bytes.")
    print("UTF-8 is variable-width. 'é' takes 2 bytes. '🎉' takes 4 bytes.")
    print("Python 3 abstracts this — len() counts characters, not bytes.\n")


# ---------------------------------------------------------------------------
# 3. STRING IMMUTABILITY AND THE O(n^2) TRAP
# ---------------------------------------------------------------------------

def immutability_demo():
    """
    Strings in Python are immutable. Every 'modification' creates a new
    string object. This means += in a loop is O(n^2) total work.
    """
    print("=" * 70)
    print("3. IMMUTABILITY — THE O(n^2) CONCATENATION TRAP")
    print("=" * 70)

    # Demonstrate immutability
    s = "hello"
    original_id = id(s)
    s = s + " world"
    new_id = id(s)

    print(f"\n  s = 'hello'        → id = {original_id}")
    print(f"  s = s + ' world'  → id = {new_id}")
    print(f"  Same object? {original_id == new_id}")
    print("  A new string was allocated. The old one will be garbage collected.")
    print()

    # Benchmark: += vs join
    sizes = [1000, 2000, 5000, 10000, 20000, 50000]

    print("Benchmark: Building a string of N characters")
    print(f"{'N':>8}  {'+=  (ms)':>10}  {'join (ms)':>10}  {'ratio':>8}")
    print("-" * 45)

    for n in sizes:
        chars = ['x'] * n

        # Method 1: += in a loop (O(n^2))
        start = time.perf_counter()
        result = ""
        for ch in chars:
            result += ch
        time_concat = (time.perf_counter() - start) * 1000

        # Method 2: join (O(n))
        start = time.perf_counter()
        result = "".join(chars)
        time_join = (time.perf_counter() - start) * 1000

        ratio = time_concat / time_join if time_join > 0 else float('inf')
        print(f"{n:>8}  {time_concat:>10.3f}  {time_join:>10.3f}  {ratio:>7.1f}x")

    print()
    print("NOTE: CPython has an optimization for += on strings with refcount 1,")
    print("which makes the gap smaller than pure theory predicts. But in real")
    print("code (where the string may have other references), the O(n^2) trap")
    print("is very real. Always use join() or list buffer.\n")


# ---------------------------------------------------------------------------
# 4. STRING INTERNING
# ---------------------------------------------------------------------------

def interning_demo():
    """
    Python caches certain strings and reuses the same object.
    This is an optimization detail — never rely on it for correctness.
    """
    print("=" * 70)
    print("4. STRING INTERNING")
    print("=" * 70)

    # Short strings and identifiers are typically interned
    a = "hello"
    b = "hello"
    print(f"\n  a = 'hello', b = 'hello'")
    print(f"  a == b: {a == b}  (value equality — always use this)")
    print(f"  a is b: {a is b}  (identity — same object in memory)")
    print(f"  id(a) = {id(a)}, id(b) = {id(b)}")
    print()

    # Strings created at runtime may not be interned
    c = "hel" + "lo"       # Compile-time constant folding → interned
    d = "hel" + str("lo")  # Runtime construction → may not be interned
    print(f"  c = 'hel' + 'lo'        → id = {id(c)}, c is a: {c is a}")
    print(f"  d = 'hel' + str('lo')   → id = {id(d)}, d is a: {d is a}")
    print()

    # Integers within common string operations
    print("  Why this matters:")
    print("  - 'is' checks identity (same object), == checks value")
    print("  - NEVER use 'is' to compare strings in production code")
    print("  - Interning is a CPython optimization, not part of the language spec\n")


# ---------------------------------------------------------------------------
# 5. COMMON OPERATIONS AND THEIR TRUE COST
# ---------------------------------------------------------------------------

def operation_costs():
    """
    Measure the real cost of common string operations.
    Key lesson: every 'modification' creates a new string.
    """
    print("=" * 70)
    print("5. OPERATION COSTS — MEASURED")
    print("=" * 70)

    s = "a" * 100_000
    t = "b" * 100_000
    pattern = "xyz"

    operations = []

    # Indexing — O(1)
    start = time.perf_counter()
    for _ in range(100_000):
        _ = s[50_000]
    t1 = time.perf_counter() - start
    operations.append(("s[i] (100K times)", t1))

    # len — O(1)
    start = time.perf_counter()
    for _ in range(100_000):
        _ = len(s)
    t1 = time.perf_counter() - start
    operations.append(("len(s) (100K times)", t1))

    # Concatenation — O(n+m)
    start = time.perf_counter()
    _ = s + t
    t1 = time.perf_counter() - start
    operations.append(("s + t (200K chars)", t1))

    # find — O(n*m) worst case
    start = time.perf_counter()
    _ = s.find(pattern)
    t1 = time.perf_counter() - start
    operations.append(("s.find('xyz') in 100K", t1))

    # replace — O(n)
    start = time.perf_counter()
    _ = s.replace("a", "b")
    t1 = time.perf_counter() - start
    operations.append(("s.replace('a','b')", t1))

    # split — O(n)
    csv_line = ",".join(["item"] * 10_000)
    start = time.perf_counter()
    _ = csv_line.split(",")
    t1 = time.perf_counter() - start
    operations.append(("split 10K-item CSV", t1))

    # reverse — O(n)
    start = time.perf_counter()
    _ = s[::-1]
    t1 = time.perf_counter() - start
    operations.append(("s[::-1] (100K chars)", t1))

    print(f"\n{'Operation':<30} {'Time (ms)':>10}")
    print("-" * 42)
    for name, elapsed in operations:
        print(f"  {name:<28} {elapsed * 1000:>10.3f}")

    print()
    print("KEY INSIGHT: Indexing and len() are O(1). Everything else involves")
    print("copying. If your algorithm 'modifies' a string N times, you are")
    print("doing N allocations. Use a list of characters instead.\n")


# ---------------------------------------------------------------------------
# 6. STRINGS AS ARRAYS — THE PATTERN CONNECTION
# ---------------------------------------------------------------------------

def strings_as_array_problems():
    """
    Most string problems are array problems. Once you see a string as int[],
    you can apply all array techniques: frequency counting, two pointers,
    sliding window, prefix sums.
    """
    print("=" * 70)
    print("6. STRING PROBLEMS ARE ARRAY PROBLEMS")
    print("=" * 70)

    # Frequency counting — same as counting elements in an integer array
    print("\nExample 1: Character frequency (= array element counting)")
    print("-" * 50)
    s = "abracadabra"
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    print(f"  String: '{s}'")
    print(f"  Frequencies: {freq}")
    print("  This is identical to counting elements in [0,1,17,0,2,0,3,...]")

    # Anagram check — frequency comparison
    print("\nExample 2: Anagram check (= frequency array equality)")
    print("-" * 50)
    word1, word2 = "listen", "silent"
    freq1 = [0] * 26
    freq2 = [0] * 26
    for ch in word1:
        freq1[ord(ch) - ord('a')] += 1
    for ch in word2:
        freq2[ord(ch) - ord('a')] += 1
    is_anagram = freq1 == freq2
    print(f"  '{word1}' and '{word2}' are anagrams: {is_anagram}")
    print(f"  freq1: {[f for i, f in enumerate(freq1) if f > 0]}")
    print(f"  Method: Two frequency arrays compared element-by-element")

    # Palindrome check — two pointers on an array
    print("\nExample 3: Palindrome check (= two-pointer array technique)")
    print("-" * 50)
    s = "racecar"
    left, right = 0, len(s) - 1
    is_palindrome = True
    comparisons = []
    while left < right:
        comparisons.append(f"s[{left}]='{s[left]}' vs s[{right}]='{s[right]}'")
        if s[left] != s[right]:
            is_palindrome = False
            break
        left += 1
        right -= 1
    print(f"  String: '{s}'")
    print(f"  Comparisons: {', '.join(comparisons)}")
    print(f"  Palindrome: {is_palindrome}")
    print(f"  This is the two-pointer technique on an array.")

    print()
    print("KEY INSIGHT: When you see a string problem, mentally replace")
    print("'string' with 'integer array'. The same patterns apply:\n")
    print("  String operation     →  Array equivalent")
    print("  ─────────────────────────────────────────")
    print("  Character frequency  →  Element counting")
    print("  Anagram check        →  Frequency array equality")
    print("  Palindrome check     →  Two pointers from ends")
    print("  Substring search     →  Subarray pattern matching")
    print("  Longest unique substr→  Sliding window on array")
    print()


# ---------------------------------------------------------------------------
# 7. MEMORY: STRING OBJECT OVERHEAD IN PYTHON
# ---------------------------------------------------------------------------

def memory_overhead():
    """
    Show how much memory Python strings actually consume.
    """
    print("=" * 70)
    print("7. PYTHON STRING MEMORY OVERHEAD")
    print("=" * 70)

    test_cases = [
        "",
        "a",
        "hello",
        "a" * 100,
        "a" * 1000,
        "café",
        "你好",
        "🎉",
    ]

    print(f"\n{'String':<15} {'chars':>5} {'sys.getsizeof':>13} {'bytes/char':>10}")
    print("-" * 48)
    for s in test_cases:
        size = sys.getsizeof(s)
        display = repr(s) if len(s) <= 10 else repr(s[:8] + "...")
        bpc = size / len(s) if len(s) > 0 else float('inf')
        print(f"  {display:<13} {len(s):>5} {size:>13} {bpc:>10.1f}")

    print()
    print("KEY INSIGHT: Python string objects have ~50 bytes of overhead")
    print("(object header, hash cache, length, etc). For short strings,")
    print("overhead dominates. For long strings, it amortizes away.")
    print("Python also uses different internal encodings (Latin-1, UCS-2,")
    print("UCS-4) depending on the widest character in the string.\n")


if __name__ == "__main__":
    strings_are_arrays()
    encoding_deep_dive()
    immutability_demo()
    interning_demo()
    operation_costs()
    strings_as_array_problems()
    memory_overhead()
