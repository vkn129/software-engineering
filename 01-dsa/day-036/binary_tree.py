"""
Day 36: Binary Tree Fundamentals
=================================
Core implementation: TreeNode, construction utilities, all four traversals
(recursive + iterative), and tree property functions.

Every tree algorithm follows the same skeleton:
    1. Base case: node is None → return identity value
    2. Recursive case: combine f(node.left), node.val, f(node.right)

The ORDER of combining defines the traversal type.
"""

from collections import deque
from typing import Optional


class TreeNode:
    """A node in a binary tree.

    Why store left/right pointers instead of an array of children?
    Binary trees constrain each node to at most 2 children, which:
    - Enables efficient array representation (heaps)
    - Makes rotation operations possible (BSTs, AVL, Red-Black)
    - Simplifies recursion to two branches instead of variable-length loops
    """
    __slots__ = ('val', 'left', 'right')

    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        return f"TreeNode({self.val})"


# ─── Construction Utilities ───────────────────────────────────────────

def from_list(values: list) -> Optional[TreeNode]:
    """Build a tree from level-order list (None = absent node).

    This is the standard LeetCode-style representation:
        [1, 2, 3, None, 4] →
              1
             / \\
            2   3
             \\
              4

    Why level-order? Because it maps to array indices:
        parent at index i → left child at 2i+1, right child at 2i+2
    This is the same insight that makes binary heaps work (Day 57).
    """
    if not values:
        return None

    root = TreeNode(values[0])
    queue = deque([root])
    i = 1

    while queue and i < len(values):
        node = queue.popleft()

        # Left child
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1

        # Right child
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1

    return root


def to_list(root: Optional[TreeNode]) -> list:
    """Serialize tree to level-order list (inverse of from_list).

    Trims trailing None values for clean output.
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        node = queue.popleft()
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)

    # Trim trailing Nones
    while result and result[-1] is None:
        result.pop()

    return result


# ─── Recursive Traversals ────────────────────────────────────────────
#
# All three DFS traversals have identical structure — only the POSITION
# of "process current node" changes relative to the recursive calls.

def inorder_recursive(root: Optional[TreeNode]) -> list:
    """Left → Root → Right

    Why this order? For BSTs, inorder visits nodes in sorted order.
    This is because everything in left subtree < root < everything in right subtree.
    """
    result = []

    def _traverse(node):
        if node is None:
            return
        _traverse(node.left)       # recurse left
        result.append(node.val)    # process root
        _traverse(node.right)      # recurse right

    _traverse(root)
    return result


def preorder_recursive(root: Optional[TreeNode]) -> list:
    """Root → Left → Right

    Why this order? Parent is processed BEFORE children.
    Used for: tree serialization (save parent, then children),
    tree copying, and expression tree prefix notation.
    """
    result = []

    def _traverse(node):
        if node is None:
            return
        result.append(node.val)    # process root FIRST
        _traverse(node.left)
        _traverse(node.right)

    _traverse(root)
    return result


def postorder_recursive(root: Optional[TreeNode]) -> list:
    """Left → Right → Root

    Why this order? Children are processed BEFORE parent.
    Used for: tree deletion (free children before parent),
    expression evaluation (operands before operator),
    directory size calculation (subdirs before parent dir).
    """
    result = []

    def _traverse(node):
        if node is None:
            return
        _traverse(node.left)
        _traverse(node.right)
        result.append(node.val)    # process root LAST

    _traverse(root)
    return result


# ─── Iterative Traversals ────────────────────────────────────────────
#
# Why iterative? Two reasons:
# 1. Python's default recursion limit is 1000 — deep trees crash
# 2. Explicit stack gives you control: pause, resume, transform
#
# The insight: we're simulating exactly what the call stack does.

def inorder_iterative(root: Optional[TreeNode]) -> list:
    """Iterative inorder using explicit stack.

    This is the TRICKIEST iterative traversal because root is
    processed BETWEEN its children, not at push or pop time.

    Pattern:
        1. Go left as far as possible, pushing each node
        2. Pop → this is the "current" node, process it
        3. Move to right child (step 1 will push its left descendants)

    Space: O(h) where h = height. For balanced tree: O(log n).
    For degenerate tree (linked list): O(n).
    """
    result = []
    stack = []
    current = root

    while current or stack:
        # Phase 1: drill down left, pushing everything
        while current:
            stack.append(current)
            current = current.left

        # Phase 2: pop = we've fully explored left subtree
        current = stack.pop()
        result.append(current.val)  # process node

        # Phase 3: explore right subtree (loop will drill left again)
        current = current.right

    return result


def preorder_iterative(root: Optional[TreeNode]) -> list:
    """Iterative preorder using explicit stack.

    Simpler than inorder because we process the node immediately
    when we first encounter it (at push time, effectively).

    Key: push RIGHT child first, then LEFT — because stack is LIFO,
    left will be popped (processed) first.
    """
    if not root:
        return []

    result = []
    stack = [root]

    while stack:
        node = stack.pop()
        result.append(node.val)  # process immediately

        # Push right first so left is processed first (LIFO)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)

    return result


def postorder_iterative(root: Optional[TreeNode]) -> list:
    """Iterative postorder using two-stack trick.

    Postorder (L→R→Root) is the reverse of a modified preorder (Root→R→L).
    So we do preorder but push left before right, then reverse the result.

    Alternative: single-stack with a 'last visited' pointer, but
    the two-stack approach is clearer and still O(n) time, O(n) space.
    """
    if not root:
        return []

    result = []
    stack = [root]

    while stack:
        node = stack.pop()
        result.append(node.val)

        # Push left first, then right (reverse of preorder)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)

    # Reverse gives us postorder
    result.reverse()
    return result


def postorder_iterative_single_stack(root: Optional[TreeNode]) -> list:
    """Single-stack postorder — the elegant but tricky version.

    Uses a 'last_visited' pointer to distinguish between:
    - Coming UP from left child → still need to visit right
    - Coming UP from right child → safe to process current node

    This avoids the double-traversal of the two-stack approach.
    """
    result = []
    stack = []
    current = root
    last_visited = None

    while current or stack:
        # Drill left
        while current:
            stack.append(current)
            current = current.left

        # Peek at top of stack
        peek = stack[-1]

        # If right child exists and we haven't visited it yet
        if peek.right and peek.right is not last_visited:
            current = peek.right
        else:
            # Both children processed — safe to process this node
            result.append(peek.val)
            last_visited = stack.pop()

    return result


# ─── Level-Order (BFS) ───────────────────────────────────────────────

def level_order(root: Optional[TreeNode]) -> list[list]:
    """BFS traversal, returning values grouped by level.

    Uses a queue (FIFO) — the fundamental BFS data structure.

    Why group by level? Many problems need level-aware processing:
    - Level averages, level maximums
    - Zigzag traversal
    - Right-side view (rightmost node at each level)

    Space: O(w) where w is max width. For a perfect tree with n nodes,
    the last level has ~n/2 nodes, so space is O(n).
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)  # nodes at current level
        level_vals = []

        for _ in range(level_size):
            node = queue.popleft()
            level_vals.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(level_vals)

    return result


# ─── Tree Properties ─────────────────────────────────────────────────

def height(root: Optional[TreeNode]) -> int:
    """Height = number of edges on the longest root-to-leaf path.

    Empty tree: -1 (convention: an empty tree has no edges)
    Single node: 0 (a leaf is at height 0)

    Recurrence: height(node) = 1 + max(height(left), height(right))
    Time: O(n) — must visit every node. No shortcut exists.
    """
    if root is None:
        return -1
    return 1 + max(height(root.left), height(root.right))


def size(root: Optional[TreeNode]) -> int:
    """Total number of nodes. O(n) — must count every node."""
    if root is None:
        return 0
    return 1 + size(root.left) + size(root.right)


def is_balanced(root: Optional[TreeNode]) -> bool:
    """A tree is balanced if for EVERY node, the height difference
    between left and right subtrees is at most 1.

    Naive approach: call height() for every node → O(n²).
    Better: compute height bottom-up, returning -1 (sentinel) if
    any subtree is unbalanced. This gives O(n).

    Why balanced matters: it guarantees O(log n) operations.
    An unbalanced BST degrades to a linked list → O(n).
    """
    def _check(node):
        """Returns height if balanced, -1 if not."""
        if node is None:
            return 0

        left_h = _check(node.left)
        if left_h == -1:
            return -1  # left subtree unbalanced, propagate failure

        right_h = _check(node.right)
        if right_h == -1:
            return -1  # right subtree unbalanced

        if abs(left_h - right_h) > 1:
            return -1  # current node unbalanced

        return 1 + max(left_h, right_h)

    return _check(root) != -1


def is_symmetric(root: Optional[TreeNode]) -> bool:
    """A tree is symmetric if it is a mirror of itself.

        1
       / \\
      2   2      ← symmetric
     / \\ / \\
    3  4 4  3

    The insight: two trees are mirrors if:
    1. Their roots have the same value
    2. Left subtree of one mirrors right subtree of the other
    """
    def _is_mirror(t1, t2):
        if t1 is None and t2 is None:
            return True
        if t1 is None or t2 is None:
            return False
        return (t1.val == t2.val and
                _is_mirror(t1.left, t2.right) and
                _is_mirror(t1.right, t2.left))

    if root is None:
        return True
    return _is_mirror(root.left, root.right)


def max_depth(root: Optional[TreeNode]) -> int:
    """Maximum depth = number of nodes on longest root-to-leaf path.

    Note: this returns node count, not edge count.
    max_depth = height + 1 (for non-empty trees).
    Some problems define depth as node count, others as edge count.
    Always check the problem definition.
    """
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


def count_leaves(root: Optional[TreeNode]) -> int:
    """Count leaf nodes (nodes with no children).

    For a full binary tree with n internal nodes, there are n+1 leaves.
    This is because each internal node adds 2 children but "uses" 1 slot.
    """
    if root is None:
        return 0
    if root.left is None and root.right is None:
        return 1
    return count_leaves(root.left) + count_leaves(root.right)


def invert_tree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    """Mirror/invert a binary tree (swap left and right at every node).

    The famous "Google interview question" that sparked the
    "Homebrew creator can't invert a binary tree" meme.

    It's trivial once you see it: just swap children, then recurse.
    Time: O(n), Space: O(h) for call stack.
    """
    if root is None:
        return None
    root.left, root.right = root.right, root.left
    invert_tree(root.left)
    invert_tree(root.right)
    return root


# ─── Demonstration ───────────────────────────────────────────────────

def print_tree(root: Optional[TreeNode], prefix="", is_left=True):
    """Visual tree printing for debugging."""
    if root is None:
        return

    print_tree(root.right, prefix + ("│   " if is_left else "    "), False)
    connector = "└── " if is_left else "┌── "
    print(f"{prefix}{connector}{root.val}")
    print_tree(root.left, prefix + ("    " if is_left else "│   "), True)


if __name__ == "__main__":
    # Build example tree:
    #         1
    #        / \
    #       2   3
    #      / \   \
    #     4   5   6
    #    /
    #   7

    tree = from_list([1, 2, 3, 4, 5, None, 6, 7])

    print("Tree structure:")
    print_tree(tree)
    print()

    print("─── Traversals ──────────────────────────────")
    print(f"Inorder  (recursive): {inorder_recursive(tree)}")
    print(f"Inorder  (iterative): {inorder_iterative(tree)}")
    print(f"Preorder (recursive): {preorder_recursive(tree)}")
    print(f"Preorder (iterative): {preorder_iterative(tree)}")
    print(f"Postorder(recursive): {postorder_recursive(tree)}")
    print(f"Postorder(iterative): {postorder_iterative(tree)}")
    print(f"Postorder(1-stack):   {postorder_iterative_single_stack(tree)}")
    print(f"Level-order (BFS):    {level_order(tree)}")

    print()
    print("─── Properties ──────────────────────────────")
    print(f"Height:       {height(tree)}")
    print(f"Size:         {size(tree)}")
    print(f"Max depth:    {max_depth(tree)}")
    print(f"Leaves:       {count_leaves(tree)}")
    print(f"Balanced:     {is_balanced(tree)}")
    print(f"Symmetric:    {is_symmetric(tree)}")

    # Test symmetric tree
    sym = from_list([1, 2, 2, 3, 4, 4, 3])
    print(f"\nSymmetric tree [1,2,2,3,4,4,3]: {is_symmetric(sym)}")

    # Test serialization round-trip
    values = to_list(tree)
    rebuilt = from_list(values)
    print(f"\nRound-trip: {to_list(tree)} → rebuild → {to_list(rebuilt)}")
    assert to_list(tree) == to_list(rebuilt), "Serialization round-trip failed!"
    print("Round-trip serialization: PASSED")

    # Verify recursive == iterative
    assert inorder_recursive(tree) == inorder_iterative(tree)
    assert preorder_recursive(tree) == preorder_iterative(tree)
    assert postorder_recursive(tree) == postorder_iterative(tree)
    assert postorder_recursive(tree) == postorder_iterative_single_stack(tree)
    print("All traversals (recursive == iterative): PASSED")
