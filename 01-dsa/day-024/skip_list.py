"""
Skip List — Probabilistic Alternative to Balanced Trees

WHY skip lists exist:
A sorted linked list gives O(n) search. Balanced BSTs give O(log n) but require
complex rotations. Skip lists achieve O(log n) expected time using randomness
instead of deterministic rebalancing — dramatically simpler code with the same
practical performance. Redis uses this exact data structure for sorted sets.

HOW it works:
- Multiple layers of linked lists stacked on top of each other.
- Level 0 is a complete sorted linked list.
- Each higher level is a random subset of the level below (~50% with p=0.5).
- Search starts at the top level and drops down — like an express train system.

COMPLEXITY (expected, with p=0.5):
- Search: O(log n) — traverse ~2 nodes per level, ~log2(n) levels
- Insert: O(log n) — search + O(1) pointer updates per level
- Delete: O(log n) — search + O(1) pointer updates per level
- Space:  O(n)     — each node has ~2 pointers on average (geometric sum)
"""

import random


class Node:
    """A skip list node with forward pointers for each level it participates in.

    WHY an array of forward pointers?
    A node at level k appears in levels 0, 1, ..., k. At each level it needs
    a 'next' pointer to the next node at that level. So we store an array of
    size (level + 1) forward pointers.
    """

    __slots__ = ('key', 'value', 'forward')

    def __init__(self, key, value, level):
        self.key = key
        self.value = value
        # forward[i] points to the next node at level i
        # Initialize all to None (will be wired up during insert)
        self.forward = [None] * (level + 1)

    def __repr__(self):
        return f"Node(key={self.key}, value={self.value}, levels={len(self.forward)})"


class SkipList:
    """
    A skip list supporting insert, search, and delete.

    Parameters:
        max_level: Maximum number of levels (typically log2 of expected n).
                   16 levels handles up to ~65,536 elements well with p=0.5.
        p:         Promotion probability. Each node at level k is promoted to
                   level k+1 with probability p. p=0.5 gives the best time
                   complexity; p=0.25 (Redis's choice) saves memory.

    WHY max_level matters:
    The expected max level for n elements is log_{1/p}(n). Setting max_level
    too low caps performance; too high wastes a tiny bit of space in the header.
    16 with p=0.5 covers up to 2^16 = 65,536 elements. 32 covers 4 billion.
    """

    def __init__(self, max_level=16, p=0.5):
        self.max_level = max_level
        self.p = p
        # Current highest level in use (0-indexed). Starts at 0.
        self.level = 0
        # Header node acts as the sentinel — never holds real data.
        # It has max_level + 1 forward pointers so it can connect to any level.
        self.header = Node(None, None, max_level)
        self._size = 0

    def __len__(self):
        return self._size

    def _random_level(self):
        """Generate a random level using geometric distribution.

        WHY geometric distribution?
        We want ~n nodes at level 0, ~n*p at level 1, ~n*p^2 at level 2, etc.
        This mimics a balanced tree structure where each level halves the nodes.
        The coin-flip loop naturally produces this distribution:
        - P(level >= 0) = 1
        - P(level >= 1) = p
        - P(level >= k) = p^k

        With p=0.5, this is literally flipping a fair coin until tails.
        """
        lvl = 0
        # Each iteration: "flip a coin" — promote with probability p
        while random.random() < self.p and lvl < self.max_level:
            lvl += 1
        return lvl

    def search(self, key):
        """Search for a key, return its value or None.

        Algorithm:
        1. Start at the header's highest level.
        2. At each level, move forward while next key < target.
        3. Drop down one level.
        4. At level 0, check if we've found the key.

        WHY this is O(log n) expected:
        At each level, we skip over ~1/p nodes on average before dropping.
        With log_{1/p}(n) levels, total work = (1/p) * log_{1/p}(n) = O(log n).

        Time:  O(log n) expected, O(n) worst case
        Space: O(1) — just pointer traversal
        """
        current = self.header

        # Traverse from the highest active level down to 0
        for i in range(self.level, -1, -1):
            # Move forward at level i while the next node's key is smaller
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]

        # We're now at the largest node with key < target at level 0.
        # Move one step forward to the candidate.
        current = current.forward[0]

        if current and current.key == key:
            return current.value
        return None

    def insert(self, key, value):
        """Insert a key-value pair, or update value if key exists.

        Algorithm:
        1. Find the position where key should go (like search).
        2. Track the 'update' array — at each level, the last node before
           the insertion point. These are the nodes whose forward pointers
           need to be rewired.
        3. If key exists, update its value (no structural change).
        4. Otherwise, generate a random level for the new node and splice
           it into each level from 0 to its random level.

        WHY the update array?
        To insert a node at level k, we need to change the forward pointer of
        the predecessor at EVERY level 0..k. The update array captures these
        predecessors in a single pass.

        Time:  O(log n) expected — search dominates
        Space: O(max_level) for the update array
        """
        # update[i] will hold the last node at level i that is < key
        update = [None] * (self.max_level + 1)
        current = self.header

        # Traverse top-down, recording predecessors at each level
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        # Move to the candidate position at level 0
        current = current.forward[0]

        # If key already exists, just update the value
        if current and current.key == key:
            current.value = value
            return

        # Generate a random level for the new node
        new_level = self._random_level()

        # If new level exceeds current max, update the header's pointers
        # WHY? The header must connect to the new node at the new levels.
        # No other node exists at these levels yet, so header is the predecessor.
        if new_level > self.level:
            for i in range(self.level + 1, new_level + 1):
                update[i] = self.header
            self.level = new_level

        # Create the new node
        new_node = Node(key, value, new_level)

        # Splice the new node into each level 0..new_level
        # This is the pointer rewiring step — like inserting into a linked list,
        # but done independently at each level.
        for i in range(new_level + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

        self._size += 1

    def delete(self, key):
        """Delete a key from the skip list. Returns True if found and deleted.

        Algorithm:
        1. Find the node (like search), tracking the update array.
        2. If found, remove it from every level by rewiring predecessors.
        3. If the highest levels are now empty, shrink self.level.

        WHY shrink self.level?
        If the tallest node was deleted, the top levels are now empty.
        Keeping them wastes time (we'd traverse empty levels during search).

        Time:  O(log n) expected
        Space: O(max_level) for the update array
        """
        update = [None] * (self.max_level + 1)
        current = self.header

        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        current = current.forward[0]

        if current is None or current.key != key:
            return False

        # Remove current from each level it participates in
        for i in range(self.level + 1):
            # If update[i]'s forward isn't the target, we've passed its height
            if update[i].forward[i] != current:
                break
            update[i].forward[i] = current.forward[i]

        # Shrink the level if top levels are now empty
        while self.level > 0 and self.header.forward[self.level] is None:
            self.level -= 1

        self._size -= 1
        return True

    def display(self):
        """Print the skip list showing all levels.

        WHY this visualization matters:
        Skip lists are one of the few data structures where the visual structure
        directly reveals performance characteristics. You can literally see the
        "express lanes" that make search fast.
        """
        print(f"\nSkip List (size={self._size}, levels={self.level + 1}):")
        print("-" * 60)

        for i in range(self.level, -1, -1):
            node = self.header.forward[i]
            keys = []
            while node:
                keys.append(str(node.key))
                node = node.forward[i]
            print(f"Level {i}: HEAD -> {' -> '.join(keys)} -> NIL")

        print("-" * 60)

    def __contains__(self, key):
        """Support 'in' operator: `if 42 in skip_list:`"""
        return self.search(key) is not None

    def __iter__(self):
        """Iterate over all (key, value) pairs in sorted order.

        WHY level 0?
        Level 0 is the complete sorted linked list — every element is here.
        """
        node = self.header.forward[0]
        while node:
            yield node.key, node.value
            node = node.forward[0]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Skip List Demo ===\n")

    sl = SkipList(max_level=4, p=0.5)

    # Insert some values
    test_data = [(3, "three"), (6, "six"), (7, "seven"), (9, "nine"),
                 (12, "twelve"), (19, "nineteen"), (17, "seventeen"),
                 (26, "twenty-six"), (21, "twenty-one"), (25, "twenty-five")]

    print("Inserting:", [k for k, v in test_data])
    for key, value in test_data:
        sl.insert(key, value)

    sl.display()

    # Search
    print("\n--- Search ---")
    for key in [6, 17, 99]:
        result = sl.search(key)
        print(f"  search({key}) = {result}")

    # Membership test
    print(f"\n  19 in skip_list? {19 in sl}")
    print(f"  99 in skip_list? {99 in sl}")

    # Delete
    print("\n--- Delete ---")
    for key in [6, 19, 99]:
        deleted = sl.delete(key)
        print(f"  delete({key}) = {deleted}")

    sl.display()

    # Iteration
    print("\n--- Sorted Iteration ---")
    for key, value in sl:
        print(f"  {key}: {value}")

    # Update existing key
    print("\n--- Update ---")
    sl.insert(7, "SEVEN_UPDATED")
    print(f"  search(7) = {sl.search(7)}")

    print(f"\n  Total size: {len(sl)}")

    # Show that the structure is probabilistic — insert the same keys
    # into a new skip list and get a different shape
    print("\n\n=== Same Keys, Different Random Structure ===")
    sl2 = SkipList(max_level=4, p=0.5)
    for key, value in test_data:
        sl2.insert(key, value)
    sl2.display()
