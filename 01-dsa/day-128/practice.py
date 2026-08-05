"""
Day 128 Practice: Huffman Coding

6 exercises covering frequency, tree construction, codes, encode/decode,
and the entropy bound. Implement TODOs, then: python practice.py
"""

from math import log2
import heapq


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# Node class shared across exercises
class _Node:
    __slots__ = ("freq", "sym", "left", "right")

    def __init__(self, freq, sym=None, left=None, right=None):
        self.freq = freq
        self.sym = sym
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None


# ===================================================================
# Exercise 1: Frequency Table
# ===================================================================

def char_frequencies(text):
    """
    text: a string
    Returns: dict char -> count (only chars that appear)
    """
    # TODO: implement
    pass


def _sol_char_frequencies(text):
    f = {}
    for c in text:
        f[c] = f.get(c, 0) + 1
    return f


# ===================================================================
# Exercise 2: Build Huffman Tree
# ===================================================================
# Build the tree. Use a heap; tie-break by a counter so internal nodes
# never compare directly.

def build_huffman(freq):
    """
    freq: dict symbol -> positive int count
    Returns: root _Node (or None if freq empty). For single-symbol input,
             must return a tree whose only leaf has depth 1 (parent → leaf left).
    """
    # TODO: implement
    pass


def _sol_build_huffman(freq):
    if not freq:
        return None
    heap = []
    counter = 0
    for s, f in freq.items():
        heapq.heappush(heap, (f, counter, _Node(f, s)))
        counter += 1
    if len(heap) == 1:
        _, _, only = heapq.heappop(heap)
        return _Node(only.freq, None, only, None)
    while len(heap) > 1:
        f1, _, n1 = heapq.heappop(heap)
        f2, _, n2 = heapq.heappop(heap)
        m = _Node(f1 + f2, None, n1, n2)
        heapq.heappush(heap, (m.freq, counter, m))
        counter += 1
    _, _, root = heap[0]
    return root


# ===================================================================
# Exercise 3: Extract Codes
# ===================================================================

def huffman_codes(root):
    """
    root: root of a Huffman tree (from build_huffman)
    Returns: dict symbol -> code-string of '0'/'1'.
             Empty dict if root is None.
             Single-leaf wrapped tree → that symbol's code is '0'.
    """
    # TODO: implement
    pass


def _sol_huffman_codes(root):
    if root is None:
        return {}
    out = {}

    def walk(n, p):
        if n is None:
            return
        if n.is_leaf():
            out[n.sym] = p or "0"
            return
        walk(n.left, p + "0")
        walk(n.right, p + "1")

    walk(root, "")
    return out


# ===================================================================
# Exercise 4: Encode and Decode (round-trip)
# ===================================================================

def encode_decode(text):
    """
    text: a non-empty string
    Build a Huffman tree from `text`, encode it, decode it, and verify
    round-trip.
    Returns: tuple (encoded_bitstring, decoded_string)
    """
    # TODO: implement using the helpers above
    pass


def _sol_encode_decode(text):
    freq = _sol_char_frequencies(text)
    root = _sol_build_huffman(freq)
    codes = _sol_huffman_codes(root)
    bits = "".join(codes[c] for c in text)

    # decode
    if root.left is not None and root.left.is_leaf() and root.right is None:
        return bits, root.left.sym * len(bits)
    out = []
    node = root
    for b in bits:
        node = node.left if b == "0" else node.right
        if node.is_leaf():
            out.append(node.sym)
            node = root
    return bits, "".join(out)


# ===================================================================
# Exercise 5: Average Code Length vs Entropy
# ===================================================================

def avg_length_and_entropy(freq):
    """
    freq: dict symbol -> count
    Returns: (avg_length, entropy) as floats.
             avg_length is the Huffman-tree weighted code length.
             entropy is the Shannon entropy in bits/symbol.
    """
    # TODO: implement
    pass


def _sol_avg_length_and_entropy(freq):
    if not freq:
        return (0.0, 0.0)
    total = sum(freq.values())
    root = _sol_build_huffman(freq)
    codes = _sol_huffman_codes(root)
    avg = sum((f / total) * len(codes[s]) for s, f in freq.items())
    H = -sum((f / total) * log2(f / total) for f in freq.values() if f > 0)
    return (avg, H)


# ===================================================================
# Exercise 6: Decode From Codebook (no tree)
# ===================================================================
# Given a codebook (symbol -> bitstring) and a bitstring, decode it.
# Use the prefix-free property: longest-prefix match consumed greedily.

def decode_from_codebook(codes, bits):
    """
    codes: dict symbol -> bitstring (prefix-free)
    bits: a string of '0'/'1'
    Returns: decoded string (concatenation of decoded symbols)
    """
    # TODO: implement
    pass


def _sol_decode_from_codebook(codes, bits):
    # Build reverse lookup; greedy longest-prefix match (correct for prefix-free).
    rev = {v: k for k, v in codes.items()}
    out = []
    buf = ""
    for b in bits:
        buf += b
        if buf in rev:
            out.append(rev[buf])
            buf = ""
    return "".join(str(x) for x in out)


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    expected: {expected}")
            print(f"    got:      {got}")
            failed += 1

    # --- Exercise 1 ---
    print("Exercise 1: Char Frequencies")
    check("abracadabra",
          try_or_sol("char_frequencies", "abracadabra"),
          {"a": 5, "b": 2, "r": 2, "c": 1, "d": 1})
    check("empty", try_or_sol("char_frequencies", ""), {})
    check("one symbol", try_or_sol("char_frequencies", "aaaa"), {"a": 4})

    # --- Exercise 2 ---
    print("\nExercise 2: Build Huffman Tree")
    root = try_or_sol("build_huffman", {"a": 5, "b": 2, "r": 2, "c": 1, "d": 1})
    check("root not None", root is not None, True)
    check("root freq == 11", root.freq, 11)

    root_single = try_or_sol("build_huffman", {"a": 100})
    check("single-symbol depth >= 1",
          root_single is not None and root_single.left is not None and root_single.left.is_leaf(),
          True)

    # --- Exercise 3 ---
    print("\nExercise 3: Extract Codes")
    freq = {"a": 5, "b": 2, "r": 2, "c": 1, "d": 1}
    root = _sol_build_huffman(freq)
    codes = try_or_sol("huffman_codes", root)
    # Most frequent (a) should get the shortest code
    a_len = len(codes["a"])
    check("'a' has shortest code",
          all(a_len <= len(v) for v in codes.values()), True)
    check("prefix-free",
          all(not codes[x].startswith(codes[y]) or x == y
              for x in codes for y in codes),
          True)

    # Single-symbol case
    root_s = _sol_build_huffman({"z": 7})
    codes_s = try_or_sol("huffman_codes", root_s)
    check("single symbol gets '0'", codes_s.get("z"), "0")

    # --- Exercise 4 ---
    print("\nExercise 4: Encode + Decode round-trip")
    bits, decoded = try_or_sol("encode_decode", "abracadabra")
    check("decoded == original", decoded, "abracadabra")
    check("encoded is bitstring",
          all(c in "01" for c in bits) and len(bits) > 0, True)
    # Single-symbol round-trip
    bits2, decoded2 = try_or_sol("encode_decode", "aaaa")
    check("single-symbol round-trip", decoded2, "aaaa")

    # --- Exercise 5 ---
    print("\nExercise 5: Avg Length vs Entropy")
    # Powers-of-two probabilities → tight bound
    avg, H = try_or_sol("avg_length_and_entropy",
                       {"w": 1, "x": 1, "y": 2, "z": 4})
    check("powers of 2 → avg == entropy", abs(avg - H) < 1e-9, True)
    check("avg == 1.75", abs(avg - 1.75) < 1e-9, True)

    # Generic — Huffman within 1 bit of entropy
    avg2, H2 = try_or_sol("avg_length_and_entropy",
                         {"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5})
    check("Huffman within 1 bit of entropy", avg2 < H2 + 1, True)
    check("Huffman >= entropy", avg2 >= H2 - 1e-9, True)

    # --- Exercise 6 ---
    print("\nExercise 6: Decode From Codebook")
    codes = {"a": "0", "b": "10", "c": "11"}
    check("decode abc", try_or_sol("decode_from_codebook", codes, "01011"), "abc")
    check("decode aaa", try_or_sol("decode_from_codebook", codes, "000"), "aaa")
    check("decode empty", try_or_sol("decode_from_codebook", codes, ""), "")

    # --- Summary ---
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
