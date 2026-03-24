"""
Day 44: BST to Sorted Array and Back
======================================
Conversions between BSTs and sorted representations: arrays, doubly linked
lists, and other BSTs. These are the maintenance operations that keep tree-
based indexes fast in databases and file systems.

Core insight: a BST's inorder traversal is sorted, and a sorted sequence
can reconstruct a balanced BST. This bidirectional relationship enables
rebalancing, bulk loading, merging, and serialization.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list, inorder_recursive


# ─── Sorted Array to Balanced BST ────────────────────────────────────

def sorted_array_to_bst(arr):
    """Convert a sorted array to a height-balanced BST.

    Strategy: binary search on the array. The middle element becomes the
    root, guaranteeing equal-sized subtrees. This is the same partitioning
    logic as binary search — and for the same reason (halving gives O(log n)
    depth).

    Time:  O(n) — each element becomes exactly one node
    Space: O(log n) — recursion depth on balanced splits
    """
    if not arr:
        return None

    def build(lo, hi):
        if lo > hi:
            return None
        mid = lo + (hi - lo) // 2
        node = TreeNode(arr[mid])
        node.left = build(lo, mid - 1)
        node.right = build(mid + 1, hi)
        return node

    return build(0, len(arr) - 1)


# ─── BST to Sorted Array ─────────────────────────────────────────────

def bst_to_sorted_array(root):
    """Extract sorted array from BST via inorder traversal.

    The BST invariant (left < root < right) means inorder traversal
    visits nodes in ascending order. This is why BSTs are used for
    ordered data — you get sorting for free.

    Time:  O(n)
    Space: O(n) for output, O(h) for call stack
    """
    result = []

    def inorder(node):
        if node is None:
            return
        inorder(node.left)
        result.append(node.val)
        inorder(node.right)

    inorder(root)
    return result


# ─── BST to Sorted Circular Doubly Linked List (In-Place) ────────────

def bst_to_sorted_dll(root):
    """Convert BST to sorted circular doubly linked list in-place.

    Rewires existing tree pointers:
        node.left  -> prev pointer
        node.right -> next pointer

    Uses inorder traversal to visit nodes in sorted order, linking
    each node to its predecessor. The final step connects head and
    tail to make it circular.

    Why circular? O(1) access to both min (head) and max (head.left),
    which is useful for range queries and merge operations.

    Time:  O(n)
    Space: O(h) for recursion stack (could be O(1) with Morris)

    Returns: head of the circular DLL (the smallest element)
    """
    if root is None:
        return None

    # Track the previously visited node and the head of the list
    first = None  # smallest node — will be DLL head
    last = None   # tracks the previous node during inorder

    def inorder(node):
        nonlocal first, last
        if node is None:
            return

        inorder(node.left)

        # Process current node: link it to the previous node
        if last is None:
            # First node in inorder — this is the minimum
            first = node
        else:
            # Link previous node's next to current
            last.right = node
            # Link current node's prev to previous
            node.left = last

        last = node

        inorder(node.right)

    inorder(root)

    # Make it circular: connect head and tail
    first.left = last
    last.right = first

    return first


# ─── Sorted DLL to Balanced BST ──────────────────────────────────────

def sorted_dll_to_bst(head, n):
    """Convert sorted circular doubly linked list back to balanced BST.

    Strategy: inorder construction. Instead of random-accessing the middle
    element (which would be O(n) in a linked list), we consume nodes from
    left to right — exactly matching inorder traversal order.

    1. Recursively build left subtree of size n//2
    2. Current head becomes root
    3. Advance head
    4. Recursively build right subtree of size n - n//2 - 1

    The mutable list [head] lets us advance the pointer across recursive
    calls — Python's closures capture the list object, not the reference.

    Time:  O(n)
    Space: O(log n) recursion stack
    """
    if n <= 0 or head is None:
        return None

    # Break circularity first to avoid infinite traversal
    tail = head.left
    if tail is not None:
        head.left = None
        tail.right = None

    current = [head]  # mutable container to track position

    def build(size):
        if size <= 0:
            return None

        # Build left subtree first (inorder: left before root)
        left = build(size // 2)

        # Current node becomes root
        root = current[0]
        root.left = left
        current[0] = current[0].right  # advance to next node

        # Build right subtree
        root.right = build(size - size // 2 - 1)
        return root

    return build(n)


# ─── Merge Two BSTs ──────────────────────────────────────────────────

def merge_two_bsts(root1, root2):
    """Merge two BSTs into a single balanced BST.

    Pipeline:
    1. Convert both BSTs to sorted arrays — O(m), O(n)
    2. Merge the two sorted arrays      — O(m + n)
    3. Build balanced BST from merged    — O(m + n)

    Total: O(m + n) time and space.

    This is optimal: you must examine every node at least once,
    and the merge step is the same as merge sort's merge operation.
    """
    # Step 1: BST -> sorted arrays
    arr1 = bst_to_sorted_array(root1)
    arr2 = bst_to_sorted_array(root2)

    # Step 2: merge two sorted arrays
    merged = []
    i, j = 0, 0
    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            merged.append(arr1[i])
            i += 1
        else:
            merged.append(arr2[j])
            j += 1
    merged.extend(arr1[i:])
    merged.extend(arr2[j:])

    # Step 3: sorted array -> balanced BST
    return sorted_array_to_bst(merged)


# ─── Flatten BST to Right-Skewed Sorted List ─────────────────────────

def flatten_bst_to_sorted_list(root):
    """Flatten BST in-place to a right-skewed linked list (sorted order).

    Every node ends up with left=None, right=next larger element.
    This is useful for simple sequential iteration without a stack.

    Strategy: reverse inorder (right, root, left) and link each node
    to the previously processed node. This builds the list from tail
    to head, avoiding the need to find the end.

    Time:  O(n)
    Space: O(h) recursion stack
    """
    if root is None:
        return None

    prev = [None]  # previously processed node (starts from largest)

    def reverse_inorder(node):
        if node is None:
            return
        reverse_inorder(node.right)

        # Link current node to the previously processed node
        node.right = prev[0]
        node.left = None
        prev[0] = node

        reverse_inorder(node.left)

    # IMPORTANT: save left/right before modification could corrupt traversal
    # We need a different approach — collect nodes first, then rewire
    nodes = []

    def inorder(node):
        if node is None:
            return
        inorder(node.left)
        nodes.append(node)
        inorder(node.right)

    inorder(root)

    # Rewire: each node points right to next, left to None
    for i in range(len(nodes) - 1):
        nodes[i].left = None
        nodes[i].right = nodes[i + 1]
    nodes[-1].left = None
    nodes[-1].right = None

    return nodes[0]


# ─── Balance BST ──────────────────────────────────────────────────────

def balance_bst(root):
    """Rebalance an unbalanced BST.

    The naive but correct approach:
    1. Extract sorted array via inorder — O(n)
    2. Build balanced BST from sorted array — O(n)

    Total: O(n) time and space.

    This is the "sledgehammer" rebalancing approach. Self-balancing trees
    (AVL, Red-Black) avoid this by maintaining balance incrementally via
    rotations. But for a one-time rebalance of a badly degraded tree,
    this is simple and optimal.

    Production systems (e.g., database index rebuild) use exactly this
    approach: dump the index to a sorted file, then bulk-load a new
    balanced tree.
    """
    arr = bst_to_sorted_array(root)
    return sorted_array_to_bst(arr)


# ─── Helper Utilities ────────────────────────────────────────────────

def _get_height(node):
    """Get height of a tree."""
    if node is None:
        return -1
    return 1 + max(_get_height(node.left), _get_height(node.right))


def _is_balanced(node):
    """Check if tree is height-balanced (height diff <= 1 at every node)."""
    def check(n):
        if n is None:
            return 0, True
        lh, lb = check(n.left)
        rh, rb = check(n.right)
        balanced = lb and rb and abs(lh - rh) <= 1
        return 1 + max(lh, rh), balanced
    _, result = check(node)
    return result


def _is_bst(node, lo=float('-inf'), hi=float('inf')):
    """Validate BST property."""
    if node is None:
        return True
    if node.val <= lo or node.val >= hi:
        return False
    return _is_bst(node.left, lo, node.val) and _is_bst(node.right, node.val, hi)


def _dll_to_list(head):
    """Convert circular DLL to a Python list (for testing)."""
    if head is None:
        return []
    result = [head.val]
    current = head.right
    while current is not head:
        result.append(current.val)
        current = current.right
    return result


def _count_dll(head):
    """Count nodes in a circular DLL."""
    if head is None:
        return 0
    count = 1
    current = head.right
    while current is not head:
        count += 1
        current = current.right
    return count


def _collect_right_skewed(root):
    """Collect values from a right-skewed list."""
    result = []
    while root:
        assert root.left is None, "Left pointer should be None in flattened tree"
        result.append(root.val)
        root = root.right
    return result


# ─── Demo ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Day 44: BST <-> Sorted Structure Conversions")
    print("=" * 60)

    # --- sorted array -> balanced BST ---
    print("\n── Sorted Array -> Balanced BST ──")
    arr = [1, 2, 3, 4, 5, 6, 7]
    bst = sorted_array_to_bst(arr)
    print(f"  Input:    {arr}")
    print(f"  Inorder:  {bst_to_sorted_array(bst)}")
    print(f"  Height:   {_get_height(bst)}")
    print(f"  Balanced: {_is_balanced(bst)}")
    print(f"  Valid BST: {_is_bst(bst)}")

    # --- BST -> sorted array ---
    print("\n── BST -> Sorted Array ──")
    tree = from_list([8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15])
    result = bst_to_sorted_array(tree)
    print(f"  Inorder: {result}")
    print(f"  Sorted:  {result == sorted(result)}")

    # --- BST -> circular DLL ---
    print("\n── BST -> Circular Doubly Linked List ──")
    tree = from_list([4, 2, 5, 1, 3])
    dll_head = bst_to_sorted_dll(tree)
    values = _dll_to_list(dll_head)
    print(f"  DLL forward:  {values}")
    print(f"  Head (min):   {dll_head.val}")
    print(f"  Tail (max):   {dll_head.left.val}")
    print(f"  Circular:     head.left.right == head -> {dll_head.left.right is dll_head}")

    # --- DLL -> balanced BST ---
    print("\n── Circular DLL -> Balanced BST ──")
    # Build a fresh DLL
    tree2 = from_list([4, 2, 6, 1, 3, 5, 7])
    dll_head2 = bst_to_sorted_dll(tree2)
    n = _count_dll(dll_head2)
    new_bst = sorted_dll_to_bst(dll_head2, n)
    print(f"  DLL had {n} nodes")
    print(f"  New BST inorder: {bst_to_sorted_array(new_bst)}")
    print(f"  Balanced: {_is_balanced(new_bst)}")
    print(f"  Valid BST: {_is_bst(new_bst)}")

    # --- Merge two BSTs ---
    print("\n── Merge Two BSTs ──")
    bst1 = from_list([2, 1, 3])
    bst2 = from_list([6, 5, 7])
    merged = merge_two_bsts(bst1, bst2)
    print(f"  BST1 inorder: {bst_to_sorted_array(from_list([2, 1, 3]))}")
    print(f"  BST2 inorder: {bst_to_sorted_array(from_list([6, 5, 7]))}")
    print(f"  Merged inorder: {bst_to_sorted_array(merged)}")
    print(f"  Balanced: {_is_balanced(merged)}")
    print(f"  Valid BST: {_is_bst(merged)}")

    # --- Flatten BST ---
    print("\n── Flatten BST to Right-Skewed List ──")
    tree3 = from_list([4, 2, 6, 1, 3, 5, 7])
    flat_head = flatten_bst_to_sorted_list(tree3)
    flat_vals = _collect_right_skewed(flat_head)
    print(f"  Flattened: {flat_vals}")
    print(f"  All left pointers None: True")

    # --- Balance BST ---
    print("\n── Rebalance a Degenerate BST ──")
    # Build a right-skewed tree manually
    degenerate = TreeNode(1)
    degenerate.right = TreeNode(2)
    degenerate.right.right = TreeNode(3)
    degenerate.right.right.right = TreeNode(4)
    degenerate.right.right.right.right = TreeNode(5)
    print(f"  Before — height: {_get_height(degenerate)}, balanced: {_is_balanced(degenerate)}")
    balanced = balance_bst(degenerate)
    print(f"  After  — height: {_get_height(balanced)}, balanced: {_is_balanced(balanced)}")
    print(f"  Inorder preserved: {bst_to_sorted_array(balanced)}")
    print(f"  Valid BST: {_is_bst(balanced)}")

    print(f"\n{'=' * 60}")
    print("All conversions demonstrated successfully.")
