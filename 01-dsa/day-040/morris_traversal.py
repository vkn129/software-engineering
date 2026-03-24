"""
Day 40: Morris Traversal — O(1) Space Inorder Without Stack
=============================================================
The core insight: a tree with n nodes has n+1 null pointers sitting unused.
Morris temporarily repurposes these null pointers as "threads" — backward
links to ancestor nodes — enabling traversal without a stack or recursion.

Time: O(n) for all variants (each edge traversed at most twice)
Space: O(1) extra (no stack, no recursion)

Tradeoff: temporarily mutates the tree structure during traversal.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list, inorder_recursive, preorder_recursive


# ─── Morris Inorder Traversal ───────────────────────────────────────

def morris_inorder(root):
    """Inorder traversal using O(1) extra space.

    Algorithm:
        For each node, we need to return to it after processing its left
        subtree. Instead of using a stack, we create a temporary "thread"
        from the inorder predecessor (rightmost node in left subtree)
        back to the current node.

        Each node is encountered twice:
        1. First time: create thread, go left
        2. Second time: thread already exists → remove it, process node, go right

    Why O(n) time despite nested loops:
        The inner while loop (finding predecessor) traverses edges. Each of
        the n-1 edges in the tree is traversed at most 2 times total across
        the entire algorithm. So total inner-loop work = O(n).
    """
    result = []
    current = root

    while current is not None:
        if current.left is None:
            # No left subtree — process this node immediately.
            # If we arrived here via a thread, current.right points
            # back to the ancestor (the thread).
            result.append(current.val)
            current = current.right  # move right (or follow thread)
        else:
            # Find the inorder predecessor: rightmost node in left subtree.
            # Stop if we hit None (first visit) or current (thread exists).
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right

            if predecessor.right is None:
                # FIRST VISIT: predecessor's right is null.
                # Create thread: predecessor.right → current
                # Then move left to process the left subtree.
                predecessor.right = current
                current = current.left
            else:
                # SECOND VISIT: predecessor.right == current (thread exists).
                # Left subtree is fully processed.
                # Remove the thread (restore the tree).
                # Process current node.
                predecessor.right = None  # restore original structure
                result.append(current.val)
                current = current.right

    return result


# ─── Morris Preorder Traversal ──────────────────────────────────────

def morris_preorder(root):
    """Preorder traversal using O(1) extra space.

    The ONLY difference from inorder: we process the node on the FIRST
    encounter (when creating the thread) instead of the second.

    Inorder:  process on second visit (after left subtree done)
    Preorder: process on first visit (before going left)
    """
    result = []
    current = root

    while current is not None:
        if current.left is None:
            # No left subtree — process and move right
            result.append(current.val)
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right

            if predecessor.right is None:
                # FIRST VISIT: process NOW (preorder = root before children)
                result.append(current.val)
                predecessor.right = current  # create thread
                current = current.left
            else:
                # SECOND VISIT: left subtree done, just remove thread
                # Do NOT process again — we already did on first visit
                predecessor.right = None
                current = current.right

    return result


# ─── Practical Applications ─────────────────────────────────────────

def is_bst_morris(root):
    """Validate BST using Morris inorder — O(1) space, O(n) time.

    A BST's inorder traversal is strictly increasing.
    Instead of collecting all values and checking, we track the
    previous value and verify ordering as we go.

    Important: even after detecting an invalid ordering, we must
    complete the full traversal to remove all temporary threads
    and restore the tree structure.
    """
    current = root
    prev_val = float('-inf')
    is_valid = True

    while current is not None:
        if current.left is None:
            if current.val <= prev_val:
                is_valid = False
            prev_val = current.val
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right

            if predecessor.right is None:
                predecessor.right = current
                current = current.left
            else:
                predecessor.right = None
                if current.val <= prev_val:
                    is_valid = False
                prev_val = current.val
                current = current.right

    return is_valid


def kth_smallest_morris(root, k):
    """Find kth smallest element in BST using Morris — O(1) space.

    Since Morris inorder visits nodes in sorted order, we just count
    to k and return. No need to collect all values.

    Important: we must complete the full traversal even after finding
    the answer, to ensure all temporary threads are removed and the
    tree is restored to its original structure.

    Returns None if k is out of range.
    """
    current = root
    count = 0
    result = None

    while current is not None:
        if current.left is None:
            count += 1
            if count == k:
                result = current.val
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right

            if predecessor.right is None:
                predecessor.right = current
                current = current.left
            else:
                predecessor.right = None
                count += 1
                if count == k:
                    result = current.val
                current = current.right

    return result


# ─── Threaded Binary Tree ───────────────────────────────────────────

class ThreadedNode:
    """A node in a right-threaded binary tree.

    Unlike a regular TreeNode, we store a flag indicating whether
    the right pointer is a real child or a thread (pointer to
    inorder successor).

    This makes the threads permanent — no need to create/remove them
    during traversal like Morris does.
    """
    __slots__ = ('val', 'left', 'right', 'right_is_thread')

    def __init__(self, val, left=None, right=None, right_is_thread=False):
        self.val = val
        self.left = left
        self.right = right
        self.right_is_thread = right_is_thread

    def __repr__(self):
        suffix = " →thread" if self.right_is_thread else ""
        return f"ThreadedNode({self.val}{suffix})"


class ThreadedBinaryTree:
    """A right-threaded binary tree.

    Every node whose right child is None instead points to its
    inorder successor. The flag right_is_thread distinguishes
    real children from threads.

    Benefits over regular binary tree:
    - O(1) inorder successor lookup (no stack needed)
    - O(n) inorder traversal in O(1) space without modifying the tree
    - Efficient for repeated forward iteration (database cursors)

    Cost: insert/delete must maintain threading invariant.
    """

    def __init__(self):
        self.root = None

    def insert_bst(self, val):
        """Insert a value maintaining BST property and threading.

        After inserting a new leaf:
        - Its right pointer threads to its inorder successor
        - The inorder predecessor's thread (if any) updates to point to the new node
        """
        if self.root is None:
            self.root = ThreadedNode(val, right_is_thread=False)
            return

        parent = None
        current = self.root
        going_left = True

        # Find insertion point, respecting threads
        while current is not None:
            parent = current
            if val < current.val:
                going_left = True
                current = current.left  # left is always a real child or None
            elif val > current.val:
                going_left = False
                if current.right_is_thread:
                    current = None  # stop: right is a thread, not a child
                else:
                    current = current.right
            else:
                return  # duplicate, do nothing

        # Create new node
        new_node = ThreadedNode(val)

        if going_left:
            # New node is left child of parent.
            # Inorder successor of new node = parent (thread right to parent).
            new_node.right = parent
            new_node.right_is_thread = True
            parent.left = new_node
        else:
            # New node is right child of parent.
            # Inorder successor of new node = whatever parent was threaded to.
            new_node.right = parent.right
            new_node.right_is_thread = parent.right_is_thread
            parent.right = new_node
            parent.right_is_thread = False  # parent now has a real right child

    def inorder(self):
        """O(1) space inorder traversal using threads.

        Unlike Morris, this does NOT modify the tree. The threads are
        permanent, so we just follow them.

        Algorithm:
        1. Go to the leftmost node
        2. Process it
        3. If right is a thread, follow it to successor
        4. If right is a real child, go to leftmost node in right subtree
        """
        result = []
        current = self.root

        # Go to leftmost node
        while current is not None and current.left is not None:
            current = current.left

        while current is not None:
            result.append(current.val)

            if current.right_is_thread:
                # Follow thread to inorder successor
                current = current.right
            else:
                # Move to right child, then find its leftmost descendant
                current = current.right
                while current is not None and current.left is not None:
                    current = current.left

        return result

    def find_successor(self, val):
        """Find the inorder successor of a given value in O(h) time.

        Once we find the node, getting its successor is O(1) if threaded,
        or O(h) if it has a right child (must find leftmost in right subtree).
        """
        node = self._find(val)
        if node is None:
            return None

        if node.right_is_thread:
            return node.right.val if node.right else None

        # Has real right child: successor is leftmost in right subtree
        successor = node.right
        if successor is None:
            return None  # no right child and not threaded → largest node
        while successor.left is not None:
            successor = successor.left
        return successor.val

    def _find(self, val):
        """Find a node by value."""
        current = self.root
        while current is not None:
            if val == current.val:
                return current
            elif val < current.val:
                current = current.left
            else:
                if current.right_is_thread:
                    return None
                current = current.right
        return None


# ─── Step-by-Step Trace ─────────────────────────────────────────────

def morris_inorder_traced(root):
    """Morris inorder with detailed step-by-step output.

    Shows exactly when threads are created and removed,
    making the algorithm's behavior visible.
    """
    result = []
    current = root
    step = 0

    print("─── Morris Inorder Trace ───")
    print(f"    Starting at root: {root.val if root else 'None'}\n")

    while current is not None:
        step += 1
        if current.left is None:
            result.append(current.val)
            print(f"    Step {step}: node={current.val}, no left child")
            print(f"             → VISIT {current.val}")
            if current.right:
                print(f"             → move right to {current.right.val}")
            else:
                print(f"             → move right to None (done)")
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right

            if predecessor.right is None:
                predecessor.right = current
                print(f"    Step {step}: node={current.val}, predecessor={predecessor.val}")
                print(f"             → CREATE thread: {predecessor.val}.right → {current.val}")
                print(f"             → move left to {current.left.val}")
                current = current.left
            else:
                predecessor.right = None
                result.append(current.val)
                print(f"    Step {step}: node={current.val}, thread from {predecessor.val} found")
                print(f"             → REMOVE thread: {predecessor.val}.right → None")
                print(f"             → VISIT {current.val}")
                if current.right:
                    print(f"             → move right to {current.right.val}")
                else:
                    print(f"             → move right to None (done)")
                current = current.right

        print()

    print(f"    Result: {result}")
    return result


# ─── Demonstration ──────────────────────────────────────────────────

if __name__ == "__main__":
    # ── Basic Traversals ──
    #         4
    #        / \
    #       2   6
    #      / \ / \
    #     1  3 5  7
    bst = from_list([4, 2, 6, 1, 3, 5, 7])

    print("=" * 60)
    print("MORRIS TRAVERSAL — O(1) Space Tree Traversal")
    print("=" * 60)

    print("\nTree (BST):")
    print("        4")
    print("       / \\")
    print("      2   6")
    print("     / \\ / \\")
    print("    1  3 5  7")

    # Verify Morris matches recursive
    print("\n── Inorder Comparison ──")
    recursive_in = inorder_recursive(bst)
    morris_in = morris_inorder(bst)
    print(f"  Recursive: {recursive_in}")
    print(f"  Morris:    {morris_in}")
    assert recursive_in == morris_in, "Morris inorder mismatch!"
    print("  MATCH ✓")

    print("\n── Preorder Comparison ──")
    recursive_pre = preorder_recursive(bst)
    morris_pre = morris_preorder(bst)
    print(f"  Recursive: {recursive_pre}")
    print(f"  Morris:    {morris_pre}")
    assert recursive_pre == morris_pre, "Morris preorder mismatch!"
    print("  MATCH ✓")

    # ── Traced Inorder ──
    print("\n── Step-by-Step Morris Inorder ──")
    # Use a small tree for clarity
    #       4
    #      / \
    #     2   5
    #    / \
    #   1   3
    small = from_list([4, 2, 5, 1, 3])
    traced_result = morris_inorder_traced(small)

    # ── BST Validation ──
    print("\n── BST Validation (O(1) space) ──")
    print(f"  BST [4,2,6,1,3,5,7] is valid BST: {is_bst_morris(from_list([4, 2, 6, 1, 3, 5, 7]))}")
    print(f"  Non-BST [4,2,6,1,3,1,7] is valid BST: {is_bst_morris(from_list([4, 6, 2, 1, 3, 5, 7]))}")
    print(f"  Single node [5] is valid BST: {is_bst_morris(from_list([5]))}")
    print(f"  Empty tree is valid BST: {is_bst_morris(None)}")

    # ── Kth Smallest ──
    print("\n── Kth Smallest in BST (O(1) space) ──")
    bst2 = from_list([4, 2, 6, 1, 3, 5, 7])
    for k in range(1, 8):
        print(f"  k={k}: {kth_smallest_morris(bst2, k)}")
    print(f"  k=8 (out of range): {kth_smallest_morris(from_list([4, 2, 6, 1, 3, 5, 7]), 8)}")

    # ── Threaded Binary Tree ──
    print("\n── Threaded Binary Tree ──")
    tbt = ThreadedBinaryTree()
    for val in [4, 2, 6, 1, 3, 5, 7]:
        tbt.insert_bst(val)

    print(f"  Inorder (using permanent threads): {tbt.inorder()}")
    assert tbt.inorder() == [1, 2, 3, 4, 5, 6, 7], "Threaded inorder mismatch!"
    print("  MATCH ✓")

    print("\n  Successor lookups:")
    for val in [1, 2, 3, 4, 5, 6, 7]:
        succ = tbt.find_successor(val)
        print(f"    successor({val}) = {succ}")

    # ── Verify Tree Restoration ──
    print("\n── Tree Integrity After Morris ──")
    bst3 = from_list([4, 2, 6, 1, 3, 5, 7])
    original_inorder = inorder_recursive(bst3)
    morris_result = morris_inorder(bst3)
    after_inorder = inorder_recursive(bst3)
    print(f"  Before Morris: {original_inorder}")
    print(f"  Morris result: {morris_result}")
    print(f"  After Morris:  {after_inorder}")
    assert original_inorder == after_inorder, "Tree was not properly restored!"
    print("  Tree structure restored correctly ✓")

    print("\n" + "=" * 60)
    print("All Morris traversal tests passed!")
    print("=" * 60)
