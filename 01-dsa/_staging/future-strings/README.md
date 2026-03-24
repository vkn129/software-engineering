# Day 16: Strings as Arrays — Encoding, Immutability, and Patterns

## Why This Exists

A string is not a magical text type. It is an array of numbers. Every character you see on screen is an integer — 'A' is 65, 'z' is 122, and the emoji you texted last night is a 4-byte integer somewhere above 127,000. The difference between a string and an integer array is *encoding*: the agreed-upon mapping between numbers and characters.

Getting encoding wrong has real consequences. In 2003, the Japanese edition of Windows XP had a bug where filenames containing certain characters caused data loss — a character encoding mismatch between the filesystem and the display layer. Today, emoji rendering bugs (the "flag emoji crash" on iOS, certain Telugu character crashes on Apple devices) happen because string processing code assumed fixed-width characters in a variable-width world.

Most string interview problems are array problems in disguise. Once you internalize that a string is just `int[]` with a pretty-print function, the techniques you already know — indexing, slicing, two pointers, hashing — all transfer directly. But strings also have their own traps: immutability in Python means naive concatenation is O(n^2), and UTF-8 means `len(s)` and "number of characters" can be different things.

Today we strip the abstraction and look at strings as they actually are: arrays of bytes, with encoding rules layered on top.

---

## Theory (40 min)

### 1. Strings Are Arrays of Integers (10 min)

At the hardware level, memory stores bytes. A "string" is a contiguous block of bytes where each byte (or group of bytes) represents a character according to some encoding scheme.

```python
s = "Hello"
# In memory (ASCII): [72, 101, 108, 108, 111]
# Each character is one byte. This IS an array.

# Python proves it:
print(ord('H'))      # 72
print(chr(72))       # 'H'
print(list(s))       # ['H', 'e', 'l', 'l', 'o']
print([ord(c) for c in s])  # [72, 101, 108, 108, 111]
```

Everything you know about arrays applies: indexing is O(1), slicing creates copies, you can iterate character by character. The difference is that strings carry encoding metadata so the system knows how to render bytes as glyphs.

### 2. ASCII, Unicode, and UTF-8 — Why UTF-8 Won (10 min)

**ASCII (1963):** 7 bits, 128 characters. Enough for English. 'A' = 65, 'a' = 97, '0' = 48. Simple, fixed-width, and hopelessly limited — no accents, no CJK, no emoji.

**Unicode (1991):** A universal character catalog. Every character ever written gets a "code point" — an integer. 'A' = U+0041, '日' = U+65E5, '🎉' = U+1F389. Unicode defines ~150,000 characters across 154 scripts. But Unicode is a *mapping*, not an encoding — it does not tell you how to store code points in bytes.

**UTF-32:** Store every code point as 4 bytes. Simple and fixed-width, but wasteful — English text uses 4x the memory it needs.

**UTF-16:** Store common characters in 2 bytes, rare ones in 4 bytes (surrogate pairs). Java and JavaScript use this internally. The problem: it is *variable-width*, so you get all the complexity of variable-width encoding without the space savings for ASCII text.

**UTF-8:** Variable-width, 1-4 bytes per character.
```
U+0000 to U+007F:    1 byte  (ASCII compatible!)
U+0080 to U+07FF:    2 bytes (Latin, Greek, Cyrillic, Arabic, Hebrew)
U+0800 to U+FFFF:    3 bytes (CJK, most living scripts)
U+10000 to U+10FFFF: 4 bytes (emoji, historic scripts)
```

**Why UTF-8 won** — three reasons rooted in economics:
1. **Backward compatibility with ASCII.** Every existing ASCII file is already valid UTF-8. Migration cost = zero for English text.
2. **No wasted space for common text.** English uses 1 byte/char, not 4. Web pages are predominantly English or Latin-script, so UTF-8 is typically 1-2x smaller than UTF-32.
3. **No byte-order issues.** UTF-16 and UTF-32 need BOM (byte order mark) to indicate endianness. UTF-8 does not.

Today, UTF-8 encodes ~98% of all web pages. It is the default in Python 3, Go, Rust, and most modern systems.

**The trap for programmers:** In UTF-8, `len(byte_string)` counts bytes, not characters. The string "café" is 5 characters but 6 bytes (the 'é' is 2 bytes). Python 3 abstracts this away — `len("café")` returns 4 (character count) — but when you write to files, send over networks, or call C libraries, the byte count matters.

### 3. String Immutability — Why `+=` in a Loop is O(n^2) (10 min)

In Python (and Java, Go, JavaScript), strings are **immutable**. Once created, their bytes cannot be changed. When you "modify" a string, you actually create a new one.

```python
s = "hello"
s[0] = "H"  # TypeError: 'str' object does not support item assignment

# This works, but creates a NEW string:
s = "H" + s[1:]  # Allocates new memory, copies all characters
```

This has devastating performance implications for the naive pattern:

```python
# BAD: O(n^2) total work
result = ""
for word in words:          # n words
    result += word + " "    # Each += copies ALL of result so far

# Iteration 1: copies 1 word
# Iteration 2: copies 2 words
# Iteration 3: copies 3 words
# ...
# Total copies: 1 + 2 + 3 + ... + n = n(n+1)/2 = O(n^2)
```

```python
# GOOD: O(n) total work
result = " ".join(words)    # Single allocation, single pass
```

This is not academic — production systems have been brought down by string concatenation in loops. If you are building an HTML page by appending tags in a loop, or constructing a CSV line by concatenating fields, you must use `join()` or a list buffer.

**String interning:** Python caches small strings and reuses them. String literals and identifiers are often "interned" — stored once and shared.

```python
a = "hello"
b = "hello"
print(a is b)  # True — same object in memory (interned)

a = "hello world!"
b = "hello world!"
print(a is b)  # May be False — longer strings may not be interned
```

This is an optimization, not a guarantee. Never rely on `is` for string comparison — always use `==`.

### 4. Common String Operations and Their Complexity (10 min)

| Operation | Complexity | Why |
|-----------|-----------|-----|
| `s[i]` | O(1) | Array index (Python handles UTF-8 internally) |
| `len(s)` | O(1) | Stored as attribute, not computed |
| `s + t` | O(len(s) + len(t)) | Must copy both strings |
| `s.find(t)` / `t in s` | O(n*m) worst, often better | Naive: check each position. CPython uses Boyer-Moore-Horspool |
| `s.replace(a, b)` | O(n) | Single pass with new allocation |
| `s.split()` | O(n) | Single pass |
| `"".join(list)` | O(total chars) | Single allocation + copy |
| `s[::-1]` | O(n) | Creates reversed copy |
| `s == t` | O(min(n,m)) | Character-by-character until mismatch |

The key insight: because strings are immutable, every "modification" is actually a creation. Think about where you are allocating.

---

## Practice (20 min)

1. Run `string_fundamentals.py` and observe:
   - How Python strings map to integer arrays
   - The difference between byte length and character length for Unicode
   - The O(n^2) vs O(n) concatenation benchmark
   - String interning behavior

2. Open `practice.py` and complete the TODO exercises covering:
   - Manual character encoding and decoding
   - Efficient string building
   - String-as-array pattern matching

---

## Daily Project

The main demonstrations are in `string_fundamentals.py`. Study the output, then:

1. Predict whether `s += char` or `parts.append(char); "".join(parts)` will be faster for building a 100,000-character string. Run the benchmark to verify.
2. Find a Unicode string where `len(s)` differs from `len(s.encode('utf-8'))`. Explain exactly why the byte counts differ.
3. Implement a function that checks if two strings are anagrams in O(n) time by treating strings as arrays and using character frequency counting.

---

## Checkpoint Questions

1. **A string is "immutable" in Python. What does this mean at the memory level?** When you do `s = s + "x"`, how many string objects exist in memory (before garbage collection)?

2. **Why did UTF-8 win over UTF-16 and UTF-32?** Give three concrete reasons rooted in backward compatibility, space efficiency, and byte ordering.

3. **Your colleague writes a function that builds a SQL query by concatenating strings in a loop: `query += f"OR id = {x} "` for 50,000 IDs. What is the time complexity? How would you fix it?** What is the fixed version's complexity?

4. **`ord('A')` returns 65. `ord('é')` returns 233. But `'é'.encode('utf-8')` returns `b'\xc3\xa9'` (2 bytes). Explain the discrepancy.** What is the difference between a Unicode code point and its UTF-8 encoding?

5. **You are solving a string problem on an array of characters. Should you convert the string to a list first, or work with the string directly?** When does each approach make sense, and what are the memory trade-offs?
