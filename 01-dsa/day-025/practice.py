"""
Day 25 Practice: XOR Linked List Exercises

4 exercises that deepen understanding of XOR pointer compression.
Each has a TODO stub and a _sol_ solution below.

Run: python practice.py
"""

from xor_linked_list import XORNode, XORLinkedList


# ============================================================
# Exercise 1: Reverse XOR List in O(1)
# ============================================================
# WHY this is interesting: In a standard doubly-linked list, reversing
# requires O(n) traversal to swap every node's prev/next pointers.
# An XOR list stores prev^next — this value is DIRECTION-AGNOSTIC.
# Swapping head and tail is all you need. The XOR fields don't change.

def reverse_xor_list(xll):
    """Reverse the XOR linked list in O(1) time and O(1) space.

    Args:
        xll: XORLinkedList to reverse in place.

    Returns:
        The same XORLinkedList, now reversed.

    Hint: Think about what determines traversal direction. The npx values
    encode prev^next, which is symmetric — it's the SAME from either side.
    What two things define which direction "forward" means?
    """
    # TODO: Implement O(1) reversal
    pass


def _sol_reverse_xor_list(xll):
    """Solution: Just swap head and tail.

    WHY this works: npx = prev ^ next is the same regardless of direction.
    Forward traversal starts at head with prev_id=0 and follows next.
    Backward traversal starts at tail with next_id=0 and follows prev.
    Swapping head/tail makes "forward" go the other way — no node changes needed.

    Compare to standard doubly-linked list where you must visit every node
    to swap its prev and next pointers — that's O(n).
    """
    xll.head_id, xll.tail_id = xll.tail_id, xll.head_id
    return xll


# ============================================================
# Exercise 2: Find Middle Element
# ============================================================
# WHY: Classic slow/fast pointer technique adapted to XOR linked lists.
# The wrinkle: you must track previous IDs for both pointers since
# XOR traversal needs the previous address to compute the next one.

def find_middle(xll):
    """Find the middle element of the XOR linked list.

    For even-length lists, return the second of the two middle elements.
    For empty lists, return None.

    Args:
        xll: XORLinkedList to search.

    Returns:
        The data value of the middle node, or None if empty.

    Hint: Use slow/fast pointer technique. Both pointers need their own
    prev_id tracking since XOR traversal requires knowing where you came from.
    """
    # TODO: Implement using slow/fast pointers
    pass


def _sol_find_middle(xll):
    """Solution: Slow/fast pointers with separate prev tracking.

    WHY we need two prev trackers: In a standard list, slow.next and
    fast.next.next are simple dereferences. In XOR, computing "next"
    requires knowing "prev" — so each pointer needs its own history.
    """
    if xll.head_id == 0:
        return None

    # Slow pointer state
    slow_prev_id = 0
    slow_curr_id = xll.head_id

    # Fast pointer state
    fast_prev_id = 0
    fast_curr_id = xll.head_id

    while fast_curr_id != 0:
        fast_node = xll._get_node(fast_curr_id)
        fast_next_id = fast_node.npx ^ fast_prev_id

        # Try to advance fast by 2
        if fast_next_id == 0:
            # Fast is at the last node (odd length) — slow is at middle
            break

        fast_next_node = xll._get_node(fast_next_id)
        fast_next_next_id = fast_next_node.npx ^ fast_curr_id

        # Advance fast by 2
        fast_prev_id = fast_next_id
        fast_curr_id = fast_next_next_id

        # Advance slow by 1
        slow_node = xll._get_node(slow_curr_id)
        slow_next_id = slow_node.npx ^ slow_prev_id
        slow_prev_id = slow_curr_id
        slow_curr_id = slow_next_id

    return xll._get_node(slow_curr_id).data


# ============================================================
# Exercise 3: Memory Comparison vs Standard Doubly-Linked List
# ============================================================
# WHY: The whole point of XOR linked lists is saving memory.
# This exercise makes you quantify exactly how much, so you can
# decide when the complexity trade-off is justified.

def memory_comparison(n):
    """Compare memory overhead of XOR vs standard doubly-linked list.

    Assume 64-bit system (8 bytes per pointer/id).
    Only count POINTER overhead, not the data payload.

    Args:
        n: Number of nodes.

    Returns:
        dict with keys:
            'doubly_linked_bytes': total pointer overhead for doubly-linked
            'xor_linked_bytes': total pointer overhead for XOR linked list
            'savings_bytes': bytes saved by XOR approach
            'savings_percent': percentage saved (float, 0-100)

    Hint: A doubly-linked node has 2 pointers (prev, next).
    An XOR node has 1 field (npx). Both lists also need head/tail pointers.
    """
    # TODO: Calculate and return the comparison dict
    pass


def _sol_memory_comparison(n):
    """Solution: Straightforward arithmetic.

    WHY the savings scale linearly: Each node saves exactly one pointer.
    For n=1,000,000 nodes on 64-bit: saves ~7.6 MB.
    That's meaningful in embedded systems but irrelevant on a server with 64 GB.

    The list-level overhead (head + tail pointers) is constant and identical
    for both — 2 pointers each. It only matters when n is very small.
    """
    pointer_size = 8  # bytes on 64-bit

    # Per-node pointer overhead
    # Doubly-linked: prev pointer + next pointer = 2 * 8
    # XOR linked: npx field = 1 * 8
    doubly_per_node = 2 * pointer_size
    xor_per_node = 1 * pointer_size

    # List-level overhead: head + tail pointers (same for both)
    list_overhead = 2 * pointer_size

    doubly_total = n * doubly_per_node + list_overhead
    xor_total = n * xor_per_node + list_overhead

    savings = doubly_total - xor_total
    savings_pct = (savings / doubly_total * 100) if doubly_total > 0 else 0.0

    return {
        'doubly_linked_bytes': doubly_total,
        'xor_linked_bytes': xor_total,
        'savings_bytes': savings,
        'savings_percent': round(savings_pct, 2),
    }


# ============================================================
# Exercise 4: Merge Two XOR Linked Lists
# ============================================================
# WHY: Merging tests whether you truly understand how npx fields
# are maintained. You must correctly update the tail of list1
# and the head of list2 so the XOR chain is unbroken across the join.

def merge_xor_lists(xll1, xll2):
    """Merge xll2 onto the end of xll1. Modifies xll1 in place.

    After merge: xll1 contains all elements of xll1 followed by xll2.
    xll2 becomes empty.

    Args:
        xll1: First XOR linked list (will contain merged result).
        xll2: Second XOR linked list (will be emptied).

    Returns:
        xll1 (the merged list).

    Hint: The join point is xll1's tail and xll2's head. Both nodes'
    npx values must be updated to include each other. Think about
    what the tail's npx currently encodes (prev ^ 0) and what it
    should become (prev ^ xll2_head).
    """
    # TODO: Implement the merge
    pass


def _sol_merge_xor_lists(xll1, xll2):
    """Solution: Update the join point's npx fields and merge registries.

    WHY the npx updates work:
    - xll1's tail currently has npx = tail_prev ^ 0 (next is NULL)
      It must become: tail_prev ^ xll2_head_id
      Since tail_prev = npx ^ 0 = npx, new npx = old_npx ^ xll2_head_id

    - xll2's head currently has npx = 0 ^ head_next (prev is NULL)
      It must become: xll1_tail_id ^ head_next
      Since head_next = npx ^ 0 = npx, new npx = xll1_tail_id ^ old_npx
    """
    # Handle edge cases
    if xll2.head_id == 0:
        return xll1  # Nothing to merge
    if xll1.head_id == 0:
        # xll1 is empty, just take xll2's state
        xll1.head_id = xll2.head_id
        xll1.tail_id = xll2.tail_id
        xll1.registry = {**xll1.registry, **xll2.registry}
        xll1.size = xll2.size
        xll2.head_id = 0
        xll2.tail_id = 0
        xll2.registry.clear()
        xll2.size = 0
        return xll1

    # Update xll1's tail: its "next" changes from 0 to xll2's head
    tail1 = xll1._get_node(xll1.tail_id)
    # Old npx = prev ^ 0, new npx = prev ^ xll2.head_id
    # XOR with 0 cancels nothing; XOR with xll2.head_id adds the link
    tail1.npx = tail1.npx ^ xll2.head_id

    # Update xll2's head: its "prev" changes from 0 to xll1's tail
    head2 = xll2._get_node(xll2.head_id)
    # Old npx = 0 ^ next, new npx = xll1.tail_id ^ next
    head2.npx = xll1.tail_id ^ head2.npx

    # Merge metadata
    xll1.tail_id = xll2.tail_id
    xll1.registry.update(xll2.registry)
    xll1.size += xll2.size

    # Empty out xll2
    xll2.head_id = 0
    xll2.tail_id = 0
    xll2.registry.clear()
    xll2.size = 0

    return xll1


# ============================================================
# Test Runner
# ============================================================

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
            print(f"    Expected: {expected}")
            print(f"    Got:      {got}")
            failed += 1

    # --- Exercise 1: Reverse ---
    print("\nExercise 1: Reverse XOR List in O(1)")
    xll = XORLinkedList()
    for v in [10, 20, 30, 40]:
        xll.insert_back(v)

    # Test student solution
    result = reverse_xor_list(xll)
    if result is not None:
        check("reverse forward", result.traverse_forward(), [40, 30, 20, 10])
        check("reverse backward", result.traverse_backward(), [10, 20, 30, 40])
    else:
        # Fall back to reference solution
        xll2 = XORLinkedList()
        for v in [10, 20, 30, 40]:
            xll2.insert_back(v)
        result = _sol_reverse_xor_list(xll2)
        check("reverse forward (ref)", result.traverse_forward(), [40, 30, 20, 10])
        check("reverse backward (ref)", result.traverse_backward(), [10, 20, 30, 40])

    # --- Exercise 2: Find Middle ---
    print("\nExercise 2: Find Middle Element")
    xll_odd = XORLinkedList()
    for v in [1, 2, 3, 4, 5]:
        xll_odd.insert_back(v)

    xll_even = XORLinkedList()
    for v in [1, 2, 3, 4]:
        xll_even.insert_back(v)

    xll_one = XORLinkedList()
    xll_one.insert_back(42)

    xll_empty = XORLinkedList()

    mid_odd = find_middle(xll_odd)
    mid_even = find_middle(xll_even)
    mid_one = find_middle(xll_one)
    mid_empty = find_middle(xll_empty)

    if mid_odd is not None or mid_even is not None:
        check("middle of [1,2,3,4,5]", mid_odd, 3)
        check("middle of [1,2,3,4]", mid_even, 3)
        check("middle of [42]", mid_one, 42)
        check("middle of []", mid_empty, None)
    else:
        check("middle of [1,2,3,4,5] (ref)", _sol_find_middle(xll_odd), 3)
        check("middle of [1,2,3,4] (ref)", _sol_find_middle(xll_even), 3)
        check("middle of [42] (ref)", _sol_find_middle(xll_one), 42)
        check("middle of [] (ref)", _sol_find_middle(xll_empty), None)

    # --- Exercise 3: Memory Comparison ---
    print("\nExercise 3: Memory Comparison")
    result = memory_comparison(1000)
    if result is not None:
        check("doubly_linked_bytes", result['doubly_linked_bytes'], 16016)
        check("xor_linked_bytes", result['xor_linked_bytes'], 8016)
        check("savings_bytes", result['savings_bytes'], 8000)
        check("savings_percent", result['savings_percent'], 49.95)
    else:
        result = _sol_memory_comparison(1000)
        check("doubly_linked_bytes (ref)", result['doubly_linked_bytes'], 16016)
        check("xor_linked_bytes (ref)", result['xor_linked_bytes'], 8016)
        check("savings_bytes (ref)", result['savings_bytes'], 8000)
        check("savings_percent (ref)", result['savings_percent'], 49.95)

    # Large scale — this is where XOR lists actually matter
    big = _sol_memory_comparison(1_000_000)
    print(f"\n  At 1M nodes: save {big['savings_bytes'] / 1024 / 1024:.1f} MB "
          f"({big['savings_percent']}%)")

    # --- Exercise 4: Merge ---
    print("\nExercise 4: Merge Two XOR Linked Lists")
    xll_a = XORLinkedList()
    for v in [1, 2, 3]:
        xll_a.insert_back(v)

    xll_b = XORLinkedList()
    for v in [4, 5, 6]:
        xll_b.insert_back(v)

    merged = merge_xor_lists(xll_a, xll_b)
    if merged is not None:
        check("merged forward", merged.traverse_forward(), [1, 2, 3, 4, 5, 6])
        check("merged backward", merged.traverse_backward(), [6, 5, 4, 3, 2, 1])
        check("merged size", len(merged), 6)
    else:
        # Rebuild for reference solution
        xll_a2 = XORLinkedList()
        for v in [1, 2, 3]:
            xll_a2.insert_back(v)
        xll_b2 = XORLinkedList()
        for v in [4, 5, 6]:
            xll_b2.insert_back(v)
        merged = _sol_merge_xor_lists(xll_a2, xll_b2)
        check("merged forward (ref)", merged.traverse_forward(), [1, 2, 3, 4, 5, 6])
        check("merged backward (ref)", merged.traverse_backward(), [6, 5, 4, 3, 2, 1])
        check("merged size (ref)", len(merged), 6)

    # Edge case: merge with empty list
    xll_c = XORLinkedList()
    for v in [7, 8]:
        xll_c.insert_back(v)
    xll_empty2 = XORLinkedList()
    merged2 = _sol_merge_xor_lists(xll_c, xll_empty2)
    check("merge with empty", merged2.traverse_forward(), [7, 8])

    # Summary
    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    run_tests()
