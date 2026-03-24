"""
Day 46 Practice: AVL Tree Exercises

Implement the functions marked with TODO, then run:

    python3 practice.py

All 6 exercises deal with AVL tree concepts: rotations, balance checking,
construction, and analysis. Solutions are at the bottom — try first.

Rules:
- Do NOT use any external libraries.
- Each function should work with the AVLNode class defined here.
- Solutions are at the bottom — try before looking.
"""


# ---------------------------------------------------------------------------
# AVLNode class (given — do not modify)
# ---------------------------------------------------------------------------

class AVLNode:
    __slots__ = ('val', 'left', 'right', 'height')

    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
        self.height = 0
        _update_height(self)

    def __repr__(self):
        return f"AVLNode({self.val})"


def _update_height(node):
    """Recalculate height from children."""
    if node is None:
        return
    lh = node.left.height if node.left else -1
    rh = node.right.height if node.right else -1
    node.height = 1 + max(lh, rh)


def _get_height(node):
    return node.height if node else -1


def _get_balance(node):
    if node is None:
        return 0
    return _get_height(node.left) - _get_height(node.right)


def _right_rotate(z):
    y = z.left
    t3 = y.right
    y.right = z
    z.left = t3
    _update_height(z)
    _update_height(y)
    return y


def _left_rotate(z):
    y = z.right
    t2 = y.left
    y.left = z
    z.right = t2
    _update_height(z)
    _update_height(y)
    return y


def _avl_insert(node, val):
    """Insert val into the AVL subtree rooted at node. Returns new root."""
    if node is None:
        return AVLNode(val)
    if val < node.val:
        node.left = _avl_insert(node.left, val)
    elif val > node.val:
        node.right = _avl_insert(node.right, val)
    else:
        return node
    _update_height(node)
    balance = _get_balance(node)
    if balance > 1:
        if _get_balance(node.left) < 0:
            node.left = _left_rotate(node.left)
        return _right_rotate(node)
    if balance < -1:
        if _get_balance(node.right) > 0:
            node.right = _right_rotate(node.right)
        return _left_rotate(node)
    return node


def build_avl(values):
    """Build an AVL tree from a list of values. Returns root node."""
    root = None
    for v in values:
        root = _avl_insert(root, v)
    return root


def inorder(node):
    """Return inorder traversal as a list."""
    if node is None:
        return []
    return inorder(node.left) + [node.val] + inorder(node.right)


def preorder(node):
    """Return preorder traversal as a list."""
    if node is None:
        return []
    return [node.val] + preorder(node.left) + preorder(node.right)


# ---------------------------------------------------------------------------
# Exercise 1: Check if a binary tree is AVL-balanced
# ---------------------------------------------------------------------------

def is_avl_balanced(root):
    """Return True if the tree rooted at `root` satisfies the AVL invariant.

    The AVL invariant: for EVERY node, |height(left) - height(right)| <= 1.

    Do NOT just check the root — check every node recursively.
    Return True for an empty tree (None).

    Hint: write a helper that returns the height of a subtree, or -1 if
    it finds a violation.
    """
    # TODO: implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Count the number of rotations needed to build an AVL tree
# ---------------------------------------------------------------------------

def count_rotations(values):
    """Insert `values` one by one into an AVL tree, counting total rotations.

    Return (root, rotation_count) where root is the final AVL tree root.

    A single rotation (left or right) counts as 1.
    A double rotation (LR or RL) counts as 2.

    Hint: modify the standard AVL insert to increment a counter each time
    a rotation function is called.
    """
    # TODO: implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Find the lowest common ancestor in an AVL (BST) tree
# ---------------------------------------------------------------------------

def lowest_common_ancestor(root, val1, val2):
    """Find the lowest common ancestor (LCA) of val1 and val2 in the BST.

    The LCA is the deepest node that is an ancestor of both val1 and val2.
    A node is considered an ancestor of itself.

    Since this is a BST, you can use the BST property:
    - If both values are less than current node, LCA is in the left subtree.
    - If both values are greater, LCA is in the right subtree.
    - Otherwise, current node is the LCA.

    Assume both val1 and val2 exist in the tree. Return the node's value.
    Return None if root is None.
    """
    # TODO: implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Convert a sorted array to a height-balanced AVL tree
# ---------------------------------------------------------------------------

def sorted_array_to_avl(arr):
    """Convert a sorted array into a height-balanced AVL tree.

    Return the root AVLNode.

    Strategy: pick the middle element as root, recursively build left and
    right subtrees from the left and right halves.

    This produces a perfectly balanced tree (which is also AVL-balanced).
    Return None for an empty array.

    IMPORTANT: after building, update heights correctly.
    """
    # TODO: implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Find the kth smallest element in the AVL tree
# ---------------------------------------------------------------------------

def kth_smallest(root, k):
    """Return the kth smallest value in the AVL tree (1-indexed).

    k=1 returns the minimum, k=2 returns the second smallest, etc.
    Return None if k is out of range.

    Hint: use an inorder traversal (which visits BST nodes in sorted order)
    and stop early at the kth element. Avoid building the full list if
    you want O(k) time instead of O(n).
    """
    # TODO: implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Determine the minimum number of nodes in an AVL tree of height h
# ---------------------------------------------------------------------------

def min_avl_nodes(h):
    """Return the minimum number of nodes in an AVL tree of height h.

    Height convention: empty tree has height -1, single node has height 0.

    The minimum-node AVL tree of height h has:
    - A root node
    - One subtree of height h-1 (minimum nodes)
    - One subtree of height h-2 (minimum nodes)

    This gives the recurrence:
        N(h) = 1 + N(h-1) + N(h-2)

    Base cases:
        N(-1) = 0  (empty tree)
        N(0)  = 1  (single node)

    Return the count. Use iteration or recursion.
    """
    # TODO: implement this
    pass


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

    # --- Exercise 1: is_avl_balanced ---
    print("Exercise 1: is_avl_balanced")
    # A properly built AVL tree should be balanced
    avl_root = build_avl([3, 1, 5, 2, 4, 6])
    check("avl tree is balanced", is_avl_balanced(avl_root), True)
    check("empty tree is balanced", is_avl_balanced(None), True)
    check("single node is balanced", is_avl_balanced(AVLNode(1)), True)
    # Manually create an unbalanced tree
    unbal = AVLNode(10)
    unbal.left = AVLNode(5)
    unbal.left.left = AVLNode(2)
    unbal.left.left.left = AVLNode(1)
    _update_height(unbal.left.left)
    _update_height(unbal.left)
    _update_height(unbal)
    check("unbalanced tree", is_avl_balanced(unbal), False)

    # --- Exercise 2: count_rotations ---
    print("\nExercise 2: count_rotations")
    # Sorted input causes the most rotations
    root, count = count_rotations([1, 2, 3, 4, 5, 6, 7])
    check("sorted input produces valid AVL", inorder(root), [1, 2, 3, 4, 5, 6, 7])
    check("sorted input needs rotations", count > 0, True)
    # Already balanced input needs no rotations
    root2, count2 = count_rotations([4, 2, 6, 1, 3, 5, 7])
    check("balanced input no rotations", count2, 0)

    # --- Exercise 3: lowest_common_ancestor ---
    print("\nExercise 3: lowest_common_ancestor")
    lca_root = build_avl([1, 2, 3, 4, 5, 6, 7, 8, 9])
    check("lca of 1 and 3", lowest_common_ancestor(lca_root, 1, 3), 2)
    check("lca of 1 and 9", lowest_common_ancestor(lca_root, 1, 9), 4)
    check("lca of 4 and 4", lowest_common_ancestor(lca_root, 4, 4), 4)
    check("lca of 7 and 9", lowest_common_ancestor(lca_root, 7, 9), 8)
    check("lca of empty tree", lowest_common_ancestor(None, 1, 2), None)

    # --- Exercise 4: sorted_array_to_avl ---
    print("\nExercise 4: sorted_array_to_avl")
    arr_root = sorted_array_to_avl([1, 2, 3, 4, 5, 6, 7])
    check("sorted array inorder", inorder(arr_root), [1, 2, 3, 4, 5, 6, 7])
    check("sorted array root is middle", arr_root.val, 4)
    check("sorted array is balanced", is_avl_balanced(arr_root), True)
    check("empty array", sorted_array_to_avl([]), None)
    single = sorted_array_to_avl([42])
    check("single element", single.val, 42)

    # --- Exercise 5: kth_smallest ---
    print("\nExercise 5: kth_smallest")
    kth_root = build_avl([5, 3, 7, 1, 4, 6, 8, 2])
    check("1st smallest", kth_smallest(kth_root, 1), 1)
    check("3rd smallest", kth_smallest(kth_root, 3), 3)
    check("8th smallest", kth_smallest(kth_root, 8), 8)
    check("k out of range", kth_smallest(kth_root, 9), None)
    check("k=0 out of range", kth_smallest(kth_root, 0), None)
    check("empty tree", kth_smallest(None, 1), None)

    # --- Exercise 6: min_avl_nodes ---
    print("\nExercise 6: min_avl_nodes")
    check("height -1 (empty)", min_avl_nodes(-1), 0)
    check("height 0 (single node)", min_avl_nodes(0), 1)
    check("height 1", min_avl_nodes(1), 2)
    check("height 2", min_avl_nodes(2), 4)
    check("height 3", min_avl_nodes(3), 7)
    check("height 4", min_avl_nodes(4), 12)
    check("height 10", min_avl_nodes(10), 232)

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

def _sol_is_avl_balanced(root):
    """Solution for Exercise 1."""
    def check(node):
        if node is None:
            return -1  # height of empty tree
        left_h = check(node.left)
        if left_h == -2:
            return -2  # propagate failure
        right_h = check(node.right)
        if right_h == -2:
            return -2
        if abs(left_h - right_h) > 1:
            return -2  # sentinel for "not balanced"
        return 1 + max(left_h, right_h)

    return check(root) != -2


def _sol_count_rotations(values):
    """Solution for Exercise 2."""
    rotation_count = [0]

    def right_rotate(z):
        rotation_count[0] += 1
        y = z.left
        t3 = y.right
        y.right = z
        z.left = t3
        _update_height(z)
        _update_height(y)
        return y

    def left_rotate(z):
        rotation_count[0] += 1
        y = z.right
        t2 = y.left
        y.left = z
        z.right = t2
        _update_height(z)
        _update_height(y)
        return y

    def insert(node, val):
        if node is None:
            return AVLNode(val)
        if val < node.val:
            node.left = insert(node.left, val)
        elif val > node.val:
            node.right = insert(node.right, val)
        else:
            return node
        _update_height(node)
        balance = _get_balance(node)
        if balance > 1:
            if _get_balance(node.left) < 0:
                node.left = left_rotate(node.left)
            return right_rotate(node)
        if balance < -1:
            if _get_balance(node.right) > 0:
                node.right = right_rotate(node.right)
            return left_rotate(node)
        return node

    root = None
    for v in values:
        root = insert(root, v)
    return (root, rotation_count[0])


def _sol_lowest_common_ancestor(root, val1, val2):
    """Solution for Exercise 3."""
    if root is None:
        return None
    node = root
    while node is not None:
        if val1 < node.val and val2 < node.val:
            node = node.left
        elif val1 > node.val and val2 > node.val:
            node = node.right
        else:
            return node.val
    return None


def _sol_sorted_array_to_avl(arr):
    """Solution for Exercise 4."""
    if not arr:
        return None

    def build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = AVLNode(arr[mid])
        node.left = build(lo, mid - 1)
        node.right = build(mid + 1, hi)
        _update_height(node)
        return node

    return build(0, len(arr) - 1)


def _sol_kth_smallest(root, k):
    """Solution for Exercise 5."""
    if root is None or k <= 0:
        return None
    count = [0]
    result = [None]

    def inorder_walk(node):
        if node is None or result[0] is not None:
            return
        inorder_walk(node.left)
        count[0] += 1
        if count[0] == k:
            result[0] = node.val
            return
        inorder_walk(node.right)

    inorder_walk(root)
    return result[0]


def _sol_min_avl_nodes(h):
    """Solution for Exercise 6."""
    if h <= -1:
        return 0
    if h == 0:
        return 1
    # N(h) = 1 + N(h-1) + N(h-2)
    prev2 = 0  # N(-1)
    prev1 = 1  # N(0)
    for _ in range(1, h + 1):
        current = 1 + prev1 + prev2
        prev2 = prev1
        prev1 = current
    return prev1


SOLUTIONS = """
================================================================================
SOLUTIONS — read only after a genuine attempt
================================================================================

Exercise 1: is_avl_balanced

    def is_avl_balanced(root):
        def check(node):
            if node is None:
                return -1
            left_h = check(node.left)
            if left_h == -2:
                return -2
            right_h = check(node.right)
            if right_h == -2:
                return -2
            if abs(left_h - right_h) > 1:
                return -2
            return 1 + max(left_h, right_h)
        return check(root) != -2

Exercise 2: count_rotations

    Modify the standard AVL insert to use local left_rotate/right_rotate
    functions that increment a counter each time they are called.
    A double rotation (LR or RL) calls two rotation functions, so it
    naturally counts as 2.

Exercise 3: lowest_common_ancestor

    def lowest_common_ancestor(root, val1, val2):
        if root is None:
            return None
        node = root
        while node:
            if val1 < node.val and val2 < node.val:
                node = node.left
            elif val1 > node.val and val2 > node.val:
                node = node.right
            else:
                return node.val
        return None

Exercise 4: sorted_array_to_avl

    def sorted_array_to_avl(arr):
        if not arr:
            return None
        def build(lo, hi):
            if lo > hi:
                return None
            mid = (lo + hi) // 2
            node = AVLNode(arr[mid])
            node.left = build(lo, mid - 1)
            node.right = build(mid + 1, hi)
            _update_height(node)
            return node
        return build(0, len(arr) - 1)

Exercise 5: kth_smallest

    def kth_smallest(root, k):
        if root is None or k <= 0:
            return None
        count = [0]
        result = [None]
        def inorder_walk(node):
            if node is None or result[0] is not None:
                return
            inorder_walk(node.left)
            count[0] += 1
            if count[0] == k:
                result[0] = node.val
                return
            inorder_walk(node.right)
        inorder_walk(root)
        return result[0]

Exercise 6: min_avl_nodes

    def min_avl_nodes(h):
        if h <= -1:
            return 0
        if h == 0:
            return 1
        prev2, prev1 = 0, 1     # N(-1), N(0)
        for _ in range(1, h + 1):
            current = 1 + prev1 + prev2
            prev2 = prev1
            prev1 = current
        return prev1

    The recurrence N(h) = 1 + N(h-1) + N(h-2) mirrors Fibonacci.
    This is why AVL tree height is bounded by ~1.44 * log2(n).
"""


def show_solutions():
    print(SOLUTIONS)


if __name__ == "__main__":
    print("Day 46 Practice: AVL Tree Exercises")
    print("=" * 50)
    print()
    print("Implement the TODO functions above, then run this file.")
    print("Tests will tell you which functions work and which need fixing.\n")
    run_tests()
    print("\nTo see solutions, uncomment the line below or call show_solutions().")
    # show_solutions()
