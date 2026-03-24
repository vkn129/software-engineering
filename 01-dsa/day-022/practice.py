"""
Day 6 Practice: Implement a Singly Linked List from Scratch

Build every operation yourself. Each function has a docstring explaining
what to implement and test cases that will verify your solution.

The tests run automatically when you execute this file. Implement the
functions marked with TODO, then run:

    python practice.py

Rules:
- Do NOT use Python's built-in list, deque, or any collection for storage.
- Each function should work with the Node/LinkedList classes defined here.
- Solutions are at the bottom — try before looking.
"""


# ---------------------------------------------------------------------------
# Node class (given — do not modify)
# ---------------------------------------------------------------------------

class Node:
    __slots__ = ('data', 'next')

    def __init__(self, data):
        self.data = data
        self.next = None

    def __repr__(self):
        return f"Node({self.data!r})"


# ---------------------------------------------------------------------------
# Exercise 1: Build the LinkedList class with insert_at_head and to_list
# ---------------------------------------------------------------------------

class LinkedList:
    """A singly linked list.

    You need to implement:
    - insert_at_head(data): Insert a new node at the beginning. O(1).
    - to_list(): Convert to a Python list for testing. O(n).
    - __len__(): Return the number of elements. O(1) if you track size.
    """

    def __init__(self):
        self.head = None
        self.size = 0

    def insert_at_head(self, data):
        """Create a new node with `data` and make it the new head.

        Steps:
        1. Create a new Node.
        2. Set new_node.next = current head.
        3. Update self.head to point to new_node.
        4. Increment size.
        """
        # TODO: implement this
        pass

    def to_list(self):
        """Walk the list and collect all data values into a Python list.

        Returns a list like [head_data, ..., tail_data].
        """
        # TODO: implement this
        pass

    def __len__(self):
        """Return the number of elements in the list."""
        # TODO: implement this
        pass

    def __repr__(self):
        items = self.to_list() if self.to_list() is not None else []
        return " -> ".join(str(x) for x in items) + " -> None"


# ---------------------------------------------------------------------------
# Exercise 2: insert_at_tail
# ---------------------------------------------------------------------------

    # (Add this method to LinkedList above — shown here for clarity)

def insert_at_tail(ll, data):
    """Insert a new node at the END of linked list `ll`.

    If the list is empty, the new node becomes the head.
    Otherwise, traverse to the last node and set its .next to the new node.

    Complexity: O(n) — must traverse the full list.
    """
    # TODO: implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 3: search
# ---------------------------------------------------------------------------

def search(ll, target):
    """Return the 0-based index of the first node with data == target.

    Return -1 if not found.

    Complexity: O(n) worst case.
    """
    # TODO: implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 4: delete_by_value
# ---------------------------------------------------------------------------

def delete_by_value(ll, target):
    """Delete the FIRST node whose data equals `target`.

    Return True if a node was deleted, False if target was not found.

    Edge cases to handle:
    - Empty list -> return False
    - Target is in the head node -> update head
    - Target is in the middle or tail -> update previous node's .next

    Complexity: O(n) — must find the node first.
    """
    # TODO: implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 5: reverse_list
# ---------------------------------------------------------------------------

def reverse_list(ll):
    """Reverse the linked list IN-PLACE (do not create new nodes).

    Use the three-pointer technique:
    - prev = None
    - current = head
    - In each step: save next, reverse current's pointer, advance prev and current

    Complexity: O(n) time, O(1) space.
    """
    # TODO: implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 6: find_middle
# ---------------------------------------------------------------------------

def find_middle(ll):
    """Return the data of the middle node.

    For odd-length lists, return the exact middle.
    For even-length lists, return the second of the two middle nodes.
    Return None if the list is empty.

    HINT: Use the slow/fast pointer technique.
    - slow moves 1 step at a time
    - fast moves 2 steps at a time
    - When fast reaches the end, slow is at the middle.

    Complexity: O(n) time, O(1) space.
    """
    # TODO: implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 7: has_cycle
# ---------------------------------------------------------------------------

def has_cycle(ll):
    """Detect if the linked list contains a cycle.

    A cycle means some node's .next points back to an earlier node,
    creating an infinite loop.

    Use Floyd's cycle detection (tortoise and hare):
    - slow moves 1 step, fast moves 2 steps
    - If they ever meet, there is a cycle
    - If fast reaches None, there is no cycle

    Complexity: O(n) time, O(1) space.
    """
    # TODO: implement this
    pass


# ===========================================================================
# TEST CASES — run these to verify your implementations
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

    # --- Exercise 1: insert_at_head, to_list, __len__ ---
    print("Exercise 1: insert_at_head / to_list / __len__")
    ll = LinkedList()
    check("empty list to_list", ll.to_list(), [])
    check("empty list len", len(ll), 0)
    ll.insert_at_head(3)
    ll.insert_at_head(2)
    ll.insert_at_head(1)
    check("insert_at_head to_list", ll.to_list(), [1, 2, 3])
    check("insert_at_head len", len(ll), 3)

    # --- Exercise 2: insert_at_tail ---
    print("\nExercise 2: insert_at_tail")
    ll2 = LinkedList()
    insert_at_tail(ll2, 1)
    insert_at_tail(ll2, 2)
    insert_at_tail(ll2, 3)
    check("insert_at_tail to_list", ll2.to_list(), [1, 2, 3])
    check("insert_at_tail len", len(ll2), 3)

    # --- Exercise 3: search ---
    print("\nExercise 3: search")
    ll3 = LinkedList()
    for v in [10, 20, 30, 40, 50]:
        insert_at_tail(ll3, v)
    check("search found at head", search(ll3, 10), 0)
    check("search found at tail", search(ll3, 50), 4)
    check("search found in middle", search(ll3, 30), 2)
    check("search not found", search(ll3, 99), -1)
    check("search empty list", search(LinkedList(), 1), -1)

    # --- Exercise 4: delete_by_value ---
    print("\nExercise 4: delete_by_value")
    ll4 = LinkedList()
    for v in [1, 2, 3, 4, 5]:
        insert_at_tail(ll4, v)
    check("delete head", delete_by_value(ll4, 1), True)
    check("after delete head", ll4.to_list(), [2, 3, 4, 5])
    check("delete middle", delete_by_value(ll4, 3), True)
    check("after delete middle", ll4.to_list(), [2, 4, 5])
    check("delete tail", delete_by_value(ll4, 5), True)
    check("after delete tail", ll4.to_list(), [2, 4])
    check("delete not found", delete_by_value(ll4, 99), False)
    check("delete from empty", delete_by_value(LinkedList(), 1), False)

    # --- Exercise 5: reverse_list ---
    print("\nExercise 5: reverse_list")
    ll5 = LinkedList()
    for v in [1, 2, 3, 4, 5]:
        insert_at_tail(ll5, v)
    reverse_list(ll5)
    check("reverse 5 elements", ll5.to_list(), [5, 4, 3, 2, 1])
    ll5_single = LinkedList()
    ll5_single.insert_at_head(42)
    reverse_list(ll5_single)
    check("reverse single element", ll5_single.to_list(), [42])
    ll5_empty = LinkedList()
    reverse_list(ll5_empty)
    check("reverse empty", ll5_empty.to_list(), [])

    # --- Exercise 6: find_middle ---
    print("\nExercise 6: find_middle")
    ll6_odd = LinkedList()
    for v in [1, 2, 3, 4, 5]:
        insert_at_tail(ll6_odd, v)
    check("middle of 5 elements", find_middle(ll6_odd), 3)
    ll6_even = LinkedList()
    for v in [1, 2, 3, 4]:
        insert_at_tail(ll6_even, v)
    check("middle of 4 elements", find_middle(ll6_even), 3)
    ll6_one = LinkedList()
    ll6_one.insert_at_head(99)
    check("middle of 1 element", find_middle(ll6_one), 99)
    check("middle of empty", find_middle(LinkedList()), None)

    # --- Exercise 7: has_cycle ---
    print("\nExercise 7: has_cycle")
    ll7 = LinkedList()
    for v in [1, 2, 3, 4, 5]:
        insert_at_tail(ll7, v)
    check("no cycle", has_cycle(ll7), False)
    check("empty no cycle", has_cycle(LinkedList()), False)
    # Create a cycle: 5 -> 3
    ll7_cycle = LinkedList()
    nodes = []
    for v in [1, 2, 3, 4, 5]:
        insert_at_tail(ll7_cycle, v)
    # Walk to collect node references
    cur = ll7_cycle.head
    while cur:
        nodes.append(cur)
        cur = cur.next
    nodes[4].next = nodes[2]  # 5 -> 3 creates a cycle
    check("has cycle", has_cycle(ll7_cycle), True)

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

Exercise 1: insert_at_head / to_list / __len__

    def insert_at_head(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def to_list(self):
        result = []
        current = self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def __len__(self):
        return self.size

Exercise 2: insert_at_tail

    def insert_at_tail(ll, data):
        new_node = Node(data)
        ll.size += 1
        if ll.head is None:
            ll.head = new_node
            return
        current = ll.head
        while current.next is not None:
            current = current.next
        current.next = new_node

Exercise 3: search

    def search(ll, target):
        current = ll.head
        index = 0
        while current is not None:
            if current.data == target:
                return index
            current = current.next
            index += 1
        return -1

Exercise 4: delete_by_value

    def delete_by_value(ll, target):
        if ll.head is None:
            return False
        if ll.head.data == target:
            ll.head = ll.head.next
            ll.size -= 1
            return True
        current = ll.head
        while current.next is not None:
            if current.next.data == target:
                current.next = current.next.next
                ll.size -= 1
                return True
            current = current.next
        return False

Exercise 5: reverse_list

    def reverse_list(ll):
        prev = None
        current = ll.head
        while current is not None:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        ll.head = prev

Exercise 6: find_middle

    def find_middle(ll):
        if ll.head is None:
            return None
        slow = ll.head
        fast = ll.head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
        return slow.data

Exercise 7: has_cycle (Floyd's algorithm)

    def has_cycle(ll):
        if ll.head is None:
            return False
        slow = ll.head
        fast = ll.head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False
"""


def show_solutions():
    print(SOLUTIONS)


if __name__ == "__main__":
    print("Day 6 Practice: Implement a Singly Linked List")
    print("=" * 50)
    print()
    print("Implement the TODO functions above, then run this file.")
    print("Tests will tell you which functions work and which need fixing.\n")
    run_tests()
    print("\nTo see solutions, uncomment the line below or call show_solutions().")
    # show_solutions()
