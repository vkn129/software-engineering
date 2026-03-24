"""
Day 7 Practice: Implement a Doubly Linked List + LRU Cache from Scratch

Build a doubly linked list with sentinel nodes, then use it to implement
an LRU cache. Each exercise builds on the previous one.

Run: python practice.py

Rules:
- Do NOT use Python's built-in collections (deque, OrderedDict, etc.)
- Do NOT import functools.lru_cache
- Build everything from the Node class up.
"""


# ---------------------------------------------------------------------------
# Node class (given — do not modify)
# ---------------------------------------------------------------------------

class DNode:
    """A doubly linked list node with key and data.

    The key field exists for the LRU cache: when we evict a node, we need
    to know its key so we can remove it from the hash map.
    """
    __slots__ = ('key', 'data', 'prev', 'next')

    def __init__(self, key=None, data=None):
        self.key = key
        self.data = data
        self.prev = None
        self.next = None

    def __repr__(self):
        return f"DNode({self.key!r}: {self.data!r})"


# ---------------------------------------------------------------------------
# Exercise 1: Doubly Linked List with Sentinel Nodes
# ---------------------------------------------------------------------------

class DoublyLinkedList:
    """A doubly linked list with head and tail sentinel nodes.

    Structure:
        [HEAD_SENTINEL] <-> [real nodes...] <-> [TAIL_SENTINEL]

    An empty list:
        [HEAD_SENTINEL] <-> [TAIL_SENTINEL]

    The sentinels are permanent — never removed. They guarantee that
    every real node always has valid .prev and .next pointers.

    You need to implement:
    - __init__: Create sentinels and wire them together
    - push_front(key, data): Insert at front, return the new node
    - push_back(key, data): Insert at back, return the new node
    - remove(node): Remove a node given a direct reference. O(1).
    - pop_back(): Remove and return the last real node
    - move_to_front(node): Move an existing node to the front. O(1).
    - __len__(): Return number of real nodes
    - to_list(): Return list of (key, data) tuples front to back
    """

    def __init__(self):
        """Create head and tail sentinels. Wire them together.

        After init:
          self._head.next = self._tail
          self._tail.prev = self._head
          self._size = 0
        """
        # TODO: implement this
        pass

    def push_front(self, key=None, data=None):
        """Create a new node and insert it right after the head sentinel.

        Returns the new node (callers need this for hash map storage).

        Steps:
        1. Create new DNode with key and data.
        2. Wire it between self._head and self._head.next.
        3. Increment size.
        4. Return the new node.

        No if-statements needed — sentinels handle the empty case.
        """
        # TODO: implement this
        pass

    def push_back(self, key=None, data=None):
        """Create a new node and insert it right before the tail sentinel.

        Returns the new node.
        """
        # TODO: implement this
        pass

    def remove(self, node):
        """Remove a node from the list given a direct reference.

        This is the O(1) operation that makes doubly linked lists valuable.

        Steps:
        1. node.prev.next = node.next
        2. node.next.prev = node.prev
        3. Clear node's prev/next (optional but clean)
        4. Decrement size.
        5. Return the removed node.

        Do NOT allow removing sentinel nodes.
        """
        # TODO: implement this
        pass

    def pop_back(self):
        """Remove and return the last real node (just before tail sentinel).

        Raise IndexError if the list is empty.
        """
        # TODO: implement this
        pass

    def move_to_front(self, node):
        """Move an existing node to the front (right after head sentinel).

        Steps:
        1. Remove node from its current position.
        2. Re-insert it at the front.

        Both steps are O(1). Total: O(1).
        """
        # TODO: implement this
        pass

    def __len__(self):
        # TODO: implement this
        pass

    def is_empty(self):
        return self.__len__() == 0 if self.__len__() is not None else True

    def to_list(self):
        """Return a list of (key, data) tuples from front to back.

        Walk from self._head.next until you reach self._tail.
        """
        # TODO: implement this
        pass

    def __repr__(self):
        items = self.to_list()
        if items is None or len(items) == 0:
            return "[HEAD] <-> [TAIL]"
        parts = " <-> ".join(f"[{k}:{d}]" for k, d in items)
        return f"[HEAD] <-> {parts} <-> [TAIL]"


# ---------------------------------------------------------------------------
# Exercise 2: LRU Cache
# ---------------------------------------------------------------------------

class LRUCache:
    """Least Recently Used cache: O(1) get and O(1) put.

    Architecture:
    - self.cache: dict mapping key -> DNode
    - self.dll: DoublyLinkedList maintaining access order
      - Front = most recently used
      - Back = least recently used (eviction candidate)

    You need to implement:
    - __init__(capacity): Set up cache dict and DLL
    - get(key): Look up key, move to front, return value (or None)
    - put(key, value): Insert/update key-value pair, evict LRU if full
    """

    def __init__(self, capacity):
        """Initialize with given capacity.

        self.capacity = capacity
        self.cache = {}            # key -> DNode
        self.dll = DoublyLinkedList()
        """
        # TODO: implement this
        pass

    def get(self, key):
        """Look up a key in the cache.

        If found:
          1. Move the node to the front of the DLL (most recently used)
          2. Return the node's data

        If not found:
          Return None

        Complexity: O(1)
        """
        # TODO: implement this
        pass

    def put(self, key, value):
        """Insert or update a key-value pair.

        If key already exists:
          1. Update the node's data to the new value
          2. Move the node to the front

        If key does not exist:
          1. If cache is at capacity, evict the LRU item:
             a. Pop the back node from the DLL
             b. Delete that node's key from self.cache
          2. Create a new node at the front of the DLL
          3. Store the node reference in self.cache[key]

        Complexity: O(1)

        IMPORTANT: The DLL node stores the key so that during eviction,
        we know which key to delete from the hash map.
        """
        # TODO: implement this
        pass

    def __len__(self):
        return len(self.dll) if hasattr(self, 'dll') and self.dll is not None else 0

    def __repr__(self):
        if not hasattr(self, 'dll') or self.dll is None:
            return "LRUCache(uninitialized)"
        return f"LRUCache(size={len(self.dll)}, order={self.dll})"


# ===========================================================================
# TEST CASES
# ===========================================================================

def run_tests():
    print("Running tests...\n")
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"        Expected: {expected}")
            print(f"        Got:      {got}")
            failed += 1

    # --- Exercise 1: Doubly Linked List ---
    print("Exercise 1: Doubly Linked List with Sentinels")

    dll = DoublyLinkedList()
    check("empty list length", len(dll), 0)
    check("empty list to_list", dll.to_list(), [])

    n1 = dll.push_front(key="B", data=2)
    check("push_front B", dll.to_list(), [("B", 2)])
    check("length after 1 push", len(dll), 1)

    n2 = dll.push_front(key="A", data=1)
    check("push_front A", dll.to_list(), [("A", 1), ("B", 2)])

    n3 = dll.push_back(key="C", data=3)
    check("push_back C", dll.to_list(), [("A", 1), ("B", 2), ("C", 3)])
    check("length after 3 pushes", len(dll), 3)

    # Remove middle node
    dll.remove(n1)  # remove B
    check("remove middle (B)", dll.to_list(), [("A", 1), ("C", 3)])
    check("length after remove", len(dll), 2)

    # Pop back
    popped = dll.pop_back()
    check("pop_back returns C", (popped.key, popped.data), ("C", 3))
    check("after pop_back", dll.to_list(), [("A", 1)])
    check("length after pop", len(dll), 1)

    # Move to front
    n4 = dll.push_back(key="D", data=4)
    n5 = dll.push_back(key="E", data=5)
    # List: A <-> D <-> E
    check("before move_to_front", dll.to_list(),
          [("A", 1), ("D", 4), ("E", 5)])
    dll.move_to_front(n4)  # move D to front
    check("after move_to_front(D)", dll.to_list(),
          [("D", 4), ("A", 1), ("E", 5)])

    # Move back node to front
    dll.move_to_front(n5)  # move E to front
    check("after move_to_front(E)", dll.to_list(),
          [("E", 5), ("D", 4), ("A", 1)])

    # --- Exercise 2: LRU Cache ---
    print("\nExercise 2: LRU Cache")

    cache = LRUCache(capacity=3)
    check("empty cache len", len(cache), 0)

    cache.put("A", 1)
    cache.put("B", 2)
    cache.put("C", 3)
    check("cache len after 3 puts", len(cache), 3)

    # Get existing key
    check("get A", cache.get("A"), 1)
    # A is now most recently used: order should be A, C, B

    # Put new key when full -> evicts LRU (B)
    cache.put("D", 4)
    check("cache len still 3", len(cache), 3)
    check("get B after eviction", cache.get("B"), None)  # B was evicted
    check("get D", cache.get("D"), 4)

    # Update existing key
    cache.put("A", 10)
    check("get A after update", cache.get("A"), 10)

    # Fill and evict
    cache.put("E", 5)
    # After putting E, LRU should have been evicted
    # Order before E: A, D, C (A was most recent due to put, D was accessed, C is oldest)
    # C should be evicted
    check("get C after eviction", cache.get("C"), None)
    check("get E", cache.get("E"), 5)

    # Test with capacity 1
    tiny = LRUCache(capacity=1)
    tiny.put("X", 1)
    check("tiny get X", tiny.get("X"), 1)
    tiny.put("Y", 2)
    check("tiny get X after evict", tiny.get("X"), None)
    check("tiny get Y", tiny.get("Y"), 2)

    # Test with capacity 2 — ordering
    cache2 = LRUCache(capacity=2)
    cache2.put("A", 1)
    cache2.put("B", 2)
    cache2.get("A")      # A is now most recent
    cache2.put("C", 3)   # B should be evicted (it is LRU)
    check("cap2: B evicted", cache2.get("B"), None)
    check("cap2: A still present", cache2.get("A"), 1)
    check("cap2: C present", cache2.get("C"), 3)

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")

    if failed == 0:
        print("\n  All tests passed. Well done.")
    else:
        print("\n  Some tests failed. Check your implementations above.")
        print("  Scroll down for solutions if you are stuck.")


# ===========================================================================
# SOLUTIONS — scroll down only after attempting all exercises
# ===========================================================================
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

SOLUTIONS = """
================================================================================
SOLUTIONS — read only after a genuine attempt
================================================================================

Exercise 1: DoublyLinkedList

    def __init__(self):
        self._head = DNode(key="HEAD_SENTINEL")
        self._tail = DNode(key="TAIL_SENTINEL")
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    def push_front(self, key=None, data=None):
        new_node = DNode(key=key, data=data)
        successor = self._head.next
        new_node.prev = self._head
        new_node.next = successor
        self._head.next = new_node
        successor.prev = new_node
        self._size += 1
        return new_node

    def push_back(self, key=None, data=None):
        new_node = DNode(key=key, data=data)
        predecessor = self._tail.prev
        new_node.next = self._tail
        new_node.prev = predecessor
        predecessor.next = new_node
        self._tail.prev = new_node
        self._size += 1
        return new_node

    def remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self._size -= 1
        return node

    def pop_back(self):
        if self._size == 0:
            raise IndexError("pop from empty list")
        return self.remove(self._tail.prev)

    def move_to_front(self, node):
        self.remove(node)
        # Re-insert at front
        successor = self._head.next
        node.prev = self._head
        node.next = successor
        self._head.next = node
        successor.prev = node
        self._size += 1

    def __len__(self):
        return self._size

    def to_list(self):
        result = []
        current = self._head.next
        while current is not self._tail:
            result.append((current.key, current.data))
            current = current.next
        return result


Exercise 2: LRUCache

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.dll = DoublyLinkedList()

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self.dll.move_to_front(node)
            return node.data
        return None

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.data = value
            self.dll.move_to_front(node)
            return
        if len(self.dll) >= self.capacity:
            evicted = self.dll.pop_back()
            del self.cache[evicted.key]
        new_node = self.dll.push_front(key=key, data=value)
        self.cache[key] = new_node
"""


def show_solutions():
    print(SOLUTIONS)


if __name__ == "__main__":
    print("Day 7 Practice: Doubly Linked List + LRU Cache")
    print("=" * 50)
    print()
    print("Implement the TODO functions above, then run this file.")
    print("Exercises build on each other: DLL first, then LRU Cache.\n")
    run_tests()
    print("\nTo see solutions, uncomment the line below or call show_solutions().")
    # show_solutions()
