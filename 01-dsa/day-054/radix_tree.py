"""
Day 54: Radix Tree (Patricia Trie) — Compressed Prefix Tree
=============================================================
Compress single-child chains into multi-character edge labels.
Drastically reduces node count while preserving O(k) operations.

Structure:
    Each node has a dict of (edge_label → child_node).
    Edge labels are strings, not single characters.
    Branching only occurs where keys actually diverge.

Run: python radix_tree.py
"""


# ─── RadixNode ──────────────────────────────────────────────────────

class RadixNode:
    __slots__ = ('children', 'is_end', 'value')

    def __init__(self):
        self.children = {}  # edge_label (str) → RadixNode
        self.is_end = False
        self.value = None


# ─── RadixTree ──────────────────────────────────────────────────────

class RadixTree:
    """
    Compressed trie where edges store string labels.

    Key operations:
        insert(key): Add key, splitting edges as needed.
        search(key): Check if exact key exists.
        delete(key): Remove key, merging edges if possible.
        keys_with_prefix(prefix): All keys starting with prefix.
    """

    def __init__(self):
        self.root = RadixNode()
        self._size = 0

    def __len__(self):
        return self._size

    def insert(self, key, value=None):
        """
        Insert a key, splitting edges where the new key diverges.

        Three cases at each node:
        1. No matching edge → create new edge for remaining key
        2. Edge fully matches a prefix of remaining key → follow edge, continue
        3. Edge partially matches → split edge at divergence point
        """
        node = self.root
        i = 0  # Position in key

        while i < len(key):
            # Find an edge whose first character matches key[i]
            found = False
            for label, child in node.children.items():
                if label[0] == key[i]:
                    # Found matching edge — how far does it match?
                    match_len = self._common_prefix_len(label, key[i:])

                    if match_len == len(label):
                        # Full edge match — continue down
                        node = child
                        i += match_len
                        found = True
                        break
                    else:
                        # Partial match — split the edge
                        # Before: node --[label]--> child
                        # After:  node --[label[:match]]--> mid --[label[match:]]--> child
                        #                                       --[key[i+match:]]--> new_leaf
                        mid = RadixNode()
                        remaining_label = label[match_len:]
                        remaining_key = key[i + match_len:]

                        # Rewire: remove old edge, add edge to mid
                        del node.children[label]
                        node.children[label[:match_len]] = mid

                        # Mid → old child (with remaining label)
                        mid.children[remaining_label] = child

                        # Mid → new leaf (with remaining key)
                        if remaining_key:
                            leaf = RadixNode()
                            leaf.is_end = True
                            leaf.value = value
                            mid.children[remaining_key] = leaf
                        else:
                            mid.is_end = True
                            mid.value = value

                        self._size += 1
                        return

                    break  # Only one edge can match

            if not found:
                # No matching edge — create new edge for remaining key
                leaf = RadixNode()
                leaf.is_end = True
                leaf.value = value
                node.children[key[i:]] = leaf
                self._size += 1
                return

        # Exhausted key — mark current node as end
        if not node.is_end:
            self._size += 1
        node.is_end = True
        node.value = value

    def search(self, key):
        """Return True if key exists in the tree."""
        node = self._find_node(key)
        return node is not None and node.is_end

    def get(self, key):
        """Return value associated with key, or None."""
        node = self._find_node(key)
        if node and node.is_end:
            return node.value
        return None

    def starts_with(self, prefix):
        """Return True if any key starts with prefix."""
        node, _ = self._find_prefix_node(prefix)
        return node is not None

    def keys_with_prefix(self, prefix):
        """Return all keys starting with prefix."""
        node, consumed = self._find_prefix_node(prefix)
        if node is None:
            return []
        results = []
        self._collect(node, list(prefix[:consumed]), results)
        # If we consumed more than the prefix (partial edge match),
        # we need to adjust
        return results

    def delete(self, key):
        """
        Delete key. After deletion, merge single-child non-end nodes
        with their child to maintain compression.
        """
        # Find the node
        path = []  # [(parent_node, edge_label, child_node), ...]
        node = self.root
        i = 0

        while i < len(key):
            found = False
            for label, child in node.children.items():
                if key[i:i + len(label)] == label:
                    path.append((node, label, child))
                    node = child
                    i += len(label)
                    found = True
                    break
            if not found:
                return False

        if not node.is_end:
            return False

        node.is_end = False
        node.value = None
        self._size -= 1

        # Clean up: remove leaf nodes, merge single-child chains
        self._cleanup(path)
        return True

    def all_keys(self):
        """Return all keys in sorted order."""
        results = []
        self._collect(self.root, [], results)
        return results

    def node_count(self):
        """Count total nodes (for memory comparison with basic trie)."""
        count = [0]
        def walk(node):
            count[0] += 1
            for child in node.children.values():
                walk(child)
        walk(self.root)
        return count[0]

    # ── Internal Helpers ────────────────────────────────────────────

    def _find_node(self, key):
        """Walk tree for exact key match."""
        node = self.root
        i = 0
        while i < len(key):
            found = False
            for label, child in node.children.items():
                if key[i:i + len(label)] == label:
                    node = child
                    i += len(label)
                    found = True
                    break
            if not found:
                return None
        return node

    def _find_prefix_node(self, prefix):
        """Walk tree for prefix. Return (node, chars_consumed)."""
        node = self.root
        i = 0
        while i < len(prefix):
            found = False
            for label, child in node.children.items():
                plen = min(len(label), len(prefix) - i)
                if label[:plen] == prefix[i:i + plen]:
                    if plen < len(label):
                        # Prefix ends mid-edge — the child node covers it
                        return child, i + len(label)
                    node = child
                    i += len(label)
                    found = True
                    break
            if not found:
                return None, i
        return node, i

    def _collect(self, node, path, results):
        if node.is_end:
            results.append(''.join(path))
        for label in sorted(node.children):
            path.append(label)
            self._collect(node.children[label], path, results)
            path.pop()

    def _cleanup(self, path):
        """Remove empty leaves and merge single-child chains."""
        for parent, label, child in reversed(path):
            if not child.is_end and not child.children:
                # Empty leaf — remove
                del parent.children[label]
            elif not child.is_end and len(child.children) == 1:
                # Single child, not an end — merge with child
                child_label, grandchild = next(iter(child.children.items()))
                del parent.children[label]
                parent.children[label + child_label] = grandchild

    @staticmethod
    def _common_prefix_len(a, b):
        """Return length of common prefix between two strings."""
        i = 0
        while i < len(a) and i < len(b) and a[i] == b[i]:
            i += 1
        return i


# ─── Demo ───────────────────────────────────────────────────────────

def visualize(tree):
    def _print(node, indent=""):
        for label in sorted(node.children):
            child = node.children[label]
            marker = " ★" if child.is_end else ""
            print(f"{indent}├── '{label}'{marker}")
            _print(child, indent + "│   ")
    print("(root)")
    _print(tree.root)


if __name__ == "__main__":
    print("=" * 60)
    print("Day 54: Radix Tree — Compressed Trie")
    print("=" * 60)

    rt = RadixTree()
    words = ["romane", "romanus", "romulus", "rubens", "ruber", "rubicon", "rubicundus"]

    print(f"\nInserting: {words}")
    for w in words:
        rt.insert(w)

    print(f"\nStructure ({rt.node_count()} nodes for {len(words)} keys):")
    visualize(rt)

    print(f"\n--- Search ---")
    for w in ["romane", "roman", "rubicon", "ruby"]:
        print(f"  search('{w}') = {rt.search(w)}")

    print(f"\n--- Prefix ---")
    print(f"  keys_with_prefix('rom') = {rt.keys_with_prefix('rom')}")
    print(f"  keys_with_prefix('rub') = {rt.keys_with_prefix('rub')}")

    # Memory comparison
    from trie import Trie
    basic = Trie()
    for w in words:
        basic.insert(w)

    basic_nodes = [0]
    def count_trie(node):
        basic_nodes[0] += 1
        for c in node.children.values():
            count_trie(c)
    count_trie(basic.root)

    print(f"\n--- Memory Comparison ---")
    print(f"  Basic trie: {basic_nodes[0]} nodes")
    print(f"  Radix tree: {rt.node_count()} nodes")
    print(f"  Compression ratio: {basic_nodes[0] / rt.node_count():.1f}x")

    print(f"\n--- Delete ---")
    rt.delete("romanus")
    print(f"  After delete('romanus'): {rt.all_keys()}")
    visualize(rt)

    print("\n✓ All demos complete")
