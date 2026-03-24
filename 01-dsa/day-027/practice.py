"""
Day 27 Practice: Linked List Algorithm Exercises

5 exercises covering classic linked list manipulation patterns.
Each exercise has a TODO stub for you to implement and a _sol_ solution below.

Rules:
- Only heapq is allowed as an import (and you won't need it here)
- Build everything using the ListNode class provided
- Do NOT look at solutions until you've tried each exercise

Run: python practice.py
"""


# ---------------------------------------------------------------------------
# Node class (shared by all exercises)
# ---------------------------------------------------------------------------

class ListNode:
    """Singly linked list node."""
    __slots__ = ('val', 'next')

    def __init__(self, val=0, nxt=None):
        self.val = val
        self.next = nxt

    def __repr__(self):
        return f"ListNode({self.val})"


def list_to_linked(arr):
    """Convert Python list to linked list."""
    if not arr:
        return None
    dummy = ListNode(0)
    curr = dummy
    for val in arr:
        curr.next = ListNode(val)
        curr = curr.next
    return dummy.next


def linked_to_list(head):
    """Convert linked list to Python list."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


# ===========================================================================
# Exercise 1: Reverse Nodes in Groups of K
# ===========================================================================
# Given a linked list and integer k, reverse the nodes in groups of k.
# If the remaining nodes are fewer than k, leave them as-is.
#
# Example: [1,2,3,4,5], k=2 -> [2,1,4,3,5]
# Example: [1,2,3,4,5], k=3 -> [3,2,1,4,5]
#
# Why this matters: This tests your ability to do precise pointer surgery
# on a bounded segment of a list. It combines reversal with bookkeeping
# of where each group starts and ends. Real-world analogy: reordering
# fixed-size blocks in a buffer without extra allocation.
# ===========================================================================

def reverse_k_group(head, k):
    """Reverse the linked list in groups of k nodes.

    Approach:
    1. Count if there are at least k nodes remaining
    2. If yes, reverse the next k nodes
    3. Recursively/iteratively handle the rest
    4. Connect the reversed group to the result of the rest

    Time: O(n), Space: O(1) iterative or O(n/k) recursive stack.
    """
    # TODO: implement this
    pass


def _sol_reverse_k_group(head, k):
    """Solution: Reverse nodes in groups of k."""
    # First, check if there are at least k nodes remaining
    count = 0
    curr = head
    while curr and count < k:
        curr = curr.next
        count += 1

    if count < k:
        # Fewer than k nodes left — do not reverse, return as-is
        return head

    # Reverse the first k nodes
    # Standard reversal but we stop after k nodes instead of at None
    prev = None
    curr = head
    for _ in range(k):
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node

    # After reversal:
    # - prev points to the new head of this group (was the k-th node)
    # - head is now the tail of this group
    # - curr points to the (k+1)-th node (start of next group)

    # Recursively reverse the rest and connect
    head.next = _sol_reverse_k_group(curr, k)

    return prev  # New head of this reversed group


# ===========================================================================
# Exercise 2: Remove N-th Node from End in One Pass
# ===========================================================================
# Given a linked list, remove the n-th node from the end and return the head.
# Do it in a single pass (one traversal of the list).
#
# Example: [1,2,3,4,5], n=2 -> [1,2,3,5] (removed 4)
# Example: [1], n=1 -> [] (removed 1)
#
# Why this matters: The two-pointer gap technique is a fundamental pattern.
# By maintaining a fixed gap between two pointers, you can locate the n-th
# from end without knowing the list length. This pattern shows up whenever
# you need to find something relative to the end in a single pass.
# ===========================================================================

def remove_nth_from_end(head, n):
    """Remove the n-th node from the end of the list.

    Approach (two-pointer gap):
    1. Use a dummy node before head (handles edge case of removing head)
    2. Advance the fast pointer n+1 steps ahead of slow
    3. Move both at the same speed until fast reaches None
    4. slow.next is the node to remove — skip it

    Time: O(len), Space: O(1).
    """
    # TODO: implement this
    pass


def _sol_remove_nth_from_end(head, n):
    """Solution: Remove n-th node from end in one pass."""
    # Dummy node handles the case where we remove the head itself
    # Without it, removing the head requires a special case
    dummy = ListNode(0, head)
    fast = dummy
    slow = dummy

    # Move fast n+1 steps ahead so that when fast reaches the end,
    # slow is right before the node to delete
    for _ in range(n + 1):
        fast = fast.next

    # Move both until fast hits None
    while fast:
        fast = fast.next
        slow = slow.next

    # slow.next is the node to remove
    slow.next = slow.next.next

    return dummy.next


# ===========================================================================
# Exercise 3: Add Two Numbers as Linked Lists
# ===========================================================================
# Two non-empty linked lists represent non-negative integers. Digits are
# stored in REVERSE order (least significant digit first). Add the two
# numbers and return the sum as a linked list.
#
# Example: [2,4,3] + [5,6,4] -> [7,0,8] (342 + 465 = 807)
# Example: [9,9,9] + [1] -> [0,0,0,1] (999 + 1 = 1000)
#
# Why this matters: This mirrors how hardware adders work — processing
# digits from least significant to most significant, propagating carries.
# Understanding carry propagation is essential for understanding ALU design
# and arbitrary-precision arithmetic libraries.
# ===========================================================================

def add_two_numbers(l1, l2):
    """Add two numbers represented as reversed linked lists.

    Approach:
    1. Walk both lists simultaneously, adding corresponding digits + carry
    2. Create a new node for each digit of the result
    3. Handle carry propagation (carry can extend the result by one digit)

    Time: O(max(n, m)), Space: O(max(n, m)) for the result.
    """
    # TODO: implement this
    pass


def _sol_add_two_numbers(l1, l2):
    """Solution: Add two numbers as linked lists."""
    dummy = ListNode(0)
    curr = dummy
    carry = 0

    # Process both lists until both are exhausted AND no carry remains
    while l1 or l2 or carry:
        # Get values (0 if list is exhausted)
        v1 = l1.val if l1 else 0
        v2 = l2.val if l2 else 0

        # Compute sum and carry, just like grade school addition
        total = v1 + v2 + carry
        carry = total // 10
        digit = total % 10

        curr.next = ListNode(digit)
        curr = curr.next

        # Advance pointers if not exhausted
        if l1:
            l1 = l1.next
        if l2:
            l2 = l2.next

    return dummy.next


# ===========================================================================
# Exercise 4: Flatten a Multilevel Doubly Linked List
# ===========================================================================
# A node has val, next, and child. The child pointer may point to a separate
# linked list (which itself may have children). Flatten all levels into a
# single-level list using DFS order.
#
# Example:
#   1 - 2 - 3 - 4 - 5
#           |
#           6 - 7
#           |
#           8
# Flattened: 1 - 2 - 3 - 6 - 8 - 7 - 4 - 5
#
# Why this matters: This models real structures — file system directory
# flattening, DOM tree linearization, nested comment threads. The key
# insight is that "child" is just DFS branching, and flattening is a
# DFS traversal wired into a flat list.
# ===========================================================================

class MultiNode:
    """A node with next and child pointers (simplified — no prev for clarity)."""
    __slots__ = ('val', 'next', 'child')

    def __init__(self, val=0, nxt=None, child=None):
        self.val = val
        self.next = nxt
        self.child = child


def flatten_multilevel(head):
    """Flatten a multilevel linked list into a single-level list.

    Approach (iterative DFS using the list itself as a stack):
    1. Walk the list. When you encounter a node with a child:
       a. Find the tail of the child list
       b. Connect the child's tail to the current node's next
       c. Connect the current node's next to the child
       d. Clear the child pointer
    2. Continue walking — the child list is now inline

    Time: O(n) where n is total nodes across all levels.
    Space: O(1) — no explicit stack needed.
    """
    # TODO: implement this
    pass


def _sol_flatten_multilevel(head):
    """Solution: Flatten multilevel linked list."""
    curr = head
    while curr:
        if curr.child:
            # Find the tail of the child chain
            child_tail = curr.child
            while child_tail.next:
                child_tail = child_tail.next

            # Splice the child chain between curr and curr.next
            # child_tail connects to what was after curr
            child_tail.next = curr.next

            # curr now points to its child chain
            curr.next = curr.child

            # Clear the child pointer — it is now flattened
            curr.child = None

        curr = curr.next

    return head


def multi_to_list(head):
    """Convert a flattened multilevel list to Python list (for testing)."""
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


# ===========================================================================
# Exercise 5: Reorder List
# ===========================================================================
# Given a list L0 -> L1 -> ... -> Ln-1 -> Ln,
# reorder it to: L0 -> Ln -> L1 -> Ln-1 -> L2 -> Ln-2 -> ...
#
# Example: [1,2,3,4] -> [1,4,2,3]
# Example: [1,2,3,4,5] -> [1,5,2,4,3]
#
# Why this matters: This combines three fundamental operations:
# 1. Finding the middle (slow/fast pointers)
# 2. Reversing a list (pointer reversal)
# 3. Merging two lists (interleaving)
# It is the synthesis exercise — if you can do this cleanly, you have
# mastered the core linked list manipulation toolkit.
# ===========================================================================

def reorder_list(head):
    """Reorder the list in-place to L0->Ln->L1->Ln-1->...

    Approach:
    1. Find the middle of the list (slow/fast pointers)
    2. Reverse the second half
    3. Merge the first half and reversed second half by interleaving

    Time: O(n), Space: O(1).
    """
    # TODO: implement this
    pass


def _sol_reorder_list(head):
    """Solution: Reorder list L0->Ln->L1->Ln-1->..."""
    if not head or not head.next:
        return head

    # Step 1: Find the middle
    # After this, slow is the last node of the first half
    slow = head
    fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    # Step 2: Reverse the second half
    # second_half starts at slow.next
    prev = None
    curr = slow.next
    slow.next = None  # Sever the two halves

    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    # prev is now the head of the reversed second half

    # Step 3: Interleave the two halves
    # Take one node from first half, then one from reversed second half
    first = head
    second = prev
    while second:
        # Save next pointers before rewiring
        tmp1 = first.next
        tmp2 = second.next

        first.next = second    # first -> second
        second.next = tmp1     # second -> next_first

        first = tmp1           # advance first
        second = tmp2          # advance second

    return head


# ===========================================================================
# Test runner
# ===========================================================================

def run_tests():
    """Run all exercise tests. Uses solution functions to verify correctness."""
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  [PASS] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name}: got {got}, expected {expected}")
            failed += 1

    # --- Exercise 1: Reverse in groups of k ---
    print("\nExercise 1: Reverse Nodes in Groups of K")
    test_fn = reverse_k_group if reverse_k_group(list_to_linked([1, 2]), 2) is not None else _sol_reverse_k_group

    cases1 = [
        ([1, 2, 3, 4, 5], 2, [2, 1, 4, 3, 5]),
        ([1, 2, 3, 4, 5], 3, [3, 2, 1, 4, 5]),
        ([1, 2, 3, 4], 2, [2, 1, 4, 3]),
        ([1, 2, 3, 4], 4, [4, 3, 2, 1]),
        ([1], 1, [1]),
        ([1, 2], 3, [1, 2]),
    ]
    for arr, k, expected in cases1:
        result = linked_to_list(test_fn(list_to_linked(arr), k))
        check(f"reverse_k_group({arr}, k={k})", result, expected)

    # --- Exercise 2: Remove n-th from end ---
    print("\nExercise 2: Remove N-th Node from End")
    test_fn = remove_nth_from_end if remove_nth_from_end(list_to_linked([1, 2]), 1) is not None else _sol_remove_nth_from_end

    cases2 = [
        ([1, 2, 3, 4, 5], 2, [1, 2, 3, 5]),
        ([1, 2, 3, 4, 5], 1, [1, 2, 3, 4]),
        ([1, 2, 3, 4, 5], 5, [2, 3, 4, 5]),
        ([1], 1, []),
        ([1, 2], 2, [2]),
    ]
    for arr, n, expected in cases2:
        result = linked_to_list(test_fn(list_to_linked(arr), n))
        check(f"remove_nth_from_end({arr}, n={n})", result, expected)

    # --- Exercise 3: Add two numbers ---
    print("\nExercise 3: Add Two Numbers as Linked Lists")
    test_fn = add_two_numbers if add_two_numbers(list_to_linked([1]), list_to_linked([1])) is not None else _sol_add_two_numbers

    cases3 = [
        ([2, 4, 3], [5, 6, 4], [7, 0, 8]),        # 342 + 465 = 807
        ([9, 9, 9], [1], [0, 0, 0, 1]),            # 999 + 1 = 1000
        ([0], [0], [0]),                             # 0 + 0 = 0
        ([9, 9], [9, 9, 9], [8, 9, 0, 1]),         # 99 + 999 = 1098
        ([5], [5], [0, 1]),                          # 5 + 5 = 10
    ]
    for a, b, expected in cases3:
        result = linked_to_list(test_fn(list_to_linked(a), list_to_linked(b)))
        check(f"add_two_numbers({a}, {b})", result, expected)

    # --- Exercise 4: Flatten multilevel list ---
    print("\nExercise 4: Flatten Multilevel Linked List")

    # Build test structure:
    #   1 - 2 - 3 - 4 - 5
    #           |
    #           6 - 7
    #           |
    #           8
    def build_multi_test():
        n1 = MultiNode(1)
        n2 = MultiNode(2)
        n3 = MultiNode(3)
        n4 = MultiNode(4)
        n5 = MultiNode(5)
        n6 = MultiNode(6)
        n7 = MultiNode(7)
        n8 = MultiNode(8)
        n1.next = n2; n2.next = n3; n3.next = n4; n4.next = n5
        n3.child = n6; n6.next = n7
        n6.child = n8
        return n1

    test_fn = flatten_multilevel if flatten_multilevel(build_multi_test()) is not None else _sol_flatten_multilevel
    result = multi_to_list(test_fn(build_multi_test()))
    check("flatten [1-2-3(6(8)-7)-4-5]", result, [1, 2, 3, 6, 8, 7, 4, 5])

    # Simple case: no children
    n1 = MultiNode(1); n2 = MultiNode(2); n3 = MultiNode(3)
    n1.next = n2; n2.next = n3
    result = multi_to_list(test_fn(n1))
    check("flatten [1-2-3] (no children)", result, [1, 2, 3])

    # Single child
    n1 = MultiNode(1); n2 = MultiNode(2); n3 = MultiNode(3)
    n1.next = n2; n1.child = n3
    # Need fresh nodes for test_fn
    n1 = MultiNode(1); n2 = MultiNode(2); n3 = MultiNode(3)
    n1.next = n2; n1.child = n3
    result = multi_to_list(test_fn(n1))
    check("flatten [1(3)-2]", result, [1, 3, 2])

    # --- Exercise 5: Reorder list ---
    print("\nExercise 5: Reorder List")
    test_fn = reorder_list if reorder_list(list_to_linked([1, 2, 3, 4])) is not None else _sol_reorder_list

    cases5 = [
        ([1, 2, 3, 4], [1, 4, 2, 3]),
        ([1, 2, 3, 4, 5], [1, 5, 2, 4, 3]),
        ([1, 2, 3], [1, 3, 2]),
        ([1, 2], [1, 2]),
        ([1], [1]),
    ]
    for arr, expected in cases5:
        head = list_to_linked(arr)
        result_head = test_fn(head)
        # reorder_list may return None (modifies in-place), so use head if None
        result = linked_to_list(result_head if result_head else head)
        check(f"reorder_list({arr})", result, expected)

    # --- Summary ---
    total = passed + failed
    print(f"\n{'=' * 40}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All tests passed!")
    else:
        print(f"{failed} test(s) failed — review your implementations.")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    run_tests()
