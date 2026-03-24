"""
Day 27: Linked List Algorithms

Classic algorithmic patterns on singly linked lists:
- Floyd's cycle detection (O(1) space cycle finding)
- Merge sort on lists (O(n log n) time, O(1) heap space)
- Intersection detection (O(1) space)
- Palindrome check (O(1) space)
- Merge k sorted lists (O(N log k) using a min-heap)

Only heapq is imported — everything else is built from scratch.

Run: python linked_list_algorithms.py
"""

import heapq


# ---------------------------------------------------------------------------
# Node definition
# ---------------------------------------------------------------------------

class ListNode:
    """A singly linked list node.

    We use __slots__ to save memory — each node is just data + one pointer.
    No __eq__ override: identity comparison (is) is what we want for
    algorithms like intersection detection where we care about the same
    object, not equal values.
    """

    __slots__ = ('val', 'next')

    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt

    def __repr__(self):
        return f"ListNode({self.val})"

    # Required for heapq: when two nodes have the same val, heapq needs
    # a tiebreaker. We use id() so comparison never raises TypeError.
    def __lt__(self, other):
        return id(self) < id(other)


# ---------------------------------------------------------------------------
# Helpers: convert between Python lists and linked lists
# ---------------------------------------------------------------------------

def list_to_linked(arr):
    """Convert a Python list to a singly linked list. Returns head node.

    Why a dummy head? It avoids a special case for the first node.
    We create a sentinel, build the chain, then return sentinel.next.
    """
    if not arr:
        return None
    dummy = ListNode(0)
    curr = dummy
    for val in arr:
        curr.next = ListNode(val)
        curr = curr.next
    return dummy.next


def linked_to_list(head):
    """Convert a linked list to a Python list. For testing and display.

    Safety: we cap at 10000 nodes to avoid infinite loops from cycles.
    """
    result = []
    seen = 0
    curr = head
    while curr and seen < 10000:
        result.append(curr.val)
        curr = curr.next
        seen += 1
    return result


# ---------------------------------------------------------------------------
# Floyd's Cycle Detection
# ---------------------------------------------------------------------------

def floyd_detect_cycle(head):
    """Detect whether a cycle exists in the linked list.

    Uses two pointers at different speeds. If there is a cycle, the fast
    pointer (moving 2 steps) will eventually catch the slow pointer (moving
    1 step) because the gap between them shrinks by exactly 1 each iteration.

    If there is no cycle, fast reaches the end (None).

    Returns True if a cycle exists, False otherwise.
    Time: O(n), Space: O(1).
    """
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next          # 1 step
        fast = fast.next.next     # 2 steps
        if slow is fast:
            # They collided inside the cycle
            return True
    # fast reached the end — no cycle
    return False


def find_cycle_start(head):
    """Find the node where the cycle begins, or None if no cycle.

    Phase 1: Detect collision point using Floyd's algorithm.
    Phase 2: Move one pointer to head, keep the other at the collision point.
             Advance both at speed 1. They meet at the cycle start.

    Why phase 2 works:
        Let a = distance from head to cycle start
            b = distance from cycle start to collision point
            C = cycle length
        At collision: slow traveled a+b, fast traveled a+b+kC
        Since fast = 2*slow: 2(a+b) = a+b+kC => a = kC - b
        So traveling 'a' steps from the collision point lands at the cycle start
        (it goes (kC - b) steps forward from a point b into the cycle = cycle start).
        A pointer from head also travels 'a' steps to reach cycle start.
        They meet there.

    Time: O(n), Space: O(1).
    """
    # Phase 1: find collision
    slow = head
    fast = head
    found_cycle = False
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            found_cycle = True
            break

    if not found_cycle:
        return None

    # Phase 2: find cycle start
    # One pointer at head, one at collision point, both move at speed 1
    finder = head
    while finder is not slow:
        finder = finder.next
        slow = slow.next

    return finder  # This is the cycle start node


# ---------------------------------------------------------------------------
# Merge Sort on Linked List
# ---------------------------------------------------------------------------

def _get_mid(head):
    """Find the middle node using slow/fast pointers.

    Returns the node just before the midpoint so we can split the list.
    For even-length lists, returns the end of the first half.

    Why slow/fast? We cannot index into a linked list, so we use the
    geometric trick: when fast reaches the end, slow is at the middle.
    This avoids a two-pass approach (count then traverse to n/2).
    """
    slow = head
    fast = head.next  # Start fast one ahead so slow stops before mid
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow


def _merge_sorted(l1, l2):
    """Merge two sorted linked lists into one sorted list.

    Uses a dummy node to avoid special-casing the head.
    This is pure pointer rewiring — no new nodes are allocated.

    Time: O(n + m) where n, m are the lengths of the two lists.
    """
    dummy = ListNode(0)
    tail = dummy

    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next

    # Attach whichever list still has remaining nodes
    tail.next = l1 if l1 else l2
    return dummy.next


def merge_sort_list(head):
    """Sort a linked list using merge sort.

    Unlike array merge sort which needs O(n) auxiliary space for merging,
    linked list merge sort only rewires pointers — O(1) heap space.
    The O(log n) stack space comes from recursion depth.

    Algorithm:
    1. Find the midpoint (slow/fast pointers)
    2. Split the list into two halves
    3. Recursively sort each half
    4. Merge the two sorted halves

    Time: O(n log n), Space: O(log n) stack, O(1) heap.
    """
    # Base case: empty list or single node is already sorted
    if not head or not head.next:
        return head

    # Split: find mid, then sever the link
    mid = _get_mid(head)
    right_head = mid.next
    mid.next = None  # Sever the list into two halves

    # Recurse on both halves
    left = merge_sort_list(head)
    right = merge_sort_list(right_head)

    # Merge the two sorted halves
    return _merge_sorted(left, right)


# ---------------------------------------------------------------------------
# Find Intersection of Two Lists
# ---------------------------------------------------------------------------

def find_intersection(headA, headB):
    """Find the node where two singly linked lists intersect, or None.

    The elegant two-pointer approach: pointer A walks listA then listB,
    pointer B walks listB then listA. Both travel the same total distance
    (lenA + lenB), so they reach the intersection node at the same time.

    Why this works:
        If lists intersect at node C with:
            listA: a nodes before C, then c common nodes
            listB: b nodes before C, then c common nodes
        Pointer A travels: a + c + b (to reach C on second pass)
        Pointer B travels: b + c + a (to reach C on second pass)
        a + c + b = b + c + a — they arrive at C simultaneously.

    If no intersection, both pointers reach None at the same time
    (after traversing lenA + lenB nodes total).

    Time: O(n + m), Space: O(1).
    """
    if not headA or not headB:
        return None

    ptrA = headA
    ptrB = headB

    # When ptrA reaches the end of A, redirect to head of B (and vice versa).
    # After at most one redirect each, they either meet at the intersection
    # or both become None simultaneously.
    while ptrA is not ptrB:
        ptrA = ptrA.next if ptrA else headB
        ptrB = ptrB.next if ptrB else headA

    return ptrA  # Either the intersection node or None


# ---------------------------------------------------------------------------
# Palindrome Check
# ---------------------------------------------------------------------------

def _reverse_list(head):
    """Reverse a singly linked list in-place. Returns new head.

    Classic three-pointer technique:
    - prev: the reversed portion so far
    - curr: the node we are about to reverse
    - next_node: saved so we do not lose the rest of the list

    Time: O(n), Space: O(1).
    """
    prev = None
    curr = head
    while curr:
        next_node = curr.next
        curr.next = prev  # Reverse the pointer
        prev = curr
        curr = next_node
    return prev


def is_palindrome(head):
    """Check if a linked list reads the same forwards and backwards.

    Strategy:
    1. Find the middle using slow/fast pointers
    2. Reverse the second half in-place
    3. Compare the first half and reversed second half node by node
    4. Restore the list by reversing the second half back (good practice)

    Why not just copy to an array? That is O(n) space. This approach
    uses O(1) space — important when the list is huge.

    Time: O(n), Space: O(1).
    """
    if not head or not head.next:
        return True

    # Step 1: find the end of the first half
    slow = head
    fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    # slow is now at the end of the first half
    # Step 2: reverse the second half
    second_half_head = _reverse_list(slow.next)

    # Step 3: compare both halves
    p1 = head
    p2 = second_half_head
    is_palin = True
    while p2:  # Second half is same length or one shorter
        if p1.val != p2.val:
            is_palin = False
            break
        p1 = p1.next
        p2 = p2.next

    # Step 4: restore the list (reverse second half back)
    slow.next = _reverse_list(second_half_head)

    return is_palin


# ---------------------------------------------------------------------------
# Merge K Sorted Lists
# ---------------------------------------------------------------------------

def merge_k_sorted(lists):
    """Merge k sorted linked lists into one sorted list.

    Uses a min-heap of size k. Each element in the heap is (node.val, node)
    so the heap orders by value. When values tie, ListNode.__lt__ breaks
    the tie using id().

    Algorithm:
    1. Push the head of each non-empty list onto the heap
    2. Pop the minimum node, append it to the result
    3. If that node has a next, push next onto the heap
    4. Repeat until the heap is empty

    Why a heap? We need the minimum of k candidates. A heap gives O(log k)
    per extraction. Each of the N total nodes enters and leaves the heap
    exactly once, so total work is O(N log k).

    Time: O(N log k), Space: O(k) for the heap.
    """
    dummy = ListNode(0)
    tail = dummy
    heap = []

    # Initialize the heap with the head of each non-empty list
    for lst in lists:
        if lst:
            heapq.heappush(heap, (lst.val, lst))

    while heap:
        val, node = heapq.heappop(heap)
        tail.next = node
        tail = tail.next
        if node.next:
            heapq.heappush(heap, (node.next.val, node.next))

    # Important: terminate the merged list
    tail.next = None
    return dummy.next


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Day 27: Linked List Algorithms")
    print("=" * 60)

    # --- Floyd's Cycle Detection ---
    print("\n--- Floyd's Cycle Detection ---")

    # No cycle
    head = list_to_linked([1, 2, 3, 4, 5])
    print(f"List [1,2,3,4,5] has cycle: {floyd_detect_cycle(head)}")

    # Create a cycle: 5 -> 3
    node3 = head.next.next          # node with val 3
    node5 = node3.next.next         # node with val 5
    node5.next = node3              # cycle: 5 points back to 3
    print(f"List [1,2,3,4,5->3] has cycle: {floyd_detect_cycle(head)}")

    cycle_start = find_cycle_start(head)
    print(f"Cycle starts at node with val: {cycle_start.val}")  # Should be 3

    # Break the cycle for later use
    node5.next = None

    # --- Merge Sort ---
    print("\n--- Merge Sort on Linked List ---")
    unsorted = list_to_linked([4, 2, 1, 3, 5, 0, 8, 7, 6])
    print(f"Before sort: {linked_to_list(unsorted)}")
    sorted_head = merge_sort_list(unsorted)
    print(f"After sort:  {linked_to_list(sorted_head)}")

    # --- Find Intersection ---
    print("\n--- Find Intersection ---")
    # Build two lists that share a common tail: c1 -> c2 -> c3
    common = list_to_linked([100, 200, 300])
    listA = list_to_linked([1, 2, 3])
    listB = list_to_linked([10, 20])

    # Attach common tail
    currA = listA
    while currA.next:
        currA = currA.next
    currA.next = common

    currB = listB
    while currB.next:
        currB = currB.next
    currB.next = common

    inter = find_intersection(listA, listB)
    print(f"Intersection at node with val: {inter.val}")  # Should be 100

    # No intersection
    listX = list_to_linked([1, 2, 3])
    listY = list_to_linked([4, 5, 6])
    print(f"No intersection: {find_intersection(listX, listY)}")

    # --- Palindrome Check ---
    print("\n--- Palindrome Check ---")
    cases = [
        ([1, 2, 3, 2, 1], True),
        ([1, 2, 2, 1], True),
        ([1, 2, 3], False),
        ([1], True),
        ([], True),
    ]
    for arr, expected in cases:
        head = list_to_linked(arr)
        result = is_palindrome(head)
        status = "PASS" if result == expected else "FAIL"
        print(f"  [{status}] {arr} -> is_palindrome = {result}")

    # --- Merge K Sorted Lists ---
    print("\n--- Merge K Sorted Lists ---")
    lists = [
        list_to_linked([1, 4, 7]),
        list_to_linked([2, 5, 8]),
        list_to_linked([3, 6, 9]),
    ]
    merged = merge_k_sorted(lists)
    print(f"Merged 3 sorted lists: {linked_to_list(merged)}")

    lists2 = [
        list_to_linked([1, 10, 100]),
        list_to_linked([2, 20, 200]),
        list_to_linked([5, 50, 500]),
        list_to_linked([]),
        list_to_linked([3]),
    ]
    merged2 = merge_k_sorted(lists2)
    print(f"Merged 5 sorted lists: {linked_to_list(merged2)}")

    print("\n" + "=" * 60)
    print("All demos complete.")
    print("=" * 60)
