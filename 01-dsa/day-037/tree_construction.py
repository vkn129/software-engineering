"""
Day 37: Tree Construction — From Traversals, Serialization/Deserialization
==========================================================================
Core problem: given a linear representation of a tree, reconstruct the
pointer-based structure. This is the inverse of traversal.

Why this matters:
    - Compilers serialize ASTs to disk and reconstruct them
    - Databases serialize B-tree pages to disk blocks
    - Network protocols transmit tree structures as byte sequences
    - Git stores directory trees as serialized objects

Key insight: a single traversal (inorder, preorder, or postorder) is NOT
enough to uniquely determine a tree. You need EITHER:
    1. Two complementary traversals (inorder + preorder, or inorder + postorder)
    2. One traversal WITH sentinel markers for None children
"""

import sys
import os
from collections import deque
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import (TreeNode, from_list, to_list,
                         inorder_recursive, preorder_recursive, postorder_recursive)


# ─── Reconstruction from Two Traversals ─────────────────────────────

def build_from_inorder_preorder(inorder: list, preorder: list) -> Optional[TreeNode]:
    """Reconstruct a binary tree from its inorder and preorder traversals.

    WHY this works:
        - preorder[0] is ALWAYS the root (preorder visits root first)
        - Finding that root in the inorder array SPLITS it into:
          left_inorder (everything left of root) and right_inorder (everything right)
        - The LENGTH of left_inorder tells us how many nodes are in the left subtree,
          which lets us split the preorder array too

    WHY we use a hash map:
        Without it, finding root in inorder is O(n) per call → O(n²) total.
        With a hash map: O(1) lookup → O(n) total.
        This is the difference between 1 second and 16 minutes for n=1,000,000.

    Constraints: all values must be unique (otherwise inorder position is ambiguous).

    Time: O(n)  — each node processed exactly once
    Space: O(n) — hash map + recursion stack (O(h) for balanced, O(n) worst case)
    """
    if not inorder or not preorder:
        return None

    # Build index map: value → position in inorder array
    # This turns O(n) linear search into O(1) hash lookup
    inorder_index = {val: idx for idx, val in enumerate(inorder)}

    # pre_idx tracks our position in the preorder array as we consume roots
    # Using a list so the nested function can mutate it (Python closure semantics)
    pre_idx = [0]

    def _build(in_left: int, in_right: int) -> Optional[TreeNode]:
        """Build subtree from inorder[in_left:in_right+1].

        in_left, in_right: bounds of the current subtree in the inorder array.
        pre_idx[0]: index of the next root in the preorder array.
        """
        if in_left > in_right:
            return None  # empty subtree

        # The next element in preorder is the root of this subtree
        root_val = preorder[pre_idx[0]]
        pre_idx[0] += 1

        root = TreeNode(root_val)

        # Find where the root sits in inorder — this splits left from right
        in_root = inorder_index[root_val]

        # CRITICAL: build left subtree FIRST because preorder visits left before right.
        # If we built right first, pre_idx would advance past the left subtree's nodes.
        root.left = _build(in_left, in_root - 1)
        root.right = _build(in_root + 1, in_right)

        return root

    return _build(0, len(inorder) - 1)


def build_from_inorder_postorder(inorder: list, postorder: list) -> Optional[TreeNode]:
    """Reconstruct a binary tree from its inorder and postorder traversals.

    WHY this works:
        Same logic as inorder+preorder, but mirrored:
        - postorder[-1] is ALWAYS the root (postorder visits root LAST)
        - We consume postorder from RIGHT to LEFT
        - We must build RIGHT subtree FIRST because postorder visits
          right subtree after left but before root — so reading backwards,
          the right subtree's nodes come immediately after the root

    Think of it this way:
        Preorder:  Root, Left, Right  → read left-to-right, build left first
        Postorder: Left, Right, Root  → read right-to-left, build right first

    Time: O(n), Space: O(n)
    """
    if not inorder or not postorder:
        return None

    inorder_index = {val: idx for idx, val in enumerate(inorder)}
    post_idx = [len(postorder) - 1]  # start from the END

    def _build(in_left: int, in_right: int) -> Optional[TreeNode]:
        if in_left > in_right:
            return None

        root_val = postorder[post_idx[0]]
        post_idx[0] -= 1  # consume from right to left

        root = TreeNode(root_val)
        in_root = inorder_index[root_val]

        # CRITICAL: build RIGHT subtree first!
        # Postorder = [left..., right..., root]
        # Reading backwards: root, then right subtree, then left subtree
        root.right = _build(in_root + 1, in_right)
        root.left = _build(in_left, in_root - 1)

        return root

    return _build(0, len(inorder) - 1)


# ─── DFS Serialization (Preorder with Sentinels) ────────────────────

def serialize(root: Optional[TreeNode]) -> str:
    """Serialize a binary tree to a string using preorder with sentinels.

    WHY preorder with sentinels?
        - A plain preorder traversal loses structural information (where are the Nones?)
        - By recording '#' for every None child, we capture the COMPLETE structure
        - Preorder is ideal because the root comes first → the deserializer can
          build the tree top-down in a single pass without lookahead

    WHY not just use two traversals?
        Two traversals require unique values and twice the data.
        Sentinel-based serialization works with duplicate values and uses one pass.

    Format: "val,val,#,#,val,#,#" where '#' represents None.

    Example:
            1
           / \\
          2   3
             / \\
            4   5

        → "1,2,#,#,3,4,#,#,5,#,#"

    Time: O(n), Space: O(n) for the output string
    """
    tokens = []

    def _preorder(node):
        if node is None:
            tokens.append('#')
            return
        tokens.append(str(node.val))
        _preorder(node.left)
        _preorder(node.right)

    _preorder(root)
    return ','.join(tokens)


def deserialize(data: str) -> Optional[TreeNode]:
    """Deserialize a string back into a binary tree.

    WHY this works:
        The serialized preorder with sentinels is unambiguous because:
        - Each node contributes exactly one value token
        - Each None contributes exactly one '#' token
        - A tree with n nodes has exactly n+1 None children (external nodes)
        - So the total token count is always 2n+1 — no ambiguity

    The deserializer is a recursive descent parser — the same technique
    compilers use to parse programming languages. Each call to _build()
    consumes tokens for exactly one subtree.

    Time: O(n), Space: O(n)
    """
    if not data:
        return None

    tokens = iter(data.split(','))

    def _build():
        val = next(tokens)
        if val == '#':
            return None

        node = TreeNode(int(val))
        # Preorder: after the root value, the next tokens describe
        # the left subtree, then the right subtree
        node.left = _build()
        node.right = _build()
        return node

    return _build()


# ─── BFS Serialization (Level-Order) ────────────────────────────────

def serialize_bfs(root: Optional[TreeNode]) -> str:
    """Serialize a binary tree using level-order (BFS) traversal.

    WHY BFS serialization?
        - Natural for complete/nearly-complete trees (heaps, segment trees)
        - The LeetCode standard representation uses this format
        - Preserves level structure explicitly — useful when level information matters

    WHY it's less efficient for sparse trees:
        A deep, sparse tree (e.g., a linked list of 1000 nodes) would require
        recording None for every missing node at every level, producing
        O(2^h) tokens instead of O(n).

    Format: "1,2,3,#,#,4,5" — level by level, '#' for None.
    Trailing '#' markers are trimmed for cleaner output.

    Time: O(n), Space: O(n)
    """
    if root is None:
        return ''

    tokens = []
    queue = deque([root])

    while queue:
        node = queue.popleft()
        if node is None:
            tokens.append('#')
        else:
            tokens.append(str(node.val))
            queue.append(node.left)
            queue.append(node.right)

    # Trim trailing '#' — they carry no information for BFS reconstruction
    # (We know to stop when we run out of tokens)
    while tokens and tokens[-1] == '#':
        tokens.pop()

    return ','.join(tokens)


def deserialize_bfs(data: str) -> Optional[TreeNode]:
    """Deserialize a BFS-serialized string back into a binary tree.

    WHY this mirrors the serialization:
        BFS serialization writes nodes level by level. Deserialization reads
        them back in the same order, using a queue to track which parent
        gets the next child.

    The queue-based approach:
        1. Create root from first token
        2. For each node in the queue, consume next two tokens as left and right children
        3. Enqueue non-None children for their own child assignment

    This is essentially the same algorithm as from_list() in day-036,
    but operating on a string instead of a Python list.

    Time: O(n), Space: O(n)
    """
    if not data:
        return None

    tokens = data.split(',')
    if not tokens or tokens[0] == '#':
        return None

    root = TreeNode(int(tokens[0]))
    queue = deque([root])
    i = 1

    while queue and i < len(tokens):
        node = queue.popleft()

        # Left child
        if i < len(tokens) and tokens[i] != '#':
            node.left = TreeNode(int(tokens[i]))
            queue.append(node.left)
        i += 1

        # Right child
        if i < len(tokens) and tokens[i] != '#':
            node.right = TreeNode(int(tokens[i]))
            queue.append(node.right)
        i += 1

    return root


# ─── Demonstration ──────────────────────────────────────────────────

if __name__ == "__main__":
    print("Day 37: Tree Construction")
    print("=" * 55)

    # ── Reconstruction from traversals ──
    #
    #         3
    #        / \
    #       9  20
    #         / \
    #        15  7

    inorder  = [9, 3, 15, 20, 7]
    preorder = [3, 9, 20, 15, 7]
    postorder = [9, 15, 7, 20, 3]

    print("\n── Reconstruction from Traversals ──")
    print(f"Inorder:   {inorder}")
    print(f"Preorder:  {preorder}")
    print(f"Postorder: {postorder}")

    tree1 = build_from_inorder_preorder(inorder, preorder)
    tree2 = build_from_inorder_postorder(inorder, postorder)

    print(f"\nFrom inorder+preorder:  {to_list(tree1)}")
    print(f"From inorder+postorder: {to_list(tree2)}")

    # Verify both produce the same tree
    assert to_list(tree1) == to_list(tree2), "Reconstructions should match!"
    print("Both reconstructions match: PASSED")

    # Verify round-trip: tree → traversals → tree
    assert inorder_recursive(tree1) == inorder
    assert preorder_recursive(tree1) == preorder
    assert postorder_recursive(tree1) == postorder
    print("Round-trip (tree → traversals → tree): PASSED")

    # ── DFS Serialization ──
    print("\n── DFS Serialization (Preorder + Sentinels) ──")
    original = from_list([1, 2, 3, None, None, 4, 5])
    serialized = serialize(original)
    print(f"Original tree (level-order):  {to_list(original)}")
    print(f"Serialized (DFS):             {serialized}")

    restored = deserialize(serialized)
    print(f"Deserialized (level-order):   {to_list(restored)}")
    assert to_list(original) == to_list(restored), "DFS round-trip failed!"
    print("DFS round-trip: PASSED")

    # ── BFS Serialization ──
    print("\n── BFS Serialization (Level-Order) ──")
    serialized_bfs = serialize_bfs(original)
    print(f"Serialized (BFS):             {serialized_bfs}")

    restored_bfs = deserialize_bfs(serialized_bfs)
    print(f"Deserialized (level-order):   {to_list(restored_bfs)}")
    assert to_list(original) == to_list(restored_bfs), "BFS round-trip failed!"
    print("BFS round-trip: PASSED")

    # ── Edge cases ──
    print("\n── Edge Cases ──")

    # Empty tree
    assert deserialize(serialize(None)) is None
    assert deserialize_bfs(serialize_bfs(None)) is None
    print("Empty tree round-trip: PASSED")

    # Single node
    single = TreeNode(42)
    assert to_list(deserialize(serialize(single))) == [42]
    assert to_list(deserialize_bfs(serialize_bfs(single))) == [42]
    print("Single node round-trip: PASSED")

    # Skewed tree (all left children — worst case for recursion depth)
    skewed = from_list([1, 2, None, 3, None, 4])
    assert to_list(deserialize(serialize(skewed))) == to_list(skewed)
    assert to_list(deserialize_bfs(serialize_bfs(skewed))) == to_list(skewed)
    print("Skewed tree round-trip: PASSED")

    # Negative values
    neg_tree = from_list([-1, -2, -3])
    assert to_list(deserialize(serialize(neg_tree))) == [-1, -2, -3]
    print("Negative values round-trip: PASSED")

    print(f"\n{'=' * 55}")
    print("All demonstrations passed!")
