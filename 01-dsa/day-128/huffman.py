"""
Day 128: Huffman Coding — Optimal Prefix Codes (from scratch)

No heapq import here for the core build — we implement a tiny binary heap
from scratch to keep the data-structure visible. Standard heapq is allowed
per project rules; we use it elsewhere where convenient.

Time:  O(n log n)   Space: O(n) for the tree
"""

from math import log2


# ---------------------------------------------------------------------------
# Tiny min-heap from scratch (illustration; heapq is fine in stdlib)
# ---------------------------------------------------------------------------

class MinHeap:
    """Min-heap on tuples; comparison by first element (then second for tie-break)."""

    def __init__(self):
        self.a = []

    def __len__(self):
        return len(self.a)

    def push(self, item):
        self.a.append(item)
        self._sift_up(len(self.a) - 1)

    def pop(self):
        top = self.a[0]
        last = self.a.pop()
        if self.a:
            self.a[0] = last
            self._sift_down(0)
        return top

    def _sift_up(self, i):
        while i > 0:
            p = (i - 1) // 2
            if self.a[i] < self.a[p]:
                self.a[i], self.a[p] = self.a[p], self.a[i]
                i = p
            else:
                return

    def _sift_down(self, i):
        n = len(self.a)
        while True:
            l, r = 2 * i + 1, 2 * i + 2
            best = i
            if l < n and self.a[l] < self.a[best]:
                best = l
            if r < n and self.a[r] < self.a[best]:
                best = r
            if best == i:
                return
            self.a[i], self.a[best] = self.a[best], self.a[i]
            i = best


# ---------------------------------------------------------------------------
# Huffman tree node
# ---------------------------------------------------------------------------

class Node:
    __slots__ = ("freq", "sym", "left", "right")

    def __init__(self, freq, sym=None, left=None, right=None):
        self.freq = freq
        self.sym = sym      # None for internal nodes
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None


# ---------------------------------------------------------------------------
# Frequency table
# ---------------------------------------------------------------------------

def frequencies(data):
    """Return dict: symbol -> count."""
    freq = {}
    for c in data:
        freq[c] = freq.get(c, 0) + 1
    return freq


# ---------------------------------------------------------------------------
# Build Huffman tree
# ---------------------------------------------------------------------------

def build_tree(freq):
    """
    freq: dict symbol -> count
    Returns: root Node, or None if freq is empty.
    Single-symbol corner case: returns a parent with that symbol as left child,
    so the code length is 1 (not 0).
    """
    if not freq:
        return None

    heap = MinHeap()
    # Tie-breaker: a monotonic counter so Node objects never get compared directly.
    counter = 0
    for sym, f in freq.items():
        heap.push((f, counter, Node(f, sym)))
        counter += 1

    # Edge case: single symbol → force code length 1
    if len(heap) == 1:
        _, _, only = heap.pop()
        return Node(only.freq, None, only, None)

    while len(heap) > 1:
        f1, _, n1 = heap.pop()
        f2, _, n2 = heap.pop()
        merged = Node(f1 + f2, None, n1, n2)
        heap.push((merged.freq, counter, merged))
        counter += 1

    _, _, root = heap.pop()
    return root


# ---------------------------------------------------------------------------
# Generate codes
# ---------------------------------------------------------------------------

def build_codes(root):
    """
    Walk the tree, assign codes. Returns dict: symbol -> code-string of '0'/'1'.
    Single-symbol corner: the only symbol gets '0'.
    """
    if root is None:
        return {}
    codes = {}

    def walk(node, prefix):
        if node is None:
            return
        if node.is_leaf():
            codes[node.sym] = prefix or "0"
            return
        walk(node.left, prefix + "0")
        walk(node.right, prefix + "1")

    walk(root, "")
    return codes


# ---------------------------------------------------------------------------
# Encode / Decode
# ---------------------------------------------------------------------------

def encode(data, codes):
    """Concatenate codes for each symbol. Returns a bitstring of '0'/'1'."""
    return "".join(codes[c] for c in data)


def decode(bits, root):
    """Walk the tree bit by bit. Returns the original sequence as a list."""
    if root is None:
        return []
    # Single-leaf tree wrapped above as Node(_, None, leaf, None): treat any
    # bit as that one symbol.
    if root.left is not None and root.left.is_leaf() and root.right is None:
        return [root.left.sym] * len(bits)

    out = []
    node = root
    for b in bits:
        node = node.left if b == "0" else node.right
        if node.is_leaf():
            out.append(node.sym)
            node = root
    return out


# ---------------------------------------------------------------------------
# Analysis: entropy + average code length
# ---------------------------------------------------------------------------

def entropy(freq):
    """Shannon entropy in bits/symbol from a frequency dict."""
    total = sum(freq.values())
    if total == 0:
        return 0.0
    H = 0.0
    for f in freq.values():
        if f == 0:
            continue
        p = f / total
        H -= p * log2(p)
    return H


def average_code_length(freq, codes):
    """Σ p(c) * len(code(c))."""
    total = sum(freq.values())
    if total == 0:
        return 0.0
    L = 0.0
    for sym, f in freq.items():
        L += (f / total) * len(codes[sym])
    return L


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("=" * 65)
    print("Day 128 — Huffman Coding")
    print("=" * 65)

    text = "abracadabra"
    print(f"\n--- Encoding '{text}' ---")
    freq = frequencies(text)
    print(f"Frequencies: {freq}")
    root = build_tree(freq)
    codes = build_codes(root)
    print(f"Codes: {codes}")
    bits = encode(text, codes)
    print(f"Encoded: {bits}  ({len(bits)} bits)")
    print(f"Fixed (8 bits/char): {len(text) * 8} bits  → ratio {len(bits)/(len(text)*8):.2f}")
    decoded = "".join(decode(bits, root))
    print(f"Decoded: '{decoded}'  match={decoded == text}")
    print(f"Entropy:  {entropy(freq):.3f} bits/sym")
    print(f"Huffman:  {average_code_length(freq, codes):.3f} bits/sym")

    print("\n--- The classic CLRS example ---")
    freq = {'a': 45, 'b': 13, 'c': 12, 'd': 16, 'e': 9, 'f': 5}
    root = build_tree(freq)
    codes = build_codes(root)
    for sym in sorted(codes):
        print(f"  {sym!r}: {codes[sym]:>5}  (freq {freq[sym]})")
    print(f"Average length: {average_code_length(freq, codes):.3f} bits/sym")
    print(f"Entropy:        {entropy(freq):.3f} bits/sym")
    print(f"Within 1 bit?   {average_code_length(freq, codes) < entropy(freq) + 1}")

    print("\n--- Single symbol corner case ---")
    freq = {'a': 100}
    root = build_tree(freq)
    codes = build_codes(root)
    print(f"Codes: {codes}  (must have length >= 1)")
    bits = encode("aaaa", codes)
    print(f"Encoded 'aaaa': {bits}")
    print(f"Decoded: {''.join(decode(bits, root))}")

    print("\n--- Powers of 2 → entropy is tight ---")
    # Frequencies 1, 1, 2, 4 → probabilities 1/8, 1/8, 1/4, 1/2 → entropy 1.75
    # Huffman should hit 1.75 exactly.
    freq = {'w': 1, 'x': 1, 'y': 2, 'z': 4}
    root = build_tree(freq)
    codes = build_codes(root)
    print(f"Codes: {codes}")
    print(f"Average length: {average_code_length(freq, codes):.3f}  Entropy: {entropy(freq):.3f}")
    print("Equal because all probabilities are 2^(-k).")

    print("\n" + "=" * 65)
    print("Huffman: greedy on a min-heap. Within 1 bit of Shannon entropy.")


if __name__ == "__main__":
    demo()
