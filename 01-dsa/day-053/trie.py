"""
Day 53: Trie (Prefix Tree) — Character-by-Character Key Storage
================================================================
A trie distributes each key across tree edges, one character per edge.
Every node represents a prefix of all keys below it.

    insert("cat")  → root → c → a → t[end]
    insert("car")  → root → c → a → r[end]   (shares "ca" prefix)
    search("cat")  → walk c→a→t, check end marker → True
    starts_with("ca") → walk c→a, return all below

Why dict-based children?
    - Flexible alphabet (Unicode, binary, DNA, etc.)
    - Space-efficient for sparse nodes (most nodes have 1-2 children)
    - Array-based is faster for known small alphabets (lowercase a-z)

Run: python trie.py
"""


# ─── TrieNode ───────────────────────────────────────────────────────

class TrieNode:
    """A single node in the trie.

    children: dict mapping character → child TrieNode
    is_end:   True if this node marks the end of a stored key
    count:    how many keys pass through this node (for prefix counting)
    """
    __slots__ = ('children', 'is_end', 'count', 'value')

    def __init__(self):
        self.children = {}
        self.is_end = False
        self.count = 0       # Number of keys passing through this node
        self.value = None    # Optional associated value


# ─── Trie ───────────────────────────────────────────────────────────

class Trie:
    """
    A prefix tree supporting insert, search, prefix query, delete,
    autocomplete, and longest common prefix.
    """

    def __init__(self):
        self.root = TrieNode()
        self._size = 0

    def __len__(self):
        return self._size

    # ── Insert ──────────────────────────────────────────────────────

    def insert(self, key, value=None):
        """
        Insert a key into the trie. O(k) where k = len(key).
        Optionally associate a value with the key.
        """
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.count += 1
        if not node.is_end:
            self._size += 1
        node.is_end = True
        node.value = value

    # ── Search ──────────────────────────────────────────────────────

    def search(self, key):
        """
        Return True if key exists in the trie. O(k).
        """
        node = self._find_node(key)
        return node is not None and node.is_end

    def get(self, key):
        """Return the value associated with key, or None."""
        node = self._find_node(key)
        if node and node.is_end:
            return node.value
        return None

    # ── Prefix Operations ───────────────────────────────────────────

    def starts_with(self, prefix):
        """Return True if any key starts with the given prefix. O(p)."""
        return self._find_node(prefix) is not None

    def count_prefix(self, prefix):
        """Return the number of keys that start with prefix. O(p)."""
        node = self._find_node(prefix)
        return node.count if node else 0

    def keys_with_prefix(self, prefix):
        """Return all keys that start with prefix. O(p + total_chars_below)."""
        node = self._find_node(prefix)
        if node is None:
            return []
        results = []
        self._collect(node, list(prefix), results)
        return results

    def autocomplete(self, prefix, limit=10):
        """Return up to `limit` keys that start with prefix."""
        node = self._find_node(prefix)
        if node is None:
            return []
        results = []
        self._collect(node, list(prefix), results, limit)
        return results

    # ── Delete ──────────────────────────────────────────────────────

    def delete(self, key):
        """
        Delete a key from the trie. O(k).
        Returns True if the key was found and deleted.

        Strategy: walk to the end, unmark is_end, then clean up
        nodes that are no longer part of any key.
        """
        # First verify the key exists
        node = self._find_node(key)
        if node is None or not node.is_end:
            return False

        node.is_end = False
        node.value = None
        self._size -= 1

        # Decrement counts and clean up empty branches
        self._cleanup(self.root, key, 0)
        return True

    # ── Longest Common Prefix ───────────────────────────────────────

    def longest_common_prefix(self):
        """
        Find the longest prefix shared by ALL keys in the trie.
        Walk from root while each node has exactly one child and isn't an end.
        """
        prefix = []
        node = self.root
        while len(node.children) == 1 and not node.is_end:
            char = next(iter(node.children))
            prefix.append(char)
            node = node.children[char]
        return ''.join(prefix)

    # ── All Keys ────────────────────────────────────────────────────

    def all_keys(self):
        """Return all keys in the trie (sorted by default due to traversal)."""
        results = []
        self._collect(self.root, [], results)
        return results

    # ── Internal Helpers ────────────────────────────────────────────

    def _find_node(self, prefix):
        """Walk the trie for the given prefix. Return the node or None."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _collect(self, node, path, results, limit=None):
        """DFS collect all keys below node."""
        if limit and len(results) >= limit:
            return
        if node.is_end:
            results.append(''.join(path))
        for char in sorted(node.children):
            if limit and len(results) >= limit:
                return
            path.append(char)
            self._collect(node.children[char], path, results, limit)
            path.pop()

    def _cleanup(self, node, key, depth):
        """Decrement counts and remove empty nodes after deletion."""
        if depth == len(key):
            return

        char = key[depth]
        child = node.children[char]
        child.count -= 1

        self._cleanup(child, key, depth + 1)

        # Remove child if it has no keys passing through it
        if child.count == 0:
            del node.children[char]


# ─── Visualization ──────────────────────────────────────────────────

def visualize_trie(trie, max_depth=10):
    """Print the trie structure."""
    def _print(node, prefix, indent):
        if indent // 2 > max_depth:
            return
        marker = " ★" if node.is_end else ""
        count_str = f" ({node.count})" if node.count > 0 else ""
        if prefix:
            print(f"{'│ ' * (indent // 2 - 1)}├─ {prefix}{marker}{count_str}")
        for char in sorted(node.children):
            _print(node.children[char], char, indent + 2)

    print("(root)")
    for char in sorted(trie.root.children):
        _print(trie.root.children[char], char, 2)


# ─── Demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Day 53: Trie — Prefix Tree")
    print("=" * 60)

    t = Trie()

    # Insert words
    words = ["apple", "app", "application", "apt", "bat", "bar", "batch", "bath"]
    print(f"\nInserting: {words}")
    for w in words:
        t.insert(w)

    visualize_trie(t)

    # Search
    print(f"\n--- Search ---")
    for w in ["app", "apple", "ap", "cat"]:
        print(f"  search('{w}') = {t.search(w)}")

    # Prefix operations
    print(f"\n--- Prefix Operations ---")
    for p in ["app", "ba", "c"]:
        print(f"  starts_with('{p}') = {t.starts_with(p)}")
        print(f"  count_prefix('{p}') = {t.count_prefix(p)}")
        print(f"  keys_with_prefix('{p}') = {t.keys_with_prefix(p)}")

    # Autocomplete
    print(f"\n--- Autocomplete ---")
    print(f"  autocomplete('app', 3) = {t.autocomplete('app', 3)}")
    print(f"  autocomplete('ba', 2) = {t.autocomplete('ba', 2)}")

    # Longest common prefix
    t2 = Trie()
    for w in ["flower", "flow", "flight"]:
        t2.insert(w)
    print(f"\n--- Longest Common Prefix ---")
    print(f"  Words: ['flower', 'flow', 'flight']")
    print(f"  LCP: '{t2.longest_common_prefix()}'")

    # Delete
    print(f"\n--- Delete ---")
    print(f"  Before delete: {t.all_keys()}")
    t.delete("app")
    print(f"  After delete('app'): {t.all_keys()}")
    print(f"  search('app') = {t.search('app')}")
    print(f"  search('apple') = {t.search('apple')}")

    print(f"\n  Total keys: {len(t)}")
    print("\n✓ All demos complete")
